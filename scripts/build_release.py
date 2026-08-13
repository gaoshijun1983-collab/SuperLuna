#!/usr/bin/env python3
"""Build and verify a deterministic SuperLuna source release archive."""

from __future__ import annotations

import argparse
import hashlib
import json
import stat
import subprocess
import zipfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath


FIXED_ZIP_TIME = (1980, 1, 1, 0, 0, 0)
MANIFEST_NAME = "RELEASE-MANIFEST.sha256"


class ReleaseError(RuntimeError):
    """Raised when the release tree or archive cannot be trusted."""


@dataclass(frozen=True)
class ReleaseFile:
    path: str
    executable: bool
    data: bytes


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _safe_relative_path(value: str) -> str:
    path = PurePosixPath(value)
    if not value or path.is_absolute() or ".." in path.parts or "\\" in value:
        raise ReleaseError(f"unsafe release path: {value!r}")
    return path.as_posix()


def collect_tracked_files(root: Path) -> list[ReleaseFile]:
    """Read stage-0 regular files from Git's index and current worktree."""
    output = subprocess.check_output(
        ["git", "ls-files", "--stage", "-z"], cwd=root
    )
    files: list[ReleaseFile] = []
    seen: set[str] = set()
    for raw_entry in output.split(b"\0"):
        if not raw_entry:
            continue
        try:
            metadata, raw_path = raw_entry.split(b"\t", 1)
            mode, _object_id, stage = metadata.decode("ascii").split()
            relative = _safe_relative_path(raw_path.decode("utf-8"))
        except (ValueError, UnicodeDecodeError) as exc:
            raise ReleaseError("invalid git index entry") from exc
        if stage != "0":
            raise ReleaseError(f"unmerged release path: {relative}")
        if relative in seen:
            raise ReleaseError(f"duplicate release path: {relative}")
        seen.add(relative)
        if mode not in {"100644", "100755"}:
            raise ReleaseError(f"unsupported release file mode {mode}: {relative}")
        full_path = root / relative
        if not full_path.is_file() or full_path.is_symlink():
            raise ReleaseError(f"tracked release file is unavailable: {relative}")
        files.append(
            ReleaseFile(relative, mode == "100755", full_path.read_bytes())
        )
    if not files:
        raise ReleaseError("release tree is empty")
    return sorted(files, key=lambda item: item.path)


def _manifest_bytes(files: list[ReleaseFile]) -> bytes:
    return "".join(
        f"{_sha256(item.data)}  {item.path}\n" for item in files
    ).encode("utf-8")


def _write_entry(
    archive: zipfile.ZipFile, name: str, data: bytes, *, executable: bool = False
) -> None:
    info = zipfile.ZipInfo(name, FIXED_ZIP_TIME)
    info.create_system = 3
    info.compress_type = zipfile.ZIP_DEFLATED
    unix_mode = stat.S_IFREG | (0o755 if executable else 0o644)
    info.external_attr = unix_mode << 16
    archive.writestr(info, data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)


def _package_version(root: Path) -> str:
    manifest = json.loads(
        (root / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8")
    )
    version = manifest.get("version")
    if not isinstance(version, str) or not version:
        raise ReleaseError("plugin version is missing")
    return version


def verify_archive(root: Path, archive_path: Path) -> dict[str, object]:
    files = collect_tracked_files(root)
    prefix = f"SuperLuna-{_package_version(root)}"
    expected = {f"{prefix}/{item.path}": item for item in files}
    expected_manifest_name = f"{prefix}/{MANIFEST_NAME}"
    with zipfile.ZipFile(archive_path, "r") as archive:
        actual_names = set(archive.namelist())
        expected_names = set(expected) | {expected_manifest_name}
        if actual_names != expected_names:
            missing = sorted(expected_names - actual_names)
            extra = sorted(actual_names - expected_names)
            raise ReleaseError(f"archive tree mismatch: missing={missing}, extra={extra}")
        for name, item in expected.items():
            if archive.read(name) != item.data:
                raise ReleaseError(f"archive content mismatch: {item.path}")
        if archive.read(expected_manifest_name) != _manifest_bytes(files):
            raise ReleaseError("archive manifest does not match current source")
    digest = _sha256(archive_path.read_bytes())
    return {
        "ok": True,
        "archive": str(archive_path),
        "sha256": digest,
        "source_files": len(files),
    }


def build_archive(root: Path, output_dir: Path) -> dict[str, object]:
    files = collect_tracked_files(root)
    version = _package_version(root)
    prefix = f"SuperLuna-{version}"
    output_dir.mkdir(parents=True, exist_ok=True)
    archive_path = output_dir / f"{prefix}.zip"
    temporary_path = output_dir / f".{prefix}.zip.tmp"
    try:
        with zipfile.ZipFile(temporary_path, "w") as archive:
            for item in files:
                _write_entry(
                    archive,
                    f"{prefix}/{item.path}",
                    item.data,
                    executable=item.executable,
                )
            _write_entry(
                archive,
                f"{prefix}/{MANIFEST_NAME}",
                _manifest_bytes(files),
            )
        temporary_path.replace(archive_path)
    finally:
        temporary_path.unlink(missing_ok=True)
    result = verify_archive(root, archive_path)
    checksum_path = archive_path.with_suffix(".zip.sha256.txt")
    checksum_path.write_text(
        f"{result['sha256']}  {archive_path.name}\n", encoding="utf-8", newline="\n"
    )
    result["checksum"] = str(checksum_path)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("build", "verify"), nargs="?", default="build")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--archive", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    if args.action == "build":
        output_dir = (args.output_dir or (root / "dist")).resolve()
        result = build_archive(root, output_dir)
    else:
        archive = args.archive
        if archive is None:
            version = _package_version(root)
            archive = root / "dist" / f"SuperLuna-{version}.zip"
        result = verify_archive(root, archive.resolve())
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import hashlib
import importlib.util
import tempfile
import sys
import unittest
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "build_release.py"
SPEC = importlib.util.spec_from_file_location("superluna_build_release", SCRIPT)
release = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = release
SPEC.loader.exec_module(release)


class ReleasePackagingTests(unittest.TestCase):
    def test_current_source_archive_is_deterministic_and_verifiable(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            first = release.build_archive(ROOT, output)
            first_bytes = Path(first["archive"]).read_bytes()
            second = release.build_archive(ROOT, output)
            second_bytes = Path(second["archive"]).read_bytes()

            self.assertEqual(first_bytes, second_bytes)
            self.assertEqual(first["sha256"], hashlib.sha256(first_bytes).hexdigest())
            self.assertGreater(first["source_files"], 50)
            verified = release.verify_archive(ROOT, Path(second["archive"]))
            self.assertTrue(verified["ok"])

    def test_archive_contains_only_tracked_source_plus_hash_manifest(self):
        with tempfile.TemporaryDirectory() as temporary:
            result = release.build_archive(ROOT, Path(temporary))
            prefix = f"SuperLuna-{release._package_version(ROOT)}/"
            tracked = {item.path for item in release.collect_tracked_files(ROOT)}
            with zipfile.ZipFile(result["archive"], "r") as archive:
                packaged = {
                    name.removeprefix(prefix)
                    for name in archive.namelist()
                    if name != f"{prefix}{release.MANIFEST_NAME}"
                }
            self.assertEqual(packaged, tracked)
            self.assertFalse(any(path.startswith("dist/") for path in packaged))
            self.assertFalse(any(".superluna/" in path for path in packaged))

    def test_verifier_rejects_mutated_archive_content(self):
        with tempfile.TemporaryDirectory() as temporary:
            result = release.build_archive(ROOT, Path(temporary))
            archive_path = Path(result["archive"])
            with zipfile.ZipFile(archive_path, "a") as archive:
                archive.writestr("unexpected.txt", b"tampered")
            with self.assertRaisesRegex(release.ReleaseError, "archive tree mismatch"):
                release.verify_archive(ROOT, archive_path)


if __name__ == "__main__":
    unittest.main()

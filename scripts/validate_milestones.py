#!/usr/bin/env python3
"""Validate the versioned milestone and rollback contract."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


REQUIRED_FIELDS = (
    "version",
    "upgrade_prerequisites",
    "rollback_triggers",
    "rollback_steps",
    "verification",
)
ALLOWED_SCOPES = {"local_only", "real_device", "public_beta"}


def _nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_contract(document: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(document, dict):
        return ["document must be an object"]
    if document.get("contract_version") != "1":
        errors.append("contract_version must be '1'")
    milestones = document.get("milestones")
    if not isinstance(milestones, list) or not milestones:
        return errors + ["milestones must be a non-empty array"]

    seen: set[str] = set()
    for index, milestone in enumerate(milestones):
        label = f"milestones[{index}]"
        if not isinstance(milestone, dict):
            errors.append(f"{label} must be an object")
            continue
        missing = [field for field in REQUIRED_FIELDS if field not in milestone]
        errors.extend(f"{label} missing {field}" for field in missing)
        version = milestone.get("version")
        if not _nonempty_string(version):
            errors.append(f"{label}.version must be a non-empty string")
        elif version in seen:
            errors.append(f"{label}.version is duplicated: {version}")
        else:
            seen.add(version)
        for field in REQUIRED_FIELDS[1:]:
            value = milestone.get(field)
            if not isinstance(value, list) or not value or not all(_nonempty_string(item) for item in value):
                errors.append(f"{label}.{field} must be a non-empty list of strings")

        scope = milestone.get("evidence_scope")
        if scope not in ALLOWED_SCOPES:
            errors.append(f"{label}.evidence_scope must be one of {sorted(ALLOWED_SCOPES)}")
        real_device = milestone.get("real_device_evidence")
        public_beta = milestone.get("public_beta_evidence")
        if not isinstance(real_device, bool):
            errors.append(f"{label}.real_device_evidence must be boolean")
        if not isinstance(public_beta, bool):
            errors.append(f"{label}.public_beta_evidence must be boolean")
        if scope == "local_only" and (real_device is not False or public_beta is not False):
            errors.append(f"{label} local_only scope cannot claim real-device or Public Beta evidence")
        if scope == "real_device" and (real_device is not True or public_beta is not False):
            errors.append(f"{label} real_device scope requires real-device evidence only")
        if scope == "public_beta" and (real_device is not True or public_beta is not True):
            errors.append(f"{label} public_beta scope requires real-device and Public Beta evidence")
    return errors


def validate_file(path: Path) -> dict[str, Any]:
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {"ok": False, "path": str(path), "errors": [f"cannot read JSON: {exc}"]}
    errors = validate_contract(document)
    return {
        "ok": not errors,
        "path": str(path),
        "milestones": len(document.get("milestones", [])) if isinstance(document, dict) else 0,
        "errors": errors,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", default="docs/milestones.json")
    args = parser.parse_args(argv)
    result = validate_file(Path(args.path))
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())

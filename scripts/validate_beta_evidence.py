#!/usr/bin/env python3
"""Validate truthful SuperLuna Public Beta evidence and release-report parity."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


REQUIRED_GATES = (
    "codex_host_same_turn_continuation_enforcement",
    "ten_consecutive_real_project_cycles_on_frozen_candidate",
    "windows_waiting_check_platform_automation",
    "windows_in_app_browser_full_loop",
    "macos_in_app_browser_version_matrix",
    "real_browser_network_and_rate_limit_recovery",
)
PLATFORM_BY_GATE = {
    "windows_waiting_check_platform_automation": "windows",
    "windows_in_app_browser_full_loop": "windows",
    "macos_in_app_browser_version_matrix": "macos",
}
SHA40 = re.compile(r"^[0-9a-f]{40}$")


def _text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _valid_evidence(
    item: Any,
    candidate_version: str,
    candidate_commit: str,
    gate_name: str | None = None,
) -> bool:
    if not isinstance(item, dict):
        return False
    required = (
        "id", "platform", "os_version", "codex_version", "observed_at",
        "artifact", "sha256",
    )
    if not all(_text(item.get(field)) for field in required):
        return False
    return (
        item.get("result") == "pass"
        and item.get("source") == "real_device"
        and item.get("candidate_version") == candidate_version
        and item.get("candidate_commit") == candidate_commit
        and (gate_name is None or item.get("gate") == gate_name)
        and (
            gate_name not in PLATFORM_BY_GATE
            or item.get("platform") == PLATFORM_BY_GATE[gate_name]
        )
        and bool(re.fullmatch(r"[0-9a-f]{64}", item["sha256"]))
    )


def _artifact_error(item: dict[str, Any], root: Path, label: str) -> str | None:
    relative = Path(item["artifact"])
    if relative.is_absolute() or ".." in relative.parts:
        return f"{label}.artifact must stay inside the repository"
    root = root.resolve()
    path = root / relative
    try:
        if path.is_symlink() or not path.is_file() or not path.resolve().is_relative_to(root):
            return f"{label}.artifact must be a regular repository file"
        raw = path.read_bytes()
        actual = hashlib.sha256(raw).hexdigest()
    except OSError as exc:
        return f"{label}.artifact cannot be read: {exc}"
    if actual != item["sha256"]:
        return f"{label}.artifact sha256 does not match the file"
    try:
        artifact = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        return f"{label}.artifact must be a UTF-8 JSON object: {exc}"
    expected = {key: value for key, value in item.items() if key not in {"artifact", "sha256"}}
    if artifact != expected:
        return f"{label}.artifact content must match the recorded evidence"
    return None


def validate_contract(document: Any, release_report: Any | None = None) -> list[str]:
    errors: list[str] = []
    if not isinstance(document, dict):
        return ["document must be an object"]
    if document.get("contract_version") != "1":
        errors.append("contract_version must be '1'")
    version = document.get("candidate_version")
    commit = document.get("candidate_commit")
    if not _text(version):
        errors.append("candidate_version must be a non-empty string")
    if not isinstance(commit, str) or not SHA40.fullmatch(commit):
        errors.append("candidate_commit must be a lowercase 40-character Git SHA")
    required_cycles = document.get("required_consecutive_cycles")
    if required_cycles != 10:
        errors.append("required_consecutive_cycles must be 10")

    gates = document.get("gates")
    if not isinstance(gates, dict):
        return errors + ["gates must be an object"]
    if set(gates) != set(REQUIRED_GATES):
        errors.append("gates must contain exactly the six required Beta gates")

    computed_pass: dict[str, bool] = {}
    for name in REQUIRED_GATES:
        gate = gates.get(name)
        if not isinstance(gate, dict):
            errors.append(f"gates.{name} must be an object")
            computed_pass[name] = False
            continue
        if gate.get("evidence_scope") != "real_device":
            errors.append(f"gates.{name}.evidence_scope must be real_device")
        passed = gate.get("passed")
        if not isinstance(passed, bool):
            errors.append(f"gates.{name}.passed must be boolean")
            passed = False

        if name == "ten_consecutive_real_project_cycles_on_frozen_candidate":
            cycles = gate.get("cycles")
            if not isinstance(cycles, list):
                errors.append(f"gates.{name}.cycles must be an array")
                cycles = []
            valid = [
                item for item in cycles
                if _valid_evidence(item, version, commit, name)
            ]
            valid = [
                item for item in valid
                if all(item.get(field) == 0 for field in (
                    "outside_wakeups", "duplicate_sends", "cross_chat_reads",
                    "replacement_tasks",
                ))
            ]
            ids = [item.get("id") for item in valid]
            evidence_complete = len(valid) == required_cycles and len(set(ids)) == required_cycles
            if passed and not evidence_complete:
                errors.append(f"gates.{name} cannot pass without 10 unique candidate-bound cycles")
        else:
            evidence = gate.get("evidence")
            if not isinstance(evidence, list):
                errors.append(f"gates.{name}.evidence must be an array")
                evidence = []
            evidence_complete = bool(evidence) and all(
                _valid_evidence(item, version, commit, name) for item in evidence
            )
            if passed and not evidence_complete:
                errors.append(f"gates.{name} cannot pass without candidate-bound real-device evidence")
        computed_pass[name] = bool(passed and evidence_complete)

    computed_ready = all(computed_pass.get(name, False) for name in REQUIRED_GATES)
    if document.get("ready") is not computed_ready:
        errors.append(f"ready must equal computed gate result ({str(computed_ready).lower()})")

    if release_report is not None:
        if not isinstance(release_report, dict):
            errors.append("release report must be an object")
        else:
            beta = release_report.get("beta_gate_status", {})
            blockers = beta.get("blocking_items") if isinstance(beta, dict) else None
            expected_blockers = [name for name in REQUIRED_GATES if not computed_pass.get(name, False)]
            if release_report.get("package_version") != version:
                errors.append("release report package_version must match candidate_version")
            if release_report.get("candidate_commit") != commit:
                errors.append("release report candidate_commit must match candidate_commit")
            if release_report.get("public_beta_ready") is not computed_ready:
                errors.append("release report public_beta_ready must match computed readiness")
            if not isinstance(beta, dict) or beta.get("ready") is not computed_ready:
                errors.append("release report beta_gate_status.ready must match computed readiness")
            if blockers != expected_blockers:
                errors.append("release report blocking_items must match incomplete matrix gates")
    return errors


def validate_files(matrix_path: Path, report_path: Path) -> dict[str, Any]:
    try:
        matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
        report = json.loads(report_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {"ok": False, "ready": False, "errors": [f"cannot read JSON: {exc}"]}
    errors = validate_contract(matrix, report)
    if not errors:
        root = matrix_path.resolve().parents[1]
        for name in REQUIRED_GATES:
            gate = matrix["gates"][name]
            items = (
                gate.get("cycles", [])
                if name == "ten_consecutive_real_project_cycles_on_frozen_candidate"
                else gate.get("evidence", [])
            )
            for index, item in enumerate(items):
                if isinstance(item, dict) and _valid_evidence(
                    item,
                    matrix["candidate_version"],
                    matrix["candidate_commit"],
                    name,
                ):
                    artifact_error = _artifact_error(item, root, f"gates.{name}[{index}]")
                    if artifact_error:
                        errors.append(artifact_error)
    return {
        "ok": not errors,
        "ready": bool(matrix.get("ready")) if isinstance(matrix, dict) else False,
        "blocking_gates": [
            name for name in REQUIRED_GATES
            if not isinstance(matrix.get("gates", {}).get(name), dict)
            or not matrix["gates"][name].get("passed", False)
        ],
        "errors": errors,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--matrix", default="docs/beta_evidence_matrix.json")
    parser.add_argument("--report", default="release/alpha_release_report.json")
    parser.add_argument("--require-ready", action="store_true")
    args = parser.parse_args(argv)
    result = validate_files(Path(args.matrix), Path(args.report))
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    if not result["ok"] or (args.require_ready and not result["ready"]):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

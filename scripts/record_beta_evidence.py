#!/usr/bin/env python3
"""Record one already-observed real-device Beta result without running a test."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any

from validate_beta_evidence import REQUIRED_GATES, _valid_evidence, validate_contract


CYCLE_GATE = "ten_consecutive_real_project_cycles_on_frozen_candidate"
ZERO_COUNTERS = ("outside_wakeups", "duplicate_sends", "cross_chat_reads", "replacement_tasks")


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _inside_evidence_root(path: Path, root: Path) -> bool:
    try:
        return (
            not path.is_symlink()
            and path.is_file()
            and path.resolve().is_relative_to((root / "evidence" / "beta").resolve())
        )
    except OSError:
        return False


def prepare_update(
    matrix: Any,
    evidence: Any,
    artifact: str,
    sha256: str,
    gate_name: str,
) -> tuple[Any, list[str]]:
    errors: list[str] = []
    if not isinstance(matrix, dict) or not isinstance(evidence, dict):
        return matrix, ["matrix and evidence must be objects"]
    if "artifact" in evidence or "sha256" in evidence:
        return matrix, ["raw evidence must not contain controller-owned artifact or sha256 fields"]
    if gate_name not in REQUIRED_GATES:
        return matrix, ["gate must be one of the six required Beta gates"]
    record = dict(evidence)
    record["artifact"] = artifact
    record["sha256"] = sha256
    version = matrix.get("candidate_version")
    commit = matrix.get("candidate_commit")
    if record.get("candidate_version") != version or record.get("candidate_commit") != commit:
        errors.append("evidence candidate must match the frozen matrix candidate")
    if record.get("gate") != gate_name:
        errors.append("evidence gate must match the requested gate")
    if record.get("result") not in {"pass", "fail"}:
        errors.append("evidence result must be pass or fail")
    probe = dict(record)
    probe["result"] = "pass"
    if not _valid_evidence(probe, version, commit):
        errors.append("evidence is missing required real-device identity fields")
    if errors:
        return matrix, errors

    updated = json.loads(json.dumps(matrix))
    gate = updated["gates"][gate_name]
    failures = gate.setdefault("failures", [])
    if record["result"] == "fail":
        failures.append(record)
        gate["passed"] = False
        if gate_name == CYCLE_GATE:
            gate["cycles"] = []
        else:
            gate["evidence"] = []
    elif gate_name == CYCLE_GATE:
        if not all(record.get(field) == 0 for field in ZERO_COUNTERS):
            return matrix, ["a passing cycle requires all four safety counters to be zero"]
        cycles = gate.setdefault("cycles", [])
        if record["id"] in {item.get("id") for item in cycles if isinstance(item, dict)}:
            return matrix, ["evidence id is already recorded"]
        cycles.append(record)
        required = updated["required_consecutive_cycles"]
        if len(cycles) > required:
            del cycles[:-required]
        gate["passed"] = len(cycles) == required
    else:
        evidence_items = gate.setdefault("evidence", [])
        if record["id"] in {item.get("id") for item in evidence_items if isinstance(item, dict)}:
            return matrix, ["evidence id is already recorded"]
        evidence_items.append(record)
        gate["passed"] = True

    updated["ready"] = all(updated["gates"][name].get("passed") is True for name in REQUIRED_GATES)
    errors.extend(validate_contract(updated))
    return updated, errors


def record_file(matrix_path: Path, evidence_path: Path, gate_name: str) -> dict[str, Any]:
    root = matrix_path.resolve().parents[1]
    if not _inside_evidence_root(evidence_path, root):
        return {"ok": False, "errors": ["evidence file must be a regular file under evidence/beta"]}
    try:
        matrix = _load(matrix_path)
        evidence = _load(evidence_path)
        raw = evidence_path.read_bytes()
    except (OSError, json.JSONDecodeError) as exc:
        return {"ok": False, "errors": [f"cannot read input: {exc}"]}
    artifact = evidence_path.resolve().relative_to(root).as_posix()
    updated, errors = prepare_update(matrix, evidence, artifact, hashlib.sha256(raw).hexdigest(), gate_name)
    if errors:
        return {"ok": False, "errors": errors}
    payload = json.dumps(updated, ensure_ascii=False, indent=2) + "\n"
    matrix_path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{matrix_path.name}.", dir=matrix_path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, matrix_path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    return {"ok": True, "ready": updated["ready"], "gate": gate_name}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--matrix", default="docs/beta_evidence_matrix.json")
    parser.add_argument("--gate", required=True, choices=REQUIRED_GATES)
    parser.add_argument("--evidence", required=True)
    args = parser.parse_args(argv)
    result = record_file(Path(args.matrix), Path(args.evidence), args.gate)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())

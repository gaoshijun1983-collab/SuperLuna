from __future__ import annotations

import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "beta_evidence_validator", ROOT / "scripts" / "validate_beta_evidence.py"
)
validator = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(validator)


class BetaEvidenceValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.matrix = json.loads((ROOT / "docs" / "beta_evidence_matrix.json").read_text(encoding="utf-8"))
        cls.report = json.loads((ROOT / "release" / "alpha_release_report.json").read_text(encoding="utf-8"))

    def test_repository_beta_truth_is_consistent_and_blocked(self):
        errors = validator.validate_contract(self.matrix, self.report)
        self.assertEqual(errors, [])
        self.assertFalse(self.matrix["ready"])

    def test_local_or_mock_evidence_cannot_pass_real_device_gate(self):
        matrix = copy.deepcopy(self.matrix)
        gate = matrix["gates"]["windows_in_app_browser_full_loop"]
        gate["passed"] = True
        gate["evidence_scope"] = "local_only"
        errors = validator.validate_contract(matrix)
        self.assertIn(
            "gates.windows_in_app_browser_full_loop.evidence_scope must be real_device",
            errors,
        )

    def test_gate_cannot_pass_with_empty_evidence(self):
        matrix = copy.deepcopy(self.matrix)
        matrix["gates"]["macos_in_app_browser_version_matrix"]["passed"] = True
        errors = validator.validate_contract(matrix)
        self.assertIn(
            "gates.macos_in_app_browser_version_matrix cannot pass without candidate-bound real-device evidence",
            errors,
        )

    def test_cycles_require_ten_unique_candidate_bound_records(self):
        matrix = copy.deepcopy(self.matrix)
        gate = matrix["gates"]["ten_consecutive_real_project_cycles_on_frozen_candidate"]
        gate["passed"] = True
        sample = {
            "id": "cycle-1", "platform": "macos", "observed_at": "2026-08-15T00:00:00Z",
            "os_version": "macOS test", "codex_version": "Codex test", "result": "pass",
            "artifact": "evidence/cycle-1.json", "sha256": "a" * 64,
            "candidate_version": matrix["candidate_version"],
            "candidate_commit": matrix["candidate_commit"],
            "outside_wakeups": 0, "duplicate_sends": 0,
            "cross_chat_reads": 0, "replacement_tasks": 0,
        }
        gate["cycles"] = [sample] * 10
        errors = validator.validate_contract(matrix)
        self.assertIn(
            "gates.ten_consecutive_real_project_cycles_on_frozen_candidate cannot pass without 10 unique candidate-bound cycles",
            errors,
        )

    def test_release_report_cannot_claim_beta_early(self):
        report = copy.deepcopy(self.report)
        report["public_beta_ready"] = True
        report["beta_gate_status"]["ready"] = True
        errors = validator.validate_contract(self.matrix, report)
        self.assertIn("release report public_beta_ready must match computed readiness", errors)
        self.assertIn("release report beta_gate_status.ready must match computed readiness", errors)

    def test_cycle_with_outside_wakeup_cannot_count(self):
        matrix = copy.deepcopy(self.matrix)
        gate = matrix["gates"]["ten_consecutive_real_project_cycles_on_frozen_candidate"]
        gate["passed"] = True
        gate["cycles"] = []
        for index in range(10):
            gate["cycles"].append({
                "id": f"cycle-{index}", "platform": "macos",
                "os_version": "macOS test", "codex_version": "Codex test",
                "observed_at": "2026-08-15T00:00:00Z", "result": "pass",
                "artifact": f"evidence/cycle-{index}.json", "sha256": "a" * 64,
                "candidate_version": matrix["candidate_version"],
                "candidate_commit": matrix["candidate_commit"],
                "outside_wakeups": 1 if index == 9 else 0,
                "duplicate_sends": 0, "cross_chat_reads": 0, "replacement_tasks": 0,
            })
        errors = validator.validate_contract(matrix)
        self.assertIn(
            "gates.ten_consecutive_real_project_cycles_on_frozen_candidate cannot pass without 10 unique candidate-bound cycles",
            errors,
        )

    def test_file_validation_rejects_a_missing_evidence_artifact(self):
        matrix = copy.deepcopy(self.matrix)
        gate = matrix["gates"]["windows_in_app_browser_full_loop"]
        gate["passed"] = True
        gate["evidence"] = [{
            "id": "windows-loop", "platform": "windows",
            "os_version": "Windows test", "codex_version": "Codex test",
            "observed_at": "2026-08-15T00:00:00Z", "result": "pass",
            "artifact": "evidence/missing.json", "sha256": "a" * 64,
            "candidate_version": matrix["candidate_version"],
            "candidate_commit": matrix["candidate_commit"],
        }]
        report = copy.deepcopy(self.report)
        report["beta_gate_status"]["blocking_items"].remove("windows_in_app_browser_full_loop")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "docs").mkdir()
            (root / "release").mkdir()
            matrix_path = root / "docs" / "beta_evidence_matrix.json"
            report_path = root / "release" / "alpha_release_report.json"
            matrix_path.write_text(json.dumps(matrix), encoding="utf-8")
            report_path.write_text(json.dumps(report), encoding="utf-8")
            result = validator.validate_files(matrix_path, report_path)
        self.assertFalse(result["ok"])
        self.assertIn(
            "gates.windows_in_app_browser_full_loop[0].artifact must be a regular repository file",
            result["errors"],
        )


if __name__ == "__main__":
    unittest.main()

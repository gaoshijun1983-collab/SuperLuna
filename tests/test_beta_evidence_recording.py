from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))
SPEC = importlib.util.spec_from_file_location("beta_evidence_recorder", SCRIPTS / "record_beta_evidence.py")
recorder = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(recorder)


class BetaEvidenceRecordingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.matrix = json.loads((ROOT / "docs" / "beta_evidence_matrix.json").read_text(encoding="utf-8"))

    def evidence(self, identifier: str, result: str = "pass"):
        return {
            "id": identifier,
            "gate": recorder.CYCLE_GATE,
            "source": "real_device",
            "platform": "macos",
            "os_version": "macOS test",
            "codex_version": "Codex test",
            "observed_at": "2026-08-15T00:00:00Z",
            "result": result,
            "candidate_version": self.matrix["candidate_version"],
            "candidate_commit": self.matrix["candidate_commit"],
            "outside_wakeups": 0,
            "duplicate_sends": 0,
            "cross_chat_reads": 0,
            "replacement_tasks": 0,
        }

    def test_ten_unique_clean_cycles_complete_the_cycle_gate(self):
        matrix = json.loads(json.dumps(self.matrix))
        for index in range(10):
            matrix, errors = recorder.prepare_update(
                matrix, self.evidence(f"cycle-{index}"),
                f"evidence/beta/cycle-{index}.json", "a" * 64, recorder.CYCLE_GATE,
            )
            self.assertEqual(errors, [])
        self.assertTrue(matrix["gates"][recorder.CYCLE_GATE]["passed"])
        self.assertEqual(len(matrix["gates"][recorder.CYCLE_GATE]["cycles"]), 10)

    def test_failed_cycle_resets_the_consecutive_streak(self):
        matrix, errors = recorder.prepare_update(
            self.matrix, self.evidence("cycle-1"),
            "evidence/beta/cycle-1.json", "a" * 64, recorder.CYCLE_GATE,
        )
        self.assertEqual(errors, [])
        matrix, errors = recorder.prepare_update(
            matrix, self.evidence("cycle-fail", "fail"),
            "evidence/beta/cycle-fail.json", "b" * 64, recorder.CYCLE_GATE,
        )
        self.assertEqual(errors, [])
        self.assertEqual(matrix["gates"][recorder.CYCLE_GATE]["cycles"], [])
        self.assertFalse(matrix["gates"][recorder.CYCLE_GATE]["passed"])

    def test_nonzero_safety_counter_cannot_record_a_pass(self):
        evidence = self.evidence("cycle-unsafe")
        evidence["duplicate_sends"] = 1
        _, errors = recorder.prepare_update(
            self.matrix, evidence, "evidence/beta/cycle-unsafe.json", "a" * 64,
            recorder.CYCLE_GATE,
        )
        self.assertIn("a passing cycle requires all four safety counters to be zero", errors)

    def test_candidate_mismatch_is_rejected(self):
        evidence = self.evidence("cycle-wrong")
        evidence["candidate_commit"] = "f" * 40
        _, errors = recorder.prepare_update(
            self.matrix, evidence, "evidence/beta/cycle-wrong.json", "a" * 64,
            recorder.CYCLE_GATE,
        )
        self.assertIn("evidence candidate must match the frozen matrix candidate", errors)

    def test_raw_evidence_cannot_predeclare_controller_owned_fields(self):
        evidence = self.evidence("cycle-reserved")
        evidence["artifact"] = "evidence/beta/forged.json"
        evidence["sha256"] = "a" * 64
        _, errors = recorder.prepare_update(
            self.matrix, evidence, "evidence/beta/cycle-reserved.json", "b" * 64,
            recorder.CYCLE_GATE,
        )
        self.assertEqual(
            errors,
            ["raw evidence must not contain controller-owned artifact or sha256 fields"],
        )

    def test_file_outside_evidence_beta_is_rejected_without_matrix_write(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "docs").mkdir()
            matrix_path = root / "docs" / "beta_evidence_matrix.json"
            matrix_path.write_text(json.dumps(self.matrix), encoding="utf-8")
            outside = root / "outside.json"
            outside.write_text(json.dumps(self.evidence("outside")), encoding="utf-8")
            before = matrix_path.read_bytes()
            result = recorder.record_file(matrix_path, outside, recorder.CYCLE_GATE)
            after = matrix_path.read_bytes()
        self.assertFalse(result["ok"])
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()

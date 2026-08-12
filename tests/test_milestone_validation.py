from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("milestone_validator", ROOT / "scripts" / "validate_milestones.py")
validator = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(validator)


class MilestoneValidationTests(unittest.TestCase):
    def test_repository_contract_is_valid(self):
        result = validator.validate_file(ROOT / "docs" / "milestones.json")
        self.assertTrue(result["ok"], result["errors"])
        self.assertEqual(result["milestones"], 1)

    def test_missing_rollback_section_fails(self):
        document = {"contract_version": "1", "milestones": [{"version": "1.0.0"}]}
        errors = validator.validate_contract(document)
        self.assertIn("milestones[0] missing rollback_steps", errors)
        self.assertIn("milestones[0] missing rollback_triggers", errors)

    def test_empty_verification_fails(self):
        document = {
            "contract_version": "1",
            "milestones": [{
                "version": "1.0.0", "upgrade_prerequisites": ["ready"],
                "rollback_triggers": ["failure"], "rollback_steps": ["restore"],
                "verification": [], "evidence_scope": "local_only",
            }],
        }
        self.assertIn("milestones[0].verification must be a non-empty list of strings", validator.validate_contract(document))

    def test_local_only_scope_cannot_claim_real_device_or_beta_evidence(self):
        document = json.loads((ROOT / "docs" / "milestones.json").read_text(encoding="utf-8"))
        document["milestones"][0]["real_device_evidence"] = True
        document["milestones"][0]["public_beta_evidence"] = True
        errors = validator.validate_contract(document)
        self.assertIn(
            "milestones[0] local_only scope cannot claim real-device or Public Beta evidence",
            errors,
        )

    def test_alpha_can_record_real_device_evidence_without_claiming_public_beta(self):
        document = json.loads((ROOT / "docs" / "milestones.json").read_text(encoding="utf-8"))
        milestone = document["milestones"][0]
        milestone["evidence_scope"] = "real_device"
        milestone["real_device_evidence"] = True
        self.assertEqual(validator.validate_contract(document), [])


if __name__ == "__main__":
    unittest.main()

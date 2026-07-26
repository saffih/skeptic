from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "validation"))

from validate_current_main_artifacts import classify_terminal, validate_scenario_manifest


class CurrentMainValidationContractTests(unittest.TestCase):
    def test_scenario_manifest_is_complete(self) -> None:
        path = ROOT / "validation/current-main-20260726/scenario-manifest.json"
        self.assertEqual(validate_scenario_manifest(path), [])

    def test_each_terminal_state_maps_uniquely(self) -> None:
        base = {
            "infrastructure_valid": True,
            "runtime_blocked": False,
            "owner_decision_required": False,
            "critical_material_losses": 0,
            "candidate_only_dangerous_failures": 0,
            "noncritical_material_losses": 0,
            "material_negative_control_growth": False,
            "incomparable_required_scenarios": 0,
            "material_judge_inconsistency": False,
            "all_required_families_valid": True,
        }
        cases = [
            ({**base, "infrastructure_valid": False}, "VALIDATION_INFRASTRUCTURE_DEFECT"),
            ({**base, "runtime_blocked": True}, "MODEL_CREDITS_OR_RUNTIME_BLOCKED"),
            ({**base, "owner_decision_required": True}, "OWNER_DECISION_REQUIRED"),
            ({**base, "critical_material_losses": 1}, "CURRENT_MAIN_REGRESSION_FOUND"),
            ({**base, "incomparable_required_scenarios": 1}, "CURRENT_MAIN_VALIDATION_INCONCLUSIVE"),
            (base, "CURRENT_MAIN_BEHAVIORALLY_SUPPORTED"),
        ]
        for record, expected in cases:
            with self.subTest(expected=expected):
                self.assertEqual(classify_terminal(record), expected)


if __name__ == "__main__":
    unittest.main()

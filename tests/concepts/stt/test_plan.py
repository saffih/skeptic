from __future__ import annotations

import unittest

from concepts.stt.contracts import DEFAULT_LIMITS
from concepts.stt.errors import STTError
from concepts.stt.plan import validate_plan


class PlanTests(unittest.TestCase):
    def base(self):
        return {
            "schema_version": 1,
            "mission_sha256": "m" * 64,
            "baseline_id": "base",
            "objective": "repair",
            "done": [
                {"id": "tests", "kind": "deterministic_predicate", "predicate_id": "all_declared_final_commands_succeeded", "subject_ref": "final_evidence"},
                {"id": "objective", "kind": "reviewer_claim", "claim_id": "mission_objective_satisfied", "subject_ref": "frozen_final_candidate"},
                {"id": "clean", "kind": "reviewer_claim", "claim_id": "final_find_loop_clean", "subject_ref": "frozen_final_candidate"},
            ],
            "steps": [{"id": "validate", "kind": "validation", "commands": [{"tool_id": "python", "args": ["-m", "unittest"], "cwd": ".", "timeout_seconds": 10, "accepted_exit_codes": [0]}]}],
        }

    def test_valid(self):
        validate_plan(self.base(), mission_sha256="m" * 64, baseline_id="base", catalog_ids={"python"}, source_paths=["/source", "/state"], limits=DEFAULT_LIMITS)

    def test_unknown_done_rejected(self):
        plan = self.base(); plan["done"][0]["predicate_id"] = "invented"
        with self.assertRaises(STTError):
            validate_plan(plan, mission_sha256="m" * 64, baseline_id="base", catalog_ids={"python"}, source_paths=[], limits=DEFAULT_LIMITS)

    def test_python_inline_code_rejected(self):
        plan = self.base(); plan["steps"][0]["commands"][0]["args"] = ["-c", "print(1)"]
        with self.assertRaises(STTError):
            validate_plan(plan, mission_sha256="m" * 64, baseline_id="base", catalog_ids={"python"}, source_paths=[], limits=DEFAULT_LIMITS)

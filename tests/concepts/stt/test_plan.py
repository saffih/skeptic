from __future__ import annotations

import unittest

from concepts.stt.contracts import DEFAULT_LIMITS
from concepts.stt.errors import STTError
from concepts.stt.plan import validate_plan


class PlanTests(unittest.TestCase):
    def base(self) -> dict:
        return {
            "schema_version": 2,
            "mission_sha256": "m" * 64,
            "baseline_id": "base",
            "objective": "repair",
            "delivery_kind": "workspace_change",
            "done": [
                {"id": "tests", "kind": "deterministic_predicate", "predicate_id": "all_declared_final_commands_succeeded", "subject_ref": "final_evidence"},
                {"id": "paths", "kind": "deterministic_predicate", "predicate_id": "changed_paths_bound_to_workspace", "subject_ref": "final_evidence"},
                {"id": "objective", "kind": "reviewer_claim", "claim_id": "mission_objective_satisfied", "subject_ref": "frozen_final_candidate"},
                {"id": "clean", "kind": "reviewer_claim", "claim_id": "final_find_loop_clean", "subject_ref": "frozen_final_candidate"},
            ],
            "steps": [{"id": "validate", "kind": "validation", "commands": [{"tool_id": "python", "args": ["-m", "unittest"], "cwd": ".", "timeout_seconds": 10, "accepted_exit_codes": [0]}]}],
        }

    def validate(self, plan: dict, **kwargs: object) -> dict:
        return validate_plan(
            plan,
            mission_sha256="m" * 64,
            baseline_id="base",
            catalog_ids={"python"},
            source_paths=["/source", "/state"],
            limits=DEFAULT_LIMITS,
            **kwargs,
        )

    def test_exact_v2_plan_is_valid(self):
        self.validate(self.base())

    def test_schema_v1_is_rejected(self):
        plan = self.base(); plan["schema_version"] = 1
        with self.assertRaises(STTError) as caught:
            self.validate(plan)
        self.assertEqual(caught.exception.code, "PLAN_SCHEMA")

    def test_unknown_done_rejected(self):
        plan = self.base(); plan["done"][0]["predicate_id"] = "invented"
        with self.assertRaises(STTError):
            self.validate(plan)

    def test_malformed_unhashable_plan_fields_are_bounded_errors(self):
        mutations = (
            ("delivery", lambda plan: plan.update(delivery_kind=[])),
            ("done-id", lambda plan: plan["done"][0].update(id=[])),
            ("predicate", lambda plan: plan["done"][0].update(predicate_id=[])),
            ("tool", lambda plan: plan["steps"][0]["commands"][0].update(tool_id=[])),
        )
        for label, mutate in mutations:
            plan = self.base(); mutate(plan)
            with self.subTest(label=label), self.assertRaises(STTError):
                self.validate(plan)

    def test_python_inline_code_rejected(self):
        plan = self.base(); plan["steps"][0]["commands"][0]["args"] = ["-c", "print(1)"]
        with self.assertRaises(STTError):
            self.validate(plan)

    def test_inspect_delivery_rejects_change_step(self):
        plan = self.base(); plan["delivery_kind"] = "inspect"
        plan["done"] = [
            {"id": "inventory", "kind": "deterministic_predicate", "predicate_id": "inventory_scope_completed", "subject_ref": "inspect_report"},
            {"id": "bound", "kind": "reviewer_claim", "claim_id": "report_bound_to_baseline", "subject_ref": "inspect_report"},
            {"id": "objective", "kind": "reviewer_claim", "claim_id": "mission_objective_satisfied", "subject_ref": "frozen_final_candidate"},
            {"id": "clean", "kind": "reviewer_claim", "claim_id": "final_find_loop_clean", "subject_ref": "frozen_final_candidate"},
        ]
        plan["steps"] = [{"id": "change", "kind": "change", "route_profile": "standard", "objective": "bad", "read_scope": [{"path": "x", "kind": "file"}], "write_scope": [{"path": "x", "kind": "file"}], "validation_commands": []}]
        with self.assertRaises(STTError) as caught:
            self.validate(plan)
        self.assertEqual(caught.exception.code, "INSPECT_AUTHORITY_VIOLATION")

    def test_inspect_delivery_requires_inspection_or_child_result(self):
        plan = self.base(); plan["delivery_kind"] = "inspect"
        plan["done"] = [
            {"id": "inventory", "kind": "deterministic_predicate", "predicate_id": "inventory_scope_completed", "subject_ref": "inspect_report"},
            {"id": "bound", "kind": "reviewer_claim", "claim_id": "report_bound_to_baseline", "subject_ref": "inspect_report"},
            {"id": "objective", "kind": "reviewer_claim", "claim_id": "mission_objective_satisfied", "subject_ref": "frozen_final_candidate"},
            {"id": "clean", "kind": "reviewer_claim", "claim_id": "final_find_loop_clean", "subject_ref": "frozen_final_candidate"},
        ]
        with self.assertRaises(STTError) as caught:
            self.validate(plan)
        self.assertEqual(caught.exception.code, "PLAN_DONE")

    def test_inherited_read_only_authority_requires_inspect_delivery(self):
        with self.assertRaises(STTError) as caught:
            self.validate(self.base(), read_only_authority=True)
        self.assertEqual(caught.exception.code, "INSPECT_AUTHORITY_VIOLATION")

    def test_control_component_and_nested_repository_scopes_are_rejected(self):
        plan = self.base(); plan["steps"] = [{"id": "change", "kind": "change", "route_profile": "standard", "objective": "bad", "read_scope": [{"path": "src/.git/config", "kind": "file"}], "write_scope": [{"path": "vendor/file", "kind": "file"}], "validation_commands": []}]
        with self.assertRaises(STTError) as caught:
            self.validate(plan, nested_roots=("vendor",))
        self.assertIn(caught.exception.code, {"GIT_CONTROL_PATH_FORBIDDEN", "NESTED_REPOSITORY_SCOPE_FORBIDDEN"})

    def test_declared_write_scope_rejects_casefold_and_nfc_collisions(self):
        for left, right in (("Alpha.txt", "alpha.txt"), ("caf\u00e9.txt", "cafe\u0301.txt")):
            plan = self.base()
            plan["steps"] = [{
                "id": "change",
                "kind": "change",
                "route_profile": "standard",
                "objective": "reject alias",
                "read_scope": [],
                "write_scope": [{"path": left, "kind": "file"}, {"path": right, "kind": "file"}],
                "validation_commands": [],
            }]
            with self.subTest(left=left, right=right), self.assertRaises(STTError) as caught:
                self.validate(plan)
            self.assertEqual(caught.exception.code, "PATH_ALIAS_COLLISION")

    def test_step_id_cannot_escape_transition_artifact_paths(self):
        plan = self.base(); plan["steps"][0]["id"] = "../../escape"
        with self.assertRaises(STTError) as caught:
            self.validate(plan)
        self.assertEqual(caught.exception.code, "PLAN_STEP_ID")


if __name__ == "__main__":
    unittest.main()

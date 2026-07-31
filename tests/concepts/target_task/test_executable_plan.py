import tempfile
import unittest
from pathlib import Path

from concepts.target_task.executable_plan import (
    ExecutablePlanError,
    load_execution_manifest,
    persist_execution_manifest,
    validate_execution_manifest, validate_step_references,
)
from concepts.target_task.store import persist_plan_artifact, write_immutable_artifact


class ExecutablePlanTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.instruction = write_immutable_artifact(
            self.root, "instructions/s1.md", b"do it\n",
            reference_id="instruction", artifact_type="step_instruction",
            description="instruction", read_condition="worker",
        )
        self.contract = write_immutable_artifact(
            self.root, "contracts/s1.json", b"{}\n",
            reference_id="contract", artifact_type="output_contract",
            description="contract", read_condition="Boundary",
        )
        self.plan = {
            "schema_version": "1", "plan_id": "p", "task_id": "t",
            "mission_sha256": "a" * 64,
            "steps": [{
                "step_id": "s1", "objective": "do it", "role": "worker",
                "success_criteria": ["done"],
            }],
        }
        self.plan_ref = persist_plan_artifact(self.root, self.plan)

    def tearDown(self):
        self.tmp.cleanup()

    def manifest(self):
        return {
            "schema_version": "1", "task_id": "t",
            "sealed_plan_sha256": self.plan_ref["sha256"],
            "steps": [{
                "step_id": "s1", "objective": "do it", "role": "worker",
                "instruction_ref": self.instruction,
                "task_artifact_references": [], "source_artifact_references": [],
                "retrieval_recipe_ref": None, "output_contract_ref": self.contract,
                "routing_profile": {"provider": "generic-recorded-host", "model_class": "small", "effort": "low", "timeout_seconds": 30, "budget": 0},
                "scope": "one file", "authority": "write-source",
                "prohibitions": [], "validation_commands": [],
                "success_criteria": ["done"],
                "result_manifest_directory": "results/manifests",
            }],
        }

    def test_persist_and_load_plan_bound_companion(self):
        ref = persist_execution_manifest(self.root, self.plan_ref, self.plan, self.manifest())
        loaded_ref, loaded = load_execution_manifest(self.root, self.plan_ref, self.plan)
        self.assertEqual(ref["sha256"], loaded_ref["sha256"])
        self.assertEqual(loaded["steps"][0]["instruction_ref"], self.instruction)

    def test_minimal_plan_without_companion_is_not_executable(self):
        with self.assertRaises(ExecutablePlanError):
            load_execution_manifest(self.root, self.plan_ref, self.plan)

    def test_missing_instruction_and_duplicate_reference_are_rejected(self):
        missing = self.manifest()
        del missing["steps"][0]["instruction_ref"]
        with self.assertRaises(ExecutablePlanError):
            validate_execution_manifest(missing, sealed_plan=self.plan)
        duplicate = self.manifest()
        duplicate["steps"][0]["task_artifact_references"] = [self.instruction]
        with self.assertRaises(ExecutablePlanError):
            validate_execution_manifest(duplicate, sealed_plan=self.plan)

    def test_plan_binding_is_exact(self):
        changed = self.manifest()
        changed["steps"][0]["objective"] = "reinterpret it"
        with self.assertRaises(ExecutablePlanError):
            validate_execution_manifest(changed, sealed_plan=self.plan)

    def test_task_and_source_roots_are_not_interchangeable(self):
        manifest = validate_execution_manifest(self.manifest(), sealed_plan=self.plan)
        manifest["steps"][0]["source_artifact_references"] = [self.instruction]
        with tempfile.TemporaryDirectory() as other:
            with self.assertRaises(Exception):
                validate_step_references(manifest["steps"][0], task_root=self.root, source_root=Path(other))


if __name__ == "__main__":
    unittest.main()

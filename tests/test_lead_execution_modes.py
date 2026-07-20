# made by AI
from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LEAD_PROMPT = ROOT / "agents" / "lead-agent-prompt.md"
GOVERNANCE = ROOT / "skeptic-tests.md"


def section(document: str, heading: str) -> str:
    match = re.search(
        rf"^{re.escape(heading)}\n(?P<body>.*?)(?=^##\s|\Z)",
        document,
        flags=re.MULTILINE | re.DOTALL,
    )
    if match is None:
        raise AssertionError(f"missing section: {heading}")
    return match.group("body")


class LeadExecutionModeContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.lead = LEAD_PROMPT.read_text(encoding="utf-8")
        cls.governance = GOVERNANCE.read_text(encoding="utf-8")
        cls.execution = section(cls.lead, "## Execution mode and package ownership")
        cls.resume = section(cls.lead, "## Checkpoint-first resume and closure fast path")
        cls.core = section(cls.lead, "## Core job")
        cls.scenarios = section(
            cls.governance,
            "### Lead execution-mode regression scenarios",
        )

    def test_execution_modes_are_distinct_and_routed_in_core_flow(self) -> None:
        for mode in ["DESIGN_PACKAGE", "EXECUTE_PACKAGE", "REPAIR_PACKAGE"]:
            self.assertIn(f"`{mode}`", self.execution)
            self.assertIn(f"`{mode}`", self.core)
        self.assertLess(
            self.lead.index("## Execution mode and package ownership"),
            self.lead.index("## Core job"),
        )

    def test_predesigned_package_is_operated_not_rebuilt(self) -> None:
        for behavior in [
            "validates and operates that package",
            "Execute through the supplied controller or primary command.",
            "does not rebuild the workflow inside the execution session",
        ]:
            self.assertIn(behavior, self.execution)
        self.assertRegex(
            self.scenarios,
            r"Predesigned benchmark package[\s\S]*?classify `EXECUTE_PACKAGE`[\s\S]*?run the supplied controller",
        )

    def test_incomplete_large_package_stops_before_replacement_runtime(self) -> None:
        required_artifacts = [
            "controller or primary command",
            "immutable inputs",
            "schemas",
            "validator",
            "durable state",
            "scoring or aggregation",
            "recovery or resume command",
        ]
        for artifact in required_artifacts:
            self.assertIn(artifact, self.execution)
        self.assertIn("return `PACKAGE_INCOMPLETE` before expensive execution", self.execution)
        self.assertIn("List the exact missing artifacts.", self.execution)
        self.assertIn("Do not improvise a substantial replacement runtime", self.execution)

    def test_small_reversible_task_avoids_package_ceremony(self) -> None:
        self.assertIn("A small bounded task may execute directly", self.execution)
        self.assertRegex(
            self.scenarios,
            r"Small one-off task[\s\S]*?execute directly without controller, agent team, or package ceremony",
        )

    def test_validator_repair_reuses_valid_expensive_outputs(self) -> None:
        for behavior in [
            "repair the checker",
            "revalidate existing outputs",
            "do not regenerate valid expensive work",
        ]:
            self.assertIn(behavior, self.execution)
        self.assertRegex(
            self.scenarios,
            r"Validator defect after successful generation[\s\S]*?repair the validator[\s\S]*?do not regenerate valid outputs",
        )

    def test_whole_batch_feasibility_precedes_launch(self) -> None:
        for behavior in [
            "entire phase plus verification, persistence, and closure",
            "Do not start a batch merely because its first calls fit.",
            "Pilot, reduce, hand off, or stop before the phase",
        ]:
            self.assertIn(behavior, self.execution)
        self.assertRegex(
            self.scenarios,
            r"Complete batch cannot fit[\s\S]*?do not launch the batch[\s\S]*?Generic context protection is not sufficient",
        )

    def test_receipts_and_operational_stop_preserve_skeptic_categories(self) -> None:
        for field in [
            "Execution mode",
            "Package completeness",
            "Primary command/controller",
            "Whole-phase feasibility",
            "Resume/recovery state",
        ]:
            self.assertIn(f"`{field}`", self.core)
        self.assertIn("operational stop reason", self.core)
        self.assertIn("not a new Skeptic", self.core)

    def test_checkpoint_state_precedes_resume_or_artifact_review(self) -> None:
        for behavior in [
            "read and verify the authoritative state or checkpoint before broad artifact review",
            "the highest completed phase",
            "the first incomplete phase",
            "A lifecycle written from phase zero does not authorize replay.",
        ]:
            self.assertIn(behavior, self.resume)
        for mode in ["EXECUTE_PACKAGE", "REPAIR_PACKAGE"]:
            self.assertRegex(
                self.core,
                rf"`{mode}`: read authoritative state first;[\s\S]*?resume at the first incomplete phase",
            )

    def test_closure_only_fills_missing_fields_without_replay(self) -> None:
        for behavior in [
            "When substantive work is complete, enter `CLOSURE_ONLY`",
            "Read only the authoritative checkpoint, final result, gap or missing-field ledger, and draft or final closure receipt.",
            "Fill missing receipt fields deterministically.",
            "Issue the Task Closure Receipt and stop.",
        ]:
            self.assertIn(behavior, self.resume)
        self.assertRegex(
            self.scenarios,
            r"Closure-only missing receipt fields[\s\S]*?enter `CLOSURE_ONLY`[\s\S]*?do not replay, recompute, call an advisor, or broadly read raw outputs",
        )

    def test_accepted_controller_result_is_verified_not_recomputed(self) -> None:
        for behavior in [
            "verify its identity, inputs, hash, acceptance, and required counts",
            "Do not recreate inventories, score tables, regression ledgers, or conclusions",
            "Open raw evidence only for a named unresolved dispute.",
        ]:
            self.assertIn(behavior, self.resume)
        self.assertRegex(
            self.scenarios,
            r"Accepted controller result needs no independent confirmation[\s\S]*?verify identity, inputs, hash, acceptance, and required counts[\s\S]*?without recomputation",
        )

    def test_checkpoint_invalidation_reopens_only_smallest_phase(self) -> None:
        for invalidation in [
            "a hash mismatch",
            "a corrupt or missing accepted artifact",
            "failed acceptance",
            "a changed immutable input",
            "contradictory authoritative state",
        ]:
            self.assertIn(invalidation, self.resume)
        for record in [
            "invalid checkpoint",
            "deterministic evidence",
            "smallest phase reopened",
            "preserved unaffected evidence",
            "renewed feasibility",
        ]:
            self.assertIn(record, self.resume)
        self.assertIn("Otherwise stop with `CHECKPOINT_CONFLICT`.", self.resume)

    def test_closure_ready_state_forbids_optional_advisor(self) -> None:
        self.assertIn(
            'do not initiate an advisor, Judge, extra review, new inventory, independent analysis, or "one more check"',
            self.resume,
        )
        self.assertRegex(
            self.scenarios,
            r"Optional advisor after closure-ready[\s\S]*?do not call the advisor; close",
        )

    def test_lifecycle_resumes_at_first_incomplete_phase(self) -> None:
        self.assertRegex(
            self.scenarios,
            r"Resume at the first incomplete phase[\s\S]*?P0-P5 complete[\s\S]*?start at P6 without replaying earlier phases",
        )

    def test_context_exhaustion_after_completion_is_failure(self) -> None:
        for failure in [
            "`prompt too long`",
            "session exhaustion",
            "forced compression",
            "unplanned handoff",
        ]:
            self.assertIn(failure, self.resume)
        self.assertRegex(
            self.scenarios,
            r"Context exhaustion after completion[\s\S]*?context protection as failed[\s\S]*?surviving artifacts do not make that Lead execution successful",
        )

    def test_resume_receipt_records_checkpoint_and_transition_state(self) -> None:
        for field in [
            "Authoritative checkpoint",
            "Highest completed phase",
            "First incomplete phase",
            "Closure-ready status",
            "Lead-context files opened and reason",
            "Remaining work",
            "Backward-transition authorization and evidence",
        ]:
            self.assertIn(f"`{field}`", self.resume)
            self.assertIn(f"`{field}`", self.core)


if __name__ == "__main__":
    unittest.main()

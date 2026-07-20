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


if __name__ == "__main__":
    unittest.main()

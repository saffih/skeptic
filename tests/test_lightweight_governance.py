from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
LEAD_PROMPT = ROOT / "agents" / "lead-agent-prompt.md"
TASK_PROMPT = ROOT / "agents" / "task-prompt.md"


class LightweightGovernanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.lead = LEAD_PROMPT.read_text(encoding="utf-8")
        cls.task = TASK_PROMPT.read_text(encoding="utf-8")
        cls.combined = cls.lead + "\n" + cls.task

    def test_plan_precedes_substantive_work(self) -> None:
        self.assertIn(
            "write a concise plan before substantive work",
            self.lead,
        )

    def test_runs_skeptic_once_on_the_plan_by_default(self) -> None:
        self.assertIn("RunSkeptic on the plan once", self.lead)
        self.assertIn(
            "RunSkeptic is primarily a planning check",
            self.lead,
        )

    def test_material_findings_are_resolved(self) -> None:
        self.assertIn("Resolve material findings", self.lead)

    def test_lead_may_execute_directly(self) -> None:
        self.assertIn("The Lead may execute work directly", self.lead)

    def test_delegation_is_optional_and_bounded(self) -> None:
        self.assertIn("Delegate when", self.lead)
        self.assertIn("Delegation is optional", self.task)
        self.assertIn("a bounded objective", self.lead)

    def test_deterministic_validation_is_the_default(self) -> None:
        self.assertIn("Prefer deterministic evidence", self.lead)
        self.assertIn(
            "Use the smallest validation set sufficient",
            self.lead,
        )

    def test_repeated_skeptic_review_is_conditional(self) -> None:
        self.assertIn("Run it again only when:", self.lead)
        self.assertIn(
            "Do not repeat it automatically",
            self.lead,
        )

    def test_harmless_output_does_not_invalidate_work(self) -> None:
        self.assertIn(
            "Useful work is not invalidated by harmless extra prose",
            self.lead,
        )
        self.assertIn(
            "Harmless extra prose or formatting differences do not invalidate useful work",
            self.task,
        )

    def test_task_prompt_uses_proportional_triggers(self) -> None:
        for heading in [
            "### Trivial read-only work",
            "### Small bounded change",
            "### Normal implementation",
            "### High-risk change",
            "### Material plan change",
        ]:
            with self.subTest(heading=heading):
                self.assertIn(heading, self.task)

    def test_removed_heavy_mechanisms_are_absent(self) -> None:
        removed = [
            "CONTEXT_BOUNDARY_VIOLATION",
            "CONTEXT_BOUNDARY_UNENFORCEABLE",
            "one orchestration transition",
            "three consecutive PASS",
            "exact receipt fields",
            "orchestration only",
        ]
        for phrase in removed:
            with self.subTest(phrase=phrase):
                self.assertNotIn(phrase, self.combined)


if __name__ == "__main__":
    unittest.main()

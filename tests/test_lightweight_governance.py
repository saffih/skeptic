from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
LEAD = (ROOT / "agents" / "lead-agent-prompt.md").read_text(encoding="utf-8")
TASK = (ROOT / "agents" / "task-prompt.md").read_text(encoding="utf-8")


class LightweightGovernanceTests(unittest.TestCase):
    def test_default_workflow(self) -> None:
        self.assertIn("RunSkeptic on the plan once", LEAD)
        self.assertIn("The Lead may execute work directly", LEAD)
        self.assertIn("smallest sufficient deterministic checks", TASK)

    def test_repeated_review_is_conditional(self) -> None:
        self.assertIn("Run it again only when:", LEAD)
        self.assertIn("Repeat RunSkeptic only after", TASK)

    def test_trivial_work_can_skip_process(self) -> None:
        self.assertIn("skip the formal plan and RunSkeptic", TASK)

    def test_heavy_governance_is_absent(self) -> None:
        combined = LEAD + TASK
        for phrase in [
            "CONTEXT_BOUNDARY_VIOLATION",
            "CONTEXT_BOUNDARY_UNENFORCEABLE",
            "three consecutive PASS",
            "orchestration only",
        ]:
            self.assertNotIn(phrase, combined)


if __name__ == "__main__":
    unittest.main()

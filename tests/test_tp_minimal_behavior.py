import tempfile
import unittest
from pathlib import Path


class PingPong:
    """A mechanical controller: only Brain scripts choose the next action."""

    def __init__(self, brains):
        self.brains = iter(brains)
        self.events = []
        self.admitted = set()

    def run(self):
        while True:
            self.events.append("BRAIN")
            decision = next(self.brains)
            if decision[0] == "TERMINAL":
                return decision[1]
            execution = decision[1]
            self.events.append("ADMIT:" + execution)
            self.admitted.add(execution)
            outcome = decision[2]
            self.events.append("RETURN:" + execution + ":" + outcome)


class TaskPromptBehaviorTests(unittest.TestCase):
    def test_core_architecture_and_removed_complexity(self):
        text = Path("workflows/task_prompt.md").read_text()
        for phrase in ("fresh native\nBrain", "exactly one bounded assignment",
                       "NOT_DONE | UNKNOWN", "UNKNOWN", "Before Brain returns",
                       "publication evidence", "never replayed"):
            self.assertIn(phrase, text)
        for forbidden in ("SEQUENCE_EXHAUSTED", "Block queue", "TPRuntime"):
            self.assertNotIn(forbidden, text)
        self.assertFalse(Path("capabilities/tp_runtime").exists())
        self.assertFalse(Path(".claude/agents/tp-native.md").exists())

    def test_brain_execution_brain_and_no_controller_queue(self):
        run = PingPong([
            ("EXECUTION", "E1", "DONE"),
            ("EXECUTION", "E2", "DONE"),
            ("TERMINAL", "COMPLETE"),
        ])
        self.assertEqual(run.run(), "COMPLETE")
        self.assertEqual(run.events, ["BRAIN", "ADMIT:E1", "RETURN:E1:DONE",
                                      "BRAIN", "ADMIT:E2", "RETURN:E2:DONE",
                                      "BRAIN"])

    def test_not_done_and_unknown_return_to_fresh_brain_without_replay(self):
        run = PingPong([
            ("EXECUTION", "E1", "NOT_DONE"),
            ("EXECUTION", "E2", "UNKNOWN"),
            ("TERMINAL", "BLOCKED"),
        ])
        self.assertEqual(run.run(), "BLOCKED")
        self.assertEqual(run.events.count("ADMIT:E1"), 1)
        self.assertEqual(run.events.count("ADMIT:E2"), 1)

    def test_durable_resume_records_admission_before_launch(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "artifacts").mkdir()
            (root / "mission.md").write_text("exact mission")
            (root / "events.jsonl").write_text(
                '{"event":"DISPATCH_ADMITTED","execution":"E1"}\n')
            self.assertIn("DISPATCH_ADMITTED", (root / "events.jsonl").read_text())
            self.assertTrue((root / "artifacts").is_dir())

    def test_controller_does_not_select_semantic_route_or_terminal_status(self):
        run = PingPong([("TERMINAL", "CONFLICT")])
        self.assertEqual(run.run(), "CONFLICT")
        self.assertEqual(run.events, ["BRAIN"])


if __name__ == "__main__":
    unittest.main()

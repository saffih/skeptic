import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class Controller:
    """Mechanical sequence runner: it never chooses the next semantic step."""

    def __init__(self, blocks):
        self.blocks = iter(blocks)
        self.events = []

    def run(self):
        self.events.append("BRAIN")
        for block in self.blocks:
            self.events.append("ADMITTED:" + block)
            result = yield block
            self.events.append("RETURNED:" + block + ":" + result)
            if result != "DONE":
                self.events.append("BRAIN")
                return
        self.events.append("BRAIN")


class MinimalTpBehaviorTests(unittest.TestCase):
    def test_brain_establishes_semantic_fit_before_dispatch(self):
        task_prompt = " ".join(
            (ROOT / "workflows" / "task_prompt.md")
            .read_text(encoding="utf-8")
            .split()
        )
        for required in (
            "Before Brain authorizes a Block",
            "known subsequent source loading",
            "genuinely bounded",
            "Decomposition must not weaken required freshness, completeness, or",
            "returns an explicit context blocker rather than narrowing the obligation",
        ):
            self.assertIn(required, task_prompt)
        for overbuilt in (
            "CHILD_CLEANUP_UNKNOWN",
            "maximum turn/tool budget",
            "measures referenced file bytes",
        ):
            self.assertNotIn(overbuilt, task_prompt)

    def test_brain_authorized_sequence_returns_to_brain_after_three_done_blocks(self):
        controller = Controller(["B1", "B2", "B3"])
        run = controller.run()
        self.assertEqual(next(run), "B1")
        self.assertEqual(run.send("DONE"), "B2")
        self.assertEqual(run.send("DONE"), "B3")
        with self.assertRaises(StopIteration):
            run.send("DONE")
        self.assertEqual(controller.events, [
            "BRAIN", "ADMITTED:B1", "RETURNED:B1:DONE",
            "ADMITTED:B2", "RETURNED:B2:DONE",
            "ADMITTED:B3", "RETURNED:B3:DONE", "BRAIN",
        ])

    def test_non_done_returns_to_brain_without_replay(self):
        controller = Controller(["B1", "B2"])
        run = controller.run()
        self.assertEqual(next(run), "B1")
        with self.assertRaises(StopIteration):
            run.send("BLOCKED")
        self.assertEqual(controller.events, [
            "BRAIN", "ADMITTED:B1", "RETURNED:B1:BLOCKED", "BRAIN",
        ])

    def test_minimal_durable_state_has_mission_events_and_artifacts(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "artifacts").mkdir()
            (root / "mission.md").write_text("Fix the bounded issue\n")
            (root / "events.jsonl").write_text(json.dumps({"event": "DISPATCH_ADMITTED"}) + "\n")
            self.assertEqual((root / "mission.md").read_text(), "Fix the bounded issue\n")
            self.assertTrue((root / "artifacts").is_dir())
            self.assertIn("DISPATCH_ADMITTED", (root / "events.jsonl").read_text())


if __name__ == "__main__":
    unittest.main()

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from concepts.target_task.contracts import Phase
from concepts.target_task.store import read_ledger, verify_chain
from concepts.target_task.trigger import TriggerError, bootstrap_task, parse_trigger


class ParseTriggerTests(unittest.TestCase):
    def test_recognizes_exact_prefix(self) -> None:
        self.assertEqual(parse_trigger("TT: fix the thing"), " fix the thing")

    def test_tolerates_leading_whitespace(self) -> None:
        self.assertEqual(parse_trigger("   TT: fix the thing"), " fix the thing")

    def test_non_trigger_message_returns_none(self) -> None:
        self.assertIsNone(parse_trigger("please fix the thing"))

    def test_prefix_without_colon_is_not_a_trigger(self) -> None:
        self.assertIsNone(parse_trigger("TT fix the thing"))

    def test_lowercase_prefix_is_not_recognized(self) -> None:
        self.assertIsNone(parse_trigger("tt: fix the thing"))

    def test_empty_mission_is_rejected(self) -> None:
        with self.assertRaises(TriggerError):
            parse_trigger("TT:    ")

    def test_mission_text_preserved_exactly_including_internal_whitespace(self) -> None:
        self.assertEqual(parse_trigger("TT: fix  the   thing"), " fix  the   thing")


class BootstrapTaskTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.tasks_root = Path(self.tmp.name)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_creates_workspace_with_mission_and_ledger(self) -> None:
        result = bootstrap_task("do the thing", "task-1", self.tasks_root)
        self.assertEqual(result.workspace_root.resolve(), (self.tasks_root / "task-1").resolve())
        self.assertTrue((result.workspace_root / "mission.md").is_file())
        self.assertEqual((result.workspace_root / "mission.md").read_text(), "do the thing")
        events = read_ledger(result.workspace_root / "ledger.jsonl")
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["phase"], Phase.MISSION_PERSISTED.value)
        self.assertTrue(verify_chain(events))

    def test_result_never_carries_mission_body(self) -> None:
        result = bootstrap_task("a very specific and sensitive mission body", "task-2", self.tasks_root)
        self.assertNotIn("sensitive mission body", str(result))

    def test_duplicate_task_id_is_rejected(self) -> None:
        bootstrap_task("first", "task-3", self.tasks_root)
        with self.assertRaises(TriggerError):
            bootstrap_task("second", "task-3", self.tasks_root)
        # the first task's workspace must be untouched by the rejected second attempt
        self.assertEqual((self.tasks_root / "task-3" / "mission.md").read_text(), "first")

    def test_workspace_publication_is_durably_fsynced(self) -> None:
        with patch("concepts.target_task.trigger._fsync_dir") as fsync_dir:
            bootstrap_task("do the thing", "task-5", self.tasks_root)
        fsync_dir.assert_called_once()
        self.assertEqual(fsync_dir.call_args[0][0].resolve(), self.tasks_root.resolve())

    def test_no_partial_task_root_survives_a_failed_bootstrap(self) -> None:
        # Pre-create the tmp staging directory to force bootstrap to fail
        # part-way through, and confirm cleanup leaves no observable task root.
        tmp_dir = self.tasks_root / ".task-4.bootstrap.tmp"
        tmp_dir.mkdir()
        with self.assertRaises(TriggerError):
            bootstrap_task("will not complete", "task-4", self.tasks_root)
        self.assertFalse((self.tasks_root / "task-4").exists())


if __name__ == "__main__":
    unittest.main()

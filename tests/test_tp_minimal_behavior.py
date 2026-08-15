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


class SafeHost:
    """Minimal model of the host-owned TP admission and child-lifecycle guards."""

    def __init__(self, expected_commit, expected_tp_blob):
        self.expected_commit = expected_commit
        self.expected_tp_blob = expected_tp_blob
        self.authority_bound = False
        self.active_child = None
        self.events = []

    def bind_authority(self, observed_commit, observed_tp_blob):
        if (observed_commit, observed_tp_blob) != (
            self.expected_commit,
            self.expected_tp_blob,
        ):
            self.events.append("AUTHORITY_REJECTED")
            return False
        self.authority_bound = True
        self.events.append("AUTHORITY_BOUND")
        return True

    def resume(self, observed_commit, observed_tp_blob):
        if not self.authority_bound:
            raise RuntimeError("AUTHORITY_NOT_BOUND")
        if (observed_commit, observed_tp_blob) != (
            self.expected_commit,
            self.expected_tp_blob,
        ):
            raise RuntimeError("AUTHORITY_CHANGED")
        self.events.append("AUTHORITY_RESUME_OK")

    def launch(self, invocation_id):
        if not self.authority_bound:
            raise RuntimeError("AUTHORITY_NOT_BOUND")
        if self.active_child is not None:
            raise RuntimeError("LIVE_CHILD_EXISTS")
        self.active_child = invocation_id
        self.events.append("LAUNCH:" + invocation_id)

    def reconcile(self, invocation_id, *, owned, abandoned):
        if owned and abandoned:
            self.events.append("REAP:" + invocation_id + ":ORPHAN")
            if self.active_child == invocation_id:
                self.active_child = None
            return True
        self.events.append("LEAVE:" + invocation_id)
        return False

    def reap(self, reason):
        if self.active_child is not None:
            self.events.append("REAP:" + self.active_child + ":" + reason)
            self.active_child = None


class TaskPromptBehaviorTests(unittest.TestCase):
    def test_core_architecture_and_removed_complexity(self):
        text = Path("workflows/task_prompt.md").read_text()
        for phrase in (
            "fresh native Brain",
            "exactly one bounded assignment",
            "NOT_DONE | UNKNOWN",
            "UNKNOWN",
            "Before Brain returns",
            "publication evidence",
            "never replayed",
            "tp-authority.md",
            "clean checkout is not proof",
            "finite host-enforced",
            "terminates and reaps",
        ):
            self.assertIn(phrase, text)
        for forbidden in (
            "SEQUENCE_EXHAUSTED",
            "Block queue",
            "TPRuntime",
            "next: SEQUENCE",
            "role: BLOCK",
        ):
            self.assertNotIn(forbidden, text)
        self.assertFalse(Path("capabilities/tp_runtime").exists())
        self.assertFalse(Path(".claude/agents/tp-native.md").exists())

    def test_host_observability_is_mechanical_and_non_authoritative(self):
        text = Path("workflows/task_prompt.md").read_text()
        for phrase in (
            "`events.jsonl` is the primary durable mechanical lifecycle evidence",
            "otherwise `UNKNOWN`",
            "watchdog stable process identities",
            "diagnostics.jsonl",
            "derived, non-authoritative",
            "never controller input",
            "contains no secrets, auth material, environment dumps, or",
            "never controls continuation or",
            "terminal status, contains no secrets",
        ):
            self.assertIn(phrase, text)
        for forbidden in (
            "TPRuntime",
            "role: BLOCK",
            "next: SEQUENCE",
        ):
            self.assertNotIn(forbidden, text)

    def test_brain_execution_brain_and_no_controller_queue(self):
        run = PingPong([
            ("EXECUTION", "E1", "DONE"),
            ("EXECUTION", "E2", "DONE"),
            ("TERMINAL", "COMPLETE"),
        ])
        self.assertEqual(run.run(), "COMPLETE")
        self.assertEqual(
            run.events,
            [
                "BRAIN",
                "ADMIT:E1",
                "RETURN:E1:DONE",
                "BRAIN",
                "ADMIT:E2",
                "RETURN:E2:DONE",
                "BRAIN",
            ],
        )

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
            (root / "tp-authority.md").write_text("exact TP authority")
            (root / "events.jsonl").write_text(
                '{"event":"DISPATCH_ADMITTED","execution":"E1"}\n'
            )
            self.assertIn(
                "DISPATCH_ADMITTED", (root / "events.jsonl").read_text()
            )
            self.assertTrue((root / "tp-authority.md").is_file())
            self.assertTrue((root / "artifacts").is_dir())

    def test_controller_does_not_select_semantic_route_or_terminal_status(self):
        run = PingPong([("TERMINAL", "CONFLICT")])
        self.assertEqual(run.run(), "CONFLICT")
        self.assertEqual(run.events, ["BRAIN"])

    def test_stale_but_clean_authority_is_rejected_before_launch(self):
        host = SafeHost(
            "11edab8dd1a005852bb9d685a377f66b5403a8e9",
            "e9369228615cbe975edf3ff48d0ef4734eeb6067",
        )
        self.assertFalse(
            host.bind_authority(
                "ba5c927603826f77347b0879b44615ddb410a6a7",
                "28e3138454c043b3624d0309679d18f3ef6dacbd",
            )
        )
        with self.assertRaisesRegex(RuntimeError, "AUTHORITY_NOT_BOUND"):
            host.launch("BRAIN-1")
        self.assertEqual(host.events, ["AUTHORITY_REJECTED"])

    def test_exact_authority_is_bound_before_launch(self):
        host = SafeHost(
            "11edab8dd1a005852bb9d685a377f66b5403a8e9",
            "e9369228615cbe975edf3ff48d0ef4734eeb6067",
        )
        self.assertTrue(
            host.bind_authority(
                "11edab8dd1a005852bb9d685a377f66b5403a8e9",
                "e9369228615cbe975edf3ff48d0ef4734eeb6067",
            )
        )
        host.launch("BRAIN-1")
        self.assertEqual(host.events, ["AUTHORITY_BOUND", "LAUNCH:BRAIN-1"])

    def test_live_child_blocks_duplicate_and_is_reaped(self):
        host = SafeHost(
            "11edab8dd1a005852bb9d685a377f66b5403a8e9",
            "e9369228615cbe975edf3ff48d0ef4734eeb6067",
        )
        host.bind_authority(
            "11edab8dd1a005852bb9d685a377f66b5403a8e9",
            "e9369228615cbe975edf3ff48d0ef4734eeb6067",
        )
        host.launch("EXECUTION-1")
        with self.assertRaisesRegex(RuntimeError, "LIVE_CHILD_EXISTS"):
            host.launch("EXECUTION-2")
        host.reap("DEADLINE")
        self.assertIsNone(host.active_child)
        host.launch("BRAIN-2")
        host.reap("TERMINAL")
        self.assertIsNone(host.active_child)

    def test_reconciliation_reaps_only_proven_tp_owned_orphans(self):
        host = SafeHost(
            "11edab8dd1a005852bb9d685a377f66b5403a8e9",
            "e9369228615cbe975edf3ff48d0ef4734eeb6067",
        )
        self.assertTrue(
            host.reconcile("OLD-TP-AGENT", owned=True, abandoned=True)
        )
        self.assertFalse(
            host.reconcile("UNRELATED-PROCESS", owned=False, abandoned=True)
        )
        self.assertEqual(
            host.events,
            ["REAP:OLD-TP-AGENT:ORPHAN", "LEAVE:UNRELATED-PROCESS"],
        )

    def test_resume_rejects_changed_authority(self):
        host = SafeHost(
            "11edab8dd1a005852bb9d685a377f66b5403a8e9",
            "e9369228615cbe975edf3ff48d0ef4734eeb6067",
        )
        host.bind_authority(
            "11edab8dd1a005852bb9d685a377f66b5403a8e9",
            "e9369228615cbe975edf3ff48d0ef4734eeb6067",
        )
        with self.assertRaisesRegex(RuntimeError, "AUTHORITY_CHANGED"):
            host.resume(
                "11edab8dd1a005852bb9d685a377f66b5403a8e9",
                "28e3138454c043b3624d0309679d18f3ef6dacbd",
            )

    def test_routing_stubs_do_not_reintroduce_block_sequence_model(self):
        agents = Path("AGENTS.md").read_text()
        brain = Path("agents/tp_brain.md").read_text()
        self.assertNotIn("bounded work blocks", agents)
        self.assertNotIn('"TP Brain" section', brain)
        self.assertIn("bounded Execution", agents)
        self.assertIn("tp_authority_ref", brain)


if __name__ == "__main__":
    unittest.main()

import json
import tempfile
import unittest
from pathlib import Path

from capabilities.tp_runtime.tp_runtime import DispatchOutcome, TPResultError, TPRuntime, parse_block_result, parse_brain_result


def brain(status, *, route="NONE", next_step="NONE", blocks="NONE"):
    return "\n".join(("TP_RESULT", "role: BRAIN", f"status: {status}", f"route: {route}", f"next: {next_step}", f"blocks: {blocks}", "reason: bounded test"))


def block(status, ref="B1", result_ref="NONE"):
    return "\n".join(("TP_RESULT", "role: BLOCK", f"status: {status}", f"block_ref: {ref}", f"result_ref: {result_ref}", "reason: bounded test"))


class ScriptedAdapter:
    def __init__(self, outcomes):
        self.outcomes = iter(outcomes)
        self.calls = []

    def __call__(self, role, route, packet):
        self.calls.append((role, route, packet["condition"]))
        return next(self.outcomes)


def returned(text):
    return DispatchOutcome(True, True, text)


class TPResultTests(unittest.TestCase):
    def test_brain_valid_forms(self):
        self.assertEqual(parse_brain_result(brain("CONTINUE", route="LOW", next_step="SEQUENCE", blocks="B1, B2"))["blocks"], ("B1", "B2"))
        for status in ("COMPLETE", "BLOCKED", "CONFLICT"):
            self.assertEqual(parse_brain_result(brain(status))["status"], status)

    def test_brain_invalid_forms_fail_closed(self):
        cases = (
            "TP_RESULT\nrole: BRAIN",
            brain("NOPE"),
            brain("CONTINUE", route="NONE", next_step="SEQUENCE", blocks="B1"),
            brain("COMPLETE", blocks="B1"),
            "not an envelope",
        )
        for value in cases:
            with self.subTest(value=value), self.assertRaises(TPResultError):
                parse_brain_result(value)

    def test_block_valid_and_invalid_forms(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "artifacts").mkdir()
            (root / "artifacts" / "result.md").write_text("evidence")
            self.assertEqual(parse_block_result(block("DONE", result_ref="artifacts/result.md"), assigned_block_ref="B1", run_root=root)["status"], "DONE")
            for status in ("BLOCKED", "CONFLICT"):
                self.assertEqual(parse_block_result(block(status), assigned_block_ref="B1", run_root=root)["status"], status)
            cases = (
                block("DONE", ref="other"),
                "TP_RESULT\nrole: BLOCK\nstatus: DONE",
                block("NOPE"),
                block("DONE", result_ref="artifacts/missing.md"),
                block("DONE", result_ref="mission.md"),
                "TP_RESULT\nrole: BLOCK\nstatus: DONE\nblock_ref: B1\nresult_ref: NONE",
            )
            for value in cases:
                with self.subTest(value=value), self.assertRaises(TPResultError):
                    parse_block_result(value, assigned_block_ref="B1", run_root=root)


class TPRuntimeTests(unittest.TestCase):
    def make_runtime(self, outcomes):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        root = Path(temp.name)
        repository = root / "repository"
        repository.mkdir()
        (repository / "keep.txt").write_text("untouched")
        adapter = ScriptedAdapter(outcomes)
        runtime = TPRuntime(repository, "one bounded mission\n", adapter, runtime_base=root / "external")
        return runtime, adapter, repository

    def events(self, runtime):
        return [json.loads(line) for line in (runtime.run_root / "events.jsonl").read_text().splitlines()]

    def test_external_state_persists_without_repository_run(self):
        runtime, _, repository = self.make_runtime([returned(brain("COMPLETE"))])
        self.assertEqual(runtime.run(), "COMPLETE")
        self.assertNotEqual(runtime.run_root.parents[2], repository)
        self.assertFalse((repository / "run").exists())
        self.assertEqual((repository / "keep.txt").read_text(), "untouched")
        self.assertEqual((runtime.run_root / "mission.md").read_text(), "one bounded mission\n")
        self.assertTrue((runtime.run_root / "artifacts").is_dir())
        identity = json.loads((runtime.run_root / "repository.json").read_text())
        self.assertEqual(identity["repository_root"], str(repository.resolve()))

    def test_ordered_done_sequence_then_brain_completion(self):
        runtime, adapter, _ = self.make_runtime([
            returned(brain("CONTINUE", route="MEDIUM", next_step="SEQUENCE", blocks="B1, B2")),
            returned(block("DONE", "B1")), returned(block("DONE", "B2")), returned(brain("COMPLETE")),
        ])
        self.assertEqual(runtime.run(), "COMPLETE")
        self.assertEqual([call[0] for call in adapter.calls], ["BRAIN", "BLOCK", "BLOCK", "BRAIN"])
        self.assertEqual([call[2] for call in adapter.calls], ["NORMAL", "BLOCK_ASSIGNED:B1", "BLOCK_ASSIGNED:B2", "SEQUENCE_EXHAUSTED"])

    def test_every_non_done_or_malformed_block_returns_to_brain(self):
        cases = (returned(block("BLOCKED")), returned(block("CONFLICT")), returned("not an envelope"), DispatchOutcome(True, True, None, "interrupted"))
        for outcome in cases:
            with self.subTest(outcome=outcome):
                runtime, adapter, _ = self.make_runtime([
                    returned(brain("CONTINUE", route="LOW", next_step="SEQUENCE", blocks="B1")), outcome, returned(brain("CONFLICT")),
                ])
                self.assertEqual(runtime.run(), "CONFLICT")
                self.assertEqual(adapter.calls[-1][0], "BRAIN")
                self.assertEqual(len([event for event in self.events(runtime) if event["event"] == "BLOCK_CONTROL_TO_BRAIN"]), 1)

    def test_artifact_is_preserved_but_malformed_control_is_not_interpreted(self):
        runtime, adapter, _ = self.make_runtime([])
        evidence = runtime.run_root / "artifacts" / "substantive.md"
        evidence.write_text("do not infer control from this")
        adapter.outcomes = iter([
            returned(brain("CONTINUE", route="LOW", next_step="SEQUENCE", blocks="B1")), returned("not an envelope"), returned(brain("BLOCKED")),
        ])
        self.assertEqual(runtime.run(), "BLOCKED")
        self.assertTrue(evidence.exists())
        self.assertIn("BLOCK_RESULT_INVALID", [event["event"] for event in self.events(runtime)])

    def test_admission_states_are_recorded_without_block_replay(self):
        cases = (
            DispatchOutcome(False, False, None, "rejected"),
            DispatchOutcome(True, False, None, "context too long"),
            DispatchOutcome(True, True, None, "failed after start"),
        )
        for failed in cases:
            with self.subTest(failed=failed):
                runtime, adapter, _ = self.make_runtime([
                    returned(brain("CONTINUE", route="LOW", next_step="SEQUENCE", blocks="B1")), failed, returned(brain("BLOCKED")),
                ])
                self.assertEqual(runtime.run(), "BLOCKED")
                self.assertEqual([call[0] for call in adapter.calls], ["BRAIN", "BLOCK", "BRAIN"])
                event_names = [event["event"] for event in self.events(runtime)]
                self.assertIn("BLOCK_CONTROL_TO_BRAIN", event_names)
                self.assertNotIn("BLOCK_RETURN_VALID", event_names)

    def test_invalid_brain_fails_closed(self):
        runtime, _, _ = self.make_runtime([returned("not an envelope")])
        self.assertEqual(runtime.run(), "BRAIN_REQUIRED")
        self.assertIn("BRAIN_RESULT_INVALID", [event["event"] for event in self.events(runtime)])


if __name__ == "__main__":
    unittest.main()

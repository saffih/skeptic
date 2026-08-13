import json
import tempfile
import unittest
from pathlib import Path

from capabilities.tp_runtime.tp_runtime import DispatchOutcome, TPResultError, TPRuntime, parse_block_result, parse_brain_result


def brain(status, *, route="NONE", next_step="NONE", blocks="NONE", result_ref=None, reason="bounded test"):
    if result_ref is None:
        result_ref = "NONE" if status == "CONTINUE" else "artifacts/brain-terminal.md"
    return "\n".join(("TP_RESULT", "role: BRAIN", f"status: {status}", f"route: {route}", f"next: {next_step}", f"blocks: {blocks}", f"result_ref: {result_ref}", f"reason: {reason}"))


def block(status, ref="artifacts/assignments/B1.md", result_ref=None, reason="bounded test"):
    if result_ref is None:
        result_ref = "artifacts/results/" + Path(ref).stem + ".md"
    return "\n".join(("TP_RESULT", "role: BLOCK", f"status: {status}", f"block_ref: {ref}", f"result_ref: {result_ref}", f"reason: {reason}"))


class ScriptedAdapter:
    def __init__(self, outcomes):
        self.outcomes = iter(outcomes)
        self.calls = []

    def __call__(self, role, route, packet):
        self.calls.append((role, route, dict(packet)))
        return next(self.outcomes)


def returned(text):
    return DispatchOutcome(True, True, text)


class TPResultTests(unittest.TestCase):
    def test_brain_valid_forms(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "artifacts" / "assignments").mkdir(parents=True)
            (root / "artifacts" / "brain-terminal.md").write_text("terminal report")
            for name in ("B1.md", "B2.md"):
                (root / "artifacts" / "assignments" / name).write_text("bounded assignment")
            (root / "artifacts" / "results").mkdir()
            (root / "artifacts" / "results" / "escalation.md").write_text("durable handoff")
            refs = "artifacts/assignments/B1.md, artifacts/assignments/B2.md"
            self.assertEqual(parse_brain_result(brain("CONTINUE", route="LOW", next_step="SEQUENCE", blocks=refs), run_root=root)["blocks"], tuple(refs.split(", ")))
            self.assertEqual(parse_brain_result(brain("CONTINUE", route="STRONG", next_step="BRAIN", result_ref="artifacts/results/escalation.md"), run_root=root)["next"], "BRAIN")
            for status in ("COMPLETE", "BLOCKED", "CONFLICT"):
                self.assertEqual(parse_brain_result(brain(status), run_root=root)["status"], status)
            self.assertEqual(parse_brain_result(brain("COMPLETE", result_ref="NONE"), run_root=root)["result_ref"], "NONE")

    def test_brain_invalid_forms_fail_closed(self):
        cases = (
            "TP_RESULT\nrole: BRAIN",
            brain("NOPE"),
            brain("CONTINUE", route="NONE", next_step="SEQUENCE", blocks="artifacts/assignment.md"),
            "\n".join(line for line in brain("CONTINUE", route="LOW", next_step="SEQUENCE", blocks="artifacts/assignment.md").splitlines() if not line.startswith("route: ")),
            brain("CONTINUE", route="LOW", next_step="BRAIN", result_ref="artifacts/brain-terminal.md"),
            brain("CONTINUE", route="MEDIUM", next_step="BRAIN", result_ref="artifacts/brain-terminal.md"),
            brain("CONTINUE", route="NONE", next_step="BRAIN", result_ref="artifacts/brain-terminal.md"),
            brain("CONTINUE", route="STRONG", next_step="BRAIN"),
            brain("CONTINUE", route="STRONG", next_step="BRAIN", result_ref="artifacts/results/missing.md"),
            brain("CONTINUE", route="STRONG", next_step="BRAIN", blocks="artifacts/assignments/B1.md", result_ref="artifacts/brain-terminal.md"),
            brain("COMPLETE", blocks="B1"),
            "not an envelope",
        )
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "artifacts").mkdir()
            (root / "artifacts" / "brain-terminal.md").write_text("report")
            for value in cases:
                with self.subTest(value=value), self.assertRaises(TPResultError):
                    parse_brain_result(value, run_root=root)

    def test_block_valid_and_invalid_forms(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "artifacts" / "assignments").mkdir(parents=True)
            (root / "artifacts" / "results").mkdir()
            (root / "artifacts" / "result.md").write_text("evidence")
            assigned = "artifacts/assignments/B1.md"
            self.assertEqual(parse_block_result(block("DONE", result_ref="artifacts/result.md"), assigned_block_ref=assigned, run_root=root)["status"], "DONE")
            for status in ("BLOCKED", "CONFLICT"):
                (root / "artifacts" / "results" / "B1.md").write_text("report")
                self.assertEqual(parse_block_result(block(status), assigned_block_ref=assigned, run_root=root)["status"], status)
            cases = (
                block("DONE", ref="other"),
                "TP_RESULT\nrole: BLOCK\nstatus: DONE",
                block("NOPE"),
                block("DONE", result_ref="artifacts/missing.md"),
                block("DONE", result_ref="mission.md"),
                block("DONE", result_ref="NONE"),
                block("DONE") + "\nnext: BRAIN",
            )
            for value in cases:
                with self.subTest(value=value), self.assertRaises(TPResultError):
                    parse_block_result(value, assigned_block_ref=assigned, run_root=root)


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
        (runtime.run_root / "artifacts" / "assignments").mkdir()
        (runtime.run_root / "artifacts" / "results").mkdir()
        for name in ("B1", "B2"):
            (runtime.run_root / "artifacts" / "assignments" / f"{name}.md").write_text("bounded assignment")
            (runtime.run_root / "artifacts" / "results" / f"{name}.md").write_text("bounded result")
        (runtime.run_root / "artifacts" / "brain-terminal.md").write_text("terminal report")
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
        b1, b2 = "artifacts/assignments/B1.md", "artifacts/assignments/B2.md"
        runtime, adapter, _ = self.make_runtime([
            returned(brain("CONTINUE", route="MEDIUM", next_step="SEQUENCE", blocks=f"{b1}, {b2}")),
            returned(block("DONE", b1)), returned(block("DONE", b2)), returned(brain("COMPLETE")),
        ])
        self.assertEqual(runtime.run(), "COMPLETE")
        self.assertEqual([call[0] for call in adapter.calls], ["BRAIN", "BLOCK", "BLOCK", "BRAIN"])
        self.assertEqual([call[2]["condition"] for call in adapter.calls], ["NORMAL", "BLOCK_ASSIGNED", "BLOCK_ASSIGNED", "SEQUENCE_EXHAUSTED"])
        self.assertEqual([call[2].get("block_ref") for call in adapter.calls], [None, b1, b2, None])

    def test_strong_brain_escalation_is_fresh_and_does_not_route_a_block(self):
        assignment, handoff = "artifacts/assignments/B1.md", "artifacts/results/escalation.md"
        runtime, adapter, _ = self.make_runtime([
            returned(brain("CONTINUE", route="STRONG", next_step="BRAIN", result_ref=handoff)),
            returned(brain("CONTINUE", route="LOW", next_step="SEQUENCE", blocks=assignment)),
            returned(block("DONE", assignment)), returned(brain("COMPLETE")),
        ])
        (runtime.run_root / handoff).write_text("durable handoff")
        self.assertEqual(runtime.run(), "COMPLETE")
        self.assertEqual([(call[0], call[1]) for call in adapter.calls], [("BRAIN", "MEDIUM"), ("BRAIN", "STRONG"), ("BLOCK", "LOW"), ("BRAIN", "MEDIUM")])
        self.assertEqual(adapter.calls[1][2]["condition"], "BRAIN_ESCALATION")
        self.assertEqual(adapter.calls[1][2]["result_ref"], handoff)
        self.assertEqual(set(adapter.calls[1][2]), {"run_ref", "mission_ref", "condition", "result_ref"})
        self.assertNotIn("block_ref", adapter.calls[1][2])
        self.assertIn({"event": "BRAIN_ESCALATION", "result_ref": handoff}, self.events(runtime))

    def test_every_non_done_or_malformed_block_returns_to_brain(self):
        b1 = "artifacts/assignments/B1.md"
        cases = (returned(block("BLOCKED")), returned(block("CONFLICT")), returned("not an envelope"), DispatchOutcome(True, True, None, "interrupted"))
        for outcome in cases:
            with self.subTest(outcome=outcome):
                runtime, adapter, _ = self.make_runtime([
                    returned(brain("CONTINUE", route="LOW", next_step="SEQUENCE", blocks=b1)), outcome, returned(brain("CONFLICT")),
                ])
                self.assertEqual(runtime.run(), "CONFLICT")
                self.assertEqual(adapter.calls[-1][0], "BRAIN")
                self.assertEqual(len([event for event in self.events(runtime) if event["event"] == "BLOCK_CONTROL_TO_BRAIN"]), 1)

    def test_artifact_is_preserved_but_malformed_control_is_not_interpreted(self):
        runtime, adapter, _ = self.make_runtime([])
        evidence = runtime.run_root / "artifacts" / "substantive.md"
        evidence.write_text("do not infer control from this")
        adapter.outcomes = iter([
            returned(brain("CONTINUE", route="LOW", next_step="SEQUENCE", blocks="artifacts/assignments/B1.md")), returned("not an envelope"), returned(brain("BLOCKED")),
        ])
        self.assertEqual(runtime.run(), "BLOCKED")
        self.assertTrue(evidence.exists())
        self.assertIn("BLOCK_RESULT_INVALID", [event["event"] for event in self.events(runtime)])

    def test_admission_states_are_recorded_without_block_replay(self):
        b1 = "artifacts/assignments/B1.md"
        cases = (
            DispatchOutcome(False, False, None, "rejected"),
            DispatchOutcome(True, False, None, "context too long"),
            DispatchOutcome(True, True, None, "failed after start"),
        )
        for failed in cases:
            with self.subTest(failed=failed):
                runtime, adapter, _ = self.make_runtime([
                    returned(brain("CONTINUE", route="LOW", next_step="SEQUENCE", blocks=b1)), failed, returned(brain("BLOCKED")),
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

    def test_ambiguous_brain_escalation_fails_closed(self):
        handoff = "artifacts/results/escalation.md"
        runtime, adapter, _ = self.make_runtime([
            returned(brain("CONTINUE", route="LOW", next_step="BRAIN", result_ref=handoff)),
        ])
        (runtime.run_root / handoff).write_text("durable handoff")
        self.assertEqual(runtime.run(), "BRAIN_REQUIRED")
        self.assertEqual([call[0] for call in adapter.calls], ["BRAIN"])
        self.assertIn("BRAIN_RESULT_INVALID", [event["event"] for event in self.events(runtime)])

    def test_missing_or_out_of_run_assignment_fails_before_block_dispatch(self):
        for reference in ("artifacts/assignments/missing.md", "mission.md"):
            with self.subTest(reference=reference):
                runtime, adapter, _ = self.make_runtime([
                    returned(brain("CONTINUE", route="LOW", next_step="SEQUENCE", blocks=reference)),
                ])
                self.assertEqual(runtime.run(), "BRAIN_REQUIRED")
                self.assertEqual([call[0] for call in adapter.calls], ["BRAIN"])

    def test_valid_block_result_ref_is_durable_for_fresh_brain(self):
        assignment, result = "artifacts/assignments/B1.md", "artifacts/results/B1.md"
        runtime, _, _ = self.make_runtime([
            returned(brain("CONTINUE", route="LOW", next_step="SEQUENCE", blocks=assignment)),
            returned(block("DONE", assignment, result)), returned(brain("COMPLETE")),
        ])
        self.assertEqual(runtime.run(), "COMPLETE")
        block_return = next(event for event in self.events(runtime) if event["event"] == "BLOCK_RETURN_VALID")
        self.assertEqual(block_return, {"event": "BLOCK_RETURN_VALID", "block_ref": assignment, "status": "DONE", "result_ref": result})

    def test_result_refs_and_malformed_control_fail_closed_without_reason_interpretation(self):
        assignment = "artifacts/assignments/B1.md"
        for result_ref in ("artifacts/results/missing.md", "mission.md"):
            with self.subTest(result_ref=result_ref):
                runtime, adapter, _ = self.make_runtime([
                    returned(brain("CONTINUE", route="LOW", next_step="SEQUENCE", blocks=assignment)),
                    returned(block("DONE", assignment, result_ref, reason="semantic evidence must not matter")),
                    returned(brain("BLOCKED")),
                ])
                self.assertEqual(runtime.run(), "BLOCKED")
                self.assertEqual([call[0] for call in adapter.calls], ["BRAIN", "BLOCK", "BRAIN"])
                self.assertNotIn("semantic evidence must not matter", (runtime.run_root / "events.jsonl").read_text())

    def test_oversized_reason_is_malformed_even_with_a_valid_artifact(self):
        runtime, _, _ = self.make_runtime([returned(brain("COMPLETE", reason="x" * 241))])
        self.assertEqual(runtime.run(), "BRAIN_REQUIRED")
        self.assertIn("BRAIN_RESULT_INVALID", [event["event"] for event in self.events(runtime)])

    def test_terminal_brain_result_ref_is_validated_and_recorded(self):
        runtime, _, _ = self.make_runtime([returned(brain("COMPLETE"))])
        self.assertEqual(runtime.run(), "COMPLETE")
        self.assertIn({"event": "BRAIN_RETURN_VALID", "status": "COMPLETE", "result_ref": "artifacts/brain-terminal.md"}, self.events(runtime))
        invalid, _, _ = self.make_runtime([returned(brain("COMPLETE", result_ref="artifacts/missing.md"))])
        self.assertEqual(invalid.run(), "BRAIN_REQUIRED")


if __name__ == "__main__":
    unittest.main()

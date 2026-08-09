"""Recovered TP completion/escalation tests plus native-routing tests.

Git preserved the pre-existing staged version after the routing run overwrote
this worktree file. Its five completion/packet tests are restored below. The
six fixed-Sonnet escalation assertions were superseded by the authorized native
route design; their test identities and load-bearing concerns are retained as
native-route assertions alongside the six interrupted-candidate routing tests.

These tests prove the written contract, not runtime model behavior.
"""
from __future__ import annotations

from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


def raw(path: str = "workflows/task_prompt.md") -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def flat(path: str = "workflows/task_prompt.md") -> str:
    return " ".join(raw(path).split())


def flat_text(text: str) -> str:
    return " ".join(text.split())


def packet(text: str, token: str) -> str:
    start = text.index(token + "\n")
    return text[start : text.index("```", start)]


# The recovered fixed-Sonnet assertions are updated only where the authorized
# LOW/MEDIUM/STRONG transport supersedes their old premise. Their test class,
# six obligations, and controller/Brain ownership checks remain intact.


def assert_controller_cannot_infer_or_author_escalation(
    text: str, case: unittest.TestCase
) -> None:
    case.assertIn("controller applies the returned route token mechanically", text)
    case.assertIn("never opens substantive references to choose it", text)
    case.assertIn(
        "it does not author, open, interpret, or discharge the checkpoint", text
    )
    case.assertNotIn("the controller emits the `MODEL_ESCALATION_CHECKPOINT`", text)


def assert_block_route_has_single_source(
    text: str, case: unittest.TestCase
) -> None:
    case.assertIn(
        "It must not name a requested model, model class, route token, or "
        "reasoning effort",
        text,
    )
    case.assertIn(
        "Brain's `TP_RESULT.route` is the single route and model selection for "
        "that block",
        text,
    )
    case.assertIn("Route and model selection do not live there", text)
    case.assertIn("Brain returns the route once in `TP_RESULT.route`", text)


def assert_brain_may_continue_with_another_valid_block(
    text: str, case: unittest.TestCase
) -> None:
    case.assertIn(
        "Brain selects `LOW`, `MEDIUM`, or `STRONG` semantically for each "
        "bounded work block",
        text,
    )
    case.assertIn(
        "After every work block, whatever its status, the controller dispatches "
        "a fresh Brain",
        text,
    )
    case.assertIn(
        "If a work-block invocation cannot be created for the same reason, the "
        "controller records `ROUTE_UNAVAILABLE`",
        text,
    )
    case.assertIn(
        "then launches a fresh Brain at the current Brain route", text
    )
    case.assertIn("never uses the work-block route", text)


def assert_terminal_blocked_only_when_mission_cannot_proceed(
    text: str, case: unittest.TestCase
) -> None:
    case.assertIn(
        "Brain returns terminal `BLOCKED` only when it determines that the "
        "mission cannot proceed through any valid authorized and available "
        "route or reference",
        text,
    )
    case.assertIn(
        "One unavailable candidate route or failed block is not enough when "
        "Brain can select a valid continuation",
        text,
    )
    case.assertIn(
        "If a Brain invocation cannot be created because native transport or "
        "its requested mapped model is unavailable",
        text,
    )
    case.assertIn(
        "reports the terminal blocker: no Brain semantic authority is available "
        "to choose a continuation",
        text,
    )


def assert_checkpoint_content_is_brain_authored_and_referenced(
    text: str, case: unittest.TestCase
) -> None:
    case.assertIn(
        "Brain writes the required `MODEL_ESCALATION_CHECKPOINT` into a durable "
        "blocker artifact",
        text,
    )
    case.assertIn(
        "returns `BLOCKED` with that artifact as `result_ref` and `route=NONE`",
        text,
    )
    case.assertIn(
        "The controller reports the reference and stops; it does not author, "
        "open, interpret, or discharge the checkpoint",
        text,
    )
    case.assertIn("silence is not authorization", text)
    case.assertIn("No premium dispatch occurs before the required authorization", text)


def assert_variable_model_execution_is_explicit(
    text: str, case: unittest.TestCase
) -> None:
    for line in (
        "LOW = gpt-5.6-luna",
        "MEDIUM = gpt-5.6-terra",
        "STRONG = gpt-5.6-sol",
    ):
        case.assertIn(line, text)
    case.assertIn("`route` is the sole mechanically returned routing field", text)
    case.assertIn("Route is invocation metadata only", text)
    case.assertIn(
        "TP fixes the requested effort at `medium` for every Brain and "
        "work-block invocation",
        text,
    )


class TpEscalationSemanticsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.task = flat()

    def test_controller_cannot_infer_author_or_execute_escalation(self) -> None:
        assert_controller_cannot_infer_or_author_escalation(self.task, self)

    def test_block_route_has_single_source(self) -> None:
        assert_block_route_has_single_source(self.task, self)

    def test_brain_may_choose_another_valid_block(self) -> None:
        assert_brain_may_continue_with_another_valid_block(self.task, self)

    def test_brain_returns_terminal_blocked_only_when_mission_cannot_proceed(
        self,
    ) -> None:
        assert_terminal_blocked_only_when_mission_cannot_proceed(self.task, self)

    def test_premium_checkpoint_is_brain_authored_and_only_referenced(self) -> None:
        assert_checkpoint_content_is_brain_authored_and_referenced(self.task, self)

    def test_variable_model_tp_execution_is_explicit(self) -> None:
        assert_variable_model_execution_is_explicit(self.task, self)


def assert_mission_complete_is_strictly_terminal(
    text: str, case: unittest.TestCase
) -> None:
    case.assertIn("`MISSION_COMPLETE` is strictly terminal", text)
    case.assertIn(
        "Mechanical completion is the controller's: recording final statuses "
        "and references, and reporting. That is the whole of it",
        text,
    )
    case.assertIn(
        "The controller performs only deterministic terminal recording and user "
        "reporting",
        text,
    )


def assert_nothing_runs_after_mission_complete(
    text: str, case: unittest.TestCase
) -> None:
    case.assertIn(
        "Once Brain has returned `MISSION_COMPLETE`, no further block may be "
        "dispatched, and no test, review, acceptance gate, check, or "
        "publication may run",
        text,
    )
    case.assertNotIn(
        "dispatching any deterministic checks Brain's control state specified "
        "as bounded children and recording their results",
        text,
    )


def assert_required_work_precedes_completion(
    text: str, case: unittest.TestCase
) -> None:
    case.assertIn(
        "Whatever the mission actually requires — tests, review, qualification, "
        "Git safety checks, publication, remote verification, or anything "
        "else — occurs as Brain-selected work blocks before Brain returns it",
        text,
    )
    case.assertIn(
        "The lifecycle is therefore: Brain → required block → Brain → ... → "
        "final required block → Brain → `MISSION_COMPLETE` → record and report "
        "only",
        text,
    )
    case.assertIn(
        "A check the controller wanted to run after `MISSION_COMPLETE` is a "
        "check Brain should have sequenced as a block before it",
        text,
    )
    case.assertIn(
        "Brain sequences them as blocks, and — like every other block — before "
        "it declares the mission complete",
        text,
    )


DETERMINISTIC_CHECKS = (
    "Deterministic checks are work blocks like any other; the controller does "
    "not run them in its own context"
)


def assert_deterministic_checks_stated_with_blocks(
    text_raw: str, case: unittest.TestCase
) -> None:
    text = flat_text(text_raw)
    checks_at = text.find(DETERMINISTIC_CHECKS)
    case.assertNotEqual(checks_at, -1, "deterministic-checks rule must survive")
    blocks_at = text.index("## Work blocks")
    completion_at = text.index("## Completion")
    case.assertTrue(
        blocks_at < checks_at < completion_at,
        "the deterministic-checks rule must sit under '## Work blocks', not "
        "inside '## Completion'",
    )


BRAIN_PACKET = """TP_BRAIN
workflow_ref: <receiver-resolvable reference to workflows/task_prompt.md>
intent_ref: <receiver-resolvable reference to the persisted verbatim TP intent>
run_ref: <receiver-resolvable reference to run storage>
dispatch_id: <mechanically generated identifier unique within this task>
"""

BLOCK_PACKET = """TP_BLOCK
workflow_ref: <receiver-resolvable reference to workflows/task_prompt.md>
block_ref: <receiver-resolvable reference to the durable work-block artifact>
run_ref: <receiver-resolvable reference to run storage>
dispatch_id: <mechanically generated identifier unique within this task>
"""

RESULT_PACKET = """TP_RESULT
dispatch_id: <the identifier the controller issued>
status: DONE | BLOCKED | CONFLICT
result_ref: <receiver-resolvable reference to the durable artifact, or NONE>
next: <block_ref> | BRAIN_REDISPATCH | MISSION_COMPLETE | NONE
route: LOW | MEDIUM | STRONG | NONE
"""

CONTINUATION_RECORD = """CONTINUATION_RECORD
run_id
run_ref
intent_ref
intent_sha256
dispatches[]: dispatch_id, role, requested_route, mapped_model, effort, packet, state, result
role: "TP_BRAIN" | "TP_BLOCK"
packet: exact issued packet field names and values for role
state: ADMITTED | RETURNED | ROUTE_UNAVAILABLE
result: NONE | exact returned TP_RESULT field names and values
entry identity: packet.dispatch_id = dispatch_id
returned identity: result.TP_RESULT.dispatch_id = dispatch_id
"""

CONTINUATION_TRANSITIONS = """CONTINUATION_TRANSITIONS
ADMITTED (result=NONE) -> RETURNED (structurally valid result and returned identity match)
ADMITTED (result=NONE) -> ROUTE_UNAVAILABLE (result=NONE)
RETURNED -> no transition
ROUTE_UNAVAILABLE -> no transition
"""


def assert_wire_formats_unchanged(text_raw: str, case: unittest.TestCase) -> None:
    """Brain/block packets stay exact; TP_RESULT has its authorized addition."""
    case.assertEqual(packet(text_raw, "TP_BRAIN"), BRAIN_PACKET)
    case.assertEqual(packet(text_raw, "TP_BLOCK"), BLOCK_PACKET)
    case.assertEqual(packet(text_raw, "TP_RESULT"), RESULT_PACKET)
    case.assertNotIn("route:", BRAIN_PACKET)
    case.assertNotIn("route:", BLOCK_PACKET)
    case.assertEqual(RESULT_PACKET.count("route:"), 1)
    for token in ("TP_BRAIN\n", "TP_BLOCK\n", "TP_RESULT\n"):
        case.assertEqual(text_raw.count(token), 1, f"{token!r} must be defined once")


class TpMissionCompleteTerminalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.task = flat()
        cls.task_raw = raw()

    def test_mission_complete_is_strictly_terminal(self) -> None:
        assert_mission_complete_is_strictly_terminal(self.task, self)

    def test_nothing_may_follow_mission_complete(self) -> None:
        assert_nothing_runs_after_mission_complete(self.task, self)

    def test_all_required_work_precedes_completion(self) -> None:
        assert_required_work_precedes_completion(self.task, self)

    def test_deterministic_checks_are_stated_with_blocks_not_completion(self) -> None:
        assert_deterministic_checks_stated_with_blocks(self.task_raw, self)

    def test_wire_formats_are_unchanged_by_both_repairs(self) -> None:
        assert_wire_formats_unchanged(self.task_raw, self)


class TpInterruptedRunResumeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.task = flat()

    def test_controller_admits_only_identity_bound_mechanical_state(self) -> None:
        for phrase in (
            "durable controller-authored continuation record",
            "newly generated run identity",
            "SHA-256 digest of the exact persisted intent bytes",
            "preserves verbatim the issued `dispatch_id`, role,",
            "every packet field/reference value",
            "preserves verbatim every `TP_RESULT` field and reference value",
            "no semantic artifact body, summary, interpretation, or reconstructed value",
        ):
            self.assertIn(phrase, self.task)

    def test_continuation_record_has_one_canonical_mechanical_schema(self) -> None:
        self.assertEqual(
            packet(raw(), "CONTINUATION_RECORD"), CONTINUATION_RECORD
        )

    def test_continuation_record_permits_only_exhaustive_state_transitions(self) -> None:
        self.assertEqual(
            packet(raw(), "CONTINUATION_TRANSITIONS"), CONTINUATION_TRANSITIONS
        )

    def test_returned_brain_selection_resumes_its_recorded_block_once(self) -> None:
        self.assertIn(
            "When the latest entry is a fully recorded returned Brain result with "
            "`status=DONE`, `next=<block_ref>`, and `route=LOW|MEDIUM|STRONG`, and "
            "no dispatch for that selected block was admitted, the controller "
            "dispatches exactly that recorded block exactly once using its recorded "
            "block reference and route",
            self.task,
        )

    def test_completed_block_resume_issues_only_a_fresh_brain(self) -> None:
        self.assertIn(
            "After a fully recorded returned work block, or a fully recorded "
            "work-block `ROUTE_UNAVAILABLE`, the controller issues exactly one fresh "
            "Brain dispatch at the recorded current Brain route",
            self.task,
        )
        self.assertIn("It never replays an admitted block", self.task)
        self.assertIn("never opens a block artifact to choose continuation", self.task)

    def test_unbound_or_incomplete_resumed_state_stops_before_dispatch(self) -> None:
        self.assertIn(
            "A missing, malformed, identity-mismatched, substituted, or unresolved "
            "`ADMITTED` entry stops the run with a mechanical `BLOCKED` or `CONFLICT` "
            "outcome",
            self.task,
        )
        self.assertIn("before any semantic dispatch or replay", self.task)
        self.assertIn("neither reconstructs the record nor retries the admitted child", self.task)


class TpRoutingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = raw()

    def test_native_host_neutral_routing(self) -> None:
        t = self.text
        self.assertIn(
            "launch fresh native subagent(role, route, effort, reference packet)", t
        )
        self.assertIn("LOW    = gpt-5.6-luna", t)
        self.assertIn("MEDIUM = gpt-5.6-terra", t)
        self.assertIn("STRONG = gpt-5.6-sol", t)
        self.assertNotIn("LOW    = gpt-5.6-terra", t)
        self.assertNotIn("model: sonnet", t)
        self.assertNotIn("Claude Code execution path", t)
        self.assertNotIn("codex exec", t)

    def test_brain_rules(self) -> None:
        t = flat_text(self.text)
        self.assertIn("initial Brain route is always `MEDIUM`", t)
        self.assertIn("Brain never starts at `LOW`", t)
        self.assertIn("Brain `LOW` is invalid", t)
        self.assertIn("same workflow, intent, and run references", t)
        self.assertIn("only a new `dispatch_id`", t)
        self.assertIn("no downgrade is permitted", t)

    def test_reference_only_packets(self) -> None:
        brain = packet(self.text, "TP_BRAIN")
        block = packet(self.text, "TP_BLOCK")
        self.assertEqual(brain, BRAIN_PACKET)
        self.assertEqual(block, BLOCK_PACKET)
        self.assertNotIn("route:", brain)
        self.assertNotIn("route:", block)

    def test_result_adds_only_route(self) -> None:
        result = packet(self.text, "TP_RESULT")
        self.assertEqual(result, RESULT_PACKET)
        self.assertEqual(result.count("route:"), 1)

    def test_result_combinations_are_declared(self) -> None:
        t = flat_text(self.text)
        for phrase in (
            "`DONE` with `next=<block_ref>` and `route=LOW|MEDIUM|STRONG`",
            "`DONE` with `next=BRAIN_REDISPATCH` and `route=STRONG`",
            "`DONE` with `next=MISSION_COMPLETE` and `route=NONE`",
            "blocked, conflict, and work-block returns use `next=NONE` and `route=NONE`",
        ):
            self.assertIn(phrase, t)
        self.assertIn("next=BRAIN_REDISPATCH", t)
        self.assertIn("route=STRONG", t)
        self.assertIn("route=NONE", t)
        self.assertIn("retains the current Brain route", t)

    def test_controller_is_mechanical(self) -> None:
        t = flat_text(self.text)
        self.assertIn("applies the returned route token mechanically", t)
        self.assertIn("never opens substantive references to choose it", t)
        self.assertIn(
            "`TP_RESULT.route` is the single route and model selection for "
            "that block",
            t,
        )
        self.assertIn("Route and model selection do not live there", t)
        self.assertIn(
            "requested route token, its mechanically mapped model, and the "
            "workflow-fixed `medium` effort",
            t,
        )
        self.assertIn("never performs semantic fallback", t)
        self.assertIn("No CLI or Claude/Sonnet-specific transport is required", t)
        self.assertIn("no authorized Brain role or reference", t)
        self.assertIn("`ROUTE_UNAVAILABLE`", t)
        self.assertIn(
            "If a work-block invocation cannot be created for the same reason",
            t,
        )
        self.assertIn("launches a fresh Brain at the current Brain route", t)
        self.assertIn(
            "reports the terminal blocker: no Brain semantic authority is "
            "available to choose a continuation",
            t,
        )
        self.assertIn("unavailable `gpt-5.6-luna`", t)
        self.assertIn("not silently replaced by `gpt-5.6-terra`", t)
        self.assertIn("`ACTUAL_ROUTING_UNKNOWN`", t)

if __name__ == "__main__":
    unittest.main()

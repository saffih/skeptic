# made by AI
"""Slice A.1: dispatch-first execution entry for the practically stateless Lead.

Slice A froze the general rule (one lifecycle transition per invocation). This
slice makes it operational *at execution entry*, so the first Lead invocation
cannot repeat the aborted Slice B failure: broad repository reads, running the
full test suite, consulting an advisor, and mapping implementation work until
`prompt too long` -- all before any dispatch.

Two kinds of coverage, matching repository convention:

- A self-contained frozen decision table encodes the entry rule so the contract
  cannot silently regress toward "the Lead may warm up before dispatching."
- Marker tests freeze the governing prose in `agents/lead-agent-prompt.md`.

The decision table does not prove agent behavior; it freezes the reference
decision the prompt must match. Marker tests assert against
`agents/lead-agent-prompt.md` only; `skeptic.md` is out of scope and protected.
"""
from __future__ import annotations

import hashlib
import json
import re
import unittest
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LEAD_PROMPT = ROOT / "agents" / "lead-agent-prompt.md"


def subsection(document: str, heading: str) -> str:
    """Return the body of a `### heading` up to the next `##`/`###` or EOF."""
    match = re.search(
        rf"^{re.escape(heading)}\n(?P<body>.*?)(?=^#{{2,3}}\s|\Z)",
        document,
        flags=re.MULTILINE | re.DOTALL,
    )
    if match is None:
        raise AssertionError(f"missing subsection: {heading}")
    return match.group("body")


# --------------------------------------------------------------------------
# Executable reference decision table
# --------------------------------------------------------------------------


class PreDispatchAction(str, Enum):
    # Permitted: the minimal reads that validate routing before one dispatch.
    VALIDATE_COMPACT_STATE = "VALIDATE_COMPACT_STATE"
    IDENTIFY_NEXT_STAGE = "IDENTIFY_NEXT_STAGE"
    VALIDATE_ROUTING_AUTHORITY = "VALIDATE_ROUTING_AUTHORITY"
    READ_NEXT_TICKET = "READ_NEXT_TICKET"
    # Forbidden before dispatch: substantive stage work / context accumulation.
    BROAD_REPO_INSPECTION = "BROAD_REPO_INSPECTION"
    RUN_BASELINE_SUITE = "RUN_BASELINE_SUITE"
    RUN_FULL_SUITE = "RUN_FULL_SUITE"
    MAP_TEST_BLAST_RADIUS = "MAP_TEST_BLAST_RADIUS"
    IMPLEMENT = "IMPLEMENT"
    SEMANTIC_REVIEW = "SEMANTIC_REVIEW"
    CONSULT_ADVISOR = "CONSULT_ADVISOR"
    RUN_SKEPTIC = "RUN_SKEPTIC"
    REPAIR = "REPAIR"
    INTEGRATE = "INTEGRATE"
    ACCUMULATE_FULL_CONTEXT = "ACCUMULATE_FULL_CONTEXT"


PERMITTED_PRE_DISPATCH = frozenset(
    {
        PreDispatchAction.VALIDATE_COMPACT_STATE,
        PreDispatchAction.IDENTIFY_NEXT_STAGE,
        PreDispatchAction.VALIDATE_ROUTING_AUTHORITY,
        PreDispatchAction.READ_NEXT_TICKET,
    }
)


def permitted_before_dispatch(action: PreDispatchAction) -> bool:
    """Only minimal routing/authority/state/ticket validation is permitted
    before the single authorized dispatch."""
    return action in PERMITTED_PRE_DISPATCH


@dataclass(frozen=True)
class EntryInvocation:
    """One dispatch-first entry invocation. No field has a default: an
    incomplete case must fail to construct rather than resolve to 'well-formed'.
    """

    pre_dispatch_actions: tuple
    stage_agents_dispatched: int
    inline_substantive_stages: int
    receipts_validated: int
    state_updated: bool
    stopped_after_update: bool
    post_receipt_inspection_without_cause: bool


def entry_wellformed(e: EntryInvocation) -> bool:
    """A dispatch-first entry: no substantive pre-dispatch work; at most one
    substantive transition (one dispatch OR one inline stage); at most one
    receipt validated; no post-receipt inspection of a completed stage without
    cause; and it stops after updating state."""
    if any(not permitted_before_dispatch(a) for a in e.pre_dispatch_actions):
        return False
    if e.stage_agents_dispatched + e.inline_substantive_stages > 1:
        return False
    if e.receipts_validated > 1:
        return False
    if e.post_receipt_inspection_without_cause:
        return False
    if not e.stopped_after_update:
        return False
    return True


def may_inspect_completed_stage(
    named_blocker: bool, receipt_mismatch: bool, deterministic_invalidation: bool
) -> bool:
    """A completed stage may be inspected after its receipt is accepted only for
    one named unresolved blocker, a receipt mismatch, or deterministic
    invalidation -- never for reassurance."""
    return named_blocker or receipt_mismatch or deterministic_invalidation


@dataclass(frozen=True)
class Continuation:
    fresh_invocation: bool
    only_compact_state: bool
    carried_completed_history: bool


def continuation_valid(c: Continuation) -> bool:
    """The next stage requires a fresh Lead invocation carrying only the compact
    updated state -- never the completed-stage history of the prior one."""
    return (
        c.fresh_invocation
        and c.only_compact_state
        and not c.carried_completed_history
    )


@dataclass(frozen=True)
class EntryProportionality:
    small: bool
    reversible: bool
    single_stage: bool
    delegation_costs_more: bool
    review: bool
    repair: bool
    integration: bool
    repeated_work: bool
    context_exhaustion_risk: bool


def entry_may_execute_directly(c: EntryProportionality) -> bool:
    """The proportionality exception is not a dispatch-first bypass: a genuinely
    small, reversible, single-stage entry may execute directly, and it never
    covers review, repair, integration, repeated work, or a task with meaningful
    context-exhaustion risk."""
    if not (
        c.small and c.reversible and c.single_stage and c.delegation_costs_more
    ):
        return False
    excluded = (
        c.review
        or c.repair
        or c.integration
        or c.repeated_work
        or c.context_exhaustion_risk
    )
    return not excluded


# Frozen regression fixture: the EXACT aborted Slice B behavior this slice
# forbids -- the first Lead invocation broadly reads the repo, runs the full
# suite, consults an advisor, and keeps mapping implementation work, dispatching
# nothing, until the context overflows with `prompt too long`. This is distinct
# from Slice A's stage-chaining fixture, which is about owning multiple stages
# *after* dispatching. Any change to this scenario must change the hash.
SLICE_B_PREDISPATCH_FIXTURE = {
    "scenario": "lead_accumulates_pre_dispatch_context_until_prompt_too_long",
    "pre_dispatch_actions": [
        "BROAD_REPO_INSPECTION",
        "RUN_FULL_SUITE",
        "CONSULT_ADVISOR",
        "MAP_TEST_BLAST_RADIUS",
        "IMPLEMENT",
    ],
    "stage_agents_dispatched": 0,
    "inline_substantive_stages": 0,
    "receipts_validated": 0,
    "state_updated": False,
    "stopped_after_update": False,
    "post_receipt_inspection_without_cause": False,
    "terminated_by": "prompt_too_long",
    "expected_entry_wellformed": False,
    "expected_all_pre_dispatch_forbidden": True,
}
SLICE_B_PREDISPATCH_FIXTURE_SHA256 = (
    "4e7fb70778e352d0b159ff5b5d0f743240ba09753744d488e075296d1e33b9ae"
)


class SliceBRegressionFixtureTests(unittest.TestCase):
    def test_fixture_is_frozen(self) -> None:
        canonical = json.dumps(
            SLICE_B_PREDISPATCH_FIXTURE, sort_keys=True
        ).encode("utf-8")
        digest = hashlib.sha256(canonical).hexdigest()
        self.assertEqual(digest, SLICE_B_PREDISPATCH_FIXTURE_SHA256)

    def test_every_pre_dispatch_action_in_fixture_is_forbidden(self) -> None:
        actions = [
            PreDispatchAction(name)
            for name in SLICE_B_PREDISPATCH_FIXTURE["pre_dispatch_actions"]
        ]
        for action in actions:
            with self.subTest(action=action):
                self.assertFalse(permitted_before_dispatch(action))
        self.assertEqual(
            SLICE_B_PREDISPATCH_FIXTURE["expected_all_pre_dispatch_forbidden"],
            all(not permitted_before_dispatch(a) for a in actions),
        )

    def test_slice_b_pattern_is_not_a_wellformed_entry(self) -> None:
        e = EntryInvocation(
            pre_dispatch_actions=tuple(
                PreDispatchAction(n)
                for n in SLICE_B_PREDISPATCH_FIXTURE["pre_dispatch_actions"]
            ),
            stage_agents_dispatched=SLICE_B_PREDISPATCH_FIXTURE[
                "stage_agents_dispatched"
            ],
            inline_substantive_stages=SLICE_B_PREDISPATCH_FIXTURE[
                "inline_substantive_stages"
            ],
            receipts_validated=SLICE_B_PREDISPATCH_FIXTURE["receipts_validated"],
            state_updated=SLICE_B_PREDISPATCH_FIXTURE["state_updated"],
            stopped_after_update=SLICE_B_PREDISPATCH_FIXTURE[
                "stopped_after_update"
            ],
            post_receipt_inspection_without_cause=SLICE_B_PREDISPATCH_FIXTURE[
                "post_receipt_inspection_without_cause"
            ],
        )
        self.assertEqual(
            entry_wellformed(e),
            SLICE_B_PREDISPATCH_FIXTURE["expected_entry_wellformed"],
        )


class PreDispatchProhibitionTests(unittest.TestCase):
    def test_minimal_routing_reads_are_permitted(self) -> None:
        for action in PERMITTED_PRE_DISPATCH:
            with self.subTest(action=action):
                self.assertTrue(permitted_before_dispatch(action))

    def test_full_suite_before_dispatch_is_forbidden(self) -> None:
        self.assertFalse(permitted_before_dispatch(PreDispatchAction.RUN_FULL_SUITE))
        self.assertFalse(
            permitted_before_dispatch(PreDispatchAction.RUN_BASELINE_SUITE)
        )

    def test_advisor_before_dispatch_is_forbidden(self) -> None:
        self.assertFalse(
            permitted_before_dispatch(PreDispatchAction.CONSULT_ADVISOR)
        )

    def test_broad_implementation_read_before_dispatch_is_forbidden(self) -> None:
        self.assertFalse(
            permitted_before_dispatch(PreDispatchAction.BROAD_REPO_INSPECTION)
        )
        self.assertFalse(
            permitted_before_dispatch(PreDispatchAction.MAP_TEST_BLAST_RADIUS)
        )

    def test_running_suite_before_dispatch_breaks_entry(self) -> None:
        self.assertFalse(
            entry_wellformed(
                EntryInvocation(
                    pre_dispatch_actions=(PreDispatchAction.RUN_FULL_SUITE,),
                    stage_agents_dispatched=1,
                    inline_substantive_stages=0,
                    receipts_validated=1,
                    state_updated=True,
                    stopped_after_update=True,
                    post_receipt_inspection_without_cause=False,
                )
            )
        )

    def test_advisor_before_dispatch_breaks_entry(self) -> None:
        self.assertFalse(
            entry_wellformed(
                EntryInvocation(
                    pre_dispatch_actions=(PreDispatchAction.CONSULT_ADVISOR,),
                    stage_agents_dispatched=1,
                    inline_substantive_stages=0,
                    receipts_validated=1,
                    state_updated=True,
                    stopped_after_update=True,
                    post_receipt_inspection_without_cause=False,
                )
            )
        )


class OneTransitionEntryTests(unittest.TestCase):
    def _clean(self, **overrides) -> EntryInvocation:
        fields = dict(
            pre_dispatch_actions=(
                PreDispatchAction.VALIDATE_COMPACT_STATE,
                PreDispatchAction.IDENTIFY_NEXT_STAGE,
                PreDispatchAction.READ_NEXT_TICKET,
            ),
            stage_agents_dispatched=1,
            inline_substantive_stages=0,
            receipts_validated=1,
            state_updated=True,
            stopped_after_update=True,
            post_receipt_inspection_without_cause=False,
        )
        fields.update(overrides)
        return EntryInvocation(**fields)

    def test_clean_dispatch_first_entry_is_wellformed(self) -> None:
        self.assertTrue(entry_wellformed(self._clean()))

    def test_two_dispatched_stage_agents_break_entry(self) -> None:
        self.assertFalse(entry_wellformed(self._clean(stage_agents_dispatched=2)))

    def test_implementation_and_checking_in_one_entry_break_it(self) -> None:
        # Lead performs two substantive stages itself (implement + check).
        self.assertFalse(
            entry_wellformed(
                self._clean(
                    stage_agents_dispatched=0, inline_substantive_stages=2
                )
            )
        )
        # Or dispatches one and does one inline.
        self.assertFalse(
            entry_wellformed(
                self._clean(
                    stage_agents_dispatched=1, inline_substantive_stages=1
                )
            )
        )

    def test_must_stop_after_state_update(self) -> None:
        self.assertFalse(entry_wellformed(self._clean(stopped_after_update=False)))

    def test_incomplete_entry_raises(self) -> None:
        with self.assertRaises(TypeError):
            EntryInvocation(stage_agents_dispatched=1)  # type: ignore[call-arg]


class PostReceiptInspectionTests(unittest.TestCase):
    def test_inspecting_completed_stage_without_cause_breaks_entry(self) -> None:
        self.assertFalse(
            entry_wellformed(
                EntryInvocation(
                    pre_dispatch_actions=(
                        PreDispatchAction.VALIDATE_COMPACT_STATE,
                    ),
                    stage_agents_dispatched=1,
                    inline_substantive_stages=0,
                    receipts_validated=1,
                    state_updated=True,
                    stopped_after_update=True,
                    post_receipt_inspection_without_cause=True,
                )
            )
        )

    def test_no_inspection_without_named_cause(self) -> None:
        self.assertFalse(may_inspect_completed_stage(False, False, False))

    def test_inspection_allowed_only_for_named_cause(self) -> None:
        self.assertTrue(may_inspect_completed_stage(True, False, False))
        self.assertTrue(may_inspect_completed_stage(False, True, False))
        self.assertTrue(may_inspect_completed_stage(False, False, True))


class ContinuationTests(unittest.TestCase):
    def test_fresh_invocation_with_only_compact_state_is_valid(self) -> None:
        self.assertTrue(
            continuation_valid(Continuation(True, True, False))
        )

    def test_same_invocation_continuation_is_invalid(self) -> None:
        self.assertFalse(
            continuation_valid(Continuation(False, True, False))
        )

    def test_carrying_completed_history_is_invalid(self) -> None:
        self.assertFalse(
            continuation_valid(Continuation(True, True, True))
        )


class EntryProportionalityExceptionTests(unittest.TestCase):
    def _base(self, **overrides) -> EntryProportionality:
        fields = dict(
            small=True,
            reversible=True,
            single_stage=True,
            delegation_costs_more=True,
            review=False,
            repair=False,
            integration=False,
            repeated_work=False,
            context_exhaustion_risk=False,
        )
        fields.update(overrides)
        return EntryProportionality(**fields)

    def test_small_reversible_single_stage_entry_may_execute_directly(self) -> None:
        self.assertTrue(entry_may_execute_directly(self._base()))

    def test_exception_never_covers_excluded_categories(self) -> None:
        for exclusion in [
            "review",
            "repair",
            "integration",
            "repeated_work",
            "context_exhaustion_risk",
        ]:
            with self.subTest(exclusion=exclusion):
                self.assertFalse(
                    entry_may_execute_directly(self._base(**{exclusion: True}))
                )


# --------------------------------------------------------------------------
# Marker tests: the governing prose must be present in lead-agent-prompt.md
# --------------------------------------------------------------------------


class DispatchFirstEntryMarkerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.lead = LEAD_PROMPT.read_text(encoding="utf-8")
        cls.entry = subsection(cls.lead, "### Dispatch-first execution entry")

    def test_subsection_exists_and_is_singular(self) -> None:
        self.assertEqual(
            self.lead.count("### Dispatch-first execution entry"), 1
        )

    def test_entry_is_declared_first_invocation_and_dispatch_first(self) -> None:
        self.assertIn("the first Lead invocation is a dispatch-first entry", self.entry)
        self.assertIn("performs no substantive stage work before dispatch", self.entry)

    def test_seven_authorized_entry_steps_are_enumerated(self) -> None:
        for step in [
            "validate the compact authoritative state",
            "identify the next authorized stage",
            "create one bounded stage ticket",
            "dispatch one fresh stage agent",
            "validate one compact receipt",
            "update the compact authoritative state",
            "stop",
        ]:
            self.assertIn(step, self.entry)

    def test_minimal_pre_dispatch_reads_are_bounded(self) -> None:
        self.assertIn(
            "Only the minimal reads needed to validate routing, authority, "
            "compact state, and the next ticket are permitted before dispatch.",
            self.entry,
        )

    def test_pre_dispatch_prohibitions_are_enumerated(self) -> None:
        for prohibition in [
            "inspect the implementation surface broadly",
            "run the baseline or full test suite",
            "map the test blast radius",
            "implement",
            "perform semantic review",
            "consult an advisor",
            "perform RunSkeptic",
            "repair",
            "integrate",
            "execute multiple stages",
            'accumulate "full context."',
        ]:
            self.assertIn(prohibition, self.entry)

    def test_immediate_stop_and_no_second_transition(self) -> None:
        self.assertIn("the Lead must immediately stop", self.entry)
        for forbidden in [
            "launch another stage",
            "inspect the returned implementation",
            "run follow-up checks",
            "add a reassurance review",
            "continue toward terminal DONE",
        ]:
            self.assertIn(forbidden, self.entry)

    def test_post_receipt_inspection_exception_is_named(self) -> None:
        self.assertIn(
            "permitted only for one named unresolved blocker, a receipt "
            "mismatch, or deterministic invalidation",
            self.entry,
        )

    def test_continuation_requires_fresh_invocation_and_compact_state(self) -> None:
        self.assertIn(
            "The next stage requires a fresh Lead invocation carrying only the "
            "compact updated state",
            self.entry,
        )

    def test_prompt_too_long_named_as_failure_path(self) -> None:
        self.assertIn("prompt too long", self.entry)
        self.assertIn("is a failed execution path", self.entry)

    def test_references_rather_than_restates_slice_a_state_fields(self) -> None:
        # Uses the existing Slice A compact-state fields by reference; must not
        # redefine them.
        self.assertIn('"Compact authoritative state"', self.entry)
        self.assertIn('"One lifecycle transition per invocation"', self.entry)

    def test_minimal_mechanism_is_required(self) -> None:
        self.assertIn(
            "workflow engine, daemon, queue, database, recursive hierarchy, "
            "Phase Supervisor, or repository-owned state directory",
            self.entry,
        )
        self.assertIn(
            "Add a deterministic wrapper only if tests show", self.entry
        )


class CanonicalEntryTemplateMarkerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.lead = LEAD_PROMPT.read_text(encoding="utf-8")
        cls.entry = subsection(cls.lead, "### Dispatch-first execution entry")

    def test_canonical_template_is_present(self) -> None:
        for line in [
            "This invocation is the Lead orchestrator only.",
            "You may perform exactly one lifecycle transition.",
            "Do not implement, test, review, advise, repair, integrate",
            "prior state identity",
            "dispatched stage and role",
            "ticket identity",
            "receipt identity and outcome",
            "updated compact state",
            "next authorized stage",
            "explicit stop confirmation",
        ]:
            self.assertIn(line, self.entry)

    def test_behavioral_restrictions_must_remain_explicit(self) -> None:
        self.assertIn(
            "the behavioral restrictions above must remain explicit", self.entry
        )


if __name__ == "__main__":
    unittest.main()

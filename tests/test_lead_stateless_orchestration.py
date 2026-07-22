# made by AI
"""Slice A: the Lead Agent as a practically stateless orchestrator.

Two kinds of coverage, matching repository convention:

- Marker tests freeze the governing prose in `agents/lead-agent-prompt.md`.
- A self-contained frozen decision table encodes the operational rule so the
  contract cannot silently regress toward "the Lead may do everything itself."

The decision table does not prove agent behavior; it freezes the reference
decision the prompt must match. It asserts against `agents/lead-agent-prompt.md`
only -- `agents/task-prompt.md` is out of scope for this slice.
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


def section(document: str, heading: str) -> str:
    match = re.search(
        rf"^{re.escape(heading)}\n(?P<body>.*?)(?=^##\s|\Z)",
        document,
        flags=re.MULTILINE | re.DOTALL,
    )
    if match is None:
        raise AssertionError(f"missing section: {heading}")
    return match.group("body")


# --------------------------------------------------------------------------
# Executable reference decision table
# --------------------------------------------------------------------------


class StageAgent(str, Enum):
    IMPLEMENTER = "IMPLEMENTER"
    CHECKER = "CHECKER"
    SKEPTIC_REVIEWER = "SKEPTIC_REVIEWER"
    REPAIRER = "REPAIRER"
    INTEGRATOR = "INTEGRATOR"


SUBSTANTIVE_STAGES = frozenset(StageAgent)


class InputKind(str, Enum):
    COMPACT_STATE = "COMPACT_STATE"
    RECEIPT_REFERENCE = "RECEIPT_REFERENCE"
    RAW_EVIDENCE = "RAW_EVIDENCE"
    COMPLETED_HISTORY = "COMPLETED_HISTORY"


NORMAL_LEAD_INPUT = frozenset({InputKind.COMPACT_STATE, InputKind.RECEIPT_REFERENCE})


@dataclass(frozen=True)
class Invocation:
    """One Lead invocation. No field has a default: an incomplete case must
    fail to construct rather than silently resolve toward 'well-formed'."""

    substantive_stages_launched: int
    deterministic_terminal_actions: int


def invocation_wellformed(inv: Invocation) -> bool:
    """One Lead invocation performs at most one lifecycle transition: launch
    one fresh stage agent OR perform one deterministic terminal action."""
    return inv.substantive_stages_launched + inv.deterministic_terminal_actions <= 1


@dataclass(frozen=True)
class RawOpenRequest:
    """Whether the Lead may open referenced raw evidence / completed history."""

    named_unresolved_blocker: bool
    receipt_mismatch: bool
    deterministic_invalidation: bool


def may_open_raw_evidence(req: RawOpenRequest) -> bool:
    """Raw evidence and completed history are rejected as normal Lead input;
    they open only for one of the three named exceptions."""
    return (
        req.named_unresolved_blocker
        or req.receipt_mismatch
        or req.deterministic_invalidation
    )


def accepts_as_normal_input(kind: InputKind) -> bool:
    return kind in NORMAL_LEAD_INPUT


@dataclass(frozen=True)
class ReviewClaim:
    """A claimed Skeptic Reviewer result. Structurally cannot express 'the
    narration was persuasive' -- only whether the flow actually executed."""

    executed_full_runskeptic: bool
    considered_all_thinkers: bool
    included_receipt: bool
    named_identity_matches: bool
    blocking_finding: bool


def counts_as_pass(claim: ReviewClaim) -> bool:
    """A narrated or simulated review is not an executed PASS."""
    return (
        claim.executed_full_runskeptic
        and claim.considered_all_thinkers
        and claim.included_receipt
        and claim.named_identity_matches
        and not claim.blocking_finding
    )


def may_reopen_accepted_stage(deterministic_invalidation: bool) -> bool:
    """An accepted stage reopens only on deterministic invalidation."""
    return deterministic_invalidation


@dataclass(frozen=True)
class DirectExecCase:
    small: bool
    reversible: bool
    single_stage: bool
    delegation_costs_more: bool
    repeated_review: bool
    repair: bool
    integration: bool
    cross_session: bool
    context_exhaustion_risk: bool


def may_execute_directly(c: DirectExecCase) -> bool:
    """The narrow proportionality exception: a genuinely small, reversible,
    single-stage task may execute directly -- and never covers the excluded
    categories."""
    if not (c.small and c.reversible and c.single_stage and c.delegation_costs_more):
        return False
    excluded = (
        c.repeated_review
        or c.repair
        or c.integration
        or c.cross_session
        or c.context_exhaustion_risk
    )
    return not excluded


# Frozen regression fixture: the observed anti-pattern this slice forbids --
# one Lead invocation implements, then checks, then reviews, then integrates,
# carrying full history in active context. Any change must change the hash.
REGRESSION_FIXTURE = {
    "scenario": "lead_chains_multiple_substantive_stages_in_one_invocation",
    "invocation": {
        "substantive_stages_launched": 4,
        "deterministic_terminal_actions": 1,
    },
    "expected_wellformed": False,
    "narrated_review": {
        "executed_full_runskeptic": False,
        "considered_all_thinkers": True,
        "included_receipt": True,
        "named_identity_matches": True,
        "blocking_finding": False,
    },
    "expected_counts_as_pass": False,
}
REGRESSION_FIXTURE_SHA256 = (
    "0f7e3fa1889472de37df2b64c96da86c77c7e17813e711aab7755f984c91fe24"
)


class RegressionFixtureTests(unittest.TestCase):
    def test_fixture_is_frozen(self) -> None:
        canonical = json.dumps(REGRESSION_FIXTURE, sort_keys=True).encode("utf-8")
        digest = hashlib.sha256(canonical).hexdigest()
        self.assertEqual(digest, REGRESSION_FIXTURE_SHA256)

    def test_chained_stages_are_not_wellformed(self) -> None:
        inv = Invocation(
            substantive_stages_launched=REGRESSION_FIXTURE["invocation"][
                "substantive_stages_launched"
            ],
            deterministic_terminal_actions=REGRESSION_FIXTURE["invocation"][
                "deterministic_terminal_actions"
            ],
        )
        self.assertEqual(invocation_wellformed(inv), REGRESSION_FIXTURE["expected_wellformed"])

    def test_narrated_review_is_not_a_pass(self) -> None:
        claim = ReviewClaim(**REGRESSION_FIXTURE["narrated_review"])
        self.assertEqual(counts_as_pass(claim), REGRESSION_FIXTURE["expected_counts_as_pass"])


class OneTransitionPerInvocationTests(unittest.TestCase):
    def test_single_stage_launch_is_wellformed(self) -> None:
        self.assertTrue(invocation_wellformed(Invocation(1, 0)))

    def test_single_terminal_action_is_wellformed(self) -> None:
        self.assertTrue(invocation_wellformed(Invocation(0, 1)))

    def test_no_action_is_wellformed(self) -> None:
        self.assertTrue(invocation_wellformed(Invocation(0, 0)))

    def test_two_substantive_stages_is_not_wellformed(self) -> None:
        self.assertFalse(invocation_wellformed(Invocation(2, 0)))

    def test_stage_plus_terminal_action_is_not_wellformed(self) -> None:
        self.assertFalse(invocation_wellformed(Invocation(1, 1)))

    def test_five_named_substantive_stages_exist(self) -> None:
        self.assertEqual(
            {s.value for s in SUBSTANTIVE_STAGES},
            {"IMPLEMENTER", "CHECKER", "SKEPTIC_REVIEWER", "REPAIRER", "INTEGRATOR"},
        )

    def test_incomplete_invocation_raises(self) -> None:
        with self.assertRaises(TypeError):
            Invocation(substantive_stages_launched=1)  # type: ignore[call-arg]


class NormalInputRejectionTests(unittest.TestCase):
    def test_compact_state_and_receipt_reference_are_normal_input(self) -> None:
        self.assertTrue(accepts_as_normal_input(InputKind.COMPACT_STATE))
        self.assertTrue(accepts_as_normal_input(InputKind.RECEIPT_REFERENCE))

    def test_raw_evidence_and_history_are_not_normal_input(self) -> None:
        self.assertFalse(accepts_as_normal_input(InputKind.RAW_EVIDENCE))
        self.assertFalse(accepts_as_normal_input(InputKind.COMPLETED_HISTORY))

    def test_raw_evidence_opens_only_for_named_exception(self) -> None:
        self.assertFalse(may_open_raw_evidence(RawOpenRequest(False, False, False)))
        self.assertTrue(may_open_raw_evidence(RawOpenRequest(True, False, False)))
        self.assertTrue(may_open_raw_evidence(RawOpenRequest(False, True, False)))
        self.assertTrue(may_open_raw_evidence(RawOpenRequest(False, False, True)))


class NarratedPassRejectionTests(unittest.TestCase):
    def test_fully_executed_clean_review_counts(self) -> None:
        self.assertTrue(
            counts_as_pass(
                ReviewClaim(
                    executed_full_runskeptic=True,
                    considered_all_thinkers=True,
                    included_receipt=True,
                    named_identity_matches=True,
                    blocking_finding=False,
                )
            )
        )

    def test_missing_execution_does_not_count(self) -> None:
        self.assertFalse(
            counts_as_pass(
                ReviewClaim(
                    executed_full_runskeptic=False,
                    considered_all_thinkers=True,
                    included_receipt=True,
                    named_identity_matches=True,
                    blocking_finding=False,
                )
            )
        )

    def test_wrong_identity_does_not_count(self) -> None:
        self.assertFalse(
            counts_as_pass(
                ReviewClaim(
                    executed_full_runskeptic=True,
                    considered_all_thinkers=True,
                    included_receipt=True,
                    named_identity_matches=False,
                    blocking_finding=False,
                )
            )
        )

    def test_blocking_finding_does_not_count(self) -> None:
        self.assertFalse(
            counts_as_pass(
                ReviewClaim(
                    executed_full_runskeptic=True,
                    considered_all_thinkers=True,
                    included_receipt=True,
                    named_identity_matches=True,
                    blocking_finding=True,
                )
            )
        )


class ReopenRequiresInvalidationTests(unittest.TestCase):
    def test_accepted_stage_does_not_reopen_without_invalidation(self) -> None:
        self.assertFalse(may_reopen_accepted_stage(False))

    def test_accepted_stage_reopens_on_deterministic_invalidation(self) -> None:
        self.assertTrue(may_reopen_accepted_stage(True))


class DirectExecutionExceptionTests(unittest.TestCase):
    def _base(self, **overrides) -> DirectExecCase:
        fields = dict(
            small=True,
            reversible=True,
            single_stage=True,
            delegation_costs_more=True,
            repeated_review=False,
            repair=False,
            integration=False,
            cross_session=False,
            context_exhaustion_risk=False,
        )
        fields.update(overrides)
        return DirectExecCase(**fields)

    def test_small_reversible_single_stage_task_may_execute_directly(self) -> None:
        self.assertTrue(may_execute_directly(self._base()))

    def test_delegation_cheaper_task_must_delegate(self) -> None:
        self.assertFalse(may_execute_directly(self._base(delegation_costs_more=False)))

    def test_multi_stage_task_must_delegate(self) -> None:
        self.assertFalse(may_execute_directly(self._base(single_stage=False)))

    def test_excluded_categories_are_never_covered(self) -> None:
        for exclusion in [
            "repeated_review",
            "repair",
            "integration",
            "cross_session",
            "context_exhaustion_risk",
        ]:
            with self.subTest(exclusion=exclusion):
                self.assertFalse(may_execute_directly(self._base(**{exclusion: True})))


# --------------------------------------------------------------------------
# Marker tests: the governing prose must be present in lead-agent-prompt.md
# --------------------------------------------------------------------------


class StatelessOrchestrationMarkerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.lead = LEAD_PROMPT.read_text(encoding="utf-8")
        cls.orch = section(cls.lead, "## Stateless orchestration")

    def test_stateless_invariant_is_declared(self) -> None:
        self.assertIn("practically stateless orchestrator", self.orch)
        self.assertIn(
            "performs no substantive stage work itself", self.orch
        )
        self.assertIn(
            "does not carry completed-stage history in active context", self.orch
        )

    def test_compact_state_whitelist_is_enumerated(self) -> None:
        for item in [
            "task identity",
            "current stage",
            "candidate commit and tree",
            "accepted receipt references and hashes",
            "PASS streak, fix-cycle, and retry counters",
            "unresolved blocker",
            "next authorized stage",
            "closure-ready status",
        ]:
            self.assertIn(item, self.orch)

    def test_state_is_in_context_not_a_directory(self) -> None:
        self.assertIn(
            "not a repository state directory, controller, or on-disk store",
            self.orch,
        )

    def test_forbidden_ingestion_list_is_enumerated(self) -> None:
        for item in [
            "implementation history",
            "raw logs",
            "full diffs",
            "full test output",
            "worker reasoning",
            "previous reviewer reasoning",
            "completed-stage narratives",
            "advisor discussions",
            "complete evidence chains",
        ]:
            self.assertIn(item, self.orch)

    def test_raw_evidence_opens_only_for_named_exceptions(self) -> None:
        for cond in [
            "one named unresolved blocker",
            "a receipt mismatch",
            "deterministic invalidation of an accepted stage",
        ]:
            self.assertIn(cond, self.orch)

    def test_five_stage_agents_are_named(self) -> None:
        for stage in [
            "Implementer",
            "Checker",
            "Skeptic Reviewer",
            "Repairer",
            "Integrator",
        ]:
            self.assertIn(stage, self.orch)
        self.assertIn("never a sub-Lead and never a recursive hierarchy", self.orch)

    def test_one_transition_per_invocation_cycle(self) -> None:
        self.assertIn(
            "One Lead invocation performs at most one lifecycle transition", self.orch
        )
        for step in [
            "read and validate the compact state",
            "launch one fresh stage agent or perform one deterministic terminal action",
            "validate one compact receipt",
            "update the authoritative state",
        ]:
            self.assertIn(step, self.orch)
        self.assertIn(
            "must not own two substantive stages in one invocation", self.orch
        )

    def test_lead_must_nots(self) -> None:
        for must_not in [
            "perform RunSkeptic itself",
            "repair the candidate",
            "review a reviewer",
            "add an advisor for reassurance",
            "reconstruct accepted evidence without a named blocker",
            "repeat an accepted stage without deterministic invalidation",
            "count narrated or simulated reviews as executed PASS results",
            "continue after closure",
        ]:
            self.assertIn(must_not, self.orch)

    def test_narrated_pass_is_rejected(self) -> None:
        self.assertIn(
            "A described, planned, or narrated review is not an executed PASS.",
            self.orch,
        )

    def test_proportionality_exception_and_exclusions(self) -> None:
        self.assertIn(
            "may execute directly when delegation would cost more than the work",
            self.orch,
        )
        self.assertIn(
            "must not cover repeated review, repair, integration, cross-session work",
            self.orch,
        )

    def test_section_references_rather_than_restates_checkpoint_doctrine(self) -> None:
        # The slice sharpens existing doctrine; it must point back to it,
        # not re-derive the invalidation/capacity mechanics.
        self.assertIn("Checkpoint-first resume and closure fast path", self.orch)


if __name__ == "__main__":
    unittest.main()

# made by AI
"""Contract tests for the recursive A/B/C hierarchical lead-context contract.

Slice H1 defines a recursive Executive Lead (A) / Phase Supervisor (B) /
Worker-Checker-Reviewer (C) execution hierarchy whose purpose is to stop the
task-level Lead from accumulating worker-level evidence and execution history.
The hierarchy must control ownership, information flow, and promotion authority,
and must be realizable with or without genuine nested agents.

Like the other contract tests in this suite, these check that the written
contract is present -- not agent behavior or genuine reviewer independence.
The canonical home for the hierarchy is agents/task-prompt.md;
agents/lead-agent-prompt.md references and specializes it. skeptic.md and
skeptic-questions.md are protected and must stay byte-identical.
"""
from __future__ import annotations

import hashlib
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TASK_PROMPT = ROOT / "agents" / "task-prompt.md"
LEAD_PROMPT = ROOT / "agents" / "lead-agent-prompt.md"
SKEPTIC = ROOT / "skeptic.md"
SKEPTIC_QUESTIONS = ROOT / "skeptic-questions.md"


def _git_blob_sha1(path: Path) -> str:
    content = path.read_bytes()
    header = f"blob {len(content)}\0".encode()
    return hashlib.sha1(header + content).hexdigest()


class CanonicalHierarchyHomeTests(unittest.TestCase):
    """The A/B/C hierarchy is defined once, in agents/task-prompt.md."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.task = TASK_PROMPT.read_text(encoding="utf-8")

    def test_hierarchy_section_and_three_roles_exist(self) -> None:
        for marker in [
            "## Recursive execution hierarchy (A/B/C)",
            "A -- Executive Lead",
            "B -- Phase Supervisor",
            "C -- Worker, Checker, or Reviewer",
        ]:
            self.assertIn(marker, self.task)

    def test_hierarchy_controls_all_three_dimensions(self) -> None:
        # Hierarchy alone is insufficient unless ownership, information flow,
        # and promotion authority are all explicit.
        self.assertIn(
            "controls three things at once -- ownership, information flow, and "
            "promotion authority",
            self.task,
        )
        self.assertIn(
            "Hierarchy alone is insufficient unless all three are explicit.",
            self.task,
        )

    def test_hierarchy_is_portable_without_nested_agents(self) -> None:
        # A P4 reviewer requirement and a stated CONFLICT rule: the design must
        # be implementable in runtimes without genuine nested agents.
        self.assertIn(
            "It is a set of roles and boundaries, not a requirement for genuine "
            "nested agents.",
            self.task,
        )
        self.assertIn("must hold with or without nested agents", self.task)

    def test_roles_map_onto_existing_vocabulary(self) -> None:
        # Scenario 13: existing Task-Prompt Builder and verification terminology
        # remain consistent -- map A/B/C onto the existing role names rather than
        # inventing a parallel vocabulary.
        self.assertIn(
            "A -- Executive Lead is the Lead / Orchestrator", self.task
        )
        self.assertIn(
            "Reviewer is the independent-evaluation role this document also "
            "calls Judge",
            self.task,
        )
        self.assertIn(
            "B -- Phase Supervisor is a new bounded layer between A and C",
            self.task,
        )


class ExecutiveLeadContextProtectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.task = TASK_PROMPT.read_text(encoding="utf-8")

    def test_a_does_not_receive_full_c_evidence(self) -> None:
        # Scenario 1: three verbose C outputs do not all reach A.
        for marker in [
            "A must not normally receive:",
            "raw worker reasoning",
            "full logs or diffs",
            "entire evidence packages",
        ]:
            self.assertIn(marker, self.task)

    def test_a_opens_lower_evidence_only_for_dispute(self) -> None:
        self.assertIn(
            "A opens lower-level evidence only for a named dispute or "
            "deterministic invalidation.",
            self.task,
        )

    def test_a_does_not_directly_manage_c_when_b_exists(self) -> None:
        # Scenario 5: A cannot directly absorb full C output when B exists.
        self.assertIn(
            "When a B Supervisor exists, A does not directly manage that phase's "
            "C agents; it manages B and consumes B's one upward receipt.",
            self.task,
        )


class PhaseSupervisorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.task = TASK_PROMPT.read_text(encoding="utf-8")

    def test_b_owns_one_phase_and_preserves_dissent(self) -> None:
        # Scenario 2: B must preserve minority dissent upward.
        for marker in [
            "B owns exactly one bounded phase",
            "preserves dissent and contradictions",
            "produces one compact upward phase receipt",
        ]:
            self.assertIn(marker, self.task)

    def test_b_cannot_expand_objective_or_self_accept(self) -> None:
        # Scenario 3: B cannot both implement and finally accept the same phase.
        for marker in [
            "expand the task objective",
            "claim task-level DONE",
            "accept its own unverified implementation",
            "forward all C output to A",
            "continue optional work after phase acceptance",
        ]:
            self.assertIn(marker, self.task)

    def test_context_protection_applies_recursively_to_b(self) -> None:
        # Scenario 6: context limits apply to B recursively.
        self.assertIn(
            "Context protection applies recursively", self.task
        )
        self.assertIn(
            "B must use references and bounded receipts rather than accumulating "
            "unlimited C history.",
            self.task,
        )


class WorkerCheckerReviewerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.task = TASK_PROMPT.read_text(encoding="utf-8")

    def test_c_receives_bounded_ticket_fields(self) -> None:
        self.assertIn(
            "C receives one bounded Dispatch Ticket with role, objective, source "
            "of truth, scope, allowed and forbidden actions, output limit, "
            "evidence destination, and acceptance and stop rules.",
            self.task,
        )

    def test_c_cannot_self_promote_or_expand_scope(self) -> None:
        # Scenario 4: C cannot claim phase or task completion.
        for marker in [
            "cannot promote its own output across a trust boundary",
            "cannot silently expand scope",
            "reports adjacent findings without acting on them",
        ]:
            self.assertIn(marker, self.task)

    def test_c_reports_to_b_not_a(self) -> None:
        # Scenario 5 (C side): returns evidence to B, not directly to A.
        self.assertIn(
            "returns evidence to its B Supervisor, not directly to A", self.task
        )
        self.assertIn(
            "It does not claim phase or task completion.", self.task
        )


class NoSelfPromotionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.task = TASK_PROMPT.read_text(encoding="utf-8")

    def test_no_producer_promotes_own_output_across_trust_boundary(self) -> None:
        # Scenario 3: independent or deterministic check required for acceptance.
        self.assertIn(
            "No producer may accept or promote its own output across a trust "
            "boundary.",
            self.task,
        )
        self.assertIn(
            "acceptance requires an independent Reviewer or a deterministic "
            "Checker",
            self.task,
        )
        self.assertIn(
            "C cannot self-accept to B, and B cannot self-accept its own "
            "implementation as the phase result to A.",
            self.task,
        )


class UpwardPhaseReceiptTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.task = TASK_PROMPT.read_text(encoding="utf-8")

    def test_receipt_has_required_bounded_fields(self) -> None:
        # DONE 4: one bounded receipt with references and material conclusions.
        for marker in [
            "### Upward phase receipt (B -> A)",
            "phase ID and status",
            "accepted artifact identity",
            "evidence location and hash",
            "acceptance owner and validation result",
            "material findings",
            "unresolved dissent, contradiction, unknown, or blocker",
            "budget / capacity result",
            "next authorized state",
        ]:
            self.assertIn(marker, self.task)

    def test_receipt_carries_references_not_full_evidence(self) -> None:
        # Scenario 12: references and hashes preferred over embedded logs/diffs.
        self.assertIn(
            "The receipt carries references and material conclusions, not full "
            "evidence.",
            self.task,
        )
        self.assertIn(
            "every field that would otherwise embed a log, diff, or full "
            "artifact must instead carry a reference (path, ref, hash, line "
            "range) and the material conclusion",
            self.task,
        )

    def test_receipt_is_a_claim_until_verified(self) -> None:
        # Scenario 11: missing receipt evidence identity blocks promotion.
        self.assertIn(
            "It is a claim until A or a deterministic Checker verifies its "
            "material fields.",
            self.task,
        )

    def test_size_bound_is_by_field_not_arbitrary_number(self) -> None:
        # The measurable constraint is a bounded-field rule justified by the
        # document's existing compact-receipt convention, not a new number.
        self.assertIn(
            "Size is bounded by field, not by an arbitrary count", self.task
        )
        self.assertIn("it introduces no new numeric limit", self.task)

    def test_dissent_survives_upward_compression(self) -> None:
        # DONE 5 / Scenario 2: dissent, contradictions, blockers, and unknowns
        # cannot be silently removed during upward compression.
        self.assertIn(
            "Minority dissent, contradictions, blockers, and unknowns cannot be "
            "silently removed during upward compression.",
            self.task,
        )
        self.assertIn(
            "is a defective receipt, not a smaller one", self.task
        )


class SafeHierarchyCollapseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.task = TASK_PROMPT.read_text(encoding="utf-8")

    def test_collapse_to_a_only_permitted(self) -> None:
        # Scenario 8: a tiny read-only task may collapse to A-only.
        self.assertIn(
            "A-only execution for tiny, reversible, non-delegated work",
            self.task,
        )

    def test_collapse_to_a_to_c_permitted(self) -> None:
        # Scenario 9: one small delegation may use A -> C.
        self.assertIn(
            "A -> C for one small bounded delegation when creating a B "
            "Supervisor would cost more than the work",
            self.task,
        )

    def test_full_hierarchy_required_for_material_work(self) -> None:
        # Scenario 10: multi-worker or implementation-plus-checking requires B.
        self.assertIn("Require A -> B -> C when the work materially includes:", self.task)
        for marker in [
            "multiple C agents",
            "implementation plus checking",
            "independent review",
            "meaningful context-exhaustion risk",
        ]:
            self.assertIn(marker, self.task)

    def test_collapse_does_not_waive_verification_or_invent_layers(self) -> None:
        self.assertIn(
            "Collapsed execution does not waive receipt verification, authority "
            "boundaries, or exact DONE.",
            self.task,
        )
        self.assertIn(
            "do not describe a single-context task as if a separate B or C "
            "reviewed it, and do not claim independence a collapsed structure "
            "did not have",
            self.task,
        )

    def test_closure_ready_state_still_forbids_optional_review(self) -> None:
        # Scenario 7: A closure-ready state forbids an optional advisor/review.
        # This ties the new hierarchy to the pre-existing closure rule.
        self.assertIn(
            'do not add an advisor, Judge, optional review, new inventory, broad '
            'analysis, or "one more check"',
            self.task,
        )


class LeadPromptReferencesCanonicalHierarchyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.lead = LEAD_PROMPT.read_text(encoding="utf-8")
        cls.task = TASK_PROMPT.read_text(encoding="utf-8")

    def test_lead_references_canonical_hierarchy(self) -> None:
        self.assertIn(
            "recursive A/B/C execution hierarchy defined in "
            "`agents/task-prompt.md`",
            self.lead,
        )
        self.assertIn(
            "That document is authoritative for the hierarchy, its upward phase "
            "receipt, and its safe-collapse rules; do not restate the full "
            "definitions here.",
            self.lead,
        )

    def test_lead_reconciles_existing_operational_roles(self) -> None:
        self.assertIn(
            "A -- Executive Lead is this Orchestrator", self.lead
        )
        self.assertIn(
            "B -- Phase Supervisor is a bounded per-phase owner between the Lead "
            "and its workers",
            self.lead,
        )

    def test_lead_states_recursive_context_and_no_self_promotion(self) -> None:
        # Scenario 6 (Lead side) and DONE 6/7 restated compactly by reference.
        self.assertIn(
            "Context protection applies recursively to B as well as to the Lead",
            self.lead,
        )
        self.assertIn(
            "no producer may accept or promote its own output across a trust "
            "boundary",
            self.lead,
        )

    def test_full_role_definition_lives_only_in_task_prompt(self) -> None:
        # No-duplicate discipline: the canonical defining sentence appears once,
        # in the canonical home, mirroring the verification-vocabulary pattern.
        sentence = "B -- Phase Supervisor is a new bounded layer between A and C"
        self.assertEqual(self.task.count(sentence), 1)
        self.assertEqual(self.lead.count(sentence), 0)


class ProtectedFilesUnchangedTests(unittest.TestCase):
    """Scenario 14 / DONE 11: protected files remain byte-identical."""

    def test_skeptic_md_hash_matches_recorded_baseline(self) -> None:
        self.assertEqual(
            _git_blob_sha1(SKEPTIC),
            "63602be10e0e532ce512aaac0ea6a4d3cd67ce09",
        )

    def test_skeptic_questions_md_hash_matches_recorded_baseline(self) -> None:
        self.assertEqual(
            _git_blob_sha1(SKEPTIC_QUESTIONS),
            "f5f299d2e3fa925dabb5ba4e661cbb5fa3c1c6cd",
        )


if __name__ == "__main__":
    unittest.main()

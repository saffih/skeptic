# made by AI
"""Contract tests for the canonical verification vocabulary.

These tests check that AGENTS.md defines Verification, Skeptic verification,
Pure Skeptic verification, and Fix Skeptic verification as the single
canonical source, and that agents/task-prompt.md and
agents/task-prompt-builder.md reference or specialize those definitions
instead of restating a competing full definition. skeptic.md must stay
byte-identical to its pre-existing baseline.

agents/lead-agent-prompt.md is now a compact orchestration-only contract; it
does not name or cross-reference the AGENTS.md vocabulary. It instead owns a
narrower current verification rule -- delegate to a Boundary Agent, allowlist
the receipt fields, and drive a consecutive-PASS streak -- checked separately
below against its actual current text.

Like the other contract tests in this suite, these check that the written
contract is present -- not agent behavior or genuine reviewer independence.
"""
from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AGENTS = ROOT / "AGENTS.md"
LEAD_PROMPT = ROOT / "agents" / "lead-agent-prompt.md"
TASK_PROMPT = ROOT / "agents" / "task-prompt.md"
BUILDER = ROOT / "agents" / "task-prompt-builder.md"
SKEPTIC = ROOT / "skeptic.md"


class CanonicalDefinitionsLiveInAgentsMdTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.agents = AGENTS.read_text(encoding="utf-8")

    def test_four_terms_defined_in_agents_md(self) -> None:
        for marker in [
            "### Verification",
            "### Skeptic verification",
            "### Pure Skeptic verification",
            "### Fix Skeptic verification",
        ]:
            self.assertIn(marker, self.agents)

    def test_agents_md_states_ownership_of_vocabulary(self) -> None:
        self.assertIn(
            "`AGENTS.md` is the canonical home for these four verification terms",
            self.agents,
        )
        self.assertIn(
            "they must not restate a competing full definition",
            self.agents,
        )

    def test_skeptic_md_stays_authoritative_for_pass_internals(self) -> None:
        self.assertIn(
            "`skeptic.md` remains authoritative for the internal mechanics of one RunSkeptic pass",
            self.agents,
        )
        self.assertIn("which these terms do not redefine", self.agents)

    def test_general_verification_does_not_require_runskeptic(self) -> None:
        self.assertIn(
            "Verification is not confidence, repeated prose review, automatically RunSkeptic, or automatically a three-pass process.",
            self.agents,
        )

    def test_skeptic_verification_is_three_consecutive_pass(self) -> None:
        self.assertIn(
            "Skeptic verification is the orchestration-level completion criterion of three consecutive complete RunSkeptic PASS results on the same unchanged artifact identity.",
            self.agents,
        )

    def test_action_and_conflict_do_not_count_as_pass(self) -> None:
        self.assertIn(
            "A counted PASS is the review-level PASS with no blocking finding; ACTION and CONFLICT do not count as PASS.",
            self.agents,
        )

    def test_fourth_pass_forbidden_after_acceptance(self) -> None:
        self.assertIn(
            "After the third PASS, accept and stop; do not perform a fourth reassurance pass.",
            self.agents,
        )

    def test_pure_mode_cannot_fix(self) -> None:
        self.assertIn(
            "Pure Skeptic verification is read-only Skeptic verification: no fixes, no artifact changes, no mutation authority.",
            self.agents,
        )
        self.assertIn(
            "ACTION or CONFLICT stops without acceptance.",
            self.agents,
        )

    def test_fix_mode_resets_streak_on_change(self) -> None:
        self.assertIn(
            "Any artifact change resets the consecutive-PASS count to zero.",
            self.agents,
        )

    def test_fix_workflow_must_declare_bounds_before_execution(self) -> None:
        for marker in [
            "artifact identity",
            "maximum fix cycles",
            "maximum total RunSkeptic passes",
            "an early-stop rule for when the remaining allowance cannot still yield three consecutive passes",
            "Do not enlarge limits because the workflow failed.",
        ]:
            self.assertIn(marker, self.agents)

    def test_ordinary_readiness_gate_is_not_skeptic_verification(self) -> None:
        self.assertIn(
            'is a different, bounded purpose and is not Skeptic verification unless explicitly invoked as pure or fix Skeptic verification',
            self.agents,
        )


class NoDuplicateFullDefinitionOutsideAgentsMdTests(unittest.TestCase):
    """A canonical defining sentence must appear once, in AGENTS.md only."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.files = {
            "AGENTS.md": AGENTS.read_text(encoding="utf-8"),
            "lead-agent-prompt.md": LEAD_PROMPT.read_text(encoding="utf-8"),
            "task-prompt.md": TASK_PROMPT.read_text(encoding="utf-8"),
            "task-prompt-builder.md": BUILDER.read_text(encoding="utf-8"),
        }

    def _assert_sentence_only_in_agents_md(self, sentence: str) -> None:
        occurrences = {name: text.count(sentence) for name, text in self.files.items()}
        total = sum(occurrences.values())
        self.assertEqual(
            total,
            1,
            f"expected exactly one occurrence of canonical sentence across governing "
            f"docs, found {occurrences!r}",
        )
        self.assertEqual(occurrences["AGENTS.md"], 1)

    def test_skeptic_verification_definition_sentence_is_unique(self) -> None:
        self._assert_sentence_only_in_agents_md(
            "Skeptic verification is the orchestration-level completion criterion of "
            "three consecutive complete RunSkeptic PASS results on the same unchanged "
            "artifact identity."
        )

    def test_pure_skeptic_verification_definition_sentence_is_unique(self) -> None:
        self._assert_sentence_only_in_agents_md(
            "Pure Skeptic verification is read-only Skeptic verification: no fixes, "
            "no artifact changes, no mutation authority."
        )

    def test_fix_skeptic_verification_numbered_procedure_is_unique(self) -> None:
        self._assert_sentence_only_in_agents_md(
            "1. Run complete RunSkeptic.\n"
            "2. On ACTION, apply only the smallest authorized evidence-supported fix.\n"
            "3. Any artifact change resets the consecutive-PASS count to zero."
        )

    def test_general_verification_definition_sentence_is_unique(self) -> None:
        self._assert_sentence_only_in_agents_md(
            "Verification is an evidence-based pass/fail process that checks a "
            "declared claim, artifact, phase, or result against explicit acceptance "
            "conditions and meaningful disconfirming checks."
        )


class LeadAgentPromptVerificationContractTests(unittest.TestCase):
    """`agents/lead-agent-prompt.md` is now a compact orchestration-only
    contract and no longer restates or cross-references the AGENTS.md
    verification vocabulary by name. It still owns a narrower, current
    verification rule: verification is always delegated to a fresh Boundary
    Agent, its receipt is limited to an explicit field allowlist, and the
    consecutive-PASS streak is the sole basis for stopping. These tests check
    that current rule as actually written, instead of the deleted
    canonical-vocabulary cross-reference and pure/fix mode language."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.lead = LEAD_PROMPT.read_text(encoding="utf-8")

    def test_verification_is_always_delegated_to_a_boundary_agent(self) -> None:
        self.assertIn("Verification is always performed by Boundary Agents.", self.lead)
        self.assertIn(
            "For RunSkeptic, dispatch a fresh Boundary Agent and permit only this receipt:",
            self.lead,
        )

    def test_runskeptic_receipt_is_field_limited(self) -> None:
        for field in [
            "candidate_identity",
            "verdict",
            "finding_ids",
            "report_identity",
            "receipt_identity",
        ]:
            self.assertIn(field, self.lead)
        self.assertIn("The full report must remain outside the Lead context.", self.lead)

    def test_pass_and_action_verdicts_drive_the_streak(self) -> None:
        self.assertIn(
            "If the verdict is PASS, increment the consecutive PASS count.",
            self.lead,
        )
        self.assertIn(
            "If the verdict is ACTION, reset the PASS count to zero and dispatch a "
            "fresh Boundary Agent to repair only the identified findings.",
            self.lead,
        )

    def test_any_candidate_change_resets_streak_and_stops_after_three_pass(self) -> None:
        self.assertIn(
            "Any candidate change resets the PASS count to zero.",
            self.lead,
        )
        self.assertIn(
            "Stop verification after three consecutive PASS results on the same "
            "unchanged candidate.",
            self.lead,
        )


class TaskPromptDistinguishesReadinessGateFromExplicitVerificationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.task = TASK_PROMPT.read_text(encoding="utf-8")

    def test_readiness_gate_not_misrepresented_as_three_pass_verification(self) -> None:
        self.assertIn(
            "It is not `Skeptic verification` as defined in `AGENTS.md`, and passing "
            "it must not be reported as satisfying the three-consecutive-PASS Skeptic "
            "verification criterion.",
            self.task,
        )

    def test_ordinary_default_still_documented_as_bounded_gate(self) -> None:
        # Locked by tests/test_task_prompt_contract.py; must survive unchanged.
        self.assertIn(
            "one initial pass plus at most two materially revised reruns",
            self.task,
        )

    def test_explicit_pure_or_fix_mode_uses_agents_md_contract(self) -> None:
        self.assertIn(
            "use the canonical definitions and bounds in `AGENTS.md`",
            self.task,
        )

    def test_template_exposes_required_verification_fields(self) -> None:
        for marker in [
            "RunSkeptic mode (ordinary readiness gate / pure Skeptic verification / fix Skeptic verification):",
            "Artifact identity/hash under review:",
            "Required consecutive PASS count:",
            "Maximum fix cycles:",
            "Maximum total RunSkeptic passes:",
            "Remaining-budget early-stop rule:",
        ]:
            self.assertIn(marker, self.task)


class BuilderPlanSkepticVerificationIsASpecializationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.builder = BUILDER.read_text(encoding="utf-8")

    def test_plan_skeptic_verification_references_canonical_fix_verification(self) -> None:
        self.assertIn(
            "**Plan Skeptic verification** is this Builder's specialization of the "
            "canonical **Fix Skeptic verification** defined in `AGENTS.md`",
            self.builder,
        )
        self.assertIn("Do not restate the canonical fix procedure here", self.builder)

    def test_plan_specific_artifact_identity_preserved(self) -> None:
        self.assertIn(
            "the artifact identity is fixed to the exact plan bytes and their SHA-256",
            self.builder,
        )

    def test_repair_cycle_and_total_review_bounds_preserved(self) -> None:
        for marker in [
            "at most two plan-changing repair cycles",
            "at most seven RunSkeptic reviews total",
            "stop early when the remaining review allowance cannot still produce three consecutive passes",
        ]:
            self.assertIn(marker, self.builder)

    def test_receipts_and_blocked_outcome_preserved(self) -> None:
        for marker in [
            "preserve every required RunSkeptic receipt and the plan SHA-256",
            "`PLAN_VERIFICATION_BLOCKED`",
        ]:
            self.assertIn(marker, self.builder)

    def test_same_context_disclosure_preserved(self) -> None:
        self.assertIn("must not be described as independent", self.builder)

    def test_freeze_on_three_consecutive_pass_preserved(self) -> None:
        self.assertIn(
            "After three consecutive `PASS` verdicts on one unchanged hash, freeze: "
            "the verified plan, its SHA-256, the three PASS receipts, the objective "
            "identity, and any unresolved assumptions.",
            self.builder,
        )


class SkepticMdUnchangedTests(unittest.TestCase):
    """skeptic.md is protected; this task must not touch it."""

    def test_skeptic_md_hash_matches_recorded_baseline(self) -> None:
        import hashlib

        recorded_baseline = "63602be10e0e532ce512aaac0ea6a4d3cd67ce09"  # git blob SHA-1
        content = SKEPTIC.read_bytes()
        header = f"blob {len(content)}\0".encode()
        git_blob_sha1 = hashlib.sha1(header + content).hexdigest()
        self.assertEqual(git_blob_sha1, recorded_baseline)


if __name__ == "__main__":
    unittest.main()

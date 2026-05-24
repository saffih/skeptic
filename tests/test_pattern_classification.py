from pathlib import Path
import unittest

TEXT = Path("skeptic.md").read_text(encoding="utf-8")


class PatternClassificationTests(unittest.TestCase):
    def test_pattern_classification_section_exists(self):
        self.assertIn("### Pattern Classification", TEXT)
        self.assertIn("Repeated findings are candidate patterns, not proven patterns.", TEXT)

    def test_candidate_pattern_requires_rule_boundary_lifecycle_and_challenge(self):
        for marker in [
            "shared rule, root cause, or violated invariant",
            "boundary: included, excluded, uncertain",
            "lifecycle point",
            "why they may not be one pattern",
            "Promote only if the rule and boundary survive challenge.",
        ]:
            self.assertIn(marker, TEXT)

    def test_promoted_pattern_plans_treatment_without_acting(self):
        for marker in [
            "define the common treatment",
            "split risk tiers if needed",
            "plan action only after DECIDE=FIX",
            "list exceptions",
        ]:
            self.assertIn(marker, TEXT)

    def test_superficial_batching_is_forbidden(self):
        self.assertIn(
            "Never batch by similar wording, location, file shape, or symptom alone.",
            TEXT,
        )

    def test_minimal_invariants_exist(self):
        for marker in [
            "Never promote repeated findings without a shared rule and boundary.",
            "Never batch without asking why they are not one pattern.",
            "Never use Pattern Classification to act before DECIDE=FIX.",
        ]:
            self.assertIn(marker, TEXT)

    def test_existing_runskeptic_contract_is_preserved(self):
        for marker in [
            "`RunSkeptic` is the formal invocation string",
            "Do not use memory, summaries, previous variants, or generated replacements as substitutes.",
            "Treat `skeptic.md` as the runtime source of truth.",
            "Apply the current recipe exactly and in order.",
            "Use the exact output categories from this file.",
            "Every task ends as HANDLED or CONFLICT.",
        ]:
            self.assertIn(marker, TEXT)


if __name__ == "__main__":
    unittest.main()

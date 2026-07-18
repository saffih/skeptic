# made by AI
from __future__ import annotations

import unittest
from dataclasses import dataclass
from pathlib import Path

from test_pareto_frontier import (
    DEFER_EXISTING,
    DOMINANCE_UNPROVEN,
    ELIMINATE_DOMINATED,
    NOT_APPLICABLE,
    PRESERVE_FRONTIER,
)

ROOT = Path(__file__).resolve().parents[1]
SKEPTIC = ROOT / "skeptic.md"
GOVERNANCE = ROOT / "skeptic-tests.md"

CH_CR = "CH:CR"
SH_WL = "SH:WL"

ROUTING_HEADER = "#### Constraint, leverage, and dominance routing"


@dataclass(frozen=True)
class RoutingCase:
    case_id: str
    expected_findings: frozenset[str]
    expected_pf: str
    wrong_constraint: bool = False
    tradeoff_present: bool = False
    wrong_lever: bool = False
    live_options: int = 0
    dominated_option_present: bool = False
    dominance_evidence_complete: bool = True


def route(case: RoutingCase) -> tuple[frozenset[str], str]:
    """Executable reference for the documented routing contract.

    Each lens fires only when its entity is present; a live wrong-constraint
    finding defers dominance elimination; incomplete dominance evidence fails
    closed without inventing constraint or leverage findings.
    """
    findings = set()
    if case.wrong_constraint:
        findings.add(CH_CR)
    if case.tradeoff_present and case.wrong_lever:
        findings.add(SH_WL)

    if case.live_options < 2:
        pf = NOT_APPLICABLE
    elif case.wrong_constraint:
        pf = DEFER_EXISTING
    elif not case.dominance_evidence_complete:
        pf = DOMINANCE_UNPROVEN
    elif case.dominated_option_present:
        pf = ELIMINATE_DOMINATED
    else:
        pf = PRESERVE_FRONTIER
    return frozenset(findings), pf


SCENARIOS = (
    # Wrong bottleneck, no trade-off, no option set: constraint lens only.
    RoutingCase(
        "RT01",
        frozenset({CH_CR}),
        NOT_APPLICABLE,
        wrong_constraint=True,
    ),
    # Correct bottleneck, wrong intervention inside a real trade-off.
    RoutingCase(
        "RT02",
        frozenset({SH_WL}),
        NOT_APPLICABLE,
        tradeoff_present=True,
        wrong_lever=True,
    ),
    # Several options, one strictly dominated, no constraint doubt.
    RoutingCase(
        "RT03",
        frozenset(),
        ELIMINATE_DOMINATED,
        live_options=3,
        dominated_option_present=True,
    ),
    # Wrong bottleneck plus apparently dominated options: constraint finding
    # defers premature Pareto elimination.
    RoutingCase(
        "RT04",
        frozenset({CH_CR}),
        DEFER_EXISTING,
        wrong_constraint=True,
        live_options=2,
        dominated_option_present=True,
    ),
    # Real trade-off with frontier options and no dominance: leverage finding,
    # no elimination.
    RoutingCase(
        "RT05",
        frozenset({SH_WL}),
        PRESERVE_FRONTIER,
        tradeoff_present=True,
        wrong_lever=True,
        live_options=2,
    ),
    # Ordinary task: all three lenses remain silent.
    RoutingCase("RT06", frozenset(), NOT_APPLICABLE),
    # Wrong bottleneck and wrong lever both materially apply: two distinct
    # findings, no duplication.
    RoutingCase(
        "RT07",
        frozenset({CH_CR, SH_WL}),
        NOT_APPLICABLE,
        wrong_constraint=True,
        tradeoff_present=True,
        wrong_lever=True,
    ),
    # Incomplete dominance evidence fails closed and invents nothing.
    RoutingCase(
        "RT08",
        frozenset(),
        DOMINANCE_UNPROVEN,
        live_options=2,
        dominance_evidence_complete=False,
    ),
)


class RoutingContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.skeptic = SKEPTIC.read_text(encoding="utf-8")
        cls.governance = GOVERNANCE.read_text(encoding="utf-8")

    def _routing_section(self) -> str:
        sh_start = self.skeptic.index("### Saffi (SH)")
        sh_end = self.skeptic.index("## 4. Structural Checks")
        section = self.skeptic[sh_start:sh_end]
        start = section.index(ROUTING_HEADER)
        end = section.index("If no real opposing forces")
        return section[start:end]

    def test_all_scenarios_match_the_oracle(self) -> None:
        self.assertEqual(len(SCENARIOS), 8)
        observed = {case.case_id: route(case) for case in SCENARIOS}
        expected = {
            case.case_id: (case.expected_findings, case.expected_pf)
            for case in SCENARIOS
        }
        self.assertEqual(observed, expected)

    def test_wrong_constraint_blocks_premature_elimination(self) -> None:
        case = next(case for case in SCENARIOS if case.case_id == "RT04")
        self.assertTrue(case.dominated_option_present)
        findings, pf = route(case)
        self.assertIn(CH_CR, findings)
        self.assertEqual(pf, DEFER_EXISTING)
        self.assertNotEqual(pf, ELIMINATE_DOMINATED)

    def test_co_report_is_two_distinct_findings_not_duplicates(self) -> None:
        findings, _ = route(
            next(case for case in SCENARIOS if case.case_id == "RT07")
        )
        self.assertEqual(findings, frozenset({CH_CR, SH_WL}))
        self.assertEqual(len(findings), 2)

    def test_ordinary_task_stays_silent(self) -> None:
        findings, pf = route(
            next(case for case in SCENARIOS if case.case_id == "RT06")
        )
        self.assertEqual(findings, frozenset())
        self.assertEqual(pf, NOT_APPLICABLE)

    def test_unproven_dominance_invents_no_other_finding(self) -> None:
        findings, pf = route(
            next(case for case in SCENARIOS if case.case_id == "RT08")
        )
        self.assertEqual(pf, DOMINANCE_UNPROVEN)
        self.assertEqual(findings, frozenset())

    def test_runtime_contains_the_routing_contract(self) -> None:
        section = self._routing_section()
        for marker in [
            "different questions about different entities",
            "triggers none of them",
            "skip absent stages",
            "does not require inventing a bottleneck",
            "premature",
            DEFER_EXISTING,
            "materially different defects",
            "merge them in STABILIZE",
            "neither substitutes for constraint or leverage analysis",
        ]:
            self.assertIn(marker, section)

    def test_routing_contract_stays_compact(self) -> None:
        line_count = self._routing_section().count("\n")
        self.assertLessEqual(line_count, 30)

    def test_no_mandatory_universal_sequence(self) -> None:
        section = self._routing_section()
        self.assertIn("practical default order", section)
        self.assertNotIn("must always run", section)
        self.assertNotIn("mandatory sequence", section)

    def test_governance_binds_the_coverage(self) -> None:
        for marker in [
            "tests/test_constraint_leverage_dominance_routing.py",
            "wrong-constraint deferral",
        ]:
            self.assertIn(marker, self.governance)


if __name__ == "__main__":
    unittest.main()

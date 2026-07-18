from __future__ import annotations

import unittest
from dataclasses import dataclass, field
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKEPTIC = ROOT / "skeptic.md"
GOVERNANCE = ROOT / "skeptic-tests.md"

NOT_APPLICABLE = "NOT_APPLICABLE"
DEFER_EXISTING = "DEFER_EXISTING"
DOMINANCE_UNPROVEN = "DOMINANCE_UNPROVEN"
PRESERVE_FRONTIER = "PRESERVE_FRONTIER"
ELIMINATE_DOMINATED = "ELIMINATE_DOMINATED"

Interval = tuple[float, float]


@dataclass(frozen=True)
class Option:
    name: str
    outcomes: dict[str, Interval]


@dataclass(frozen=True)
class ParetoCase:
    case_id: str
    expected: str
    options: tuple[Option, ...]
    comparison_objective: bool = True
    existing_blocker: bool = False
    guard_failures: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class ParetoDecision:
    result: str
    frontier: frozenset[str]
    dominated: frozenset[str]


def _safely_dominates(candidate: Option, other: Option) -> bool:
    """Return strict interval dominance on the same protected dimensions."""
    if candidate.outcomes.keys() != other.outcomes.keys():
        return False

    weakly_better_everywhere = all(
        candidate.outcomes[dimension][0] >= other.outcomes[dimension][1]
        for dimension in candidate.outcomes
    )
    strictly_better_somewhere = any(
        candidate.outcomes[dimension][0] > other.outcomes[dimension][1]
        for dimension in candidate.outcomes
    )
    return weakly_better_everywhere and strictly_better_somewhere


def _comparison_basis_is_valid(options: tuple[Option, ...]) -> bool:
    dimensions = options[0].outcomes.keys()
    if not dimensions:
        return False
    if any(option.outcomes.keys() != dimensions for option in options[1:]):
        return False
    return all(
        lower <= upper
        for option in options
        for lower, upper in option.outcomes.values()
    )


def evaluate(case: ParetoCase) -> ParetoDecision:
    names = frozenset(option.name for option in case.options)
    if not case.comparison_objective or len(case.options) < 2:
        return ParetoDecision(NOT_APPLICABLE, names, frozenset())
    if case.existing_blocker:
        return ParetoDecision(DEFER_EXISTING, names, frozenset())
    if case.guard_failures:
        return ParetoDecision(DOMINANCE_UNPROVEN, names, frozenset())
    if not _comparison_basis_is_valid(case.options):
        return ParetoDecision(DOMINANCE_UNPROVEN, names, frozenset())

    dominated = {
        other.name
        for candidate in case.options
        for other in case.options
        if candidate is not other and _safely_dominates(candidate, other)
    }
    frontier = names - dominated
    result = ELIMINATE_DOMINATED if dominated else PRESERVE_FRONTIER
    return ParetoDecision(result, frozenset(frontier), frozenset(dominated))


def _option(name: str, **outcomes: float | Interval) -> Option:
    normalized = {
        dimension: value if isinstance(value, tuple) else (value, value)
        for dimension, value in outcomes.items()
    }
    return Option(name, normalized)


SCENARIOS = (
    ParetoCase(
        "PF01",
        ELIMINATE_DOMINATED,
        (
            _option("A", cost=8, speed=8, safety=9),
            _option("B", cost=6, speed=7, safety=9),
        ),
    ),
    ParetoCase(
        "PF02",
        ELIMINATE_DOMINATED,
        (
            _option("A", reliability=9, implementation_effort=8, protected=8),
            _option("B", reliability=7, implementation_effort=6, protected=8),
        ),
    ),
    ParetoCase(
        "PF03",
        DEFER_EXISTING,
        (_option("A", value=9), _option("B", value=5)),
        existing_blocker=True,
    ),
    ParetoCase(
        "PF04",
        DEFER_EXISTING,
        (_option("safe", value=7), _option("unsafe", value=9)),
        existing_blocker=True,
    ),
    ParetoCase("PF05", NOT_APPLICABLE, (_option("typo-fix", value=1),)),
    ParetoCase(
        "PF06",
        PRESERVE_FRONTIER,
        (
            _option("A", cost=9, majority=9, minority=4),
            _option("B", cost=7, majority=7, minority=8),
        ),
    ),
    ParetoCase(
        "PF07",
        PRESERVE_FRONTIER,
        (
            _option("A", common_case=9, long_tail=3),
            _option("B", common_case=7, long_tail=9),
        ),
    ),
    ParetoCase(
        "PF08",
        DOMINANCE_UNPROVEN,
        (_option("A", value=9), _option("B", value=6)),
        guard_failures=("stale evidence",),
    ),
    ParetoCase(
        "PF09",
        DOMINANCE_UNPROVEN,
        (_option("A", outcome=9), _option("B", outcome=6)),
        guard_failures=("causal claim supported only by correlation",),
    ),
    ParetoCase(
        "PF10",
        DOMINANCE_UNPROVEN,
        (_option("A", weighted_total=9), _option("B", weighted_total=6)),
        guard_failures=("legitimate stakeholder weights differ",),
    ),
    ParetoCase(
        "PF11",
        DOMINANCE_UNPROVEN,
        (_option("A", average=9), _option("B", average=6)),
        guard_failures=("grouping hides a subgroup outcome",),
    ),
    ParetoCase(
        "PF12",
        DOMINANCE_UNPROVEN,
        (_option("A", projected_value=9), _option("B", projected_value=6)),
        guard_failures=("tractability is not modeled",),
    ),
    ParetoCase(
        "PF13",
        DOMINANCE_UNPROVEN,
        (
            _option("A", value=(7, 10)),
            _option("B", value=(6, 9)),
        ),
        guard_failures=("material uncertainty overlaps",),
    ),
    ParetoCase(
        "PF14",
        PRESERVE_FRONTIER,
        (
            _option("A", current_value=9, reversibility_and_option_value=2),
            _option("B", current_value=7, reversibility_and_option_value=9),
        ),
    ),
    ParetoCase(
        "PF15",
        DOMINANCE_UNPROVEN,
        (_option("A", short_term=9), _option("B", short_term=6)),
        guard_failures=("consequence horizons differ",),
    ),
    ParetoCase(
        "PF16",
        PRESERVE_FRONTIER,
        (_option("A", value=8, safety=8), _option("B", value=8, safety=8)),
    ),
)


class ParetoFrontierContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.skeptic = SKEPTIC.read_text(encoding="utf-8")
        cls.governance = GOVERNANCE.read_text(encoding="utf-8")

    def test_runtime_contains_complete_pareto_decision_contract(self) -> None:
        sh_start = self.skeptic.index("### Saffi (SH)")
        sh_end = self.skeptic.index("## 4. Structural Checks")
        section = self.skeptic[sh_start:sh_end]
        for marker in [
            "SH:PF",
            NOT_APPLICABLE,
            DEFER_EXISTING,
            DOMINANCE_UNPROVEN,
            PRESERVE_FRONTIER,
            ELIMINATE_DOMINATED,
            "lower credible bound",
            "upper credible bound",
            "every protected dimension",
            "strictly better",
            "Weighted totals, averages, or grouped outcomes",
            "minority or subgroup",
            "long-tail value",
            "reversibility or information value",
            "strategic option value",
            "tractability",
            "correlation alone",
            "Report the dominating option",
        ]:
            self.assertIn(marker, section)

    def test_runtime_tag_legend_and_governance_bind_the_capability(self) -> None:
        self.assertIn("SH:PF Pareto frontier / proven dominance", self.skeptic)
        for marker in [
            "Pareto frontier / dominance changes",
            "tests/test_pareto_frontier.py",
            "false-dominance traps",
            "minority, long-tail, uncertainty, and option value",
            "16/16",
            "0 false eliminations",
        ]:
            self.assertIn(marker, self.governance)

    def test_all_frozen_scenarios_match_the_oracle(self) -> None:
        self.assertEqual(len(SCENARIOS), 16)
        observed = {case.case_id: evaluate(case).result for case in SCENARIOS}
        expected = {case.case_id: case.expected for case in SCENARIOS}
        self.assertEqual(observed, expected)

    def test_true_dominance_is_eliminated_and_frontier_is_reported(self) -> None:
        for case_id in ("PF01", "PF02"):
            case = next(case for case in SCENARIOS if case.case_id == case_id)
            decision = evaluate(case)
            self.assertEqual(decision.result, ELIMINATE_DOMINATED)
            self.assertEqual(decision.frontier, frozenset({"A"}))
            self.assertEqual(decision.dominated, frozenset({"B"}))

    def test_existing_and_ordinary_controls_remain_silent(self) -> None:
        expected = {
            "PF03": DEFER_EXISTING,
            "PF04": DEFER_EXISTING,
            "PF05": NOT_APPLICABLE,
        }
        observed = {
            case.case_id: evaluate(case).result
            for case in SCENARIOS
            if case.case_id in expected
        }
        self.assertEqual(observed, expected)

    def test_false_dominance_traps_have_zero_eliminations(self) -> None:
        protected_cases = [
            case for case in SCENARIOS if 6 <= int(case.case_id[2:]) <= 16
        ]
        decisions = {case.case_id: evaluate(case) for case in protected_cases}
        eliminated = {
            case_id: decision
            for case_id, decision in decisions.items()
            if decision.result == ELIMINATE_DOMINATED
        }
        self.assertEqual(eliminated, {})

    def test_weighted_or_aggregated_win_cannot_hide_a_protected_loss(self) -> None:
        candidate = _option("A", weighted_total=100, protected_minority=2)
        other = _option("B", weighted_total=70, protected_minority=8)
        self.assertFalse(_safely_dominates(candidate, other))

    def test_overlapping_intervals_do_not_prove_dominance(self) -> None:
        candidate = _option("A", value=(7, 10))
        other = _option("B", value=(6, 9))
        self.assertFalse(_safely_dominates(candidate, other))

    def test_equal_options_are_not_pareto_dominated(self) -> None:
        case = next(case for case in SCENARIOS if case.case_id == "PF16")
        decision = evaluate(case)
        self.assertEqual(decision.result, PRESERVE_FRONTIER)
        self.assertEqual(decision.dominated, frozenset())

    def test_incomplete_comparison_basis_fails_closed(self) -> None:
        cases = {
            "mismatched dimensions": ParetoCase(
                "probe-mismatch",
                DOMINANCE_UNPROVEN,
                (
                    _option("A", value=9, protected_minority=7),
                    _option("B", value=6),
                ),
            ),
            "empty dimensions": ParetoCase(
                "probe-empty",
                DOMINANCE_UNPROVEN,
                (Option("A", {}), Option("B", {})),
            ),
            "invalid interval": ParetoCase(
                "probe-interval",
                DOMINANCE_UNPROVEN,
                (_option("A", value=(10, 7)), _option("B", value=(5, 6))),
            ),
        }
        for label, case in cases.items():
            with self.subTest(label=label):
                self.assertEqual(evaluate(case).result, DOMINANCE_UNPROVEN)

    def test_three_option_frontier_keeps_only_non_dominated_options(self) -> None:
        case = ParetoCase(
            "probe-frontier",
            ELIMINATE_DOMINATED,
            (
                _option("A", value=9, protected=8),
                _option("B", value=6, protected=7),
                _option("C", value=7, protected=10),
            ),
        )
        decision = evaluate(case)
        self.assertEqual(decision.result, ELIMINATE_DOMINATED)
        self.assertEqual(decision.frontier, frozenset({"A", "C"}))
        self.assertEqual(decision.dominated, frozenset({"B"}))


if __name__ == "__main__":
    unittest.main()

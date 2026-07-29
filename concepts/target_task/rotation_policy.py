"""Context-pressure policy and rotation trigger for pre-exhaustion checkpoints."""

from typing import Tuple, Optional


def evaluate_context_reserve(
    current_token_usage: int,
    context_budget: int,
    minimum_reserve_percent: float = 20.0,
) -> Tuple[bool, int]:
    """Evaluate whether current context reserve is adequate.

    Args:
        current_token_usage: estimated tokens used so far
        context_budget: total context budget (e.g., 200,000)
        minimum_reserve_percent: minimum reserve percentage to maintain (default 20%)

    Returns:
        (is_adequate: bool, reserve_remaining_percent: int)
    """
    if current_token_usage > context_budget:
        return False, 0

    reserve_tokens = context_budget - current_token_usage
    reserve_percent = (reserve_tokens / context_budget) * 100

    is_adequate = reserve_percent >= minimum_reserve_percent

    return is_adequate, int(reserve_percent)


def should_rotate(
    context_used: int,
    context_budget: int,
    phase: str,
    minimum_reserve_percent: float = 20.0,
) -> Tuple[bool, Optional[str]]:
    """Determine if current phase should trigger rotation.

    Rotation is triggered if:
    1. Context reserve drops below minimum threshold, OR
    2. Material pressure is detected (reserve very low for safe operations)

    Args:
        context_used: estimated tokens consumed
        context_budget: total budget
        phase: name of current phase (for logging)
        minimum_reserve_percent: minimum safe reserve

    Returns:
        (should_rotate: bool, reason: str or None)
    """
    is_adequate, reserve_percent = evaluate_context_reserve(
        context_used, context_budget, minimum_reserve_percent
    )

    if not is_adequate:
        reason = (
            f"Context reserve {reserve_percent}% below {minimum_reserve_percent}% threshold in {phase}; "
            f"rotating to fresh Lead session"
        )
        return True, reason

    # Also check if we're in a high-pressure zone (above 75% usage)
    usage_percent = (context_used / context_budget) * 100
    if usage_percent > 75:
        reason = (
            f"Context usage at {usage_percent:.0f}% in {phase}; "
            f"material pressure detected; consider rotation soon"
        )
        return True, reason  # Still trigger rotation as precautionary measure

    return False, None


def estimate_completion_reserve_needed(
    remaining_phases: int,
    avg_tokens_per_phase: int = 5000,
    final_validation_tokens: int = 10000,
) -> int:
    """Estimate tokens needed to safely complete remaining work.

    Args:
        remaining_phases: number of phases left to implement
        avg_tokens_per_phase: estimated tokens per phase (default 5000)
        final_validation_tokens: tokens needed for final tests/review (default 10000)

    Returns:
        estimated tokens needed
    """
    phase_tokens = remaining_phases * avg_tokens_per_phase
    return phase_tokens + final_validation_tokens


def can_safely_continue(
    context_used: int,
    context_budget: int,
    remaining_phases: int,
    safety_margin_percent: float = 10.0,
) -> Tuple[bool, Optional[str]]:
    """Determine if we can safely continue without rotation.

    Adds a safety margin to completion estimate.

    Args:
        context_used: tokens consumed so far
        context_budget: total budget
        remaining_phases: number of implementation phases left
        safety_margin_percent: extra buffer (default 10%)

    Returns:
        (can_continue: bool, reason: str or None)
    """
    estimate_needed = estimate_completion_reserve_needed(remaining_phases)
    reserve_available = context_budget - context_used

    # Apply safety margin
    estimate_with_margin = estimate_needed * (1 + (safety_margin_percent / 100))

    if reserve_available < estimate_with_margin:
        reason = (
            f"Insufficient reserve: have {reserve_available}, need {estimate_with_margin:.0f} "
            f"({estimate_needed} + {safety_margin_percent}% margin) for {remaining_phases} phases"
        )
        return False, reason

    return True, None

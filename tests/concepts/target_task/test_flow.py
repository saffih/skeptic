import unittest

from concepts.target_task.contracts import LunaAction, Phase
from concepts.target_task.flow import IllegalTransitionError, allowed_actions, next_phase


class LegalPathTests(unittest.TestCase):
    def test_full_happy_path_reaches_closed(self) -> None:
        path = [
            (Phase.MISSION_PERSISTED, LunaAction.CONTINUE),
            (Phase.PLAN_DRAFTED, LunaAction.CONTINUE),
            (Phase.PLAN_REVIEW, LunaAction.ADVANCE),
            (Phase.PLAN_SEALED, LunaAction.ADVANCE),
            (Phase.STEP_EXECUTING, LunaAction.ADVANCE),
            (Phase.STEP_VALIDATED, LunaAction.ADVANCE),
            (Phase.CANDIDATE_FROZEN, LunaAction.ADVANCE),
            (Phase.FINAL_REVIEW, LunaAction.ADVANCE),
            (Phase.INTEGRATED, LunaAction.ADVANCE),
        ]
        current = Phase.MISSION_PERSISTED
        for expected_current, action in path:
            self.assertEqual(current, expected_current)
            current = next_phase(current, action).phase
        self.assertEqual(current, Phase.CLOSED)

    def test_plan_review_continue_stays_in_plan_review(self) -> None:
        result = next_phase(Phase.PLAN_REVIEW, LunaAction.CONTINUE)
        self.assertEqual(result.phase, Phase.PLAN_REVIEW)

    def test_plan_review_retry_returns_to_plan_drafted(self) -> None:
        result = next_phase(Phase.PLAN_REVIEW, LunaAction.RETRY)
        self.assertEqual(result.phase, Phase.PLAN_DRAFTED)

    def test_step_executing_retry_and_recover_stay_in_step_executing(self) -> None:
        for action in (LunaAction.RETRY, LunaAction.RECOVER, LunaAction.CONTINUE):
            self.assertEqual(next_phase(Phase.STEP_EXECUTING, action).phase, Phase.STEP_EXECUTING)


class SealedPlanInvariantTests(unittest.TestCase):
    def test_no_transition_from_sealed_back_to_drafted(self) -> None:
        for action in (LunaAction.RETRY, LunaAction.CONTINUE):
            with self.assertRaises(IllegalTransitionError):
                next_phase(Phase.PLAN_SEALED, action)

    def test_only_advance_is_legal_from_sealed(self) -> None:
        self.assertEqual(next_phase(Phase.PLAN_SEALED, LunaAction.ADVANCE).phase, Phase.STEP_EXECUTING)


class StopAndRecoverTests(unittest.TestCase):
    def test_stop_from_any_non_closed_phase_goes_to_blocked(self) -> None:
        for phase in Phase:
            if phase in (Phase.CLOSED, Phase.BLOCKED):
                continue
            self.assertEqual(next_phase(phase, LunaAction.STOP).phase, Phase.BLOCKED)

    def test_stop_from_closed_is_illegal(self) -> None:
        with self.assertRaises(IllegalTransitionError):
            next_phase(Phase.CLOSED, LunaAction.STOP)

    def test_recover_without_resume_phase_is_illegal(self) -> None:
        with self.assertRaises(IllegalTransitionError):
            next_phase(Phase.BLOCKED, LunaAction.RECOVER)

    def test_recover_with_resume_phase_returns_there(self) -> None:
        result = next_phase(Phase.BLOCKED, LunaAction.RECOVER, resume_phase=Phase.STEP_EXECUTING)
        self.assertEqual(result.phase, Phase.STEP_EXECUTING)

    def test_non_recover_action_from_blocked_is_illegal(self) -> None:
        with self.assertRaises(IllegalTransitionError):
            next_phase(Phase.BLOCKED, LunaAction.ADVANCE)

    def test_recover_cannot_bypass_the_lifecycle_straight_to_closed(self) -> None:
        # CLOSED is reachable only via INTEGRATED + ADVANCE; recovering
        # straight to it would let RECOVER skip deterministic validation,
        # the frozen-candidate Find Loop, and integration in one step.
        with self.assertRaises(IllegalTransitionError):
            next_phase(Phase.BLOCKED, LunaAction.RECOVER, resume_phase=Phase.CLOSED)

    def test_recover_cannot_resume_into_blocked_itself(self) -> None:
        with self.assertRaises(IllegalTransitionError):
            next_phase(Phase.BLOCKED, LunaAction.RECOVER, resume_phase=Phase.BLOCKED)

    def test_recover_can_resume_a_legitimate_intermediate_phase(self) -> None:
        result = next_phase(Phase.BLOCKED, LunaAction.RECOVER, resume_phase=Phase.PLAN_REVIEW)
        self.assertEqual(result.phase, Phase.PLAN_REVIEW)


class IllegalTransitionTests(unittest.TestCase):
    def test_advance_too_far_is_illegal(self) -> None:
        with self.assertRaises(IllegalTransitionError):
            next_phase(Phase.MISSION_PERSISTED, LunaAction.ADVANCE)

    def test_closed_has_no_legal_action(self) -> None:
        with self.assertRaises(IllegalTransitionError):
            next_phase(Phase.CLOSED, LunaAction.CONTINUE)


class AllowedActionsTests(unittest.TestCase):
    def test_every_non_closed_phase_offers_stop(self) -> None:
        for phase in Phase:
            if phase in (Phase.CLOSED, Phase.BLOCKED):
                continue
            self.assertIn(LunaAction.STOP, allowed_actions(phase))

    def test_closed_offers_no_actions(self) -> None:
        self.assertEqual(allowed_actions(Phase.CLOSED), ())

    def test_blocked_offers_only_recover_and_stop(self) -> None:
        self.assertEqual(set(allowed_actions(Phase.BLOCKED)), {LunaAction.RECOVER, LunaAction.STOP})


if __name__ == "__main__":
    unittest.main()

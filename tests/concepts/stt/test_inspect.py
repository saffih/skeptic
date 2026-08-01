import unittest

from .test_recursive_tasks import RecursiveTaskTests


class InspectionPlanLifecycleTests(unittest.TestCase):
    def test_inspection_plan_is_sandbox_independent(self):
        RecursiveTaskTests("test_task_whose_plan_performs_inspection_is_closed_without_checkpoint").test_task_whose_plan_performs_inspection_is_closed_without_checkpoint()

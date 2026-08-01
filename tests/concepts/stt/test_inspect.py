import unittest

from .test_recursive_tasks import RecursiveTaskTests


class InspectLifecycleTests(unittest.TestCase):
    def test_inspect_child_lifecycle_is_sandbox_independent(self):
        RecursiveTaskTests("test_inspect_child_is_closed_and_preserves_parent_checkpoint").test_inspect_child_is_closed_and_preserves_parent_checkpoint()

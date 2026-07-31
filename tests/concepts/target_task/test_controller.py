import unittest

from concepts.target_task.controller import ControllerError, compact_receipt


class CompactControllerReceiptTests(unittest.TestCase):
    def test_reference_only_receipt_is_allowed(self):
        value = compact_receipt({"task_id": "t", "request_ref": "requests/a.json", "next_action": "CONTINUE"})
        self.assertEqual(value["task_id"], "t")

    def test_body_bearing_and_oversized_receipts_are_rejected(self):
        for field in ("body", "content", "text", "transcript", "patch", "log"):
            with self.subTest(field=field), self.assertRaises(ControllerError):
                compact_receipt({field: "leak"})
        with self.assertRaises(ControllerError):
            compact_receipt({"summary": "x" * 2000})


if __name__ == "__main__":
    unittest.main()

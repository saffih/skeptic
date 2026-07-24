from __future__ import annotations

import unittest

from harness.governance_checks import check_agent_envelope, check_skeptic_receipt

VALID_ENVELOPE = """BEGIN_AGENT_RETURN
dispatch_id: AG-1
status: COMPLETE
output: patch-inline
validation: PASS
blocker: NONE
END_AGENT_RETURN
"""

VALID_RECEIPT = """## RunSkeptic report
Final task output category: HANDLED

### RunSkeptic Receipt
- **Source read:** skeptic.md SHA 63602be10e0e532ce512aaac0ea6a4d3cd67ce09
- **Companion files read:** agents/task-prompt.md
- **Permission mode:** read-only
- **DONE:** review completed
- **Prompt review / feasibility:** Task Prompt / feasible
- **Major steps run:** GATE -> FUNDAMENTAL SCAN -> MAP -> CONFIDENCE -> STABILIZE -> EVIDENCE -> DECIDE -> ACT skipped -> VERIFY -> LEARN
- **Thinkers considered:** CH, OM, FE, PO, KT, SH
- **Evidence used:** supplied artifact
- **Decision path:** PASS
- **Verification performed:** promotion check
- **Unresolved conflicts / unknowns:** none
- **Final output category:** HANDLED
"""


class AgentEnvelopeTests(unittest.TestCase):
    def test_valid(self):
        self.assertEqual(check_agent_envelope(VALID_ENVELOPE, "AG-1", True)["result"], "AGENT_ENVELOPE_VALID")

    def test_missing(self):
        self.assertEqual(check_agent_envelope("none", "AG-1")["result"], "AGENT_RETURN_MISSING")

    def test_duplicate(self):
        self.assertEqual(check_agent_envelope(VALID_ENVELOPE * 2, "AG-1")["result"], "AGENT_RETURN_DUPLICATE")

    def test_wrong_dispatch(self):
        self.assertEqual(check_agent_envelope(VALID_ENVELOPE, "AG-2")["result"], "AGENT_ENVELOPE_INVALID")

    def test_truncated(self):
        self.assertEqual(check_agent_envelope(VALID_ENVELOPE.replace("END_AGENT_RETURN", ""), "AG-1")["result"], "AGENT_ENVELOPE_INVALID")

    def test_complete_with_blocker(self):
        text = VALID_ENVELOPE.replace("blocker: NONE", "blocker: missing input")
        self.assertEqual(check_agent_envelope(text, "AG-1")["result"], "AGENT_ENVELOPE_INVALID")

    def test_complete_with_failed_validation(self):
        text = VALID_ENVELOPE.replace("validation: PASS", "validation: FAIL")
        self.assertEqual(check_agent_envelope(text, "AG-1")["result"], "AGENT_ENVELOPE_INVALID")


class ReceiptTests(unittest.TestCase):
    def test_valid(self):
        result = check_skeptic_receipt(VALID_RECEIPT, "skeptic.md", "63602be10e0e532ce512aaac0ea6a4d3cd67ce09", True)
        self.assertEqual(result["result"], "SKEPTIC_RECEIPT_VALID")

    def test_missing_receipt(self):
        self.assertEqual(check_skeptic_receipt("Decision: PASS")["result"], "SKEPTIC_SUBSTANTIVE_RERUN_REQUIRED")

    def test_missing_thinker(self):
        text = VALID_RECEIPT.replace("CH, OM, FE, PO, KT, SH", "CH, OM, FE, PO, KT")
        self.assertEqual(check_skeptic_receipt(text)["result"], "SKEPTIC_SUBSTANTIVE_RERUN_REQUIRED")

    def test_unavailable_source(self):
        text = VALID_RECEIPT.replace("skeptic.md SHA 63602be10e0e532ce512aaac0ea6a4d3cd67ce09", "unavailable")
        self.assertEqual(check_skeptic_receipt(text)["result"], "SKEPTIC_RECEIPT_CONFLICT")

    def test_body_receipt_conflict(self):
        text = VALID_RECEIPT.replace("- **Final output category:** HANDLED", "- **Final output category:** CONFLICT")
        self.assertEqual(check_skeptic_receipt(text)["result"], "SKEPTIC_RECEIPT_CONFLICT")


if __name__ == "__main__":
    unittest.main()

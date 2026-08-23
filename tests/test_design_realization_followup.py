# made by AI
from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKEPTIC = (ROOT / "skeptic.md").read_text(encoding="utf-8")


class DesignRealizationFollowupTests(unittest.TestCase):
    def test_claim_driven_verification_has_no_fixed_premortem_quota(self) -> None:
        line = next(line for line in SKEPTIC.splitlines() if line.startswith("- pre-mortem:"))
        self.assertNotIn("3 concrete failure modes", line)
        self.assertIn("materially plausible failure modes", line)
        self.assertIn("when risk warrants it", line)


if __name__ == "__main__":
    unittest.main()

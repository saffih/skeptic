# made by AI
"""Verify every repository file path referenced by AGENTS.md exists."""
from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AGENTS = ROOT / "AGENTS.md"


class AgentsPathIntegrityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = AGENTS.read_text(encoding="utf-8")
        backtick_strings = re.findall(r"`([^`]+)`", cls.text)
        cls.paths = sorted(
            {
                s
                for s in backtick_strings
                if "/" in s or s.endswith(".md")
            }
        )

    def test_referenced_paths_are_nonempty(self) -> None:
        self.assertGreater(
            len(self.paths),
            0,
            "AGENTS.md must reference at least one repository file path",
        )

    def test_every_referenced_path_exists(self) -> None:
        for path_str in self.paths:
            with self.subTest(path=path_str):
                full = ROOT / path_str
                self.assertTrue(
                    full.exists(),
                    f"AGENTS.md references `{path_str}` but {full} does not exist",
                )


if __name__ == "__main__":
    unittest.main()

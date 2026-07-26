from __future__ import annotations

import re
import unittest
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
QUESTIONS = ROOT / "skeptic-questions.md"
DOMAIN_CODES = {"SEC", "CPX", "REL", "DAT", "ARC", "CFT"}


class SkepticQuestionConsistencyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = QUESTIONS.read_text(encoding="utf-8")

    def test_question_ids_are_contiguous_and_summary_counts_match(self) -> None:
        question_ids: dict[str, list[int]] = {code: [] for code in DOMAIN_CODES}
        for code, number in re.findall(
            r"^(SEC|CPX|REL|DAT|ARC|CFT)(\d+)\.", self.text, re.MULTILINE
        ):
            question_ids[code].append(int(number))

        for code, numbers in question_ids.items():
            self.assertTrue(numbers, f"{code} has no questions")
            self.assertEqual(numbers, list(range(1, len(numbers) + 1)))

        summary = {
            code: int(count)
            for code, count in re.findall(
                r"^- (SEC|CPX|REL|DAT|ARC|CFT): (\d+) questions$",
                self.text,
                re.MULTILINE,
            )
        }
        self.assertEqual(set(summary), DOMAIN_CODES)
        self.assertEqual(
            summary,
            {code: len(numbers) for code, numbers in question_ids.items()},
        )

    def test_parallelization_groups_partition_domains_without_subset_counts(self) -> None:
        section = self.text.split("## Parallelization", 1)[1].split("---", 1)[0]
        pairs = re.findall(r"^- ([A-Z]{3})\+([A-Z]{3}):", section, re.MULTILINE)

        self.assertEqual(len(pairs), 3)
        members = [code for pair in pairs for code in pair]
        self.assertEqual(set(members), DOMAIN_CODES)
        self.assertEqual(Counter(members), Counter({code: 1 for code in DOMAIN_CODES}))
        self.assertNotRegex(section, r"\d+\s*\+\s*\d+\s*=\s*\d+")


if __name__ == "__main__":
    unittest.main()

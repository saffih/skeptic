from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from concepts.stt.canonical import canonical_json_bytes, loads_strict, safe_relpath
from concepts.stt.errors import STTError


class CanonicalTests(unittest.TestCase):
    def test_canonical_json(self) -> None:
        self.assertEqual(canonical_json_bytes({"b": 1, "a": "é"}), b'{"a":"\xc3\xa9","b":1}\n')

    def test_duplicate_key_rejected(self) -> None:
        with self.assertRaises(STTError):
            loads_strict('{"a":1,"a":2}')
        with self.assertRaises(STTError):
            loads_strict('{"a":NaN}')

    def test_recursive_and_non_utf8_canonical_values_are_bounded_errors(self) -> None:
        recursive: list[object] = []
        recursive.append(recursive)
        with self.assertRaises(STTError) as caught:
            canonical_json_bytes(recursive)
        self.assertEqual(caught.exception.code, "NON_CANONICAL_JSON")
        with self.assertRaises(STTError) as caught:
            canonical_json_bytes({"value": "\ud800"})
        self.assertEqual(caught.exception.code, "NON_CANONICAL_JSON")

    def test_path_guards(self) -> None:
        self.assertEqual(safe_relpath("a/b"), "a/b")
        for path in ("../a", "/a", "a/../b", ".git/config", "nested/.git/config", "nested/.stt/private"):
            with self.subTest(path=path), self.assertRaises(STTError):
                safe_relpath(path)

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

from concepts.stt.boundary import scope_contains, validate_path_collisions, validate_tree
from concepts.stt.errors import STTError


class BoundaryTests(unittest.TestCase):
    def test_scope(self):
        scope = [{"path": "src", "kind": "tree"}, {"path": "README.md", "kind": "file"}]
        self.assertTrue(scope_contains(scope, "src/a.py"))
        self.assertFalse(scope_contains(scope, "tests/a.py"))

    def test_path_alias_collision_rejected(self):
        with self.assertRaises(STTError):
            validate_path_collisions(["A.txt", "a.txt"], ignore_case=True)
        with self.assertRaises(STTError):
            validate_path_collisions(["caf\u00e9.txt", "cafe\u0301.txt"])

    def test_external_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); os.symlink("../../etc/passwd", root / "bad")
            with self.assertRaises(STTError): validate_tree(root)

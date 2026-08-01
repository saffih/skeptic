from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

from concepts.stt.capsule import apply_delta
from concepts.stt.errors import STTError


class CapsuleDeltaTests(unittest.TestCase):
    def test_existing_symlink_parent_rejects_entire_delta_before_write(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            workspace = root / "workspace"; workspace.mkdir()
            capsule = root / "capsule"; capsule.mkdir()
            outside = root / "outside"; outside.mkdir()
            (workspace / "safe.txt").write_text("before\n")
            (capsule / "safe.txt").write_text("after\n")
            (capsule / "link").mkdir(); (capsule / "link/file.txt").write_text("escape\n")
            (workspace / "link").symlink_to(outside, target_is_directory=True)
            delta = [
                {"path": "safe.txt", "op": "file", "mode": 0o644},
                {"path": "link/file.txt", "op": "file", "mode": 0o644},
            ]
            scope = [{"path": "safe.txt", "kind": "file"}, {"path": "link", "kind": "tree"}]

            with self.assertRaises(STTError) as caught:
                apply_delta(workspace, capsule, delta, scope)

            self.assertEqual(caught.exception.code, "WORKSPACE_SYMLINK_PARENT")
            self.assertEqual((workspace / "safe.txt").read_text(), "before\n")
            self.assertFalse((outside / "file.txt").exists())

    def test_relative_escaping_symlink_delta_is_rejected_before_mutation(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            workspace = root / "workspace"; workspace.mkdir()
            capsule = root / "capsule"; capsule.mkdir()
            (workspace / "safe.txt").write_text("before\n")
            (capsule / "safe.txt").write_text("after\n")
            (capsule / "escape").symlink_to("../../outside")
            delta = [
                {"path": "safe.txt", "op": "file", "mode": 0o644},
                {"path": "escape", "op": "symlink", "target": "../../outside"},
            ]
            scope = [{"path": "safe.txt", "kind": "file"}, {"path": "escape", "kind": "file"}]

            with self.assertRaises(STTError) as caught:
                apply_delta(workspace, capsule, delta, scope)

            self.assertEqual(caught.exception.code, "UNSUPPORTED_SYMLINK_DELTA")
            self.assertEqual((workspace / "safe.txt").read_text(), "before\n")
            self.assertFalse((workspace / "escape").exists())

    def test_all_worker_symlink_deltas_are_unsupported(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            workspace = root / "workspace"; workspace.mkdir()
            capsule = root / "capsule"; capsule.mkdir()
            (capsule / "link").symlink_to("ordinary-target")

            with self.assertRaises(STTError) as caught:
                apply_delta(
                    workspace,
                    capsule,
                    [{"path": "link", "op": "symlink", "target": "ordinary-target"}],
                    [{"path": "link", "kind": "file"}],
                )

            self.assertEqual(caught.exception.code, "UNSUPPORTED_SYMLINK_DELTA")
            self.assertFalse((workspace / "link").exists())

    def test_nonempty_directory_delete_fails_and_preserves_unexpected_child(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            workspace = root / "workspace"; workspace.mkdir()
            capsule = root / "capsule"; capsule.mkdir()
            directory = workspace / "tree"; directory.mkdir()
            (directory / "declared.txt").write_text("declared\n")
            (directory / "unexpected.txt").write_text("unexpected\n")
            delta = [
                {"path": "tree", "op": "delete"},
                {"path": "tree/declared.txt", "op": "delete"},
            ]

            with self.assertRaises(STTError) as caught:
                apply_delta(workspace, capsule, delta, [{"path": "tree", "kind": "tree"}])

            self.assertEqual(caught.exception.code, "NONEMPTY_DIRECTORY_OPERATION")
            self.assertTrue(directory.is_dir())
            self.assertFalse((directory / "declared.txt").exists())
            self.assertEqual((directory / "unexpected.txt").read_text(), "unexpected\n")

    def test_scoped_file_create_replace_and_delete_still_work(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            workspace = root / "workspace"; workspace.mkdir()
            capsule = root / "capsule"; capsule.mkdir()
            (workspace / "replace.txt").write_text("before\n")
            (workspace / "delete.txt").write_text("delete\n")
            (capsule / "replace.txt").write_text("after\n")
            (capsule / "create.txt").write_text("created\n")
            delta = [
                {"path": "delete.txt", "op": "delete"},
                {"path": "replace.txt", "op": "file", "mode": 0o640},
                {"path": "create.txt", "op": "file", "mode": 0o644},
            ]
            scope = [{"path": name, "kind": "file"} for name in ("delete.txt", "replace.txt", "create.txt")]

            apply_delta(workspace, capsule, delta, scope)

            self.assertFalse((workspace / "delete.txt").exists())
            self.assertEqual((workspace / "replace.txt").read_text(), "after\n")
            self.assertEqual((workspace / "create.txt").read_text(), "created\n")
            self.assertEqual(os.stat(workspace / "replace.txt").st_mode & 0o777, 0o640)

    def test_symlink_leaf_can_only_be_deleted(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            workspace = root / "workspace"; workspace.mkdir()
            capsule = root / "capsule"; capsule.mkdir()
            target = root / "outside.txt"; target.write_text("outside\n")
            (workspace / "link").symlink_to(target)
            (capsule / "link").write_text("replacement\n")
            scope = [{"path": "link", "kind": "file"}]

            with self.assertRaises(STTError) as caught:
                apply_delta(workspace, capsule, [{"path": "link", "op": "file", "mode": 0o644}], scope)
            self.assertEqual(caught.exception.code, "WORKSPACE_SYMLINK_LEAF")
            self.assertEqual(target.read_text(), "outside\n")

            apply_delta(workspace, capsule, [{"path": "link", "op": "delete"}], scope)
            self.assertFalse((workspace / "link").exists())
            self.assertEqual(target.read_text(), "outside\n")


if __name__ == "__main__":
    unittest.main()

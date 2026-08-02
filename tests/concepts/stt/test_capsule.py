from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

from concepts.stt.capsule import apply_delta, derive_delta, materialize_capsule, object_identity, prepare_capsule_admission
from concepts.stt.contracts import DEFAULT_LIMITS
from concepts.stt.errors import STTError


MAX_FILE = DEFAULT_LIMITS["max_single_file_bytes"]


def identity(root: Path, rel: str) -> dict:
    return object_identity(root / rel, rel, max_single_file_bytes=MAX_FILE)


class CapsuleDeltaTests(unittest.TestCase):
    def test_scoped_file_create_replace_and_delete_are_atomic_per_file(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); workspace = root / "workspace"; capsule = root / "capsule"
            workspace.mkdir(); capsule.mkdir()
            (workspace / "replace.txt").write_text("before\n"); (workspace / "delete.txt").write_text("delete\n")
            before_replace = identity(workspace, "replace.txt"); before_delete = identity(workspace, "delete.txt")
            (capsule / "replace.txt").write_text("after\n"); os.chmod(capsule / "replace.txt", 0o640)
            (capsule / "create.txt").write_text("created\n")
            delta = [
                {"path": "delete.txt", "op": "delete", "before": before_delete, "after": {"path": "delete.txt", "state": "missing"}},
                {"path": "replace.txt", "op": "file", "before": before_replace, "after": identity(capsule, "replace.txt")},
                {"path": "create.txt", "op": "file", "before": {"path": "create.txt", "state": "missing"}, "after": identity(capsule, "create.txt")},
            ]
            scope = [{"path": name, "kind": "file"} for name in ("delete.txt", "replace.txt", "create.txt")]

            apply_delta(workspace, capsule, delta, scope, max_single_file_bytes=MAX_FILE)

            self.assertFalse((workspace / "delete.txt").exists())
            self.assertEqual((workspace / "replace.txt").read_text(), "after\n")
            self.assertEqual((workspace / "create.txt").read_text(), "created\n")
            self.assertEqual(os.stat(workspace / "replace.txt").st_mode & 0o777, 0o640)
            self.assertFalse(any(path.name.startswith(".replace.txt.stt-") for path in workspace.iterdir()))

    def test_symlink_parent_rejects_entire_delta_before_first_write(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); workspace = root / "workspace"; capsule = root / "capsule"; outside = root / "outside"
            workspace.mkdir(); capsule.mkdir(); outside.mkdir()
            (workspace / "safe.txt").write_text("before\n"); before = identity(workspace, "safe.txt")
            (capsule / "safe.txt").write_text("after\n"); (capsule / "link").mkdir(); (capsule / "link/file.txt").write_text("escape\n")
            (workspace / "link").symlink_to(outside, target_is_directory=True)
            delta = [
                {"path": "safe.txt", "op": "file", "before": before, "after": identity(capsule, "safe.txt")},
                {"path": "link/file.txt", "op": "file", "before": {"path": "link/file.txt", "state": "missing"}, "after": identity(capsule, "link/file.txt")},
            ]
            with self.assertRaises(STTError) as caught:
                apply_delta(workspace, capsule, delta, [{"path": "safe.txt", "kind": "file"}, {"path": "link", "kind": "tree"}], max_single_file_bytes=MAX_FILE)
            self.assertEqual(caught.exception.code, "WORKSPACE_SYMLINK_PARENT")
            self.assertEqual((workspace / "safe.txt").read_text(), "before\n")
            self.assertFalse((outside / "file.txt").exists())

    def test_changed_workspace_precondition_rejects_before_first_write(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); workspace = root / "workspace"; capsule = root / "capsule"
            workspace.mkdir(); capsule.mkdir()
            (workspace / "one").write_text("old-one"); (workspace / "two").write_text("old-two")
            before_one = identity(workspace, "one"); before_two = identity(workspace, "two")
            (capsule / "one").write_text("new-one"); (capsule / "two").write_text("new-two")
            delta = [
                {"path": "one", "op": "file", "before": before_one, "after": identity(capsule, "one")},
                {"path": "two", "op": "file", "before": before_two, "after": identity(capsule, "two")},
            ]
            (workspace / "two").write_text("external-change")
            with self.assertRaises(STTError) as caught:
                apply_delta(workspace, capsule, delta, [{"path": "one", "kind": "file"}, {"path": "two", "kind": "file"}], max_single_file_bytes=MAX_FILE)
            self.assertEqual(caught.exception.code, "WORKSPACE_PRECONDITION_CHANGED")
            self.assertEqual((workspace / "one").read_text(), "old-one")

    def test_worker_created_symlink_is_rejected_before_mutation(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); workspace = root / "workspace"; capsule = root / "capsule"
            workspace.mkdir(); capsule.mkdir(); (capsule / "link").symlink_to("target")
            delta = [{"path": "link", "op": "file", "before": {"path": "link", "state": "missing"}, "after": {"path": "link", "state": "symlink", "target": "target", "size": 6, "mode": 0o777}}]
            with self.assertRaises(STTError) as caught:
                apply_delta(workspace, capsule, delta, [{"path": "link", "kind": "file"}], max_single_file_bytes=MAX_FILE)
            self.assertEqual(caught.exception.code, "UNSUPPORTED_SYMLINK_DELTA")
            self.assertFalse((workspace / "link").exists())

    def test_leaf_first_directory_delete_reports_later_partial_failure(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); workspace = root / "workspace"; capsule = root / "capsule"
            workspace.mkdir(); capsule.mkdir(); tree = workspace / "tree"; tree.mkdir()
            (tree / "declared.txt").write_text("declared\n"); (tree / "unexpected.txt").write_text("unexpected\n")
            delta = [
                {"path": "tree", "op": "delete", "before": identity(workspace, "tree"), "after": {"path": "tree", "state": "missing"}},
                {"path": "tree/declared.txt", "op": "delete", "before": identity(workspace, "tree/declared.txt"), "after": {"path": "tree/declared.txt", "state": "missing"}},
            ]
            with self.assertRaises(STTError) as caught:
                apply_delta(workspace, capsule, delta, [{"path": "tree", "kind": "tree"}], max_single_file_bytes=MAX_FILE)
            self.assertEqual(caught.exception.code, "NONEMPTY_DIRECTORY_OPERATION")
            self.assertFalse((tree / "declared.txt").exists())
            self.assertEqual((tree / "unexpected.txt").read_text(), "unexpected\n")

    def test_successful_directory_delete_fsyncs_its_parent(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); workspace = root / "workspace"; capsule = root / "capsule"
            workspace.mkdir(); capsule.mkdir(); tree = workspace / "tree"; tree.mkdir()
            delta = [{"path": "tree", "op": "delete", "before": identity(workspace, "tree"), "after": {"path": "tree", "state": "missing"}}]
            from unittest.mock import patch
            with patch("concepts.stt.capsule.fsync_dir") as fsync:
                apply_delta(workspace, capsule, delta, [{"path": "tree", "kind": "tree"}], max_single_file_bytes=MAX_FILE)
            self.assertFalse(tree.exists())
            fsync.assert_called_once_with(workspace)

    def test_delta_is_derived_from_frozen_admission_not_live_workspace(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); workspace = root / "workspace"; capsule = root / "capsule"
            workspace.mkdir(); (workspace / "value.txt").write_text("before\n")
            scope = [{"path": "value.txt", "kind": "file"}]
            manifest = prepare_capsule_admission(workspace, scope, scope, nested_roots=(), limits=DEFAULT_LIMITS)
            materialize_capsule(workspace, capsule, manifest, scope)
            os.chmod(capsule / "value.txt", 0o644); (capsule / "value.txt").write_text("worker\n")
            (workspace / "value.txt").write_text("external\n")
            delta = derive_delta(manifest, capsule, scope, DEFAULT_LIMITS)
            self.assertEqual(delta[0]["before"]["sha256"], manifest["write_baseline"][0]["sha256"])
            with self.assertRaises(STTError) as caught:
                apply_delta(workspace, capsule, delta, scope, max_single_file_bytes=MAX_FILE)
            self.assertEqual(caught.exception.code, "WORKSPACE_PRECONDITION_CHANGED")

    def test_capsule_entry_and_byte_limits_are_preflighted(self):
        with tempfile.TemporaryDirectory() as td:
            workspace = Path(td) / "workspace"; workspace.mkdir(); (workspace / "a").write_bytes(b"1234")
            scope = [{"path": "a", "kind": "file"}]
            limits = {**DEFAULT_LIMITS, "max_capsule_bytes_per_step": 3}
            with self.assertRaises(STTError) as caught:
                prepare_capsule_admission(workspace, scope, scope, nested_roots=(), limits=limits)
            self.assertEqual(caught.exception.code, "CAPSULE_BYTE_LIMIT")
            limits = {**DEFAULT_LIMITS, "max_capsule_entries_per_step": 0}
            with self.assertRaises(STTError) as caught:
                prepare_capsule_admission(workspace, scope, scope, nested_roots=(), limits=limits)
            self.assertEqual(caught.exception.code, "CAPSULE_ENTRY_LIMIT")

    def test_workspace_case_alias_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            workspace = Path(td) / "workspace"; workspace.mkdir(); (workspace / "Value.txt").write_text("x")
            scope = [{"path": "value.txt", "kind": "file"}]
            with self.assertRaises(STTError) as caught:
                prepare_capsule_admission(workspace, scope, scope, nested_roots=(), limits=DEFAULT_LIMITS)
            self.assertEqual(caught.exception.code, "PATH_ALIAS_COLLISION")


if __name__ == "__main__":
    unittest.main()

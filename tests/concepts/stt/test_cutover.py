from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

from concepts.stt.canonical import atomic_write, canonical_json_bytes
from concepts.stt.cutover import apply_manifest, build_manifest


class CutoverTests(unittest.TestCase):
    def test_file_directory_transition_and_idempotent_recovery(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); before = root / "before"; after = root / "after"; source = root / "source"
            before.mkdir(); after.mkdir(); source.mkdir()
            (before / "x").write_text("old")
            (source / "x").write_text("old")
            (after / "x").mkdir(); (after / "x" / "y").write_text("new")
            manifest = build_manifest(before, after)
            journal = root / "journal.json"; backup = root / "backup"
            apply_manifest(source_repo=source, final_candidate=after, manifest=manifest, journal=journal, backup_root=backup)
            self.assertEqual((source / "x" / "y").read_text(), "new")
            apply_manifest(source_repo=source, final_candidate=after, manifest=manifest, journal=journal, backup_root=backup)
            self.assertEqual((source / "x" / "y").read_text(), "new")

    def test_recovers_after_backup_and_removal_before_install(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); before = root / "before"; after = root / "after"; source = root / "source"
            before.mkdir(); after.mkdir(); source.mkdir()
            (before / "x").write_text("old")
            (source / "x").write_text("old")
            (after / "x").write_text("new")
            manifest = build_manifest(before, after)
            backup = root / "backup"; backup.mkdir(); shutil.copy2(source / "x", backup / "x")
            (source / "x").unlink()
            journal = root / "journal.json"
            atomic_write(journal, canonical_json_bytes({"schema_version": 1, "completed": []}), create_only=True)
            apply_manifest(source_repo=source, final_candidate=after, manifest=manifest, journal=journal, backup_root=backup)
            self.assertEqual((source / "x").read_text(), "new")

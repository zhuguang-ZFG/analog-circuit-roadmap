#!/usr/bin/env python3
"""schema-2 manifest 必须覆盖每一页 docs，并给出 77 个逻辑页。"""
import sys
import tempfile
import unittest
from pathlib import Path

BOOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BOOK))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from book.manifest import (BookError, book_pages, direct_files,  # noqa: E402
                           excluded_files, validate_manifest)
import book_fixtures  # noqa: E402


class ManifestTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.docs = self.root / "docs"
        self.manifest = book_fixtures.manifest()
        book_fixtures.write_docs(self.docs)

    def problems(self, manifest=None):
        try:
            validate_manifest(manifest or self.manifest, self.docs)
        except BookError as exc:
            return str(exc)
        return ""

    def test_accepts_complete_schema_2_manifest(self):
        validate_manifest(self.manifest, self.docs)
        self.assertEqual(54, len(direct_files(self.manifest)))
        self.assertEqual(10, len(excluded_files(self.manifest)))
        self.assertEqual(64, len(direct_files(self.manifest)) + len(excluded_files(self.manifest)))

    def test_book_pages_are_77_and_ordered(self):
        pages = book_pages(self.manifest)
        self.assertEqual(77, len(pages))
        self.assertEqual(
            ["half-title", "title-page", "copyright", "p0-01-preface",
             "p0-02-how-to-use", "p0-03-timeline", "p0-11-conventions",
             "p0-12-symbols", "toc", "list-of-figures", "list-of-tables"],
            [p["stem"] for p in pages[:11]])
        self.assertEqual("part-I", pages[11]["stem"])
        self.assertEqual(24, sum(1 for p in pages if p["kind"] in {"part", "chapter"}))
        self.assertEqual(36, sum(1 for p in pages if p["kind"].startswith("appendix")))
        self.assertEqual(["bibliography", "index", "p9-12-changelog",
                          "p9-13-thanks", "p9-14-credits", "colophon"],
                         [p["stem"] for p in pages[-6:]])
        self.assertEqual(77, len({p["stem"] for p in pages}))

    def test_rejects_legacy_schema(self):
        self.manifest["schema"] = 1
        self.assertIn("schema", self.problems())

    def test_rejects_missing_chapter(self):
        self.manifest["parts"][0]["units"][0]["chapters"].pop()
        self.assertIn("19", self.problems())

    def test_rejects_duplicate_chapter(self):
        self.manifest["parts"][0]["units"][0]["chapters"].append("p1-01-ch0.md")
        self.assertIn("重复", self.problems())

    def test_rejects_unknown_excluded_page(self):
        self.manifest["excluded_pages"][0]["file"] = "p1-01-ch0.md"
        self.assertIn("排除", self.problems())

    def test_rejects_excluded_without_reason(self):
        self.manifest["excluded_pages"][0]["reason"] = ""
        self.assertIn("reason", self.problems())

    def test_rejects_missing_new_page(self):
        self.manifest["front_matter"] = [
            e for e in self.manifest["front_matter"]
            if e.get("file") != "p0-11-conventions.md"]
        self.assertIn("p0-11", self.problems())

    def test_rejects_duplicate_direct_page(self):
        self.manifest["appendices"][1]["files"].append("p0-01-preface.md")
        self.assertIn("重复", self.problems())

    def test_rejects_manual_spine(self):
        self.manifest["cover"]["spine_mm"] = 20
        self.assertIn("spine_mm", self.problems())

    def test_rejects_negative_bleed(self):
        self.manifest["cover"]["bleed_mm"] = -1
        self.assertIn("bleed_mm", self.problems())

    def test_rejects_unknown_appendix_id(self):
        self.manifest["appendices"][-1]["id"] = "Z"
        self.assertIn("附录", self.problems())

    def test_rejects_wrong_appendix_file_count(self):
        self.manifest["appendices"][2]["files"].pop()
        self.assertIn("C", self.problems())

    def test_rejects_missing_back_matter_kind(self):
        self.manifest["back_matter"] = [
            e for e in self.manifest["back_matter"] if e.get("kind") != "index"]
        self.assertIn("index", self.problems())

if __name__ == "__main__":
    unittest.main()

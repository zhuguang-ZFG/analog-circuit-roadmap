#!/usr/bin/env python3
"""构建报告与 PRINT-SPEC：只读事实、书脊算术、草稿门与稳定版。"""
import json
import sys
import tempfile
import unittest
from pathlib import Path

BOOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BOOK))

from book import config, report  # noqa: E402
from book.manifest import BookError  # noqa: E402

MANIFEST = {
    "title": "通往模拟电路之路",
    "edition": "第一版",
    "version": "2.0.0-draft.1",
    "source_version": "3.61",
    "date": "2026-10-25",
    "trim": {"width_mm": 185, "height_mm": 260},
    "parts": [{"id": str(i), "units": [{"chapters": [f"c{i}"]}]}
              for i in range(5)],
    "cover": {"bleed_mm": 3, "paper_caliper_mm": 0.10,
              "spine_allowance_mm": 1.0},
    "release": {"edition_status": "draft"},
}
MODEL = {
    "pages": [{"id": f"p{i}"} for i in range(77)],
    "stats": {"figures": 12, "tables": 8, "formulas": 900, "images": 200},
    "endnotes": 123,
    "audit": {"errors": [], "warnings": ["draft word count"]},
}
PDF = {"pages": 652, "body_start": 13, "bookmarks": 143,
       "problems": [], "warnings": []}
COVER = {"pages": 652, "size_mm": [409.6, 266.0],
         "spine_mm": 33.6, "problems": []}


class ReportTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.out = Path(self.tmp.name)
        files = {
            config.OUTPUT_NAME: b"<!doctype html><title>book</title>",
            config.PDF_NAME: b"%PDF-1.7\n" + b"0" * 2048,
            config.COVER_PDF_NAME: b"%PDF-1.7\n" + b"1" * 1024,
            config.COVER_PREVIEW_NAME: b"\x89PNG\r\n\x1a\n" + b"2" * 512,
        }
        for name, payload in files.items():
            (self.out / name).write_bytes(payload)

    def write(self, manifest=MANIFEST, pdf=PDF, cover=COVER):
        return report.write_report(
            self.out, MODEL, manifest, pdf, cover,
            sample_report={"fallback": "mirrored"})

    def test_json_report_records_actual_facts(self):
        data = self.write()
        self.assertEqual(77, data["logical_pages"])
        self.assertEqual(5, data["parts"])
        self.assertEqual(652, data["pdf_pages"])
        self.assertEqual(13, data["body_start"])
        self.assertEqual(143, data["bookmarks"])
        self.assertEqual(20, data["figures"] + data["tables"])
        self.assertEqual("PDF 1.7", data["pdf_version"])
        self.assertEqual("mirrored", data["mirrored"])
        self.assertEqual(652, data["cover"]["pages"])
        self.assertEqual(33.6, data["cover"]["spine_mm"])
        self.assertEqual([409.6, 266.0], data["cover"]["size_mm"])
        saved = json.loads(
            (self.out / "build-report.json").read_text(encoding="utf-8"))
        self.assertEqual(data, saved)

    def test_print_spec_has_spine_math_and_no_fake_isbn(self):
        self.write()
        spec = (self.out / "PRINT-SPEC.md").read_text(encoding="utf-8")
        self.assertIn("652 / 2 × 0.10 + 1.0 = 33.60 mm", spec)
        self.assertIn("2 × 185 + 33.60 + 2 × 3 = 409.60 mm", spec)
        self.assertIn("185 × 260 mm", spec)
        self.assertIn("未申请 ISBN", spec)
        self.assertNotIn("978-", spec)
        self.assertIn("草稿", spec)
        for heading in ("开本与版心", "页数、书脊与封面", "字体与许可",
                        "打样与校对页", "尚未关闭的质量门"):
            self.assertIn(heading, spec)

    def test_problems_block_report(self):
        broken = dict(COVER, problems=["spine mismatch"])
        with self.assertRaisesRegex(BookError, "封面结构问题"):
            self.write(cover=broken)

    def test_final_has_no_deferred_gates(self):
        final = {**MANIFEST, "release": {"edition_status": "final"}}
        data = self.write(manifest=final)
        self.assertEqual([], data["deferred"])
        spec = (self.out / "PRINT-SPEC.md").read_text(encoding="utf-8")
        self.assertIn("无（本版为稳定版）", spec)

    def test_style_guide_is_executable(self):
        text = (config.BOOK_DIR / "STYLE.md").read_text(encoding="utf-8")
        for heading in ("三层读法", "证据等级", "仿真与实测", "交稿检查"):
            self.assertIn(heading, text)


if __name__ == "__main__":
    unittest.main()

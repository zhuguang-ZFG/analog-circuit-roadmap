#!/usr/bin/env python3
"""封面：书脊公式、尺寸、出血、裁切线、二维码与无假 ISBN。"""
import sys
import tempfile
import unittest
from pathlib import Path

BOOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BOOK))

from book import config  # noqa: E402
from book.cover import (build_cover, cover_html, cover_size_mm,  # noqa: E402
                        inspect_cover, qr_svg, spine_mm)

try:
    import fitz
except ImportError:  # pragma: no cover
    fitz = None

try:
    from playwright.sync_api import sync_playwright
except ImportError:  # pragma: no cover
    sync_playwright = None

MANIFEST = {
    "title": "通往模拟电路之路",
    "subtitle": "从欧姆定律到芯片内部结构",
    "edition": "第一版", "version": "2.0.0-draft.1", "date": "2026-10-25",
    "author": "zhuguang-ZFG 与贡献者", "license": "CC BY-SA 4.0",
    "site_url": "https://example.test/analog/",
    "repository": "https://github.com/example/analog",
    "trim": {"width_mm": 185, "height_mm": 260},
    "cover": {
        "bleed_mm": 3, "crop_marks": True, "paper_caliper_mm": 0.10,
        "spine_allowance_mm": 1.0, "isbn_area": False,
        "back_cover": {
            "blurb": "把直觉、推导、仿真、实测与排故连起来。",
            "audience": "电子、自动化、通信与嵌入式方向的学生和工程师。",
            "highlights": ["19 章完整知识链", "三层读法", "可复现仿真",
                           "实测实验", "故障速查与索引"],
        },
    },
    "release": {"edition_status": "draft"},
}


class SpineTests(unittest.TestCase):
    def test_spine_formula_uses_final_page_count(self):
        self.assertEqual(31.0, spine_mm(600, MANIFEST))
        self.assertEqual(33.5, spine_mm(650, MANIFEST))
        self.assertEqual(26.0, spine_mm(500, MANIFEST))

    def test_cover_size_includes_two_trim_panels_and_bleed(self):
        width, height = cover_size_mm(650, MANIFEST)
        self.assertAlmostEqual(409.5, width, places=2)
        self.assertAlmostEqual(266.0, height, places=2)

    def test_cover_size_rejects_zero_pages(self):
        with self.assertRaises(ValueError):
            cover_size_mm(0, MANIFEST)


class CoverHtmlTests(unittest.TestCase):
    def setUp(self):
        self.html = cover_html(MANIFEST, 650)

    def test_three_panels_and_title(self):
        for value in ('class="cover-panel cover-back"',
                      'class="cover-panel cover-spine"',
                      'class="cover-panel cover-front"',
                      "通往模拟电路之路", "从欧姆定律到芯片内部结构",
                      "zhuguang-ZFG 与贡献者", "第一版"):
            self.assertIn(value, self.html)

    def test_has_eight_crop_marks_and_bleed(self):
        self.assertEqual(8, self.html.count('<line class="crop-mark"'))
        self.assertIn("3mm", (config.COVER_DIR / "cover.css").read_text(
            encoding="utf-8").replace("__BLEED__", "3"))

    def test_spine_is_vertical_and_can_be_thin(self):
        css = (config.COVER_DIR / "cover.css").read_text(encoding="utf-8")
        self.assertIn("writing-mode: vertical-rl", css)
        thin = cover_html(MANIFEST, 80)
        self.assertIn('class="cover-panel cover-spine is-thin"', thin)
        self.assertNotIn('class="spine-text"', thin)

    def test_back_cover_has_blurb_highlights_qr_and_blank_isbn(self):
        for text in ("把直觉、推导、仿真、实测与排故连起来。",
                     "电子、自动化、通信与嵌入式方向", "19 章完整知识链",
                     "故障速查与索引", "ISBN / 条码预留区（留空）",
                     'data-qr="site"', 'data-qr="repo"'):
            self.assertIn(text, self.html)
        self.assertNotRegex(self.html, r"ISBN[^<]{0,16}\d{10,13}")
        self.assertNotIn("978-", self.html)

    def test_qr_is_inline_vector_and_no_remote_assets(self):
        svg = qr_svg(MANIFEST["site_url"])
        self.assertTrue(svg.startswith("<svg"))
        self.assertIn("path", svg)
        self.assertNotIn("<image", svg)
        self.assertNotIn('<img src="http', self.html)
        self.assertNotIn("<iframe", self.html)

    def test_cover_art_is_inlined(self):
        self.assertIn("cover-dots", self.html)
        self.assertIn("<svg", self.html)


@unittest.skipIf(fitz is None or sync_playwright is None,
                 "需要 PyMuPDF 与 Playwright")
class CoverBuildTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.tmp.cleanup)
        cls.out = Path(cls.tmp.name) / "dist"
        cls.html_path, cls.pdf_path, cls.png_path = build_cover(
            cls.out, 650, MANIFEST)

    def test_pdf_size_and_single_page(self):
        report = inspect_cover(self.pdf_path, 650, MANIFEST)
        self.assertEqual([], report["problems"])
        self.assertEqual(1, report["pages"])
        width, height = report["size_mm"]
        self.assertAlmostEqual(409.5, width, delta=0.5)
        self.assertAlmostEqual(266.0, height, delta=0.5)

    def test_preview_is_150dpi(self):
        doc = fitz.open(self.pdf_path)
        try:
            pix = doc[0].get_pixmap(dpi=150)
            expected_width = round(409.5 / 25.4 * 150)
            self.assertAlmostEqual(expected_width, pix.width, delta=3)
            self.assertTrue(self.png_path.is_file())
            self.assertGreater(self.png_path.stat().st_size, 50_000)
        finally:
            doc.close()

    def test_text_survives_printing(self):
        doc = fitz.open(self.pdf_path)
        try:
            text = doc[0].get_text()
        finally:
            doc.close()
        for value in ("通往模拟电路之路", "从欧姆定律到芯片内部结构",
                      "zhuguang-ZFG 与贡献者", "ISBN / 条码预留区"):
            self.assertIn(value, text)

    def test_build_refuses_wrong_page_count(self):
        with self.assertRaises(ValueError):
            build_cover(self.out / "bad", 0, MANIFEST)


if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3
"""16K 样张必须证明版心、镜像边距回退与九类版式都不溢出。"""
import sys
import unittest
from pathlib import Path

BOOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BOOK))
from book import config  # noqa: E402
from book.sample import SAMPLE_SECTIONS, build_sample, inspect_sample  # noqa: E402

try:
    import fitz
except ImportError:  # pragma: no cover
    fitz = None

try:
    from playwright.sync_api import sync_playwright
except ImportError:  # pragma: no cover
    sync_playwright = None


@unittest.skipIf(fitz is None or sync_playwright is None,
                 "需要 PyMuPDF 与 Playwright")
class SampleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html, cls.pdf, cls.report = build_sample(config.DIST_DIR / "sample")

    def test_page_is_16k(self):
        doc = fitz.open(self.pdf)
        try:
            for page in doc:
                width = page.rect.width * 25.4 / 72
                height = page.rect.height * 25.4 / 72
                self.assertAlmostEqual(185, width, delta=0.5)
                self.assertAlmostEqual(260, height, delta=0.5)
        finally:
            doc.close()

    def test_nine_sections_are_present(self):
        self.assertEqual(9, len(SAMPLE_SECTIONS))
        doc = fitz.open(self.pdf)
        try:
            text = "\n".join(page.get_text() for page in doc)
        finally:
            doc.close()
        for title in SAMPLE_SECTIONS:
            self.assertIn(title, text)

    def test_text_stays_inside_145mm_text_block(self):
        report = inspect_sample(self.pdf)
        self.assertLessEqual(report["text_width_mm"], 145.5)
        self.assertGreaterEqual(report["text_width_mm"], 130)
        self.assertEqual(9, len(report["sections"]))
        self.assertIn(report["fallback"], {"mirrored", "uniform-20mm"})
        self.assertTrue((self.html.parent / "sample-report.json").is_file())

    def test_print_css_has_16k_and_typography_contract(self):
        css = (config.STYLES_DIR / "print.css").read_text(encoding="utf-8")
        self.assertIn("size: 185mm 260mm", css)
        self.assertIn("font-size: 10.5pt", css)
        self.assertIn("line-height: 17.5pt", css)
        self.assertIn("font-size: 28pt", css)
        self.assertIn(".book .half-title", css)
        self.assertIn("font-size: 8.5pt", css)
        self.assertIn("column-count: 2", css)
        self.assertIn("break-inside: avoid", css)
        self.assertIn("thead", css)
        self.assertIn("@page :left", css)
        self.assertIn("@page :right", css)


if __name__ == "__main__":
    unittest.main()

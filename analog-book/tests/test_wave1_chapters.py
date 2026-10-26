#!/usr/bin/env python3
"""Wave 1 逐章合同：字数、节结构、图表、算例、仿真与练习。"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

BOOK = Path(__file__).resolve().parent.parent
ROOT = BOOK.parent
sys.path.insert(0, str(BOOK))


class VisualContractTests(unittest.TestCase):
    def test_print_css_has_chapter_stage_and_figure_frames(self):
        css = (BOOK / "styles" / "print.css").read_text(encoding="utf-8")
        for selector in (
            ".book .chapter-hero",
            ".book .chapter-hero-num",
            ".book .md-typeset figure",
            ".book .md-typeset figcaption",
        ):
            self.assertIn(selector, css)
        self.assertIn("break-inside: avoid", css)


if __name__ == "__main__":
    unittest.main()

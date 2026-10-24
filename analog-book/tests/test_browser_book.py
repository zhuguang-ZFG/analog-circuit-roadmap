#!/usr/bin/env python3
"""Playwright 冒烟：离线整书能断网排版公式、渲染计算器并跳转。"""
import sys
import unittest
from pathlib import Path

BOOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BOOK))

import build_book  # noqa: E402

try:
    from playwright.sync_api import sync_playwright
except ImportError:  # pragma: no cover
    sync_playwright = None


def launch_chromium(playwright):
    try:
        return playwright.chromium.launch(headless=True)
    except Exception:
        # 部分机器只装了系统 Chrome，没有 Playwright 自带的 Chromium。
        return playwright.chromium.launch(headless=True, channel="chrome")


@unittest.skipIf(sync_playwright is None, "Playwright 未安装")
class BrowserBook(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        out = BOOK / "dist"
        cls.html = out / build_book.OUTPUT_NAME
        if not cls.html.is_file():
            cls.html = build_book.build_html(out, rebuild_site=False)

    def test_offline_formulas_calculators_and_toc(self):
        with sync_playwright() as p:
            browser = launch_chromium(p)
            page = browser.new_page(reduced_motion="reduce")
            errors = []
            page.on("console", lambda msg: errors.append(msg.text)
                    if msg.type == "error" else None)
            page.goto(self.html.resolve().as_uri(), wait_until="load")
            page.wait_for_function(
                "window.MathJax && MathJax.startup && MathJax.startup.promise",
                timeout=60000)
            page.wait_for_function(
                "document.querySelectorAll('mjx-container').length > 1000",
                timeout=120000)
            self.assertGreater(
                page.evaluate("document.querySelectorAll('mjx-container').length"), 1000)
            self.assertGreater(
                page.evaluate("document.querySelectorAll('[data-calc-ready]').length"), 0)
            page.click('a[href="#page-p1-01-ch0"]')
            page.wait_for_function(
                "document.getElementById('page-p1-01-ch0').getBoundingClientRect().top < 300")
            self.assertEqual([], errors[:5])
            browser.close()


if __name__ == "__main__":
    unittest.main()

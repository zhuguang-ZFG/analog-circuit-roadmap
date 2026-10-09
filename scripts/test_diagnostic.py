"""Regression tests for the 入场诊断 widget (p0-09) on the built site.

Rebuilds in a temp workspace and serves it, mirroring test_reading_journey.py:
the widget must map answer paths to the right route, deep-link to real pages,
and the no-JS fallback table must stay readable.
"""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import threading
import unittest

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *_):
        pass


class DiagnosticTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        temporary = tempfile.TemporaryDirectory(prefix='analog-diag-')
        cls.addClassCleanup(temporary.cleanup)
        work = Path(temporary.name)
        for folder in ('docs', 'assets', 'scripts'):
            shutil.copytree(ROOT / folder, work / folder,
                            ignore=shutil.ignore_patterns('__pycache__', '_probe*'))
        for filename in ('CONTRIBUTING.md', 'CONTRIBUTORS.md', 'LICENSE'):
            shutil.copyfile(ROOT / filename, work / filename)
        result = subprocess.run([sys.executable, '-X', 'utf8', 'scripts/build_site.py', '--build'],
                                cwd=work, capture_output=True, text=True, encoding='utf8',
                                errors='replace', timeout=300)
        if result.returncode:
            raise RuntimeError(result.stdout + result.stderr)
        server = ThreadingHTTPServer(('127.0.0.1', 0),
                                     partial(QuietHandler, directory=str(work / 'build')))
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()

        def stop_server():
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)
        cls.addClassCleanup(stop_server)
        cls.base = f'http://127.0.0.1:{server.server_port}/site/'
        playwright = sync_playwright().start()
        cls.addClassCleanup(playwright.stop)
        cls.browser = playwright.chromium.launch(channel='chrome', headless=True)

    def open_page(self, js=True):
        context = self.browser.new_context(java_script_enabled=js)
        self.addCleanup(context.close)
        page = context.new_page()
        page.on('pageerror', lambda error: self.fail(f'page error: {error}'))
        page.goto(self.base + 'p0-09-diagnostic.html')
        return page

    def answer_all(self, page, picks):
        for index, pick in enumerate(picks):
            expect_card = page.locator('.diag-card')
            self.assertTrue(expect_card.is_enabled(timeout=10000),
                            f'question {index + 1} missing')
            page.locator('.diag-opts .diag-btn').nth(pick).click()
            page.wait_for_timeout(50)

    def result_id(self, page):
        card = page.locator('.diag-result')
        card.wait_for(state='attached', timeout=10000)
        return card.get_attribute('data-diag-result')

    def test_working_engineer_gets_practice_route_with_live_links(self):
        page = self.open_page()
        self.answer_all(page, [3, 2, 2, 2, 3, 2])
        card = page.locator('.diag-result')
        card.wait_for(state='attached', timeout=10000)
        self.assertEqual(card.get_attribute('data-diag-result'), 'practice')
        first = card.locator('ol a').first
        self.assertIn('p3-01-ch14.html#ch14', first.get_attribute('href'))
        first.click()
        page.wait_for_timeout(300)
        self.assertIn('设计方法论', page.locator('h2').first.inner_text())

    def test_zero_basis_time_poor_defaults_to_intuition_route(self):
        page = self.open_page()
        self.answer_all(page, [0] * 6)
        self.assertEqual(self.result_id(page), 'intuition')

    def test_back_button_returns_to_previous_question(self):
        page = self.open_page()
        page.locator('.diag-opts .diag-btn').nth(1).click()
        page.wait_for_timeout(50)
        page.locator('.diag-opts .diag-btn').nth(2).click()
        page.wait_for_timeout(50)
        page.locator('.diag-back').click()
        page.wait_for_timeout(50)
        self.assertEqual(page.locator('.diag-progress').inner_text(), '第 2 / 6 题')

    def test_without_javascript_static_routing_table_remains(self):
        page = self.open_page(js=False)
        rows = page.locator('table tr')
        self.assertGreaterEqual(rows.count(), 5)
        body = page.inner_text('main')
        for route in ('直觉线', '硬件线', '实战线', '深造线'):
            self.assertIn(route, body)

    def test_time_budget_selects_matching_timeline_row(self):
        page = self.open_page()
        self.answer_all(page, [3, 2, 2, 2, 3, 2])  # 每周 6～8 小时 → 一周末档
        href = page.locator('.diag-time a').get_attribute('href')
        self.assertTrue(href.endswith('p0-03-timeline.html#t-week'), href)
        page.goto(self.base + 'p0-09-diagnostic.html')
        self.answer_all(page, [0] * 6)  # 每周不到 1 小时 → 5 分钟档
        href = page.locator('.diag-time a').get_attribute('href')
        self.assertTrue(href.endswith('p0-03-timeline.html#t-min'), href)
        page.goto(self.base + href.split('/')[-1])
        page.wait_for_timeout(300)
        row = page.evaluate("() => document.getElementById('t-min').closest('tr').innerText")
        self.assertIn('5 分钟', row)
        self.assertIn('水路比喻', row)


if __name__ == '__main__':
    unittest.main()

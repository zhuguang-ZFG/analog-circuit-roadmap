"""Exercise the built site, including search workers and instant navigation.

Uses a temporary build served under /site/ to catch project-site path mistakes.
All external requests are blocked; no deployed site or external player is needed.
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

from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[1]


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *_):
        pass

    def copyfile(self, source, outputfile):
        try:
            super().copyfile(source, outputfile)
        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
            pass  # Navigating away cancels in-flight images and search requests.


class ReadingJourneyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        temporary = tempfile.TemporaryDirectory(prefix='analog-reading-')
        cls.addClassCleanup(temporary.cleanup)
        work = Path(temporary.name)
        for folder in ('docs', 'assets', 'scripts'):
            shutil.copytree(ROOT / folder, work / folder,
                            ignore=shutil.ignore_patterns('__pycache__', '_probe*'))
        for filename in ('CONTRIBUTING.md', 'CONTRIBUTORS.md', 'LICENSE'):
            shutil.copyfile(ROOT / filename, work / filename)
        result = subprocess.run([sys.executable, '-X', 'utf8', 'scripts/build_site.py', '--build'],
                                cwd=work, capture_output=True, text=True, encoding='utf-8',
                                errors='replace', timeout=180)
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
        cls.addClassCleanup(cls.browser.close)

    def setUp(self):
        self.errors = []
        self.context = self.browser.new_context(viewport={'width': 1280, 'height': 900})
        self.addCleanup(self.context.close)
        self.context.route('**/*', lambda route: route.continue_()
                           if route.request.url.startswith(self.base) else route.abort())
        self.page = self.context.new_page()
        self.page.on('pageerror', lambda error: self.errors.append(str(error)))

    def tearDown(self):
        self.assertEqual([], self.errors)

    def test_homepage_start_takes_the_reader_to_chapter_zero(self):
        self.page.goto(self.base)
        expect(self.page.locator('.learning-path')).to_have_count(3)
        expect(self.page.locator('.learning-lesson')).to_have_count(3)
        start = self.page.get_by_role('link', name='从第 0 章开始 →', exact=True)
        expect(start).to_be_in_viewport()
        start.click()
        expect(self.page).to_have_url(self.base + 'p1-01-ch0.html#ch0')
        expect(self.page.locator('p:has(> #ch0) + h2')).to_contain_text('第 0 章')

    def test_chapter_quiz_review_and_next_chapter_form_a_round_trip(self):
        self.page.goto(self.base + 'p1-07-ch6.html#ch6')
        self.page.get_by_role('link', name='做第 6 章自测 →', exact=True).click()
        expect(self.page).to_have_url(self.base + 'p9-00-quiz.html#quiz-ch6')
        expect(self.page.locator('p:has(> #quiz-ch6) + h2')).to_contain_text('第 6 章')
        self.page.get_by_role('link', name='← 返回第 6 章复习', exact=True).click()
        expect(self.page).to_have_url(self.base + 'p1-07-ch6.html#ch6')
        expect(self.page.locator('.reading-nav')).to_have_count(1)
        self.page.locator('.reading-nav a').last.click()
        expect(self.page).to_have_url(self.base + 'p1-08-ch7.html#ch7')

    def test_page_titles_and_social_metadata_survive_pre_heading_anchors(self):
        for filename, title in (
            ('p1-00-part1.html', '第一篇：器件深度原理解析 🔬'),
            ('p9-00-quiz.html', '第九篇：自测与练习 🎯'),
            ('p1-08-ch7.html', '第 7 章 比较器：专为"判决"而生'),
        ):
            with self.subTest(page=filename):
                self.page.goto(self.base + filename)
                self.assertIn(title, self.page.title())
                expect(self.page.locator('meta[property="og:title"]')).to_have_attribute('content', title)
                expect(self.page.locator('meta[name="twitter:title"]')).to_have_attribute('content', title)

    def test_old_bookmarks_redirect_without_losing_queries_or_trapping_back(self):
        for source, target in (
            ('p1-01-ch0.html#ch1', 'p1-02-ch1.html#ch1'),
            ('p4-03-ch18.html#part5', 'p5-00-part5.html#part5'),
            ('p8-08-s8-8.html#sec89', 'p8-09-s8-9.html#sec89'),
            ('index.html#preface', 'p0-01-preface.html#preface'),
        ):
            with self.subTest(source=source):
                self.page.goto(self.base)
                self.page.goto(self.base + source.replace('#', '?from=bookmark#'))
                expect(self.page).to_have_url(self.base + target.replace('#', '?from=bookmark#'))
                self.page.go_back()
                expect(self.page).to_have_url(self.base)

    def test_reading_and_legacy_fallback_work_without_javascript(self):
        context = self.browser.new_context(java_script_enabled=False)
        self.addCleanup(context.close)
        context.route('**/*', lambda route: route.continue_()
                      if route.request.url.startswith(self.base) else route.abort())
        page = context.new_page()
        page.goto(self.base)
        page.get_by_role('link', name='从第 0 章开始 →', exact=True).click()
        expect(page).to_have_url(self.base + 'p1-01-ch0.html#ch0')
        page.get_by_role('link', name='做第 0 章自测 →', exact=True).click()
        expect(page).to_have_url(self.base + 'p9-00-quiz.html#quiz-ch0')
        page.goto(self.base + 'p1-01-ch0.html#ch1')
        fallback = page.locator('.legacy-anchor:target a')
        expect(fallback).to_be_visible()
        fallback.click()
        expect(page).to_have_url(self.base + 'p1-02-ch1.html#ch1')

    def test_home_and_chapter_navigation_fit_mobile_in_both_themes(self):
        for theme in ('light', 'dark'):
            context = self.browser.new_context(color_scheme=theme, reduced_motion='reduce')
            self.addCleanup(context.close)
            context.route('**/*', lambda route: route.continue_()
                          if route.request.url.startswith(self.base) else route.abort())
            page = context.new_page()
            page.on('pageerror', lambda error: self.errors.append(str(error)))
            for width in (360, 390, 1280):
                page.set_viewport_size({'width': width, 'height': 900})
                for path in ('', 'p1-02-ch1.html#ch1'):
                    with self.subTest(theme=theme, width=width, path=path):
                        page.goto(self.base + path)
                        expect(page.locator('body')).to_have_attribute('data-md-color-scheme',
                                                                      'slate' if theme == 'dark' else 'default')
                        self.assertFalse(page.evaluate('document.documentElement.scrollWidth > innerWidth'))
                        links = page.locator('.reading-nav a' if path else '.learning-actions a')
                        for link in links.all():
                            self.assertGreaterEqual(link.bounding_box()['height'], 44)
                        links.first.focus()
                        expect(links.first).to_be_focused()

    def test_real_search_returns_relevant_chinese_and_model_number_results(self):
        self.page.goto(self.base)
        search = self.page.locator('input[data-md-component="search-query"]')
        search.click()
        for query, expected_page in (
            ('去耦电容', 'p1-02-ch1.html'),
            ('相位裕度', 'p2-01-ch11.html'),
            ('LM358', 'p1-07-ch6.html'),
        ):
            with self.subTest(query=query):
                # Playwright inserts non-Latin text without keyup. Material's
                # query observer listens to keyup (not input), so finish the
                # input with a real, non-editing key rather than depending on
                # the worker-ready event happening after text insertion.
                search.fill(query)
                search.press('End')
                expect(search).to_have_value(query)
                result = self.page.locator('.md-search-result__link[href*="' + expected_page + '"]')
                expect(result.first).to_be_visible(timeout=15000)
        search.fill('zzzxqv987654')
        search.press('End')
        expect(self.page.locator('.md-search-result__meta')).to_contain_text('没有找到')


if __name__ == '__main__':
    unittest.main()

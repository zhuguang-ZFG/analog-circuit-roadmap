#!/usr/bin/env python3
"""书内语义转换：emoji、提示框、图表编号、尾注与计算器兜底。"""
import re
import sys
import unittest
from pathlib import Path

BOOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BOOK))

from book import transforms  # noqa: E402
from book.manifest import BookError  # noqa: E402


class EmojiAndCalloutTests(unittest.TestCase):
    def test_maps_check_marks_and_drops_decoration(self):
        text = transforms.strip_emoji(
            "<p>✅ 对，❌ 错，⚠️ 注意，🚀 直觉，α→β，R≤10kΩ</p>")
        self.assertIn("✓ 对", text)
        self.assertIn("✗ 错", text)
        self.assertIn("注意 注意", text)
        self.assertNotIn("🚀", text)
        self.assertIn("α→β", text)
        self.assertIn("R≤10kΩ", text)

    def test_command_key_becomes_ascii(self):
        self.assertEqual("<p>Cmd+P</p>", transforms.strip_emoji("<p>\u2318+P</p>"))

    def test_semantic_callout_gets_label_and_keeps_body(self):
        fragment = ('<div class="callout callout-goal"><p>🎯 <strong>学完你应能</strong>：'
                    '看懂分压。</p></div>')
        result = transforms.transform_callouts(transforms.strip_emoji(fragment))
        self.assertIn('<aside class="book-callout book-callout-goal"', result)
        self.assertIn('data-label="学习目标"', result)
        self.assertIn('<p class="callout-label">学习目标</p>', result)
        self.assertIn("看懂分压。", result)
        self.assertNotIn("学完你应能", result)

    def test_unknown_callout_becomes_plain_quote(self):
        fragment = '<div class="callout callout-mystery"><p>正文</p></div>'
        result = transforms.transform_callouts(fragment)
        self.assertIn('<blockquote class="book-quote">', result)
        self.assertNotIn("callout-mystery", result)


class DetailsTests(unittest.TestCase):
    def test_details_become_visible_blocks(self):
        fragment = ('<details open><summary>展开公式</summary>'
                    '<p>正文 <strong>加粗</strong>。</p></details>'
                    '<details><summary>自测</summary><p>答案。</p></details>')
        result = transforms.unwrap_details(fragment)
        self.assertNotIn("<details", result)
        self.assertNotIn("<summary", result)
        self.assertEqual(2, result.count('class="book-reveal"'))
        self.assertIn('class="book-reveal-title">展开公式<', result)
        self.assertIn('正文 <strong>加粗</strong>。', result)
        self.assertIn('class="book-reveal-title">自测<', result)


class FigureTests(unittest.TestCase):
    def test_numbers_captioned_figure_and_records_entry(self):
        fragment = ('<figure><img src="data:image/svg+xml;base64,AA" alt="波形">'
                    '<figcaption>共射输出削顶</figcaption></figure>')
        result, entries, warnings = transforms.number_figures(
            fragment, "3", "p1-04-ch3")
        self.assertIn('id="p1-04-ch3--fig-1"', result)
        self.assertIn("图 3-1　共射输出削顶", result)
        self.assertEqual([], warnings)
        self.assertEqual("图 3-1", entries[0]["number"])
        self.assertEqual("p1-04-ch3--fig-1", entries[0]["anchor"])

    def test_empty_caption_does_not_consume_number(self):
        fragment = ('<figure><img src="data:image/svg+xml;base64,AA" alt="a">'
                    '<figcaption> </figcaption></figure>'
                    '<figure><img src="data:image/svg+xml;base64,AA" alt="b">'
                    '<figcaption>真图注</figcaption></figure>')
        result, entries, warnings = transforms.number_figures(
            fragment, "3", "p1-04-ch3")
        self.assertEqual(["图 3-1"], [e["number"] for e in entries])
        self.assertIn("图 3-1　真图注", result)
        self.assertEqual(1, len(warnings))

    def test_caption_keeps_inline_markup(self):
        fragment = ('<figure><img src="data:image/svg+xml;base64,AA" alt="a">'
                    '<figcaption>共射 <code>R_C</code> 削顶</figcaption></figure>')
        result, entries, warnings = transforms.number_figures(
            fragment, "3", "p1-04-ch3")
        self.assertIn('<code>R_C</code>', result)
        self.assertIn("图 3-1　共射", result)
        self.assertEqual("图 3-1　共射 R_C 削顶", entries[0]["caption"])

    def test_uncaptioned_figure_warns_in_draft_and_fails_final(self):
        fragment = '<figure><img src="data:image/svg+xml;base64,AA" alt="波形"></figure>'
        _, entries, warnings = transforms.number_figures(
            fragment, "3", "p1-04-ch3")
        self.assertEqual([], entries)
        self.assertTrue(warnings)
        with self.assertRaisesRegex(BookError, "图注"):
            transforms.number_figures(fragment, "3", "p1-04-ch3", final=True)

    def test_table_caption_precedes_wrapped_table(self):
        fragment = ('<p><strong>表 2-1　二极管三种工作区</strong></p>'
                    '<table><tr><td>1</td></tr></table>')
        wrapped, entries, warnings = transforms.number_tables(
            fragment, "2", "p1-03-ch2")
        self.assertIn('class="table-wrap"', wrapped)
        self.assertIn("表 2-1", wrapped)
        self.assertEqual("表 2-1", entries[0]["number"])
        self.assertEqual([], warnings)

    def test_uncaptioned_table_warns(self):
        result, entries, warnings = transforms.number_tables(
            "<table><tr><td>1</td></tr></table>", "2", "p1-03-ch2")
        self.assertIn('<div class="table-wrap">', result)
        self.assertEqual([], entries)
        self.assertTrue(warnings)

    def test_number_tables_is_idempotent(self):
        fragment = ('<p><strong>表 2-1　二极管三种工作区</strong></p>'
                    '<table><tr><td>1</td></tr></table>')
        first, entries, warnings = transforms.number_tables(fragment, "2", "p1-03-ch2")
        second, entries2, warnings2 = transforms.number_tables(first, "2", "p1-03-ch2")
        self.assertEqual(first, second)
        self.assertEqual([], warnings)
        self.assertEqual([], warnings2)


class EndnoteTests(unittest.TestCase):
    def test_deduplicates_and_appends_notes(self):
        fragment = ('<p><a href="https://a.test/x">资料甲</a> 与 '
                    '<a href="https://a.test/x">资料甲</a> 与 '
                    '<a href="mailto:a@b.test">邮件</a>。</p>'
                    '<p><a href="#p1-01-ch0--s">站内</a></p>')
        result, notes = transforms.transform_endnotes(fragment, "p1-01-ch0")
        self.assertEqual(2, len(notes))
        self.assertIn('id="p1-01-ch0--note-ref-1"', result)
        self.assertIn('id="p1-01-ch0--note-ref-2"', result)
        self.assertNotIn('href="https://a.test/x"', result)
        self.assertIn('href="#p1-01-ch0--s"', result)
        self.assertIn("chapter-endnotes", result)

    def test_repeated_url_references_get_unique_ids(self):
        fragment = ('<a href="https://a.test/x">甲</a> 与 '
                    '<a href="https://a.test/x">甲</a>')
        result, notes = transforms.transform_endnotes(fragment, "p1-01-ch0")
        refs = re.findall(r'id="(p1-01-ch0--note-ref-[^"]+)"', result)
        self.assertEqual(["p1-01-ch0--note-ref-1", "p1-01-ch0--note-ref-1-2"], refs)
        self.assertEqual(1, len(notes))
        self.assertEqual(2, result.count('href="#p1-01-ch0--note-1"'))

    def test_note_ids_are_stable_and_unique(self):
        fragment = '<a href="https://a.test/1">1</a><a href="https://a.test/2">2</a>'
        result, notes = transforms.transform_endnotes(fragment, "p")
        ids = [note["id"] for note in notes]
        self.assertEqual(["p--note-1", "p--note-2"], ids)
        self.assertEqual(result, transforms.transform_endnotes(fragment, "p")[0])


class CalculatorTests(unittest.TestCase):
    def test_adjacent_example_is_accepted(self):
        fragment = ('<div class="calc" data-calc="divider"></div>'
                    '<p><strong>例 0-1</strong>：分压器带载。</p>')
        self.assertEqual([], transforms.check_calculator_fallbacks(
            fragment, "p1-01-ch0"))

    def test_preceding_example_is_accepted(self):
        fragment = ('<p><strong>例 0-1</strong>：分压器带载。</p>'
                    '<div class="calc" data-calc="divider"></div>')
        self.assertEqual([], transforms.check_calculator_fallbacks(
            fragment, "p1-01-ch0"))

    def test_missing_fallback_warns_then_fails(self):
        fragment = '<div class="calc" data-calc="opamp"></div><p>无关正文。</p>'
        warnings = transforms.check_calculator_fallbacks(fragment, "p1-07-ch6")
        self.assertEqual(1, len(warnings))
        with self.assertRaisesRegex(BookError, "计算器"):
            transforms.check_calculator_fallbacks(
                fragment, "p1-07-ch6", final=True)

    def test_chapter_and_appendix_labels(self):
        self.assertEqual("0", transforms.chapter_label("p1-01-ch0"))
        self.assertEqual("18", transforms.chapter_label("p4-03-ch18"))
        self.assertIsNone(transforms.chapter_label("p0-01-preface"))
        self.assertEqual("C", transforms.chapter_label("p6-01-s6-1", "C"))


class PrintStyleTests(unittest.TestCase):
    def test_print_css_styles_emitted_classes(self):
        css = (BOOK / "styles" / "print.css").read_text(encoding="utf-8")
        for selector in (".callout-label", ".table-caption", ".chapter-endnotes"):
            self.assertIn(selector, css)


if __name__ == "__main__":
    unittest.main()

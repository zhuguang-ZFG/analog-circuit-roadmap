#!/usr/bin/env python3
"""docs/ 内部链接完整性：跨页锚点必须真实存在（站点与 README 双形态都要能跳转）。"""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"

MD_LINK = re.compile(r"\]\(([\w\-]+\.md)#([^)/]+)\)")
HTML_HREF = re.compile(r'href="([\w\-]+\.md)#([^"]+)"')
ANCHOR_DEF = re.compile(r'<a\s+id="([^"]+)"')
IMG_REF = re.compile(r'<img src="assets/svg/([\w\-]+\.svg)"')


class DocsLinks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.anchors = {}
        cls.pages = sorted(DOCS.glob("*.md"))
        for p in cls.pages:
            text = p.read_text(encoding="utf-8")
            cls.anchors[p.name] = set(ANCHOR_DEF.findall(text))

    def test_cross_page_anchors_exist(self):
        broken = []
        for p in self.pages:
            text = p.read_text(encoding="utf-8")
            for target, anchor in MD_LINK.findall(text) + HTML_HREF.findall(text):
                if target not in self.anchors:
                    broken.append("%s -> 缺少页面 %s" % (p.name, target))
                elif anchor not in self.anchors[target]:
                    broken.append("%s -> %s 缺少锚点 #%s" % (p.name, target, anchor))
        self.assertEqual([], broken, "\n".join(broken[:10]))

    def test_svg_references_exist(self):
        have = {f.name for f in (ROOT / "assets" / "svg").glob("*.svg")}
        missing = set()
        for p in self.pages:
            for svg in IMG_REF.findall(p.read_text(encoding="utf-8")):
                if svg not in have:
                    missing.add("%s:%s" % (p.name, svg))
        self.assertEqual(set(), missing, "引用了不存在的 SVG：%s" % sorted(missing)[:5])

    def test_every_page_has_heading(self):
        for p in self.pages:
            text = p.read_text(encoding="utf-8")
            self.assertTrue(re.search(r"^#{1,2} ", text, re.M),
                            "%s 缺少标题（站点导航会退化成文件名）" % p.name)

    def test_chapter_and_part_anchors_belong_to_their_content(self):
        """A link existing on the previous page is still a broken learning route."""
        for page in self.pages:
            match = re.search(r'-(ch\d+|part\d+)\.md$', page.name)
            if match:
                with self.subTest(page=page.name):
                    self.assertIn(match[1], self.anchors[page.name])
                    prefix = page.read_text(encoding='utf-8').splitlines()[:4]
                    self.assertIn(f'<a id="{match[1]}"></a>', prefix)
            self.assertIsNone(re.search(r'<a id="[^"]+"></a>\s*\Z',
                                       page.read_text(encoding='utf-8')),
                              f'{page.name}: anchor stranded at the end of a page')

    def test_source_anchors_are_unique_in_the_single_file_edition(self):
        seen = set()
        for page in self.pages:
            for anchor in ANCHOR_DEF.findall(page.read_text(encoding='utf-8')):
                self.assertNotIn(anchor, seen, f'Duplicate anchor #{anchor}')
                seen.add(anchor)

    def test_numbered_section_links_point_to_the_same_chapter(self):
        pattern = re.compile(r'\[([^\]]+)\]\((p\d+-\d+-ch(\d+)\.md)#[^)]+\)')
        for page in self.pages:
            if page.name == 'p9-12-changelog.md':
                continue
            for match in pattern.finditer(page.read_text(encoding='utf-8')):
                number = re.match(r'^§?(\d+)\.\d+(?:\D|$)', match[1])
                if number:
                    self.assertEqual(int(number[1]), int(match[3]), f'{page.name}: {match[1]} -> {match[2]}')

    def test_every_chapter_has_a_quiz_and_a_return_link(self):
        quiz = (DOCS / 'p9-00-quiz.md').read_text(encoding='utf-8')
        for page in self.pages:
            match = re.search(r'-ch(\d+)\.md$', page.name)
            if match:
                number = match[1]
                with self.subTest(chapter=number):
                    section = re.search(rf'<a id="quiz-ch{number}"></a>\n(.*?)(?=\n## |\Z)',
                                        quiz, re.S)
                    self.assertIsNotNone(section, f'Missing quiz for chapter {number}')
                    self.assertIn(f'({page.name}#ch{number})', section.group(1))

    def test_quiz_numbered_references_land_at_the_named_section(self):
        quiz = (DOCS / 'p9-00-quiz.md').read_text(encoding='utf-8')
        checked = 0
        for label, filename, anchor in re.findall(r'\[([^\]]+)\]\((p\d+-\d+-ch\d+\.md)#([^)]+)\)', quiz):
            number = re.match(r'^§?(\d+(?:\.\d+)+)', label)
            if not number:
                continue
            checked += 1
            target = (DOCS / filename).read_text(encoding='utf-8').split(f'<a id="{anchor}"></a>', 1)[1]
            heading = re.match(r'\s*#{2,4} (\d+(?:\.\d+)+)(?=\s)', target)
            self.assertIsNotNone(heading, f'{label}: #{anchor} must immediately precede its section')
            self.assertEqual(number[1], heading[1], f'{label} -> {filename}#{anchor}')
        self.assertGreater(checked, 80)

    def test_quiz_return_rows_link_to_cheatsheet_section(self):
        quiz = (DOCS / 'p9-00-quiz.md').read_text(encoding='utf-8')
        sheet = (DOCS / 'p0-08-cheatsheet.md').read_text(encoding='utf-8')
        for page in self.pages:
            match = re.search(r'-ch(\d+)\.md$', page.name)
            if match:
                with self.subTest(chapter=match[1]):
                    section = re.search(rf'<a id="quiz-ch{match[1]}"></a>\n(.*?)(?=\n## |\Z)', quiz, re.S)
                    self.assertIsNotNone(section)
                    ref = re.search(r'\[🧮 [^\]]*\]\(p0-08-cheatsheet\.md#([a-z]+)\)', section.group(1))
                    self.assertIsNotNone(ref, 'each quiz chapter must link to the formula cheatsheet')
                    self.assertIn(f'<a id="{ref[1]}"></a>', sheet)

    def test_cheatsheet_sections_link_back_to_quizzes(self):
        sheet = (DOCS / 'p0-08-cheatsheet.md').read_text(encoding='utf-8')
        quiz = (DOCS / 'p9-00-quiz.md').read_text(encoding='utf-8')
        blocks = re.findall(r'<a id="([a-z]+)"></a>\n### [^\n]+\n(.*?)(?=\n<a id="|\n📌 |\Z)', sheet, re.S)
        self.assertEqual(len(blocks), 16)
        for sid, body in blocks:
            with self.subTest(section=sid):
                rows = re.findall(r'\[第 (\d+) 章\]\(p9-00-quiz\.md#quiz-ch(\d+)\)', body)
                self.assertTrue(rows, f'{sid} must link to chapter quizzes')
                for shown, anchor in rows:
                    self.assertEqual(shown, anchor)
                    self.assertIn(f'<a id="quiz-ch{shown}"></a>', quiz)


if __name__ == "__main__":
    unittest.main()

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

    def test_every_chapter_links_its_cheatsheet_section(self):
        sheet = (DOCS / 'p0-08-cheatsheet.md').read_text(encoding='utf-8')
        for page in self.pages:
            match = re.search(r'-ch(\d+)\.md$', page.name)
            if match:
                with self.subTest(chapter=match[1]):
                    text = page.read_text(encoding='utf-8')
                    ref = re.search(r'\[速查表·[^\]]*\]\(p0-08-cheatsheet\.md#([a-z]+)\)', text)
                    self.assertIsNotNone(ref, 'chapter must link its cheatsheet section')
                    self.assertIn(f'<a id="{ref[1]}"></a>', sheet)

    PICK_ITEMS = re.compile(r'<a id="(pick-[a-z]+)"></a>.*?\[速查表·[^\]]*\]\(p0-08-cheatsheet\.md#([a-z]+)\)')

    def test_picks_items_link_to_cheatsheet_section(self):
        """必读精选每条必须带行级锚点 + 🧮 速查表直达链接，且目标段存在。"""
        picks = (DOCS / 'p0-05-picks.md').read_text(encoding='utf-8')
        sheet = (DOCS / 'p0-08-cheatsheet.md').read_text(encoding='utf-8')
        items = self.PICK_ITEMS.findall(picks)
        self.assertEqual(6, len(items), '精选共 6 条，每条都要有 <a id="pick-*"> 行级锚点和速查表链接')
        for anchor, sec in items:
            with self.subTest(pick=anchor):
                self.assertIn(f'<a id="{sec}"></a>', sheet, f'速查表缺段：{sec}')

    def test_cheatsheet_sections_link_back_to_picks_symmetrically(self):
        """速查表段的 ⭐ 回链与精选条的 🧮 正链必须互指 —— 只改一侧（映射漂移）即红。"""
        sheet = (DOCS / 'p0-08-cheatsheet.md').read_text(encoding='utf-8')
        picks = (DOCS / 'p0-05-picks.md').read_text(encoding='utf-8')
        forward = dict()
        for anchor, sec in self.PICK_ITEMS.findall(picks):
            forward[sec] = anchor
        self.assertEqual(6, len(forward), '正链的 段→条 映射塌缩——两条精选指向了同一段')
        actual = dict()
        for sid, body in re.findall(r'<a id="([a-z]+)"></a>\n### [^\n]+\n(.*?)(?=\n<a id="|\n📌 |\Z)', sheet, re.S):
            m = re.search(r'⭐ \[[^\]]*\]\(p0-05-picks\.md#(pick-[a-z]+)\)', body)
            if m:
                self.assertIn(f'<a id="{m.group(1)}"></a>', picks, f'{sid} 的回链锚点在精选页不存在')
                actual[sid] = m.group(1)
        self.assertEqual(forward, actual, '精选 ↔ 速查表映射不对称（一侧改了另一侧没跟）')

    def test_changelog_quick_view_jumps_resolve(self):
        """更新日志「系列速览」必须真能跳：每个 (#锚点) 都落在本页的 <a id> 上。"""
        page = (DOCS / 'p9-12-changelog.md').read_text(encoding='utf-8')
        jumps = re.findall(r'\]\(#([^)]+)\)', page)
        self.assertGreaterEqual(len(jumps), 8, '速览至少覆盖 8 个系列组——速览表塌了就是护栏瞎了')
        ids = set(ANCHOR_DEF.findall(page))
        missing = sorted({j for j in jumps if j not in ids})
        self.assertEqual([], missing, f'速览跳转缺少锚点：{missing}')

    def test_changelog_series_groups_hold_every_version(self):
        """每个版本行必须恰好落在一个系列组里；速览与组标题的条数必须等于实际行数。

        发版仪式新增版本行时，速览条数、组标题条数、组范围都要跟着动——
        这一条把「忘了同步」直接变红，而不是让速览悄悄说谎。
        """
        page = (DOCS / 'p9-12-changelog.md').read_text(encoding='utf-8')
        version_row = re.compile(r'^\| \**v\d', re.M)
        parts = re.split(r'^<a id="(log-[\w\-]+)"></a>$', page, flags=re.M)
        groups = list(zip(parts[1::2], parts[2::2]))
        self.assertGreaterEqual(len(groups), 8, '系列组塌回单表——分组本身被删了')
        self.assertEqual([], version_row.findall(parts[0]), '第一组之前不允许出现版本行')
        counts, covered = {}, []
        for anchor, body in groups:
            rows = version_row.findall(body)
            self.assertTrue(rows, f'组 {anchor} 里没有版本行')
            title = re.search(r'(?m)^### .+（(\d+) 条）', body)
            self.assertIsNotNone(title, f'组 {anchor} 缺带条数的标题（右侧目录会瞎）')
            self.assertEqual(int(title.group(1)), len(rows), f'组 {anchor} 标题条数与实际行数不符')
            counts[anchor] = len(rows)
            covered += rows
        self.assertEqual(covered, version_row.findall(page), '各组行数拼起来必须等于全表、不多不少')
        declared = dict((m[0], int(m[1])) for m in
                        re.findall(r'\]\(#(log-[\w\-]+)\) \| [^|]+\| (\d+) \|', page))
        self.assertEqual(declared, counts, '速览的条数与组内实际行数不一致（发版忘同步速览）')


if __name__ == "__main__":
    unittest.main()

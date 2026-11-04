#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""视觉密度扫描器：口径、锚点形态与边界情形（夹具测试，不扫真实章节）。"""
import tempfile
import unittest
from pathlib import Path

import audit_visual_density as avd

DOC = """# 第 N 章\n\n## {h}\n\n{body}\n"""


def chapter(body: str, name: str = "p1-01-ch0.md") -> Path:
    tmp = Path(tempfile.mkdtemp())
    path = tmp / name
    path.write_text(body, encoding="utf-8")
    return path


def filler(n: int) -> str:
    return "字" * n


class AnchorFormsTests(unittest.TestCase):
    def test_html_and_markdown_images_count(self):
        raw = ('<p><img src="assets/figures/a.svg" alt="a"></p>\n'
               "![说明](assets/photos/b.jpg)\n")
        p = chapter(raw)
        r = avd.audit(p)
        self.assertEqual(2, r["visuals"])
        self.assertEqual(["assets/figures/a.svg", "assets/photos/b.jpg"],
                         r["assets"])

    def test_link_masquerading_as_image_does_not_count(self):
        raw = '<a href="assets/svg/anim.svg">看动画</a>\n' + filler(900)
        r = avd.audit(chapter(raw))
        self.assertEqual(0, r["visuals"])

    def test_code_fence_and_comment_images_do_not_count(self):
        raw = ("```bash\n<img src=\"assets/figures/x.svg\">\n```\n"
               "<!-- <img src=\"assets/figures/y.svg\"> -->\n")
        r = avd.audit(chapter(raw))
        self.assertEqual(0, r["visuals"])

    def test_figure_wrapping_img_counts_once(self):
        raw = ('<figure><img src="assets/figures/a.svg" alt="a">'
               "<figcaption>图注</figcaption></figure>\n")
        r = avd.audit(chapter(raw))
        self.assertEqual(1, r["visuals"])


class CharConventionTests(unittest.TestCase):
    def test_chars_are_raw_non_whitespace(self):
        raw = "abc 汉字\n\n**粗** | 表 |"
        r = avd.audit(chapter(raw))
        # 原文非空白字符：abc汉字**粗**|表|（标记符与表格竖线都计）
        self.assertEqual(avd.nonws(chapter(raw).read_text(encoding="utf-8")),
                         r["chars"])

    def test_gaps_split_by_anchor_and_cover_head_tail(self):
        raw = filler(700) + '\n<img src="assets/figures/m.svg">\n' + filler(500)
        r = avd.audit(chapter(raw))
        self.assertEqual([700, 500], r["gaps"])
        self.assertEqual(700, r["longest_gap"])

    def test_gap_ignores_the_img_tag_itself(self):
        raw = filler(600) + '\n<img src="assets/figures/a-really-long-file-name.svg" alt="long alt text here">\n' + filler(600)
        r = avd.audit(chapter(raw))
        self.assertEqual([600, 600], r["gaps"])


if __name__ == "__main__":
    unittest.main()

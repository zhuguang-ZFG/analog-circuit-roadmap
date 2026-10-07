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


if __name__ == "__main__":
    unittest.main()

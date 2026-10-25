#!/usr/bin/env python3
"""16K PDF：补白、罗马/阿拉伯标签、三级书签、000 回填、页眉页脚。"""
import sys
import tempfile
import unittest
from pathlib import Path

BOOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BOOK))

from book.pdf import check_pdf, pad_to_multiple, stamp_pdf  # noqa: E402

try:
    import fitz
except ImportError:  # pragma: no cover
    fitz = None

try:
    from playwright.sync_api import sync_playwright
except ImportError:  # pragma: no cover
    sync_playwright = None

MM = 72 / 25.4

FRONT = [
    {"kind": "half_title", "id": "half-title", "title": "半书名", "group": "front"},
    {"kind": "title_page", "id": "title-page", "title": "书名页", "group": "front"},
    {"kind": "copyright", "id": "copyright", "title": "版权页", "group": "front"},
    {"kind": "front", "id": "page-front-a", "title": "前言", "group": "front"},
    {"kind": "front", "id": "page-front-b", "title": "导读", "group": "front"},
    {"kind": "front", "id": "page-front-c", "title": "简史", "group": "front"},
    {"kind": "front", "id": "page-front-d", "title": "约定", "group": "front"},
    {"kind": "toc", "id": "book-toc", "title": "全书目录", "group": "front"},
    {"kind": "list_of_figures", "id": "list-of-figures", "title": "插图目录",
     "group": "front"},
    {"kind": "list_of_tables", "id": "list-of-tables", "title": "表格目录",
     "group": "front"},
    {"kind": "front", "id": "page-front-e", "title": "符号", "group": "front"},
]
BODY = [
    {"kind": "part", "id": "part-i", "title": "第一篇 测试", "group": "body"},
    {"kind": "chapter", "id": "page-p1-01-ch0", "title": "第 0 章 测试章",
     "group": "body"},
    {"kind": "appendix_opener", "id": "appendix-a", "title": "附录 A 测试",
     "group": "appendix"},
    {"kind": "appendix", "id": "page-p0-08-cheatsheet", "title": "附录 B 速查",
     "group": "appendix"},
]
BACK = [
    {"kind": "bibliography", "id": "bibliography", "title": "参考文献", "group": "back"},
    {"kind": "index", "id": "book-index", "title": "索引", "group": "back"},
    {"kind": "back", "id": "page-p9-12-changelog", "title": "版本记录", "group": "back"},
    {"kind": "colophon", "id": "colophon", "title": "版本页", "group": "back"},
]
PAGES = FRONT + BODY + BACK
TOC = [
    {"level": 1, "title": "第一篇 测试", "anchor": "part-i", "kind": "part"},
    {"level": 2, "title": "第 0 章 测试章", "anchor": "page-p1-01-ch0",
     "kind": "chapter"},
    {"level": 3, "title": "0.1 测试小节", "anchor": "p1-01-ch0--s1",
     "kind": "section"},
    {"level": 1, "title": "附录 A 测试", "anchor": "appendix-a", "kind": "appendix"},
    {"level": 2, "title": "附录 B 速查", "anchor": "page-p0-08-cheatsheet",
     "kind": "appendix"},
]
MODEL = {
    "schema": 1, "manifest_sha256": "0" * 64, "edition_status": "draft",
    "pages": PAGES, "toc": TOC,
    "lof": [{"caption": "图 0-1　测试图", "anchor": "p1-01-ch0--fig-1"}],
    "lot": [{"caption": "表 0-1　测试表", "anchor": "p1-01-ch0--table-1"}],
    "figures": 1, "tables": 1, "endnotes": 0,
    "audit": {"errors": [], "warnings": [], "pages": len(PAGES), "bytes": 0},
    "stats": {"logical_pages": len(PAGES), "images": 1, "formulas": 0,
              "chapters": {}},
}
MANIFEST = {
    "title": "通往模拟电路之路", "subtitle": "从欧姆定律到芯片内部结构",
    "author": "zhuguang-ZFG 与贡献者", "license": "CC BY-SA 4.0",
    "release": {"edition_status": "draft"},
}


def _rows(entries):
    # brief 的合成 lof/lot 只有 caption（真实模型两者都有），按 caption 兜底
    return "".join(
        f'<div class="toc-row"><a href="#{e["anchor"]}">'
        f'{e.get("title") or e["caption"]}<span class="toc-page">000</span></a></div>'
        for e in entries)


def synthetic_html():
    toc = _rows(TOC)
    lof = _rows(MODEL["lof"])
    lot = _rows(MODEL["lot"])
    paragraphs = "".join(
        "<p>" + ("测试正文用于把章节撑到多页，验证续页页眉与页脚。" * 3) + "</p>"
        for _ in range(80))
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
@page {{ size: 185mm 260mm; margin: 20mm; }}
html, body {{ margin: 0; }}
body {{ font-family: serif; font-size: 10.5pt; line-height: 17.5pt; }}
.book-page {{ break-before: page; }}
.book-page:first-of-type {{ break-before: auto; }}
h1 {{ font-size: 22pt; }}
.toc-row a {{ display: flex; justify-content: space-between; }}
figure, table {{ break-inside: avoid; }}
</style></head><body>
<section class="book-page"><h1 id="half-title">半书名</h1></section>
<section class="book-page"><h1 id="title-page">书名页</h1></section>
<section class="book-page"><h1 id="copyright">版权页</h1></section>
<section class="book-page"><h1 id="page-front-a">前言</h1></section>
<section class="book-page"><h1 id="page-front-b">导读</h1></section>
<section class="book-page"><h1 id="page-front-c">简史</h1></section>
<section class="book-page"><h1 id="page-front-d">约定</h1></section>
<section class="book-page"><h1 id="book-toc">全书目录</h1><nav>{toc}</nav></section>
<section class="book-page"><h1 id="list-of-figures">插图目录</h1><nav>{lof}</nav></section>
<section class="book-page"><h1 id="list-of-tables">表格目录</h1><nav>{lot}</nav></section>
<section class="book-page"><h1 id="page-front-e">符号</h1></section>
<section class="book-page"><h1 id="part-i">第一篇 测试</h1></section>
<section class="book-page"><h1 id="page-p1-01-ch0">第 0 章 测试章</h1>
<h2 id="p1-01-ch0--s1">0.1 测试小节</h2>
<figure id="p1-01-ch0--fig-1"><p>图</p><figcaption>图 0-1 测试图</figcaption></figure>
<table id="p1-01-ch0--table-1"><caption>表 0-1 测试表</caption>
<tr><th>列</th></tr><tr><td>值</td></tr></table>{paragraphs}</section>
<section class="book-page"><h1 id="appendix-a">附录 A 测试</h1></section>
<section class="book-page"><h1 id="page-p0-08-cheatsheet">附录 B 速查</h1></section>
<section class="book-page"><h1 id="bibliography">参考文献</h1></section>
<section class="book-page"><h1 id="book-index">索引</h1>
<p><a href="#page-p1-01-ch0"><strong>测试术语</strong></a>
<a href="#p1-01-ch0--s1"><span class="index-page">000</span></a></p></section>
<section class="book-page"><h1 id="page-p9-12-changelog">版本记录</h1></section>
<section class="book-page"><h1 id="colophon">版本页</h1></section>
</body></html>"""


@unittest.skipIf(fitz is None or sync_playwright is None,
                 "需要 PyMuPDF 与 Playwright")
class PdfTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.tmp.cleanup)
        cls.root = Path(cls.tmp.name)
        cls.html = cls.root / "synthetic.html"
        cls.html.write_text(synthetic_html(), encoding="utf-8")
        cls.raw = cls.root / "raw.pdf"
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(cls.html.resolve().as_uri(), wait_until="load")
            page.pdf(path=str(cls.raw), print_background=True,
                     prefer_css_page_size=True, outline=True, tagged=True)
            browser.close()
        cls.pdf = cls.root / "stamped.pdf"
        cls.report = stamp_pdf(cls.raw, cls.pdf, MODEL, MANIFEST)
        cls.doc = fitz.open(cls.pdf)

    @classmethod
    def tearDownClass(cls):
        cls.doc.close()

    def test_page_is_16k_and_padded_to_four(self):
        self.assertEqual(0, self.report["pages"] % 4)
        for page in self.doc:
            self.assertAlmostEqual(185, page.rect.width / MM, delta=0.5)
            self.assertAlmostEqual(260, page.rect.height / MM, delta=0.5)
        self.assertTrue(self.report["padded"])

    def test_page_labels_are_roman_then_arabic(self):
        self.assertEqual("i", self.doc[0].get_label())
        self.assertEqual("xi", self.doc[10].get_label())
        self.assertEqual("1", self.doc[self.report["body_start"]].get_label())
        self.assertEqual("2", self.doc[self.report["body_start"] + 1].get_label())

    def test_bookmarks_are_three_levels_from_model(self):
        toc = self.doc.get_toc()
        self.assertEqual([1, 2, 3, 1, 2], [entry[0] for entry in toc])
        self.assertEqual([entry["title"] for entry in MODEL["toc"]],
                         [entry[1] for entry in toc])
        starts = self.report["starts"]
        self.assertEqual(starts[11] + 1, toc[0][2])
        self.assertEqual(starts[12] + 1, toc[1][2])
        self.assertEqual(starts[12] + 1, toc[2][2])
        self.assertEqual(starts[13] + 1, toc[3][2])
        self.assertEqual(starts[14] + 1, toc[4][2])

    def test_000_is_backfilled_and_links_survive(self):
        starts = self.report["starts"]
        regions = [(starts[7], starts[8]), (starts[8], starts[9]),
                   (starts[9], starts[10]), (starts[16], starts[17])]
        for begin, end in regions:
            text = "\n".join(self.doc[p].get_text() for p in range(begin, end))
            self.assertNotIn("000", text)
        self.assertGreaterEqual(self.report["backfilled"], 7)
        toc_links = [link for link in self.doc[starts[7]].get_links()
                     if isinstance(link.get("page"), int)]
        self.assertEqual(len(TOC), len(toc_links))

    def test_openers_and_front_pages_have_no_folio(self):
        starts = self.report["starts"]
        height = self.doc[0].rect.height
        clip = fitz.Rect(0, height - 18 * MM, self.doc[0].rect.width, height)
        for pno in (0, 1, 2, starts[11], starts[12]):
            self.assertEqual("", self.doc[pno].get_text("text", clip=clip).strip())
        continuation = starts[12] + 1
        self.assertTrue(self.doc[continuation].get_text("text", clip=clip).strip())

    def test_running_heads_use_outer_edge_and_chapter_title(self):
        starts = self.report["starts"]
        clip = fitz.Rect(0, 0, self.doc[0].rect.width, 18 * MM)
        chapter_start = starts[12]
        left_page = chapter_start + 1
        right_page = chapter_start + 2
        self.assertEqual(1, left_page % 2, "物理奇数页必须是左页")
        self.assertEqual(0, right_page % 2, "物理偶数页必须是右页")
        self.assertIn("通往模拟电路之路",
                      self.doc[left_page].get_text("text", clip=clip))
        self.assertIn("第 0 章 测试章",
                      self.doc[right_page].get_text("text", clip=clip))

    def test_check_pdf_reports_draft_length_without_failing(self):
        report = check_pdf(self.pdf, MODEL, MANIFEST)
        self.assertEqual([], report["problems"])
        self.assertTrue(any("450" in warning for warning in report["warnings"]))

    def test_pad_to_multiple_is_idempotent(self):
        doc = fitz.open(self.pdf)
        try:
            before = doc.page_count
            padded = pad_to_multiple(doc, 4)
            self.assertEqual([], padded)
            self.assertEqual(before, doc.page_count)
        finally:
            doc.close()


if __name__ == "__main__":
    unittest.main()

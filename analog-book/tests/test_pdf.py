#!/usr/bin/env python3
"""PDF 结构冒烟：页数、元数据、书签、页码与封面无页码。"""
import sys
import unittest
from pathlib import Path

BOOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BOOK))

import build_book  # noqa: E402

try:
    import fitz
except ImportError:  # pragma: no cover
    fitz = None

try:
    from playwright.sync_api import sync_playwright
except ImportError:  # pragma: no cover
    sync_playwright = None


@unittest.skipIf(fitz is None or sync_playwright is None,
                 "需要 PyMuPDF 与 Playwright")
class PdfBook(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = BOOK / "dist" / build_book.OUTPUT_NAME
        if not cls.html.is_file():
            build_book.build_html(BOOK / "dist", rebuild_site=False)
        cls.pdf = build_book.build_pdf(cls.html)

    def test_pdf_structure(self):
        document = fitz.open(self.pdf)
        try:
            self.assertGreater(document.page_count, 40)
            self.assertEqual("通往模拟电路之路", document.metadata["title"])
            toc = document.get_toc()
            self.assertEqual(11, sum(1 for level, _, _ in toc if level == 1))
            self.assertEqual(60, sum(1 for level, _, _ in toc if level == 2))
            pages = [page for _level, _title, page in toc]
            self.assertEqual(pages, sorted(pages))
            self.assertTrue(all(1 <= page <= document.page_count for page in pages))
            # 封面/版权/目录无页码：前 3 页不含 " / " 页脚
            for index in range(min(3, document.page_count)):
                self.assertNotIn(" / ", document[index].get_text())
            toc_text = "".join(document[i].get_text()
                               for i in range(min(3, document.page_count)))
            self.assertIn("全书目录", toc_text)
            self.assertRegex(toc_text, r"\b[1-9]\d*\b")
            # 正文页有页码
            self.assertIn(" / ", document[document.page_count - 1].get_text())
            first_body = min(page for level, _title, page in toc if level == 2)
            sizes = [round(span["size"], 1)
                     for block in document[first_body - 1].get_text("dict")["blocks"]
                     for line in block.get("lines", [])
                     for span in line["spans"]]
            self.assertTrue(any(10.2 <= size <= 10.8 for size in sizes),
                            f"正文未按 10.5pt 排版：{sorted(set(sizes))[:8]}")
            self.assertIn("来源与许可",
                          "".join(document[i].get_text()
                                  for i in range(document.page_count - 10,
                                                 document.page_count)))
        finally:
            document.close()


if __name__ == "__main__":
    unittest.main()

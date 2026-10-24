"""整书产物必须并入 Pages 站点，并生成可点开两种格式的下载页。"""
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from publish_book import BOOK_DIR_NAME, publish  # noqa: E402

BOOK_HTML = """<!doctype html>
<html><head>
<meta name="book-version" content="1.2.3">
<meta name="book-date" content="2026-10-24">
</head><body><h1>整书</h1></body></html>
"""


class PublishBookTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.site = self.root / "site"
        self.site.mkdir()
        (self.site / "index.html").write_text("<!doctype html><title>site</title>", encoding="utf-8")
        self.html = self.root / "analog-circuit-book.html"
        self.html.write_text(BOOK_HTML, encoding="utf-8")
        self.pdf = self.root / "analog-circuit-book.pdf"
        self.pdf.write_bytes(b"%PDF-1.7\n" + b"0" * 4096)

    def test_copies_artifacts_and_writes_landing_page(self):
        target = publish(self.html, self.pdf, self.site)
        self.assertEqual(self.site / BOOK_DIR_NAME, target)
        self.assertTrue((target / "analog-circuit-book.html").is_file())
        self.assertTrue((target / "analog-circuit-book.pdf").is_file())
        landing = (target / "index.html").read_text(encoding="utf-8")
        self.assertIn("离线整书", landing)
        self.assertIn("1.2.3", landing)
        self.assertIn("2026-10-24", landing)
        self.assertIn('href="analog-circuit-book.html"', landing)
        self.assertIn('href="analog-circuit-book.pdf"', landing)
        self.assertIn("4 KB", landing)
        self.assertIn('href="../index.html"', landing)

    def test_rejects_missing_artifact(self):
        self.pdf.unlink()
        with self.assertRaises(FileNotFoundError):
            publish(self.html, self.pdf, self.site)

    def test_rejects_missing_site_index(self):
        (self.site / "index.html").unlink()
        with self.assertRaises(FileNotFoundError):
            publish(self.html, self.pdf, self.site)


if __name__ == "__main__":
    unittest.main()

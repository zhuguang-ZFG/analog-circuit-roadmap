"""README internal-link integrity: every `#fragment` link must resolve.

README links come in two forms — HTML (`href="#..."` in nav blocks) and
Markdown (`[text](#frag)` everywhere else). Both must point at an existing
`<a id="...">`, and neither may be empty. Catches empty fragments
(e.g. `[⭐ 必读精选](#)`) and anchors left behind after section renames.
Pure stdlib, runs in seconds.
"""
import re
import unittest
from pathlib import Path

README = Path(__file__).resolve().parents[1] / "README.md"


class ReadmeLinkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = README.read_text(encoding="utf-8")
        cls.ids = set(re.findall(r'<a id="([^"]+)"\s*></a>', cls.text))

    def test_ids_exist(self):
        self.assertTrue(self.ids, "no <a id> anchors found — regex may be wrong")

    def test_all_fragment_links_resolve(self):
        html = re.findall(r'href="#([^"]*)"', self.text)
        md = re.findall(r'\]\(#([^)]*)\)', self.text)
        hrefs = html + md
        self.assertTrue(hrefs, "no #fragment links found — regex may be wrong")
        empty = sorted({h for h in hrefs if not h})
        self.assertEqual(empty, [], "empty fragment links (`](#)` / `href=\"#\"`) must have a target")
        missing = sorted({h for h in hrefs if h and h not in self.ids})
        self.assertEqual(missing, [],
                         f"fragments without a matching <a id>: {missing}")


if __name__ == "__main__":
    unittest.main()

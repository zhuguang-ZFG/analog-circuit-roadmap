#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""皮肤管线：finalize 注入纸面层、标题装饰，且幂等；产物过底稿闸。"""
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1]
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from visuals import static_fig  # noqa: E402

DRAFT = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 680" role="img"
 aria-labelledby="figTitle figDesc">
<title id="figTitle">标题行</title>
<desc id="figDesc">描述。</desc>
<text x="480" y="29" text-anchor="middle" font-size="19" font-weight="bold"
 fill="#1e293b">标题行</text>
<line x1="100" y1="200" x2="860" y2="200" stroke="#16202b" stroke-width="2"/>
<rect x="100" y="260" width="200" height="120" rx="10" stroke="#1f5d7a"
 fill="#e6eff3"/>
<circle cx="500" cy="320" r="40" stroke="#a8321f" fill="none"/>
<text x="110" y="420" font-size="16" fill="#37424e">甲乙丙丁戊己庚辛壬癸子丑寅卯</text>
<text x="110" y="450" font-size="14" fill="#5b666f">32 mV / 1.1 V / 8 Ω</text>
<text x="110" y="480" font-size="14" fill="#8b8272">小字标注</text>
<text x="110" y="510" font-size="14" fill="#3d6b4a">通过</text>
<text x="110" y="540" font-size="14" fill="#a4630f">返工点</text>
</svg>'''


class FinalizeTests(unittest.TestCase):
    def out(self, text: str, title: str | None) -> str:
        return static_fig.finalize(text, title)

    def test_injects_paper_and_dark_css(self):
        out = self.out(DRAFT, None)
        self.assertIn("page-bg", out)
        self.assertIn('id="bgL"', out)
        self.assertIn("prefers-color-scheme", out)

    def test_retint_legacy_title_and_bow_lines(self):
        out = self.out(DRAFT, None)
        self.assertNotIn("#1e293b", out)
        self.assertIn('fill="none"', out)

    def test_title_decor_only_with_title(self):
        plain = self.out(DRAFT, None)
        self.assertNotIn("KaiTi", plain)
        decor = self.out(DRAFT, "标题行")
        self.assertIn("KaiTi", decor)
        self.assertIn("opacity=\"0.5\"", decor)

    def test_idempotent(self):
        once = self.out(DRAFT, "标题行")
        twice = self.out(once, "标题行")
        self.assertEqual(once, twice)

    def test_finalized_passes_draft_checker(self):
        """皮肤后的成品仍是合法底稿（纸面层不影响闸）。"""
        import visuals.check_draft as cd
        tmp = Path(tempfile.mkdtemp()) / "f.svg"
        tmp.write_text(self.out(DRAFT, "标题行"), encoding="utf-8")
        self.assertEqual([], [line for line in cd.check(tmp)
                              if "非 token 色值" not in line])

    def test_missing_viewbox_raises(self):
        with self.assertRaises(ValueError):
            self.out("<svg></svg>", None)


if __name__ == "__main__":
    unittest.main()

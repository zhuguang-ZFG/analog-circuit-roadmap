#!/usr/bin/env python3
"""印刷 SVG 净化：去底纹、深色模式、动效与高饱和色，保留静态内容。"""
import base64
import re
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

BOOK = Path(__file__).resolve().parent.parent
ROOT = BOOK.parent
sys.path.insert(0, str(BOOK))

from book import content  # noqa: E402
from book.svg_refine import is_legacy_svg, refine_svg  # noqa: E402

LEGACY = """<svg xmlns="http://www.w3.org/2000/svg" width="400" height="300" viewBox="0 0 400 300">
<defs>
<linearGradient id="bgL"><stop stop-color="#ffffff"/></linearGradient>
<linearGradient id="hdr"><stop stop-color="#2563eb"/></linearGradient>
<pattern id="dots"><circle r="1"/></pattern>
<filter id="soft"><feDropShadow dx="0" dy="2"/></filter>
</defs>
<rect class="page-bg" width="400" height="300" fill="url(#bgL)"/>
<rect width="400" height="300" fill="url(#dots)" opacity="0.4"/>
<style>text{font-family:"Segoe UI","Microsoft YaHei"}@media (prefers-color-scheme: dark){.page-bg{fill:#0a1020}}</style>
<title>\U0001F9EE 示例图</title>
<path d="M10 10 L100 100" stroke="#2563eb" stroke-width="2" fill="none"/>
<rect x="20" y="20" width="80" height="40" rx="4" fill="#f8fafc" stroke="#e2e8f0" filter="url(#soft)"/>
<text x="20" y="140" fill="#dc2626">错误</text>
<text x="20" y="110" fill="#059669">正确</text>
<text x="20" y="160" fill="#f59e0b">注意</text>
<text class="waveform-phase" x="20" y="140" fill="#b45309">阶段字幕</text>
<circle r="4" fill="#7c3aed"><animateMotion dur="2s" path="M0 0 L10 10"/></circle>
<g><rect x="0" y="270" width="400" height="30" fill="#2563eb" opacity="0"/><text x="200" y="290" opacity="0">隐藏字幕</text></g>
</svg>"""

LEGACY_COLORS = re.compile(
    r"#(?:2563eb|1d4ed8|3b82f6|0284c7|0369a1|0ea5e9|60a5fa|7dd3fc|"
    r"38bdf8|0891b2|93c5fd|059669|10b981|34d399|065f46|7c3aed|a78bfa|"
    r"dc2626|b91c1c|991b1b|f87171|fca5a5|f59e0b|94a3b8|8497ad|64748b|"
    r"475569|334155|1e293b|0f172a|cbd5e1|e2e8f0|f8fafc|f1f5f9|fecaca)\b",
    re.IGNORECASE)


class RefineFixtureTests(unittest.TestCase):
    def test_legacy_marker_detection(self):
        self.assertTrue(is_legacy_svg(LEGACY))
        self.assertFalse(is_legacy_svg(
            '<svg xmlns="http://www.w3.org/2000/svg"><path d="M0 0"/></svg>'))

    def test_removes_theme_animation_and_saturated_palette(self):
        out = refine_svg(LEGACY)
        for token in ("<linearGradient", "<pattern", "<filter", "<animate",
                      "prefers-color-scheme", "page-bg", "url(#",
                      "filter=", "Segoe UI"):
            self.assertNotIn(token, out)
        self.assertIsNone(LEGACY_COLORS.search(out))
        self.assertNotIn("\U0001F9EE", out)
        self.assertIn("示例图", out)

    def test_preserves_static_content_and_maps_palette(self):
        out = refine_svg(LEGACY)
        for token in ('d="M10 10 L100 100"', "#0f766e", "#b42318",
                      "#3f6f4f", "#b45309", 'x="20"',
                      "Microsoft YaHei", "Noto Sans SC", "错误", "正确",
                      "注意"):
            self.assertIn(token, out)
        self.assertNotIn("阶段字幕", out)
        ET.fromstring(out)

    def test_refine_is_idempotent(self):
        once = refine_svg(LEGACY)
        self.assertEqual(once, refine_svg(once))

    def test_rejects_dtd_and_entities(self):
        with self.assertRaises(ValueError):
            refine_svg("<!DOCTYPE svg [<!ENTITY x 'y'>]>" + LEGACY)

    def test_non_legacy_svg_is_untouched(self):
        svg = ('<svg xmlns="http://www.w3.org/2000/svg">'
               '<path stroke="#2563eb"/></svg>')
        self.assertEqual(svg, refine_svg(svg))

    def test_data_uri_hook_refines_legacy_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            legacy = root / "legacy.svg"
            legacy.write_text(LEGACY, encoding="utf-8")
            uri = content._data_uri(legacy, root)
            svg = base64.b64decode(uri.split(",", 1)[1]).decode("utf-8")
            self.assertNotIn("<animate", svg)
            plain = root / "plain.svg"
            source = '<svg xmlns="http://www.w3.org/2000/svg"/>'
            plain.write_text(source, encoding="utf-8")
            decoded = base64.b64decode(
                content._data_uri(plain, root).split(",", 1)[1]).decode()
            self.assertEqual(source, decoded)


class RefineBookAssetsTests(unittest.TestCase):
    def test_all_legacy_assets_are_print_clean(self):
        files = sorted((ROOT / "assets" / "svg").glob("*.svg"))
        self.assertEqual(112, len(files))
        for path in files:
            with self.subTest(path.name):
                source = path.read_text(encoding="utf-8")
                self.assertTrue(is_legacy_svg(source), path.name)
                out = refine_svg(source)
                ET.fromstring(out)
                for token in ("<animate", "<linearGradient", "<pattern",
                              "<filter", "prefers-color-scheme",
                              "url(#", "filter=", "Segoe UI"):
                    self.assertNotIn(token, out, path.name)
                self.assertIsNone(LEGACY_COLORS.search(out), path.name)
                self.assertIsNone(
                    re.search(r"[\U0001F000-\U0001FAFF]", out), path.name)
                self.assertIn("Microsoft YaHei", out, path.name)

    def test_representative_figure_keeps_geometry_and_labels(self):
        source = (ROOT / "assets" / "svg" / "pcb-routing.svg").read_text(
            encoding="utf-8")
        out = refine_svg(source)
        for token in ('viewBox="0 0 800 560"', "PCB 布线四招",
                      "M70,150 H160 V220", "① 拐角：用 45°，不用 90°"):
            self.assertIn(token, out)


if __name__ == "__main__":
    unittest.main()

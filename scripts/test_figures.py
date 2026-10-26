#!/usr/bin/env python3
"""静态技术插图：离线、配色、标题/描述，以及正文中的 figure + 图注。"""
import re
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIGURES = ROOT / "assets" / "figures"
DOCS = ROOT / "docs"

WAVE1_FIGURES = {
    "ch00-controlled-sources.svg",
    "ch02-operating-map.svg",
    "ch02-tvs-clamp.svg",
    "ch11-cascode.svg",
    "ch14-error-budget.svg",
    "ch14-power-tree-timing.svg",
    "ch16-probe-model.svg",
    "ch16-signal-injection.svg",
}
PALETTE = {"#14213d", "#b45309", "#0f766e"}
EXTERNAL_REF = re.compile(r'(?:href|src)\s*=\s*["\']https?://', re.I)


class FigureTests(unittest.TestCase):
    def test_wave1_figures_exist(self):
        present = {path.name for path in FIGURES.glob("*.svg")}
        self.assertEqual(set(), WAVE1_FIGURES - present)

    def test_svgs_are_offline_labelled_and_colour_locked(self):
        for path in sorted(FIGURES.glob("*.svg")):
            name = path.name
            text = path.read_text(encoding="utf-8")
            root = ET.fromstring(text)
            self.assertTrue(root.tag.endswith("svg"), name)
            self.assertTrue(root.get("viewBox"), name)
            self.assertNotIn("<script", text.lower(), name)
            self.assertNotIn("<image", text.lower(), name)
            self.assertNotIn("<foreignobject", text.lower(), name)
            self.assertEqual([], EXTERNAL_REF.findall(text), name)
            self.assertRegex(text, r"<title[^>]*>.+?</title>", name)
            self.assertRegex(text, r"<desc[^>]*>.+?</desc>", name)
            self.assertGreaterEqual(text.count("<text"), 6, name)
            self.assertTrue(any(colour in text.lower() for colour in PALETTE),
                            name)

    def test_each_figure_is_wrapped_in_a_figure_with_caption(self):
        docs = "\n".join(path.read_text(encoding="utf-8")
                         for path in sorted(DOCS.glob("*.md")))
        blocks = re.findall(r"<figure\b.*?</figure>", docs, re.S)
        for path in sorted(FIGURES.glob("*.svg")):
            name = path.name
            matches = [block for block in blocks
                       if f"assets/figures/{name}" in block]
            self.assertEqual(1, len(matches), f"{name} 应恰好出现一次")
            self.assertRegex(matches[0], r"<figcaption>\s*\S",
                             f"{name} 缺少非空图注")
        referenced = set(re.findall(
            r"assets/figures/([A-Za-z0-9._-]+\.svg)", docs))
        self.assertEqual(set(), referenced - {path.name for path in
                                              FIGURES.glob("*.svg")},
                        "正文引用了不存在的图")


if __name__ == "__main__":
    unittest.main()

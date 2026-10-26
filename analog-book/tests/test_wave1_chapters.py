#!/usr/bin/env python3
"""Wave 1 逐章合同：字数、节结构、图表、算例、仿真与练习。"""
from __future__ import annotations

import json
import re
import sys
import unittest
from pathlib import Path

BOOK = Path(__file__).resolve().parent.parent
ROOT = BOOK.parent
sys.path.insert(0, str(BOOK))

CHAPTER_CONTRACTS = {
    "0": {
        "file": "p1-01-ch0.md",
        "floor": 15000,
        "sections": ("### 0.7", "### 0.8", "### 0.9", "### 0.10"),
        "examples": 3,
        "figures": 6,
        "tables": 6,
        "quiz": 10,
        "figure_assets": (
            "assets/figures/ch00-controlled-sources.svg",
            "assets/figures/ch00-source-personality.svg",
        ),
        "deck": "assets/spice/ch00/divider.cir",
    },
    "2": {
        "file": "p1-03-ch2.md",
        "floor": 16000,
        "sections": ("### 2.9", "### 2.10", "### 2.11", "### 2.12", "### 2.13"),
        "examples": 3,
        "figures": 9,
        "tables": 5,
        "quiz": 9,
        "figure_assets": (
            "assets/figures/ch02-operating-map.svg",
            "assets/figures/ch02-tvs-clamp.svg",
            "assets/figures/ch02-diode-roadmap.svg",
        ),
        "deck": "assets/spice/ch02/rectifier.cir",
    },
    "11": {
        "file": "p2-01-ch11.md",
        "floor": 18000,
        "sections": ("### 11.8", "### 11.9", "### 11.10", "### 11.11"),
        "examples": 3,
        "figures": 8,
        "tables": 5,
        "quiz": 10,
        "figure_assets": (
            "assets/figures/ch11-cascode.svg",
            "assets/figures/ch11-cascode-mirror.svg",
        ),
        "deck": "assets/spice/ch11/diffpair.cir",
    },
    "14": {
        "file": "p3-01-ch14.md",
        "floor": 18000,
        "sections": ("### 14.9", "### 14.10", "### 14.11", "### 14.12"),
        "examples": 3,
        "figures": 8,
        "tables": 6,
        "quiz": 10,
        "figure_assets": (
            "assets/figures/ch14-error-budget.svg",
            "assets/figures/ch14-power-tree-timing.svg",
            "assets/figures/ch14-test-plan.svg",
            "assets/figures/ch14-pt100-layout.svg",
            "assets/figures/ch14-pt100-journey.svg",
        ),
        "deck": "assets/spice/ch14/pt100.cir",
    },
}


class VisualContractTests(unittest.TestCase):
    def test_print_css_has_chapter_stage_and_figure_frames(self):
        css = (BOOK / "styles" / "print.css").read_text(encoding="utf-8")
        for selector in (
            ".book .chapter-hero",
            ".book .chapter-hero-num",
            ".book .md-typeset figure",
            ".book .md-typeset figcaption",
        ):
            self.assertIn(selector, css)
        self.assertIn("break-inside: avoid", css)


class ChapterContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.quiz = (ROOT / "docs" / "p9-00-quiz.md").read_text(encoding="utf-8")

    def test_contracts_are_well_formed(self):
        for chapter, contract in CHAPTER_CONTRACTS.items():
            self.assertRegex(chapter, r"^\d+$")
            self.assertTrue((ROOT / "docs" / contract["file"]).is_file())
            self.assertGreater(contract["floor"], 0)
            self.assertTrue(contract["sections"])
            self.assertGreater(contract["figures"], 0)
            self.assertGreater(contract["quiz"], 0)

    def test_chapter_word_floor_sections_and_counts(self):
        for chapter, contract in CHAPTER_CONTRACTS.items():
            text = (ROOT / "docs" / contract["file"]).read_text(
                encoding="utf-8")
            chars = len(re.sub(r"\s+", "", text))
            self.assertGreaterEqual(
                chars, contract["floor"],
                f"第 {chapter} 章非空白字符 {chars} < {contract['floor']}")
            for heading in contract["sections"]:
                self.assertIn(heading, text,
                              f"第 {chapter} 章缺少小节 {heading}")
            self.assertEqual(
                contract["figures"], text.count("<figure>"),
                f"第 {chapter} 章 <figure> 数量不符")
            self.assertEqual(
                contract["figures"], text.count("<figcaption>"),
                f"第 {chapter} 章有图无题注")
            self.assertEqual(
                contract["tables"],
                len(re.findall(rf"\*\*表 {chapter}-\d+", text)),
                f"第 {chapter} 章表题数量不符")
            self.assertEqual(
                contract["examples"],
                text.count('class="example-title"'),
                f"第 {chapter} 章算例数量不符")
            for marker in ("TODO", "TBD", "待补", "占位"):
                self.assertNotIn(marker, text)

    def test_chapter_quiz_and_assets(self):
        for chapter, contract in CHAPTER_CONTRACTS.items():
            questions = re.findall(rf'id="q-ch{chapter}-\d+"', self.quiz)
            self.assertEqual(
                contract["quiz"], len(questions),
                f"第 {chapter} 章应有 {contract['quiz']} 道章节题")
            for asset in contract["figure_assets"]:
                path = ROOT / asset
                self.assertTrue(path.is_file(), f"缺少插图 {asset}")
                svg = path.read_text(encoding="utf-8")
                self.assertIn("<svg", svg)
                self.assertIn("<title", svg)
                self.assertNotIn("<script", svg.lower())
                self.assertNotRegex(svg, r'(?:href|src)="https?://')
                self.assertNotRegex(svg, r"url\(https?://")
            deck = ROOT / contract["deck"]
            assertion = deck.with_name("assert.json")
            self.assertTrue(deck.is_file(), f"缺少 deck {contract['deck']}")
            self.assertTrue(assertion.is_file(), "缺少 assert.json")
            spec = json.loads(assertion.read_text(encoding="utf-8"))
            self.assertEqual(deck.name, spec["deck"])
            self.assertEqual({"deck", "analysis", "data", "min_rows",
                              "metrics"}, set(spec))
            self.assertNotIn(".include", deck.read_text(
                encoding="utf-8").lower())


if __name__ == "__main__":
    unittest.main()


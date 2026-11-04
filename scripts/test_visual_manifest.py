#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""manifest 不变量：ID、状态机、评分下限、磁盘覆盖（夹具测试）。"""
import tempfile
import unittest
from pathlib import Path

import check_visual_manifest as chk

VALID = {
    "id": "ch17-demo",
    "chapter": 17,
    "kind": "figure",
    "type": "V3",
    "anchor": "17.0",
    "purpose": "定量图",
    "style_id": "FA-029",
    "layout_id": "IG-012",
    "color_ids": ["C-30"],
    "source_facts": ["docs/p4-02-ch17.md#17.0"],
    "prompt_file": "prompts/ch17-demo.md",
    "output": "assets/figures/ch17-demo.svg",
    "print_fallback": "assets/figures/ch17-demo.svg",
    "status": "generated",
    "review_scores": {},
}


def sandbox() -> tuple[Path, dict]:
    root = Path(tempfile.mkdtemp())
    (root / "docs").mkdir()
    (root / "docs" / "p4-02-ch17.md").write_text(
        "## 17.0\n\n故障占比 41% 与 23%。\n\n"
        '<img src="assets/figures/ch17-demo.svg">\n', encoding="utf-8")
    for sub in ("assets/svg", "assets/figures", "assets/photos",
                "prompts", "docs/superpowers/visual"):
        (root / sub).mkdir(parents=True, exist_ok=True)
    (root / "docs/superpowers/visual/visual-manifest.yml").write_text(
        "", encoding="utf-8")
    (root / "docs/superpowers/visual/handraw-style-lock.md").write_text(
        "-", encoding="utf-8")
    (root / "assets/figures/ch17-demo.svg").write_text("<svg/>", encoding="utf-8")
    (root / "prompts/ch17-demo.md").write_text(
        "---\nid: ch17-demo\ngenerator: deterministic-svg-v1\n"
        "numbers: ['41%']\nzh_prompt: 中文\nen_prompt: English\n---\n",
        encoding="utf-8")
    data = {"meta": {"statuses": chk.STATUSES}, "assets": [dict(VALID)]}
    return root, data


class ManifestTests(unittest.TestCase):
    def setUp(self):
        self.root, self.data = sandbox()
        self._root = chk.ROOT
        chk.ROOT = self.root

    def tearDown(self):
        chk.ROOT = self._root

    def fails(self) -> list[str]:
        return chk.check(self.data)

    def test_valid_entry_passes(self):
        self.assertEqual([], self.fails())

    def test_duplicate_ids_fail(self):
        self.data["assets"].append(dict(VALID))
        self.assertTrue(any("ID 重复" in x for x in self.fails()))

    def test_bad_status_fails(self):
        self.data["assets"][0]["status"] = "done"
        self.assertTrue(any("非法状态" in x for x in self.fails()))

    def test_reviewed_requires_scores(self):
        self.data["assets"][0]["status"] = "reviewed"
        bad = self.fails()
        self.assertTrue(any("评分" in x for x in bad))

    def test_reviewed_with_scores_passes(self):
        a = self.data["assets"][0]
        a["status"] = "accepted"
        a["review_scores"] = {dim: 4 for dim in chk.SCORE_DIMS}
        self.assertEqual([], self.fails())

    def test_animation_requires_motion_dimensions(self):
        a = self.data["assets"][0]
        a["kind"], a["type"] = "animation", "A2"
        a["status"] = "reviewed"
        a["review_scores"] = {dim: 5 for dim in chk.SCORE_DIMS}
        self.assertTrue(any("运动叙事" in x for x in self.fails()))

    def test_missing_output_file_fails(self):
        (self.root / "assets/figures/ch17-demo.svg").unlink()
        self.assertTrue(any("output 不存在" in x for x in self.fails()))

    def test_unregistered_disk_asset_fails(self):
        (self.root / "assets/figures/orphan.svg").write_text(
            "<svg/>", encoding="utf-8")
        self.assertTrue(any("未登记" in x for x in self.fails()))

    def test_legacy_entry_skips_deep_fields(self):
        self.data["assets"] = [{
            "id": "legacy-x", "chapter": 0, "kind": "figure", "type": "V2",
            "output": "assets/figures/ch17-demo.svg",
            "status": "legacy-unreviewed"}]
        self.assertEqual([], self.fails())

    def test_bootstrap_is_idempotent(self):
        self.data["assets"] = []
        added = chk.bootstrap(self.data)
        self.assertEqual(1, added)
        self.assertEqual(0, chk.bootstrap(self.data))
        self.assertEqual("legacy-unreviewed", self.data["assets"][0]["status"])

    def test_bootstrap_infers_chapter_from_docs(self):
        self.data["assets"] = []
        chk.bootstrap(self.data)
        self.assertEqual(17, self.data["assets"][0]["chapter"])


if __name__ == "__main__":
    unittest.main()

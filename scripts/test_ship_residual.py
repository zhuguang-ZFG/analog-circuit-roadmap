#!/usr/bin/env python3
from __future__ import annotations
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import check_ship_residual as residual  # noqa: E402


class ShipResidualTests(unittest.TestCase):
    def test_full_scan_passes_on_current_tree(self):
        issues = []
        issues += residual.check_contract()
        issues += residual.check_slop()
        issues += residual.check_references()
        issues += residual.check_svg_floor()
        issues += residual.check_no_parallel_tree()
        issues += residual.check_five_line_sample()
        self.assertEqual([], issues, issues)

    def test_parallel_tree_detector_fires(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "book-manuscript").mkdir()
            issues = residual.check_no_parallel_tree(root=root)
            self.assertEqual(["发现疑似平行书稿目录：book-manuscript/（spec §3 废止）"], issues)


if __name__ == "__main__":
    unittest.main()

# -*- coding: utf-8 -*-
"""字幕折行回归：坏折行（行首标点/孤标点块/超两行/溢出）清零。

跑法：python -m unittest video.test_subtitles -v
（开发侧测试，未挂 CI；samples/ 时间轴在仓内可直接读）
"""
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from master import wrap, chunk_voice, PUNC  # noqa: E402

SAMPLES = Path(__file__).parent / "samples"


class TestWrap(unittest.TestCase):
    def test_no_line_leading_punctuation(self):
        # 旧实现 17 字硬切会在行首留下 ，。——（避头点）
        lines = wrap("本来电压一路往上爬——爬着爬着，突然不动了。").split("\n")
        for ln in lines:
            self.assertFalse(ln[0] in PUNC, f"行首标点: {ln!r}")

    def test_dash_pair_not_split(self):
        lines = wrap("伏秒平衡——电感一个周期平均电压必须是零").split("\n")
        for ln in lines:
            self.assertFalse(ln[0] in PUNC, f"行首标点: {ln!r}")

    def test_max_two_lines_for_30_char_chunk(self):
        # chunk_voice 上限 30 字 + wrap 宽 16 → 任何块 ≤2 行
        lines = wrap("x" * 30).split("\n")
        self.assertLessEqual(len(lines), 2)

    def test_no_vertical_overflow(self):
        # 最长行 18 字 × 57px + 托板 32px < 1080
        for n in (16, 17, 18, 30):
            for ln in wrap("字" * n).split("\n"):
                self.assertLess(len(ln) * 57 + 32, 1080, f"溢出: {len(ln)} 字")

    def test_ascii_run_not_split(self):
        # 数字不能被拆成 0.0|.01（ep18 实证缺陷）
        board = json.loads((SAMPLES / "ep18-ground-timeline.json").read_text(encoding="utf-8"))
        for chunk in chunk_voice(board["shots"][2]["voice"]):
            lines = wrap(chunk).split("\n")
            for a, b in zip(lines, lines[1:]):
                self.assertFalse(a[-1].isascii() and a[-1].isalnum() and b[0].isalnum(),
                                 f"ASCII 串被拆: {a!r} | {b!r}")


class TestChunkVoice(unittest.TestCase):
    def test_no_orphan_punctuation_chunk(self):
        # ep10 幕5 原实现：逗号前段 33 字硬切 30 后留下孤 "，" 块
        voice = ("续流二极管就是给这份能量一条回家的路——1N4148 几毛钱，"
                 "救一只几十块的管子。")
        for c in chunk_voice(voice):
            self.assertTrue(c.strip(PUNC), f"孤标点块: {c!r}")

    def test_chunks_fit_two_lines(self):
        self.assertLessEqual(max(len(c) for c in chunk_voice("字" * 48)), 32)


class TestAllTimelineSubtitles(unittest.TestCase):
    def test_zero_bad_breaks_across_all_episodes(self):
        bad = []
        for tl in sorted(SAMPLES.glob("*-timeline.json")):
            board = json.loads(tl.read_text(encoding="utf-8"))
            for i, shot in enumerate(board["shots"], 1):
                for chunk in chunk_voice(shot.get("voice", "")):
                    lines = wrap(chunk).split("\n")
                    if any(ln and ln[0] in PUNC for ln in lines):
                        bad.append(f"{tl.name} 幕{i} 行首标点")
                    if len(lines) > 2:
                        bad.append(f"{tl.name} 幕{i} 超两行")
                    if max(len(l) for l in lines) * 57 + 32 >= 1080:
                        bad.append(f"{tl.name} 幕{i} 溢出")
                    if not chunk.strip(PUNC):
                        bad.append(f"{tl.name} 幕{i} 孤标点块")
        self.assertEqual(bad, [])


if __name__ == "__main__":
    unittest.main()

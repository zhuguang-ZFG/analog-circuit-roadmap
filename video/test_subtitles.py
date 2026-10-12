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


class TestSubFont(unittest.TestCase):
    def test_kuaile_default(self):
        from master import sub_font, KUAI_LE
        self.assertIn("ZCOOLKuaiLe", sub_font("本来电压一路往上爬"))

    def test_beta_fallback(self):
        # 快乐体缺 β（全量口播文本覆盖核验的唯一缺字），命中分块回退雅黑
        from master import sub_font, FONT
        self.assertEqual(sub_font("强制 β=10"), FONT.replace("\\", "/").replace(":", "\\:"))


class TestNumCards(unittest.TestCase):
    SHOTS = Path(__file__).parent / "shots"

    def test_from_to_distinct(self):
        # from==to 会让跳数卡显示「990 → 990」（ep12 实证），退化失去冲击力
        bad = []
        for sj in sorted(self.SHOTS.glob("ep*.json")):
            board = json.loads(sj.read_text(encoding="utf-8"))
            for i, s in enumerate(board["shots"], 1):
                if s["type"] == "num" and s.get("from") == s.get("to"):
                    bad.append(f"{board['name']} 幕{i}: {s['from']} -> {s['to']}")
        self.assertEqual(bad, [])


class TestNumRowFit(unittest.TestCase):
    """数字行不出边：全量分镜双尺寸页面级量测（playwright）。
    回归三层历史缺陷：字体解码与量测赛跑（采集端 fonts.ready 门控）、
    跳数 from/to 宽度赛跑（落定值测量）、scrollWidth 低估（改用渲染盒）。"""

    def test_all_num_rows_fit(self):
        from playwright.sync_api import sync_playwright
        sys.path.insert(0, str(Path(__file__).parent))
        import director
        bad = []
        with sync_playwright() as pw:
            browser = pw.chromium.launch(channel="chrome", headless=True)
            try:
                for sj in sorted((Path(__file__).parent / "shots").glob("ep*.json")):
                    board = json.loads(sj.read_text(encoding="utf-8"))
                    if not any(s["type"] == "num" for s in board["shots"]):
                        continue
                    for w, h, cls in ((720, 1280, "v"), (1920, 1080, "h")):
                        html = director.build_html(board, w=w, h=h, cls=cls)
                        page = browser.new_page(viewport={"width": w, "height": h})
                        page.add_init_script("window.__det = true;")
                        page.goto("about:blank")
                        page.set_content(html)
                        page.evaluate("() => document.fonts.ready")
                        t = 0.0
                        for i, s in enumerate(board["shots"], 1):
                            if s["type"] == "num":
                                page.evaluate(f"window.__seek({int((t + s['seconds'] / 2) * 1000)})")
                                r = page.evaluate(
                                    "() => { const q = document.querySelectorAll('.shot.active')[0]"
                                    ".querySelector('.numrow').getBoundingClientRect();"
                                    " return { l: Math.round(q.left), r: Math.round(q.right) }; }")
                                if r["l"] < 2 or r["r"] > w - 2:
                                    bad.append(f"{board['name']} 幕{i} [{cls}]: {r}")
                            t += s["seconds"]
                        page.close()
            finally:
                browser.close()
        self.assertEqual(bad, [])


if __name__ == "__main__":
    unittest.main()

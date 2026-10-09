"""无障碍静态护栏：SVG 的可读名称与描述、图片 alt、减弱动效开关。

Run: python -B -m unittest discover -s scripts -p test_a11y.py -v

为什么需要这组测试：全站 313 张 `<img>` 里有 108 张是自动播放的 SMIL 动画，
而 SVG 自身此前只有 `<title>`、没有 `<desc>`，也没有 `role`/`aria-*`——
读屏用户拿到的是一个"没有名字的图形"。更糟的是 3 张实物图连 `alt` 都没有，
读屏会直接念出文件 URL。

这里把三件事钉成红灯（都不需要浏览器，纯静态检查）：
  1. 每张 SVG 有 role="img" + aria-labelledby + 非空 <title> + 非空 <desc>；
  2. <desc> 里带上这张图自己的节拍字幕（不许串到别的图），
     且描述文案与图内字幕逐字一致；
  3. 每张 SVG 都带 prefers-reduced-motion 块（真行为由
     test_reduced_motion.py 在 Chromium 里验证）；
  4. docs/ 里每个 <img> 都有非空 alt（代码围栏与行内代码里的 `<img>`
     是文档在讲语法，不是真标签，必须先剥掉再查）。
"""
from pathlib import Path
import re
import unittest
import xml.etree.ElementTree as ET
from xml.sax.saxutils import unescape

ROOT = Path(__file__).resolve().parents[1]
SVGS = sorted((ROOT / "assets" / "svg").glob("*.svg"))
DOCS = sorted((ROOT / "docs").glob("*.md"))

TITLE = re.compile(r'<title id="ttl">(.*?)</title>', re.S)
DESC = re.compile(r"<desc>(.*?)</desc>", re.S)
IMG = re.compile(r"<img\b[^>]*>", re.I)
ALT = re.compile(r'\balt="([^"]*)"', re.I)

MOTION_SELECTORS = (
    ":has(> animateMotion):not(:has(text))",
    ":has(> animateTransform):not(:has(text))",
    ':has(> animate:not([attributeName="opacity"])):not(:has(text))',
)


def strip_code(text):
    """剥掉围栏代码块与行内代码——里面的 <img> 是文档在讲语法。"""
    text = re.sub(r"^[ \t]*(```|~~~).*?^[ \t]*\1[ \t]*$", "", text, flags=re.S | re.M)
    return re.sub(r"`[^`\n]*`", "", text)


class SvgAccessibilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = {p.name: p.read_text(encoding="utf-8") for p in SVGS}

    def test_inventory_is_complete(self):
        """防假绿：探针必须真的看到 108 张图。"""
        self.assertGreaterEqual(len(self.sources), 108,
                                "assets/svg 少于 108 张，下面的断言会变成空转")

    def test_every_svg_has_role_name_and_description(self):
        missing = []
        for name, text in self.sources.items():
            title = TITLE.search(text)
            desc = DESC.search(text)
            if 'role="img"' not in text:
                missing.append((name, "role=img"))
            if 'aria-labelledby="ttl"' not in text:
                missing.append((name, "aria-labelledby"))
            if not title or len(title.group(1).strip()) < 6:
                missing.append((name, "title"))
            if not desc or len(desc.group(1).strip()) < 6:
                missing.append((name, "desc"))
        self.assertEqual([], missing, "这些图缺可读名称/描述：" + repr(missing[:10]))

    def test_description_carries_this_diagrams_own_beat_narration(self):
        """<desc> 的节拍必须与图内字幕**逐字相同**。

        只查"desc 里的文案在本文件出现过"是不够的——desc 本身就在文件里，
        断言会永远成立（变异验证时踩过这个坑）。这里改成双向对照：
        从图里抽出节拍字幕组（同时带 animateTransform 子节点与 text 的 <g>，
        正是 caption() 的结构），再要求 desc 的节拍串与它完全相等。
        """
        ns = "{http://www.w3.org/2000/svg}"
        with_beats = 0
        for name, text in self.sources.items():
            root = ET.fromstring(text)
            beats = [t.text.strip()
                     for g in root.iter(ns + "g")
                     if any(c.tag == ns + "animateTransform" for c in g)
                     for t in g.iter(ns + "text")
                     if (t.text or "").strip()]
            if not beats:
                continue
            with_beats += 1
            desc = unescape(DESC.search(text).group(1))
            self.assertIn("节拍：", desc, f"{name} 有 {len(beats)} 条节拍字幕，<desc> 却没写")
            self.assertEqual("；".join(beats), desc.split("节拍：", 1)[1],
                             f"{name} 的 <desc> 与图内字幕对不上（串图或漏抄）")
        self.assertGreaterEqual(with_beats, 90,
                                "带节拍描述的图太少，说明字幕登记（_BEATS）没生效")

    def test_every_svg_ships_the_reduced_motion_block(self):
        missing = [name for name, text in self.sources.items()
                   if "prefers-reduced-motion: reduce" not in text
                   or not all(sel in text for sel in MOTION_SELECTORS)]
        self.assertEqual([], missing, "这些图缺减弱动效块：" + repr(missing[:10]))

    def test_every_docs_image_has_a_non_empty_alt(self):
        offenders = []
        total = 0
        for path in DOCS:
            for tag in IMG.findall(strip_code(path.read_text(encoding="utf-8"))):
                total += 1
                alt = ALT.search(tag)
                if not alt or not alt.group(1).strip():
                    offenders.append((path.name, tag[:80]))
        # docs/ 现有 251 张真 <img>；下限取 240，一旦 strip_code 把真标签也剥掉、
        # 或某页整批图丢失，这里会先红。
        self.assertGreaterEqual(total, 240, f"只扫到 {total} 张图，覆盖面不对")
        self.assertEqual([], offenders, "这些图没有 alt：" + repr(offenders[:6]))


if __name__ == "__main__":
    unittest.main()

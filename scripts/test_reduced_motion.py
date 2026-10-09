"""「减弱动效」在真实 Chromium 里的行为护栏。

Run: python -B -m unittest discover -s scripts -p test_reduced_motion.py -v

为什么需要它：108 张 SVG 全是自动播放的 SMIL 动画，前庭敏感的用户打开站点
没有任何开关能停下来。现在每张图内置了 @media (prefers-reduced-motion: reduce)
块，关掉"会飞"的东西（电流粒子 / 波形游标 / 扫压圆点 / 脉冲辉光圈），
但**保留节拍字幕**——字幕是多路复用的（同一行轮流显示），若一起显示会互相压字，
反而更读不了；同理器件状态变化也保留，那是教学内容本身。

这里用真实 Chromium 断言三件事：
  1. reduce 下，108 张图里**没有任何可见的运动载体**；
  2. reduce 下，**节拍字幕组一个都没被误伤**（仍可见）；
  3. no-preference 下同一个探针必须真能看见大量运动元素 —— 防假绿：
     否则"没漏"可能只是因为选择器根本没命中。
另外验证站点自身的悬停位移在 reduce 下也停掉。
"""
from pathlib import Path
import re
import unittest

from playwright.sync_api import sync_playwright

from build_site import GALLERY_CSS, GALLERY_JS, parse_demos, render_gallery

ROOT = Path(__file__).resolve().parents[1]
SVGS = sorted((ROOT / "assets" / "svg").glob("*.svg"))

# 会「飞」的动画：位移/形变类。opacity 淡入淡出不算运动，节拍字幕靠它分时显示。
PROBE = """() => {
  const motion = 'animateMotion, animateTransform, animate:not([attributeName="opacity"])';
  let carriers = 0, visibleMotion = 0, captions = 0, captionsVisible = 0;
  const samples = [];
  for (const el of document.querySelectorAll('*')) {
    if (!Array.from(el.children).some(k => k.matches(motion))) { continue; }
    carriers += 1;
    const hidden = getComputedStyle(el).display === 'none';
    const hasText = el.querySelector('text') !== null;
    if (hasText) {
      captions += 1;
      if (!hidden) { captionsVisible += 1; }
    } else if (!hidden) {
      visibleMotion += 1;
      if (samples.length < 3) { samples.push(el.tagName + '.' + (el.getAttribute('class') || '-')); }
    }
  }
  return { carriers, visibleMotion, captions, captionsVisible, samples };
}"""


class ReducedMotionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        playwright = sync_playwright().start()
        cls.addClassCleanup(playwright.stop)
        cls.browser = playwright.chromium.launch(channel="chrome", headless=True)
        cls.addClassCleanup(cls.browser.close)
        page = cls.browser.new_page(viewport={"width": 900, "height": 700})
        cls.addClassCleanup(page.close)
        cls.page = page

        cls.report = {}
        for mode in ("no-preference", "reduce"):
            page.emulate_media(reduced_motion=mode)
            rows = {}
            for svg in SVGS:
                page.goto(svg.as_uri())
                rows[svg.name] = page.evaluate(PROBE)
            cls.report[mode] = rows

    def totals(self, mode):
        rows = self.report[mode].values()
        return (sum(r["carriers"] for r in rows),
                sum(r["visibleMotion"] for r in rows),
                sum(r["captions"] for r in rows),
                sum(r["captionsVisible"] for r in rows))

    def test_probe_sees_motion_when_the_user_wants_motion(self):
        """防假绿：默认偏好下必须能看见大量运动载体，否则下面的"没漏"是空转。"""
        carriers, visible, captions, captions_visible = self.totals("no-preference")
        self.assertGreaterEqual(carriers, 1000, f"只找到 {carriers} 个运动载体，探针失效")
        self.assertGreaterEqual(captions, 350, f"只找到 {captions} 个字幕组")
        self.assertEqual(captions, captions_visible, "默认偏好下字幕组不该被隐藏")
        self.assertEqual(carriers - captions, visible,
                         "默认偏好下不该有被隐藏的运动载体："
                         f"{carriers} 个载体 - {captions} 个字幕组 != {visible} 个可见")

    def test_reduced_motion_stops_every_particle_in_every_diagram(self):
        _, visible, _, _ = self.totals("reduce")
        leaked = {name: r["samples"] for name, r in self.report["reduce"].items()
                  if r["visibleMotion"]}
        self.assertEqual(0, visible,
                         f"减弱动效下仍有 {visible} 个运动元素可见：" + repr(list(leaked.items())[:5]))

    def test_reduced_motion_keeps_beat_captions_readable(self):
        _, _, captions, captions_visible = self.totals("reduce")
        self.assertGreaterEqual(captions, 350, f"reduce 下只找到 {captions} 个字幕组")
        self.assertEqual(captions, captions_visible,
                         "减弱动效把节拍字幕也藏掉了——字幕是多路复用的，藏了就整段读不到")

    def test_gallery_cards_do_not_slide_under_reduced_motion(self):
        html = ('<!doctype html><html><head><meta charset="utf-8"><style>'
                + GALLERY_CSS + '</style></head><body>'
                + render_gallery(parse_demos()[0])
                + '<script>' + GALLERY_JS + '</script></body></html>')
        page = self.browser.new_page()
        self.addCleanup(page.close)
        page.route("**/*", lambda route: route.fulfill(
            content_type="text/html" if route.request.resource_type == "document"
            else "image/svg+xml", body=html if route.request.resource_type == "document"
            else '<svg xmlns="http://www.w3.org/2000/svg" width="800" height="580"/>'))
        for mode, expect in (("no-preference", "matrix"), ("reduce", "none")):
            page.emulate_media(reduced_motion=mode)
            page.goto("https://gallery.test/gallery.html")
            card = page.locator(".gal-card").first
            card.hover()
            transform = card.evaluate("el => getComputedStyle(el).transform")
            if expect == "none":
                self.assertEqual("none", transform,
                                 "减弱动效下卡片悬停仍会位移：" + transform)
            else:
                self.assertTrue(re.search(r"matrix|translate", transform),
                                "默认偏好下卡片悬停位移消失了，测试失去意义：" + transform)


if __name__ == "__main__":
    unittest.main()

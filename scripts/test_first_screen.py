"""首屏（顶栏 + 首页 hero）的视觉护栏 —— 这些只能在浏览器里验。

Run: python -B -m unittest discover -s scripts -p test_first_screen.py -v

为什么不能靠静态检查：
  1. **hero 皮肤有没有真的贴上**。`reading.css` 里 hero 的底色是
     `background-color` + `background-image` 分开写的 —— 一旦有人改回
     `background:` **简写**，background-image（品牌渐变 + 蓝图点阵）会被整个重置成
     none，而页面**照样能构建、照样不报错**，只是首屏变回一块灰底。
     实测踩过：typography.css 里写的同一批规则被 reading.css 的简写覆盖掉了。
  2. **chip 文字在暗色主题下读不读得出**。chip 文字色是 `color-mix` 掺出来的，
     而 `--md-primary-fg-color` 在暗色主题下**不变**（仍是 #4051b5），直接拿它当
     文字色压在本站深靛底色上只有 2.56:1。色值算得对不对，只有量像素才知道。
  3. **四个 chip 会不会掉行**。Material 有一条 `[dir=ltr] .md-typeset ul li
     {margin-left:1.25em}`，特异性 (0,2,2) 比 `.md-typeset .learning-stats > li`
     的 (0,2,1) 高 —— 每个 chip 会凭空多 17.5px 左外边距（四个共 70px），
     刚好把第四枚挤到第二行。这类「差 1px」的排版事故静态查不出来。
  4. **顶栏那两处**（品牌标识是描边还是实心盘、仓库链接有没有被截断）同样是
     纯 CSS 计算结果：Material 的 `.md-header__button.md-logo :is(img,svg)
     {fill:currentcolor}` 会压掉根 <svg> 上的 fill 属性，而 `.md-header__source`
     在桌面上宽度写死 11.5rem、跟视口无关。两条都是「构建不报错、只有人看得见」。

对比度口径：截图取元素区域，**众数色当底色、离底色最远的像素当字芯**，
按 WCAG 算比值，正文级要求 ≥4.5（比 SVG 那套 ≥3.0 严，因为 chip 是正文字号）。
"""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from collections import Counter
import io
import shutil
import subprocess
import sys
import tempfile
import threading
import unittest

from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]

# 正文字号的门槛（WCAG AA）。SVG 那套用 3.0 是因为图里的标注算"大号图形文字"。
MIN_RATIO = 4.5

# 顶栏 logo 框里「接近白色」的像素占比上限。实测：描边 0.198、实心盘 0.535。
LOGO_MAX_INK = 0.35


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *_):
        pass


def _luminance(rgb):
    def channel(value):
        v = value / 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    return 0.2126 * channel(rgb[0]) + 0.7152 * channel(rgb[1]) + 0.0722 * channel(rgb[2])


def contrast(a, b):
    la, lb = _luminance(a), _luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def measured_contrast(page, selector):
    """截取元素区域，众数色=底、离底最远的像素=字芯，返回 (底, 字, 比值)。"""
    box = page.eval_on_selector(selector, "e => e.getBoundingClientRect().toJSON()")
    shot = page.screenshot(clip={"x": box["x"], "y": box["y"],
                                 "width": box["width"], "height": box["height"]})
    pixels = list(Image.open(io.BytesIO(shot)).convert("RGB").get_flattened_data())
    background = Counter(pixels).most_common(1)[0][0]
    glyph = max(pixels, key=lambda c: sum((c[i] - background[i]) ** 2 for i in range(3)))
    return background, glyph, contrast(background, glyph)


def ink_fraction(page, selector, threshold=190):
    """元素区域里「接近白色」的像素占比 —— 用来分辨「描边图形」与「实心色块」。"""
    box = page.eval_on_selector(selector, "e => e.getBoundingClientRect().toJSON()")
    shot = page.screenshot(clip={"x": box["x"], "y": box["y"],
                                 "width": box["width"], "height": box["height"]})
    pixels = list(Image.open(io.BytesIO(shot)).convert("RGB").get_flattened_data())
    white = sum(1 for pixel in pixels if min(pixel) > threshold)
    return white / max(1, len(pixels))


class FirstScreenTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        temporary = tempfile.TemporaryDirectory(prefix="analog-hero-")
        cls.addClassCleanup(temporary.cleanup)
        work = Path(temporary.name)
        for folder in ("docs", "assets", "scripts"):
            shutil.copytree(ROOT / folder, work / folder,
                            ignore=shutil.ignore_patterns("__pycache__", "_probe*"))
        for filename in ("CONTRIBUTING.md", "CONTRIBUTORS.md", "LICENSE"):
            shutil.copyfile(ROOT / filename, work / filename)
        result = subprocess.run([sys.executable, "-X", "utf8", "scripts/build_site.py", "--build"],
                                cwd=work, capture_output=True, text=True,
                                encoding="utf-8", errors="replace", timeout=300)
        if result.returncode:
            raise RuntimeError(result.stdout + result.stderr)
        server = ThreadingHTTPServer(("127.0.0.1", 0),
                                     partial(QuietHandler, directory=str(work / "build")))
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        cls.addClassCleanup(lambda: (server.shutdown(), server.server_close(), thread.join(5)))
        cls.base = f"http://127.0.0.1:{server.server_port}/site/"
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch(channel="chrome")
        cls.addClassCleanup(cls.playwright.stop)
        cls.addClassCleanup(cls.browser.close)

    def homepage(self, scheme="light", width=1280, height=900):
        context = self.browser.new_context(viewport={"width": width, "height": height},
                                           color_scheme=scheme)
        self.addCleanup(context.close)
        page = context.new_page()
        page.goto(self.base + "index.html", wait_until="load")
        page.wait_for_timeout(700)   # 等字体与渐变铺好
        return page

    # ---------- ① 皮肤真的贴上了 ----------
    def test_hero_skin_is_not_reset_by_a_background_shorthand(self):
        """品牌渐变 + 蓝图点阵必须真的画出来（`background:` 简写会把它重置成 none）。"""
        for scheme in ("light", "dark"):
            with self.subTest(scheme=scheme):
                page = self.homepage(scheme)
                skin = page.evaluate("""() => {
                  const hero = document.querySelector('.learning-hero');
                  const cs = getComputedStyle(hero);
                  const before = getComputedStyle(hero, '::before');
                  return {image: cs.backgroundImage, shadow: cs.boxShadow,
                          isolation: cs.isolation, glow: before.backgroundImage,
                          glowZ: before.zIndex, dots: cs.backgroundSize};
                }""")
                self.assertNotEqual("none", skin["image"],
                                    "hero 的 background-image 被重置了（多半是改回了 background 简写）")
                self.assertIn("radial-gradient", skin["image"], "蓝图点阵丢了")
                self.assertIn("linear-gradient", skin["image"], "品牌渐变丢了")
                self.assertNotEqual("none", skin["shadow"], "hero 的投影丢了")
                self.assertIn("radial-gradient", skin["glow"], "右上角辉光（::before）丢了")
                # 辉光必须压在文字之下，否则会盖住标题
                self.assertEqual("-1", skin["glowZ"], "辉光的 z-index 变了，可能盖住文字")
                self.assertEqual("isolate", skin["isolation"],
                                 "少了 isolation:isolate，z-index:-1 会跑到页面底板后面")

    # ---------- ② 文字读得出来 ----------
    def test_hero_text_meets_body_contrast_in_both_themes(self):
        """chip 文字与 eyebrow 在明暗两套主题下都必须 ≥4.5。

        暗色主题是重灾区：`--md-primary-fg-color` 在 slate 下**不变**，
        直接拿它当文字色只有 2.56:1。修法是改用随主题变化的
        `--md-typeset-a-color`，再掺四成正文色兜底。
        """
        targets = [("chip 文字", ".learning-stats > li"),
                   ("eyebrow", ".learning-eyebrow")]
        for scheme in ("light", "dark"):
            page = self.homepage(scheme)
            for name, selector in targets:
                with self.subTest(scheme=scheme, target=name):
                    background, glyph, ratio = measured_contrast(page, selector)
                    self.assertGreaterEqual(
                        ratio, MIN_RATIO,
                        f"{scheme} 主题下 {name} 对比度只有 {ratio:.2f}（底={background} 字={glyph}），"
                        f"低于正文级 {MIN_RATIO}")

    # ---------- ③ chip 不掉行、不溢出 ----------
    def test_chips_share_one_row_and_never_overflow(self):
        """桌面宽度下四个 chip 同处一行；手机上换行但不产生横向滚动。

        桌面必须**同一行**是刻意的：Material 的 `[dir=ltr] .md-typeset ul li
        {margin-left:1.25em}` 会给每个 chip 加 17.5px 左外边距，把第四枚挤下去 ——
        选择器写成 `ul.learning-stats:not([hidden])`（特异性 0,3,1）才压得住它。
        """
        for width in (1280, 1024):
            with self.subTest(width=width):
                page = self.homepage(width=width)
                rows = page.evaluate("""() => {
                  const ul = document.querySelector('.learning-stats');
                  const tops = [...ul.children].map(e => Math.round(e.getBoundingClientRect().top));
                  return {rows: new Set(tops).size, count: ul.children.length,
                          marginLeft: getComputedStyle(ul.children[0]).marginLeft};
                }""")
                self.assertEqual(4, rows["count"], "规模清单应恰好四项")
                self.assertEqual("0px", rows["marginLeft"],
                                 "chip 被 Material 的 li 左外边距推开了（选择器特异性不够）")
                self.assertEqual(1, rows["rows"], f"{width}px 下 chip 掉到了多行")

        page = self.homepage(width=390)
        overflow = page.evaluate(
            "() => document.documentElement.scrollWidth > window.innerWidth + 1")
        self.assertFalse(overflow, "手机宽度下 chip 撑出了横向滚动")

    # ---------- ④ 顶栏品牌（每页都有，属于首屏的一部分） ----------
    def test_header_logo_is_an_outline_not_a_filled_disc(self):
        """顶栏标识必须是「圈 + 正弦」的**描边**，不能糊成一个实心圆盘。

        为什么专门钉这个：Material 有
        `.md-header__button.md-logo :is(img,svg){fill:currentcolor}` —— CSS 声明
        压得过根 <svg> 上的 `fill="none"`（呈现属性优先级最低）。所以只要有人把
        `fill="none"` 从**子元素**挪到根元素上（看起来更「整洁」），圆就变成实心盘。
        构建不报错、静态检查也看不出来，只有人眼发现「logo 变成一个白点」。

        实测 24×24 的 logo 框：描边时白像素占比 0.198，实心盘 0.535 ——
        门槛取 0.35，两边都留足余量。
        """
        for scheme in ("light", "dark"):
            with self.subTest(scheme=scheme):
                page = self.homepage(scheme)
                size = page.eval_on_selector(
                    ".md-header__button.md-logo svg",
                    "e => { const r = e.getBoundingClientRect();"
                    "       return {w: r.width, h: r.height}; }")
                self.assertGreater(size["w"], 8, "顶栏标识没渲染出来")
                ink = ink_fraction(page, ".md-header__button.md-logo svg")
                self.assertLess(
                    ink, LOGO_MAX_INK,
                    f"{scheme} 主题下顶栏标识有 {ink:.3f} 的像素是白的（上限 {LOGO_MAX_INK}）——"
                    "多半是 fill=\"none\" 被挪到根 <svg> 上、又被 Material 的 "
                    "fill:currentcolor 覆盖了，圈糊成了实心盘")

    def test_header_repo_link_is_not_truncated(self):
        """顶栏右上角的仓库链接不能被截断。

        Material 给 `.md-header__source` 的宽度在桌面上是**写死的 11.5rem**，
        跟视口宽度无关 —— 所以写全路径 `zhuguang-ZFG/analog-circuit-roadmap`
        会被 CSS 截成 `zhuguang-ZFG/analog-ci…`：每页顶栏都挂着一个省略号。
        这里直接比 scrollWidth 与 clientWidth（截断时前者更大）。
        """
        for width in (1440, 1280, 1024):
            with self.subTest(width=width):
                page = self.homepage(width=width)
                box = page.evaluate("""() => {
                  const e = document.querySelector('.md-source__repository');
                  return {scroll: e.scrollWidth, client: e.clientWidth,
                          text: e.textContent.trim()};
                }""")
                self.assertTrue(box["text"], "顶栏仓库链接是空的")
                self.assertLessEqual(
                    box["scroll"], box["client"] + 1,
                    f"{width}px 下仓库链接「{box['text']}」被截断了"
                    f"（内容 {box['scroll']}px > 容器 {box['client']}px）")

    def test_header_text_meets_body_contrast_in_both_themes(self):
        """顶栏的站点标题与仓库链接在明暗两套主题下都要 ≥4.5。

        顶栏底色是固定的品牌色（`--md-primary-fg-color` 在 slate 下也不变），
        文字是白色 —— 理论上够用，但这条线此前**没有任何测试覆盖**
        （SVG 那套管的是图里的文字，hero 那套管的是首页正文）。
        """
        targets = [("站点标题", ".md-header__title"),
                   ("仓库链接", ".md-source__repository")]
        for scheme in ("light", "dark"):
            page = self.homepage(scheme)
            for name, selector in targets:
                with self.subTest(scheme=scheme, target=name):
                    background, glyph, ratio = measured_contrast(page, selector)
                    self.assertGreaterEqual(
                        ratio, MIN_RATIO,
                        f"{scheme} 主题下顶栏{name}对比度只有 {ratio:.2f}"
                        f"（底={background} 字={glyph}），低于正文级 {MIN_RATIO}")


if __name__ == "__main__":
    unittest.main()

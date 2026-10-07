"""在临时目录里跑一遍 build_site.py，检查生成的站点源是否自洽。

Run: python -B -m unittest discover -s scripts -p test_site_build.py -v

为什么要这组测试：`build_site.py` 里有一批"静默失效"的正则（DEMO_LINK、DEMO_IMG、
CHAPTER_ROW）。docs/ 迁移成多页后，`DEMO_LINK` 只认 `](#demoN)`、认不出
`(p5-00-part5.md#demoN)`，结果画廊的章节筛选 chips 全部消失——页面照样生成、
构建照样成功，只有人肉点开才发现。这里把这类漂移变成红灯。

只用标准库；mkdocs.yml 的重复键检查需要 PyYAML（随 mkdocs-material 一起装）。
"""
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
PART5 = "p5-00-part5.md"

DEMO_HEAD = re.compile(r'^## (5\.\d+)\s+(.+?)\s*<a id="(demo\d+)"')
ANCHOR = re.compile(r'<a\s+id="(demo\d+)"')
CHAPTER_ROW = re.compile(r"^\|\s*§(\d+)\s+(第\s*\d+\s*章[^|]*?)\s*\|")
DEMO_LINK = re.compile(r"\[(5\.\d+)\]\((?:[\w\-]+\.md)?#(demo\d+)\)")

CARD = re.compile(
    r'<div class="gal-card" data-ch="([^"]*)" data-title="([^"]*)" data-file="([^"]*)">\s*'
    r'<a href="([^"]+)"[^>]*>\s*<img src="([^"]+)"[^>]*>\s*'
    r'<div class="gal-meta">\s*<div class="gal-title">([^<]*)</div>\s*'
    r'<div class="gal-tag">([^<]*)</div>\s*</div>\s*</a>\s*'
    r'<div class="gal-actions">\s*<button class="gal-play"[^>]*data-svg="([^"]+)"\s*'
    r'data-title="([^"]*)" data-href="([^"]*)"[^>]*>')
CHIP = re.compile(r'<button class="gal-chip" data-ch="([^"]*)" aria-pressed="[^"]*">([^<]*)</button>')


class SiteBuildTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        temporary = tempfile.TemporaryDirectory(prefix="analog-site-parity-")
        cls.addClassCleanup(temporary.cleanup)
        work = Path(temporary.name)
        cls.work = work
        (work / "scripts").mkdir()
        shutil.copyfile(ROOT / "scripts" / "build_site.py", work / "scripts" / "build_site.py")
        shutil.copytree(ROOT / "docs", work / "docs")
        shutil.copytree(ROOT / "assets", work / "assets")
        for extra in ("CONTRIBUTING.md", "CONTRIBUTORS.md"):
            src = ROOT / extra
            if src.exists():
                shutil.copyfile(src, work / extra)

        result = subprocess.run(
            [sys.executable, "-B", str(work / "scripts" / "build_site.py")],
            cwd=str(work), capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=180,
        )
        if result.returncode:
            raise RuntimeError("build_site.py failed:\n" + result.stdout + result.stderr)
        cls.stdout = result.stdout
        cls.out = work / "build" / "docs"
        cls.build = work / "build"
        if not cls.out.is_dir():
            raise AssertionError("build_site.py 没有产出 build/docs")

        cls.gallery = (cls.out / "gallery.md").read_text(encoding="utf-8")
        cls.part5 = (work / "docs" / PART5).read_text(encoding="utf-8")
        cls.cards = CARD.findall(cls.gallery)
        cls.chips = CHIP.findall(cls.gallery)

    # ---------- 画廊卡片 ----------
    def test_card_inventory_matches_animation_headings(self):
        """卡片数必须等于第 5 篇里带 demo 锚点的动画条目数。"""
        expected = [m.group(3) for m in map(DEMO_HEAD.match, self.part5.split("\n")) if m]
        self.assertEqual(len(expected), len(self.cards),
                         "画廊卡片数与 p5-00-part5.md 的动画条目数不一致")
        got = [c[3].rsplit("#", 1)[-1] for c in self.cards]
        self.assertEqual(sorted(expected, key=self._n), sorted(got, key=self._n),
                         "卡片锚点集合与动画条目锚点集合不一致")

    def test_every_card_has_a_chapter(self):
        """每张卡片都要能归到某一章——这条专门守住 DEMO_LINK 正则漂移。"""
        blank = [c[1] for c in self.cards if not c[0].strip()]
        self.assertEqual([], blank, "有卡片没有 data-ch（章节筛选会漏掉它们）")
        bad = [c[0] for c in self.cards if not c[0].isdigit()]
        self.assertEqual([], bad, "data-ch 必须是章号")

    def test_card_chapters_match_the_index_table(self):
        """卡片归属的章集合 == 第 5 篇速查索引表里列出的章集合。"""
        indexed = set()
        for ln in self.part5.split("\n"):
            m = CHAPTER_ROW.match(ln)
            if m and DEMO_LINK.search(ln):
                indexed.add(m.group(1))
        got = {c[0] for c in self.cards}
        self.assertEqual(indexed, got,
                         "索引表章集合 %s != 卡片章集合 %s" % (sorted(indexed), sorted(got)))

    def test_every_card_svg_exists(self):
        for ch, _t, f, _h, img, *_ in self.cards:
            with self.subTest(card=f):
                self.assertTrue(f, "data-file 为空")
                self.assertEqual("assets/svg/%s" % f, img, "data-file 与 img src 不一致")
                self.assertTrue((self.out / "assets" / "svg" / f).is_file(),
                                "卡片引用的 SVG 不存在：%s" % f)

    def test_every_card_anchor_exists(self):
        anchors = set(ANCHOR.findall(self.part5))
        for ch, _t, f, href, *_ in self.cards:
            with self.subTest(card=f):
                self.assertTrue(href.startswith("p5-00-part5.html#"),
                                "卡片链接必须指向第 5 篇的锚点：%s" % href)
                self.assertIn(href.rsplit("#", 1)[-1], anchors,
                              "卡片锚点不存在：%s" % href)

    def test_every_card_has_a_play_button(self):
        """卡片数 == 放大播放按钮数（lightbox 与卡片一一对应）。"""
        plays = re.findall(r'<button class="gal-play"[^>]*data-svg="([^"]+)"', self.gallery)
        self.assertEqual(len(self.cards), len(plays))
        for ch, _t, f, href, _img, *_rest in self.cards:
            with self.subTest(card=f):
                self.assertEqual("assets/svg/%s" % f, plays[[c[2] for c in self.cards].index(f)])

    def test_lightbox_is_wired(self):
        for needle in ('id="gal-modal"', 'id="gal-modal-img"', 'id="gal-modal-title"',
                       'id="gal-modal-link"', 'id="gal-modal-close"'):
            self.assertIn(needle, self.gallery, "画廊缺少 lightbox 结构：%s" % needle)
        js = (self.out / "javascripts" / "gallery.js").read_text(encoding="utf-8")
        for needle in ("gal-play", "gal-modal", "Escape"):
            self.assertIn(needle, js, "gallery.js 缺少 lightbox 逻辑：%s" % needle)

    def test_lightbox_prev_next_and_keyboard(self):
        for needle in ('id="gal-modal-prev"', 'id="gal-modal-next"', 'id="gal-modal-pos"'):
            self.assertIn(needle, self.gallery, "lightbox 缺少翻页结构：%s" % needle)
        js = (self.out / "javascripts" / "gallery.js").read_text(encoding="utf-8")
        for needle in ("ArrowLeft", "ArrowRight", "gal-modal-prev", "gal-modal-next"):
            self.assertIn(needle, js, "gallery.js 缺少翻页/键盘逻辑：%s" % needle)

    def test_filter_state_is_shareable(self):
        """筛选状态要能写进地址栏（?ch=&q=），否则分享出去的链接会丢掉筛选。"""
        js = (self.out / "javascripts" / "gallery.js").read_text(encoding="utf-8")
        self.assertIn("URLSearchParams", js)
        self.assertIn("replaceState", js)
        self.assertIn("?ch=", self.gallery)
        for needle in ('id="gal-random"', "gal-random"):
            self.assertIn(needle, self.gallery if needle.startswith("id=") else js)

    def test_card_images_reserve_space(self):
        """<img> 必须带真实 width/height（否则 102 张图会让画廊疯狂抖动）。"""
        pat = re.compile(r'<img src="(assets/svg/[\w\-]+\.svg)"[^>]*?width="(\d+)" height="(\d+)"')
        found = pat.findall(self.gallery)
        self.assertEqual(len(self.cards), len(found),
                         "有卡片图片没写 width/height")
        for src, w, h in found:
            with self.subTest(svg=src):
                head = (self.out / src).read_text(encoding="utf-8", errors="replace")[:600]
                m = re.search(r'<svg[^>]*\bwidth="(\d+)"\s+height="(\d+)"', head)
                self.assertIsNotNone(m, "SVG 里读不到画布尺寸")
                self.assertEqual((w, h), (m.group(1), m.group(2)),
                                 "卡片上的 width/height 与 SVG 画布不一致")

    # ---------- 筛选 chips ----------
    def test_chips_cover_all_and_every_chapter(self):
        self.assertEqual("all", self.chips[0][0], "第一个 chip 必须是「全部」")
        self.assertEqual(1, len([c for c in self.chips if c[0] == "all"]))
        chip_ch = [c[0] for c in self.chips[1:]]
        self.assertEqual(sorted(chip_ch, key=int), sorted({c[0] for c in self.cards}, key=int),
                         "每个出现过的章都要有一个 chip")
        self.assertEqual(len(chip_ch), len(set(chip_ch)), "chip 重复")

    def test_chip_counts_sum_to_card_total(self):
        total = sum(int(re.search(r"(\d+)\s*$", label).group(1))
                    for _ch, label in self.chips if _ch != "all")
        self.assertEqual(len(self.cards), total, "各章 chip 上的数字之和 != 卡片总数")
        all_label = [l for c, l in self.chips if c == "all"][0]
        self.assertEqual(len(self.cards), int(re.search(r"(\d+)", all_label).group(1)))

    # ---------- 导航与配置 ----------
    def test_nav_covers_every_content_page(self):
        nav = (self.build / "mkdocs.yml").read_text(encoding="utf-8")
        pages = [p.name for p in sorted(self.out.glob("*.md"))
                 if p.name not in {"gallery.md", "CONTRIBUTING.md", "CONTRIBUTORS.md"}]
        missing = [p for p in pages if p not in nav]
        self.assertEqual([], missing, "这些页面没进侧栏导航：%s" % missing)
        for extra in ("gallery.md", "CONTRIBUTING.md", "CONTRIBUTORS.md"):
            self.assertIn(extra, nav, "%s 没进导航" % extra)

    def test_no_placeholders_left(self):
        nav = (self.build / "mkdocs.yml").read_text(encoding="utf-8")
        self.assertNotIn("__NAV__", nav)
        main = (self.build / "overrides" / "main.html").read_text(encoding="utf-8")
        self.assertNotIn("__OG_IMAGE__", main)
        self.assertIn("og:image", main)

    def test_mkdocs_yml_has_no_duplicate_keys(self):
        """重复键（例如被复制粘贴两遍的 use_directory_urls）必须报错，而不是静默取最后一个。"""
        try:
            import yaml
        except ImportError:  # pragma: no cover - 站点构建 job 会装 PyYAML
            self.skipTest("PyYAML 未安装")

        class DupCheck(yaml.SafeLoader):
            pass

        def construct_mapping(loader, node, deep=False):
            mapping = {}
            for key_node, value_node in node.value:
                key = loader.construct_object(key_node, deep=deep)
                if key in mapping:
                    raise AssertionError("mkdocs.yml 第 %d 行有重复键：%r"
                                         % (key_node.start_mark.line + 1, key))
                mapping[key] = loader.construct_object(value_node, deep=deep)
            return mapping

        DupCheck.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, construct_mapping)
        DupCheck.add_multi_constructor("tag:yaml.org,2002:python/name:", lambda l, s, n: None)
        text = (self.build / "mkdocs.yml").read_text(encoding="utf-8")
        cfg = yaml.load(text, Loader=DupCheck)
        self.assertEqual("https://zhuguang-ZFG.github.io/analog-circuit-roadmap/", cfg["site_url"])
        self.assertIn("edit_uri", cfg)
        self.assertEqual("overrides", cfg["theme"]["custom_dir"])
        self.assertIn("content.action.edit", cfg["theme"]["features"])

    def test_seo_files(self):
        robots = (self.out / "robots.txt").read_text(encoding="utf-8")
        self.assertIn("Sitemap: https://zhuguang-ZFG.github.io/analog-circuit-roadmap/sitemap.xml",
                      robots)

    # ---------- 共建页脚 ----------
    def test_feedback_footer_on_every_page(self):
        for page in sorted(self.out.glob("*.md")):
            with self.subTest(page=page.name):
                text = page.read_text(encoding="utf-8")
                self.assertIn("issues/new?template=content-fix.yml", text)
                self.assertIn("issues/new?template=new-topic.yml", text)

    def test_docs_stay_clean(self):
        """页脚 / lightbox 只进站点产物，docs/ 里不能出现这些标记。"""
        for page in sorted((self.work / "docs").glob("*.md")):
            with self.subTest(page=page.name):
                text = page.read_text(encoding="utf-8")
                self.assertNotIn("issues/new?template=content-fix.yml", text)
                self.assertNotIn("gal-card", text)

    # ---------- 辅助 ----------
    @staticmethod
    def _n(demo_anchor):
        return int(re.sub(r"\D", "", demo_anchor))


if __name__ == "__main__":
    unittest.main()

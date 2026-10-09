"""在临时目录里跑一遍 build_site.py，检查生成的站点源是否自洽。

Run: python -B -m unittest discover -s scripts -p test_site_build.py -v

为什么要这组测试：`build_site.py` 里有一批"静默失效"的正则（DEMO_LINK、DEMO_IMG、
CHAPTER_ROW）。docs/ 迁移成多页后，`DEMO_LINK` 只认 `](#demoN)`、认不出
`(p5-00-part5.md#demoN)`，结果画廊的章节筛选 chips 全部消失——页面照样生成、
构建照样成功，只有人肉点开才发现。这里把这类漂移变成红灯。

只用标准库；mkdocs.yml 的重复键检查需要 PyYAML（随 mkdocs-material 一起装）。
"""
from pathlib import Path
import json
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
    r'<a href="([^"]+)"[^>]*>\s*'
    # 动画 <img> 现在包在 <picture> 里（<source media> 负责挑「减弱动效」的静止版）；
    # 用非捕获组，保持下面的分组下标不变。
    r'(?:<picture><source srcset="[^"]+"\s+media="[^"]*">)?'
    r'<img src="([^"]+)"[^>]*>\s*'
    r'(?:</picture>\s*)?'
    r'<div class="gal-meta">\s*<div class="gal-title">([^<]*)</div>\s*'
    r'<div class="gal-tag">([^<]*)</div>\s*</div>\s*</a>\s*'
    r'<div class="gal-actions">\s*<button class="gal-play"[^>]*data-svg="([^"]+)"\s*'
    r'data-title="([^"]*)" data-href="([^"]*)"[^>]*>')
CHIP = re.compile(r'<button class="gal-chip" data-ch="([^"]*)" aria-pressed="[^"]*">([^<]*)</button>')

# 篇级落地页 → 子页文件名前缀：落地页必须把本篇每个子页都链接一遍
PART_LANDING_PREFIX = {
    "p1-00-part1.md": "p1-", "p2-00-part2.md": "p2-", "p3-00-part3.md": "p3-",
    "p4-00-part4.md": "p4-", "p6-00-part6.md": "p6-", "p7-00-part7.md": "p7-",
    "p8-00-part8.md": "p8-",
}


class SiteBuildTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        temporary = tempfile.TemporaryDirectory(prefix="analog-site-parity-")
        cls.addClassCleanup(temporary.cleanup)
        work = Path(temporary.name)
        cls.work = work
        (work / "scripts").mkdir()
        shutil.copyfile(ROOT / "scripts" / "build_site.py", work / "scripts" / "build_site.py")
        shutil.copytree(ROOT / "scripts" / "site_media", work / "scripts" / "site_media")
        shutil.copytree(ROOT / "docs", work / "docs")
        shutil.copytree(ROOT / "assets", work / "assets")
        for extra in ("CONTRIBUTING.md", "CONTRIBUTORS.md", "LICENSE"):
            src = ROOT / extra
            if src.exists():
                shutil.copyfile(src, work / extra)

        result = subprocess.run(
            [sys.executable, "-B", str(work / "scripts" / "build_site.py"), "--build"],
            cwd=str(work), capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=600,
        )
        if result.returncode:
            raise RuntimeError("build_site.py failed:\n" + result.stdout + result.stderr)
        cls.stdout = result.stdout
        cls.out = work / "build" / "docs"
        cls.build = work / "build"
        cls.site = work / "build" / "site"
        if not cls.out.is_dir():
            raise AssertionError("build_site.py 没有产出 build/docs")
        if not cls.site.is_dir():
            raise AssertionError("build_site.py --build 没有产出 build/site")

        cls.gallery = (cls.out / "gallery.md").read_text(encoding="utf-8")
        cls.part5 = (work / "docs" / PART5).read_text(encoding="utf-8")
        cls._part5_built = (cls.out / PART5).read_text(encoding="utf-8")
        cls.cards = CARD.findall(cls.gallery)
        cls.chips = CHIP.findall(cls.gallery)
        cls._rendered = {}

    def rendered(self, name):
        """按需读取渲染后的 HTML（62 页全读一遍也就几 MB，读一次就缓存）。"""
        if name not in self._rendered:
            self._rendered[name] = (self.site / name).read_text(encoding="utf-8")
        return self._rendered[name]

    def body_html(self, name):
        """只取 <article class="md-content__inner"> 里的正文，避开导航/目录里的同名文字。"""
        text = self.rendered(name)
        i = text.find('<article class="md-content__inner')
        j = text.find("</article>", i)
        return text[i:j] if i >= 0 and j > i else text

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

    def test_animation_images_are_lazy_and_reserve_space(self):
        """第五篇一页嵌 102 张 SVG（约 1.9MB）：必须懒加载，且按画布比例写 height 防抖动。"""
        pat = re.compile(r'<img src="assets/svg/([\w\-]+\.svg)"[^>]*?>')
        tags = pat.findall(self._part5_built)
        self.assertGreaterEqual(len(tags), 100, "第五篇的动画 <img> 数量异常")
        for m in pat.finditer(self._part5_built):
            tag, name = m.group(0), m.group(1)
            with self.subTest(svg=name):
                self.assertIn('loading="lazy"', tag, "动画图片缺 loading=lazy")
                self.assertIn('decoding="async"', tag, "动画图片缺 decoding=async")
                hm = re.search(r'\bheight="(\d+)"', tag)
                wm = re.search(r'\bwidth="(\d+)"', tag)
                self.assertIsNotNone(hm, "动画图片缺 height（会整页抖动）")
                head = (self.out / "assets" / "svg" / name).read_text(encoding="utf-8",
                                                                     errors="replace")[:600]
                sm = re.search(r'<svg[^>]*\bwidth="(\d+)"\s+height="(\d+)"', head)
                self.assertIsNotNone(sm, "SVG 里读不到画布尺寸")
                ratio = int(sm.group(2)) / int(sm.group(1))
                expect = round(int(wm.group(1)) * ratio)
                self.assertLessEqual(abs(int(hm.group(1)) - expect), 1,
                                     f"height 与画布比例不符（{hm.group(1)} vs {expect}）")

    # ---------- 减弱动效（<picture> 选源） ----------
    def test_every_animation_image_is_wrapped_in_a_reduce_picture(self):
        """每个动画 <img> 都要包进 <picture>，且 <source> 指向静止版。

        为什么必须由页面选源：SVG 作为 `<img>` 载入时 Chrome 把
        `prefers-reduced-motion` **恒判为 reduce**，所以 SVG 内部的 media query
        是恒真/恒假的（v3.45 因此把全站动画冻住过）。`<source media>` 在页面
        上下文里求值，才是准的。漏包一个，那张图在「减弱动效」下就照常乱飞。
        """
        for page in (PART5, "gallery.md"):
            text = (self.out / page).read_text(encoding="utf-8")
            imgs = re.findall(r'<img src="assets/svg/[\w\-]+\.svg"[^>]*>', text)
            wrapped = re.findall(
                r'<picture><source srcset="assets/svg/[\w\-]+\.reduce\.svg" '
                r'media="\(prefers-reduced-motion: reduce\)">'
                r'<img src="assets/svg/[\w\-]+\.svg"[^>]*></picture>', text)
            with self.subTest(page=page):
                self.assertGreaterEqual(len(imgs), 100, f"{page} 的动画图太少，覆盖面不对")
                self.assertEqual(len(imgs), len(wrapped),
                                 f"{page} 有 {len(imgs) - len(wrapped)} 张动画图没包 <picture>")

    def test_reduce_variants_exist_and_actually_freeze_the_particles(self):
        """每个静止版都要真的存在，且带上无条件生效的三条运动选择器。

        静止版由 build_site.py 从动画版追加 REDUCE_CSS 生成；这里同时守住
        「文件确实生成了」和「规则确实是那三条」——少了任何一条，
        对应类别的粒子（animateMotion / animateTransform / 非透明度 animate）就漏网。
        """
        svg_dir = self.out / "assets" / "svg"
        animated = sorted(p for p in svg_dir.glob("*.svg")
                          if not p.name.endswith(".reduce.svg"))
        self.assertGreaterEqual(len(animated), 108, "动画 SVG 数量不对")
        for svg in animated:
            variant = svg_dir / (svg.stem + ".reduce.svg")
            with self.subTest(svg=svg.name):
                self.assertTrue(variant.exists(), f"{svg.name} 没有对应的静止版")
                text = variant.read_text(encoding="utf-8")
                for sel in (":has(> animateMotion):not(:has(text))",
                            ":has(> animateTransform):not(:has(text))",
                            ':has(> animate:not([attributeName="opacity"])):not(:has(text))'):
                    self.assertIn(sel, text, f"{variant.name} 缺选择器 {sel}")
                # 静止版里不能再出现 media query——那正是 v3.45 的坑
                self.assertNotIn("prefers-reduced-motion", text,
                                 f"{variant.name} 的规则被包进了 media query")

    def test_every_page_has_a_unique_description(self):
        """59 个页面原先共用同一句 site_description：每页必须有自己的、干净的摘要。

        摘要由正文自动摘取，很容易静默劣化——曾把 `p1-04-ch3.md` 里 ASCII 画的 BJT
        结构图（`│ N ├───┬───┤ N+ │`）和 `\\dfrac{R_0}{V_{DD}-V_{IN}-V_{TH}}` 这类
        压不成文字的公式当成摘要。这里把「每页有、各不相同、无 Markdown/公式残渣」
        钉成红灯。
        """
        pat = re.compile(r'^---\ndescription: ([^\n]*)\ntitle: ([^\n]*)\n---\n')
        descs = {}
        for page in sorted(self.out.glob("*.md")):
            with self.subTest(page=page.name):
                m = pat.match(page.read_text(encoding="utf-8"))
                self.assertIsNotNone(m, "%s 没有 description（会退回全站同一句）" % page.name)
                descs[page.name] = json.loads(m.group(1))
                title = json.loads(m.group(2))
                self.assertTrue(title)
                self.assertNotEqual(page.stem, title)

        values = list(descs.values())
        dup = {v: [k for k, x in descs.items() if x == v] for v in values if values.count(v) > 1}
        self.assertEqual({}, dup, "有页面共用同一句 description：%s" % dup)

        for name, desc in descs.items():
            with self.subTest(page=name):
                self.assertGreaterEqual(len(desc), 8, "摘要太短：%r" % desc)
                self.assertLessEqual(len(desc), 150, "摘要超长：%r" % desc)
                # `"` 会把 <meta content="..."> 属性截断（p1-05-ch4 就因此整条 meta 消失），
                # 所以摘要里必须已经换成中文弯引号
                for bad in ("`", "*", "$", "\\", "|", "│", "├", "&lt;", "frac", "quad", '"'):
                    self.assertNotIn(bad, desc, "摘要里混进了 Markdown/公式/ASCII 图残渣：%r" % desc)

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

    def test_lesson_assets_and_three_entry_points_are_published(self):
        config = (self.build / "mkdocs.yml").read_text(encoding="utf-8")
        for kind, name in (("stylesheets", "learning.css"), ("javascripts", "learning.js")):
            self.assertIn(f"{kind}/{name}", config)
            self.assertEqual((self.work / "scripts/site_media" / name).read_bytes(),
                             (self.out / kind / name).read_bytes())
        for page, lesson, photo in (("p1-02-ch1.md", "rc", "capacitors.jpg"),
                                    ("p1-05-ch4.md", "mosfet", "mosfets.jpg"),
                                    ("p1-07-ch6.md", "lm358", "lm358n.jpg")):
            text = (self.out / page).read_text(encoding="utf-8")
            self.assertIn(f'data-study="{lesson}"', text)
            self.assertIn("data-study-video", text)
            self.assertNotIn("<iframe", text)
            self.assertIn(f"assets/photos/{photo}", text)
            self.assertTrue((self.out / "assets/photos" / photo).is_file())

    def test_reading_navigation_connects_all_chapters_to_their_quizzes(self):
        quiz = (self.out / 'p9-00-quiz.md').read_text(encoding='utf-8')
        chapters = sorted((int(re.search(r'-ch(\d+)\.md$', p.name)[1]), p)
                          for p in self.out.glob('*-ch[0-9]*.md'))
        self.assertEqual(list(range(19)), [n for n, _ in chapters])
        for position, (number, page) in enumerate(chapters):
            content = page.read_text(encoding='utf-8')
            self.assertIn(f'href="p9-00-quiz.html#quiz-ch{number}"', content)
            self.assertIn(f'<a id="quiz-ch{number}"></a>', quiz)
            if position + 1 < len(chapters):
                next_number, next_page = chapters[position + 1]
                self.assertIn(f'href="{next_page.stem}.html#ch{next_number}"', content)
            if position:
                previous_number, previous_page = chapters[position - 1]
                self.assertIn(f'href="{previous_page.stem}.html#ch{previous_number}"', content)
        self.assertIn('href="index.html"', chapters[0][1].read_text(encoding='utf-8'))
        self.assertIn('href="p8-03-s8-3.html"', chapters[-1][1].read_text(encoding='utf-8'))

    def test_legacy_links_resolve_to_canonical_source_anchors(self):
        redirects = json.loads((self.work / 'scripts/site_media/legacy-anchors.json').read_text(encoding='utf-8'))
        self.assertEqual(35, len(redirects))
        for source, target in redirects.items():
            old_page, old_anchor = source.split('#')
            new_page, new_anchor = target.split('#')
            old = (self.out / old_page.replace('.html', '.md')).read_text(encoding='utf-8')
            canonical = (self.work / 'docs' / new_page.replace('.html', '.md')).read_text(encoding='utf-8')
            self.assertIn(f'class="legacy-anchor" id="{old_anchor}"', old)
            self.assertIn(f'href="{target}"', old)
            self.assertIn(f'<a id="{new_anchor}"></a>', canonical)
            self.assertNotIn(target, redirects, 'Redirect chains must not be introduced')

    def test_homepage_local_html_links_and_reading_assets_are_published(self):
        home = (self.out / 'index.md').read_text(encoding='utf-8')
        self.assertNotRegex(home, r'href="[^"]*\.md(?:#|\")')
        for filename in re.findall(r'href="([\w-]+)\.html', home):
            self.assertTrue((self.out / f'{filename}.md').exists())
        self.assertTrue((self.out / 'LICENSE').is_file())
        for directory, filename in (('stylesheets', 'reading.css'), ('javascripts', 'reading.js')):
            self.assertEqual((self.work / 'scripts/site_media' / filename).read_bytes(),
                             (self.out / directory / filename).read_bytes())

    def test_learning_catalog_covers_all_chapters_and_question_anchors(self):
        data = (self.out / 'javascripts/learning-catalog.js').read_text(encoding='utf-8')
        catalog = json.loads(data.split(' = ', 1)[1].rstrip(';\n'))
        self.assertEqual(19, len(catalog['chapters']))
        self.assertEqual(92, len(catalog['questions']))
        quiz = (self.out / 'p9-00-quiz.md').read_text(encoding='utf-8')
        ids = [question['id'] for question in catalog['questions']]
        self.assertEqual(len(ids), len(set(ids)))
        for question in catalog['questions']:
            self.assertIn(f'id="{question["id"]}"', quiz)
            self.assertEqual('p9-00-quiz.html#' + question['id'], question['href'])
        self.assertEqual((self.work / 'scripts/site_media/progress.js').read_bytes(),
                         (self.out / 'javascripts/progress.js').read_bytes())

    def test_homepage_hero_counts_match_the_real_inventory(self):
        """首页宣传行的数字必须由真实清单推导：加动画/题目/样板忘改首页即红灯。"""
        home = (self.out / 'index.md').read_text(encoding='utf-8')
        hero = re.search(r'\*\*(\d+) 章核心内容\*\* · \*\*(\d+) 张原理动画\*\* · '
                         r'\*\*(\d+) 个可控教学样板\*\* · \*\*(\d+) 道章节题 \+ (\d+) 道专题题\*\*', home)
        self.assertIsNotNone(hero, '首页 hero 宣传行缺失或格式改变')
        claimed_chapters, animations, lessons, chapter_q, extra_q = map(int, hero.groups())
        data = (self.out / 'javascripts/learning-catalog.js').read_text(encoding='utf-8')
        catalog = json.loads(data.split(' = ', 1)[1].rstrip(';\n'))
        studies = []
        for page in self.out.glob('*.md'):
            studies += re.findall(r'<a id="(\w+)-study"></a>', page.read_text(encoding='utf-8'))
        self.assertEqual(len(catalog['chapters']), claimed_chapters, 'hero 章数与学习目录不符')
        self.assertEqual(len(list((self.work / 'assets/svg').glob('*.svg'))), animations,
                         'hero 动画张数与 assets/svg 实际文件数不符')
        self.assertEqual(len(set(studies)), lessons, 'hero 样板数与 *-study 互动课锚点不符')
        self.assertEqual(sum(1 for q in catalog['questions'] if re.fullmatch(r'q-ch\d+-\d+', q['id'])),
                         chapter_q, 'hero 章节题数与 q-ch* 题目不符')
        self.assertEqual(sum(1 for q in catalog['questions'] if re.fullmatch(r'q-extra-\d+', q['id'])),
                         extra_q, 'hero 专题题数与 q-extra-* 题目不符')


    # ---------- 篇级落地页与章级验收 ----------
    def test_part_landing_pages_link_all_children(self):
        """篇级落地页不能退化成一句标题：必须给出「怎么读」并链接本篇全部子页。"""
        for landing, prefix in sorted(PART_LANDING_PREFIX.items()):
            with self.subTest(page=landing):
                text = (self.work / "docs" / landing).read_text(encoding="utf-8")
                self.assertIn("怎么读", text)
                children = [p.name for p in sorted((self.work / "docs").glob(prefix + "*.md"))
                            if p.name != landing]
                self.assertTrue(children, f"{landing} 没有找到任何子页")
                for child in children:
                    self.assertIn(f"({child}", text, f"{landing} 缺少子页链接 {child}")

    def test_every_chapter_declares_verifiable_outcomes(self):
        """章首「学完你应能」落实共建铁律 9：新增章节忘写验收标准即红灯。"""
        chapters = sorted(p.name for p in (self.work / "docs").glob("p[1-4]-*-ch*.md"))
        self.assertGreaterEqual(len(chapters), 19)
        for page in chapters:
            with self.subTest(page=page):
                self.assertIn("学完你应能", (self.work / "docs" / page).read_text(encoding="utf-8"))

    def test_cheatsheet_cites_every_chapter(self):
        """公式速查表是全站的「算」入口：19 章每章至少贡献一条，新增章节漏入表即红灯。"""
        text = (self.work / "docs" / "p0-08-cheatsheet.md").read_text(encoding="utf-8")
        chapters = sorted(p.name for p in (self.work / "docs").glob("p[1-4]-*-ch*.md"))
        self.assertGreaterEqual(len(chapters), 19)
        for page in chapters:
            with self.subTest(page=page):
                self.assertIn(f"]({page}#", text, f"速查表没有引用 {page}")

    # ---------- 共建页脚 ----------
    def test_feedback_footer_on_every_page(self):
        for page in sorted(self.out.glob("*.md")):
            with self.subTest(page=page.name):
                text = page.read_text(encoding="utf-8")
                self.assertIn("issues/new?template=content-fix.yml", text)
                self.assertIn("issues/new?template=new-topic.yml", text)

    def test_docs_stay_clean(self):
        """页脚 / lightbox / 懒加载属性 / description / 提示卡只进站点产物，docs/ 里不能出现。

        懒加载要按 `<img …loading="lazy">` 匹配——更新日志里会**用文字**提到这个属性，
        只查字面量会把正常的文档表述误判成注入。
        """
        for page in sorted((self.work / "docs").glob("*.md")):
            with self.subTest(page=page.name):
                text = page.read_text(encoding="utf-8")
                self.assertNotIn("issues/new?template=content-fix.yml", text)
                self.assertNotIn("gal-card", text)
                self.assertNotIn('<div class="callout callout-', text,
                                 "docs/ 里要能直接读，提示卡是站点产物才有的")
                self.assertIsNone(re.search(r'<img[^>]*\bloading="lazy"', text),
                                  "docs/ 里的 <img> 不该带懒加载属性")
                self.assertFalse(text.startswith("---\n"), "docs/ 里不该有 front-matter")

    # ---------- 标题层级 ----------
    HEADING = re.compile(r"<h([1-6])(?:\s[^>]*)?>(.*?)</h\1>", re.S)
    CALL_TAG = re.compile(r"<[^>]+>")
    SIGNATURE = re.compile(r"^> *(?:💎|🧮|🎯|📚|📺|📷|📎|🔧|⚠️|💡|📌|🎬|🔗)")

    def headings(self, name):
        return [(int(m.group(1)), self.CALL_TAG.sub("", m.group(2)).replace("&para;", "").strip())
                for m in self.HEADING.finditer(self.body_html(name))]

    def test_every_page_renders_exactly_one_h1(self):
        """正文里必须恰好一个 h1。

        48 个页面原本用 `##` 当章标题，正文里没有 h1，Material 就补一个来自 nav 的
        `<h1>`，正文再渲染一个**同名**的 `<h2>` —— 标题在页面上出现两遍，
        而且文档大纲里根本没有「这一页的主题」。修法是 build_site.shift_headings()。
        """
        for page in sorted(self.site.glob("*.html")):
            with self.subTest(page=page.name):
                h1 = [t for lv, t in self.headings(page.name) if lv == 1]
                self.assertEqual(1, len(h1), f"h1 个数应为 1，实际 {len(h1)}：{h1}")

    def test_no_page_repeats_its_title_as_h1_plus_h2(self):
        for page in sorted(self.site.glob("*.html")):
            with self.subTest(page=page.name):
                hs = self.headings(page.name)
                dup = [a[1] for a, b in zip(hs, hs[1:])
                       if a[0] == 1 and b[0] == 2 and a[1] and a[1] == b[1]]
                self.assertEqual([], dup, f"标题重复（主题 h1 与正文首个 h2 同名）：{dup}")

    def test_no_page_skips_a_heading_level(self):
        """h1 → h3 这种跳级会让屏幕阅读器读不出层级（WCAG 1.3.1）。

        实测踩过一次：入场诊断组件用 h3 当「第 N 题」的题面，而它长在页面最顶部，
        于是每页第一条标题就是 h1 → h3。
        """
        for page in sorted(self.site.glob("*.html")):
            with self.subTest(page=page.name):
                levels = [lv for lv, _t in self.headings(page.name)]
                for a, b in zip(levels, levels[1:]):
                    self.assertLessEqual(b, a + 1,
                                         f"标题层级从 h{a} 跳到 h{b}：{self.headings(page.name)}")

    # ---------- 标志性提示卡 ----------
    def test_signature_blockquotes_become_cards(self):
        """💎/🧮/🎯… 开头的引用块必须被包成彩色卡片，且四类都要有。"""
        counts = {}
        for page in sorted(self.out.glob("*.md")):
            text = page.read_text(encoding="utf-8")
            for kind in re.findall(r'<div class="callout callout-([a-z]+)" markdown="1">', text):
                counts[kind] = counts.get(kind, 0) + 1
        self.assertGreaterEqual(sum(counts.values()), 160,
                                f"提示卡总数偏少，可能有一类没被包上：{counts}")
        for kind in ("gem", "calc", "goal", "prereq", "video", "photo", "attach", "fix",
                     "warn", "idea", "pin", "link"):
            with self.subTest(kind=kind):
                self.assertGreater(counts.get(kind, 0), 0, f"{kind} 类一张都没有：{counts}")

    def test_no_signature_blockquote_is_left_unwrapped(self):
        """包完不该还剩 `> 💎` 这种——漏一张就是「同一类提示两种长相」。"""
        leftovers = []
        for page in sorted(self.out.glob("*.md")):
            text = page.read_text(encoding="utf-8")
            for num, line in enumerate(text.split("\n"), 1):
                if self.SIGNATURE.match(line):
                    leftovers.append(f"{page.name}:{num} {line[:40]}")
        self.assertEqual([], leftovers, "还有没被包成卡片的标志性引用块：\n  "
                         + "\n  ".join(leftovers))

    def test_card_count_equals_the_number_of_signature_prompts_in_docs(self):
        """独立数一遍 docs/ 里的提示行，和产物里的卡片数对上——防「切多 / 切少」。

        切分规则是「每一行**自己**以标志性 emoji 开头就另起一张卡」，所以
        「签名行数」与「卡片数」必须一一对应。这条不复用 build_site 的函数，
        是照着规则独立数一遍——两边一起漂移才可能同时错。
        """
        expected = 0
        for page in sorted((self.work / "docs").glob("*.md")):
            in_fence = False
            for line in page.read_text(encoding="utf-8").split("\n"):
                s = line.strip()
                if s.startswith("```") or s.startswith("~~~"):
                    in_fence = not in_fence
                    continue
                if in_fence or not line.startswith(">"):
                    continue
                if self.SIGNATURE.match(line):
                    expected += 1
        got = sum(len(re.findall(r'<div class="callout callout-[a-z]+" markdown="1">',
                                 p.read_text(encoding="utf-8")))
                  for p in self.out.glob("*.md"))
        self.assertGreater(expected, 160, f"docs/ 里只数到 {expected} 个提示行，扫描器可能坏了")
        self.assertEqual(expected, got, "卡片数与 docs/ 里的提示行数不一致（切多或切少）")

    def test_no_card_is_empty(self):
        """空卡片 = 切割切错了（把提示行切走、只剩空行）。"""
        for page in sorted(self.out.glob("*.md")):
            text = page.read_text(encoding="utf-8")
            for m in re.finditer(r'<div class="callout callout-([a-z]+)" markdown="1">\n(.*?)\n</div>',
                                 text, re.S):
                with self.subTest(page=page.name, kind=m.group(1)):
                    self.assertTrue(m.group(2).strip(), "空的提示卡")

    # ---------- 社交卡片与结构化数据 ----------
    @staticmethod
    def _png_size(path):
        raw = path.read_bytes()[:33]
        if raw[:8] != b"\x89PNG\r\n\x1a\n":
            raise AssertionError(f"{path} 不是 PNG")
        return (int.from_bytes(raw[16:20], "big"), int.from_bytes(raw[20:24], "big"))

    def test_social_card_is_self_hosted_and_the_right_size(self):
        """og:image 必须指向本站的产物，且真是一张 1200×630 的 PNG。

        原来外链 Wikimedia 的电路板照片：抓取方要跨域取第三方资源（国内常超时），
        而且那张图与本站内容无关。自托管后还要防「只改了 URL、忘了提交图片」——
        所以这里既查 meta 也查文件本体。
        """
        from build_site import OG_HEIGHT, OG_IMAGE, OG_WIDTH
        self.assertTrue(OG_IMAGE.startswith("https://zhuguang-ZFG.github.io/analog-circuit-roadmap/"),
                        f"og:image 必须自托管：{OG_IMAGE}")
        self.assertNotIn("wikimedia", OG_IMAGE)
        page = self.rendered("p1-02-ch1.html")
        for tag, attr in (("og:image", "property"), ("twitter:image", "name")):
            with self.subTest(tag=tag):
                m = re.search(rf'<meta {attr}="{tag}" content="([^"]+)"', page)
                self.assertIsNotNone(m, f"缺少 {tag}")
                self.assertEqual(OG_IMAGE, m.group(1), f"{tag} 必须指向自托管产物")
        local = self.site / OG_IMAGE.split("/analog-circuit-roadmap/", 1)[1]
        self.assertTrue(local.is_file(), f"站点产物里没有 {local}")
        self.assertEqual((OG_WIDTH, OG_HEIGHT), self._png_size(local))
        self.assertEqual((1200, 630), self._png_size(local),
                         "og:image 应当是 1200×630（社交卡片的 1.91:1）")
        for tag in ("og:image:width", "og:image:height", "twitter:image:alt"):
            self.assertIn(tag, page)

    def test_every_page_ships_parseable_json_ld(self):
        """结构化数据必须能被 json.loads 直接吃下（转义错一个字符就整块失效）。"""
        for page in sorted(self.site.glob("*.html")):
            with self.subTest(page=page.name):
                blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>',
                                    self.rendered(page.name), re.S)
                self.assertEqual(1, len(blocks), "每页应当恰好一块 JSON-LD")
                data = json.loads(blocks[0])
                graph = data.get("@graph", [])
                self.assertEqual("https://schema.org", data.get("@context"))
                self.assertEqual(2, len(graph), f"应当有 WebSite + 页面节点：{graph}")
                self.assertEqual("WebSite", graph[0]["@type"])
                self.assertIn(graph[1]["@type"], ("WebPage", "TechArticle"))
                self.assertTrue(graph[1]["headline"].strip(), "headline 不能为空")
                self.assertTrue(graph[1]["description"].strip(), "description 不能为空")
                self.assertEqual("zh-CN", graph[1]["inLanguage"])

    def test_homepage_is_a_webpage_and_the_rest_are_articles(self):
        home = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>',
                                    self.rendered("index.html"), re.S).group(1))
        self.assertEqual("WebPage", home["@graph"][1]["@type"])
        ch1 = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>',
                                   self.rendered("p1-02-ch1.html"), re.S).group(1))
        self.assertEqual("TechArticle", ch1["@graph"][1]["@type"])

    def test_json_ld_escapes_html_specials(self):
        """把模板里的 JSON-LD 表达式抠出来，喂一份恶意摘要，直接看它转义没有。

        真站点目前**没有任何一页**的标题/摘要含 `<` `>` `&`（实测 62 页 0 命中），
        所以「扫产物里有没有裸尖括号」这条断言永远为真——是个假绿。
        摘要器会把 `&lt;` 还原成 `<`，所以这个风险是真的、只是暂时没被触发。
        这里单独渲染那段表达式，才真的能红。
        """
        import jinja2
        from build_site import OVERRIDES_MAIN_HTML

        m = re.search(r'<script type="application/ld\+json">\{\{(.*?)\}\}</script>',
                      OVERRIDES_MAIN_HTML, re.S)
        self.assertIsNotNone(m, "模板里找不到 JSON-LD 的 {{ … }} 表达式")
        expr = m.group(1)
        self.assertIn("tojson", expr, "JSON-LD 必须走 tojson（它把 < > & 转成 \\uXXXX）")

        class _Config:
            site_url = "https://example.test/x/"
            site_name = "站点"
            site_description = "描述"

        class _Page:
            is_homepage = False
            canonical_url = "https://example.test/x/a.html"
            title = "标题"
            meta = {"description": "危险 </script><script>alert(1)</script> & <b>粗</b>"}

        out = jinja2.Environment(autoescape=True).from_string(
            "{{" + expr + "}}").render(config=_Config(), page=_Page())
        for ch in "<>&":
            with self.subTest(char=ch):
                self.assertNotIn(ch, out, f"JSON-LD 里出现了裸 {ch!r}，会截断 <script>")
        data = json.loads(out)
        self.assertEqual("TechArticle", data["@graph"][1]["@type"])
        self.assertIn("</script>", data["@graph"][1]["description"],
                      "转义应当是「JSON 层面可还原」的，而不是把内容删掉")

    # ---------- 排版层 ----------
    def test_typography_layer_is_published_and_linked(self):
        from build_site import MKDOCS_YML
        self.assertRegex(MKDOCS_YML,
                         re.compile(r"^[ \t]*-[ \t]*stylesheets/typography\.css[ \t]*$", re.M),
                         "typography.css 必须在 extra_css 里被真正引用（注释不算）")
        css = self.site / "stylesheets" / "typography.css"
        self.assertTrue(css.is_file(), "typography.css 没有发布到站点")
        text = css.read_text(encoding="utf-8")
        for kind in ("callout-gem", "callout-warn", "callout-calc"):
            self.assertIn(kind, text)
        self.assertIn("stylesheets/typography.css", self.rendered("p1-02-ch1.html"))

    def test_every_callout_kind_has_light_and_dark_colours(self):
        """13 类提示卡**每一类**都要有浅色与深色两套 `--co`。

        只查「文件里出现过 `data-md-color-scheme="slate"`」是假绿：漏掉某一类，
        那一类在深色主题下就是深色文字落在深色卡片上——等于没写，而且没人看得出来
        （变异验证时踩过这个坑）。
        """
        from build_site import CALLOUT_KINDS
        kinds = sorted(set(CALLOUT_KINDS.values()))
        raw = (self.site / "stylesheets" / "typography.css").read_text(encoding="utf-8")
        # 先剥掉 /* … */ —— 否则「被注释掉的那条规则」仍然能被正则匹配到，
        # 漏配一整类颜色却照样绿灯（变异验证时踩过这个坑）。
        text = re.sub(r"/\*.*?\*/", " ", raw, flags=re.S)
        dark_rules = re.findall(r'\[data-md-color-scheme="slate"\][^{]*\{[^}]*\}', text)
        dark = "\n".join(dark_rules)
        # 浅色那边必须先把深色规则**整条摘掉**：`[data-md-color-scheme="slate"] … .callout-warn { --co }`
        # 里同样含 `.callout-warn { --co`，不摘掉的话浅色漏配也照样绿灯
        # （变异验证时踩过这个坑）。
        light = text
        for rule in dark_rules:
            light = light.replace(rule, " ")
        self.assertGreaterEqual(len(kinds), 13, f"词表缩水了：{kinds}")
        for slug in kinds:
            with self.subTest(kind=slug):
                self.assertRegex(light, rf"\.callout-{slug}\s*\{{[^}}]*--co",
                                 f"{slug} 没有浅色配色")
                self.assertRegex(dark, rf"\.callout-{slug}\b[^{{]*\{{[^}}]*--co",
                                 f"{slug} 没有深色配色")

    # ---------- 辅助 ----------
    @staticmethod
    def _n(demo_anchor):
        return int(re.sub(r"\D", "", demo_anchor))


if __name__ == "__main__":
    unittest.main()

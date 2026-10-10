"""站点产物的两处「正文结构」变换：标题层级归一 + 标志性引用块成卡。

这两个函数都在 build_site.py 里，但它们的失败方式完全不同，而且都不会报错：
  * `shift_headings` 漏掉一页 → 那一页标题出现两遍（实测 v3.47 之前 48/62 页中招）；
  * `wrap_callouts` 多切一刀 → 提示卡里混进半句话，或者代码块被拆开。
所以两边都用「构造输入 → 断言输出」的单元测试钉住，不依赖真站点构建。

（侧栏「节首页补丁」的单元测试在 test_site_build.py —— 那一组要读已安装的
 Material 模板，而本文件所在的 docs-sync 作业是**刻意零依赖**的。）

Run: python -B -m unittest discover -s scripts -p test_page_structure.py -v
"""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_site import shift_headings, wrap_callouts, wrap_chapter_hero  # noqa: E402


class ShiftHeadingsTests(unittest.TestCase):
    def test_an_h2_only_page_gets_promoted_one_level(self):
        src = "## 第 1 章 标题\n\n正文。\n\n### 1.1 小节\n\n#### 1.1.1 更小\n"
        self.assertEqual("# 第 1 章 标题\n\n正文。\n\n## 1.1 小节\n\n### 1.1.1 更小\n",
                         shift_headings(src))

    def test_a_page_with_two_top_level_sections_gets_only_one_h1(self):
        """「🙏 致谢」页有 `## 致谢` + `## 共建者墙` 两个同级标题。

        无脑全升一级会让这一页出现**两个 h1**（实测踩过）；第二个要压在 `##` 上。
        """
        src = "## 🙏 致谢\n\n正文。\n\n## 👥 共建者墙\n\n表格。\n"
        out = shift_headings(src)
        self.assertEqual(1, len([ln for ln in out.split("\n") if ln.startswith("# ")]),
                         f"只能有一个 h1：{out!r}")
        self.assertIn("\n## 👥 共建者墙\n", out)
        self.assertIn("# 🙏 致谢\n", out)

    def test_no_heading_is_ever_promoted_past_h1(self):
        """无论第一个标题是几级，整页都只会出现一个 h1。"""
        for first in ("##", "###", "####", "#####", "######"):
            with self.subTest(first=first):
                out = shift_headings(f"{first} 主题\n\n### 小节\n\n## 另一个同级\n")
                self.assertEqual(1, len([ln for ln in out.split("\n") if ln.startswith("# ")]),
                                 f"首个标题为 {first} 时出了多个 h1：{out!r}")

    def test_a_page_that_already_has_an_h1_is_left_alone(self):
        """篇首页用 `#`，不能跟着再提一级——否则 h1 变没了、Material 又补一个重复标题。"""
        src = "# 第五篇：动画演示中心\n\n## 5.1 RC 充电\n"
        self.assertIs(src, shift_headings(src))

    def test_promoting_twice_is_a_no_op(self):
        """提过之后页面就有 h1 了，第二次调用自然原样返回——流水线里重复调用是安全的。"""
        once = shift_headings("## 标题\n\n### 小节\n")
        self.assertEqual(once, shift_headings(once))

    def test_front_matter_is_kept_and_never_shifted(self):
        """front-matter 里的 `# 注释` 是 YAML 注释，不是标题。"""
        src = '---\ntitle: "x"\n# yaml 注释\n---\n\n## 标题\n'
        out = shift_headings(src)
        self.assertTrue(out.startswith('---\ntitle: "x"\n# yaml 注释\n---\n'))
        self.assertIn("\n# 标题\n", out)

    def test_fenced_code_is_untouched(self):
        """代码块里的 `# 注释` 是 shell 注释——动它就是把示例改错。"""
        src = ("## 标题\n\n```bash\n# 安装依赖\npip install x  # 行尾注释\n```\n\n"
               "~~~text\n# 波浪号围栏里的\n~~~\n")
        out = shift_headings(src)
        self.assertIn("# 安装依赖\npip install x  # 行尾注释\n", out)
        self.assertIn("~~~text\n# 波浪号围栏里的\n~~~\n", out)

    def test_fence_chars_pair_with_themselves(self):
        """``` 里的 ~~~ 只是普通文本，不能把它当成围栏结束。"""
        src = "## 标题\n\n```text\n~~~\n# 仍在围栏里\n~~~\n```\n"
        out = shift_headings(src)
        self.assertIn("~~~\n# 仍在围栏里\n~~~\n", out)

    def test_indented_code_and_quotes_and_tables_are_untouched(self):
        src = ("## 标题\n\n    # 四空格缩进是代码块\n\n> ## 引用里的井号\n\n"
               "| a | b |\n| - | - |\n")
        out = shift_headings(src)
        self.assertIn("    # 四空格缩进是代码块\n", out)
        self.assertIn("> ## 引用里的井号\n", out)

    def test_an_h1_inside_a_fence_does_not_block_promotion(self):
        """`# 注释` 出现在代码块里不算「这页有 h1」——否则整页都不会被提级。"""
        src = "## 标题\n\n```bash\n# 只是注释\n```\n"
        self.assertEqual("# 标题\n\n```bash\n# 只是注释\n```\n", shift_headings(src))


class WrapCalloutsTests(unittest.TestCase):
    def test_a_signature_blockquote_becomes_a_card(self):
        src = "> 💎 **精髓**：一句话。\n"
        out = wrap_callouts(src)
        self.assertIn('<div class="callout callout-gem" markdown="1">', out)
        self.assertIn("💎 **精髓**：一句话。", out)
        self.assertNotIn("> 💎", out)
        self.assertTrue(out.rstrip().endswith("</div>"))

    def test_two_prompts_in_one_block_split_into_two_cards(self):
        """章首固定是「🎯 学完你应能」紧跟「🧮 公式速查」——不切开会白丢一类视觉信号。"""
        src = ("> 🎯 **学完你应能**：说出 A。\n>\n> 🧮 **公式速查**：[表](p0-08-cheatsheet.md#dc)。\n")
        out = wrap_callouts(src)
        self.assertIn('class="callout callout-goal"', out)
        self.assertIn('class="callout callout-calc"', out)
        self.assertEqual(2, out.count("<div class=\"callout"), "应当切成两张卡")
        self.assertIn("🎯 **学完你应能**：说出 A。", out)
        self.assertIn("🧮 **公式速查**：[表](p0-08-cheatsheet.md#dc)。", out)

    def test_a_plain_blockquote_is_left_alone(self):
        src = "> 这一章没有公式推导。\n"
        self.assertEqual(src, wrap_callouts(src))

    def test_an_unknown_emoji_is_left_alone(self):
        """不在词表里的 emoji 不猜——宁可保持普通引用块，也不要错分类。"""
        src = "> 🚀 **发射**：不在词表里。\n"
        self.assertEqual(src, wrap_callouts(src))

    def test_fenced_code_is_untouched(self):
        src = "```text\n> 💎 这是示例文本\n```\n"
        self.assertEqual(src, wrap_callouts(src))

    def test_multiline_paragraphs_keep_their_content(self):
        src = "> 💎 **精髓**：第一段。\n>\n> 第二段，有**粗体**。\n"
        out = wrap_callouts(src)
        self.assertIn("第一段。", out)
        self.assertIn("第二段，有**粗体**。", out)
        self.assertEqual(1, out.count("<div class=\"callout"))

    def test_every_wrapped_card_is_closed(self):
        src = "> 💎 **精髓**：A。\n\n普通段落。\n\n> ⚠️ **坑**：B。\n"
        out = wrap_callouts(src)
        self.assertEqual(out.count("<div class=\"callout"), out.count("</div>"))
        self.assertEqual(2, out.count("<div class=\"callout"))


class WrapChapterHeroTests(unittest.TestCase):
    """章首舞台：只包章页开头（h1 + 引导句 + 开场提示卡），正文一概不碰。"""

    def test_a_chapter_opening_gets_wrapped_with_chapter_number(self):
        src = ("<a id=\"ch3\"></a>\n"
               "# 第 3 章 BJT\n\n"
               "> 📚 **先修**：第 2 章。\n\n"
               "> 🎯 **学完你应能**：三件事。\n\n"
               "### 3.1 正文开始\n\n段落。\n")
        out = wrap_chapter_hero(src, "p1-04-ch3.md")
        self.assertIn('<div class="chapter-hero" data-chapter="3" markdown="1">', out)
        self.assertIn('<p class="chapter-hero-num" aria-hidden="true">3</p>', out)
        # 舞台吞掉 h1 与两张开场卡；正文标题留在舞台外
        self.assertIn("# 第 3 章 BJT", out.split("</div>")[0])
        self.assertIn('### 3.1 正文开始', out.split("</div>")[-1])
        # div 配平
        self.assertEqual(out.count("<div "), out.count("</div>"))

    def test_intro_blockquote_rides_in_the_stage(self):
        """第 0 章式开头：h1 后面跟着普通引用块再接提示卡——引导句也在舞台里。"""
        src = ("# 第 0 章 学前班\n\n"
               "> 这一章没有公式推导。\n\n"
               "> 🎯 **学完你应能**：建立直觉。\n\n"
               "### 0.1 正文\n")
        out = wrap_chapter_hero(src, "p1-01-ch0.md")
        self.assertIn('<div class="chapter-hero" data-chapter="0" markdown="1">', out)
        head = out.split("</div>")[0]
        self.assertIn("> 这一章没有公式推导。", head)
        self.assertIn("> 🎯 **学完你应能**：建立直觉。", head)

    def test_body_callouts_after_first_heading_stay_outside(self):
        """舞台只吞 h1 之后的连续开场块；正文标题后面的提示卡不能被卷进来。"""
        src = ("# 第 5 章 输出\n\n"
               "> 🎯 **学完你应能**：两种输出。\n\n"
               "### 5.1 推挽\n\n"
               "> 💎 **精髓**：图腾柱。\n\n"
               "### 5.2 开漏\n")
        out = wrap_chapter_hero(src, "p1-06-ch5.md")
        hero = out.split("</div>")[0]
        self.assertIn("> 🎯 **学完你应能**：两种输出。", hero)
        self.assertNotIn("图腾柱", hero)
        self.assertIn("> 💎 **精髓**：图腾柱。", out)

    def test_non_chapter_pages_are_untouched(self):
        src = "# 首页\n\n> 引子。\n\n> 🎯 学完你应能。\n"
        self.assertEqual(src, wrap_chapter_hero(src, "index.md"))
        self.assertEqual(src, wrap_chapter_hero(src, "p0-08-cheatsheet.md"))

    def test_h1_without_followup_gets_no_stage(self):
        src = "# 第 9 章 基准\n\n正文直接开始。\n"
        self.assertEqual(src, wrap_chapter_hero(src, "p1-10-ch9.md"))

    def test_wrapped_callout_blocks_keep_their_inner_divs_intact(self):
        """提示卡 div 是成对的嵌套结构——舞台必须整块吞、不能拦腰截断。"""
        src = ("# 第 12 章 电路族\n\n"
               '<div class="callout callout-goal" markdown="1">\n\n'
               "🎯 学完你应能。\n\n"
               "</div>\n\n"
               '<div class="callout callout-calc" markdown="1">\n\n'
               "🧮 公式速查。\n\n"
               "</div>\n\n"
               "### 12.1 方法论\n")
        out = wrap_chapter_hero(src, "p2-02-ch12.md")
        start = out.find('<div class="chapter-hero"')
        end = out.rfind("</div>")
        self.assertTrue(0 <= start < end)
        hero = out[start:end]
        self.assertEqual(2, hero.count('<div class="callout'),
                         "两张开场卡都要整块进舞台")
        self.assertEqual(out.count("<div "), out.count("</div>"))


if __name__ == "__main__":
    unittest.main()

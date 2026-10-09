"""站点产物的三处「结构」变换：标题层级归一 + 引用块成卡 + 侧栏节首页补丁。

前两个函数在 build_site.py 里，失败方式完全不同，而且都不会报错：
  * `shift_headings` 漏掉一页 → 那一页标题出现两遍（实测 v3.47 之前 48/62 页中招）；
  * `wrap_callouts` 多切一刀 → 提示卡里混进半句话，或者代码块被拆开。
第三个是对 **Material 上游模板**打的最小补丁（不是我们自己写的变换），
失败方式更隐蔽：锚点对不上时补丁会静默打歪，侧栏悄悄退回去。
所以三边都用「构造输入 → 断言输出」的单元测试钉住，不依赖真站点构建。

Run: python -B -m unittest discover -s scripts -p test_page_structure.py -v
"""
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_site import (NAV_ITEM_ANCHOR, NAV_ITEM_PATCHED,  # noqa: E402
                        nav_item_override, shift_headings, wrap_callouts)


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


class NavIndexPatchTests(unittest.TestCase):
    """Material 的 navigation.indexes 对「篇首页」不生效，得给上游模板打补丁。

    `navigation.indexes` 只认 MkDocs 的 `Page.is_index`，而那个属性的定义就是
    `self.file.name == 'index'`（README.md 会被归一成 index）。本站的篇首页叫
    `p1-00-part1.md` —— 命不中，于是节标题退化成纯折叠标签（点它只能展开）、
    篇首页又以普通子项出现在列表首位，两处标题**一字不差**，侧栏里每个篇标题
    都重复一行（实测 9 处）。补丁把「首个标题与节标题相同的叶子页」也算作该节的
    index，于是标题变成链接、篇首页不再重复出现。

    这里锁四件事：
      ① 锚点在上游模板里**恰好出现一次**；
      ② 补丁确实换了判据，且只改这一处（其余逐字保持上游，升级 Material 时
         不会留下我们自己臆想的版本）；
      ③ 锚点对不上时**响亮失败**，而不是静默打歪。
    """

    @staticmethod
    def _upstream():
        import material
        return (Path(material.__file__).parent / "templates" / "partials"
                / "nav-item.html").read_text(encoding="utf-8")

    def test_the_anchor_appears_exactly_once_upstream(self):
        self.assertEqual(
            1, self._upstream().count(NAV_ITEM_ANCHOR),
            "Material 的 partials/nav-item.html 结构变了：锚点找不到或出现多次，"
            "请重新核对 build_site.NAV_ITEM_ANCHOR / NAV_ITEM_PATCHED 这对补丁")

    def test_the_patch_teaches_it_about_part_index_pages(self):
        """判据是「标题相同」——因为重复的根源正是这两处标题相同。"""
        self.assertIn("item.title == nav_item.title", NAV_ITEM_PATCHED)
        self.assertNotIn("item.title == nav_item.title", NAV_ITEM_ANCHOR)

    def test_the_patch_only_requires_a_leaf_page(self):
        """必须限定 `not item.children`，否则会把子节也当成 index。"""
        self.assertIn("not item.children and item.title == nav_item.title",
                      NAV_ITEM_PATCHED)

    def test_the_override_differs_from_upstream_only_at_the_anchor(self):
        self.assertEqual(self._upstream().replace(NAV_ITEM_ANCHOR, NAV_ITEM_PATCHED),
                         nav_item_override())

    def test_a_missing_anchor_fails_loudly_instead_of_patching_blindly(self):
        with tempfile.TemporaryDirectory(prefix="nav-item-") as tmp:
            broken = Path(tmp) / "nav-item.html"
            broken.write_text("{% macro render(nav_item, path, level, parent) %}{% endmacro %}",
                              encoding="utf-8")
            with self.assertRaises(SystemExit) as caught:
                nav_item_override(broken)
            self.assertIn("nav-item.html", str(caught.exception))


if __name__ == "__main__":
    unittest.main()

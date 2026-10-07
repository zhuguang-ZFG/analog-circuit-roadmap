#!/usr/bin/env python3
"""由 docs/ 生成 MkDocs 站点源 build/docs（含动画画廊与配套 JS/CSS）。

    python scripts/build_site.py            # 生成站点源 + build/mkdocs.yml
    python scripts/build_site.py --build    # 生成后直接调用 mkdocs build

内容页原样拷贝，另生成：
  * gallery.md —— 101 张动画卡片墙（按章筛选 + 关键字搜索，waytoagi 式卡片导航）
  * stylesheets/gallery.css、javascripts/gallery.js、javascripts/mathjax.js
  * build/mkdocs.yml —— 按篇分组的导航与 Material 主题配置
"""
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
BUILD = ROOT / "build"
OUT = BUILD / "docs"
SVG_SRC = ROOT / "assets" / "svg"

DEMO_HEAD = re.compile(r'^## (5\.\d+)\s+(.+?)\s*<a id="(demo\d+)"')
DEMO_IMG = re.compile(r'<img src="assets/svg/([\w\-]+\.svg)"[^>]*alt="([^"]*)"')
# docs 迁移后锚点链接写作 p5-00-part5.md#demoN，拼回 README 时才是 #demoN——两种都要认
DEMO_LINK = re.compile(r"\[(5\.\d+)\]\((?:[\w\-]+\.md)?#(demo\d+)\)")
CHAPTER_ROW = re.compile(r"^\|\s*§(\d+)\s+(第\s*\d+\s*章[^|]*?)\s*\|")

CHAPTER_LABEL = {
    "0": "§0 电路直觉", "1": "§1 无源元件", "2": "§2 二极管", "3": "§3 BJT",
    "4": "§4 MOSFET", "5": "§5 推挽/开漏", "6": "§6 运放", "7": "§7 比较器",
    "8": "§8 模拟开关", "9": "§9 基准稳压", "10": "§10 555",
    "11": "§11 放大拓扑", "12": "§12 运放族", "13": "§13 电源振荡",
    "14": "§14 设计方法", "15": "§15 PCB", "16": "§16 排故", "17": "§17 速查",
    "18": "§18 大师智慧",
}
APPENDIX = {"p9-12-changelog.md", "p9-13-thanks.md"}

GALLERY_CSS = """
.gal-bar{display:flex;flex-wrap:wrap;gap:.4rem;align-items:center;margin:.6rem 0 1.2rem}
.gal-bar input[type=search]{flex:1 1 220px;min-width:180px;padding:.45rem .7rem;border-radius:.5rem;
  border:1px solid var(--md-default-fg-color--lightest);background:var(--md-code-bg-color);
  color:var(--md-default-fg-color)}
.gal-chip{padding:.3rem .7rem;border-radius:999px;border:1px solid var(--md-default-fg-color--lightest);
  background:transparent;color:var(--md-default-fg-color);cursor:pointer;font-size:.75rem}
.gal-chip[aria-pressed=true]{background:var(--md-primary-fg-color);color:var(--md-primary-bg-color);
  border-color:var(--md-primary-fg-color)}
.gal-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:1rem}
.gal-card{border:1px solid var(--md-default-fg-color--lightest);border-radius:.6rem;overflow:hidden;
  background:var(--md-code-bg-color);transition:transform .15s ease,box-shadow .15s ease;
  display:flex;flex-direction:column}
.gal-card:hover{transform:translateY(-2px);box-shadow:0 4px 14px rgba(0,0,0,.18)}
.gal-card>a{display:block;text-decoration:none;color:inherit;flex:1 1 auto}
.gal-card img{display:block;width:100%;height:auto;background:#fff}
.gal-meta{padding:.5rem .7rem .7rem}
.gal-title{font-weight:600;font-size:.85rem;line-height:1.35;margin-bottom:.25rem}
.gal-tag{font-size:.7rem;opacity:.75}
.gal-empty{opacity:.7;font-size:.9rem}
.gal-actions{padding:0 .7rem .7rem}
.gal-play{width:100%;padding:.35rem .6rem;border-radius:.4rem;cursor:pointer;font-size:.75rem;font-weight:600;
  border:1px solid var(--md-primary-fg-color);background:transparent;color:var(--md-primary-fg-color)}
.gal-play:hover{background:var(--md-primary-fg-color);color:var(--md-primary-bg-color)}
.gal-modal{position:fixed;inset:0;z-index:9999;display:none;align-items:center;justify-content:center;
  background:rgba(0,0,0,.8);padding:2vh 2vw}
.gal-modal.is-open{display:flex}
.gal-modal-box{max-width:min(1100px,94vw);max-height:94vh;overflow:auto;padding:.8rem;border-radius:.6rem;
  background:var(--md-default-bg-color)}
.gal-modal-bar{display:flex;gap:.6rem;align-items:center;justify-content:space-between;flex-wrap:wrap;
  margin-bottom:.5rem}
.gal-modal-title{font-weight:700;font-size:.9rem}
.gal-modal-close{padding:.25rem .6rem;border-radius:.4rem;cursor:pointer;font-size:.78rem;
  border:1px solid var(--md-default-fg-color--lightest);background:transparent;color:inherit}
.gal-modal-box img{display:block;width:100%;height:auto;background:#fff;border-radius:.35rem}
.gal-modal-foot{margin-top:.5rem;font-size:.78rem}
.gal-modal-foot a{font-weight:600}
"""

GALLERY_JS = """
(function () {
  function init() {
    var cards = Array.prototype.slice.call(document.querySelectorAll('.gal-card'));
    var search = document.getElementById('gal-search');
    var chips = Array.prototype.slice.call(document.querySelectorAll('.gal-chip'));
    var empty = document.getElementById('gal-empty');
    var counter = document.getElementById('gal-count');
    var state = { ch: 'all', q: '' };

    function apply() {
      var shown = 0;
      cards.forEach(function (c) {
        var okCh = (state.ch === 'all') || (c.dataset.ch === state.ch);
        var hay = ((c.dataset.title || '') + ' ' + (c.dataset.file || '')).toLowerCase();
        var okQ = !state.q || hay.indexOf(state.q) >= 0;
        var ok = okCh && okQ;
        c.style.display = ok ? '' : 'none';
        if (ok) { shown++; }
      });
      if (empty) { empty.style.display = shown ? 'none' : ''; }
      if (counter) { counter.textContent = shown + ' / ' + cards.length; }
    }

    if (search) {
      search.addEventListener('input', function () {
        state.q = search.value.trim().toLowerCase();
        apply();
      });
    }
    chips.forEach(function (chip) {
      chip.addEventListener('click', function () {
        chips.forEach(function (c) { c.setAttribute('aria-pressed', 'false'); });
        chip.setAttribute('aria-pressed', 'true');
        state.ch = chip.dataset.ch;
        apply();
      });
    });
    apply();

    /* ---- 内嵌放大播放（lightbox）---- */
    var modal = document.getElementById('gal-modal');
    var mImg = document.getElementById('gal-modal-img');
    var mTitle = document.getElementById('gal-modal-title');
    var mLink = document.getElementById('gal-modal-link');
    var mClose = document.getElementById('gal-modal-close');
    if (!modal) { return; }

    function openModal(svg, title, href) {
      mImg.setAttribute('src', svg);
      mImg.setAttribute('alt', title);
      mTitle.textContent = title;
      if (mLink) { mLink.setAttribute('href', href); }
      modal.classList.add('is-open');
      if (mClose) { mClose.focus(); }
    }
    function closeModal() {
      modal.classList.remove('is-open');
      mImg.setAttribute('src', '');
    }
    document.addEventListener('click', function (e) {
      var t = e.target;
      var btn = t && t.closest ? t.closest('.gal-play') : null;
      if (btn) {
        e.preventDefault();
        openModal(btn.dataset.svg, btn.dataset.title, btn.dataset.href);
        return;
      }
      if (t === modal || (mClose && t === mClose)) { closeModal(); }
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') { closeModal(); }
    });
  }

  if (document.readyState !== 'loading') { init(); }
  else { document.addEventListener('DOMContentLoaded', init); }
})();
"""

OVERRIDES_MAIN_HTML = """{% extends "base.html" %}

{% block extrahead %}
  {{ super() }}
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="{{ config.site_name }}">
  <meta property="og:title" content="{{ page.title | default(config.site_name, true) }}">
  <meta property="og:description" content="{{ config.site_description }}">
  {% if page.canonical_url %}<meta property="og:url" content="{{ page.canonical_url }}">{% endif %}
  <meta property="og:image" content="__OG_IMAGE__">
  <meta property="og:locale" content="zh_CN">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{{ page.title | default(config.site_name, true) }}">
  <meta name="twitter:description" content="{{ config.site_description }}">
  <meta name="twitter:image" content="__OG_IMAGE__">
  <meta name="theme-color" content="#3f51b5">
  <meta name="author" content="zhuguang-ZFG">
{% endblock %}
"""

OG_IMAGE = ("https://upload.wikimedia.org/wikipedia/commons/thumb/0/0b/"
            "Printed_circuit_board.jpg/500px-Printed_circuit_board.jpg")

ROBOTS_TXT = """User-agent: *
Allow: /

Sitemap: https://zhuguang-ZFG.github.io/analog-circuit-roadmap/sitemap.xml
"""

FEEDBACK_FOOTER = """
---

> ✍️ **参与共建**：发现错别字、公式错误或失效链接？[提一个纠错 Issue](https://github.com/zhuguang-ZFG/analog-circuit-roadmap/issues/new?template=content-fix.yml) ·
> 想补充新主题、新动画或新资源？[提个建议](https://github.com/zhuguang-ZFG/analog-circuit-roadmap/issues/new?template=new-topic.yml) ·
> 想直接动手改：[共建指南](CONTRIBUTING.md) · [共建者墙](CONTRIBUTORS.md)
"""


MATHJAX_JS = r"""
window.MathJax = {
  tex: {
    inlineMath: [["\\(", "\\)"], ["$", "$"]],
    displayMath: [["\\[", "\\]"], ["$$", "$$"]],
    processEscapes: true,
    processEnvironments: true
  },
  options: { ignoreHtmlClass: ".*|", processHtmlClass: "arithmatex" }
};
"""

MKDOCS_YML = """site_name: 通往模拟电路之路
site_description: 从欧姆定律到芯片内部结构 —— 原理推导 + 器件剖析 + 故障分析 + 102 张 SVG 动画
site_url: https://zhuguang-ZFG.github.io/analog-circuit-roadmap/
repo_url: https://github.com/zhuguang-ZFG/analog-circuit-roadmap
repo_name: zhuguang-ZFG/analog-circuit-roadmap
edit_uri: edit/main/docs/
copyright: CC BY-SA 4.0

docs_dir: docs
site_dir: site
# 页面保持平铺（不带目录 URL），使正文里相对路径的 SVG 引用在各页都能解析
use_directory_urls: false

theme:
  name: material
  language: zh
  custom_dir: overrides
  features:
    - navigation.instant
    - navigation.tracking
    - navigation.sections
    - navigation.top
    - navigation.indexes
    - content.action.edit
    - content.code.copy
    - search.highlight
    - search.suggest
    - toc.follow
  palette:
    - media: "(prefers-color-scheme: light)"
      scheme: default
      primary: indigo
      accent: indigo
      toggle:
        icon: material/weather-night
        name: 切换到深色
    - media: "(prefers-color-scheme: dark)"
      scheme: slate
      primary: indigo
      accent: indigo
      toggle:
        icon: material/weather-sunny
        name: 切换到浅色

extra:
  social:
    - icon: fontawesome/brands/github
      link: https://github.com/zhuguang-ZFG/analog-circuit-roadmap
      name: GitHub 仓库
    - icon: fontawesome/solid/pen-to-square
      link: https://github.com/zhuguang-ZFG/analog-circuit-roadmap/issues/new/choose
      name: 提 Issue（纠错 / 建议）

extra_css:
  - stylesheets/gallery.css

extra_javascript:
  - javascripts/mathjax.js
  - https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js
  - javascripts/gallery.js

markdown_extensions:
  - abbr
  - admonition
  - attr_list
  - def_list
  - footnotes
  - md_in_html
  - tables
  - toc:
      permalink: true
  - pymdownx.details
  - pymdownx.superfences:
      custom_fences:
        - name: mermaid
          class: mermaid
          format: !!python/name:pymdownx.superfences.fence_code_format
  - pymdownx.arithmatex:
      generic: true
  - pymdownx.highlight:
      anchor_linenums: true
  - pymdownx.inlinehilite
  - pymdownx.tabbed:
      alternate_style: true

nav:
__NAV__
"""

def parse_demos():
    lines = (DOCS / "p5-00-part5.md").read_text(encoding="utf-8").split("\n")

    chapter_of = {}
    for ln in lines:
        m = CHAPTER_ROW.match(ln)
        if not m:
            continue
        for _num, demo in DEMO_LINK.findall(ln):
            chapter_of[demo] = m.group(1)

    items = []
    cur = None
    for ln in lines:
        m = DEMO_HEAD.match(ln)
        if m:
            if cur and cur.get("svg"):
                items.append(cur)
            cur = {"num": m.group(1), "title": m.group(2).strip(),
                   "anchor": m.group(3), "svg": "", "alt": "", "ch": ""}
            continue
        if cur and not cur.get("svg"):
            im = DEMO_IMG.search(ln)
            if im:
                cur["svg"] = im.group(1)
                cur["alt"] = im.group(2)
    if cur and cur.get("svg"):
        items.append(cur)
    for it in items:
        it["ch"] = chapter_of.get(it["anchor"], "")
    return items, chapter_of


def render_gallery(items):
    chips = ['<button class="gal-chip" data-ch="all" aria-pressed="true">全部 %d</button>'
             % len(items)]
    seen = []
    for it in items:
        if it["ch"] and it["ch"] not in seen:
            seen.append(it["ch"])
    for ch in sorted(seen, key=lambda x: int(x)):
        n = sum(1 for i in items if i["ch"] == ch)
        chips.append('<button class="gal-chip" data-ch="%s" aria-pressed="false">%s · %d</button>'
                     % (ch, CHAPTER_LABEL.get(ch, "§" + ch), n))

    cards = []
    for it in items:
        title = it["title"].replace('"', "&quot;")
        href = "p5-00-part5.html#%s" % it["anchor"]
        cards.append(
            '<div class="gal-card" data-ch="%s" data-title="%s" data-file="%s">\n'
            '  <a href="%s" title="%s">\n'
            '    <img src="assets/svg/%s" alt="%s" loading="lazy">\n'
            '    <div class="gal-meta">\n'
            '      <div class="gal-title">%s %s</div>\n'
            '      <div class="gal-tag">%s</div>\n'
            '    </div>\n'
            '  </a>\n'
            '  <div class="gal-actions">\n'
            '    <button class="gal-play" type="button" data-svg="assets/svg/%s" '
            'data-title="%s %s" data-href="%s">▶ 放大播放</button>\n'
            '  </div>\n'
            '</div>'
            % (it["ch"], title.lower(), it["svg"], href, title,
               it["svg"], it["alt"], it["num"], it["title"],
               CHAPTER_LABEL.get(it["ch"], "动画"),
               it["svg"], it["num"], title, href)
        )

    return "\n".join([
        "# 🎬 动画画廊",
        "",
        "> 全部 %d 张 SMIL 动画，可按章筛选、按标题搜索；"
        "点「▶ 放大播放」在弹窗里全尺寸观看（动画会自动播放），"
        "点卡片标题区直达该动画在 [动画演示中心](p5-00-part5.md)里的讲解与看点。" % len(items),
        "",
        '<div class="gal-bar">',
        '  <input id="gal-search" type="search" placeholder="搜索：米勒 / LDO / 迟滞 / mosfet …">',
        "  " + "\n  ".join(chips),
        '  <span class="gal-tag" id="gal-count"></span>',
        "</div>",
        "",
        '<div class="gal-grid">',
        "\n".join(cards),
        "</div>",
        "",
        '<p class="gal-empty" id="gal-empty" style="display:none">'
        "没有匹配的动画，换个关键词试试。</p>",
        "",
        '<div class="gal-modal" id="gal-modal" role="dialog" aria-modal="true" aria-label="动画放大播放">',
        '  <div class="gal-modal-box">',
        '    <div class="gal-modal-bar">',
        '      <span class="gal-modal-title" id="gal-modal-title"></span>',
        '      <button class="gal-modal-close" id="gal-modal-close" type="button">✕ 关闭（Esc）</button>',
        "    </div>",
        '    <img id="gal-modal-img" alt="">',
        '    <div class="gal-modal-foot">'
        '<a id="gal-modal-link" href="#">→ 查看这张动画的讲解与看点</a></div>',
        "  </div>",
        "</div>",
        "",
    ]) + "\n"


def page_title(path):
    for ln in path.read_text(encoding="utf-8").split("\n"):
        if ln.startswith("#"):
            t = re.sub(r"^#+\s*", "", ln)
            t = re.sub(r"<a\s+id=[^>]*>.*", "", t).strip()
            if t:
                return t
    return path.stem


def build_nav(pages):
    groups = []
    for name in pages:
        if name == "index.md":
            continue
        m = re.match(r"^p(\d+)-", name)
        key = 90 if name in APPENDIX else (int(m.group(1)) if m else 99)
        if not groups or groups[-1][0] != key:
            groups.append([key])
        groups[-1].append(name)

    lines = ["  - 首页: index.md"]
    for key, *names in groups:
        # pN-00-* 是「篇首页」：整篇的入口页，其后页面作为它的子项
        has_head = bool(re.match(r"^p\d+-00-", names[0]))
        if key == 90:
            title = "附录"
        elif key == 0:
            title = "开始之前"
        else:
            title = page_title(OUT / names[0])
        lines.append("  - %s:" % title)
        # 篇首页作为本节的首项（配合 navigation.indexes，点击节名即进入该页）
        if has_head:
            lines.append("    - %s" % names[0])
            children = names[1:]
        else:
            children = names
        for n in children:
            lines.append("    - %s: %s" % (page_title(OUT / n), n))
    lines.append("  - 🎬 动画画廊: gallery.md")
    lines.append("  - 社区:")
    lines.append("    - 参与共建: CONTRIBUTING.md")
    lines.append("    - 共建者墙: CONTRIBUTORS.md")
    return "\n".join(lines)


def write_mkdocs_config():
    skip = {"gallery.md", "CONTRIBUTING.md", "CONTRIBUTORS.md"}
    pages = [p.name for p in sorted(OUT.glob("*.md")) if p.name not in skip]
    yml = MKDOCS_YML.replace("__NAV__", build_nav(pages))
    (BUILD / "mkdocs.yml").write_text(yml, encoding="utf-8", newline="\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--build", action="store_true", help="生成后直接运行 mkdocs build")
    args = ap.parse_args()

    if not DOCS.is_dir():
        print("docs/ 不存在", file=sys.stderr)
        return 1
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)

    for page in sorted(DOCS.glob("*.md")):
        text = page.read_text(encoding="utf-8")
        # 原始 HTML 里的跨页链接 MkDocs 不会重写，这里统一 .md# -> .html#
        text = re.sub(r'href="([\w\-]+)\.md#', r'href="\1.html#', text)
        # 每页页脚加「参与共建」闭环（只在站点产物里加，docs/ 保持单一数据源干净）
        text = text.rstrip("\n") + "\n" + FEEDBACK_FOOTER
        (OUT / page.name).write_text(text, encoding="utf-8", newline="\n")
    for extra in ("CONTRIBUTING.md", "CONTRIBUTORS.md"):
        src = ROOT / extra
        if src.exists():
            shutil.copy2(src, OUT / extra)

    if SVG_SRC.is_dir():
        shutil.copytree(SVG_SRC, OUT / "assets" / "svg")

    (OUT / "stylesheets").mkdir(exist_ok=True)
    (OUT / "javascripts").mkdir(exist_ok=True)
    (OUT / "stylesheets" / "gallery.css").write_text(GALLERY_CSS, encoding="utf-8")
    (OUT / "javascripts" / "gallery.js").write_text(GALLERY_JS, encoding="utf-8")
    (OUT / "javascripts" / "mathjax.js").write_text(MATHJAX_JS, encoding="utf-8")

    # SEO：robots.txt（sitemap.xml 由 MkDocs 依据 site_url 自动生成）
    (OUT / "robots.txt").write_text(ROBOTS_TXT, encoding="utf-8", newline="\n")

    # SEO：社交卡片 meta（og / twitter）通过主题覆写注入 <head>
    ov = BUILD / "overrides"
    ov.mkdir(parents=True, exist_ok=True)
    (ov / "main.html").write_text(
        OVERRIDES_MAIN_HTML.replace("__OG_IMAGE__", OG_IMAGE), encoding="utf-8", newline="\n")

    items, _ = parse_demos()
    gallery = render_gallery(items).rstrip("\n") + "\n" + FEEDBACK_FOOTER
    (OUT / "gallery.md").write_text(gallery, encoding="utf-8", newline="\n")
    write_mkdocs_config()
    print("站点源已生成：%s（%d 页 + %d 张动画卡片）"
          % (OUT, len(list(OUT.glob("*.md"))), len(items)))

    if args.build:
        cmd = [sys.executable, "-m", "mkdocs", "build", "--config-file",
               str(BUILD / "mkdocs.yml")]
        print("mkdocs build ->", " ".join(cmd))
        return subprocess.call(cmd, cwd=str(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

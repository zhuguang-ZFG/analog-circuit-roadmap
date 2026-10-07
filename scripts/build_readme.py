#!/usr/bin/env python3
"""把 docs/ 源文件树拼回单文件 README.md（docs 是唯一数据源）。

* 页面顺序：index.md → pN-MM-*.md，按 (篇, 序号) 升序
* 跨页锚点链接 ``](page.md#anchor)`` 反写回 ``](#anchor)``，
  保证拼合后的单文件在 GitHub 上依然可跳转
* ``--check``：只比对不落盘（CI 用），不一致返回非零
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
README = ROOT / "README.md"

PAGE_RE = re.compile(r"^p(\d+)-(\d+)-.+\.md$")
MD_LINK = re.compile(r"\]\(([\w\-]+\.md)#([^)/]+)\)")
HTML_HREF = re.compile(r'href="([\w\-]+\.md)#([^"]+)"')
PAGE_LINK = re.compile(r"\]\(([\w\-]+\.md)\)")
HTML_PAGE = re.compile(r'href="([\w\-]+\.md)"')


def page_order(path: Path) -> tuple:
    name = path.name
    if name == "index.md":
        return (0, 0, name)
    m = PAGE_RE.match(name)
    if m:
        return (int(m.group(1)), int(m.group(2)), name)
    return (99, 99, name)


def collect_pages() -> list[Path]:
    if not DOCS.is_dir():
        print("docs/ not found — 先运行 scripts/split_readme.py", file=sys.stderr)
        raise SystemExit(1)
    return sorted(DOCS.glob("*.md"), key=page_order)


def build() -> str:
    page_names = {p.name for p in collect_pages()}
    all_lines: list[str] = []
    for path in collect_pages():
        raw = path.read_text(encoding="utf-8")
        lines = raw.split("\n")
        if lines and lines[-1] == "":
            lines.pop()          # 去掉文件末尾换行产生的空项
        text = "\n".join(lines)
        if not text.strip():
            continue
        text = MD_LINK.sub(lambda m: "](#%s)" % m.group(2), text)
        text = HTML_HREF.sub(lambda m: 'href="#%s"' % m.group(2), text)
        # 无锚点的整页链接（如 自测题库页）：单文件版要指向 docs/ 下的真实文件
        text = PAGE_LINK.sub(
            lambda m: "](docs/%s)" % m.group(1) if m.group(1) in page_names else m.group(0),
            text)
        # 同理：HTML 导航条里的 href="page.md" 也要指向 docs/
        text = HTML_PAGE.sub(
            lambda m: 'href="docs/%s"' % m.group(1) if m.group(1) in page_names else m.group(0),
            text)
        all_lines.append(text)
    return "\n".join(all_lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="只检查 docs 与 README 是否一致")
    args = ap.parse_args()

    out = build()
    if args.check:
        cur = README.read_text(encoding="utf-8") if README.exists() else ""
        if out.replace("\r\n", "\n") != cur.replace("\r\n", "\n"):
            print("README.md 与 docs/ 不同步：请运行 python scripts/build_readme.py",
                  file=sys.stderr)
            return 1
        print("docs/ ↔ README.md 同步 ✔")
        return 0

    README.write_text(out, encoding="utf-8", newline="\n")
    print("README.md 已由 docs/ 重建（%d 字符）" % len(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""静态插图的手绘皮肤：纸面、笔触与标题装饰，一次落盘。

底稿由 `scripts/visuals` 场景或手工 SVG 提供（已用 token 色值），
本模块只做三件事，几何与文案一律不动：

1. 注入纸面层（paper 渐变 + 纸纤维点阵 + 暗角 + 赭石表头淡染）
   与 `handraw.token_css()` 的明暗两套规则；
2. 直线微弯（`bow_lines`）与补 `fill="none"`（`stroke_only`）；
3. 标题改手写体并加马克笔划线（仅在标题几何匹配时）。

`python scripts/visuals/static_fig.py finalize <file.svg>...` 原地加工并报告；
`finalize` 可重复执行（幂等：已有纸面层的文件跳过注入）。
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1]
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import handraw  # noqa: E402

VIEWBOX = re.compile(r'viewBox="\d[\d.]*\s+\d[\d.]*\s+([\d.]+)\s+([\d.]+)"')
OPEN_SVG = re.compile(r"(<svg\b[^>]*>)", re.I)
PAPER_MARK = "page-bg"


def paper_layers(width: float, height: float) -> str:
    w, h = int(float(width)), int(float(height))
    return (f'\n{handraw.svg_defs(w, h)}\n'
            f'<rect class="page-bg" width="{w}" height="{h}" fill="url(#bgL)"/>\n'
            f'<rect class="page-grain" width="{w}" height="{h}" fill="url(#dots)"/>\n'
            f'<rect class="page-vig" width="{w}" height="{h}" fill="url(#vig)"/>\n'
            f'<rect class="page-hdr" width="{w}" height="72" fill="url(#hdr)"/>\n'
            f"{handraw.token_css()}\n")


def finalize(svg: str, title: str | None = None) -> str:
    view = VIEWBOX.search(svg)
    if view is None:
        raise ValueError("缺少 viewBox，无法注入纸面")
    width, height = float(view.group(1)), float(view.group(2))
    if PAPER_MARK not in svg:
        svg = OPEN_SVG.sub(lambda m: m.group(1) + paper_layers(width, height),
                           svg, count=1)
    svg = handraw.retint(svg)
    svg = handraw.stroke_only(handraw.bow_lines(svg))
    if title and "KaiTi" not in svg:  # 已装饰过就不再叠加第二道划线
        svg = handraw.title_decor(svg, int(width), title)
    return svg


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("mode", choices=["finalize"])
    ap.add_argument("files", nargs="+", type=Path)
    ap.add_argument("--title", help="标题文案（标题几何匹配时才加装饰）")
    args = ap.parse_args(argv)
    failed = 0
    for path in args.files:
        try:
            text = finalize(path.read_text(encoding="utf-8"), args.title)
        except ValueError as exc:
            print(f"FAIL {path.name}: {exc}")
            failed += 1
            continue
        path.write_text(text, encoding="utf-8")
        print(f"ok   {path}  ({len(text)} bytes)")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())

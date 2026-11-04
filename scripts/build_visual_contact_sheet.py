#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成视觉接触表：一页看 12~24 张图，带 manifest 元数据与评分栏。

用法：
  python scripts/build_visual_contact_sheet.py --wave ch17 \
      --out docs/superpowers/visual/reviews/contact-ch17.html
不指定 --wave 时收录 manifest 里所有非 legacy 的 figure 条目。
"""
from __future__ import annotations

import argparse
import html
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "docs" / "superpowers" / "visual" / "visual-manifest.yml"
DIMS = ["教学必要性", "事实精度", "构图层级", "风格一致性", "印刷可读性"]

CSS = """body{background:#f6eedb;color:#16202b;font-family:"Segoe UI",
"Microsoft YaHei",sans-serif;margin:24px}
h1{font-size:20px;margin:0 0 4px}p.lead{color:#5b666f;margin:0 0 20px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(430px,1fr));
gap:18px}
figure{margin:0;background:#fffdf8;border:1px solid #e0d3b8;border-radius:12px;
padding:12px}
figure img{width:100%;height:auto;display:block;border-radius:8px}
figcaption{font-size:13px;line-height:1.5;margin-top:8px}
.meta{color:#5b666f;font-size:12px;margin-top:6px}
table{width:100%;border-collapse:collapse;font-size:12px;margin-top:8px}
td,th{border:1px solid #e0d3b8;padding:2px 6px;text-align:center}
"""


def rel(path: Path) -> str:
    return "../../../../" + path.relative_to(ROOT).as_posix()


def card(asset: dict) -> str:
    out = ROOT / asset["output"]
    title = asset.get("purpose", "")
    rows = "".join(f"<th>{d}</th>" for d in DIMS)
    cells = "".join("<td> </td>" for _ in DIMS)
    return f"""<figure>
<img src="{rel(out)}" alt="{html.escape(title)}">
<figcaption><b>{html.escape(asset['id'])}</b> · {html.escape(title)}
<div class="meta">ch{asset['chapter']} · {asset['type']} · {asset['layout_id']}
 · {asset['status']}</div>
<table><tr>{rows}</tr><tr>{cells}</tr></table></figcaption>
</figure>"""


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--wave", default="", help="只收 id 以该前缀开头的条目")
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args(argv)
    data = yaml.safe_load(MANIFEST.read_text(encoding="utf-8")) or {}
    assets = [a for a in data.get("assets") or []
              if a.get("kind") in ("figure", "animation")
              and a.get("status") != "legacy-unreviewed"
              and a.get("id", "").startswith(args.wave)]
    cards = "\n".join(card(a) for a in assets)
    doc = (f"<!doctype html><meta charset='utf-8'><title>视觉接触表 "
           f"{html.escape(args.wave)}</title><style>{CSS}</style>"
           f"<h1>视觉接触表 · {html.escape(args.wave or '全部新图')}"
           f"（{len(assets)} 张）</h1>"
           f"<p class='lead'>逐项打 1–5 分；任一维度 &lt;4 返工。"
           f"评分回填 visual-manifest.yml 的 review_scores。</p>"
           f"<div class='grid'>{cards}</div>\n")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(doc, encoding="utf-8")
    print(f"{len(assets)} 张 → {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

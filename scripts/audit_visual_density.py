#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""文字量规：环形隧道口，径口按标准取值，冰背方向由环境决定。

口径（与规格书 2026-11-04 基线对齐，冻结在
docs/superpowers/visual/baseline-2026-11-04.json）：
- 视觉锚点 = 正文里实际内嵌的 `<img src="assets/...">` 或 Markdown 图片
  `![alt](assets/...)`。链接、表格、公式、计算器不算锚点。
- 字符 = 章节文件原文的非空白字符（含图片标签、标记符、表格竖线）。
- 无图段 = 相邻两个锚点之间（含章首到首锚点、末锚点到章尾）的非空白字符；
  锚点标签本身不计——量的是读者要读的字，不是标签。

闸（`--gate`）：章视觉数 < 预算、最长无图段 > 1500、H2 段 > 800 字无图、
相邻锚点 < 400 字且中间无三级标题（堆图）→ 退出码 1。
> 1200 字的无图段只警告。报告模式永远退出 0。
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
CHAPTER_GLOB = "p*-ch*.md"
# `docs/` 里还有 p0-08-cheatsheet.md、p9-12-changelog.md 这类同前缀非章节文件，
# glob 挡不住，用文件名正则把真正的 `-chNN.md` 挑出来。
CHAPTER_NAME = re.compile(r"-ch(\d+)\.md$")

HARD_MAX_GAP = 1500
WARN_MAX_GAP = 1200
MIN_SPACING = 400
H2_MAX_TEXT = 800

# 规格 §4 每章最低视觉锚点预算。
BUDGETS = {0: 18, 1: 18, 2: 22, 3: 24, 4: 18, 5: 18, 6: 18, 7: 20,
           8: 32, 9: 18, 10: 24, 11: 26, 12: 18, 13: 18, 14: 22,
           15: 24, 16: 18, 17: 18, 18: 18}

FENCE = re.compile(r"^(?:```|~~~).*?^(?:```|~~~)[ \t]*$", re.M | re.S)
COMMENT = re.compile(r"<!--.*?-->", re.S)
ANCHOR = re.compile(
    r'<img\b[^>]*\bsrc\s*=\s*["\'](assets/[^"\']+)["\'][^>]*>'
    r"|!\[[^\]]*\]\((assets/[^)]+)\)", re.I)
H2 = re.compile(r"^## ", re.M)
H3 = re.compile(r"^### ", re.M)


def chapters() -> list[Path]:
    return sorted((p for p in DOCS.glob(CHAPTER_GLOB) if CHAPTER_NAME.search(p.name)),
                  key=chapter_no)


def chapter_no(path: Path) -> int:
    m = CHAPTER_NAME.search(path.name)
    if m is None:
        raise ValueError(f"不是章节文件名：{path.name}")
    return int(m.group(1))


def nonws(text: str) -> int:
    return sum(1 for ch in text if not ch.isspace())


def _blank(match: re.Match) -> str:
    """等长空白替换：偏移不变，围栏/注释里的图片不再被当成锚点。"""
    return re.sub(r"\S", " ", match.group(0))


def load(path: Path) -> tuple[str, list[tuple[int, str]], int]:
    """返回 (哨兵化原文, 锚点[(哨兵偏移, 资源路径)], 原文非空白字符数)。

    锚点标签换成 `\x00`，其余原文一字不动，供间距与小节测量；字符数另按
    整份原文统计，与 `baseline-2026-11-04.json` 的冻结口径一致。
    """
    raw = path.read_text(encoding="utf-8")
    masked = COMMENT.sub(_blank, FENCE.sub(_blank, raw))
    out: list[str] = []
    anchors: list[tuple[int, str]] = []
    pos = size = 0
    for m in ANCHOR.finditer(masked):
        out.append(raw[pos:m.start()])
        size += len(out[-1])
        anchors.append((size, m.group(1) or m.group(2)))
        out.append("\x00")
        size += 1
        pos = m.end()
    out.append(raw[pos:])
    return "".join(out), anchors, nonws(raw)


def gaps(text: str) -> list[int]:
    return [nonws(part) for part in text.split("\x00")]


def clusters(text: str) -> int:
    """相邻锚点 < 400 字且中间无三级标题 → 堆图。"""
    bad = 0
    for m1, m2 in zip(list(re.finditer(r"\x00", text)),
                      list(re.finditer(r"\x00", text))[1:]):
        middle = text[m1.end():m2.start()]
        if nonws(middle) < MIN_SPACING and not H3.search(middle):
            bad += 1
    return bad


def h2_gaps(text: str) -> list[dict]:
    """二级小节超过 800 字且零锚点 → 失败项。"""
    hits = []
    heads = [m.start() for m in H2.finditer(text)]
    if not heads:
        return hits
    heads.append(len(text))
    for i in range(len(heads) - 1):
        body = text[heads[i]:heads[i + 1]]
        if nonws(body) > H2_MAX_TEXT and "\x00" not in body:
            title = body.splitlines()[0].lstrip("# ").strip()[:40]
            hits.append({"title": title, "chars": nonws(body)})
    return hits


def label(path: Path) -> str:
    """树内文件报相对路径；夹具临时目录报文件名。"""
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.name


def audit(path: Path) -> dict:
    text, anchors, chars = load(path)
    seg = gaps(text)
    n = chapter_no(path)
    return {
        "file": label(path),
        "chapter": n,
        "chars": chars,
        "visuals": len(anchors),
        "budget": BUDGETS[n],
        "longest_gap": max(seg) if seg else 0,
        "warn_gaps": sum(1 for g in seg if g > WARN_MAX_GAP),
        "hard_gaps": sum(1 for g in seg if g > HARD_MAX_GAP),
        "gaps": seg,
        "clusters": clusters(text),
        "h2_no_visual": h2_gaps(text),
        "assets": [src for _off, src in anchors],
    }


def row(r: dict) -> str:
    return (f"ch{r['chapter']:<2} 字符={r['chars']:>6} 视觉={r['visuals']:>3}/"
            f"{r['budget']:<3} 最长无图段={r['longest_gap']:>5} "
            f"警告={r['warn_gaps']:<2} 堆图={r['clusters']:<2} "
            f"H2无图={len(r['h2_no_visual'])}")


def failures(rows: list[dict]) -> list[str]:
    bad = []
    for r in rows:
        tag = r["file"]
        if r["visuals"] < r["budget"]:
            bad.append(f"{tag}: 视觉 {r['visuals']} < 预算 {r['budget']}")
        if r["longest_gap"] > HARD_MAX_GAP:
            bad.append(f"{tag}: 最长无图段 {r['longest_gap']} > {HARD_MAX_GAP}")
        if r["clusters"]:
            bad.append(f"{tag}: {r['clusters']} 处堆图（相邻 < {MIN_SPACING} 字）")
        for h in r["h2_no_visual"]:
            bad.append(f"{tag}: H2「{h['title']}」{h['chars']} 字零视觉")
    return bad


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--gate", action="store_true", help="按预算与间距闸判失败")
    ap.add_argument("--json", type=Path, help="写出完整统计 JSON")
    ap.add_argument("--chapter", type=int, action="append", help="只看某章")
    args = ap.parse_args(argv)
    files = chapters()
    if args.chapter:
        files = [f for f in files if chapter_no(f) in set(args.chapter)]
    rows = [audit(f) for f in files]
    for r in rows:
        print(row(r))
    total = sum(r["visuals"] for r in rows)
    print(f"合计：{len(rows)} 章 视觉 {total} 字符 "
          f"{sum(r['chars'] for r in rows)}")
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps({"chapters": rows}, ensure_ascii=False,
                                        indent=1) + "\n", encoding="utf-8")
        print(f"JSON → {args.json}")
    if args.gate:
        bad = failures(rows)
        for line in bad:
            print("FAIL " + line)
        print(f"闸：{'FAIL' if bad else 'PASS'}（{len(bad)} 项）")
        return 1 if bad else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())

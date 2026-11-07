#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 manifest 中已验收但正文未引用的插图落到对应小节。

按图内标题与副题做语义就近放置，落点用密度闸自己的口径复验：图两侧的阅读间距
不小于 MIN_GAP，且插入不会把某一段无图文字顶过硬上限。默认只报告，`--write` 才改正文。
"""
from __future__ import annotations

import argparse
import html
import re
import sys
from pathlib import Path

import yaml

import audit_visual_density as avd

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "docs/superpowers/visual/visual-manifest.yml"
MIN_GAP = 450
MAX_GAP = avd.HARD_MAX_GAP
HEADING = re.compile(r"^(#{2,4})\s+(.+?)\s*$")
CAPTION = re.compile(r"<figcaption\b[^>]*>(.*?)</figcaption>", re.S | re.I)
TEXT = re.compile(r"<text[^>]*>(.*?)</text>", re.S)
TAG = re.compile(r"<[^>]+>")
STOP = set("的了和与在是把被为这那有也就都而及或一个我们你们他们它其之与从对到把被让给用")


def chapters() -> dict[int, Path]:
    found = {}
    for path in sorted((ROOT / "docs").glob("p*-ch*.md")):
        m = re.search(r"-ch(\d+)\.md$", path.name)
        if m:
            found[int(m.group(1))] = path
    return found


def svg_texts(asset: dict) -> list[str]:
    path = ROOT / asset["output"]
    if not path.is_file():
        return []
    raw = path.read_text(encoding="utf-8")
    out = []
    for item in TEXT.findall(raw):
        text = html.unescape(TAG.sub("", item)).strip()
        text = re.sub(r"\s+", " ", text)
        if text:
            out.append(text)
    return out


def caption(asset: dict) -> str:
    texts = svg_texts(asset)
    if texts:
        title = texts[0].strip("。； ")
        subtitle = ""
        for candidate in texts[1:4]:
            if len(candidate) >= 10:
                subtitle = candidate.strip("。； ")
                break
        result = title + "。" + subtitle if subtitle else title + "。"
        return result
    return str(asset.get("purpose") or asset["id"]) + "。"


def terms(asset: dict) -> set[str]:
    raw = " ".join([caption(asset), str(asset.get("purpose") or ""),
                    str(asset.get("alt") or "")])
    chars = re.sub(r"[^\u4e00-\u9fffA-Za-z0-9]", "", raw)
    grams = {chars[i:i + 2] for i in range(len(chars) - 1)}
    return {g for g in grams if not set(g) <= STOP}


def blocks(text: str) -> list[dict]:
    """按空行切块，记录每块的起止与类型。"""
    result = []
    inside = False
    pos = 0
    current = []
    start = 0
    for line in text.splitlines(keepends=True):
        stripped = line.strip()
        if stripped.startswith("```"):
            if not inside:
                if current:
                    result.append(_block(current, start))
                    current = []
                inside = True
                start = pos
            else:
                current.append(line)
                result.append(_block(current, start))
                current = []
                inside = False
                start = pos + len(line)
                pos += len(line)
                continue
        if inside:
            current.append(line)
        elif not stripped:
            if current:
                result.append(_block(current, start))
                current = []
            start = pos + len(line)
        else:
            if not current:
                start = pos
            current.append(line)
        pos += len(line)
    if current:
        result.append(_block(current, start))
    return result


def _block(lines: list[str], start: int) -> dict:
    return {"start": start, "end": start + sum(len(x) for x in lines),
            "text": "".join(lines), "kind": classify("".join(lines))}


def classify(text: str) -> str:
    stripped = text.strip()
    for line in stripped.splitlines():
        if HEADING.match(line.strip()):
            return "heading"
    if stripped.startswith("```"):
        return "code"
    if stripped.startswith("<figure") or stripped.startswith("<img"):
        return "figure"
    if stripped.startswith("|") or stripped.startswith("$$") or stripped.startswith("<"):
        return "other"
    return "text"


def anchor_number(anchor: str) -> str:
    m = re.match(r"^(\d+(?:\.\d+)+)", str(anchor).strip())
    return m.group(1) if m else str(anchor).strip()


def section(text: str, anchor: str) -> tuple[int, int] | None:
    target = anchor_number(anchor)
    heads = []
    offset = 0
    for line in text.splitlines(keepends=True):
        m = HEADING.match(line.strip())
        if m:
            heads.append((offset, len(m.group(1)), m.group(2), len(line)))
        offset += len(line)
    for index, (start, level, title, width) in enumerate(heads):
        if not (title.startswith(target) or target in title[:len(target) + 2]):
            continue
        end = len(text)
        for later, later_level, _later_title, _w in heads[index + 1:]:
            if later_level <= level:
                end = later
                break
        return start + width, end
    return None


def sides(cand: str, src: str) -> tuple[int, int, int, int | None, int | None] | None:
    """把 src 当成已在场，返回它的 (起, 止, 原文长度, 左邻居止, 右邻居起)。

    左邻居为 None 表示这是全章第一张图——左侧是章首，只受硬上限约束，闸不算它堆图。
    """
    marks = avd.anchor_matches(cand)
    hit = [i for i, mark in enumerate(marks) if mark[2] == src]
    if len(hit) != 1:
        return None
    i = hit[0]
    return (marks[i][0], marks[i][1], len(cand),
            marks[i - 1][1] if i else None,
            marks[i + 1][0] if i + 1 < len(marks) else None)


def placement_ok(text: str, pos: int, asset: dict) -> bool:
    """插入这张图之后，它左右两段读数仍然过堆图与断层两关。

    说明文字记在图的右侧，所以段落末尾插入等于把 figcaption 全压进右段账上。
    """
    host = host_gap(text, pos)
    cand = text[:pos] + "\n" + figure_block(asset) + text[pos:]
    span = sides(cand, str(asset["output"]))
    if span is None:
        return False
    start, end, _size, left, right = span
    for seg, bounded in ((cand[(left or 0):start], left is not None),
                         (cand[end:(right if right is not None else len(cand))],
                          right is not None)):
        chars = avd.nonws(seg)
        if chars > MAX_GAP or (host > MAX_GAP and chars >= host):
            return False
        if bounded and chars < MIN_GAP and not avd.H3.search(seg):
            return False
    return True


def host_gap(text: str, pos: int) -> int:
    """pos 落在哪一段无图文字里、那段有多长——长段优先切开。"""
    marks = avd.anchor_matches(text)
    left = max((end for _s, end, _p in marks if end <= pos), default=0)
    right = min((start for start, _e, _p in marks if start >= pos), default=len(text))
    return avd.nonws(text[left:right])


def best_insertion(text: str, asset: dict) -> int | None:
    window = section(text, str(asset.get("anchor") or ""))
    if not window:
        return None
    start, end = window
    want = terms(asset)
    candidates = []
    for block in blocks(text):
        if block["kind"] != "text" or not (start <= block["start"] < end):
            continue
        body = re.sub(r"[^\u4e00-\u9fffA-Za-z0-9]", "", block["text"])
        grams = {body[i:i + 2] for i in range(max(0, len(body) - 1))}
        overlap = len(want & grams)
        score = overlap / (1 + len(body) / 900)
        pos = block["end"]
        candidates.append((score, host_gap(text, pos),
                           1 / (1 + abs(pos - start) / 2500), pos))
    candidates.sort(reverse=True)
    for _overlap, _gap, _near, pos in candidates:
        if placement_ok(text, pos, asset):
            return pos
    return None


def figure_block(asset: dict) -> str:
    if asset.get("block"):
        return asset["block"] if asset["block"].endswith("\n") else asset["block"] + "\n"
    alt = html.escape(str(asset.get("alt") or ""), quote=True)
    cap = html.escape(caption(asset))
    return (f'<figure>\n<img src="{asset["output"]}" width="720" alt="{alt}">\n'
            f"<figcaption>{cap}</figcaption>\n</figure>\n\n")


def pending(data: dict) -> dict[int, list[dict]]:
    docs = chapters()
    all_text = "\n".join(path.read_text(encoding="utf-8") for path in docs.values())
    grouped: dict[int, list[dict]] = {}
    for asset in data.get("assets") or []:
        if asset.get("status") not in ("accepted", "published"):
            continue
        if asset.get("kind") != "figure" or asset.get("generator") == "legacy":
            continue
        if asset.get("reviewed_by") != "agent-proxy":
            continue
        if asset["output"] in all_text or Path(asset["output"]).name in all_text:
            continue
        grouped.setdefault(asset.get("chapter"), []).append(asset)
    return grouped


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--chapter", type=int)
    args = ap.parse_args(argv)

    data = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
    docs = chapters()
    grouped = pending(data)
    total = 0
    for ch in sorted(grouped):
        if args.chapter and ch != args.chapter:
            continue
        path = docs.get(ch)
        if not path:
            print(f"SKIP ch{ch}: 找不到正文")
            continue
        text = path.read_text(encoding="utf-8")
        placed = 0
        for asset in grouped[ch]:
            pos = best_insertion(text, asset)
            if pos is None:
                print(f"SKIP {asset['id']}: 锚点 {asset.get('anchor')} 无合法落点")
                continue
            text = text[:pos] + "\n" + figure_block(asset) + text[pos:]
            placed += 1
            total += 1
            print(f"INSERT ch{ch} {asset['id']} @ {pos}")
        if placed and args.write:
            path.write_text(text, encoding="utf-8")
    print(f"共 {'写入' if args.write else '计划'} {total} 张")
    return 0


if __name__ == "__main__":
    sys.exit(main())

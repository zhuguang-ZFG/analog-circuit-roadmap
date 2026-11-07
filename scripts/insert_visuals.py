#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 manifest 中已验收但正文未引用的插图落到对应小节。

按图内标题与副题做语义就近放置，并保证任意两张图之间至少 450 字符，
避免制造新的堆图。默认只报告，`--write` 才改正文。
"""
from __future__ import annotations

import argparse
import html
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "docs/superpowers/visual/visual-manifest.yml"
MIN_GAP = 450
VISUAL = re.compile(r"<img\b[^>]*>", re.I)
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


def visual_offsets(text: str) -> list[int]:
    return [m.start() for m in VISUAL.finditer(text)]


def best_insertion(text: str, asset: dict, taken: list[int]) -> int | None:
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
        candidates.append((score, 1 / (1 + abs(block["start"] - start) / 2500), block["end"]))
    if not candidates:
        return None
    candidates.sort(reverse=True)
    occupied = visual_offsets(text) + taken
    for _overlap, _near, pos in candidates:
        if all(abs(pos - other) >= MIN_GAP for other in occupied):
            return pos
    return None


def figure_block(asset: dict) -> str:
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
        taken: list[int] = []
        inserts: list[tuple[int, str, str]] = []
        for asset in grouped[ch]:
            pos = best_insertion(text, asset, taken)
            if pos is None:
                print(f"SKIP {asset['id']}: 锚点 {asset.get('anchor')} 无可用段落")
                continue
            taken.append(pos)
            inserts.append((pos, figure_block(asset), asset["id"]))
            total += 1
        if not inserts:
            continue
        for pos, block, asset_id in sorted(inserts, reverse=True):
            text = text[:pos] + "\n" + block + text[pos:]
            print(f"INSERT ch{ch} {asset_id} @ {pos}")
        if args.write:
            path.write_text(text, encoding="utf-8")
    print(f"共 {'写入' if args.write else '计划'} {total} 张")
    return 0


if __name__ == "__main__":
    sys.exit(main())

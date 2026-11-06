#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""视觉几何审计：文字出画布 / 文字互压 / 文字越界面框。

用 ElementTree 解析，累加 `<g transform="translate(x y)">` 的位移（本仓只用这一种）。
文字宽度按 CJK 1.0 em、其余 0.55 em 粗估，所以报告是「提示」不是结论：
真压字一定会被这里点到，但点到不一定是真压字，最终以人眼与审图为准。

面板口径：宽 ≥40、高 ≥44 的 `<rect>` 才算面板（更扁的是进度条与分隔带，
标签本来就在条外）。完整落在某个框内的文字属于那个框，不再对它报越界。

用法：
  python scripts/audit_visual_geometry.py                # 审计全部 V4 合成图
  python scripts/audit_visual_geometry.py id1 id2 ...    # 只审计指定图
退出码：0 报告模式；`--gate` 时有缺陷返回 1。
"""
from __future__ import annotations

import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets" / "figures-v2"
FULLWIDTH = '，。、；：（）「」“”？！℃'
# 楷体把这些符号按近似全角出：按 0.55 em 算会低估右边界，实测会漏掉真溢出。
WIDE_SYM = 'Ωµ°±×÷≈≤≥→←↑↓−–—…∥τβθπΔ①②③④⑤'
TRANS = re.compile(r'translate\(\s*([-\d.]+)[\s,]+([-\d.]+)\s*\)')


def width_cjk(value: str, size: float) -> float:
    """粗估文字宽度：CJK/全角 1.0 em，楷体宽符号 0.9 em，其余 0.55 em。"""
    total = 0.0
    for ch in value:
        if '\u4e00' <= ch <= '\u9fff' or ch in FULLWIDTH:
            total += 1.0
        elif ch in WIDE_SYM:
            total += 0.9
        else:
            total += 0.55
    return total * size


def span(x: float, y: float, value: str, size: float, anchor: str) -> tuple:
    w = width_cjk(value, size)
    if anchor == 'middle':
        x0 = x - w / 2
    elif anchor == 'end':
        x0 = x - w
    else:
        x0 = x
    return (x0, y - size * 0.76, x0 + w, y + size * 0.20)


def collect(path: Path):
    """返回 (canvas, texts, panels, polys)，坐标已累加祖先 translate。"""
    tree = ET.parse(path)
    root = tree.getroot()
    vb = root.get('viewBox', '0 0 1000 700').split()
    canvas = (float(vb[2]), float(vb[3]))
    parent = {c: p for p in root.iter() for c in p}
    texts, panels, polys = [], [], []

    def offset(el):
        dx = dy = 0.0
        node = el
        while node in parent:
            m = TRANS.search(node.get('transform') or '')
            if m:
                dx += float(m.group(1))
                dy += float(m.group(2))
            node = parent[node]
        return dx, dy

    for el in root.iter():
        tag = el.tag.split('}')[-1]
        dx, dy = offset(el)
        if tag == 'text':
            size = float(el.get('font-size', 22))
            x = float(el.get('x', 0)) + dx
            y = float(el.get('y', 0)) + dy
            value = ''.join(el.itertext()).strip()
            anchor = el.get('text-anchor', 'start')
            texts.append({'value': value, 'box': span(x, y, value, size, anchor)})
        elif tag == 'rect':
            w, h = float(el.get('width', 0)), float(el.get('height', 0))
            if w >= 40 and h >= 44:          # 细条是进度条/分隔带，不是面板
                panels.append((float(el.get('x', 0)) + dx, float(el.get('y', 0)) + dy, w, h))
        elif tag == 'polyline':
            pts = []
            for pair in (el.get('points') or '').split():
                if ',' in pair:
                    a, b = pair.split(',')[:2]
                    pts.append((float(a) + dx, float(b) + dy))
            if len(pts) >= 2:
                polys.append(pts)
    return canvas, texts, panels, polys


def audit(asset_id: str) -> list:
    canvas, texts, panels, polys = collect(ASSETS / f'{asset_id}.svg')
    defects = []

    def contained(t, p):
        px, py, pw, ph = p
        x0, y0, x1, y1 = t['box']
        return px <= x0 and x1 <= px + pw and py <= y0 and y1 <= py + ph

    for t in texts:
        x0, y0, x1, y1 = t['box']
        if x0 < -1 or y0 < -1 or x1 > canvas[0] + 1 or y1 > canvas[1] + 1:
            defects.append(f'出画布 {t["value"][:22]!r} 右缘={x1:.0f} 画布={canvas[0]:.0f}')

    for i in range(len(texts)):
        for j in range(i + 1, len(texts)):
            a, b = texts[i]['box'], texts[j]['box']
            ox = min(a[2], b[2]) - max(a[0], b[0])
            oy = min(a[3], b[3]) - max(a[1], b[1])
            if ox > 2 and oy > 2:
                defects.append(f'文字互压 {texts[i]["value"][:16]!r} × {texts[j]["value"][:16]!r} '
                               f'交叠 {ox:.0f}×{oy:.0f}')

    for t in texts:
        # 完整落在某个框内的文字属于那个框（子框骑跨父面板是刻意构图）。
        if any(contained(t, p) for p in panels):
            continue
        x0, y0, x1, y1 = t['box']
        for px, py, pw, ph in panels:
            ox = min(x1, px + pw) - max(x0, px)
            oy = min(y1, py + ph) - max(y0, py)
            if ox > 2 and oy > 2:
                defects.append(
                    f'越界面板 {t["value"][:18]!r} 面板=({px:.0f},{py:.0f},{pw:.0f},{ph:.0f})'
                    f' 文字右缘={x1:.0f} 面板右缘={px + pw:.0f}')
    # 文字压曲线：字框内缩 4px 后仍被折线穿过，才算真压（贴边不算）。
    for t in texts:
        x0, y0, x1, y1 = t['box']
        ix0, iy0, ix1, iy1 = x0 + 4, y0 + 4, x1 - 4, y1 - 4
        if ix1 <= ix0 or iy1 <= iy0:
            continue
        for pts in polys:
            hit = False
            for (ax, ay), (bx, by) in zip(pts, pts[1:]):
                steps = max(2, int(max(abs(bx - ax), abs(by - ay)) / 4))
                for s in range(steps + 1):
                    px = ax + (bx - ax) * s / steps
                    py = ay + (by - ay) * s / steps
                    if ix0 <= px <= ix1 and iy0 <= py <= iy1:
                        hit = True
                        break
                if hit:
                    break
            if hit:
                defects.append(f'文字压曲线 {t["value"][:20]!r} 字框=({x0:.0f},{y0:.0f},{x1:.0f},{y1:.0f})')
                break

    return defects


def main() -> int:
    argv = [a for a in sys.argv[1:] if not a.startswith('--')]
    gate = '--gate' in sys.argv[1:]
    ids = argv or sorted(p.stem for p in ASSETS.glob('*.svg')
                         if not p.stem.endswith('-print'))
    bad = 0
    for asset_id in ids:
        d = audit(asset_id)
        if d:
            bad += 1
            print(f'FAIL {asset_id}')
            for line in d:
                print('   ', line)
        else:
            print(f'ok   {asset_id}')
    print(f'\n审计 {len(ids)} 张，有缺陷 {bad} 张')
    return 1 if (bad and gate) else 0


if __name__ == '__main__':
    raise SystemExit(main())

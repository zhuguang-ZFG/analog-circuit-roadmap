#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V2 动画最薄渲染层：场景 → 三件套（主动画 / reduced-motion 静帧 / 打印分镜）。

契约：scene 模块提供 build(timeline) 返回 Layer 列表；
Layer(beat, body, drift)：
  beat=None          常驻层（三件套始终显示）
  beat=拍名          该拍主角层（主动画带 fade 窗口；static 全显；
                     storyboard 按累积态规则出现在对应格）
  drift=(dx,dy)      主角第二层运动（spec §7.3 两层运动），入场时轻位移

主动画：SMIL 单次播放（fill=freeze），结论拍停留不退场。
静帧：无 <animate>，全部层可见 = 结论帧，供 print_fallback/reduced_motion。
分镜：2 列网格，每格画该拍结束态的累积画面 + 拍名 + 字幕。
"""
from __future__ import annotations

import sys
from collections import namedtuple
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1]
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

try:  # 以 scripts.visuals.render 包内模块被加载（scenes 调用路径）
    from scripts import handraw  # noqa: E402
    from scripts.visuals.static_fig import paper_layers  # noqa: E402
    from scripts.visuals.timeline import (  # noqa: E402
        Beat, Timeline, fade_in, fade_out, drift, opacity_window)
except ImportError:  # 直接 python scripts/visuals/render.py 运行
    import handraw  # noqa: E402
    from static_fig import paper_layers  # noqa: E402
    from timeline import (  # noqa: E402
        Beat, Timeline, fade_in, fade_out, drift, opacity_window)

Layer = namedtuple("Layer", "beat body drift", defaults=(None, "", None))


def _header(tl: Timeline) -> str:
    names = "、".join(b.name for b in tl.beats)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'viewBox="0 0 {tl.width} {tl.height}" role="img" '
            f'aria-labelledby="figTitle figDesc">\n'
            f'<title id="figTitle">{tl.title}</title>\n'
            f'<desc id="figDesc">{tl.subtitle}</desc>\n'
            f'<!-- 节拍：{names}；总时长 {tl.duration:g}s；单次播放 -->\n'
            f'{paper_layers(tl.width, tl.height)}\n')


def _titles(tl: Timeline) -> str:
    out = [f'<text x="{tl.width // 2}" y="30" text-anchor="middle" '
           f'font-size="19" font-weight="bold" fill="#16202b">{tl.title}</text>']
    if tl.subtitle:
        out.append(f'<text x="{tl.width // 2}" y="54" text-anchor="middle" '
                   f'font-size="12.5" fill="#5b666f">{tl.subtitle}</text>')
    return "\n".join(out)


def _caption_bar(tl: Timeline) -> str:
    y = tl.height - 40
    parts = [f'<rect x="24" y="{y - 24}" width="{tl.width - 48}" height="34" '
             f'rx="9" fill="#f7eedb" stroke="#c9bb9d" stroke-width="1.2"/>']
    for b in tl.beats:
        parts.append(f'<g opacity="{"1" if b.hold else "0"}">'
                     f'{"" if b.hold else fade_in(b.start)}'
                     f'{fade_out(b.end) if not b.hold and b is not tl.beats[-1] else ""}'
                     f'<text x="{tl.width // 2}" y="{y}" text-anchor="middle" '
                     f'font-size="13" font-weight="bold" fill="{b.color}">{b.caption}</text></g>')
    return "\n".join(parts)


def _animated_layer(layer: Layer, tl: Timeline) -> str:
    beat = tl.beat(layer.beat)
    start, out = opacity_window(tl, beat)
    anims = [fade_in(start)]
    if out is not None:
        anims.append(fade_out(out))
    if layer.drift is not None:
        dx, dy = layer.drift
        anims.append(drift(start, dx, dy))
    return f'<g opacity="0">{layer.body}{"".join(anims)}</g>'

def _visible_at(layer: Layer, tl: Timeline, t: float) -> bool:
    if layer.beat is None:
        return True
    beat = tl.beat(layer.beat)
    start, out = opacity_window(tl, beat)
    return start <= t and (out is None or t <= out)


def static_svg(tl: Timeline, layers: list[Layer]) -> str:
    # 结论帧 = 常驻层 + 最后一拍。变换型动画（波形变形、滑标推移）的
    # 中间拍几何绝不能进 static，否则打印/无 SMIL 环境看到叠帧拼贴。
    final = tl.beats[-1]
    body = [layer.body for layer in layers
            if layer.beat is None or layer.beat == final.name]
    bar = [f'<rect x="24" y="{tl.height - 64}" width="{tl.width - 48}" height="34" '
           f'rx="9" fill="#f7eedb" stroke="#c9bb9d" stroke-width="1.2"/>',
           f'<text x="{tl.width // 2}" y="{tl.height - 40}" text-anchor="middle" '
           f'font-size="13" font-weight="bold" fill="{final.color}">{final.caption}</text>']
    return (_header(tl) + _titles(tl) + "\n"
            + "\n".join(body) + "\n" + "\n".join(bar) + "\n</svg>\n")


def _cell(tl: Timeline, layers: list[Layer], idx: int, cx: int, cy: int,
          cw: int, ch: int) -> str:
    beat = tl.beats[idx]
    t = beat.end
    scale = min(cw / tl.width, (ch - 44) / tl.height)
    inner = [layer.body for layer in layers if _visible_at(layer, tl, t)]
    gx, gy = cx + (cw - tl.width * scale) / 2, cy + 14
    out = [f'<rect x="{cx}" y="{cy}" width="{cw}" height="{ch}" rx="10" '
           f'fill="#fdf8ea" stroke="#c9bb9d" stroke-width="1.2"/>',
           f'<g transform="translate({gx:.0f} {gy:.0f}) scale({scale:.4f})">'
           + "\n".join(inner) + "</g>",
           f'<text x="{cx + 12}" y="{cy + ch - 22}" font-size="12" '
           f'font-weight="bold" fill="{beat.color}">{idx + 1}. {beat.name}</text>',
           f'<text x="{cx + 12}" y="{cy + ch - 6}" font-size="10.5" '
           f'fill="#5b666f">{beat.caption}</text>']
    return "\n".join(out)


def storyboard_svg(tl: Timeline, layers: list[Layer]) -> str:
    beats = list(tl.beats)
    if len(beats) > 5:  # spec §7.3 分镜 3–5 格：前 4 拍各一格，结论拍收尾
        beats = beats[:4] + [beats[-1]]
    cols = 2
    cw = (tl.width - 3 * 20) // cols
    ch = 300
    rows = (len(beats) + cols - 1) // cols
    height = 64 + rows * (ch + 18) + 12
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {tl.width} {height}" '
           f'role="img" aria-labelledby="sbTitle sbDesc">',
           f'<title id="sbTitle">{tl.title}——打印分镜</title>',
           f'<desc id="sbDesc">{len(beats)} 格分镜，每格画该拍结束态</desc>',
           paper_layers(tl.width, height),
           f'<text x="{tl.width // 2}" y="34" text-anchor="middle" font-size="18" '
           f'font-weight="bold" fill="#16202b">{tl.title}·分镜</text>',
           f'<text x="{tl.width // 2}" y="56" text-anchor="middle" font-size="12" '
           f'fill="#5b666f">{tl.subtitle}</text>']
    for i, _ in enumerate(beats):
        r, c = divmod(i, cols)
        out.append(_cell(tl, layers, i if i < 4 else len(tl.beats) - 1,
                         20 + c * (cw + 20), 70 + r * (ch + 18), cw, ch))
    out.append("</svg>\n")
    return "\n".join(out)


def scene_svg(tl: Timeline, layers: list[Layer]) -> str:
    parts = [_header(tl), _titles(tl)]
    for layer in layers:
        parts.append(layer.body if layer.beat is None
                     else _animated_layer(layer, tl))
    parts.append(_caption_bar(tl))
    return "\n".join(parts) + "\n</svg>\n"


def write(tl: Timeline, layers: list[Layer], out_dir: str | Path,
          stem: str) -> list[Path]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    written = []
    for suffix, markup in (("", scene_svg(tl, layers)),
                           ("-static", static_svg(tl, layers)),
                           ("-storyboard", storyboard_svg(tl, layers))):
        path = out / f"{stem}{suffix}.svg"
        path.write_text(markup, encoding="utf-8")
        written.append(path)
    return written

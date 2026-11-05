#!/usr/bin/env python3
"""§8.2 地址跳变：011→100 的路过通道与 INH 对策。"""
from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[2]
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))
if str(SCRIPTS.parent) not in sys.path:
    sys.path.insert(0, str(SCRIPTS.parent))

from scripts.visuals.render import Layer, write  # noqa: E402
from scripts.visuals.timeline import Beat, Timeline  # noqa: E402

RED, BLUE, GREEN, AMBER, PURPLE = "#a8321f", "#1f5d7a", "#3d6b4a", "#a4630f", "#6b3f63"
RED_T, BLUE_T, GREEN_T, AMBER_T = "#f6e7e1", "#e6eff3", "#e8efe6", "#f7eedb"
INK, MUTED, RULE = "#16202b", "#5b666f", "#c9bb9d"


def scene():
    tl = Timeline(
        width=960, height=620, duration=9.0,
        beats=(
            Beat("停在011", 0.0, 1.6, "当前选中通道 3：地址 011 稳定", BLUE),
            Beat("三位抢跑", 1.6, 3.4, "改到 100 时三位不同时翻转，中间态先出现", AMBER),
            Beat("路过111", 3.4, 5.2, "111 短暂导通：无关通道被采进系统", RED),
            Beat("先拉INH", 5.2, 6.8, "先把 INH 拉高全断，再改地址", GREEN),
            Beat("等够再采", 6.8, 9.0, "地址稳定到采样窗开启 ≥ t_ON；格雷码只动一位", PURPLE, hold=True),
        ),
        title="地址跳变的路过通道",
        subtitle="011→100 不是一步到位；INH 与格雷码把中间态关掉",
    )
    persistent = "\n".join((
        f'<rect x="48" y="96" width="864" height="300" rx="14" fill="#f6eedb" stroke="{RULE}" stroke-width="1.4"/>',
        f'<text x="72" y="128" font-size="12" fill="{MUTED}">三位地址时间线</text>',
        f'<line x1="96" y1="230" x2="864" y2="230" stroke="{RULE}" stroke-width="1.6"/>',
        f'<line x1="96" y1="360" x2="864" y2="360" stroke="{RULE}" stroke-width="1.2"/>',
        f'<text x="72" y="386" font-size="12" fill="{MUTED}">选中通道</text>',
        f'<text x="72" y="430" font-size="12" fill="{MUTED}">INH</text>',
        f'<line x1="96" y1="446" x2="864" y2="446" stroke="{RULE}" stroke-width="1.2"/>',
        f'<text x="480" y="480" text-anchor="middle" font-size="12" fill="{MUTED}">时间（切换沿几十 ns 级）</text>',
    ))
    layers = [
        Layer(None, persistent),
        Layer("停在011", "\n".join((
            f'<rect x="120" y="204" width="120" height="52" rx="8" fill="{BLUE_T}" stroke="{BLUE}" stroke-width="2"/>',
            f'<text x="180" y="238" text-anchor="middle" font-size="18" font-weight="bold" fill="{BLUE}">011</text>',
            f'<text x="300" y="238" font-size="13" fill="{INK}">选中通道 3，稳定</text>',
        )), (0, -4)),
        Layer("三位抢跑", "\n".join((
            f'<rect x="340" y="204" width="120" height="52" rx="8" fill="{AMBER_T}" stroke="{AMBER}" stroke-width="2"/>',
            f'<text x="400" y="238" text-anchor="middle" font-size="18" font-weight="bold" fill="{AMBER}">111</text>',
            f'<text x="480" y="238" font-size="13" fill="{INK}">中间态先到</text>',
            f'<rect x="620" y="204" width="120" height="52" rx="8" fill="{AMBER_T}" stroke="{AMBER}" stroke-width="2"/>',
            f'<text x="680" y="238" text-anchor="middle" font-size="18" font-weight="bold" fill="{AMBER}">010</text>',
        )), (0, -4)),
        Layer("路过111", "\n".join((
            f'<rect x="340" y="310" width="120" height="34" rx="6" fill="{RED_T}" stroke="{RED}" stroke-width="2"/>',
            f'<text x="400" y="334" text-anchor="middle" font-size="12.5" font-weight="bold" fill="{RED}">通道 7 先导通</text>',
            f'<text x="480" y="334" font-size="12" fill="{RED}">无关信号短促进入 / 泄一包电荷</text>',
        )), (0, -4)),
        Layer("先拉INH", "\n".join((
            f'<path d="M120,440 L340,440 L340,404 L620,404 L620,440 L864,440" fill="none" stroke="{GREEN}" stroke-width="3"/>',
            f'<text x="690" y="398" font-size="12.5" font-weight="bold" fill="{GREEN}">INH 罩住整个地址跳变</text>',
        )), (0, -4)),
        Layer("等够再采", "\n".join((
            f'<rect x="96" y="508" width="816" height="76" rx="10" fill="{GREEN_T}" stroke="{GREEN}" stroke-width="1.6"/>',
            f'<text x="120" y="538" font-size="13" font-weight="bold" fill="{GREEN}">对策按代价排：先拉 INH → 格雷码 → 采样窗错开 ≥ t_ON</text>',
            f'<text x="120" y="564" font-size="12" fill="{INK}">判据：地址稳定到采样窗开启的间隔 ≥ t_ON，期间不采样。</text>',
        )), (0, -4)),
    ]
    return tl, layers


if __name__ == "__main__":
    tl, layers = scene()
    write(tl, layers, SCRIPTS.parent / "assets" / "svg-v2", "ch08-mux-address-glitch-v2")

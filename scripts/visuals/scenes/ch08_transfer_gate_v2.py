#!/usr/bin/env python3
"""§8.1 传输门动画：单管缺口 → 互补并联 → 双向。"""
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

RED, BLUE, GREEN, AMBER = "#a8321f", "#1f5d7a", "#3d6b4a", "#a4630f"
RED_T, BLUE_T, GREEN_T, AMBER_T = "#f6e7e1", "#e6eff3", "#e8efe6", "#f7eedb"
INK, MUTED, RULE = "#16202b", "#5b666f", "#c9bb9d"


def scene():
    tl = Timeline(
        width=960, height=620, duration=8.0,
        beats=(
            Beat("零水位", 0.0, 1.6, "VIN=0V：N 管全开，P 管没导通", BLUE),
            Beat("顶到4V", 1.6, 3.4, "VIN 升到 4V：N 管压差只剩 VTH，传输停住", AMBER),
            Beat("互补并联", 3.4, 5.6, "P 管接管高段，包络 20→26.7→20Ω 覆盖全摆幅", GREEN),
            Beat("双向与边界", 5.6, 8.0, "源漏对称所以双向；下游门限 2.5V 决定 4V 够不够", RED, hold=True),
        ),
        title="传输门：谁行谁上",
        subtitle="单管有阈值缺口，互补并联才轨到轨",
    )
    persistent = "\n".join((
        f'<rect x="48" y="92" width="864" height="440" rx="14" fill="#f6eedb" stroke="{RULE}" stroke-width="1.4"/>',
        f'<line x1="96" y1="470" x2="864" y2="470" stroke="{RULE}" stroke-width="2"/>',
        f'<text x="96" y="500" font-size="12" fill="{MUTED}">VIN 0V</text>',
        f'<text x="840" y="500" text-anchor="end" font-size="12" fill="{MUTED}">5V</text>',
        f'<line x1="96" y1="470" x2="96" y2="140" stroke="{RULE}" stroke-width="2"/>',
        f'<text x="82" y="132" text-anchor="end" font-size="12" fill="{MUTED}">R_ON</text>',
        f'<line x1="290" y1="136" x2="290" y2="500" stroke="{AMBER}" stroke-width="1.4" stroke-dasharray="5,4"/>',
        f'<text x="290" y="522" text-anchor="middle" font-size="11" fill="{AMBER}">4V</text>',
        f'<line x1="210" y1="136" x2="210" y2="500" stroke="{MUTED}" stroke-width="1.2" stroke-dasharray="3,5"/>',
        f'<text x="210" y="522" text-anchor="middle" font-size="11" fill="{MUTED}">2.5V 门限</text>',
        f'<rect x="48" y="548" width="864" height="48" rx="10" fill="{BLUE_T}" stroke="{BLUE}" stroke-width="1.2"/>',
        f'<text x="72" y="579" font-size="12.5" fill="{INK}">VDD=5V，VTH=1V；N 管管低段、P 管管高段，源漏对称所以双向。</text>',
    ))
    layers = [
        Layer(None, persistent),
        Layer("零水位", "\n".join((
            f'<path d="M96,410 C180,410 250,400 330,360 C410,320 500,260 600,230" fill="none" stroke="{BLUE}" stroke-width="3"/>',
            f'<circle cx="104" cy="410" r="6" fill="{BLUE}"/>',
            f'<text x="116" y="398" font-size="13" font-weight="bold" fill="{BLUE}">N 管 20Ω</text>',
            f'<text x="560" y="210" font-size="12" fill="{MUTED}">P 管未导通</text>',
        )), (0, -4)),
        Layer("顶到4V", "\n".join((
            f'<path d="M96,410 C200,410 260,390 290,220 C300,160 310,140 320,140" fill="none" stroke="{AMBER}" stroke-width="3.4"/>',
            f'<circle cx="290" cy="220" r="7" fill="{AMBER}"/>',
            f'<text x="306" y="206" font-size="13" font-weight="bold" fill="{AMBER}">缺口 = VTH</text>',
            f'<text x="330" y="170" font-size="12" fill="{MUTED}">N 管 R_ON→∞</text>',
        )), (0, -4)),
        Layer("互补并联", "\n".join((
            f'<path d="M96,410 C180,410 240,380 290,300 C350,240 430,300 500,360 C580,410 700,410 864,410" fill="none" stroke="{GREEN}" stroke-width="3.4"/>',
            f'<path d="M96,430 C180,430 240,400 290,320 C350,260 430,320 500,380 C580,430 700,430 864,430" fill="none" stroke="{BLUE}" stroke-width="2" stroke-dasharray="7,5"/>',
            f'<text x="430" y="264" font-size="13" font-weight="bold" fill="{GREEN}">并联包络 20→26.7→20Ω</text>',
        )), (0, -4)),
        Layer("双向与边界", "\n".join((
            f'<rect x="96" y="120" width="360" height="86" rx="10" fill="{RED_T}" stroke="{RED}" stroke-width="1.6"/>',
            f'<text x="116" y="150" font-size="13" font-weight="bold" fill="{RED}">4V 够不够，看下游是谁</text>',
            f'<text x="116" y="176" font-size="12" fill="{INK}">CMOS 门限 2.5V：够用</text>',
            f'<text x="116" y="196" font-size="12" fill="{INK}">轨到轨 ADC：不够</text>',
            f'<path d="M700,250 L820,250 M820,250 L800,236 M820,250 L800,264" stroke="{RED}" stroke-width="2.4" fill="none"/>',
            f'<text x="760" y="230" text-anchor="middle" font-size="12" fill="{RED}">双向</text>',
        )), (0, -4)),
    ]
    return tl, layers


if __name__ == "__main__":
    tl, layers = scene()
    write(tl, layers, SCRIPTS.parent / "assets" / "svg-v2", "ch08-transfer-gate-v2")

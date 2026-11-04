#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""§17.2 虚短探针动画（A5 操作演示）：先量 V- → 再量 V+ → 压差 8mV → 判读。

数字回对正文：8mV。
"""
from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[2]
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from scripts.visuals.render import Layer, write  # noqa: E402
from scripts.visuals.timeline import Beat, Timeline  # noqa: E402

RED, BLUE, AMBER, GREEN = "#a8321f", "#1f5d7a", "#a4630f", "#3d6b4a"
RED_T, BLUE_T, GREEN_T, AMBER_T = "#f6e7e1", "#e6eff3", "#e8efe6", "#f7eedb"
INK, INK2, MUTED, RULE = "#16202b", "#37424e", "#5b666f", "#c9bb9d"


def scene():
    tl = Timeline(
        width=960, height=620, duration=7.5,
        beats=(
            Beat("认脚", 0.0, 1.5, "运放两输入端：V-（反相）与 V+（同相）——虚短验证就从这两个脚开始", BLUE),
            Beat("量V-", 1.5, 3.0, "第一步：表笔落 V-，读数 2.500V", BLUE),
            Beat("量V+", 3.0, 4.5, "第二步：表笔落 V+，读数 2.508V", RED),
            Beat("算压差", 4.5, 6.0, "压差 = 2.508 - 2.500 = 8mV，远小于供电轨", AMBER),
            Beat("判读", 6.0, 7.5, "虚短成立，运放与反馈链工作正常——问题不在这里", GREEN, hold=True),
        ),
        title="虚短探针：两次读数判运放死活",
        subtitle="两输入端压差 8mV——虚短成立，问题不在运放",
    )
    persistent = "\n".join((
        f'<polygon points="380,180 380,320 560,250" fill="#f6eedb" stroke="{INK2}" stroke-width="2.2"/>',
        f'<line x1="300" y1="210" x2="380" y2="210" stroke="{INK}" stroke-width="2.2"/>',
        f'<line x1="300" y1="290" x2="380" y2="290" stroke="{INK}" stroke-width="2.2"/>',
        f'<line x1="560" y1="250" x2="640" y2="250" stroke="{INK}" stroke-width="2.2"/>',
        f'<text x="352" y="202" font-size="14" font-weight="bold" fill="{INK}">-</text>',
        f'<text x="352" y="298" font-size="14" font-weight="bold" fill="{INK}">+</text>',
        f'<text x="470" y="256" text-anchor="middle" font-size="12.5" fill="{MUTED}">运放</text>',
        f'<text x="300" y="180" text-anchor="middle" font-size="12.5" font-weight="bold" fill="{BLUE}">V-</text>',
        f'<text x="300" y="326" text-anchor="middle" font-size="12.5" font-weight="bold" fill="{RED}">V+</text>',
        f'<rect x="660" y="120" width="260" height="110" rx="12" fill="#f6eedb" stroke="{RULE}" stroke-width="1.4"/>',
        f'<text x="684" y="150" font-size="12.5" font-weight="bold" fill="{INK2}">万用表</text>',
        f'<text x="684" y="184" font-size="12" fill="{MUTED}">V- 读数：-</text>',
        f'<text x="684" y="212" font-size="12" fill="{MUTED}">V+ 读数：-</text>',
    ))
    layers = [
        Layer(None, persistent),
        Layer("量V-", "\n".join((
            f'<circle cx="340" cy="210" r="9" fill="{BLUE_T}" stroke="{BLUE}" stroke-width="2"/>',
            f'<text x="660" y="184" font-size="14" font-weight="bold" fill="{BLUE}">V- 读数：2.500V</text>',
        )), (0, -6)),
        Layer("量V+", "\n".join((
            f'<circle cx="340" cy="290" r="9" fill="{RED_T}" stroke="{RED}" stroke-width="2"/>',
            f'<text x="660" y="212" font-size="14" font-weight="bold" fill="{RED}">V+ 读数：2.508V</text>',
        )), (0, -6)),
        Layer("算压差", "\n".join((
            f'<rect x="660" y="244" width="260" height="52" rx="10" fill="{AMBER_T}" stroke="{AMBER}" stroke-width="1.8"/>',
            f'<text x="684" y="276" font-size="14" font-weight="bold" fill="{AMBER}">压差 2.508 - 2.500 = 8mV</text>',
        )), (8, 0)),
    ] + _beat_layers()
    return tl, layers


def _beat_layers():
    return [
        Layer("判读", "\n".join((
            f'<rect x="60" y="400" width="840" height="120" rx="12" fill="{GREEN_T}" stroke="{GREEN}" stroke-width="2"/>',
            f'<text x="84" y="436" font-size="14" font-weight="bold" fill="{GREEN}">判读：压差 8mV 远小于几十 mV 阈值 → 虚短成立</text>',
            f'<text x="84" y="466" font-size="12.5" fill="{INK}">运放两输入端近似等电位，反馈在正常工作——问题不在运放，</text>',
            f'<text x="84" y="490" font-size="12.5" fill="{INK}">嫌疑移交：供电、前级信号、输出负载。</text>',
        )), (0, -4)),
    ]


if __name__ == "__main__":
    tl, layers = scene()
    write(tl, layers, SCRIPTS / "assets" / "svg-v2", "ch17-virtual-short-probe")

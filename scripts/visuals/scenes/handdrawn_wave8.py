"""Wave 8 手绘草图：早期章节的选型与边界（ch1/ch4/ch5/ch7/ch9）。"""
from __future__ import annotations

from scripts.visuals.scenes.handdrawn_wave2 import (
    AMBER, BLUE, GREEN, INK, INK2, PAPER, RED, RULE, arrow, box, header, text,
)


def e24_ladder():
    parts = [header('算出来 3.285k，货架只有 3.3k',
                    'E24 每十倍频程 24 档，相邻档约 1.1 倍；±5% 容差把真实值收进档位窗。')]
    parts.append(box(50, 140, 420, 300, fill=PAPER))
    parts.append(text(74, 182, '算出来的值', 24, colour=AMBER, weight='700'))
    parts.append(text(74, 246, '3.285k', 46, weight='700'))
    parts.append(text(74, 300, 'E24 货架档', 24, colour=GREEN, weight='700'))
    parts.append(text(74, 364, '3.3k', 46, colour=GREEN, weight='700'))
    parts.append(text(74, 414, '误差落在 ±5% 窗内', 22, colour=INK2))
    parts.append(arrow(480, 300, 540, 300))
    parts.append(box(550, 140, 400, 300, fill=PAPER))
    for i, (head, note, col) in enumerate([
            ('24 档', '每十倍频程', INK2),
            ('约 1.1 倍', '相邻档位比', INK2),
            ('±5%', '与容差对齐', GREEN),
            ('E96 → ±1%', '需要更准时换系列', BLUE)]):
        y = 190 + i * 62
        parts.append(text(576, y, head, 26, colour=col, weight='700'))
        parts.append(text(576, y + 28, note, 22, colour=INK2))
    parts.append(box(50, 480, 900, 120, fill=PAPER))
    parts.append(text(76, 522, '先选系列再选值；货架上没有 3.285k。', 24, weight='700'))
    parts.append(text(76, 562, '需要更准：两只串并联，或用电位器校准。', 22, colour=INK2))
    parts.append(text(500, 650, '3.285k → 3.3k，不是偷懒，是按系列落档。', 22,
                      colour=AMBER, anchor='middle', weight='700'))
    return parts


def gate_window():
    parts = [header('栅极保护是一扇电压窗',
                    '钳位要高于驱动、低于栅氧额定；窗口外面不是余量，是击穿。')]
    parts.append(box(50, 140, 520, 360, fill=PAPER))
    bands = [
        (176, '栅氧额定 ±20 V', RED, '#f3ddd7'),
        (276, '钳位 13–16 V', AMBER, '#f6e6d2'),
        (376, '驱动 12 V', GREEN, '#e2ebe0'),
    ]
    for y, label, col, tint in bands:
        parts.append(f'<rect x="74" y="{y}" width="470" height="70" rx="8" fill="{tint}" stroke="{col}" stroke-width="2"/>')
        parts.append(text(96, y + 44, label, 27, colour=col, weight='700'))
    parts.append(text(74, 478, '钳位动作点必须落在这两条线之间。', 22, colour=INK2))
    parts.append(box(600, 140, 350, 360, fill=PAPER))
    rows = [
        ('钳位 > 驱动', '动作电压高于 12 V'),
        ('钳位 < 额定', '又低于 ±20 V'),
        ('10 kΩ 下拉', '悬空态有直流退路'),
        ('开尔文源脚', '源极电感不进栅回路'),
    ]
    for i, (head, note) in enumerate(rows):
        y = 190 + i * 76
        parts.append(text(624, y, head, 23, weight='700'))
        parts.append(text(624, y + 28, note, 22, colour=INK2))
    parts.append(box(50, 530, 900, 76, fill=PAPER))
    parts.append(text(76, 578, '12 V 驱动选 13–16 V 钳位，别让栅氧裸奔。', 24,
                      weight='700', colour=AMBER))
    parts.append(text(500, 650, '先看窗口，再选钳位器件。', 22, colour=INK2,
                      anchor='middle'))
    return parts


def deadtime_ledger():
    parts = [header('死区不是零成本，是一笔明账',
                    '体二极管顶班期间，压降从 0.15 V 变 0.8 V；损耗按占空比照付。')]
    parts.append(box(50, 140, 500, 300, fill=PAPER))
    for i, line in enumerate([
            'P_dt ≈ V_SD × I_D',
            '× (t_d,on + t_d,off) × f_sw',
            '= 0.8 V × 5 A × 100 ns × 100 kHz',
            '≈ 0.4 W']):
        parts.append(text(76, 194 + i * 62, line, 25 if i < 2 else 23,
                          weight='700' if i == 3 else '400',
                          colour=AMBER if i == 3 else INK))
    parts.append(box(580, 140, 370, 300, fill=PAPER))
    parts.append(text(604, 186, '同一只管子', 24, weight='700'))
    parts.append(text(604, 232, '沟道：5 A × 30 mΩ', 22))
    parts.append(text(604, 264, '= 0.15 V', 22, colour=GREEN, weight='700'))
    parts.append(text(604, 322, '体二极管：0.8 V', 22))
    parts.append(text(604, 354, '死区里由它说了算', 22, colour=RED, weight='700'))
    parts.append(text(604, 404, '差的那截压降全是热。', 22, colour=INK2))
    parts.append(box(50, 480, 900, 100, fill=PAPER))
    parts.append(text(76, 524, '死区压到几十纳秒，但不能压到零；', 23, weight='700'))
    parts.append(text(76, 556, '压到零就是上下管直通，4.5 节的炸管行。', 22, colour=INK2))
    parts.append(text(500, 650, '死区用损耗买安全，价格要算清。', 22, colour=AMBER,
                      anchor='middle'))
    return parts


def rp_window():
    parts = [header('上拉电阻是一道合围题',
                    '3.3 V / 100 pF / 快速模式：窗口 967 Ω 到 3.5 kΩ，取中间 2.2k。')]
    parts.append(box(50, 140, 430, 100, fill=PAPER))
    parts.append(text(74, 178, '驱动下限', 22, colour=GREEN, weight='700'))
    parts.append(text(74, 214, 'R ≥ (3.3−0.4)/3 mA = 967 Ω', 22))
    parts.append(box(520, 140, 430, 100, fill=PAPER))
    parts.append(text(544, 178, '速度上限', 22, colour=BLUE, weight='700'))
    parts.append(text(544, 214, 'R ≤ 300 ns/(0.8473×100 pF) = 3.5 kΩ', 22))
    # 窗口条
    parts.append(f'<rect x="220" y="300" width="540" height="34" rx="8" fill="#e2ebe0" stroke="{GREEN}" stroke-width="2"/>')
    parts.append(f'<line x1="100" y1="317" x2="900" y2="317" stroke="{RULE}" stroke-width="2"/>')
    for x, label in ((220, '967 Ω'), (500, '2.2k'), (760, '3.5 kΩ')):
        parts.append(f'<line x1="{x}" y1="288" x2="{x}" y2="346" stroke="{INK2}" stroke-width="2"/>')
        parts.append(text(x, 278, label, 24, anchor='middle', weight='700'))
    parts.append(text(500, 380, '实板常用 2.2k：两头都留余量', 23, colour=GREEN,
                      anchor='middle', weight='700'))
    parts.append(text(500, 424, '99kΩ 漏电上限在这条总线上不卡', 22, colour=INK2,
                      anchor='middle'))
    parts.append(box(50, 480, 900, 100, fill=PAPER))
    parts.append(text(76, 522, '任何一条约束变了，先重跑这道围合，再动电阻。', 23, weight='700'))
    parts.append(text(76, 556, '总线电容、模式等级、器件数量，都会改写窗口。', 22, colour=INK2))
    parts.append(text(500, 650, '先算窗口，再选阻值；2.2k 是结果，不是口诀。', 22,
                      colour=AMBER, anchor='middle'))
    return parts


def tristate_handover():
    parts = [header('三态交接：先闭嘴，再转身，后开口',
                    '释放到高阻要 tDIS，使能要 tEN；窗口重叠 10 ns 就是一次微型对撞。')]
    parts.append(box(60, 220, 260, 110, fill=PAPER))
    parts.append(text(80, 264, '驱动器 A', 24, weight='700'))
    parts.append(text(80, 300, '释放 / 进入高阻', 22, colour=INK2))
    parts.append(box(340, 220, 300, 110, fill=PAPER))
    parts.append(text(360, 264, '空档：tDIS 10–30 ns', 23, colour=AMBER, weight='700'))
    parts.append(text(360, 300, '没人驱动，总线靠电容保持', 22, colour=INK2))
    parts.append(box(660, 220, 280, 110, fill=PAPER))
    parts.append(text(680, 264, '驱动器 B', 24, weight='700'))
    parts.append(text(680, 300, '使能 / 开始驱动', 22, colour=INK2))
    parts.append(arrow(324, 275, 336, 275))
    parts.append(arrow(644, 275, 656, 275))
    parts.append(box(60, 390, 880, 100, fill=PAPER))
    parts.append(text(84, 432, '重叠 10 ns：A 还没退，B 已开口', 23, colour=RED, weight='700'))
    parts.append(text(84, 464, '结果不是“晚一点”，而是一串微秒级电流尖峰。', 22, colour=INK2))
    parts.append(box(60, 530, 880, 76, fill=PAPER))
    parts.append(text(84, 578, '示波器开余辉，看总线低电平上有没有叠出来的细毛刺。', 23,
                      weight='700'))
    parts.append(text(500, 650, '先撤销 OE，再转身，后开口。', 22, colour=AMBER,
                      anchor='middle'))
    return parts


def hysteresis_window():
    parts = [header('迟滞：把判决点拆成两个',
                    '上行 6.15 V 才报，下行 5.85 V 才解；305 mV 窗口盖住 120 mV 噪声。')]
    parts.append(f'<line x1="100" y1="470" x2="620" y2="470" stroke="{INK2}" stroke-width="2"/>')
    parts.append(f'<line x1="100" y1="470" x2="100" y2="180" stroke="{INK2}" stroke-width="2"/>')
    parts.append(text(600, 500, 'VIN', 22, colour=INK2, anchor='end'))
    parts.append(text(120, 170, 'VOUT', 22, colour=INK2))
    # 回环：上行在 6.15 V 翻高，下行在 5.85 V 翻低
    parts.append(f'<path d="M140,430 L480,430 L480,230 L580,230" '
                 f'fill="none" stroke="{BLUE}" stroke-width="5"/>')
    parts.append(f'<path d="M580,230 L360,230 L360,430 L140,430" '
                 f'fill="none" stroke="{BLUE}" stroke-width="5"/>')
    parts.append(arrow(250, 430, 310, 430, colour=BLUE, width=2.5))
    parts.append(arrow(540, 230, 480, 230, colour=BLUE, width=2.5))
    parts.append(text(486, 222, 'VTH+ 6.15 V', 22, colour=BLUE, weight='700'))
    parts.append(text(330, 456, 'VTH− 5.85 V', 22, colour=BLUE, anchor='end', weight='700'))
    parts.append(f'<path d="M360,360 L480,360" stroke="{AMBER}" stroke-width="2" stroke-dasharray="4,4"/>')
    parts.append(text(420, 398, '305 mV', 22, colour=AMBER, anchor='middle', weight='700'))
    parts.append(box(650, 140, 300, 360, fill=PAPER))
    rows = [
        ('186', 'ΔV ≥ 2× 噪声峰峰'),
        ('248', '现场噪声 120 mV'),
        ('310', 'R2/R1 100:1'),
        ('372', '窗口约电源 1%'),
        ('434', '窗口也是判决盲区'),
    ]
    for y, line in rows:
        parts.append(text(674, int(y), line, 22, colour=INK if y != '434' else RED,
                          weight='700' if y in ('186', '434') else '400'))
    parts.append(box(50, 530, 900, 76, fill=PAPER))
    parts.append(text(74, 578, '先量噪声，再定电阻；窗口不是越大越安全。', 23, weight='700'))
    parts.append(text(500, 650, '小窗口抗扰，大窗口锁存；量变到质变。', 22, colour=AMBER,
                      anchor='middle'))
    return parts


def esr_window():
    parts = [header('LDO 的稳定区，写在一段 ESR 窗口里',
                    '老式 NPN 准 LDO 要 0.3–22 Ω；全贴 MLCC 的 5 mΩ 反而振荡。')]
    parts.append(f'<line x1="80" y1="340" x2="920" y2="340" stroke="{RULE}" stroke-width="2"/>')
    parts.append(f'<rect x="300" y="285" width="350" height="120" rx="10" fill="#e2ebe0" stroke="{GREEN}" stroke-width="2"/>')
    parts.append(text(475, 332, '稳定区 0.3–22 Ω', 26, colour=GREEN, anchor='middle', weight='700'))
    parts.append(text(475, 366, 'ESR 造出环路零点', 22, colour=INK2, anchor='middle'))
    parts.append(text(190, 332, '5 mΩ MLCC', 24, colour=RED, anchor='middle', weight='700'))
    parts.append(text(190, 366, '零点太远 → 振荡', 22, colour=RED, anchor='middle'))
    parts.append(text(790, 332, '>22 Ω', 24, colour=AMBER, anchor='middle', weight='700'))
    parts.append(text(790, 366, '零点太近 → 响应慢', 22, colour=AMBER, anchor='middle'))
    parts.append(box(50, 430, 430, 120, fill=PAPER))
    parts.append(text(74, 472, '10 µF 钽电容', 22, weight='700'))
    parts.append(text(74, 506, '是补偿的一部分，不是随便换', 22, colour=INK2))
    parts.append(box(520, 430, 430, 120, fill=PAPER))
    parts.append(text(544, 472, '10 µF MLCC', 22, weight='700'))
    parts.append(text(544, 506, '换之前先查手册的 ESR 窗口', 22, colour=INK2))
    parts.append(box(50, 570, 900, 60, fill=PAPER))
    parts.append(text(74, 610, '容量一样，不等于环路还稳；ESR 才是藏起来的参数。', 22,
                      weight='700', colour=AMBER))
    return parts


def psrr_slope():
    parts = [header('PSRR 不是名片上的一个数',
                    '1 kHz 70 dB，100 kHz 40 dB，1 MHz 只剩 20 dB；是一条下坠的曲线。')]
    parts.append(f'<line x1="90" y1="470" x2="620" y2="470" stroke="{INK2}" stroke-width="2"/>')
    parts.append(f'<line x1="90" y1="470" x2="90" y2="170" stroke="{INK2}" stroke-width="2"/>')
    parts.append(text(600, 500, '频率', 22, colour=INK2, anchor='end'))
    parts.append(text(78, 180, 'dB', 22, colour=INK2, anchor='end'))
    parts.append(f'<path d="M150,220 C260,240 340,300 430,340 C510,375 570,405 600,420" '
                 f'fill="none" stroke="{BLUE}" stroke-width="5"/>')
    for x, y, label in ((150, 220, '1 kHz · 70 dB'), (430, 340, '100 kHz · 40 dB')):
        parts.append(f'<circle cx="{x}" cy="{y}" r="7" fill="{BLUE}"/>')
        parts.append(text(x + 14, y - 10, label, 22, colour=BLUE, weight='700'))
    parts.append(f'<circle cx="600" cy="420" r="7" fill="{BLUE}"/>')
    parts.append(text(586, 456, '1 MHz · 20 dB', 22, colour=BLUE, anchor='end', weight='700'))
    parts.append(box(650, 140, 300, 330, fill=PAPER))
    parts.append(text(674, 186, 'DCDC 后级怎么用', 22, weight='700'))
    parts.append(text(674, 234, '500 kHz 的 Buck：', 22, colour=INK2))
    parts.append(text(674, 266, '先看该频点还剩多少 dB', 22, colour=INK2))
    parts.append(text(674, 322, '不够：换型号，', 22, colour=AMBER, weight='700'))
    parts.append(text(674, 354, '或直接加一级 LC。', 22, colour=AMBER, weight='700'))
    parts.append(text(674, 410, '噪声预算按频段查。', 22, weight='700'))
    parts.append(box(50, 540, 900, 76, fill=PAPER))
    parts.append(text(74, 588, '别抄最大值；先问你的噪声落在哪一段。', 23, weight='700'))
    return parts


SCENES = {
    'ch01-e24-ladder': {
        'draw': e24_ladder, 'title': 'E24 档位与 3.3k 的来历', 'anchor': '1.1',
        'chapter': 1, 'source': 'docs/p1-02-ch1.md',
        'alt': '手绘左右两栏：左栏算出 3.285k，落到 E24 货架档 3.3k，误差落在正负 5% 窗内；右栏列出 24 档、约 1.1 倍档比、正负 5% 容差与 E96 的正负 1%。底部写先选系列再选值，货架上没有 3.285k。',
    },
    'ch04-gate-window': {
        'draw': gate_window, 'title': '栅极保护的电压窗', 'anchor': '4.4',
        'chapter': 4, 'source': 'docs/p1-05-ch4.md',
        'alt': '手绘三条电压带：栅氧额定正负 20 伏、钳位 13 到 16 伏、驱动 12 伏；右栏写明钳位高于驱动且低于额定、栅源并 10 千欧下拉、开尔文源脚。底部写 12 伏驱动选 13 到 16 伏钳位。',
    },
    'ch04-deadtime-ledger': {
        'draw': deadtime_ledger, 'title': '死区损耗的明账', 'anchor': '4.4',
        'chapter': 4, 'source': 'docs/p1-05-ch4.md',
        'alt': '手绘公式与对照：死区损耗约等于 0.8 伏乘 5 安乘 100 纳秒乘 100 千赫，约 0.4 瓦；同一只管子沟道压降 5 安乘 30 毫欧为 0.15 伏，体二极管为 0.8 伏。底部写死区压到几十纳秒但不能压到零。',
    },
    'ch05-rp-window': {
        'draw': rp_window, 'title': 'I2C 上拉电阻的合围窗口', 'anchor': '5.2',
        'chapter': 5, 'source': 'docs/p1-06-ch5.md',
        'alt': '手绘窗口数轴：3.3 伏、100 皮法、快速模式下驱动下限 967 欧，速度上限 3.5 千欧，中间取 2.2 千欧；99 千欧漏电上限在这条总线上不卡。底部写任何约束变了先重跑围合再动电阻。',
    },
    'ch05-tristate-handover': {
        'draw': tristate_handover, 'title': '三态总线的交接时序', 'anchor': '5.4',
        'chapter': 5, 'source': 'docs/p1-06-ch5.md',
        'alt': '手绘三段时间轴：驱动器 A 释放进入高阻，空档 tDIS 为 10 到 30 纳秒，驱动器 B 使能开始驱动；下方写重叠 10 纳秒会让两个驱动器同时开口，产生微秒级电流尖峰。底部写先撤销 OE 再转身后开口。',
    },
    'ch07-hysteresis-window': {
        'draw': hysteresis_window, 'title': '迟滞窗口与两个阈值', 'anchor': '7.3',
        'chapter': 7, 'source': 'docs/p1-08-ch7.md',
        'alt': '手绘迟滞回环：上行阈值 6.15 伏、下行阈值 5.85 伏，窗口 305 毫伏，覆盖现场 120 毫伏噪声；右侧列出窗口至少为噪声峰峰两倍、R2 比 R1 为 100 比 1、窗口约电源 1%。底部写先量噪声再定电阻。',
    },
    'ch09-esr-window': {
        'draw': esr_window, 'title': 'LDO 的 ESR 稳定窗口', 'anchor': '9.3',
        'chapter': 9, 'source': 'docs/p1-10-ch9.md',
        'alt': '手绘 ESR 数轴：老式 NPN 准 LDO 的稳定区是 0.3 到 22 欧；左侧 5 毫欧的 MLCC 因零点太远而振荡，右侧大于 22 欧因零点太近而响应慢。底部写容量一样不等于环路还稳。',
    },
    'ch09-psrr-slope': {
        'draw': psrr_slope, 'title': 'PSRR 随频率下坠', 'anchor': '9.3',
        'chapter': 9, 'source': 'docs/p1-10-ch9.md',
        'alt': '手绘 PSRR 下坠曲线：1 千赫 70 分贝、100 千赫 40 分贝、1 兆赫 20 分贝；右侧写 500 千赫的 Buck 后级要先看该频点还剩多少分贝，不够就换型号或加一级 LC。底部写别抄最大值。',
    },
}

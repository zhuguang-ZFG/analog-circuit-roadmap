"""Wave 7 手绘草图：示波器带宽五倍规则。"""
from __future__ import annotations

from scripts.visuals.scenes.handdrawn_wave2 import (
    AMBER, BLUE, GREEN, INK, INK2, PAPER, RED, RULE, box, header, text,
)


def bandwidth_five():
    parts = [header('带宽不够，异常会被磨平',
                    '示波器与探头带宽宜取信号最高频率分量的五倍以上。')]
    parts.append(box(50, 136, 430, 330, fill=PAPER))
    parts.append(box(520, 136, 430, 330, fill=PAPER))
    parts.append(text(74, 180, '带宽不足', 25, colour=RED, weight='700'))
    parts.append(text(544, 180, '五倍带宽', 25, colour=GREEN, weight='700'))
    parts.append(f'<line x1="86" y1="400" x2="444" y2="400" stroke="{RULE}" stroke-width="1.6"/>')
    parts.append(f'<line x1="556" y1="400" x2="914" y2="400" stroke="{RULE}" stroke-width="1.6"/>')
    parts.append(f'<path d="M96,390 C150,390 170,250 240,250 C310,250 330,390 430,390" fill="none" stroke="{RED}" stroke-width="4"/>')
    parts.append(f'<path d="M566,390 L620,390 L620,250 L760,250 L760,390 L904,390" fill="none" stroke="{GREEN}" stroke-width="4"/>')
    parts.append(text(265, 432, '边沿变圆，振铃被吃掉', 22, colour=INK2, anchor='middle'))
    parts.append(text(735, 432, '边沿与过冲保得住', 22, colour=INK2, anchor='middle'))

    parts.append(box(60, 500, 880, 76, fill=PAPER))
    parts.append(text(88, 534, '先算最高频率分量 ×5，再选探头与示波器。', 23, weight='700'))
    parts.append(text(88, 564, '看电源纹波可先开 20 MHz 限制；确认细节时再关。', 22, colour=INK2))

    parts.append(box(60, 602, 420, 52, fill=PAPER))
    parts.append(text(88, 635, '读数前先报档位，再报数值。', 22, weight='700'))
    parts.append(box(520, 602, 420, 52, fill=PAPER))
    parts.append(text(548, 635, '×1 与 ×10 差十倍，别拨错。', 22, colour=AMBER, weight='700'))
    return parts


SCENES = {
    'ch16-bandwidth-five': {
        'draw': bandwidth_five, 'title': '示波器带宽五倍规则', 'anchor': '16.3',
        'chapter': 16, 'source': 'docs/p4-01-ch16.md',
        'alt': '手绘两种边沿：带宽不足时边沿变圆、振铃被吃掉；五倍带宽时边沿与过冲保得住。底部写先算最高频率分量乘五，再看电源纹波可先开 20 兆赫限制，读数前先报档位。',
    },
}

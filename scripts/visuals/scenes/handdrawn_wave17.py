"""Wave 17 手绘草图：长而密、却只有一张旧动画的小节。

每张图的数字只取对应 anchor 小节：ch15 取 15.6 的回路面积→辐射等级换算，
ch9 取 9.2 的 TL431 分压电阻下限量，ch13 取 13.10 的负阻裕度两笔账，
ch13 取 13.6 的采样率与量化台阶，ch14 取 14.12 的误差预算六项与比率测量。
"""
from __future__ import annotations

from scripts.visuals.scenes.handdrawn_wave2 import (
    AMBER, BLUE, GREEN, INK, INK2, PAPER, RED, RULE, arrow, box, header, text,
)


def radiated_loop_area():
    parts = [header('回路面积决定辐射，改布局比加滤波器便宜',
                    '回路 15 cm² 给出 56 dBµV/m、超限 16 dB；缩到 0.5 cm² 只剩 26。')]

    parts.append(box(50, 126, 900, 84, fill=PAPER, stroke=BLUE))
    parts.append(text(76, 164, 'EMC 三要素：干扰源 → 耦合路径 → 敏感设备（或天线）', 24, colour=BLUE, weight='700'))
    parts.append(text(76, 196, '模拟工程师能掌控的是后两个：掐断路径，缩小天线', 22, colour=INK2))

    parts.append(box(50, 224, 430, 218, fill=PAPER, stroke=RED))
    parts.append(text(74, 264, '回路面积 15 cm²', 24, colour=RED, weight='700'))
    parts.append(text(74, 304, '开槽让回流绕路，环变成天线', 22, colour=INK2))
    parts.append(text(74, 344, '远场估算', 22, colour=INK2))
    parts.append(text(456, 346, '660 µV/m', 22, colour=INK, anchor='end', weight='700'))
    parts.append(text(74, 386, '换成对数', 22, colour=INK2))
    parts.append(text(456, 388, '56 dBµV/m', 24, colour=RED, anchor='end', weight='700'))
    parts.append(f'<line x1="82" y1="406" x2="448" y2="406" stroke="{RULE}" stroke-width="2"/>')
    parts.append(text(74, 428, '限值 40，超 16 dB', 22, colour=RED, weight='700'))

    parts.append(box(520, 224, 430, 218, fill=PAPER, stroke=GREEN))
    parts.append(text(544, 264, '回路面积 0.5 cm²', 24, colour=GREEN, weight='700'))
    parts.append(text(544, 304, '回流贴着地平面正下方走', 22, colour=INK2))
    parts.append(text(544, 344, '面积掉 30 倍', 22, colour=INK2))
    parts.append(text(926, 346, '−29.5 dB', 22, colour=INK, anchor='end', weight='700'))
    parts.append(text(544, 386, '换算成场强', 22, colour=INK2))
    parts.append(text(926, 388, '26 dBµV/m', 24, colour=GREEN, anchor='end', weight='700'))
    parts.append(f'<line x1="550" y1="406" x2="920" y2="406" stroke="{RULE}" stroke-width="2"/>')
    parts.append(text(544, 428, '限值 40，余量充足', 22, colour=GREEN, weight='700'))

    parts.append(box(50, 450, 900, 104, fill=PAPER, stroke=AMBER))
    parts.append(text(76, 488, '为什么先动布局', 24, colour=AMBER, weight='700'))
    parts.append(text(76, 526, '面积是线性项，布局阶段免费；滤波器、屏蔽罩是整改阶段的钱',
                      22, colour=INK2))

    parts.append(box(50, 570, 900, 104, fill=PAPER, stroke=RED))
    parts.append(text(76, 608, '辐射超标的发射，十有八九是电缆当天线', 24, colour=RED, weight='700'))
    parts.append(text(76, 646, '1 m 电缆在 30~300 MHz 是高效天线；地平面被割开形成的缝隙也是天线',
                      22, colour=INK2))
    return parts


def tl431_divider_floor():
    parts = [header('TL431 的分压电阻，不能为了省电随意放大',
                    'REF 要吸 2 µA，分压电流至少给它的 100 倍。5 V 输出时 20 kΩ 正好，100 kΩ 就崩。')]

    parts.append(box(50, 126, 900, 88, fill=PAPER, stroke=BLUE))
    parts.append(text(76, 164, 'TL431 强制 REF = 2.5 V，外接两只电阻分压', 24, colour=BLUE, weight='700'))
    parts.append(text(76, 196, 'V_KA = 2.5 × (1 + R1/R2)；用法从稳压源到开关电源反馈环路', 22, colour=INK2))

    parts.append(box(50, 228, 430, 232, fill=PAPER, stroke=GREEN))
    parts.append(text(74, 268, '算一笔：目标 5 V', 24, colour=GREEN, weight='700'))
    parts.append(text(74, 308, '分压电流取 250 µA', 22, colour=INK2))
    parts.append(text(74, 348, 'R1 + R2 = 20 kΩ', 22, colour=INK2))
    parts.append(text(74, 388, '各 10 kΩ、1% 金属膜', 22, colour=INK2))
    parts.append(f'<line x1="82" y1="410" x2="448" y2="410" stroke="{RULE}" stroke-width="2"/>')
    parts.append(text(74, 444, 'REF 的 2 µA 流过 10 kΩ，偏 20 mV', 22, colour=INK2))

    parts.append(box(520, 228, 430, 232, fill=PAPER, stroke=RED))
    parts.append(text(544, 268, '抬到 100 kΩ 档会怎样', 24, colour=RED, weight='700'))
    parts.append(text(544, 308, '同一支 2 µA，压降变大', 22, colour=INK2))
    parts.append(text(926, 310, '0.2 V', 24, colour=RED, anchor='end', weight='700'))
    parts.append(text(544, 350, '输出直接崩', 22, colour=INK2))
    parts.append(text(926, 352, '4%', 26, colour=RED, anchor='end', weight='700'))
    parts.append(f'<line x1="550" y1="374" x2="920" y2="374" stroke="{RULE}" stroke-width="2"/>')
    parts.append(text(544, 408, '省下的电，全变成输出误差', 22, colour=INK2))
    parts.append(text(544, 440, '不如直接买固定基准', 22, colour=INK2))

    parts.append(box(50, 480, 900, 96, fill=PAPER, stroke=AMBER))
    parts.append(text(76, 518, '另外三笔账：阴极电流、动态阻抗、补偿边界', 24, colour=AMBER, weight='700'))
    parts.append(text(76, 552, '最小阴极电流 0.4~1 mA；动态阻抗约 0.2 Ω；阴极电容 0.01~1 µF 有振荡窗口',
                      22, colour=INK2))

    parts.append(box(50, 596, 900, 98, fill=PAPER))
    parts.append(text(76, 634, '耐压不是分压电阻的问题，是 R1 的问题', 24, colour=INK, weight='700'))
    parts.append(text(76, 672, '输出 24 V 时 R1 扛 21.5 V；0805 单颗耐压 150 V 没问题，上百伏就要串两颗分担',
                      22, colour=INK2))
    return parts


def crystal_neg_resistance():
    parts = [header('起振的判据是负阻裕度，不是频率配准',
                    '8 MHz 只要 0.26 mA/V 就够；32.768 kHz 的 ESR 高达 35~90 kΩ，却只要 1.7 µA/V。')]

    parts.append(box(50, 126, 900, 88, fill=PAPER, stroke=BLUE))
    parts.append(text(76, 164, '工程要求：R_neg ≥ 5 × ESR_max', 24, colour=BLUE, weight='700'))
    parts.append(text(76, 196, '余量不足会起振慢，甚至低温不启振；频率配得再准也叫不醒', 22, colour=INK2))

    parts.append(box(50, 228, 430, 216, fill=PAPER, stroke=GREEN))
    parts.append(text(74, 268, '8 MHz 晶体', 24, colour=GREEN, weight='700'))
    parts.append(text(74, 308, 'ESR 80 Ω、C0 3 pF、CL 15 pF', 22, colour=INK2))
    parts.append(text(74, 348, '临界跨导', 22, colour=INK2))
    parts.append(text(456, 350, '0.26 mA/V', 22, colour=INK, anchor='end', weight='700'))
    parts.append(f'<line x1="82" y1="372" x2="448" y2="372" stroke="{RULE}" stroke-width="2"/>')
    parts.append(text(74, 406, 'MCU 内部反相器有几 mA/V', 22, colour=INK2))
    parts.append(text(74, 434, '裕度 20 倍以上，很稳', 22, colour=GREEN, weight='700'))

    parts.append(box(520, 228, 430, 216, fill=PAPER, stroke=RED))
    parts.append(text(544, 268, '32.768 kHz 晶体', 24, colour=RED, weight='700'))
    parts.append(text(544, 308, 'ESR 天然巨大', 22, colour=INK2))
    parts.append(text(926, 310, '35~90 kΩ', 22, colour=RED, anchor='end', weight='700'))
    parts.append(text(544, 348, '临界跨导反而极小', 22, colour=INK2))
    parts.append(text(926, 350, '1.7 µA/V', 22, colour=INK, anchor='end', weight='700'))
    parts.append(f'<line x1="550" y1="372" x2="920" y2="372" stroke="{RULE}" stroke-width="2"/>')
    parts.append(text(544, 406, '所以 RTC 振荡器功耗能做 µA 级', 22, colour=INK2))
    parts.append(text(544, 434, '它需要的 g_m 本来就极小', 22, colour=RED, weight='700'))

    parts.append(box(50, 464, 900, 100, fill=PAPER, stroke=AMBER))
    parts.append(text(76, 502, '两个数差得很远，方向却一致', 24, colour=AMBER, weight='700'))
    parts.append(text(76, 536, 'g_m,crit 与 ESR 成正比、与频率的平方成正比；频率降下来，阻抗升上去',
                      22, colour=INK2))

    parts.append(box(50, 584, 900, 110, fill=PAPER, stroke=RED))
    parts.append(text(76, 622, '先确认起振，再谈频率准不准', 24, colour=RED, weight='700'))
    parts.append(text(76, 656, '负载电容配错只让走时慢一点；负阻裕度不够是根本不起振', 22, colour=INK2))
    parts.append(text(76, 684, '军规 ④：起振时间与负阻裕度成反比，裕度越小醒得越慢', 22, colour=INK2))
    return parts


def sampling_quantization():
    parts = [header('采样与量化：两道翻译各自的代价',
                    '3.3 V 量程 12 位，台阶 0.8 mV；1 ksps 读 50 Hz 够，读 1 kHz 就混叠。')]

    parts.append(box(50, 126, 430, 172, fill=PAPER, stroke=BLUE))
    parts.append(text(74, 166, '① 采样：时间离散化', 24, colour=BLUE, weight='700'))
    parts.append(text(74, 206, '每隔 T_s 抓一次瞬时值', 22, colour=INK2))
    parts.append(text(74, 246, '采样率必须大于信号最高频率的 2 倍', 22, colour=INK2))
    parts.append(text(74, 282, '否则高频伪装成低频，就是混叠', 22, colour=RED, weight='700'))

    parts.append(box(520, 126, 430, 172, fill=PAPER, stroke=GREEN))
    parts.append(text(544, 166, '② 量化：幅度离散化', 24, colour=GREEN, weight='700'))
    parts.append(text(544, 206, '台阶 = 满量程 / 2 的 N 次方', 22, colour=INK2))
    parts.append(text(544, 246, '3.3 V 量程、12 位', 22, colour=INK2))
    parts.append(text(926, 248, '0.8 mV', 22, colour=INK, anchor='end', weight='700'))
    parts.append(text(544, 282, '读数末位抖动就是量化噪声', 22, colour=GREEN, weight='700'))

    parts.append(box(50, 314, 900, 177, fill=PAPER, stroke=AMBER))
    parts.append(text(76, 352, '算一笔：1 ksps 到底够不够', 24, colour=AMBER, weight='700'))
    parts.append(text(76, 392, '读 50 Hz 工频：1 ksps 大于 2 倍，够', 22, colour=INK2))
    parts.append(text(926, 394, '可以', 22, colour=GREEN, anchor='end', weight='700'))
    parts.append(text(76, 428, '直接读 1 kHz 音频：1 ksps 小于 2 倍，混叠', 22, colour=INK2))
    parts.append(text(926, 430, '失真', 22, colour=RED, anchor='end', weight='700'))
    parts.append(f'<line x1="82" y1="450" x2="920" y2="450" stroke="{RULE}" stroke-width="2"/>')
    parts.append(text(76, 474, '对策：提到 10 ksps 以上，或在 ADC 前加 500 Hz 低通', 22, colour=INK2))

    parts.append(box(50, 498, 900, 196, fill=PAPER, stroke=RED))
    parts.append(text(76, 536, '三种架构：速度、精度、成本凑成不可能三角', 24, colour=RED, weight='700'))
    parts.append(text(76, 576, 'SAR：逐次逼近，二进制搜索 N 次收敛，中速、12~18 位', 22, colour=INK2))
    parts.append(text(926, 578, '约 1 Msps', 22, colour=INK, anchor='end', weight='700'))
    parts.append(text(76, 612, 'Σ-Δ：1 位高速粗采加数字滤波，用时间换精度、16~24 位', 22, colour=INK2))
    parts.append(text(926, 614, '不到 1 ksps', 22, colour=INK, anchor='end', weight='700'))
    parts.append(text(76, 648, 'Flash：2 的 N 次方减 1 个比较器同时判决，极快、低于 8 位', 22, colour=INK2))
    parts.append(text(926, 650, 'Gsps 级', 22, colour=INK, anchor='end', weight='700'))
    parts.append(f'<line x1="82" y1="664" x2="920" y2="664" stroke="{RULE}" stroke-width="2"/>')
    return parts


def pt100_error_budget():
    parts = [header('比率测量约掉两项，剩下四项自己扛',
                    '激励与 ADC 基准同源，电流绝对误差和基准初始误差一起约掉。温漂预算只有 0.04 °C。')]

    parts.append(box(50, 126, 900, 96, fill=PAPER, stroke=BLUE))
    parts.append(text(76, 164, '误差预算先统一单位，再列六项', 24, colour=BLUE, weight='700'))
    parts.append(text(76, 200, '传感、激励、放大、滤波、ADC、基准——六项都折到同一个单位上才加得起来',
                      22, colour=INK2))

    parts.append(box(50, 236, 430, 180, fill=PAPER, stroke=GREEN))
    parts.append(text(74, 276, '比率测量能约掉', 24, colour=GREEN, weight='700'))
    parts.append(text(74, 316, '激励电流的绝对误差', 22, colour=INK2))
    parts.append(text(74, 352, '基准的初始误差', 22, colour=INK2))
    parts.append(f'<line x1="82" y1="374" x2="448" y2="374" stroke="{RULE}" stroke-width="2"/>')
    parts.append(text(74, 406, '约掉的原因：两者同源，一起变一起消', 22, colour=INK2))

    parts.append(box(520, 236, 430, 180, fill=PAPER, stroke=RED))
    parts.append(text(544, 276, '约不掉的那几项', 24, colour=RED, weight='700'))
    parts.append(text(544, 316, '传感本身的容差与自热', 22, colour=INK2))
    parts.append(text(544, 352, '放大增益的 0.1% 电阻', 22, colour=INK2))
    parts.append(text(544, 388, '基准温漂 10 ppm/°C', 22, colour=INK2))

    parts.append(box(50, 430, 900, 104, fill=PAPER, stroke=AMBER))
    parts.append(text(76, 468, '温漂预算只有 0.04 °C，别让布局吃掉它', 24, colour=AMBER, weight='700'))
    parts.append(text(76, 506, 'LDO、Buck、功率电阻都是热源；基准要靠远离热源、靠同源来保精度',
                      22, colour=INK2))

    parts.append(box(50, 548, 900, 146, fill=PAPER))
    parts.append(text(76, 586, '设计从后往前推，调试从前往后查', 24, colour=INK, weight='700'))
    parts.append(text(76, 622, '从后往前：ADC 满量程 → 增益 → 噪声预算', 22, colour=INK2))
    parts.append(text(76, 654, '从前往后：激励 → 放大 → 滤波 → 转换', 22, colour=INK2))
    parts.append(text(76, 684, '测试不回填，预算就还只是假设', 22, colour=RED, weight='700'))
    return parts


SCENES = {
    'ch15-radiated-loop-area': {
        'draw': radiated_loop_area, 'title': '回路面积决定辐射等级',
        'anchor': '15.6', 'chapter': 15, 'source': 'docs/p3-02-ch15.md',
        'alt': '手绘辐射分账。顶部蓝框写电磁兼容三要素：干扰源、耦合路径、敏感设备或天线，'
               '模拟工程师能掌控的是后两个。左红框回路面积 15 平方厘米，开槽让回流绕路、环路变成天线，'
               '远场估算 660 微伏每米，换成对数 56 分贝微伏每米，限值 40、超 16 分贝。'
               '右绿框回路面积 0.5 平方厘米，回流贴着地平面正下方走，面积掉 30 倍也就是负 29.5 分贝，'
               '换算成场强 26 分贝微伏每米，限值 40、余量充足。'
               '琥珀框写为什么先动布局：面积是线性项、布局阶段免费，滤波器与屏蔽罩是整改阶段的钱。'
               '底部红框写辐射超标的发射十有八九是电缆当天线，1 米电缆在 30 到 300 兆赫是高效天线。',
    },
    'ch09-tl431-divider-floor': {
        'draw': tl431_divider_floor, 'title': 'TL431 分压电阻的下限',
        'anchor': '9.2', 'chapter': 9, 'source': 'docs/p1-10-ch9.md',
        'alt': '手绘 TL431 分压账。顶部蓝框写 TL431 强制参考端等于 2.5 伏，外接两只电阻分压。'
               '左绿框算目标 5 伏：分压电流取 250 微安，两电阻之和 20 千欧，各 10 千欧、1% 金属膜；'
               '参考端的 2 微安流过 10 千欧，偏 20 毫伏。'
               '右红框抬到 100 千欧档：同一支 2 微安压降变大到 0.2 伏，输出直接崩 4%，'
               '省下的电全变成输出误差，不如直接买固定基准。'
               '琥珀框写另外三笔账：最小阴极电流 0.4 到 1 毫安、动态阻抗约 0.2 欧、'
               '阴极电容 0.01 到 1 微法有振荡窗口。'
               '底部写耐压不是分压电阻的问题而是 R1 的问题：输出 24 伏时 R1 扛 21.5 伏，'
               '0805 单颗耐压 150 伏没问题，上百伏就要串两颗分担。',
    },
    'ch13-crystal-neg-resistance': {
        'draw': crystal_neg_resistance, 'title': '晶振起振的负阻裕度',
        'anchor': '13.10', 'chapter': 13, 'source': 'docs/p2-03-ch13.md',
        'alt': '手绘晶振负阻两笔账。顶部蓝框写工程要求负阻大于等于 5 倍最大等效串联电阻，'
               '余量不足会起振慢甚至低温不启振。'
               '左绿框 8 兆赫晶体：等效串联电阻 80 欧、静态电容 3 皮法、负载电容 15 皮法，'
               '临界跨导 0.26 毫安每伏；单片机内部反相器有几毫安每伏，裕度 20 倍以上很稳。'
               '右红框 32.768 千赫晶体：等效串联电阻天然巨大、35 到 90 千欧，临界跨导反而极小、'
               '1.7 微安每伏，所以实时时钟振荡器功耗能做到微安级。'
               '琥珀框写两个数差得很远方向却一致：临界跨导与等效串联电阻成正比、与频率的平方成正比。'
               '底部红框写先确认起振再谈频率准不准：负载电容配错只让走时慢一点，'
               '负阻裕度不够是根本不起振；军规 ④ 说起振时间与负阻裕度成反比、裕度越小醒得越慢。',
    },
    'ch13-sampling-quantization': {
        'draw': sampling_quantization, 'title': '采样率与量化台阶的两道账',
        'anchor': '13.6', 'chapter': 13, 'source': 'docs/p2-03-ch13.md',
        'alt': '手绘采样与量化两栏。左上蓝框采样是时间离散化：每隔一个采样周期抓一次瞬时值，'
               '采样率必须大于信号最高频率的 2 倍，否则高频伪装成低频就是混叠。'
               '右上绿框量化是幅度离散化：台阶等于满量程除以 2 的 N 次方，'
               '3.3 伏量程、12 位得 0.8 毫伏，读数末位抖动就是量化噪声。'
               '琥珀框算 1 ksps 够不够：读 50 赫兹工频，1 ksps 大于 2 倍，可以；'
               '直接读 1 千赫音频，1 ksps 小于 2 倍，混叠失真；对策是提到 10 ksps 以上或前置 500 赫兹低通。'
               '底部红框三种架构：逐次逼近约 1 Msps、12 到 18 位；过采样不到 1 ksps、16 到 24 位；'
               '并行比较 Gsps 级、低于 8 位。',
    },
    'ch14-pt100-error-budget': {
        'draw': pt100_error_budget, 'title': 'PT100 的误差预算与比率测量',
        'anchor': '14.12', 'chapter': 14, 'source': 'docs/p3-01-ch14.md',
        'alt': '手绘误差预算两栏。顶部蓝框写误差预算先统一单位，再列六项：'
               '传感、激励、放大、滤波、ADC、基准，六项都折到同一个单位上才加得起来。'
               '左绿框比率测量能约掉两项：激励电流的绝对误差与基准的初始误差，'
               '原因是两者同源、一起变一起消。'
               '右红框约不掉的那几项：传感本身的容差与自热、放大增益的 0.1% 电阻、基准温漂 10 ppm 每摄氏度。'
               '琥珀框写温漂预算只有 0.04 摄氏度，低压差稳压器与开关电源都是热源，基准要靠远离热源来保精度。'
               '底部写设计从后往前推、调试从前往后查：后面是 ADC 满量程到增益到噪声预算，'
               '前面是激励到放大到滤波到转换；测试不回填，预算就还只是假设。',
    },
}

"""Wave 13 手绘草图：薄章补图（ch5 推挽直通与 AB 偏置、ch9 7805 四本账、
ch10 555 反推与 50% 占空比、ch11 两级放大器余量）。

每张图的数字只取对应 anchor 小节：ch5 取 5.6 的直通与管耗算例，
ch9 取 9.4 的四本账与升级路径，ch10 取 10.4 的反推与占空比三条路，
ch11 取 11.11 的指标对账。
"""
from __future__ import annotations

from scripts.visuals.scenes.handdrawn_wave2 import (
    AMBER, BLUE, GREEN, INK, INK2, PAPER, RED, RULE, arrow, box, header, text,
)


def astable_reverse_design():
    parts = [header('按目标反推元件：38kHz 怎么落到货架上',
                    '先定电容，再解总电阻，最后用 E 系列凑——回算一遍才算交付。')]
    parts.append(box(50, 130, 430, 330, fill=PAPER))
    parts.append(text(74, 172, '五步反推', 24, colour=BLUE, weight='700'))
    parts.append(text(74, 214, '① 目标：38 kHz 载波，占空比约 50%', 22, colour=INK2))
    parts.append(text(74, 250, '② 取 C=1 nF（COG）', 22, colour=INK2))
    parts.append(text(74, 286, '③ 解总电阻 R1+2R2 ≈ 37.9 kΩ', 22, colour=INK2))
    parts.append(text(74, 322, '④ 近 50% 要 R1 ≪ R2，取 R1=1 kΩ', 22, colour=INK2))
    parts.append(text(74, 358, '⑤ 则 R2 ≈ 18.4 kΩ，取 18 kΩ', 22, colour=INK2))
    parts.append(f'<line x1="80" y1="386" x2="450" y2="386" stroke="{RULE}" stroke-width="2"/>')
    parts.append(text(74, 428, 'R1 的下限由放电管电流定', 22, colour=AMBER, weight='700'))
    parts.append(box(520, 130, 430, 330, fill=PAPER))
    parts.append(text(544, 172, '回算：交付前的最后一步', 24, colour=GREEN, weight='700'))
    parts.append(text(544, 218, '实际频率', 22, colour=INK2))
    parts.append(text(926, 220, '38.9 kHz', 28, colour=GREEN, anchor='end', weight='700'))
    parts.append(text(544, 266, '实际占空比', 22, colour=INK2))
    parts.append(text(926, 268, '51.4%', 28, colour=GREEN, anchor='end', weight='700'))
    parts.append(f'<line x1="550" y1="296" x2="920" y2="296" stroke="{RULE}" stroke-width="2"/>')
    parts.append(text(544, 338, '偏差能不能收？', 24, colour=BLUE, weight='700'))
    parts.append(text(544, 378, '接收头带宽 ±2 kHz 级', 22, colour=INK2))
    parts.append(text(544, 414, '对占空比更不敏感', 22, colour=INK2))
    parts.append(text(544, 450, '所以遥控器敢用 RC 振荡器', 22, colour=AMBER, weight='700'))
    parts.append(box(50, 486, 900, 130, fill=PAPER))
    parts.append(text(76, 528, '超窗了怎么办：18 kΩ 换 16.9 kΩ+1.5 kΩ 串联，', 24,
                      colour=INK, weight='700'))
    parts.append(text(76, 564, '或者上一只多圈电位器修调。', 24, colour=INK, weight='700'))
    parts.append(text(76, 600, '式子给的是起点，E 系列与回算才是落地的两道手续。', 22, colour=INK2))
    return parts


def duty_cycle_fifty():
    parts = [header('想要准 50%：三条路与两个极端',
                    '标准接法充电走 R1+R2、放电只走 R2，占空比数学上永远 >50%。')]
    rows = [
        ('① 二极管抄近路', 'R2 两端并一只二极管，充电只走 R1、放电走 R2',
         '取 R1=R2 即 50%；代价是约 0.6 V 正向压降缩窄摆幅', 146, GREEN),
        ('② 单电阻回授', '去掉 R1，用 R 从 OUT 直接给 C 充放电',
         '充放时间常数天然相等；双极版高电平低 1.4 V 是隐患', 254, BLUE),
        ('③ 干脆换拓扑', '高一倍频率振荡，再 D 触发器二分频',
         '占空比由结构保证，与 RC 无关', 362, AMBER),
    ]
    for label, how, cost, y, colour in rows:
        parts.append(box(50, y, 900, 96, fill=PAPER, stroke=colour))
        parts.append(text(74, y + 38, label, 26, colour=colour, weight='700'))
        parts.append(text(300, y + 38, how, 22, colour=INK))
        parts.append(text(300, y + 76, cost, 22, colour=INK2))
    parts.append(box(50, 478, 900, 150, fill=PAPER, stroke=RED))
    parts.append(text(74, 520, '两个极端的代价是同一条教训', 26, colour=RED, weight='700'))
    parts.append(text(74, 562, '逼近 100%：R2 顶着放电管电流下限、R1 受漏电流上限，99% 已是实用极限', 22,
                      colour=INK2))
    parts.append(text(74, 598, '逼近 50%：R1=100 Ω、12 V 时峰值 120 mA 直灌放电管，芯片发热、频率漂移', 22,
                      colour=INK2))
    return parts


def shoot_through_ledger():
    parts = [header('推挽的第四拍：正常与直通差了两个数量级',
                    '同一只管子，值班表写错一次，电流账从 1.5A 跳到 24A。')]
    parts.append(box(50, 130, 430, 300, fill=PAPER, stroke=GREEN))
    parts.append(text(74, 172, '正常半周：轮流值班', 24, colour=GREEN, weight='700'))
    parts.append(text(74, 214, '8Ω 负载、±12V，理想峰值 12V', 22, colour=INK2))
    parts.append(text(74, 258, '峰值电流', 22, colour=INK2))
    parts.append(text(456, 260, '1.5A', 28, colour=GREEN, anchor='end', weight='700'))
    parts.append(text(74, 304, '输出功率', 22, colour=INK2))
    parts.append(text(456, 306, '9W', 28, colour=GREEN, anchor='end', weight='700'))
    parts.append(text(74, 350, 'B 类效率上限', 22, colour=INK2))
    parts.append(text(456, 352, '78.5%', 28, colour=GREEN, anchor='end', weight='700'))
    parts.append(text(74, 408, '电流只流过一只管子与负载', 22, colour=INK2))
    parts.append(box(520, 130, 430, 300, fill=PAPER, stroke=RED))
    parts.append(text(544, 172, '直通：两只同时导通', 24, colour=RED, weight='700'))
    parts.append(text(544, 214, '+12V 经 Q1→Q2→−12V 直接短路', 22, colour=INK2))
    parts.append(text(544, 258, '两管饱和电阻之和按 1Ω 估', 22, colour=INK2))
    parts.append(text(544, 304, '短路电流', 22, colour=INK2))
    parts.append(text(926, 306, '24A', 28, colour=RED, anchor='end', weight='700'))
    parts.append(text(544, 350, '瞬时功耗', 22, colour=INK2))
    parts.append(text(926, 352, '288W', 28, colour=RED, anchor='end', weight='700'))
    parts.append(text(544, 408, '偏置错、时序错、上电瞬间都会触发', 22, colour=INK2))
    parts.append(arrow(486, 280, 514, 280, colour=RED))
    parts.append(box(50, 456, 900, 170, fill=PAPER))
    parts.append(text(76, 498, '288W 远超 TO-220 的 60W 极限，几十毫秒就冒烟。', 26,
                      colour=RED, weight='700'))
    parts.append(text(76, 540, '电流只受饱和电阻与走线电阻限制——没有任何保护来得及动作。', 22,
                      colour=INK2))
    parts.append(text(76, 582, 'AB 类偏置的两条硬要求：够小不交越，够稳不直通。', 24,
                      colour=GREEN, weight='700'))
    return parts


def ab_bias_thermal():
    parts = [header('AB 类偏置怎么钉住：热耦合与散热器两笔账',
                    '偏置不是调一次就完事；它必须跟着功率管的温度自己收紧。')]
    parts.append(box(50, 130, 430, 330, fill=PAPER))
    parts.append(text(74, 172, '偏置账：可调电池 + 热耦合', 24, colour=BLUE, weight='700'))
    parts.append(text(74, 212, '一只晶体管配两个电阻', 22, colour=INK2))
    parts.append(text(74, 248, '接在两管基极之间', 22, colour=INK2))
    parts.append(text(74, 284, '电阻比取 3 时给', 22, colour=INK2))
    parts.append(text(456, 286, '2.4V', 28, colour=BLUE, anchor='end', weight='700'))
    parts.append(text(74, 320, '正好顶开上下管各一个结还留余量', 22, colour=INK2))
    parts.append(f'<line x1="80" y1="348" x2="450" y2="348" stroke="{RULE}" stroke-width="2"/>')
    parts.append(text(74, 384, '倍增管贴在功率管散热器上', 22, colour=INK2))
    parts.append(text(74, 418, '温度系数', 22, colour=INK2))
    parts.append(text(456, 420, '−2mV/℃', 28, colour=GREEN, anchor='end', weight='700'))
    parts.append(text(74, 452, '功率管一热，偏置自动收紧', 22, colour=GREEN, weight='700'))
    parts.append(box(520, 130, 430, 330, fill=PAPER))
    parts.append(text(544, 172, '散热账：按结温倒推热阻', 24, colour=RED, weight='700'))
    parts.append(text(544, 214, 'B 类每管最大耗散约 0.2 倍输出功率', 22, colour=INK2))
    parts.append(text(544, 252, '9W 输出即每管', 22, colour=INK2))
    parts.append(text(926, 254, '1.8W', 28, colour=AMBER, anchor='end', weight='700'))
    parts.append(text(544, 292, 'TO-220 不装散热器热阻约 65℃/W', 22, colour=INK2))
    parts.append(text(544, 330, '温升 117℃，25℃ 环境下结温', 22, colour=INK2))
    parts.append(text(926, 332, '142℃', 28, colour=RED, anchor='end', weight='700'))
    parts.append(f'<line x1="550" y1="358" x2="920" y2="358" stroke="{RULE}" stroke-width="2"/>')
    parts.append(text(544, 388, '允许结温 105℃、环境 40℃', 22, colour=INK2))
    parts.append(text(544, 424, '热阻须 ≤36℃/W', 26, colour=GREEN, weight='700'))
    parts.append(text(544, 452, '一片小型散热器即可满足', 22, colour=GREEN))
    parts.append(box(50, 486, 900, 130, fill=PAPER))
    parts.append(text(76, 528, '没有热耦合的偏置是定时炸弹：升温→阈值下降→静态电流增大→更热。', 24,
                      colour=RED, weight='700'))
    parts.append(text(76, 566, '静态电流量级是经验值：中小功率每管 20~50mA，让交接处轻微重叠导通。', 22,
                      colour=INK2))
    parts.append(text(76, 602, '射极各串 0.22~0.47Ω：既是直流负反馈也是限流，0.33Ω 约吃掉 4% 摆幅。',
                      22, colour=INK2))
    return parts


def ldo_four_accounts():
    parts = [header('7805 的四种死法，是四本不同的账',
                    '同一颗芯片，热、纹波、稳定性、上电各有各的判据与解法。')]
    accounts = [
        ('① 热账', 'P=(VIN−5V)×I；12V→5V@300mA = 2.1W', '无散热片必热关断', 134, RED),
        ('② 纹波账', '输入谷值必须 ≥ VOUT+VDROP', '100Hz 纹波跌破压差线就下垂', 222, AMBER),
        ('③ 稳定性账', 'AMS1117 的环路补偿依赖输出电容 ESR', '出窗口就振荡', 310, BLUE),
        ('④ 上电账', '大压差 + 快上电，调整管未及时响应', '过冲 >10% 持续 µs 级', 398, GREEN),
    ]
    for label, how, judge, y, colour in accounts:
        parts.append(box(50, y, 900, 78, fill=PAPER, stroke=colour))
        parts.append(text(74, y + 34, label, 26, colour=colour, weight='700'))
        parts.append(text(240, y + 34, how, 22, colour=INK))
        parts.append(text(240, y + 66, judge, 22, colour=INK2))
    parts.append(box(50, 492, 900, 136, fill=PAPER, stroke=GREEN))
    parts.append(text(74, 528, '升级路径与经验分界', 26, colour=GREEN, weight='700'))
    parts.append(text(74, 566, '降输入：Buck 到 7.5V，功耗减 2/3；换 DCDC：效率 85%–95%，2.1W 变 0.3W',
                      22, colour=INK2))
    parts.append(text(74, 602, '压差×电流 >1W 就别让线性稳压硬扛；<0.3W 时线性全面占优', 22,
                      colour=RED, weight='700'))
    return parts


def two_stage_margin():
    parts = [header('两级放大器交付前对账：四项指标各剩多少余量',
                    '四项全过，但余量不是平均分配的——最薄的两项决定这版能不能发。')]
    rows = [
        ('电压增益', '≥60 dB（1000 倍）', '1037 倍 = 60.3 dB', '+0.3 dB', 150, RED),
        ('输入电阻', '≥10 kΩ', '13.0 k ∥ 110 k = 11.6 kΩ', '过线', 238, GREEN),
        ('输出电阻', '≤100 Ω', '射随器给到约 29 Ω', '富余', 326, GREEN),
        ('带宽', '≥100 kHz', '两极点叠加约 110 kHz', '刚过线', 414, RED),
    ]
    for label, spec, actual, margin, y, colour in rows:
        parts.append(box(50, y, 900, 78, fill=PAPER, stroke=colour))
        parts.append(text(74, y + 34, label, 26, colour=INK, weight='700'))
        parts.append(text(240, y + 34, spec, 22, colour=INK2))
        parts.append(text(470, y + 34, actual, 22, colour=INK))
        parts.append(text(926, y + 36, margin, 26, colour=colour, anchor='end', weight='700'))
    parts.append(box(50, 508, 900, 120, fill=PAPER))
    parts.append(text(76, 550, '最薄的是增益与带宽：β 一漂移，两项可能齐破。', 26,
                      colour=RED, weight='700'))
    parts.append(text(76, 588, '源阻真是 10 kΩ 且没有偏置电阻分流时，第一极点掉到约 75 kHz——', 22,
                      colour=INK2))
    parts.append(text(76, 620, '要么第一级改 cascode 拆掉米勒桥，要么降第一级增益、分给第二级。', 22,
                      colour=INK2))
    return parts


SCENES = {
    'ch10-astable-reverse-design': {
        'draw': astable_reverse_design, 'title': '按 38kHz 目标反推 555 元件值',
        'anchor': '10.4', 'chapter': 10, 'source': 'docs/p1-11-ch10.md',
        'alt': '手绘 555 反推两栏：左栏列五步，目标 38 千赫载波占空比约 50%，取电容 1 纳法 COG，解总电阻 R1 加 2R2 约 37.9 千欧，近 50% 要求 R1 远小于 R2 故取 R1 等于 1 千欧，则 R2 约 18.4 千欧取 18 千欧，并注明 R1 的下限由放电管电流定；右栏回算实际频率 38.9 千赫、实际占空比 51.4%，并写接收头带宽 ±2 千赫级、对占空比更不敏感，所以遥控器敢用 RC 振荡器。底部写超窗了把 18 千欧换 16.9 千欧加 1.5 千欧串联，或上一只多圈电位器修调，式子给的是起点、E 系列与回算才是落地手续。',
    },
    'ch10-duty-fifty-paths': {
        'draw': duty_cycle_fifty, 'title': '准 50% 占空比的三条路与两个极端',
        'anchor': '10.4', 'chapter': 10, 'source': 'docs/p1-11-ch10.md',
        'alt': '手绘三行对照：第一行二极管抄近路，R2 两端并一只二极管充电只走 R1、放电走 R2，取 R1 等于 R2 即 50%，代价是约 0.6 伏正向压降缩窄摆幅；第二行单电阻回授，去掉 R1 用 R 从输出脚直接给电容充放电，充放时间常数天然相等，双极版高电平低 1.4 伏是隐患；第三行干脆换拓扑，高一倍频率振荡再 D 触发器二分频，占空比由结构保证与 RC 无关。底部红框写两个极端的代价是同一条教训：逼近 100% 时 R2 顶着放电管电流下限、R1 受漏电流上限，99% 已是实用极限；逼近 50% 时 R1 等于 100 欧、12 伏时峰值 120 毫安直灌放电管，芯片发热、频率漂移。',
    },
    'ch05-shoot-through-ledger': {
        'draw': shoot_through_ledger, 'title': '推挽正常半周与直通的电流功率对账',
        'anchor': '5.6', 'chapter': 5, 'source': 'docs/p1-06-ch5.md',
        'alt': '手绘推挽两栏对照：左栏绿框写正常半周轮流值班，8 欧负载、正负 12 伏、理想峰值 12 伏，峰值电流 1.5 安、输出功率 9 瓦、B 类效率上限 78.5%，电流只流过一只管子与负载；右栏红框写直通时两只管子同时导通，正 12 伏经 Q1 到 Q2 到负 12 伏直接短路，两管饱和电阻之和按 1 欧估，短路电流 24 安、瞬时功耗 288 瓦，偏置错、时序错、上电瞬间都会触发。底部写 288 瓦远超 TO-220 的 60 瓦极限、几十毫秒就冒烟，电流只受饱和电阻与走线电阻限制、没有任何保护来得及动作，AB 类偏置的两条硬要求是够小不交越、够稳不直通。',
    },
    'ch05-ab-bias-thermal': {
        'draw': ab_bias_thermal, 'title': 'AB 类偏置的热耦合与散热器两笔账',
        'anchor': '5.6', 'chapter': 5, 'source': 'docs/p1-06-ch5.md',
        'alt': '手绘两栏：左栏偏置账写一只晶体管配两个电阻接在两管基极之间，电阻比取 3 时给 2.4 伏，正好顶开上下管各一个结还留余量；倍增管贴在功率管散热器上，温度系数负 2 毫伏每摄氏度，功率管一热偏置自动收紧。右栏散热账写 B 类每管最大耗散约 0.2 倍输出功率，9 瓦输出即每管 1.8 瓦，TO-220 不装散热器热阻约 65 摄氏度每瓦，温升 117 摄氏度、25 摄氏度环境下结温 142 摄氏度；允许结温 105 摄氏度、环境 40 摄氏度时热阻须小于等于 36 摄氏度每瓦，一片小型散热器即可满足。底部写没有热耦合的偏置是定时炸弹，升温到阈值下降到静态电流增大到更热；静态电流中小功率每管 20 到 50 毫安；射极各串 0.22 到 0.47 欧既是直流负反馈也是限流，0.33 欧约吃掉 4% 摆幅。',
    },
    'ch09-ldo-four-accounts': {
        'draw': ldo_four_accounts, 'title': '7805 四种死法对应的四本账',
        'anchor': '9.4', 'chapter': 9, 'source': 'docs/p1-10-ch9.md',
        'alt': '手绘四行账：热账写功耗等于输入减 5 伏再乘电流，12 伏降 5 伏带 300 毫安是 2.1 瓦，无散热片必热关断；纹波账写输入谷值必须大于等于输出加压差，100 赫兹纹波跌破压差线就下垂；稳定性账写 AMS1117 的环路补偿依赖输出电容 ESR，出窗口就振荡；上电账写大压差加快上电时调整管未及时响应，过冲超过 10% 且持续微秒级。底部一行写升级路径与经验分界：降输入 Buck 到 7.5 伏功耗减三分之二，换 DCDC 效率 85% 到 95%、2.1 瓦变 0.3 瓦；压差乘电流大于 1 瓦就别让线性稳压硬扛，小于 0.3 瓦时线性全面占优。',
    },
    'ch11-two-stage-margin': {
        'draw': two_stage_margin, 'title': '两级放大器四项指标的余量对账',
        'anchor': '11.11', 'chapter': 11, 'source': 'docs/p2-01-ch11.md',
        'alt': '手绘四行对账表：电压增益要求大于等于 60 分贝即 1000 倍，实得 1037 倍即 60.3 分贝，余量只有正 0.3 分贝；输入电阻要求大于等于 10 千欧，实得 13.0 千欧并联 110 千欧等于 11.6 千欧，余量正 1.6 千欧；输出电阻要求小于等于 100 欧，射随器给到约 29 欧，富余；带宽要求大于等于 100 千赫，两极点叠加约 110 千赫，刚过线。底部写最薄的是增益与带宽，β 一漂移两项可能齐破；源阻真是 10 千欧且没有偏置电阻分流时第一极点掉到约 75 千赫，要么第一级改 cascode 拆掉米勒桥，要么降第一级增益分给第二级。',
    },
}

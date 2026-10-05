# -*- coding: utf-8 -*-
"""
generate_svgs.py — 一键再生成《通往模拟电路之路》全部 7 张 SVG SMIL 动画
用法:  python generate_svgs.py            # 输出到 ../assets/svg/
风格:  参考 BMS-Z 项目 —— 浅色底 + SMIL 节拍字幕 + 深色模式自适应 + 拟人化讲解
所有电路参数经过自洽核算（datasheet 级），详见各函数注释。
"""
import os
import numpy as np

OUT = os.path.join(os.path.dirname(__file__), '..', 'assets', 'svg')
os.makedirs(OUT, exist_ok=True)

DARK_CSS = """<style>
text{font-family:"Segoe UI","Microsoft YaHei",sans-serif;}
@media (prefers-color-scheme: dark){
rect[fill="#f8fafc"]{fill:#0f172a}
[fill="#1e293b"]{fill:#f1f5f9}[stroke="#1e293b"]{stroke:#f1f5f9}
[fill="#334155"]{fill:#e2e8f0}[stroke="#334155"]{stroke:#e2e8f0}
[fill="#475569"]{fill:#cbd5e1}[stroke="#475569"]{stroke:#cbd5e1}
[fill="#64748b"]{fill:#94a3b8}[stroke="#64748b"]{stroke:#94a3b8}
[fill="#dbeafe"]{fill:#1e3a8a}[fill="#eff6ff"]{fill:#172554}
[fill="#1d4ed8"]{fill:#60a5fa}[fill="#2563eb"]{fill:#60a5fa}[fill="#3b82f6"]{fill:#60a5fa}
[fill="#ecfdf5"]{fill:#022c22}[fill="#059669"]{fill:#34d399}[fill="#065f46"]{fill:#6ee7b7}[fill="#10b981"]{fill:#34d399}
[fill="#fffbeb"]{fill:#451a03}[fill="#b45309"]{fill:#fcd34d}[fill="#92400e"]{fill:#fcd34d}[fill="#f59e0b"]{fill:#fbbf24}
[fill="#fef2f2"]{fill:#450a0a}[fill="#dc2626"]{fill:#f87171}[fill="#991b1b"]{fill:#fca5a5}
}
</style>"""


# ======================= 模板与元件库 =======================

def svg_open(title, w=800, h=460):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
<title>{title}</title>
<rect width="{w}" height="{h}" fill="#f8fafc"/>
{DARK_CSS}
<text x="{w//2}" y="30" text-anchor="middle" font-size="19" font-weight="bold" fill="#1e293b">{title}</text>
'''


def flow(path, dur, n=3, color="#f59e0b", r=5.5, stagger=None, keypoints=None, keytimes="0;1"):
    """沿路径的电流粒子；begin 负相位保证静态首帧可见；keypoints/keyTimes 可非匀速"""
    stagger = stagger if stagger is not None else dur / n
    kp = f' keyPoints="{keypoints}" keyTimes="{keytimes}" calcMode="linear"' if keypoints else ''
    return '\n'.join(
        f'<circle r="{r}" fill="{color}">'
        f'<animateMotion dur="{dur}s" begin="{i*stagger-0.5:.2f}s" repeatCount="indefinite" path="{path}"{kp}/></circle>'
        for i in range(n))


def caption(text, color, dur, kt_values, kt_times, y=400, x=400, size=14.5):
    """节拍字幕：kt_values/kt_times 控制该幕的显隐窗口"""
    return (f'<text x="{x}" y="{y}" text-anchor="middle" font-size="{size}" font-weight="bold" fill="{color}" opacity="0">'
            f'{text}<animate attributeName="opacity" values="{kt_values}" keyTimes="{kt_times}" '
            f'dur="{dur}s" repeatCount="indefinite"/></text>')


def note_box(text, y, dur, delay_kt="0;0.82;0.86;1", color="#059669", bg="#ecfdf5", x=400, w=560):
    """延迟出现的要点注释框"""
    return f'''<g opacity="0">
<animate attributeName="opacity" values="0;0;1;1" keyTimes="{delay_kt}" dur="{dur}s" repeatCount="indefinite"/>
<rect x="{x-w//2}" y="{y-24}" width="{w}" height="34" rx="8" fill="{bg}" stroke="{color}" stroke-width="1.5"/>
<text x="{x}" y="{y-2}" text-anchor="middle" font-size="13.5" font-weight="bold" fill="{color}">{text}</text>
</g>'''


def trace2(path_d, dur, color="#2563eb", width=3.5, kt="0;0.85;1", plen=700, ghost=True):
    """描线动画（ghost=True 时附 18% 透明度完整底稿，静态首帧不空）"""
    g = f'<path d="{path_d}" fill="none" stroke="{color}" stroke-width="1.8" opacity="0.18"/>' if ghost else ''
    return g + (f'<path d="{path_d}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linecap="round" '
                f'stroke-dasharray="{plen}" stroke-dashoffset="{plen}">'
                f'<animate attributeName="stroke-dashoffset" values="{plen};{plen};0;0" keyTimes="{kt}" '
                f'dur="{dur}s" repeatCount="indefinite"/></path>')


def pulse(x, y, w, h, color="#f59e0b", dur=1.2, rx=8):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="none" stroke="{color}" stroke-width="2.5" opacity="0">'
            f'<animate attributeName="opacity" values="0.15;0.9;0.15" dur="{dur}s" repeatCount="indefinite"/></rect>')


def gnd_sym(x, y, color="#334155"):
    return (f'<line x1="{x}" y1="{y-14}" x2="{x}" y2="{y}" stroke="{color}" stroke-width="2.5"/>'
            f'<line x1="{x-16}" y1="{y}" x2="{x+16}" y2="{y}" stroke="{color}" stroke-width="3"/>'
            f'<line x1="{x-10}" y1="{y+6}" x2="{x+10}" y2="{y+6}" stroke="{color}" stroke-width="3"/>'
            f'<line x1="{x-4}" y1="{y+12}" x2="{x+4}" y2="{y+12}" stroke="{color}" stroke-width="3"/>')


def resistor_h(x, y, w=56, label='', sub='', color="#334155", lcolor="#b45309"):
    sub_t = f'<text x="{x+w/2}" y="{y+15}" text-anchor="middle" font-size="10.5" fill="#475569">{sub}</text>' if sub else ''
    return f'''<line x1="{x-20}" y1="{y}" x2="{x}" y2="{y}" stroke="{color}" stroke-width="2.5"/>
<rect x="{x}" y="{y-11}" width="{w}" height="22" fill="#f8fafc" stroke="{color}" stroke-width="2.5"/>
<line x1="{x+w}" y1="{y}" x2="{x+w+20}" y2="{y}" stroke="{color}" stroke-width="2.5"/>
<text x="{x+w/2}" y="{y-17}" text-anchor="middle" font-size="12.5" font-weight="bold" fill="{lcolor}">{label}</text>{sub_t}'''


def resistor_v(x, y, h=56, label='', color="#334155", lcolor="#b45309"):
    return f'''<line x1="{x}" y1="{y-20}" x2="{x}" y2="{y}" stroke="{color}" stroke-width="2.5"/>
<rect x="{x-11}" y="{y}" width="22" height="{h}" fill="#f8fafc" stroke="{color}" stroke-width="2.5"/>
<line x1="{x}" y1="{y+h}" x2="{x}" y2="{y+h+20}" stroke="{color}" stroke-width="2.5"/>
<text x="{x+20}" y="{y+h/2+4}" font-size="12.5" font-weight="bold" fill="{lcolor}">{label}</text>'''


def npn_svg(x, y, color="#334155"):
    """NPN：基区棒在(x-35,y)，C 右上、E 右下（发射极箭头向外，沿斜线方向）"""
    return f'''<g stroke="{color}" fill="none" stroke-width="2.5">
<circle cx="{x-12}" cy="{y}" r="34" stroke-width="1.8"/>
<line x1="{x-35}" y1="{y-20}" x2="{x-35}" y2="{y+20}" stroke-width="3.5"/>
<line x1="{x-35}" y1="{y-8}" x2="{x}" y2="{y-35}"/>
<line x1="{x-35}" y1="{y+8}" x2="{x}" y2="{y+35}"/>
<line x1="{x}" y1="{y-35}" x2="{x}" y2="{y-55}"/>
<line x1="{x}" y1="{y+35}" x2="{x}" y2="{y+55}"/>
<line x1="{x-85}" y1="{y}" x2="{x-35}" y2="{y}"/>
<polygon points="{x},{y+35} {x-12.5},{y+31.6} {x-6.5},{y+23.8}" fill="{color}" stroke="none"/>
</g>
<text x="{x-93}" y="{y-8}" font-size="12.5" font-weight="bold" fill="#dc2626">B</text>
<text x="{x+9}" y="{y-48}" font-size="12.5" font-weight="bold" fill="#2563eb">C</text>
<text x="{x+9}" y="{y+60}" font-size="12.5" font-weight="bold" fill="#059669">E</text>'''


def diode_arm(x1, y1, x2, y2, label, dlx, dly):
    """桥臂二极管：正向从 (x1,y1) 指向 (x2,y2)"""
    mx, my = (x1+x2)/2, (y1+y2)/2
    dx, dy = x2-x1, y2-y1
    L = float(np.hypot(dx, dy)); ux, uy = dx/L, dy/L
    px, py = -uy, ux
    t = 11
    tipx, tipy = mx+ux*t, my+uy*t
    bx1, by1 = mx-ux*t, my-uy*t
    return f'''<line x1="{x1}" y1="{y1}" x2="{bx1:.0f}" y2="{by1:.0f}" stroke="#334155" stroke-width="2.5"/>
<polygon points="{tipx:.0f},{tipy:.0f} {bx1+px*t:.0f},{by1+py*t:.0f} {bx1-px*t:.0f},{by1-py*t:.0f}" fill="#334155"/>
<line x1="{tipx+px*t:.0f}" y1="{tipy+py*t:.0f}" x2="{tipx-px*t:.0f}" y2="{tipy-py*t:.0f}" stroke="#334155" stroke-width="3.5"/>
<line x1="{tipx:.0f}" y1="{tipy:.0f}" x2="{x2}" y2="{y2}" stroke="#334155" stroke-width="2.5"/>
<text x="{dlx}" y="{dly}" font-size="12" font-weight="bold" fill="#475569">{label}</text>'''


def sine_path(x0, x1, ymid, amp, n=48, phase=0.0):
    pts = []
    for i in range(n+1):
        t = i/n*2*np.pi
        x = x0 + (x1-x0)*i/n
        y = ymid + amp*np.sin(t+phase)
        pts.append(f"{x:.0f},{y:.0f}")
    return "M" + " L".join(pts)


def square_path(x0, x1, y_hi, y_lo, periods=2, n=64):
    pts = []
    for i in range(n+1):
        t = i/n*periods
        x = x0 + (x1-x0)*i/n
        y = y_lo if (t % 1) < 0.5 else y_hi
        pts.append(f"{x:.0f},{y:.0f}")
    return "M" + " L".join(pts)


def tri_cap(x0, x1, y13, y23, cycles=2):
    """555 电容三角波：充电 2 份时间、放电 1 份（占空比 2/3 的来源）"""
    pts = []
    T = 3.0
    n = 90
    for i in range(n+1):
        t = i/n*cycles*T
        ph = t % T
        x = x0 + (x1-x0)*i/n
        y = y13+(y23-y13)*(ph/2) if ph < 2 else y23-(y23-y13)*(ph-2)
        pts.append(f"{x:.0f},{y:.0f}")
    return "M" + " L".join(pts)


def sq_out(x0, x1, yhi, ylo, cycles=2):
    pts = []
    T = 3.0
    n = 90
    for i in range(n+1):
        t = i/n*cycles*T
        ph = t % T
        x = x0 + (x1-x0)*i/n
        y = ylo if ph < 2 else yhi
        pts.append(f"{x:.0f},{y:.0f}")
    return "M" + " L".join(pts)


def save(name, svg):
    path = os.path.join(OUT, name)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(svg)
    print('saved', name, len(svg), 'bytes')


# ======================= 图 1：RC 充电 =======================
def make_rc_charge():
    DUR = 5
    pts = []
    for i in range(33):
        t = i/32*5
        x = 430 + (750-430)*i/32
        y = 350 - (350-182)*(1-np.exp(-t))
        pts.append(f"{x:.0f},{y:.0f}")
    curve_d = "M" + " L".join(pts)
    hs = [0, .47, .72, .86, .94, .985]          # 指数充电采样 1-e^-t
    kt_h = "0;0.2;0.4;0.6;0.8;1"
    h_vals = ";".join(f"{24*u:.1f}" for u in hs)
    y_vals = ";".join(f"{263-24*u:.1f}" for u in hs)
    svg = svg_open('RC 充电：电容是"水桶"，电阻是"细水管"')
    svg += f'''
<text x="200" y="70" text-anchor="middle" font-size="14" font-weight="bold" fill="#334155">电路</text>
<line x1="60" y1="120" x2="60" y2="196" stroke="#334155" stroke-width="2.5"/>
<line x1="60" y1="222" x2="60" y2="300" stroke="#334155" stroke-width="2.5"/>
<line x1="46" y1="196" x2="74" y2="196" stroke="#334155" stroke-width="2"/>
<line x1="52" y1="222" x2="68" y2="222" stroke="#334155" stroke-width="4"/>
<text x="36" y="193" font-size="13" fill="#334155">+</text>
<text x="30" y="216" font-size="13" fill="#334155">−</text>
<text x="18" y="260" font-size="13" font-weight="bold" fill="#b45309">5V</text>
<line x1="60" y1="120" x2="100" y2="120" stroke="#334155" stroke-width="2.5"/>
<circle cx="100" cy="120" r="3.5" fill="#334155"/>
<line x1="100" y1="120" x2="132" y2="106" stroke="#334155" stroke-width="2.5"/>
<circle cx="136" cy="120" r="3.5" fill="#334155"/>
<text x="70" y="97" font-size="11.5" fill="#475569">开关</text>
<line x1="136" y1="120" x2="150" y2="120" stroke="#334155" stroke-width="2.5"/>
<rect x="150" y="108" width="70" height="24" fill="#f8fafc" stroke="#334155" stroke-width="2.5"/>
<text x="185" y="97" text-anchor="middle" font-size="13" font-weight="bold" fill="#b45309">R = 1kΩ</text>
<text x="185" y="124" text-anchor="middle" font-size="11" fill="#475569">水管</text>
<line x1="220" y1="120" x2="320" y2="120" stroke="#334155" stroke-width="2.5"/>
<line x1="320" y1="120" x2="320" y2="235" stroke="#334155" stroke-width="2.5"/>
<line x1="285" y1="235" x2="355" y2="235" stroke="#334155" stroke-width="3"/>
<line x1="285" y1="265" x2="355" y2="265" stroke="#334155" stroke-width="3"/>
<rect x="291" y="263" width="58" height="0" fill="#3b82f6" opacity="0.75">
  <animate attributeName="height" values="{h_vals}" keyTimes="{kt_h}" dur="{DUR}s" repeatCount="indefinite"/>
  <animate attributeName="y" values="{y_vals}" keyTimes="{kt_h}" dur="{DUR}s" repeatCount="indefinite"/>
</rect>
<text x="372" y="252" font-size="13" font-weight="bold" fill="#2563eb">C = 10µF</text>
<text x="372" y="270" font-size="11" fill="#475569">水位=电量</text>
<line x1="320" y1="265" x2="320" y2="300" stroke="#334155" stroke-width="2.5"/>
<line x1="320" y1="300" x2="60" y2="300" stroke="#334155" stroke-width="2.5"/>
{gnd_sym(190, 300)}
{flow("M66,112 H314 V228", DUR, n=4, color="#f59e0b", r=5.5, keypoints="0;0.5;0.8;1", keytimes="0;0.2;0.5;1")}
<text x="120" y="152" font-size="11.5" fill="#b45309">电流（先快后慢）</text>
'''
    svg += f'''
<text x="585" y="70" text-anchor="middle" font-size="14" font-weight="bold" fill="#334155">电容电压 vC(t)</text>
<line x1="430" y1="350" x2="758" y2="350" stroke="#64748b" stroke-width="2"/>
<line x1="430" y1="350" x2="430" y2="115" stroke="#64748b" stroke-width="2"/>
<text x="752" y="370" text-anchor="end" font-size="12" fill="#475569">t →</text>
<text x="420" y="120" text-anchor="end" font-size="12" fill="#475569">vC</text>
<line x1="430" y1="182" x2="755" y2="182" stroke="#94a3b8" stroke-width="1.2" stroke-dasharray="5,4"/>
<text x="425" y="186" text-anchor="end" font-size="12" fill="#475569">5V</text>
<line x1="494" y1="350" x2="494" y2="243" stroke="#b45309" stroke-width="1.5" stroke-dasharray="4,3" opacity="0">
 <animate attributeName="opacity" values="0;0;1;1" keyTimes="0;0.62;0.66;1" dur="{DUR}s" repeatCount="indefinite"/></line>
<line x1="430" y1="243" x2="494" y2="243" stroke="#b45309" stroke-width="1.5" stroke-dasharray="4,3" opacity="0">
 <animate attributeName="opacity" values="0;0;1;1" keyTimes="0;0.62;0.66;1" dur="{DUR}s" repeatCount="indefinite"/></line>
<text x="494" y="365" text-anchor="middle" font-size="12.5" font-weight="bold" fill="#b45309" opacity="0">τ=10ms
 <animate attributeName="opacity" values="0;0;1;1" keyTimes="0;0.62;0.66;1" dur="{DUR}s" repeatCount="indefinite"/></text>
<text x="425" y="247" text-anchor="end" font-size="12" font-weight="bold" fill="#b45309" opacity="0">63.2%
 <animate attributeName="opacity" values="0;0;1;1" keyTimes="0;0.62;0.66;1" dur="{DUR}s" repeatCount="indefinite"/></text>
{trace2(curve_d, DUR, color="#2563eb", plen=700)}
'''
    svg += caption("第 1 拍：刚合闸，桶是空的——电流最猛（粒子最密最快）", "#b45309", DUR,
                   "0;1;1;0;0", "0;0.05;0.28;0.32;1", y=400)
    svg += caption("第 2 拍：水位上涨反顶着电流——越充越慢（指数曲线）", "#2563eb", DUR,
                   "0;0;1;1;0;0", "0;0.32;0.36;0.60;0.64;1", y=400)
    svg += caption("第 3 拍：1τ 充到 63%，3τ 到 95%——τ 就是电路的「性格」", "#059669", DUR,
                   "0;0;1;1", "0;0.64;0.68;1", y=400)
    svg += note_box("τ = R×C：电阻大=水管细，电容大=水桶深，都让它更慢", 442, DUR, w=520)
    save('rc-charge.svg', svg + '</svg>')


# ======================= 图 2：桥式全波整流 =======================
def make_bridge_rectifier():
    D4 = 4
    pts = []
    for i in range(97):
        t = i/96*2*np.pi
        x = 60 + 680*i/96
        y = 452 - 42*abs(np.sin(t))
        pts.append(f"{x:.0f},{y:.0f}")
    abs_d = "M" + " L".join(pts)
    svg = svg_open('桥式全波整流：四只二极管接力，负半周也「翻上来」（1N4007）', h=560)
    svg += f'''
<text x="330" y="58" text-anchor="middle" font-size="14" font-weight="bold" fill="#334155">桥式整流电路</text>
<circle cx="60" cy="230" r="21" fill="none" stroke="#2563eb" stroke-width="2.5"/>
<path d="M49,230 q5.5,-14 11,0 q5.5,14 11,0" fill="none" stroke="#2563eb" stroke-width="2"/>
<text x="22" y="206" font-size="11.5" font-weight="bold" fill="#2563eb">AC 12V</text>
<line x1="81" y1="230" x2="90" y2="230" stroke="#334155" stroke-width="2.5"/>
<line x1="39" y1="230" x2="24" y2="230" stroke="#334155" stroke-width="2.5"/>
<line x1="24" y1="230" x2="24" y2="366" stroke="#334155" stroke-width="2.5"/>
<line x1="24" y1="366" x2="466" y2="366" stroke="#334155" stroke-width="2.5"/>
<line x1="466" y1="366" x2="466" y2="230" stroke="#334155" stroke-width="2.5"/>
<line x1="466" y1="230" x2="430" y2="230" stroke="#334155" stroke-width="2.5"/>
{diode_arm(90,230,260,120,'D1',140,150)}
{diode_arm(430,230,260,120,'D3',352,150)}
{diode_arm(260,340,90,230,'D2',128,302)}
{diode_arm(260,340,430,230,'D4',352,302)}
<line x1="260" y1="120" x2="260" y2="70" stroke="#334155" stroke-width="2.5"/>
<line x1="260" y1="70" x2="600" y2="70" stroke="#334155" stroke-width="2.5"/>
<line x1="260" y1="340" x2="600" y2="340" stroke="#334155" stroke-width="2.5"/>
<text x="272" y="76" font-size="14" font-weight="bold" fill="#059669">+</text>
<text x="272" y="344" font-size="14" font-weight="bold" fill="#dc2626">−</text>
<line x1="600" y1="70" x2="600" y2="100" stroke="#334155" stroke-width="2.5"/>
{resistor_v(600, 100, 56, '负载')}
<line x1="600" y1="156" x2="600" y2="340" stroke="#334155" stroke-width="2.5"/>
<text x="600" y="56" text-anchor="middle" font-size="11.5" font-weight="bold" fill="#059669">电流方向永远不变！</text>
<line x1="600" y1="70" x2="680" y2="70" stroke="#334155" stroke-width="2.5"/>
<line x1="680" y1="70" x2="680" y2="112" stroke="#334155" stroke-width="2.5"/>
<line x1="650" y1="112" x2="710" y2="112" stroke="#334155" stroke-width="3"/>
<line x1="650" y1="128" x2="710" y2="128" stroke="#334155" stroke-width="3"/>
<line x1="680" y1="128" x2="680" y2="340" stroke="#334155" stroke-width="2.5"/>
<line x1="600" y1="340" x2="680" y2="340" stroke="#334155" stroke-width="2.5"/>
<text x="722" y="124" font-size="11.5" font-weight="bold" fill="#2563eb">C 滤波</text>
<text x="722" y="142" font-size="10" fill="#475569">（可选）</text>
<text x="96" y="190" font-size="14" font-weight="bold" fill="#059669" opacity="0">L +<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.48;0.52;1" dur="{D4}s" repeatCount="indefinite"/></text>
<text x="408" y="190" font-size="14" font-weight="bold" fill="#dc2626" opacity="0">− R<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.48;0.52;1" dur="{D4}s" repeatCount="indefinite"/></text>
<text x="96" y="190" font-size="14" font-weight="bold" fill="#dc2626" opacity="0">L −<animate attributeName="opacity" values="0;0;1;1" keyTimes="0;0.48;0.52;1" dur="{D4}s" repeatCount="indefinite"/></text>
<text x="408" y="190" font-size="14" font-weight="bold" fill="#059669" opacity="0">+ R<animate attributeName="opacity" values="0;0;1;1" keyTimes="0;0.48;0.52;1" dur="{D4}s" repeatCount="indefinite"/></text>
'''
    svg += f'<g><animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.46;0.5;1" dur="{D4}s" repeatCount="indefinite"/>'
    svg += flow("M96,224 L252,130", D4/2, n=3, color="#059669", r=5)
    svg += flow("M264,66 H592 V334", D4/2, n=6, color="#059669", r=5)
    svg += flow("M264,344 L426,236", D4/2, n=3, color="#059669", r=5)
    svg += flow("M434,234 H462 V362", D4/2, n=3, color="#059669", r=5) + '</g>'
    svg += f'<g><animate attributeName="opacity" values="0;0;1;1" keyTimes="0;0.5;0.54;1" dur="{D4}s" repeatCount="indefinite"/>'
    svg += flow("M424,224 L268,130", D4/2, n=3, color="#dc2626", r=5)
    svg += flow("M264,66 H592 V334", D4/2, n=6, color="#dc2626", r=5)
    svg += flow("M256,344 L94,236", D4/2, n=3, color="#dc2626", r=5)
    svg += flow("M86,234 H28 V362", D4/2, n=3, color="#dc2626", r=5) + '</g>'
    svg += f'''
<line x1="60" y1="452" x2="745" y2="452" stroke="#64748b" stroke-width="1.8"/>
<text x="740" y="474" text-anchor="end" font-size="11.5" fill="#475569">t →</text>
<path d="{sine_path(60, 740, 452, 42)}" fill="none" stroke="#94a3b8" stroke-width="2" stroke-dasharray="6,4"/>
<text x="64" y="404" font-size="11.5" fill="#64748b">AC 输入（虚线）</text>
<path d="{abs_d}" fill="none" stroke="#2563eb" stroke-width="3.2"/>
<text x="400" y="404" font-size="11.5" font-weight="bold" fill="#2563eb">输出：脉动直流（实线）＝ |输入| − 1.4V</text>
'''
    svg += caption("① 正半周（L+ R−）：D1、D4 导通——绿路走一遍", "#059669", D4,
                   "0;1;1;0;0", "0;0.04;0.44;0.48;1", y=512)
    svg += caption("② 负半周（L− R+）：D2、D3 导通——走红路，负载电流方向不变！", "#dc2626", D4,
                   "0;0;1;1", "0;0.52;0.56;1", y=512)
    svg += note_box("代价：两只管压降 ≈1.4V · 纹波 = 2×市电 = 100Hz · 1N4007 耐压 1000V/1A", 546, D4,
                    "0;0.55;0.6;1", w=680)
    save('bridge-rectifier.svg', svg + '</svg>')


# ======================= 图 3：BJT 共射放大 =======================
# 参数自洽核算（2N2222，β=100 下限设计）：
#   IB = (12−0.7)/390k ≈ 29µA；IC = 100×29µA ≈ 2.9mA；VCE = 12 − 2.9mA×2k ≈ 6.2V
def make_bjt_amplify():
    D6 = 6
    vbe_d = sine_path(450, 750, 150, 15)
    vce_d = sine_path(450, 750, 330, 58, phase=np.pi)
    svg = svg_open('共射放大器：偏置先算准，放大才不翻车（2N2222, β=100）', h=500)
    svg += f'''
<text x="205" y="62" text-anchor="middle" font-size="14" font-weight="bold" fill="#334155">电路（固定偏置 · 可实搭）</text>
<text x="36" y="92" font-size="13" font-weight="bold" fill="#b45309">+12V</text>
<line x1="70" y1="86" x2="320" y2="86" stroke="#334155" stroke-width="2.5"/>
<line x1="180" y1="86" x2="180" y2="106" stroke="#334155" stroke-width="2.5"/>
<rect x="169" y="106" width="22" height="56" fill="#f8fafc" stroke="#334155" stroke-width="2.5"/>
<text x="164" y="124" text-anchor="end" font-size="12.5" font-weight="bold" fill="#b45309">R<tspan baseline-shift="sub" font-size="9">B</tspan> 390kΩ</text>
<line x1="180" y1="162" x2="180" y2="210" stroke="#334155" stroke-width="2.5"/>
<circle cx="180" cy="210" r="3" fill="#334155"/>
<line x1="180" y1="210" x2="215" y2="210" stroke="#334155" stroke-width="2.5"/>
<line x1="300" y1="86" x2="300" y2="106" stroke="#334155" stroke-width="2.5"/>
<rect x="289" y="106" width="22" height="50" fill="#f8fafc" stroke="#334155" stroke-width="2.5"/>
<text x="320" y="128" font-size="12.5" font-weight="bold" fill="#b45309">R<tspan baseline-shift="sub" font-size="9">C</tspan> 2kΩ</text>
<line x1="300" y1="156" x2="300" y2="175" stroke="#334155" stroke-width="2.5"/>
{npn_svg(300, 210)}
<line x1="300" y1="265" x2="300" y2="300" stroke="#334155" stroke-width="2.5"/>
{gnd_sym(300, 314)}
<line x1="82" y1="210" x2="108" y2="210" stroke="#334155" stroke-width="2.5"/>
<line x1="108" y1="196" x2="108" y2="224" stroke="#334155" stroke-width="3"/>
<line x1="118" y1="196" x2="118" y2="224" stroke="#334155" stroke-width="3"/>
<line x1="118" y1="210" x2="180" y2="210" stroke="#334155" stroke-width="2.5"/>
<text x="113" y="192" text-anchor="middle" font-size="11.5" font-weight="bold" fill="#2563eb">C1 10µF</text>
<text x="113" y="240" text-anchor="middle" font-size="10.5" fill="#475569">隔直通交</text>
<circle cx="60" cy="210" r="21" fill="none" stroke="#2563eb" stroke-width="2.5"/>
<path d="M49,210 q5.5,-14 11,0 q5.5,14 11,0" fill="none" stroke="#2563eb" stroke-width="2"/>
<text x="30" y="252" font-size="11" font-weight="bold" fill="#2563eb">信号10mV</text>
<line x1="60" y1="231" x2="60" y2="300" stroke="#334155" stroke-width="2.5"/>
{gnd_sym(60, 314)}
<line x1="300" y1="175" x2="366" y2="175" stroke="#334155" stroke-width="2.5"/>
<text x="322" y="168" font-size="12" font-weight="bold" fill="#2563eb">vCE 输出</text>
<text x="150" y="262" font-size="11.5" font-weight="bold" fill="#dc2626">I_B ≈ 29µA</text>
<text x="238" y="105" font-size="11.5" font-weight="bold" fill="#2563eb">I_C ≈ 2.9mA</text>
<text x="322" y="192" font-size="11.5" font-weight="bold" fill="#059669">V_CE ≈ 6.2V</text>
'''
    svg += flow("M74,82 H296 V300", D6, n=9, color="#2563eb", r=6)
    svg += flow("M180,92 V206 H212", D6, n=3, color="#dc2626", r=4.5)
    svg += f'''<g opacity="0"><animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.2;0.24;1" dur="{D6}s" repeatCount="indefinite"/>
<rect x="163" y="100" width="34" height="68" rx="6" fill="none" stroke="#f59e0b" stroke-width="3">
<animate attributeName="opacity" values="0.2;0.95;0.2" dur="1.1s" repeatCount="indefinite"/></rect></g>
<g opacity="0"><animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="0;0.48;0.52;0.78;0.82;1" dur="{D6}s" repeatCount="indefinite"/>
<circle cx="288" cy="210" r="40" fill="none" stroke="#f59e0b" stroke-width="3">
<animate attributeName="opacity" values="0.2;0.95;0.2" dur="1.1s" repeatCount="indefinite"/></circle></g>
'''
    svg += f'''
<text x="600" y="62" text-anchor="middle" font-size="14" font-weight="bold" fill="#334155">波形对照（实测值核算）</text>
<text x="448" y="112" font-size="12" font-weight="bold" fill="#dc2626">基极：0.7V ± 10mV（小信号骑在偏置上）</text>
<line x1="440" y1="185" x2="760" y2="185" stroke="#64748b" stroke-width="1.8"/>
<line x1="440" y1="150" x2="760" y2="150" stroke="#94a3b8" stroke-width="1" stroke-dasharray="4,4"/>
<text x="755" y="146" text-anchor="end" font-size="10.5" fill="#475569">0.7V 偏置线</text>
<path d="{vbe_d}" fill="none" stroke="#dc2626" stroke-width="3"/>
<circle r="6" fill="#fff" stroke="#dc2626" stroke-width="3"><animateMotion dur="3s" repeatCount="indefinite" path="{vbe_d}"/></circle>
<text x="448" y="252" font-size="12" font-weight="bold" fill="#2563eb">集电极：6.2V ∓ 2V（≈200 倍 · 反相）</text>
<line x1="440" y1="400" x2="760" y2="400" stroke="#64748b" stroke-width="1.8"/>
<path d="{vce_d}" fill="none" stroke="#2563eb" stroke-width="3"/>
<circle r="6" fill="#fff" stroke="#2563eb" stroke-width="3"><animateMotion dur="3s" repeatCount="indefinite" path="{vce_d}"/></circle>
'''
    svg += caption("① 先偏置：R_B 从 12V 喂基流——没有偏置，信号再标准也放不出来", "#b45309", D6,
                   "0;1;1;0;0", "0;0.04;0.18;0.22;1", y=448)
    svg += caption("② 核算：I_B=(12−0.7)÷390k≈29µA → I_C=100×29µA≈2.9mA → V_CE=12−5.8≈6.2V", "#2563eb", D6,
                   "0;0;1;1;0;0", "0;0.22;0.26;0.44;0.48;1", y=448)
    svg += caption("③ 放大：基极 ±10mV → 集电极 ∓2V——约 200 倍，方向相反", "#dc2626", D6,
                   "0;0;1;1;0;0", "0;0.48;0.52;0.78;0.82;1", y=448)
    svg += caption("④ 能量全部来自 12V 电源——三极管是阀门，从不「创造」能量", "#059669", D6,
                   "0;0;1;1", "0;0.82;0.86;1", y=448)
    svg += note_box("2N2222 datasheet：hFE=75~300@10mA，设计时按 β=100 下限留余量", 486, D6, "0;0.9;0.94;1", w=640)
    save('bjt-amplify.svg', svg + '</svg>')


# ======================= 图 4：MOSFET 开关 =======================
# 参数：AO3400 VTH=1.45V(max)，3.3V 驱动可靠；LED 2V/20mA，R=(5−2)/20mA=150Ω
def make_mosfet_switch():
    D4 = 4
    vgs_d = square_path(430, 760, 120, 160)
    id_d = square_path(430, 760, 300, 360)
    svg = svg_open('MOSFET 开关：3.3V 单片机也能控制的「电压阀门」（AO3400）', h=470)
    svg += f'''
<text x="220" y="58" text-anchor="middle" font-size="14" font-weight="bold" fill="#334155">低边开关电路</text>
<text x="50" y="86" font-size="13" font-weight="bold" fill="#b45309">+5V</text>
<line x1="84" y1="80" x2="300" y2="80" stroke="#334155" stroke-width="2.5"/>
<line x1="300" y1="80" x2="300" y2="106" stroke="#334155" stroke-width="2.5"/>
<rect x="289" y="106" width="22" height="44" fill="#f8fafc" stroke="#334155" stroke-width="2.5"/>
<text x="320" y="132" font-size="12" font-weight="bold" fill="#b45309">R 150Ω</text>
<line x1="300" y1="150" x2="300" y2="168" stroke="#334155" stroke-width="2.5"/>
<polygon points="300,196 288,172 312,172" fill="#334155"/>
<line x1="288" y1="196" x2="312" y2="196" stroke="#334155" stroke-width="3.5"/>
<line x1="300" y1="196" x2="300" y2="212" stroke="#334155" stroke-width="2.5"/>
<text x="322" y="186" font-size="12" font-weight="bold" fill="#dc2626">LED 2V</text>
<g stroke="#f59e0b" stroke-width="2.5" opacity="0">
<animate attributeName="opacity" values="0;0;1;1" keyTimes="0;0.5;0.56;1" dur="{D4}s" repeatCount="indefinite"/>
<line x1="312" y1="168" x2="328" y2="152"/><line x1="320" y1="176" x2="338" y2="162"/>
<animate attributeName="opacity" values="0.3;0.3;1;1" keyTimes="0;0.5;0.75;1" dur="{D4}s" repeatCount="indefinite"/>
</g>
<line x1="300" y1="212" x2="300" y2="228" stroke="#334155" stroke-width="2.5"/>
<line x1="300" y1="228" x2="280" y2="228" stroke="#334155" stroke-width="2.5"/>
<line x1="280" y1="228" x2="280" y2="240" stroke="#334155" stroke-width="2.5"/>
<line x1="280" y1="254" x2="280" y2="266" stroke="#334155" stroke-width="2.5"/>
<line x1="280" y1="266" x2="300" y2="266" stroke="#334155" stroke-width="2.5"/>
<line x1="300" y1="266" x2="300" y2="300" stroke="#334155" stroke-width="2.5"/>
<line x1="272" y1="222" x2="272" y2="272" stroke="#94a3b8" stroke-width="3" stroke-dasharray="7,5">
<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.54;1" dur="{D4}s" repeatCount="indefinite"/></line>
<line x1="272" y1="222" x2="272" y2="272" stroke="#059669" stroke-width="4.5" opacity="0">
<animate attributeName="opacity" values="0;0;1;1" keyTimes="0;0.5;0.54;1" dur="{D4}s" repeatCount="indefinite"/></line>
<line x1="260" y1="222" x2="260" y2="272" stroke="#334155" stroke-width="3"/>
<line x1="210" y1="247" x2="260" y2="247" stroke="#334155" stroke-width="2.5"/>
<polygon points="279,247 268,241 268,253" fill="#334155"/>
<text x="288" y="222" font-size="12.5" font-weight="bold" fill="#2563eb">D</text>
<text x="288" y="292" font-size="12.5" font-weight="bold" fill="#059669">S</text>
<text x="216" y="240" font-size="12.5" font-weight="bold" fill="#dc2626">G</text>
{gnd_sym(300, 314)}
<text x="312" y="262" font-size="11.5" font-weight="bold" fill="#475569">AO3400</text>
<rect x="90" y="228" width="66" height="38" rx="6" fill="#eff6ff" stroke="#2563eb" stroke-width="2"/>
<text x="123" y="251" text-anchor="middle" font-size="11.5" font-weight="bold" fill="#2563eb">MCU</text>
<line x1="156" y1="247" x2="210" y2="247" stroke="#334155" stroke-width="2.5"/>
<line x1="185" y1="247" x2="185" y2="270" stroke="#334155" stroke-width="2.5"/>
<rect x="174" y="270" width="22" height="36" fill="#f8fafc" stroke="#334155" stroke-width="2.5"/>
<text x="146" y="292" font-size="11" font-weight="bold" fill="#b45309">10kΩ</text>
<line x1="185" y1="306" x2="185" y2="314" stroke="#334155" stroke-width="2.5"/>
{gnd_sym(185, 328)}
<text x="120" y="352" font-size="10.5" fill="#475569">下拉防浮空</text>
<text x="360" y="290" font-size="12.5" font-weight="bold" fill="#dc2626" opacity="0">V_GS=0 &lt; V_TH=1.45V：沟道不存在<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.48;0.52;1" dur="{D4}s" repeatCount="indefinite"/></text>
<text x="360" y="290" font-size="12.5" font-weight="bold" fill="#059669" opacity="0">V_GS=3.3V &gt; V_TH：沟道打开，I_D=20mA<animate attributeName="opacity" values="0;0;1;1" keyTimes="0;0.48;0.52;1" dur="{D4}s" repeatCount="indefinite"/></text>
'''
    svg += f'<g><animate attributeName="opacity" values="0;0;1;1" keyTimes="0;0.5;0.56;1" dur="{D4}s" repeatCount="indefinite"/>'
    svg += flow("M88,76 H296 V306", D4/2, n=7, color="#2563eb", r=5.5) + '</g>'
    svg += f'''
<text x="595" y="58" text-anchor="middle" font-size="14" font-weight="bold" fill="#334155">栅压与漏流（同步）</text>
<text x="442" y="100" font-size="11.5" font-weight="bold" fill="#7c3aed">V_GS：0 / 3.3V</text>
<path d="{vgs_d}" fill="none" stroke="#7c3aed" stroke-width="3"/>
<line x1="430" y1="160" x2="762" y2="160" stroke="#64748b" stroke-width="1.5"/>
<text x="442" y="220" font-size="11.5" font-weight="bold" fill="#2563eb">I_D：0 / 20mA</text>
<path d="{id_d}" fill="none" stroke="#2563eb" stroke-width="3"/>
<line x1="430" y1="360" x2="762" y2="360" stroke="#64748b" stroke-width="1.5"/>
<line x1="430" y1="80" x2="430" y2="380" stroke="#f59e0b" stroke-width="2" opacity="0.8">
<animate attributeName="x1" values="430;760;430" keyTimes="0;0.99;1" dur="{D4}s" repeatCount="indefinite"/>
<animate attributeName="x2" values="430;760;430" keyTimes="0;0.99;1" dur="{D4}s" repeatCount="indefinite"/></line>
'''
    svg += caption("① 栅压 0V：沟道不存在，LED 灭——漏源之间是「断开的开关」", "#dc2626", D4,
                   "0;1;1;0;0", "0;0.04;0.44;0.5;1", y=410)
    svg += caption("② 栅压 3.3V > 阈值 1.45V：沟道形成，LED 亮，I_D=(5−2)÷150≈20mA", "#059669", D4,
                   "0;0;1;1", "0;0.52;0.58;1", y=410)
    svg += note_box("栅极只取 nA 级漏电——电压控制零功耗 · MCU 驱动必须选「逻辑电平」MOS（2N7000 在 3.3V 下不可靠）",
                    452, D4, "0;0.6;0.65;1", w=740, x=400)
    save('mosfet-switch.svg', svg + '</svg>')


# ======================= 图 5：运放反相放大 =======================
# 参数：Rin=1kΩ Rf=10kΩ → 增益 −10；vin ±0.5V → vout ∓5V（±12V 电源内，不饱和）
def make_opamp_inverting():
    D5 = 5
    vin_d = sine_path(60, 390, 350, 30)
    vout_d = sine_path(430, 770, 350, 55, phase=np.pi)
    svg = svg_open('运放反相放大器：「虚短虚断」是怎么回事（增益 = −Rf/Rin）', h=480)
    svg += f'''
<text x="300" y="58" text-anchor="middle" font-size="14" font-weight="bold" fill="#334155">反相放大电路（LM358，±12V 供电）</text>
<circle cx="90" cy="180" r="21" fill="none" stroke="#2563eb" stroke-width="2.5"/>
<path d="M79,180 q5.5,-14 11,0 q5.5,14 11,0" fill="none" stroke="#2563eb" stroke-width="2"/>
<text x="42" y="152" font-size="11.5" font-weight="bold" fill="#2563eb">vin ±0.5V</text>
<line x1="111" y1="180" x2="170" y2="180" stroke="#334155" stroke-width="2.5"/>
<line x1="90" y1="201" x2="90" y2="250" stroke="#334155" stroke-width="2.5"/>
{gnd_sym(90, 264)}
{resistor_h(190, 180, 56, 'Rin 1kΩ')}
<line x1="266" y1="180" x2="330" y2="180" stroke="#334155" stroke-width="2.5"/>
<circle cx="330" cy="180" r="4" fill="#334155"/>
<line x1="330" y1="180" x2="480" y2="180" stroke="#334155" stroke-width="2.5"/>
<polygon points="480,158 480,242 566,200" fill="#f8fafc" stroke="#334155" stroke-width="2.5"/>
<text x="492" y="186" font-size="15" font-weight="bold" fill="#dc2626">−</text>
<text x="492" y="228" font-size="15" font-weight="bold" fill="#059669">+</text>
<text x="500" y="262" font-size="11.5" fill="#475569">LM358</text>
<line x1="440" y1="220" x2="480" y2="220" stroke="#334155" stroke-width="2.5"/>
<line x1="440" y1="220" x2="440" y2="252" stroke="#334155" stroke-width="2.5"/>
{gnd_sym(440, 266)}
<line x1="330" y1="180" x2="330" y2="140" stroke="#334155" stroke-width="2.5"/>
{resistor_h(350, 140, 80, 'Rf 10kΩ')}
<line x1="450" y1="140" x2="566" y2="140" stroke="#334155" stroke-width="2.5"/>
<line x1="566" y1="140" x2="566" y2="200" stroke="#334155" stroke-width="2.5"/>
<line x1="566" y1="200" x2="630" y2="200" stroke="#334155" stroke-width="2.5"/>
<text x="640" y="205" font-size="13" font-weight="bold" fill="#dc2626">vout ∓5V</text>
<circle cx="330" cy="180" r="9" fill="none" stroke="#dc2626" stroke-width="2.5">
<animate attributeName="opacity" values="0.25;1;0.25" dur="1.4s" repeatCount="indefinite"/></circle>
<text x="300" y="216" font-size="12" font-weight="bold" fill="#dc2626">虚地 v− ≈ 0V</text>
<text x="390" y="108" text-anchor="middle" font-size="11.5" fill="#475569">i 全部走 Rf（运放不取流）</text>
'''
    svg += flow("M95,176 H326 V144 H562 V194", D5, n=6, color="#f59e0b", r=5)
    svg += f'''
<line x1="60" y1="350" x2="392" y2="350" stroke="#64748b" stroke-width="1.6"/>
<path d="{vin_d}" fill="none" stroke="#2563eb" stroke-width="3"/>
<text x="64" y="306" font-size="11.5" font-weight="bold" fill="#2563eb">输入 vin = ±0.5V</text>
<circle r="5.5" fill="#fff" stroke="#2563eb" stroke-width="3"><animateMotion dur="2.5s" repeatCount="indefinite" path="{vin_d}"/></circle>
<line x1="430" y1="350" x2="772" y2="350" stroke="#64748b" stroke-width="1.6"/>
<path d="{vout_d}" fill="none" stroke="#dc2626" stroke-width="3"/>
<text x="434" y="286" font-size="11.5" font-weight="bold" fill="#dc2626">输出 vout = ∓5V（反相 ×10）</text>
<circle r="5.5" fill="#fff" stroke="#dc2626" stroke-width="3"><animateMotion dur="2.5s" repeatCount="indefinite" path="{vout_d}"/></circle>
'''
    svg += caption("① 虚断：运放输入端取流≈0——i_in 没地方去，只能全部流向 Rf", "#b45309", D5,
                   "0;1;1;0;0", "0;0.04;0.2;0.24;1", y=418)
    svg += caption("② 虚短：负反馈强迫 v−≈v+=0V——v− 被钉在地上（虚地）", "#dc2626", D5,
                   "0;0;1;1;0;0", "0;0.24;0.28;0.48;0.52;1", y=418)
    svg += caption("③ 增益 = −Rf/Rin = −10k/1k = −10：只看两只电阻，与运放型号几乎无关", "#2563eb", D5,
                   "0;0;1;1;0;0", "0;0.52;0.56;0.76;0.8;1", y=418)
    svg += caption("④ 本质：输出反过来「喂」输入端——负反馈让电路自己纠错", "#059669", D5,
                   "0;0;1;1", "0;0.8;0.84;1", y=418)
    svg += note_box("i = vin/Rin → vout = −i·Rf → vout = −vin·(Rf/Rin)：两条虚字规则推完整个电路", 462, D5,
                    "0;0.86;0.9;1", w=700)
    save('opamp-inverting.svg', svg + '</svg>')


# ======================= 图 6：比较器迟滞 =======================
# 参数：LM393 开漏+4.7k 上拉；R1=R2=10k 分压 2.5V；R3=1MΩ 正反馈 → 窗口≈1V
def make_comparator_hysteresis():
    D5 = 5
    svg = svg_open('比较器迟滞：正反馈造出 1V「免疫区」（LM393，R1=R2=10k）', h=470)
    svg += f'''
<text x="230" y="58" text-anchor="middle" font-size="14" font-weight="bold" fill="#334155">带迟滞的比较器电路</text>
<text x="56" y="86" font-size="13" font-weight="bold" fill="#b45309">+5V</text>
<line x1="90" y1="80" x2="340" y2="80" stroke="#334155" stroke-width="2.5"/>
<line x1="120" y1="80" x2="120" y2="100" stroke="#334155" stroke-width="2.5"/>
{resistor_v(120, 100, 40, 'R1 10k')}
<line x1="120" y1="140" x2="120" y2="166" stroke="#334155" stroke-width="2.5"/>
<circle cx="120" cy="166" r="3.5" fill="#334155"/>
<line x1="120" y1="166" x2="120" y2="186" stroke="#334155" stroke-width="2.5"/>
{resistor_v(120, 186, 40, 'R2 10k')}
<line x1="120" y1="226" x2="120" y2="246" stroke="#334155" stroke-width="2.5"/>
{gnd_sym(120, 260)}
<text x="128" y="170" font-size="11" font-weight="bold" fill="#7c3aed">2.5V</text>
<line x1="120" y1="166" x2="260" y2="166" stroke="#334155" stroke-width="2.5"/>
<polygon points="260,148 260,232 336,190" fill="#f8fafc" stroke="#334155" stroke-width="2.5"/>
<text x="270" y="174" font-size="14" font-weight="bold" fill="#dc2626">−</text>
<text x="270" y="216" font-size="14" font-weight="bold" fill="#059669">+</text>
<text x="272" y="252" font-size="11" fill="#475569">LM393</text>
<circle cx="80" cy="290" r="18" fill="none" stroke="#2563eb" stroke-width="2.5"/>
<path d="M71,290 q4.5,-12 9,0 q4.5,12 9,0" fill="none" stroke="#2563eb" stroke-width="2"/>
<text x="30" y="322" font-size="10.5" font-weight="bold" fill="#2563eb">带噪信号</text>
<line x1="98" y1="290" x2="260" y2="290" stroke="#334155" stroke-width="2.5"/>
<line x1="260" y1="290" x2="260" y2="216" stroke="#334155" stroke-width="2.5"/>
<circle cx="200" cy="290" r="3.5" fill="#334155"/>
<line x1="80" y1="308" x2="80" y2="330" stroke="#334155" stroke-width="2.5"/>
{gnd_sym(80, 344)}
<line x1="310" y1="80" x2="310" y2="100" stroke="#334155" stroke-width="2.5"/>
{resistor_v(310, 100, 36, '4.7k')}
<line x1="310" y1="136" x2="310" y2="190" stroke="#334155" stroke-width="2.5"/>
<circle cx="310" cy="190" r="3.5" fill="#334155"/>
<line x1="336" y1="190" x2="370" y2="190" stroke="#334155" stroke-width="2.5"/>
<text x="342" y="180" font-size="12" font-weight="bold" fill="#059669">OUT</text>
<line x1="350" y1="190" x2="350" y2="318" stroke="#334155" stroke-width="2.5"/>
<line x1="350" y1="318" x2="296" y2="318" stroke="#334155" stroke-width="2.5"/>
<rect x="240" y="307" width="56" height="22" fill="#f8fafc" stroke="#b45309" stroke-width="2.5"/>
<text x="268" y="301" text-anchor="middle" font-size="11" font-weight="bold" fill="#b45309">R3 1MΩ</text>
<line x1="240" y1="318" x2="200" y2="318" stroke="#334155" stroke-width="2.5"/>
<line x1="200" y1="318" x2="200" y2="290" stroke="#334155" stroke-width="2.5"/>
<text x="252" y="346" font-size="11" fill="#475569">正反馈：输出「拽」输入</text>
<text x="590" y="58" text-anchor="middle" font-size="14" font-weight="bold" fill="#334155">传输特性：回滞环</text>
<line x1="440" y1="300" x2="760" y2="300" stroke="#64748b" stroke-width="2"/>
<line x1="440" y1="300" x2="440" y2="110" stroke="#64748b" stroke-width="2"/>
<text x="755" y="342" text-anchor="end" font-size="11.5" fill="#475569">vin →</text>
<text x="434" y="106" text-anchor="end" font-size="11.5" fill="#475569">vout</text>
<text x="433" y="134" text-anchor="end" font-size="11" fill="#475569">5V</text>
<text x="433" y="304" text-anchor="end" font-size="11" fill="#475569">0V</text>
<text x="622" y="318" text-anchor="middle" font-size="11" font-weight="bold" fill="#059669">3V</text>
<text x="558" y="318" text-anchor="middle" font-size="11" font-weight="bold" fill="#dc2626">2V</text>
<text x="744" y="318" text-anchor="middle" font-size="11" fill="#475569">5V</text>
<path d="M440,300 H622" stroke="#2563eb" stroke-width="3.5" fill="none"/>
<path d="M558,130 H755" stroke="#2563eb" stroke-width="3.5" fill="none"/>
<line x1="622" y1="300" x2="622" y2="130" stroke="#059669" stroke-width="3" stroke-dasharray="6,4">
<animate attributeName="opacity" values="0.35;1;0.35" dur="1.3s" repeatCount="indefinite"/></line>
<line x1="558" y1="130" x2="558" y2="300" stroke="#dc2626" stroke-width="3" stroke-dasharray="6,4">
<animate attributeName="opacity" values="0.35;1;0.35" dur="1.3s" begin="0.65s" repeatCount="indefinite"/></line>
<path d="M616,142 L622,130 L628,142" stroke="#059669" stroke-width="2.5" fill="none"/>
<path d="M552,288 L558,300 L564,288" stroke="#dc2626" stroke-width="2.5" fill="none"/>
<text x="636" y="122" font-size="11" font-weight="bold" fill="#059669">升到 3V 才跳高</text>
<text x="452" y="122" font-size="11" font-weight="bold" fill="#dc2626">降到 2V 才跳低</text>
<text x="590" y="245" text-anchor="middle" font-size="11.5" font-weight="bold" fill="#7c3aed">1V 免疫区</text>
<line x1="558" y1="255" x2="622" y2="255" stroke="#7c3aed" stroke-width="1.5"/>
<path d="M558,251 L558,259 M622,251 L622,259" stroke="#7c3aed" stroke-width="1.5"/>
<circle cx="450" cy="330" r="8" fill="#f59e0b" stroke="#b45309" stroke-width="2.5">
<animate attributeName="cx" values="450;745;450" keyTimes="0;0.5;1" dur="{D5}s" repeatCount="indefinite"/></circle>
<circle cx="772" cy="300" r="8" fill="#dc2626">
<animate attributeName="cy" values="300;300;130;130;300;300" keyTimes="0;0.385;0.415;0.885;0.915;1" dur="{D5}s" repeatCount="indefinite"/>
<animate attributeName="fill" values="#dc2626;#dc2626;#059669;#059669;#dc2626;#dc2626" keyTimes="0;0.385;0.415;0.885;0.915;1" dur="{D5}s" repeatCount="indefinite"/></circle>
<text x="764" y="352" font-size="10.5" fill="#475569">OUT</text>
'''
    svg += caption("① 基准 2.5V；R3 把输出状态「拽」回 IN+——阈值随输出而变", "#b45309", D5,
                   "0;1;1;0;0", "0;0.04;0.2;0.24;1", y=400)
    svg += caption("② 输出低时阈值被抬到 3V：输入必须升过 3V 才翻转", "#059669", D5,
                   "0;0;1;1;0;0", "0;0.24;0.28;0.5;0.54;1", y=400)
    svg += caption("③ 输出高时阈值被压到 2V：输入必须跌破 2V 才翻回", "#dc2626", D5,
                   "0;0;1;1;0;0", "0;0.54;0.58;0.78;0.82;1", y=400)
    svg += caption("④ 噪声在 1V 窗口里随便闹——输出纹丝不动", "#2563eb", D5,
                   "0;0;1;1", "0;0.82;0.86;1", y=400)
    svg += note_box("窗口 ≈ (Rin÷R3)·(VOH−VOL) · LM393 开漏输出必须接上拉电阻 4.7kΩ", 448, D5,
                    "0;0.88;0.92;1", w=620)
    save('comparator-hysteresis.svg', svg + '</svg>')


# ======================= 图 7：555 无稳态振荡 =======================
# 参数：R1=R2=10kΩ, C=10µF → f=1.44/((R1+2R2)C)≈4.8Hz，占空比 66.7%
def make_ne555_astable():
    D6 = 6
    cap_d = tri_cap(60, 380, 440, 400)
    out_d = sq_out(430, 750, 400, 440)
    svg = svg_open('555 无稳态振荡：内部三块拼图，外面三只元件（R1=R2=10k, C=10µF）', h=560)
    svg += f'''
<text x="34" y="66" font-size="13" font-weight="bold" fill="#b45309">+9V</text>
<line x1="70" y1="60" x2="560" y2="60" stroke="#334155" stroke-width="2.5"/>
<rect x="60" y="110" width="280" height="200" rx="10" fill="#eff6ff" stroke="#2563eb" stroke-width="2.5"/>
<text x="200" y="132" text-anchor="middle" font-size="14" font-weight="bold" fill="#2563eb">NE555</text>
<line x1="100" y1="110" x2="100" y2="140" stroke="#64748b" stroke-width="2"/>
<rect x="92" y="140" width="16" height="40" fill="#fff" stroke="#64748b" stroke-width="2"/>
<rect x="92" y="180" width="16" height="40" fill="#fff" stroke="#64748b" stroke-width="2"/>
<rect x="92" y="220" width="16" height="40" fill="#fff" stroke="#64748b" stroke-width="2"/>
<line x1="100" y1="260" x2="100" y2="290" stroke="#64748b" stroke-width="2"/>
<text x="66" y="152" font-size="9.5" fill="#475569">5kΩ×3</text>
<text x="116" y="184" font-size="10" font-weight="bold" fill="#7c3aed">2/3=6V</text>
<text x="116" y="244" font-size="10" font-weight="bold" fill="#7c3aed">1/3=3V</text>
<polygon points="170,165 170,195 194,180" fill="#fff" stroke="#334155" stroke-width="2"/>
<polygon points="170,225 170,255 194,240" fill="#fff" stroke="#334155" stroke-width="2"/>
<text x="170" y="158" font-size="9.5" fill="#475569">THRES</text>
<text x="172" y="272" font-size="9.5" fill="#475569">TRIG</text>
<rect x="220" y="185" width="66" height="60" rx="6" fill="#fff" stroke="#334155" stroke-width="2"/>
<text x="253" y="220" text-anchor="middle" font-size="11" font-weight="bold" fill="#334155">RS</text>
<line x1="194" y1="180" x2="220" y2="198" stroke="#334155" stroke-width="1.8"/>
<line x1="194" y1="240" x2="220" y2="228" stroke="#334155" stroke-width="1.8"/>
<line x1="320" y1="150" x2="320" y2="290" stroke="#334155" stroke-width="1.8"/>
<line x1="320" y1="220" x2="306" y2="206" stroke="#dc2626" stroke-width="2.5">
<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.66;0.7;1" dur="{D6}s" repeatCount="indefinite"/></line>
<line x1="320" y1="220" x2="306" y2="220" stroke="#059669" stroke-width="2.5" opacity="0">
<animate attributeName="opacity" values="0;0;1;1" keyTimes="0;0.66;0.7;1" dur="{D6}s" repeatCount="indefinite"/></line>
<circle cx="320" cy="220" r="3" fill="#334155"/>
<text x="286" y="302" font-size="9.5" fill="#475569">放电管</text>
<line x1="286" y1="215" x2="380" y2="215" stroke="#334155" stroke-width="2.5"/>
<text x="346" y="208" font-size="11" font-weight="bold" fill="#059669">3 OUT</text>
<line x1="200" y1="60" x2="200" y2="110" stroke="#334155" stroke-width="2.5"/>
<text x="208" y="82" font-size="10" fill="#475569">8/4 VCC</text>
<line x1="120" y1="310" x2="120" y2="330" stroke="#334155" stroke-width="2.5"/>
{gnd_sym(120, 344)}
<text x="96" y="326" font-size="10" fill="#475569">1</text>
<line x1="340" y1="150" x2="400" y2="150" stroke="#334155" stroke-width="2.5"/>
<text x="346" y="142" font-size="10" fill="#475569">7 DISCH</text>
<circle cx="400" cy="150" r="4" fill="#334155"/>
<line x1="340" y1="250" x2="400" y2="250" stroke="#334155" stroke-width="2.5"/>
<text x="346" y="242" font-size="10" fill="#475569">6/2</text>
<circle cx="400" cy="250" r="4" fill="#334155"/>
<line x1="400" y1="60" x2="400" y2="80" stroke="#334155" stroke-width="2.5"/>
{resistor_v(400, 80, 56, 'R1 10k')}
<line x1="400" y1="136" x2="400" y2="170" stroke="#334155" stroke-width="2.5"/>
{resistor_v(400, 170, 56, 'R2 10k')}
<line x1="400" y1="226" x2="400" y2="250" stroke="#334155" stroke-width="2.5"/>
<line x1="400" y1="250" x2="460" y2="250" stroke="#334155" stroke-width="2.5"/>
<line x1="460" y1="250" x2="460" y2="270" stroke="#334155" stroke-width="2.5"/>
<line x1="430" y1="270" x2="490" y2="270" stroke="#334155" stroke-width="3"/>
<line x1="430" y1="286" x2="490" y2="286" stroke="#334155" stroke-width="3"/>
<line x1="460" y1="286" x2="460" y2="320" stroke="#334155" stroke-width="2.5"/>
{gnd_sym(460, 334)}
<text x="500" y="284" font-size="12" font-weight="bold" fill="#2563eb">C 10µF</text>
'''
    svg += f'<g><animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.62;0.66;1" dur="{D6}s" repeatCount="indefinite"/>'
    svg += flow("M404,56 V246 H456 V266", D6*0.62, n=5, color="#059669", r=5) + '</g>'
    svg += f'<g><animate attributeName="opacity" values="0;0;1;1" keyTimes="0;0.66;0.7;1" dur="{D6}s" repeatCount="indefinite"/>'
    svg += flow("M456,288 H404 V154 H344", D6*0.3, n=4, color="#dc2626", r=5) + '</g>'
    svg += f'''
<text x="64" y="384" font-size="11" font-weight="bold" fill="#7c3aed">电容电压：3V ↔ 6V 三角波</text>
<path d="{cap_d}" fill="none" stroke="#7c3aed" stroke-width="3"/>
<line x1="60" y1="400" x2="382" y2="400" stroke="#94a3b8" stroke-width="1" stroke-dasharray="4,3"/>
<line x1="60" y1="440" x2="382" y2="440" stroke="#94a3b8" stroke-width="1" stroke-dasharray="4,3"/>
<text x="386" y="404" font-size="10" fill="#7c3aed">6V</text>
<text x="386" y="444" font-size="10" fill="#7c3aed">3V</text>
<text x="434" y="384" font-size="11" font-weight="bold" fill="#059669">OUT 方波（充电=高，放电=低）</text>
<path d="{out_d}" fill="none" stroke="#059669" stroke-width="3"/>
<line x1="430" y1="440" x2="752" y2="440" stroke="#64748b" stroke-width="1.5"/>
'''
    svg += caption("① 充电（绿）：电流经 R1+R2 给电容充值 → 到 6V 时 THRES 比较器翻转", "#059669", D6,
                   "0;1;1;0;0", "0;0.05;0.58;0.64;1", y=486)
    svg += caption("② 放电（红）：放电管导通，电容经 R2 从 7 脚泄放 → 到 3V 时 TRIG 翻转", "#dc2626", D6,
                   "0;0;1;1", "0;0.68;0.74;1", y=486)
    svg += note_box("f = 1.44÷((R1+2R2)·C) ≈ 4.8Hz，占空比 66% · 三个 5kΩ 分压电阻正是「555」名字的由来",
                    534, D6, "0;0.76;0.8;1", w=720)
    save('ne555-astable.svg', svg + '</svg>')


if __name__ == '__main__':
    make_rc_charge()
    make_bridge_rectifier()
    make_bjt_amplify()
    make_mosfet_switch()
    make_opamp_inverting()
    make_comparator_hysteresis()
    make_ne555_astable()
    print('all 7 SVGs regenerated into', os.path.abspath(OUT))

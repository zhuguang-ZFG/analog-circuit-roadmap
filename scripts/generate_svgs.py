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
[fill="#cbd5e1"]{fill:#334155}[stroke="#cbd5e1"]{stroke:#475569}
[fill="#ffffff"]{fill:#0f172a}[fill="#94a3b8"]{fill:#64748b}[stroke="#94a3b8"]{stroke:#64748b}
[fill="#7c3aed"]{fill:#a78bfa}[stroke="#7c3aed"]{stroke:#a78bfa}
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
    body = f'''<line x1="{x}" y1="{y-20}" x2="{x}" y2="{y}" stroke="{color}" stroke-width="2.5"/>
<rect x="{x-11}" y="{y}" width="22" height="{h}" fill="#f8fafc" stroke="{color}" stroke-width="2.5"/>
<line x1="{x}" y1="{y+h}" x2="{x}" y2="{y+h+20}" stroke="{color}" stroke-width="2.5"/>'''
    if label:
        body += f'\n<text x="{x+20}" y="{y+h/2+4}" font-size="12.5" font-weight="bold" fill="{lcolor}">{label}</text>'
    return body


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
<animate attributeName="opacity" values="0;0;0.3;1;1" keyTimes="0;0.5;0.56;0.75;1" dur="{D4}s" repeatCount="indefinite"/>
<line x1="312" y1="168" x2="328" y2="152"/><line x1="320" y1="176" x2="338" y2="162"/>
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


# ======================= 图 8：推挽 vs 开漏 =======================
def make_pushpull_opendrain():
    DP = 4
    rc_pts = []
    for i in range(41):
        u = i/40
        x = 380 + 180*u
        y = 380 - 50*(1-np.exp(-3*u))
        rc_pts.append(f"{x:.0f},{y:.0f}")
    rc_edge = "M" + " L".join(rc_pts)
    svg = svg_open('推挽 vs 开漏：为什么 I2C 偏偏选「慢」的那个？', h=460)
    svg += f'''
<text x="200" y="62" text-anchor="middle" font-size="14" font-weight="bold" fill="#334155">推挽：两个开关轮流推</text>
<text x="56" y="76" font-size="12.5" font-weight="bold" fill="#b45309">VDD</text>
<line x1="90" y1="70" x2="200" y2="70" stroke="#334155" stroke-width="2.5"/>
<line x1="200" y1="70" x2="200" y2="92" stroke="#334155" stroke-width="2.5"/>
<circle cx="200" cy="96" r="3.5" fill="#334155"/>
<line x1="200" y1="96" x2="226" y2="122" stroke="#059669" stroke-width="3">
<animate attributeName="opacity" values="1;1;0;0;0;1;1" keyTimes="0;0.22;0.26;0.72;0.76;0.98;1" dur="{DP}s" repeatCount="indefinite"/></line>
<circle cx="200" cy="126" r="3.5" fill="#334155"/>
<text x="232" y="106" font-size="11" font-weight="bold" fill="#059669">上管（推高）</text>
<line x1="200" y1="126" x2="200" y2="150" stroke="#334155" stroke-width="2.5"/>
<circle cx="200" cy="150" r="4" fill="#334155"/>
<line x1="200" y1="150" x2="330" y2="150" stroke="#334155" stroke-width="2.5"/>
<text x="336" y="146" font-size="12" font-weight="bold" fill="#2563eb">OUT</text>
<line x1="200" y1="150" x2="200" y2="174" stroke="#334155" stroke-width="2.5"/>
<circle cx="200" cy="174" r="3.5" fill="#334155"/>
<line x1="200" y1="174" x2="226" y2="200" stroke="#dc2626" stroke-width="3">
<animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="0;0.24;0.28;0.7;0.74;1" dur="{DP}s" repeatCount="indefinite"/></line>
<circle cx="200" cy="204" r="3.5" fill="#334155"/>
<text x="232" y="196" font-size="11" font-weight="bold" fill="#dc2626">下管（拉低）</text>
<line x1="200" y1="204" x2="200" y2="230" stroke="#334155" stroke-width="2.5"/>
{gnd_sym(200, 244)}
<text x="120" y="270" font-size="11" fill="#475569">两管交替导通：双向都有劲</text>
'''
    svg += f'<g><animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.22;0.26;1" dur="{DP}s" repeatCount="indefinite"/>'
    svg += flow("M94,66 H196 V146 H326", DP/4, n=6, color="#059669", r=5) + '</g>'
    svg += f'<g><animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="0;0.26;0.3;0.68;0.72;1" dur="{DP}s" repeatCount="indefinite"/>'
    svg += flow("M326,146 H204 V236", DP/4, n=6, color="#dc2626", r=5) + '</g>'
    svg += f'''
<text x="590" y="62" text-anchor="middle" font-size="14" font-weight="bold" fill="#334155">开漏：只有下管，靠电阻回高</text>
<text x="446" y="76" font-size="12.5" font-weight="bold" fill="#b45309">VDD</text>
<line x1="480" y1="70" x2="560" y2="70" stroke="#334155" stroke-width="2.5"/>
{resistor_v(560, 90, 50, '上拉 Rp')}
<line x1="560" y1="140" x2="560" y2="150" stroke="#334155" stroke-width="2.5"/>
<circle cx="560" cy="150" r="4" fill="#334155"/>
<line x1="560" y1="150" x2="700" y2="150" stroke="#334155" stroke-width="2.5"/>
<text x="706" y="146" font-size="12" font-weight="bold" fill="#2563eb">OUT</text>
<line x1="560" y1="150" x2="560" y2="174" stroke="#334155" stroke-width="2.5"/>
<circle cx="560" cy="174" r="3.5" fill="#334155"/>
<line x1="560" y1="174" x2="586" y2="200" stroke="#dc2626" stroke-width="3">
<animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="0;0.24;0.28;0.7;0.74;1" dur="{DP}s" repeatCount="indefinite"/></line>
<circle cx="560" cy="204" r="3.5" fill="#334155"/>
<text x="592" y="196" font-size="11" font-weight="bold" fill="#dc2626">下管（唯一开关）</text>
<line x1="560" y1="204" x2="560" y2="230" stroke="#334155" stroke-width="2.5"/>
{gnd_sym(560, 244)}
<text x="480" y="270" font-size="11" fill="#475569">下管断开时：Rp 慢慢把总线「充」回高电平</text>
'''
    svg += f'<g><animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.22;0.26;1" dur="{DP}s" repeatCount="indefinite"/>'
    svg += flow("M484,66 H556 V146 H696", DP/2, n=3, color="#b45309", r=5, keypoints="0;0.55;0.82;1", keytimes="0;0.2;0.5;1") + '</g>'
    svg += f'<g><animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="0;0.26;0.3;0.68;0.72;1" dur="{DP}s" repeatCount="indefinite"/>'
    svg += flow("M696,146 H564 V236", DP/4, n=6, color="#dc2626", r=5) + '</g>'
    svg += f'''
<text x="64" y="316" font-size="11.5" font-weight="bold" fill="#059669">推挽沿：陡（ns 级）</text>
<path d="M80,380 V330 H180 V380" fill="none" stroke="#059669" stroke-width="3"/>
<line x1="80" y1="380" x2="270" y2="380" stroke="#64748b" stroke-width="1.5"/>
<text x="360" y="316" font-size="11.5" font-weight="bold" fill="#b45309">开漏沿：RC 缓升（上拉×总线电容）</text>
<path d="{rc_edge}" fill="none" stroke="#b45309" stroke-width="3"/>
<line x1="380" y1="380" x2="580" y2="380" stroke="#64748b" stroke-width="1.5"/>
<text x="600" y="355" font-size="11" fill="#475569">I2C 上拉 2.2~4.7kΩ：阻小快但费电</text>
'''
    svg += caption("① 推挽输出高：上管合上，VDD 直推——又快又有劲（粒子密集）", "#059669", DP,
                   "0;1;1;0;0", "0;0.03;0.2;0.24;1", y=410)
    svg += caption("② 开漏输出高：只能靠上拉电阻慢慢充电——沿是 RC 曲线（粒子稀疏）", "#b45309", DP,
                   "0;0;1;1;0;0", "0;0.24;0.28;0.46;0.5;1", y=410)
    svg += caption("③ 那为什么 I2C 还选开漏？——多设备共享总线时，两个推挽互怼=短路烧IO！", "#dc2626", DP,
                   "0;0;1;1", "0;0.52;0.56;1", y=410)
    svg += note_box("开漏+上拉=「线与」：任何一个设备都能拉低总线——仲裁、中断共享、电平转换全靠它", 448, DP, "0;0.6;0.65;1", w=700)
    save('pushpull-opendrain.svg', svg + '</svg>')



# ======================= 图 9：LDO 负反馈 =======================
def make_ldo_feedback():
    DL = 5
    t_pts = []
    for i in range(81):
        u = i/80
        x = 60 + 320*u
        if u < 0.3:
            y = 340
        else:
            du = u - 0.3
            y = 340 + 26*np.exp(-du*6)*np.cos(du*22) - 6*np.exp(-du*4)
        t_pts.append(f"{x:.0f},{y:.1f}")
    fb_d = "M" + " L".join(t_pts)
    ol_pts = []
    for i in range(81):
        u = i/80
        x = 420 + 320*u
        y = 340 if u < 0.3 else 340 + 22*(1-np.exp(-(u-0.3)*9))
        ol_pts.append(f"{x:.0f},{y:.1f}")
    ol_d = "M" + " L".join(ol_pts)
    svg = svg_open('LDO 的本质：一个会「自我调节」的分压器（负反馈环路）', h=470)
    svg += f'''
<text x="330" y="62" text-anchor="middle" font-size="14" font-weight="bold" fill="#334155">LDO 内部负反馈环路（AMS1117 同款结构）</text>
<text x="56" y="96" font-size="13" font-weight="bold" fill="#b45309">VIN 8V</text>
<line x1="100" y1="90" x2="180" y2="90" stroke="#334155" stroke-width="2.5"/>
<rect x="180" y="78" width="80" height="26" fill="#fffbeb" stroke="#b45309" stroke-width="2.5"/>
<text x="220" y="95" text-anchor="middle" font-size="11.5" font-weight="bold" fill="#b45309">调整管</text>
<text x="220" y="118" text-anchor="middle" font-size="10" fill="#475569">≈ 自动可变电阻</text>
<line x1="260" y1="90" x2="330" y2="90" stroke="#334155" stroke-width="2.5"/>
<circle cx="330" cy="90" r="4" fill="#334155"/>
<line x1="330" y1="90" x2="400" y2="90" stroke="#334155" stroke-width="2.5"/>
<text x="408" y="95" font-size="13" font-weight="bold" fill="#059669">VOUT 5V</text>
{resistor_v(400, 110, 46, '负载')}
<line x1="400" y1="156" x2="400" y2="186" stroke="#334155" stroke-width="2.5"/>
{gnd_sym(400, 200)}
<line x1="350" y1="90" x2="350" y2="130" stroke="#334155" stroke-width="2" stroke-dasharray="4,3"/>
<circle cx="350" cy="130" r="3" fill="#334155"/>
<line x1="350" y1="130" x2="368" y2="148" stroke="#dc2626" stroke-width="2.5">
<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.28;0.32;1" dur="{DL}s" repeatCount="indefinite"/></line>
<circle cx="350" cy="152" r="3" fill="#334155"/>
{resistor_v(350, 166, 34, '突加')}
<line x1="350" y1="200" x2="350" y2="214" stroke="#334155" stroke-width="2"/>
{gnd_sym(350, 228)}
<text x="356" y="118" font-size="10" fill="#dc2626" text-anchor="middle">30%处加重</text>
<line x1="330" y1="90" x2="330" y2="130" stroke="#334155" stroke-width="2.5"/>
{resistor_v(330, 130, 34, '')}
<text x="318" y="151" text-anchor="end" font-size="12.5" font-weight="bold" fill="#b45309">R1</text>
<circle cx="330" cy="186" r="3.5" fill="#334155"/>
<line x1="330" y1="164" x2="330" y2="206" stroke="#334155" stroke-width="2.5"/>
{resistor_v(330, 206, 34, '')}
<text x="318" y="227" text-anchor="end" font-size="12.5" font-weight="bold" fill="#b45309">R2</text>
<line x1="330" y1="240" x2="330" y2="252" stroke="#334155" stroke-width="2"/>
{gnd_sym(330, 266)}
<polygon points="180,170 180,222 240,196" fill="#f8fafc" stroke="#334155" stroke-width="2.5"/>
<text x="188" y="196" font-size="13" font-weight="bold" fill="#dc2626">−</text>
<text x="188" y="216" font-size="13" font-weight="bold" fill="#059669">+</text>
<text x="168" y="240" font-size="10.5" fill="#475569">误差放大器</text>
<line x1="330" y1="186" x2="240" y2="186" stroke="#334155" stroke-width="2"/>
<text x="262" y="178" font-size="10" fill="#7c3aed">采样 1.25V</text>
<rect x="150" y="230" width="70" height="24" fill="#eff6ff" stroke="#2563eb" stroke-width="2"/>
<text x="185" y="246" text-anchor="middle" font-size="11" font-weight="bold" fill="#2563eb">基准 1.25V</text>
<line x1="185" y1="230" x2="185" y2="222" stroke="#334155" stroke-width="2"/>
<line x1="240" y1="196" x2="220" y2="196" stroke="#334155" stroke-width="2"/>
<line x1="220" y1="196" x2="220" y2="104" stroke="#334155" stroke-width="2"/>
<text x="226" y="152" font-size="10" fill="#475569">驱动</text>
<path d="M120,240 C80,240 80,120 130,104" fill="none" stroke="#7c3aed" stroke-width="2" stroke-dasharray="5,4">
<animate attributeName="opacity" values="0.3;1;0.3" dur="1.6s" repeatCount="indefinite"/></path>
<text x="70" y="180" font-size="10.5" font-weight="bold" fill="#7c3aed">反馈环</text>
'''
    svg += f'''
<text x="64" y="300" font-size="11.5" font-weight="bold" fill="#059669">有反馈：跌落→拉回（振铃后稳定）</text>
<path d="{fb_d}" fill="none" stroke="#059669" stroke-width="3"/>
<line x1="60" y1="340" x2="384" y2="340" stroke="#64748b" stroke-width="1.5"/>
<line x1="156" y1="320" x2="156" y2="366" stroke="#94a3b8" stroke-width="1" stroke-dasharray="4,3"/>
<text x="424" y="300" font-size="11.5" font-weight="bold" fill="#dc2626">若无反馈：一跌不起（负载调整率灾难）</text>
<path d="{ol_d}" fill="none" stroke="#dc2626" stroke-width="3"/>
<line x1="420" y1="340" x2="744" y2="340" stroke="#64748b" stroke-width="1.5"/>
<line x1="516" y1="320" x2="516" y2="366" stroke="#94a3b8" stroke-width="1" stroke-dasharray="4,3"/>
'''
    svg += caption("① 分压器 R1/R2 把 VOUT 采样回误差放大器，与 1.25V 基准比", "#7c3aed", DL,
                   "0;1;1;0;0", "0;0.04;0.24;0.28;1", y=410)
    svg += caption("② 负载突然加重 → VOUT 一跌 → 采样低于基准 → 误差放大器喊「不够！」", "#dc2626", DL,
                   "0;0;1;1;0;0", "0;0.28;0.32;0.55;0.6;1", y=410)
    svg += caption("③ 调整管立刻「调小自己的电阻」→ VOUT 拉回 5V——全自动，无需人管", "#059669", DL,
                   "0;0;1;1", "0;0.6;0.65;1", y=410)
    svg += note_box("VOUT = 1.25×(1+R1/R2) · 发热 = (VIN−VOUT)×I 全变成热——LDO 效率低的根因", 452, DL, "0;0.68;0.73;1", w=680)
    save('ldo-feedback.svg', svg + '</svg>')


# ======================= 图 10：模拟开关电荷注入 =======================
def make_analog_switch():
    DA = 6
    sh_pts = []
    per = 160
    x_start = 430
    for seg in range(2):
        hv = None
        for i in range(17):
            u = i/16
            x = x_start + seg*per + 40*u
            t = (x-x_start)/320*4*np.pi
            y = 330 - 42*np.sin(t)
            sh_pts.append(f"{x:.0f},{y:.0f}")
            hv = y
        x0 = x_start + seg*per + 40
        sh_pts.append(f"{x0:.0f},{hv+9:.0f}")
        sh_pts.append(f"{x_start+seg*per+160:.0f},{hv+9:.0f}")
    sh_d = "M" + " L".join(sh_pts)
    sin_d = sine_path(430, 750, 330, 42, n=96)
    svg = svg_open('模拟开关的暗伤：关断瞬间，沟道电荷被「挤」进电容（CD4066）', h=480)
    svg += f'''
<text x="215" y="60" text-anchor="middle" font-size="14" font-weight="bold" fill="#334155">采样保持电路（传输门 + 保持电容）</text>
<circle cx="60" cy="160" r="20" fill="none" stroke="#2563eb" stroke-width="2.5"/>
<path d="M50,160 q5,-13 10,0 q5,13 10,0" fill="none" stroke="#2563eb" stroke-width="2"/>
<text x="30" y="196" font-size="11" font-weight="bold" fill="#2563eb">输入</text>
<line x1="80" y1="160" x2="130" y2="160" stroke="#334155" stroke-width="2.5"/>
<circle cx="140" cy="160" r="3.5" fill="#334155"/>
<line x1="140" y1="160" x2="168" y2="136" stroke="#059669" stroke-width="3">
<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.6;0.64;1" dur="{DA}s" repeatCount="indefinite"/></line>
<circle cx="176" cy="160" r="3.5" fill="#334155"/>
<text x="118" y="128" font-size="11" font-weight="bold" fill="#334155">NMOS</text>
<text x="118" y="118" font-size="9.5" fill="#475569">传低电平好手</text>
<line x1="176" y1="160" x2="210" y2="160" stroke="#334155" stroke-width="2.5"/>
<line x1="140" y1="160" x2="140" y2="210" stroke="#334155" stroke-width="2.5"/>
<line x1="210" y1="160" x2="210" y2="210" stroke="#334155" stroke-width="2.5"/>
<circle cx="140" cy="210" r="3.5" fill="#334155"/>
<line x1="140" y1="210" x2="168" y2="186" stroke="#059669" stroke-width="3">
<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.6;0.64;1" dur="{DA}s" repeatCount="indefinite"/></line>
<circle cx="176" cy="210" r="3.5" fill="#334155"/>
<text x="96" y="240" font-size="11" font-weight="bold" fill="#334155">PMOS</text>
<text x="96" y="252" font-size="9.5" fill="#475569">传高电平好手</text>
<text x="226" y="130" font-size="10.5" fill="#7c3aed">EN/EN̅ 互补控制</text>
<text x="226" y="144" font-size="10" fill="#475569">两管同开同关</text>
<line x1="210" y1="160" x2="280" y2="160" stroke="#334155" stroke-width="2.5"/>
<line x1="210" y1="210" x2="280" y2="210" stroke="#334155" stroke-width="2.5"/>
<line x1="280" y1="160" x2="280" y2="210" stroke="#334155" stroke-width="2.5"/>
<circle cx="280" cy="185" r="4" fill="#334155"/>
<line x1="280" y1="185" x2="330" y2="185" stroke="#334155" stroke-width="2.5"/>
<line x1="330" y1="185" x2="330" y2="205" stroke="#334155" stroke-width="2.5"/>
<line x1="300" y1="205" x2="360" y2="205" stroke="#334155" stroke-width="3"/>
<line x1="300" y1="221" x2="360" y2="221" stroke="#334155" stroke-width="3"/>
<line x1="330" y1="221" x2="330" y2="250" stroke="#334155" stroke-width="2.5"/>
{gnd_sym(330, 264)}
<text x="370" y="217" font-size="12" font-weight="bold" fill="#2563eb">C 保持 100pF</text>
<g fill="#f59e0b" opacity="0">
<animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="0;0.3;0.36;0.6;0.66;1" dur="{DA}s" repeatCount="indefinite"/>
<circle cx="150" cy="172" r="2.6"/><circle cx="158" cy="168" r="2.6"/><circle cx="163" cy="174" r="2.6"/>
<circle cx="152" cy="222" r="2.6"/><circle cx="160" cy="218" r="2.6"/><circle cx="165" cy="224" r="2.6"/>
</g>
<g opacity="0"><animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="0;0.62;0.66;0.9;0.94;1" dur="{DA}s" repeatCount="indefinite"/>
{flow("M170,166 H272 V181 H324", 1.6, n=4, color="#f59e0b", r=4.5)}
{flow("M170,214 H272 V189 H324", 1.6, n=4, color="#f59e0b", r=4.5)}
</g>
<text x="150" y="285" font-size="11.5" font-weight="bold" fill="#b45309" opacity="0">关断瞬间：沟道电子「无家可归」，被挤进 C！
<animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="0;0.64;0.68;0.9;0.94;1" dur="{DA}s" repeatCount="indefinite"/></text>
'''
    svg += f'<g><animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.58;0.62;1" dur="{DA}s" repeatCount="indefinite"/>'
    svg += flow("M84,156 H126 M184,156 H272 V181 H324", DA*0.6, n=6, color="#059669", r=5) + '</g>'
    svg += f'''
<text x="590" y="60" text-anchor="middle" font-size="14" font-weight="bold" fill="#334155">采样保持波形（注入跳变放大）</text>
<path d="{sin_d}" fill="none" stroke="#94a3b8" stroke-width="1.8" stroke-dasharray="5,4"/>
<text x="436" y="272" font-size="10.5" fill="#64748b">输入（虚线）</text>
<path d="{sh_d}" fill="none" stroke="#2563eb" stroke-width="2.8"/>
<text x="436" y="252" font-size="10.5" font-weight="bold" fill="#2563eb">保持电容电压（实线）</text>
<line x1="430" y1="330" x2="752" y2="330" stroke="#64748b" stroke-width="1.4"/>
<line x1="470" y1="284" x2="470" y2="300" stroke="#dc2626" stroke-width="2.5" opacity="0">
<animate attributeName="opacity" values="0;0;1;1" keyTimes="0;0.64;0.68;1" dur="{DA}s" repeatCount="indefinite"/></line>
<text x="478" y="314" font-size="11" font-weight="bold" fill="#dc2626" opacity="0">电子注入→电压下陷 ΔV≈10mV
<animate attributeName="opacity" values="0;0;1;1" keyTimes="0;0.64;0.68;1" dur="{DA}s" repeatCount="indefinite"/></text>
'''
    svg += caption("① 导通：NMOS+PMOS 互补——低走高走全摆幅无损通过（R_ON≈125Ω）", "#059669", DA,
                   "0;1;1;0;0", "0;0.03;0.28;0.32;1", y=420)
    svg += caption("② 跟随期：电容贴着输入走——采样就是把波形「复印」到电容上", "#2563eb", DA,
                   "0;0;1;1;0;0", "0;0.32;0.36;0.58;0.62;1", y=420)
    svg += caption("③ 关断瞬间：沟道电子 Q≈1pC 涌入 100pF 电容 → 电压下陷 ΔV=Q/C≈10mV！", "#dc2626", DA,
                   "0;0;1;1", "0;0.62;0.66;1", y=420)
    svg += note_box("12 位 ADC 的 1 LSB@3.3V 仅 0.8mV——10mV 注入误差=12 LSB！对策：加大保持电容/低注入开关/差分抵消", 458, DA, "0;0.7;0.75;1", w=740)
    save('analog-switch.svg', svg + '</svg>')


# ======================= 图 12：回流路径 =======================
def make_pcb_return_path():
    DR = 5
    svg = svg_open('回流路径：信号的「回家路」，永远贴着它脚下走', h=490)
    svg += f'''
<text x="210" y="52" text-anchor="middle" font-size="13.5" font-weight="bold" fill="#059669">场景 A：完整地平面——回流紧贴信号正下方</text>
<rect x="50" y="76" width="42" height="26" rx="4" fill="#eff6ff" stroke="#2563eb" stroke-width="2"/>
<text x="71" y="93" text-anchor="middle" font-size="10" fill="#2563eb">驱动</text>
<rect x="330" y="76" width="42" height="26" rx="4" fill="#eff6ff" stroke="#2563eb" stroke-width="2"/>
<text x="351" y="93" text-anchor="middle" font-size="10" fill="#2563eb">负载</text>
<line x1="92" y1="89" x2="330" y2="89" stroke="#dc2626" stroke-width="3.5"/>
<text x="200" y="72" font-size="10.5" font-weight="bold" fill="#dc2626">信号（顶层走线）</text>
<rect x="60" y="140" width="300" height="24" fill="#cbd5e1" stroke="#94a3b8" stroke-width="1.5"/>
<text x="366" y="156" font-size="10.5" fill="#475569">地平面</text>
<line x1="330" y1="152" x2="92" y2="152" stroke="#059669" stroke-width="2.5" stroke-dasharray="6,4"/>
<text x="120" y="178" font-size="10.5" font-weight="bold" fill="#059669">回流（镜像电流，紧贴脚下）</text>
<rect x="92" y="89" width="238" height="63" fill="#059669" opacity="0.07"/>
<text x="200" y="132" font-size="10" fill="#059669" text-anchor="middle" opacity="0">环路面积≈0
<animate attributeName="opacity" values="0;0;1;1" keyTimes="0;0.3;0.36;1" dur="{DR}s" repeatCount="indefinite"/></text>
{flow("M94,86 H328", DR/2, n=5, color="#dc2626", r=4.5)}
<g><animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="0;0.12;0.18;0.85;0.92;1" dur="{DR}s" repeatCount="indefinite"/>
{flow("M328,152 H94", DR/2, n=5, color="#059669", r=4.5)}
</g>
'''
    svg += f'''
<text x="590" y="52" text-anchor="middle" font-size="13.5" font-weight="bold" fill="#dc2626">场景 B：地平面开槽——回流被迫绕大圈</text>
<rect x="430" y="76" width="42" height="26" rx="4" fill="#eff6ff" stroke="#2563eb" stroke-width="2"/>
<text x="451" y="93" text-anchor="middle" font-size="10" fill="#2563eb">驱动</text>
<rect x="710" y="76" width="42" height="26" rx="4" fill="#eff6ff" stroke="#2563eb" stroke-width="2"/>
<text x="731" y="93" text-anchor="middle" font-size="10" fill="#2563eb">负载</text>
<line x1="472" y1="89" x2="710" y2="89" stroke="#dc2626" stroke-width="3.5"/>
<rect x="440" y="140" width="120" height="24" fill="#cbd5e1" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="620" y="140" width="140" height="24" fill="#cbd5e1" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="560" y="138" width="60" height="28" fill="#ffffff" stroke="#dc2626" stroke-width="2" stroke-dasharray="5,3"/>
<text x="590" y="132" font-size="10.5" font-weight="bold" fill="#dc2626" text-anchor="middle">开槽！</text>
<polygon points="472,89 710,89 710,152 620,152 620,232 560,232 560,152 472,152" fill="#7c3aed" opacity="0.08">
<animate attributeName="opacity" values="0.08;0.08;0.22;0.22;0.08;0.08" keyTimes="0;0.42;0.5;0.85;0.92;1" dur="{DR}s" repeatCount="indefinite"/></polygon>
<path d="M710,152 H620 V232 H560 V152 H472" fill="none" stroke="#7c3aed" stroke-width="2.5" stroke-dasharray="6,4"/>
<text x="560" y="258" font-size="10.5" font-weight="bold" fill="#7c3aed" text-anchor="middle">回流绕槽大圈 = 环路面积暴增</text>
{flow("M474,86 H708", DR/2, n=5, color="#dc2626", r=4.5)}
<g><animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="0;0.42;0.5;0.9;0.96;1" dur="{DR}s" repeatCount="indefinite"/>
{flow("M708,152 H620 V228 H560 V152 H474", DR/2, n=6, color="#7c3aed", r=4.5)}
</g>
<g opacity="0"><animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="0;0.6;0.66;0.9;0.96;1" dur="{DR}s" repeatCount="indefinite"/>
<path d="M590,190 q14,-16 28,0 q14,16 28,0" fill="none" stroke="#dc2626" stroke-width="2" transform="translate(-40,-20)"/>
<path d="M590,190 q14,-16 28,0 q14,16 28,0" fill="none" stroke="#dc2626" stroke-width="1.4" opacity="0.6" transform="translate(-52,-40)"/>
<text x="640" y="200" font-size="10.5" font-weight="bold" fill="#dc2626">辐射 EMI</text>
</g>
'''
    svg += caption("① 高频回流不走「几何最短」，走「电感最小」——永远贴着信号正下方（镜像电流）", "#059669", DR,
                   "0;1;1;0;0", "0;0.03;0.3;0.36;1", y=420)
    svg += caption("② 地平面一开槽：回流被断桥逼得绕大圈，环路面积从≈0 暴增几十倍", "#7c3aed", DR,
                   "0;0;1;1;0;0", "0;0.38;0.44;0.62;0.68;1", y=420)
    svg += caption("③ 环路=环形天线：向外辐射 EMI 认证翻车，向内拾取干扰=莫名串扰", "#dc2626", DR,
                   "0;0;1;1", "0;0.68;0.74;1", y=420)
    svg += note_box("军规：任何信号线不许跨分割/开槽！换层时回流地过孔必须贴着信号过孔——「让回流贴着脚下回家」", 462, DR, "0;0.78;0.84;1", w=730)
    save('pcb-return-path.svg', svg + '</svg>')


# ======================= 图 13：差分对 =======================
def make_diff_pair():
    DD = 6
    svg = svg_open('差分对：只认「差」，不认「同」——运放第一级的灵魂', h=520)
    svg += f'''
<text x="330" y="52" text-anchor="middle" font-size="14" font-weight="bold" fill="#334155">差分对（长尾对）：2mA 的零和游戏</text>
<text x="56" y="76" font-size="12.5" font-weight="bold" fill="#b45309">VCC</text>
<line x1="90" y1="70" x2="480" y2="70" stroke="#334155" stroke-width="2.5"/>
{resistor_v(220, 90, 34, 'Rc1')}
{resistor_v(420, 90, 34, 'Rc2')}
{npn_svg(220, 200)}
{npn_svg(420, 200)}
<line x1="220" y1="255" x2="220" y2="285" stroke="#334155" stroke-width="2.5"/>
<line x1="420" y1="255" x2="420" y2="285" stroke="#334155" stroke-width="2.5"/>
<line x1="220" y1="285" x2="420" y2="285" stroke="#334155" stroke-width="2.5"/>
<circle cx="320" cy="285" r="4" fill="#334155"/>
<line x1="320" y1="285" x2="320" y2="300" stroke="#334155" stroke-width="2.5"/>
<circle cx="320" cy="318" r="16" fill="#f8fafc" stroke="#334155" stroke-width="2.5"/>
<line x1="320" y1="328" x2="320" y2="310" stroke="#7c3aed" stroke-width="2.5"/>
<polygon points="320,306 315,314 325,314" fill="#7c3aed"/>
<line x1="320" y1="334" x2="320" y2="350" stroke="#334155" stroke-width="2.5"/>
{gnd_sym(320, 364)}
<text x="344" y="322" font-size="11" font-weight="bold" fill="#7c3aed">尾电流源 I_EE=2mA（总量钉死）</text>
<text x="52" y="196" font-size="12.5" font-weight="bold" fill="#059669">IN+</text>
<text x="556" y="196" font-size="12.5" font-weight="bold" fill="#dc2626">IN−</text>
<line x1="90" y1="200" x2="135" y2="200" stroke="#334155" stroke-width="2.5"/>
<line x1="385" y1="200" x2="550" y2="200" stroke="#334155" stroke-width="2.5"/>
<circle cx="220" cy="160" r="3.5" fill="#334155"/>
<circle cx="420" cy="160" r="3.5" fill="#334155"/>
<text x="168" y="158" font-size="10.5" font-weight="bold" fill="#2563eb">vC1</text>
<text x="452" y="158" font-size="10.5" font-weight="bold" fill="#2563eb">vC2</text>
<text x="150" y="130" font-size="11" fill="#059669" opacity="0">↑ 升
<animate attributeName="opacity" values="0;1;1;0;0" keyTimes="0;0.06;0.4;0.46;1" dur="{DD}s" repeatCount="indefinite"/></text>
<text x="480" y="130" font-size="11" fill="#dc2626" opacity="0">↓ 降
<animate attributeName="opacity" values="0;1;1;0;0" keyTimes="0;0.06;0.4;0.46;1" dur="{DD}s" repeatCount="indefinite"/></text>
<text x="150" y="130" font-size="11" fill="#dc2626" opacity="0">↑ 同升
<animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="0;0.52;0.56;0.9;0.96;1" dur="{DD}s" repeatCount="indefinite"/></text>
<text x="480" y="130" font-size="11" fill="#dc2626" opacity="0">↑ 同升
<animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="0;0.52;0.56;0.9;0.96;1" dur="{DD}s" repeatCount="indefinite"/></text>
'''
    svg += f'<g><animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.44;0.5;1" dur="{DD}s" repeatCount="indefinite"/>'
    svg += flow("M320,300 V285 H220 V150 V110 V74", DD/3, n=6, color="#059669", r=5)
    svg += flow("M320,300 V285 H420 V150 V74", DD/3, n=1, color="#94a3b8", r=4) + '</g>'
    svg += f'<g><animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="0;0.5;0.56;0.9;0.96;1" dur="{DD}s" repeatCount="indefinite"/>'
    svg += flow("M320,300 V285 H220 V150 V74", DD/3, n=3, color="#2563eb", r=5)
    svg += flow("M320,300 V285 H420 V150 V74", DD/3, n=3, color="#2563eb", r=5) + '</g>'
    svg += f'''
<text x="180" y="402" font-size="11" font-weight="bold" fill="#475569">电流分配（Q1 绿 vs Q2 红）</text>
<rect y="414" height="16" fill="#059669" x="100" width="220">
<animate attributeName="x" values="100;100;195;195;100" keyTimes="0;0.45;0.55;0.95;1" dur="{DD}s" repeatCount="indefinite"/>
<animate attributeName="width" values="220;220;125;125;220" keyTimes="0;0.45;0.55;0.95;1" dur="{DD}s" repeatCount="indefinite"/></rect>
<rect x="320" y="414" height="16" fill="#dc2626" width="30">
<animate attributeName="width" values="30;30;125;125;30" keyTimes="0;0.45;0.55;0.95;1" dur="{DD}s" repeatCount="indefinite"/></rect>
<text x="100" y="450" font-size="10.5" fill="#059669" opacity="0">Q1 吃 1.8mA
<animate attributeName="opacity" values="0;1;1;0;0" keyTimes="0;0.06;0.4;0.46;1" dur="{DD}s" repeatCount="indefinite"/></text>
<text x="380" y="450" font-size="10.5" fill="#94a3b8" opacity="0">Q2 剩 0.2mA
<animate attributeName="opacity" values="0;1;1;0;0" keyTimes="0;0.06;0.4;0.46;1" dur="{DD}s" repeatCount="indefinite"/></text>
<text x="210" y="450" font-size="10.5" fill="#2563eb" opacity="0">各 1mA：谁也多吃不了
<animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="0;0.52;0.56;0.9;0.96;1" dur="{DD}s" repeatCount="indefinite"/></text>
'''
    svg += caption("① 差模（IN+升 IN−降）：尾电流此消彼长——vC1 降 vC2 升，输出拉开差距", "#059669", DD,
                   "0;1;1;0;0", "0;0.03;0.2;0.26;1", y=478)
    svg += caption("② 共模（两边同升）：尾源总量钉死，两管谁也多吃不了——输出纹丝不动", "#2563eb", DD,
                   "0;0;1;1;0;0", "0;0.28;0.33;0.48;0.53;1", y=478)
    svg += caption("③ 温度漂移是同向的=共模——被结构天然免疫，这就是运放第一级必选它的原因", "#7c3aed", DD,
                   "0;0;1;1", "0;0.55;0.6;1", y=478)
    svg += note_box("CMRR（共模抑制比）的全部秘密 = 尾电流源的内阻——内阻越大，共模越动弹不得", 500, DD, "0;0.66;0.71;1", w=700)
    save('diff-pair.svg', svg + '</svg>')


# ======================= 图 14：Buck 降压 =======================
def make_buck_converter():
    DB = 6
    il_pts = []
    for i in range(97):
        u = i/96
        x = 430 + 320*u
        seg = (u*3) % 1.0
        y = 372 - (30*seg/0.42 if seg < 0.42 else 30*(1-seg)/0.58)
        il_pts.append(f"{x:.0f},{y:.0f}")
    il_d = "M" + " L".join(il_pts)
    svg = svg_open('Buck 降压：电感是「水车惯性」，把断续水流碾成直流', h=520)
    svg += f'''
<text x="220" y="52" text-anchor="middle" font-size="14" font-weight="bold" fill="#334155">Buck 变换器（12V → 5V，占空比 42%）</text>
<text x="36" y="102" font-size="12.5" font-weight="bold" fill="#b45309">12V</text>
<line x1="70" y1="96" x2="130" y2="96" stroke="#334155" stroke-width="2.5"/>
<circle cx="140" cy="96" r="3.5" fill="#334155"/>
<line x1="140" y1="96" x2="170" y2="68" stroke="#059669" stroke-width="3">
<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.4;0.46;1" dur="{DB}s" repeatCount="indefinite"/></line>
<circle cx="176" cy="96" r="3.5" fill="#334155"/>
<text x="126" y="62" font-size="11" font-weight="bold" fill="#334155">开关 SW</text>
<line x1="176" y1="96" x2="200" y2="96" stroke="#334155" stroke-width="2.5"/>
<circle cx="205" cy="96" r="4" fill="#334155"/>
<text x="180" y="118" font-size="10" fill="#7c3aed">开关节点</text>
<path d="M205,96 q8,-16 16,0 q8,16 16,0 q8,-16 16,0 q8,16 16,0 q8,-16 16,0" fill="none" stroke="#7c3aed" stroke-width="2.5"/>
<text x="222" y="70" font-size="12" font-weight="bold" fill="#7c3aed">电感 L</text>
<line x1="285" y1="96" x2="320" y2="96" stroke="#334155" stroke-width="2.5"/>
<circle cx="320" cy="96" r="4" fill="#334155"/>
<line x1="320" y1="96" x2="380" y2="96" stroke="#334155" stroke-width="2.5"/>
<text x="384" y="101" font-size="12.5" font-weight="bold" fill="#059669">5V 输出</text>
<line x1="320" y1="96" x2="320" y2="130" stroke="#334155" stroke-width="2.5"/>
<line x1="304" y1="130" x2="336" y2="130" stroke="#2563eb" stroke-width="3.5"/>
<line x1="304" y1="142" x2="336" y2="142" stroke="#2563eb" stroke-width="3.5"/>
<line x1="320" y1="142" x2="320" y2="160" stroke="#334155" stroke-width="2"/>
{gnd_sym(320, 174)}
<text x="344" y="140" font-size="10.5" fill="#2563eb">C 滤波</text>
<line x1="205" y1="96" x2="205" y2="150" stroke="#334155" stroke-width="2.5"/>
<polygon points="205,146 193,170 217,170" fill="none" stroke="#334155" stroke-width="2.5"/>
<line x1="193" y1="146" x2="217" y2="146" stroke="#334155" stroke-width="3"/>
<line x1="205" y1="170" x2="205" y2="186" stroke="#334155" stroke-width="2.5"/>
{gnd_sym(205, 200)}
<text x="150" y="182" font-size="10.5" fill="#dc2626">续流二极管</text>
<line x1="40" y1="200" x2="40" y2="96" stroke="#334155" stroke-width="1.5" stroke-dasharray="4,3" opacity="0.4"/>
<line x1="40" y1="200" x2="320" y2="200" stroke="#334155" stroke-width="1.5" stroke-dasharray="4,3" opacity="0.4"/>
'''
    svg += f'<g><animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.4;0.46;1" dur="{DB}s" repeatCount="indefinite"/>'
    svg += flow("M74,92 H196 M214,92 H316", DB/3, n=6, color="#059669", r=5) + '</g>'
    svg += f'<g><animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="0;0.5;0.56;0.88;0.94;1" dur="{DB}s" repeatCount="indefinite"/>'
    svg += flow("M205,186 V160 M214,146 V100 M214,92 H316", DB/3, n=5, color="#dc2626", r=5) + '</g>'
    svg += f'''
<text x="440" y="252" font-size="11.5" font-weight="bold" fill="#7c3aed">开关节点电压（方波）</text>
<path d="M430,300 V268 H475 V300 H537 V268 H582 V300 H644 V268 H689 V300 H750" fill="none" stroke="#7c3aed" stroke-width="2.8"/>
<text x="440" y="332" font-size="11.5" font-weight="bold" fill="#059669">电感电流（三角波：斜坡升/斜坡降）</text>
<path d="{il_d}" fill="none" stroke="#059669" stroke-width="2.8"/>
<line x1="430" y1="392" x2="750" y2="392" stroke="#2563eb" stroke-width="2.8"/>
<text x="440" y="412" font-size="11.5" font-weight="bold" fill="#2563eb">输出电压（惯性碾平=直流 5V）</text>
'''
    svg += caption("① 开关闭合：12V 经电感向输出灌能量——电感电流斜坡上升（储 ½LI²）", "#059669", DB,
                   "0;1;1;0;0", "0;0.03;0.2;0.26;1", y=460)
    svg += caption("② 开关断开：电感不许电流突变，把节点拉到负压——二极管接住续流", "#dc2626", DB,
                   "0;0;1;1;0;0", "0;0.28;0.33;0.5;0.56;1", y=460)
    svg += caption("③ 伏秒平衡：电感一周期平均电压必须为 0 → Vout = D×Vin = 0.42×12 = 5V", "#7c3aed", DB,
                   "0;0;1;1", "0;0.58;0.64;1", y=460)
    svg += note_box("电感=水车的惯性：开关只管断续送水，惯性把水流碾平——效率 90%+ 的秘密是开关不顶压差", 494, DB, "0;0.7;0.75;1", w=730)
    save('buck-converter.svg', svg + '</svg>')


# ======================= 图 11：去耦电容 =======================
def make_cap_decoupling():
    DC = 5
    def dip_wave(x0, depth, w=0.06):
        pts = []
        for i in range(81):
            u = i/80
            x = x0 + 320*u
            y = 340 + depth*np.exp(-((u-0.5)**2)/(2*w**2))
            pts.append(f"{x:.0f},{y:.1f}")
        return "M" + " L".join(pts)
    a_d = dip_wave(60, 55)
    b_d = dip_wave(420, 10)
    svg = svg_open('去耦电容为什么要「贴脸」放？——走线电感 vs 本地水库', h=480)
    svg += f'''
<text x="200" y="50" text-anchor="middle" font-size="13.5" font-weight="bold" fill="#dc2626">场景 A：电容太远（或没有）</text>
<text x="46" y="102" font-size="12" font-weight="bold" fill="#b45309">5V 源</text>
<line x1="90" y1="96" x2="150" y2="96" stroke="#334155" stroke-width="2.5"/>
<path d="M150,96 q6,-14 12,0 q6,14 12,0 q6,-14 12,0 q6,14 12,0 q6,-14 12,0" fill="none" stroke="#7c3aed" stroke-width="2.5"/>
<line x1="210" y1="96" x2="260" y2="96" stroke="#334155" stroke-width="2.5"/>
<text x="148" y="76" font-size="11" font-weight="bold" fill="#7c3aed">走线电感 ~10nH</text>
<text x="148" y="64" font-size="10" fill="#475569">10cm 长走线</text>
<rect x="260" y="76" width="90" height="40" rx="6" fill="#eff6ff" stroke="#2563eb" stroke-width="2"/>
<text x="305" y="100" text-anchor="middle" font-size="12" font-weight="bold" fill="#2563eb">IC</text>
<line x1="305" y1="116" x2="305" y2="146" stroke="#334155" stroke-width="2"/>
{gnd_sym(305, 160)}
<text x="130" y="136" font-size="11" font-weight="bold" fill="#dc2626" opacity="0">尖峰来了，电感「顶住」不给过！
<animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="0;0.42;0.46;0.62;0.66;1" dur="{DC}s" repeatCount="indefinite"/></text>
<g opacity="0"><animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="0;0.4;0.44;0.6;0.64;1" dur="{DC}s" repeatCount="indefinite"/>
{flow("M262,92 H300", 1.0, n=2, color="#dc2626", r=4)}
</g>
<text x="590" y="50" text-anchor="middle" font-size="13.5" font-weight="bold" fill="#059669">场景 B：100nF 贴脸（&lt;3mm）</text>
<text x="436" y="102" font-size="12" font-weight="bold" fill="#b45309">5V 源</text>
<line x1="480" y1="96" x2="540" y2="96" stroke="#334155" stroke-width="2.5"/>
<path d="M540,96 q6,-14 12,0 q6,14 12,0 q6,-14 12,0 q6,14 12,0 q6,-14 12,0" fill="none" stroke="#7c3aed" stroke-width="2.5" opacity="0.45"/>
<line x1="600" y1="96" x2="650" y2="96" stroke="#334155" stroke-width="2.5"/>
<text x="540" y="76" font-size="11" fill="#94a3b8">走线电感（远，无所谓）</text>
<rect x="650" y="76" width="90" height="40" rx="6" fill="#eff6ff" stroke="#2563eb" stroke-width="2"/>
<text x="695" y="100" text-anchor="middle" font-size="12" font-weight="bold" fill="#2563eb">IC</text>
<line x1="695" y1="116" x2="695" y2="146" stroke="#334155" stroke-width="2"/>
{gnd_sym(695, 160)}
<line x1="650" y1="96" x2="630" y2="96" stroke="#334155" stroke-width="2.5"/>
<circle cx="650" cy="96" r="3.5" fill="#334155"/>
<line x1="630" y1="96" x2="630" y2="120" stroke="#334155" stroke-width="2.5"/>
<line x1="612" y1="120" x2="648" y2="120" stroke="#059669" stroke-width="3.5"/>
<line x1="612" y1="132" x2="648" y2="132" stroke="#059669" stroke-width="3.5"/>
<line x1="630" y1="132" x2="630" y2="146" stroke="#334155" stroke-width="2"/>
{gnd_sym(630, 160)}
<text x="584" y="130" font-size="11" font-weight="bold" fill="#059669">100nF</text>
<text x="560" y="146" font-size="9.5" fill="#475569">本地水库</text>
<g opacity="0"><animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="0;0.4;0.44;0.6;0.64;1" dur="{DC}s" repeatCount="indefinite"/>
{flow("M634,126 V100 H648 M654,96 H688", 1.0, n=4, color="#059669", r=4.5)}
</g>
<text x="470" y="136" font-size="11" font-weight="bold" fill="#059669" opacity="0">本地水库瞬时放水，电压纹丝不动
<animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="0;0.42;0.46;0.62;0.66;1" dur="{DC}s" repeatCount="indefinite"/></text>
'''
    svg += f'''
<text x="64" y="290" font-size="11.5" font-weight="bold" fill="#dc2626">A：电源脚电压塌陷 0.5V+（复位/误触发温床）</text>
<path d="{a_d}" fill="none" stroke="#dc2626" stroke-width="3"/>
<line x1="60" y1="340" x2="384" y2="340" stroke="#64748b" stroke-width="1.5"/>
<text x="424" y="290" font-size="11.5" font-weight="bold" fill="#059669">B：微纹波（&lt;50mV），电路安心工作</text>
<path d="{b_d}" fill="none" stroke="#059669" stroke-width="3"/>
<line x1="420" y1="340" x2="744" y2="340" stroke="#64748b" stroke-width="1.5"/>
'''
    svg += caption("① IC 翻转瞬间要 100mA 尖峰电流，但只持续几 ns", "#b45309", DC,
                   "0;1;1;0;0", "0;0.03;0.2;0.24;1", y=400)
    svg += caption("② 走线电感：直流随便过，ns 尖峰面前=断路（V=L·di/dt）", "#7c3aed", DC,
                   "0;0;1;1;0;0", "0;0.24;0.28;0.42;0.46;1", y=400)
    svg += caption("③ 100nF 贴脸=本地水库：它距离近、电感小，尖峰由它顶上", "#059669", DC,
                   "0;0;1;1;0;0", "0;0.46;0.5;0.68;0.72;1", y=400)
    svg += caption("④ 所以记住：距离&lt;3mm、先过电容再到 IC、电容回路越短越好", "#2563eb", DC,
                   "0;0;1;1", "0;0.72;0.76;1", y=400)
    svg += note_box("100nF 管高频（ns 尖峰）· 10µF 管中频 · 大电解管低频——三级去耦，各司其职", 458, DC, "0;0.8;0.84;1", w=640)
    save('cap-decoupling.svg', svg + '</svg>')


# ======================= 图 15：文氏桥振荡器 =======================
def make_wien_bridge():
    DW = 6
    osc_pts = []
    for i in range(161):
        u = i/160
        x = 420 + 330*u
        A = min(1.0, 0.12*np.exp(2.2*u))
        y = 320 - 44*A*np.sin(u*12*np.pi)
        osc_pts.append(f"{x:.0f},{y:.1f}")
    osc_d = "M" + " L".join(osc_pts)
    env_pts = []
    for i in range(61):
        u = i/60
        x = 420 + 330*u
        A = min(1.0, 0.12*np.exp(2.2*u))
        env_pts.append(f"{x:.0f},{320-44*A:.1f}")
    env_d = "M" + " L".join(env_pts)
    svg = svg_open('文氏桥振荡器：正弦波是怎么「无中生有」的', h=500)
    svg += f'''
<text x="200" y="52" text-anchor="middle" font-size="14" font-weight="bold" fill="#334155">RC 选频 + 增益=3 的同相放大</text>
<text x="14" y="145" font-size="11" fill="#475569">输入</text>
{resistor_h(60, 140, 40, 'R')}
<line x1="120" y1="140" x2="128" y2="140" stroke="#334155" stroke-width="2.5"/>
<line x1="128" y1="124" x2="128" y2="156" stroke="#334155" stroke-width="3"/>
<line x1="140" y1="124" x2="140" y2="156" stroke="#334155" stroke-width="3"/>
<text x="134" y="114" font-size="11" font-weight="bold" fill="#b45309">C</text>
<line x1="140" y1="140" x2="165" y2="140" stroke="#334155" stroke-width="2.5"/>
<circle cx="165" cy="140" r="4" fill="#334155"/>
<line x1="165" y1="140" x2="300" y2="140" stroke="#334155" stroke-width="2.5"/>
{resistor_v(165, 160, 30, 'R')}
<circle cx="220" cy="140" r="4" fill="#334155"/>
<line x1="220" y1="140" x2="220" y2="160" stroke="#334155" stroke-width="2.5"/>
<line x1="208" y1="160" x2="232" y2="160" stroke="#334155" stroke-width="3"/>
<line x1="208" y1="172" x2="232" y2="172" stroke="#334155" stroke-width="3"/>
<text x="238" y="170" font-size="11" font-weight="bold" fill="#b45309">C</text>
<line x1="220" y1="172" x2="220" y2="210" stroke="#334155" stroke-width="2.5"/>
<line x1="165" y1="210" x2="220" y2="210" stroke="#334155" stroke-width="2"/>
{gnd_sym(192, 224)}
<polygon points="300,110 300,170 360,140" fill="#f8fafc" stroke="#334155" stroke-width="2.5"/>
<text x="306" y="133" font-size="13" font-weight="bold" fill="#059669">+</text>
<text x="306" y="165" font-size="13" font-weight="bold" fill="#dc2626">−</text>
<line x1="360" y1="140" x2="408" y2="140" stroke="#334155" stroke-width="2.5"/>
<circle cx="390" cy="140" r="4" fill="#334155"/>
<text x="340" y="124" font-size="11" font-weight="bold" fill="#2563eb">输出正弦</text>
<line x1="300" y1="155" x2="300" y2="185" stroke="#334155" stroke-width="2"/>
<circle cx="300" cy="185" r="3.5" fill="#334155"/>
{resistor_h(320, 185, 30)}
<circle cx="378" cy="185" r="7" fill="#fff7ed" stroke="#b45309" stroke-width="2"/>
<path d="M372,185 q2,-4 3,0 q2,4 3,0 q2,-4 3,0" fill="none" stroke="#b45309" stroke-width="1.5"/>
<text x="378" y="212" text-anchor="middle" font-size="10" font-weight="bold" fill="#b45309">灯泡</text>
<text x="335" y="212" text-anchor="middle" font-size="10.5" font-weight="bold" fill="#b45309">Rf=2R</text>
<line x1="385" y1="185" x2="390" y2="185" stroke="#334155" stroke-width="2"/>
<line x1="390" y1="185" x2="390" y2="140" stroke="#334155" stroke-width="2"/>
{resistor_v(300, 205, 30, 'R1=R')}
<line x1="300" y1="255" x2="300" y2="262" stroke="#334155" stroke-width="2"/>
{gnd_sym(300, 276)}
<text x="230" y="256" font-size="10.5" fill="#475569">增益 = 1+Rf/R1 = 3</text>
<text x="40" y="118" font-size="11" fill="#475569">反馈回 +端</text>
<path d="M45,140 C20,140 20,310 200,310 C340,310 380,230 400,150" fill="none" stroke="#7c3aed" stroke-width="1.8" stroke-dasharray="5,4">
<animate attributeName="opacity" values="0.3;1;0.3" dur="1.8s" repeatCount="indefinite"/></path>
'''
    svg += f'''
<text x="585" y="252" text-anchor="middle" font-size="11.5" font-weight="bold" fill="#2563eb">起振过程：噪声种子 → 指数长大 → 稳幅</text>
<path d="{osc_d}" fill="none" stroke="#2563eb" stroke-width="2.5"/>
<path d="{env_d}" fill="none" stroke="#7c3aed" stroke-width="1.5" stroke-dasharray="5,4"/>
<line x1="420" y1="320" x2="750" y2="320" stroke="#64748b" stroke-width="1.4"/>
<line x1="420" y1="276" x2="750" y2="276" stroke="#94a3b8" stroke-width="1" stroke-dasharray="4,3"/>
<text x="700" y="270" font-size="10" fill="#7c3aed">灯泡稳幅</text>
<text x="440" y="340" font-size="10.5" fill="#475569">开机噪声里的 f₀ 分量被选中、每圈放大一点</text>
'''
    svg += caption("① RC 串并网络在 f₀=1/(2πRC) 处：相移恰好 0°、衰减恰好 1/3", "#7c3aed", DW,
                   "0;1;1;0;0", "0;0.03;0.22;0.28;1", y=430)
    svg += caption("② 同相放大器增益=3：3 × 1/3 = 1——环路增益=1、相移=0，巴克豪森判据成立", "#059669", DW,
                   "0;0;1;1;0;0", "0;0.28;0.33;0.55;0.61;1", y=430)
    svg += caption("③ 起振靠噪声种子；幅度长大靠增益>1；停在多大？——灯泡发热升阻自动稳幅", "#2563eb", DW,
                   "0;0;1;1", "0;0.61;0.67;1", y=430)
    svg += note_box("惠普第一桶金 HP200A 就是这颗灯泡：幅度大→灯丝热→阻升→增益降，自稳在 3 倍", 474, DW, "0;0.72;0.77;1", w=690)
    save('wien-bridge.svg', svg + '</svg>')


# ======================= 图 16：乙类推挽与交越失真 =======================
def make_class_b():
    DC2 = 6
    sin_d = sine_path(60, 390, 330, 40, n=72)
    xo_pts = []
    for i in range(97):
        u = i/96
        x = 430 + 320*u
        s = np.sin(u*4*np.pi)
        y = 330 - 40*(0 if abs(s) < 0.18 else (s-0.18*np.sign(s))/0.82)
        xo_pts.append(f"{x:.0f},{y:.0f}")
    xo_d = "M" + " L".join(xo_pts)
    sin_d2 = sine_path(430, 750, 330, 40, n=72)
    svg = svg_open('乙类推挽：两个人抬轿子，交接处摔了一跤（交越失真）', h=500)
    svg += f'''
<text x="200" y="52" text-anchor="middle" font-size="14" font-weight="bold" fill="#334155">乙类推挽输出级</text>
<text x="56" y="76" font-size="12.5" font-weight="bold" fill="#b45309">+VCC</text>
<line x1="90" y1="70" x2="140" y2="70" stroke="#334155" stroke-width="2.5"/>
<line x1="140" y1="70" x2="140" y2="86" stroke="#334155" stroke-width="2.5"/>
<rect x="112" y="86" width="56" height="30" rx="5" fill="#eff6ff" stroke="#2563eb" stroke-width="2"/>
<text x="140" y="106" text-anchor="middle" font-size="11" font-weight="bold" fill="#2563eb">NPN</text>
<line x1="140" y1="116" x2="140" y2="185" stroke="#334155" stroke-width="2.5"/>
<circle cx="140" cy="185" r="4" fill="#334155"/>
<line x1="140" y1="185" x2="320" y2="185" stroke="#334155" stroke-width="2.5"/>
<text x="328" y="190" font-size="12" font-weight="bold" fill="#2563eb">输出</text>
<rect x="112" y="200" width="56" height="30" rx="5" fill="#fef2f2" stroke="#dc2626" stroke-width="2"/>
<text x="140" y="220" text-anchor="middle" font-size="11" font-weight="bold" fill="#dc2626">PNP</text>
<line x1="140" y1="185" x2="140" y2="200" stroke="#334155" stroke-width="2.5"/>
<line x1="140" y1="230" x2="140" y2="250" stroke="#334155" stroke-width="2.5"/>
<text x="56" y="256" font-size="12.5" font-weight="bold" fill="#b45309">−VEE</text>
<line x1="90" y1="250" x2="140" y2="250" stroke="#334155" stroke-width="2.5"/>
<line x1="60" y1="160" x2="112" y2="160" stroke="#334155" stroke-width="2.5"/>
<line x1="112" y1="160" x2="112" y2="101" stroke="#334155" stroke-width="2"/>
<line x1="112" y1="160" x2="112" y2="215" stroke="#334155" stroke-width="2"/>
<text x="30" y="156" font-size="11" fill="#475569">输入</text>
'''
    svg += f'<g><animate attributeName="opacity" values="1;1;0;0;0;1;1" keyTimes="0;0.22;0.26;0.7;0.74;0.96;1" dur="{DC2}s" repeatCount="indefinite"/>'
    svg += flow("M136,88 V116 V181 H314", DC2/4, n=5, color="#059669", r=5) + '</g>'
    svg += f'<g><animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="0;0.26;0.3;0.68;0.72;1" dur="{DC2}s" repeatCount="indefinite"/>'
    svg += flow("M314,181 H144 V228 V246", DC2/4, n=5, color="#dc2626", r=5) + '</g>'
    svg += f'''
<text x="64" y="290" font-size="11.5" font-weight="bold" fill="#475569">输入正弦</text>
<path d="{sin_d}" fill="none" stroke="#94a3b8" stroke-width="2.2"/>
<text x="434" y="290" font-size="11.5" font-weight="bold" fill="#dc2626">乙类输出：过零豁口（死区 ±0.7V）</text>
<path d="{sin_d2}" fill="none" stroke="#94a3b8" stroke-width="1.5" stroke-dasharray="4,3"/>
<path d="{xo_d}" fill="none" stroke="#dc2626" stroke-width="2.8"/>
<rect x="504" y="316" width="12" height="28" fill="#dc2626" opacity="0.12">
<animate attributeName="opacity" values="0.12;0.12;0.4;0.4;0.12;0.12" keyTimes="0;0.44;0.5;0.88;0.94;1" dur="{DC2}s" repeatCount="indefinite"/></rect>
<rect x="584" y="316" width="12" height="28" fill="#dc2626" opacity="0.12">
<animate attributeName="opacity" values="0.12;0.12;0.4;0.4;0.12;0.12" keyTimes="0;0.44;0.5;0.88;0.94;1" dur="{DC2}s" repeatCount="indefinite"/></rect>
<rect x="664" y="316" width="12" height="28" fill="#dc2626" opacity="0.12">
<animate attributeName="opacity" values="0.12;0.12;0.4;0.4;0.12;0.12" keyTimes="0;0.44;0.5;0.88;0.94;1" dur="{DC2}s" repeatCount="indefinite"/></rect>
<text x="590" y="356" font-size="10" fill="#dc2626">豁口=两管全关</text>
'''
    svg += caption("① 正半周：NPN 导通往下「推」电流（绿粒子）", "#059669", DC2,
                   "0;1;1;0;0", "0;0.03;0.2;0.24;1", y=430)
    svg += caption("② 负半周：PNP 导通往上「拉」电流（红粒子）", "#dc2626", DC2,
                   "0;0;1;1;0;0", "0;0.24;0.28;0.46;0.5;1", y=430)
    svg += caption("③ 交接区 |输入|&lt;0.7V：两管全关→输出豁口——这就是交越失真", "#b45309", DC2,
                   "0;0;1;1;0;0", "0;0.5;0.54;0.72;0.76;1", y=430)
    svg += caption("④ 甲乙类解法：基极间塞两只二极管预加微偏置——死区消失，功放标配", "#2563eb", DC2,
                   "0;0;1;1", "0;0.76;0.8;1", y=430)
    svg += note_box("偏置管要紧贴功率管安装（热耦合）——否则温度升→电流增→更热：热失控烧管", 474, DC2, "0;0.84;0.88;1", w=660)
    save('class-b-crossover.svg', svg + '</svg>')


# ======================= 图 17：Sallen-Key 滤波器 =======================
def make_sallen_key():
    DS = 7
    freqs = np.linspace(0.05, 4, 121)
    def bode(Q):
        pts = []
        for i, f in enumerate(freqs):
            H = 1/np.sqrt((1-f**2)**2 + (f/Q)**2)
            db = max(-52, 20*np.log10(H))
            x = 420 + (np.log10(f)-np.log10(0.05))/(np.log10(4)-np.log10(0.05))*320
            y = 262 - db*1.9
            pts.append(f"{x:.0f},{y:.0f}")
        return "M" + " L".join(pts)
    flat_d = bode(0.707); peak_d = bode(3.0)
    sin_in = sine_path(430, 750, 130, 30, n=72)
    lo_pts = []
    for i in range(73):
        u = i/72
        x = 430 + 320*u
        y = 130 - 30*np.sin(u*4*np.pi)*np.exp(-u*2.2)
        lo_pts.append(f"{x:.0f},{y:.0f}")
    lo_d = "M" + " L".join(lo_pts)
    svg = svg_open('Sallen-Key 二阶低通：滤波器是「受控的谐振」', h=520)
    svg += f'''
<text x="200" y="52" text-anchor="middle" font-size="14" font-weight="bold" fill="#334155">Sallen-Key 二阶低通（单位增益）</text>
<line x1="40" y1="140" x2="60" y2="140" stroke="#334155" stroke-width="2.5"/>
<text x="18" y="145" font-size="11" fill="#475569">输入</text>
{resistor_h(60, 140, 40, 'R1')}
{resistor_h(140, 140, 40, 'R2')}
<circle cx="216" cy="140" r="4" fill="#334155"/>
<line x1="216" y1="140" x2="250" y2="140" stroke="#334155" stroke-width="2.5"/>
<line x1="130" y1="140" x2="130" y2="100" stroke="#334155" stroke-width="2"/>
<line x1="118" y1="100" x2="142" y2="100" stroke="#7c3aed" stroke-width="3"/>
<line x1="118" y1="90" x2="142" y2="90" stroke="#7c3aed" stroke-width="3"/>
<line x1="130" y1="90" x2="130" y2="76" stroke="#334155" stroke-width="2"/>
<line x1="130" y1="76" x2="300" y2="76" stroke="#334155" stroke-width="2"/>
<text x="148" y="99" font-size="10.5" fill="#7c3aed">C1（反馈顶帽）</text>
<line x1="216" y1="140" x2="216" y2="180" stroke="#334155" stroke-width="2"/>
<line x1="204" y1="180" x2="228" y2="180" stroke="#7c3aed" stroke-width="3"/>
<line x1="204" y1="192" x2="228" y2="192" stroke="#7c3aed" stroke-width="3"/>
<line x1="216" y1="192" x2="216" y2="210" stroke="#334155" stroke-width="2"/>
{gnd_sym(216, 224)}
<text x="150" y="190" font-size="10.5" fill="#7c3aed">C2 下地</text>
<polygon points="250,110 250,170 310,140" fill="#f8fafc" stroke="#334155" stroke-width="2.5"/>
<text x="256" y="134" font-size="13" font-weight="bold" fill="#059669">+</text>
<text x="256" y="160" font-size="13" font-weight="bold" fill="#dc2626">−</text>
<line x1="250" y1="140" x2="244" y2="140" stroke="#334155" stroke-width="2.5"/>
<line x1="310" y1="140" x2="380" y2="140" stroke="#334155" stroke-width="2.5"/>
<text x="316" y="126" font-size="11" font-weight="bold" fill="#2563eb">输出</text>
<circle cx="350" cy="140" r="4" fill="#334155"/>
<line x1="350" y1="140" x2="350" y2="195" stroke="#334155" stroke-width="2"/>
<line x1="350" y1="195" x2="244" y2="195" stroke="#334155" stroke-width="2"/>
<line x1="244" y1="195" x2="244" y2="155" stroke="#334155" stroke-width="2"/>
<line x1="244" y1="155" x2="250" y2="155" stroke="#334155" stroke-width="2"/>
<line x1="300" y1="76" x2="310" y2="76" stroke="#334155" stroke-width="2"/>
<line x1="310" y1="76" x2="330" y2="76" stroke="#334155" stroke-width="2"/>
<line x1="330" y1="76" x2="330" y2="140" stroke="#334155" stroke-width="2"/>
'''
    svg += f'''
<text x="590" y="52" text-anchor="middle" font-size="14" font-weight="bold" fill="#334155">频响：Q 决定峰化</text>
<path d="{flat_d}" fill="none" stroke="#059669" stroke-width="2.8"/>
<path d="{peak_d}" fill="none" stroke="#dc2626" stroke-width="2.2" stroke-dasharray="6,4"/>
<line x1="420" y1="262" x2="750" y2="262" stroke="#64748b" stroke-width="1.4"/>
<line x1="566" y1="230" x2="566" y2="370" stroke="#94a3b8" stroke-width="1" stroke-dasharray="4,3"/>
<text x="556" y="384" font-size="10.5" fill="#475569">fc</text>
<text x="440" y="246" font-size="10.5" fill="#059669">Q=0.707 最平坦（Butterworth）</text>
<text x="580" y="222" font-size="10.5" fill="#dc2626">Q=3 峰化鼓包→再大就振荡</text>
<text x="648" y="330" font-size="10.5" fill="#475569">−40dB/dec</text>
<text x="440" y="86" font-size="11.5" font-weight="bold" fill="#475569">高频输入（实线）→ 输出（衰减）</text>
<path d="{sin_in}" fill="none" stroke="#94a3b8" stroke-width="1.6"/>
<path d="{lo_d}" fill="none" stroke="#059669" stroke-width="2.5"/>
'''
    svg += caption("① 低频：C 开路信号直通——增益=1", "#059669", DS,
                   "0;1;1;0;0", "0;0.03;0.18;0.23;1", y=460)
    svg += caption("② fc 附近：C1 顶帽正反馈「托一把」——Q 值决定这里是平还是鼓包", "#dc2626", DS,
                   "0;0;1;1;0;0", "0;0.23;0.28;0.48;0.53;1", y=460)
    svg += caption("③ 高频：两级 RC 接力衰减，−40dB/十倍频滚降", "#7c3aed", DS,
                   "0;0;1;1;0;0", "0;0.53;0.58;0.78;0.83;1", y=460)
    svg += caption("④ 级数每+1 滚降+20dB——要更陡？多级级联，Q 值按查表分配", "#2563eb", DS,
                   "0;0;1;1", "0;0.83;0.88;1", y=460)
    svg += note_box("fc = 1/(2πRC)（R1=R2、C1=C2 时）· Q 由增益设定——滤波器不是衰减器，是受控的谐振", 494, DS, "0;0.88;0.92;1", w=730)
    save('sallen-key.svg', svg + '</svg>')


# ======================= 图 18：电流镜 =======================
def make_current_mirror():
    DM = 6
    svg = svg_open('电流镜：共用一个 V_BE 的「复印机」', h=500)
    svg += f'''
<text x="300" y="52" text-anchor="middle" font-size="14" font-weight="bold" fill="#334155">基本电流镜（Q1 二极管接法设基准，Q2 复印输出）</text>
<text x="30" y="76" font-size="12.5" font-weight="bold" fill="#b45309">VCC</text>
<line x1="60" y1="70" x2="560" y2="70" stroke="#334155" stroke-width="2.5"/>
{resistor_v(140, 90, 34, 'R_SET')}
<text x="60" y="150" font-size="11" font-weight="bold" fill="#059669">I_REF=1mA</text>
<line x1="105" y1="200" x2="355" y2="200" stroke="#334155" stroke-width="2.5"/>
{npn_svg(140, 200)}
{npn_svg(440, 200)}
<path d="M140,165 V152 H98 V190 H105" fill="none" stroke="#7c3aed" stroke-width="2" stroke-dasharray="4,3"/>
<text x="220" y="142" font-size="10.5" fill="#7c3aed">C-B 短接=二极管接法</text>
<line x1="140" y1="255" x2="140" y2="285" stroke="#334155" stroke-width="2.5"/>
{gnd_sym(140, 299)}
<line x1="440" y1="255" x2="440" y2="285" stroke="#334155" stroke-width="2.5"/>
{gnd_sym(440, 299)}
<line x1="440" y1="145" x2="440" y2="120" stroke="#334155" stroke-width="2.5"/>
<circle cx="440" cy="120" r="4" fill="#334155"/>
<line x1="440" y1="120" x2="500" y2="120" stroke="#334155" stroke-width="2.5"/>
<rect x="500" y="100" width="60" height="40" rx="5" fill="#f8fafc" stroke="#334155" stroke-width="2"/>
<text x="530" y="124" text-anchor="middle" font-size="11" fill="#475569">负载</text>
<line x1="560" y1="120" x2="560" y2="70" stroke="#334155" stroke-width="2.5"/>
<text x="452" y="112" font-size="11" font-weight="bold" fill="#2563eb">I_OUT≈1mA</text>
<path d="M200,240 C280,290 360,290 420,240" fill="none" stroke="#7c3aed" stroke-width="1.8" stroke-dasharray="5,4"/>
<polygon points="420,240 410,238 413,248" fill="#7c3aed"/>
<text x="280" y="292" font-size="11" fill="#7c3aed">同一个 V_BE → 同一份 I_C</text>
<text x="120" y="330" font-size="11" fill="#059669" opacity="0">V_BE 自动建立
<animate attributeName="opacity" values="0;1;1;0;0" keyTimes="0;0.06;0.4;0.46;1" dur="{DM}s" repeatCount="indefinite"/></text>
<text x="400" y="330" font-size="11" fill="#2563eb" opacity="0">电流被复印
<animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="0;0.52;0.56;0.9;0.96;1" dur="{DM}s" repeatCount="indefinite"/></text>
'''
    svg += f'<g><animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.44;0.5;1" dur="{DM}s" repeatCount="indefinite"/>'
    svg += flow("M64,66 H140 V160 V235 V281", DM/3, n=6, color="#059669", r=5) + '</g>'
    svg += f'<g><animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="0;0.5;0.56;0.9;0.96;1" dur="{DM}s" repeatCount="indefinite"/>'
    svg += flow("M556,66 V116 H505 M444,124 V160 V235 V281", DM/3, n=5, color="#2563eb", r=5) + '</g>'
    svg += caption("① R_SET 注入 I_REF——Q1 二极管接法让 V_BE 自动停在「恰好流过 1mA」的值", "#059669", DM,
                   "0;1;1;0;0", "0;0.03;0.22;0.28;1", y=430)
    svg += caption("② 同一根基极线把这只 V_BE 同时喂给 Q2——V_BE 相同，I_C 就相同：电流被复印", "#2563eb", DM,
                   "0;0;1;1;0;0", "0;0.3;0.35;0.58;0.64;1", y=430)
    svg += caption("③ Q2 集电极电压随负载怎么变，电流纹丝不动——这就是「电流源」", "#7c3aed", DM,
                   "0;0;1;1", "0;0.64;0.7;1", y=430)
    svg += note_box("误差源头：两只基流都从 I_REF 里扣（β 有限）——Wilson 镜再加一管，把误差再压一个数量级", 474, DM, "0;0.74;0.79;1", w=700)
    save('current-mirror.svg', svg + '</svg>')


# ======================= 图 19：Boost 升压 =======================
def make_boost_converter():
    DB2 = 6
    il_pts = []
    for i in range(97):
        u = i/96
        x = 430 + 320*u
        seg = (u*3) % 1.0
        y = 372 - (30*seg/0.5 if seg < 0.5 else 30*(1-seg)/0.5)
        il_pts.append(f"{x:.0f},{y:.0f}")
    il_d = "M" + " L".join(il_pts)
    svg = svg_open('Boost 升压：电感「叠罗汉」把电压顶上去', h=520)
    svg += f'''
<text x="230" y="52" text-anchor="middle" font-size="14" font-weight="bold" fill="#334155">Boost 变换器（12V → 24V，占空比 50%）</text>
<text x="18" y="102" font-size="12.5" font-weight="bold" fill="#b45309">12V</text>
<line x1="48" y1="96" x2="90" y2="96" stroke="#334155" stroke-width="2.5"/>
<path d="M90,96 q8,-16 16,0 q8,16 16,0 q8,-16 16,0 q8,16 16,0 q8,-16 16,0" fill="none" stroke="#7c3aed" stroke-width="2.5"/>
<text x="106" y="70" font-size="12" font-weight="bold" fill="#7c3aed">电感 L</text>
<line x1="170" y1="96" x2="205" y2="96" stroke="#334155" stroke-width="2.5"/>
<circle cx="205" cy="96" r="4" fill="#334155"/>
<text x="182" y="118" font-size="10" fill="#7c3aed">开关节点</text>
<line x1="205" y1="96" x2="230" y2="96" stroke="#334155" stroke-width="2.5"/>
<polygon points="254,96 230,84 230,108" fill="none" stroke="#334155" stroke-width="2.5"/>
<line x1="254" y1="84" x2="254" y2="108" stroke="#334155" stroke-width="3"/>
<text x="222" y="78" font-size="10.5" fill="#dc2626">二极管</text>
<line x1="254" y1="96" x2="320" y2="96" stroke="#334155" stroke-width="2.5"/>
<circle cx="320" cy="96" r="4" fill="#334155"/>
<line x1="320" y1="96" x2="370" y2="96" stroke="#334155" stroke-width="2.5"/>
<text x="374" y="101" font-size="12.5" font-weight="bold" fill="#059669">24V 输出</text>
<line x1="320" y1="96" x2="320" y2="130" stroke="#334155" stroke-width="2.5"/>
<line x1="304" y1="130" x2="336" y2="130" stroke="#2563eb" stroke-width="3.5"/>
<line x1="304" y1="142" x2="336" y2="142" stroke="#2563eb" stroke-width="3.5"/>
<line x1="320" y1="142" x2="320" y2="160" stroke="#334155" stroke-width="2"/>
{gnd_sym(320, 174)}
<text x="344" y="140" font-size="10.5" fill="#2563eb">C 撑住输出</text>
<line x1="205" y1="96" x2="205" y2="150" stroke="#334155" stroke-width="2.5"/>
<circle cx="205" cy="156" r="3.5" fill="#334155"/>
<line x1="205" y1="156" x2="185" y2="180" stroke="#059669" stroke-width="3">
<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.4;0.46;1" dur="{DB2}s" repeatCount="indefinite"/></line>
<circle cx="205" cy="186" r="3.5" fill="#334155"/>
<text x="150" y="176" font-size="11" font-weight="bold" fill="#334155">开关 SW</text>
<line x1="205" y1="186" x2="205" y2="196" stroke="#334155" stroke-width="2.5"/>
{gnd_sym(205, 210)}
<line x1="48" y1="96" x2="48" y2="210" stroke="#334155" stroke-width="1.5" stroke-dasharray="4,3" opacity="0.4"/>
<line x1="48" y1="210" x2="320" y2="210" stroke="#334155" stroke-width="1.5" stroke-dasharray="4,3" opacity="0.4"/>
<text x="100" y="245" font-size="11" fill="#059669" opacity="0">电感储能 ½LI²
<animate attributeName="opacity" values="0;1;1;0;0" keyTimes="0;0.06;0.4;0.46;1" dur="{DB2}s" repeatCount="indefinite"/></text>
<text x="240" y="245" font-size="11" fill="#dc2626" opacity="0">Vin+L 叠加=24V 顶上去
<animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="0;0.52;0.56;0.9;0.96;1" dur="{DB2}s" repeatCount="indefinite"/></text>
'''
    svg += f'<g><animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.4;0.46;1" dur="{DB2}s" repeatCount="indefinite"/>'
    svg += flow("M52,92 H196 M205,110 V150 V196", DB2/3, n=6, color="#059669", r=5) + '</g>'
    svg += f'<g><animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="0;0.5;0.56;0.88;0.94;1" dur="{DB2}s" repeatCount="indefinite"/>'
    svg += flow("M52,92 H196 M214,92 H316 M320,100 V126", DB2/3, n=6, color="#dc2626", r=5) + '</g>'
    svg += f'''
<text x="440" y="252" font-size="11.5" font-weight="bold" fill="#7c3aed">开关节点（0 / 24V 方波）</text>
<path d="M430,300 V268 H483 V300 H537 V268 H590 V300 H644 V268 H697 V300 H750" fill="none" stroke="#7c3aed" stroke-width="2.8"/>
<text x="440" y="332" font-size="11.5" font-weight="bold" fill="#059669">电感电流（升降各半：D=0.5）</text>
<path d="{il_d}" fill="none" stroke="#059669" stroke-width="2.8"/>
<line x1="430" y1="392" x2="750" y2="392" stroke="#2563eb" stroke-width="2.8"/>
<text x="440" y="412" font-size="11.5" font-weight="bold" fill="#2563eb">输出 24V = 12V/(1−0.5)</text>
'''
    svg += caption("① 开关闭合：12V 全加在电感上，电流斜坡上升——能量存进磁场（输出靠电容撑）", "#059669", DB2,
                   "0;1;1;0;0", "0;0.03;0.2;0.26;1", y=460)
    svg += caption("② 开关断开：电感不许电流突变，极性翻转与 12V 串联叠加——顶开二极管向 24V 灌能", "#dc2626", DB2,
                   "0;0;1;1;0;0", "0;0.28;0.33;0.5;0.56;1", y=460)
    svg += caption("③ 伏秒平衡：Vin·D = (Vout−Vin)·(1−D) → Vout = Vin/(1−D)——D 越近 1 升得越高", "#7c3aed", DB2,
                   "0;0;1;1", "0;0.58;0.64;1", y=460)
    svg += note_box("升压的秘密 = 电感电压与输入「叠罗汉」；Buck 是电感在后级碾平，Boost 是电感在前级打气", 494, DB2, "0;0.7;0.75;1", w=730)
    save('boost-converter.svg', svg + '</svg>')


# ======================= 图 20：精密整流 =======================
def make_precision_rectifier():
    DP = 6
    sin_in = sine_path(430, 750, 120, 26, n=72)
    half_pts = []
    for i in range(73):
        u = i/72
        x = 430 + 320*u
        s = np.sin(u*4*np.pi)
        half_pts.append(f"{x:.0f},{280 - 40*max(0.0, s):.0f}")
    half_d = "M" + " L".join(half_pts)
    flat_d = f"M430,280 L750,280"
    svg = svg_open('精密整流：运放「借增益」消灭二极管压降', h=500)
    svg += f'''
<text x="210" y="52" text-anchor="middle" font-size="14" font-weight="bold" fill="#334155">精密半波整流器（反相型）</text>
<text x="16" y="145" font-size="11" fill="#475569">输入</text>
<text x="16" y="160" font-size="10" fill="#94a3b8">±100mV</text>
{resistor_h(60, 150, 40, 'R1')}
<circle cx="170" cy="150" r="4" fill="#334155"/>
<polygon points="200,120 200,180 260,150" fill="#f8fafc" stroke="#334155" stroke-width="2.5"/>
<text x="206" y="144" font-size="13" font-weight="bold" fill="#dc2626">−</text>
<text x="206" y="170" font-size="13" font-weight="bold" fill="#059669">+</text>
<line x1="170" y1="150" x2="200" y2="135" stroke="#334155" stroke-width="2"/>
<line x1="200" y1="165" x2="196" y2="190" stroke="#334155" stroke-width="2"/>
{gnd_sym(196, 204)}
<line x1="260" y1="150" x2="284" y2="150" stroke="#334155" stroke-width="2.5"/>
<polygon points="308,150 284,138 284,162" fill="none" stroke="#334155" stroke-width="2.5"/>
<line x1="308" y1="138" x2="308" y2="162" stroke="#334155" stroke-width="3"/>
<text x="272" y="132" font-size="10.5" fill="#dc2626">D</text>
<line x1="308" y1="150" x2="350" y2="150" stroke="#334155" stroke-width="2.5"/>
<circle cx="350" cy="150" r="4" fill="#334155"/>
<line x1="350" y1="150" x2="400" y2="150" stroke="#334155" stroke-width="2.5"/>
<text x="360" y="136" font-size="11" font-weight="bold" fill="#2563eb">输出</text>
{resistor_h(200, 210, 40, 'Rf')}
<line x1="120" y1="150" x2="170" y2="150" stroke="#334155" stroke-width="2.5"/>
<line x1="260" y1="210" x2="280" y2="210" stroke="#334155" stroke-width="2"/>
<line x1="170" y1="150" x2="170" y2="210" stroke="#334155" stroke-width="2"/>
<line x1="170" y1="210" x2="180" y2="210" stroke="#334155" stroke-width="2"/>
<line x1="280" y1="210" x2="350" y2="210" stroke="#334155" stroke-width="2"/>
<line x1="350" y1="210" x2="350" y2="150" stroke="#334155" stroke-width="2"/>
<text x="120" y="245" font-size="11" fill="#dc2626" opacity="0">运放输出自动多抬 0.7V
<animate attributeName="opacity" values="0;1;1;0;0" keyTimes="0;0.06;0.4;0.46;1" dur="{DP}s" repeatCount="indefinite"/></text>
'''
    svg += f'<g><animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.44;0.5;1" dur="{DP}s" repeatCount="indefinite"/>'
    svg += flow("M64,146 H160 M170,210 H200 M260,210 H346 V154 H396", DP/3, n=6, color="#059669", r=5) + '</g>'
    svg += f'''
<text x="590" y="66" text-anchor="middle" font-size="11.5" font-weight="bold" fill="#475569">输入 ±100mV（太小，普通整流全丢）</text>
<path d="{sin_in}" fill="none" stroke="#94a3b8" stroke-width="2"/>
<text x="590" y="200" text-anchor="middle" font-size="11.5" font-weight="bold" fill="#dc2626">普通二极管整流：0.7V 死区 → 输出=0</text>
<path d="{flat_d}" fill="none" stroke="#dc2626" stroke-width="2" stroke-dasharray="6,4"/>
<text x="590" y="416" text-anchor="middle" font-size="11.5" font-weight="bold" fill="#059669">精密整流输出：干净半波（基线=0V）</text>
<path d="{half_d}" fill="none" stroke="#059669" stroke-width="2.5" transform="translate(0,80)"/>
<line x1="430" y1="360" x2="750" y2="360" stroke="#64748b" stroke-width="1.2"/>
'''
    svg += caption("① 正半周：运放开环增益 10 万倍——输出只需多抬 0.7V，折算回输入仅 7µV 误差", "#059669", DP,
                   "0;1;1;0;0", "0;0.03;0.22;0.28;1", y=430)
    svg += caption("② 负半周：二极管截止、运放饱和也无妨——输出被 Rf 锚在 0", "#dc2626", DP,
                   "0;0;1;1;0;0", "0;0.3;0.35;0.58;0.64;1", y=430)
    svg += caption("③ 对比：普通二极管对 100mV 信号输出为零；精密整流分毫毕现——mV 级信号救星", "#2563eb", DP,
                   "0;0;1;1", "0;0.64;0.7;1", y=430)
    svg += note_box("0.7V ÷ 开环增益 = 等效死区 7µV——把非线性元件塞进反馈环，让增益替你买单", 474, DP, "0;0.74;0.79;1", w=680)
    save('precision-rectifier.svg', svg + '</svg>')


# ======================= 图 21：米勒效应 =======================
def make_miller_effect():
    DML = 6
    svg = svg_open('米勒效应：小电容被增益放大 (1+A) 倍', h=500)
    svg += f'''
<text x="220" y="52" text-anchor="middle" font-size="14" font-weight="bold" fill="#334155">跨接在增益级输入输出之间的电容 C</text>
<text x="20" y="145" font-size="11" fill="#475569">输入源</text>
{resistor_h(60, 150, 40, 'R_sig')}
<circle cx="190" cy="150" r="4" fill="#334155"/>
<text x="182" y="172" font-size="11" font-weight="bold" fill="#2563eb">IN</text>
<rect x="230" y="120" width="90" height="60" rx="6" fill="#f8fafc" stroke="#334155" stroke-width="2.5"/>
<text x="275" y="146" text-anchor="middle" font-size="13" font-weight="bold" fill="#334155">增益级</text>
<text x="275" y="166" text-anchor="middle" font-size="12" font-weight="bold" fill="#dc2626">−A = −100</text>
<line x1="190" y1="150" x2="230" y2="150" stroke="#334155" stroke-width="2.5"/>
<line x1="320" y1="150" x2="360" y2="150" stroke="#334155" stroke-width="2.5"/>
<circle cx="360" cy="150" r="4" fill="#334155"/>
<text x="352" y="172" font-size="11" font-weight="bold" fill="#dc2626">OUT</text>
<line x1="190" y1="150" x2="190" y2="90" stroke="#334155" stroke-width="2"/>
<line x1="190" y1="90" x2="216" y2="90" stroke="#334155" stroke-width="2"/>
<line x1="216" y1="76" x2="216" y2="104" stroke="#7c3aed" stroke-width="3"/>
<line x1="228" y1="76" x2="228" y2="104" stroke="#7c3aed" stroke-width="3"/>
<text x="238" y="82" font-size="11" font-weight="bold" fill="#7c3aed">C=10pF</text>
<line x1="228" y1="90" x2="360" y2="90" stroke="#334155" stroke-width="2"/>
<line x1="360" y1="90" x2="360" y2="150" stroke="#334155" stroke-width="2"/>
<text x="60" y="220" font-size="11" fill="#2563eb" opacity="0">IN 摆 1mV
<animate attributeName="opacity" values="0;1;1;0;0" keyTimes="0;0.06;0.4;0.46;1" dur="{DML}s" repeatCount="indefinite"/></text>
<text x="300" y="220" font-size="11" fill="#dc2626" opacity="0">OUT 反相摆 −100mV
<animate attributeName="opacity" values="0;1;1;0;0" keyTimes="0;0.06;0.4;0.46;1" dur="{DML}s" repeatCount="indefinite"/></text>
<text x="150" y="290" font-size="11.5" font-weight="bold" fill="#7c3aed" opacity="0">C 两端电压差摆了 101mV——充电电流是「预期」的 101 倍！
<animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="0;0.52;0.56;0.9;0.96;1" dur="{DML}s" repeatCount="indefinite"/></text>
<text x="60" y="330" font-size="12" fill="#334155" opacity="0">⇒ 从输入端看：等效电容 C_eff = (1+A)×C = 101×10pF ≈ <tspan font-weight="bold" fill="#dc2626">1nF</tspan>
<animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="0;0.56;0.6;0.92;0.98;1" dur="{DML}s" repeatCount="indefinite"/></text>
'''
    svg += f'''
<rect x="480" y="90" width="270" height="130" rx="8" fill="#f8fafc" stroke="#94a3b8" stroke-width="1.5" stroke-dasharray="5,4"/>
<text x="615" y="116" text-anchor="middle" font-size="12" font-weight="bold" fill="#334155">输入端看到的「等效世界」</text>
<line x1="500" y1="150" x2="560" y2="150" stroke="#334155" stroke-width="2.5"/>
<line x1="560" y1="150" x2="560" y2="170" stroke="#334155" stroke-width="2"/>
<line x1="546" y1="170" x2="574" y2="170" stroke="#7c3aed" stroke-width="3"/>
<line x1="546" y1="182" x2="574" y2="182" stroke="#7c3aed" stroke-width="3"/>
<line x1="560" y1="182" x2="560" y2="196" stroke="#334155" stroke-width="2"/>
<text x="586" y="180" font-size="11" font-weight="bold" fill="#dc2626">1nF 到地</text>
<text x="615" y="212" text-anchor="middle" font-size="10.5" fill="#475569">10pF 变身 1nF——高频信号全被它拖慢</text>
<text x="440" y="242" font-size="11" font-weight="bold" fill="#2563eb">IN：±1mV 小摆幅</text>
<path d="{sine_path(440, 740, 268, 7, n=64)}" fill="none" stroke="#2563eb" stroke-width="2.2"/>
<line x1="440" y1="268" x2="740" y2="268" stroke="#94a3b8" stroke-width="0.8" stroke-dasharray="3,3"/>
<text x="440" y="312" font-size="11" font-weight="bold" fill="#dc2626">OUT：∓100mV 大摆幅（反相）</text>
<path d="{sine_path(440, 740, 352, 38, n=64, phase=3.14159)}" fill="none" stroke="#dc2626" stroke-width="2.2"/>
<line x1="440" y1="352" x2="740" y2="352" stroke="#94a3b8" stroke-width="0.8" stroke-dasharray="3,3"/>
'''
    svg += caption("① IN 只摆 1mV，OUT 反相摆 −100mV——电容两端实际承受 101mV 的摆幅", "#2563eb", DML,
                   "0;1;1;0;0", "0;0.03;0.22;0.28;1", y=430)
    svg += caption("② 充同一份电荷，输入源要供 101 倍电流——仿佛对着 1nF 而不是 10pF", "#7c3aed", DML,
                   "0;0;1;1;0;0", "0;0.3;0.35;0.58;0.64;1", y=430)
    svg += caption("③ 坏事变好事：运放人为跨接小补偿电容——用米勒效应低成本获得大电容", "#059669", DML,
                   "0;0;1;1", "0;0.64;0.7;1", y=430)
    svg += note_box("C_eff=(1+A)·C：它是放大器高频滚降的元凶（C_bc 只有几 pF），也是密勒补偿的原理", 474, DML, "0;0.74;0.79;1", w=710)
    save('miller-effect.svg', svg + '</svg>')

if __name__ == '__main__':
    make_rc_charge()
    make_bridge_rectifier()
    make_bjt_amplify()
    make_mosfet_switch()
    make_opamp_inverting()
    make_comparator_hysteresis()
    make_ne555_astable()
    make_pushpull_opendrain()
    make_ldo_feedback()
    make_analog_switch()
    make_cap_decoupling()
    make_pcb_return_path()
    make_diff_pair()
    make_buck_converter()
    make_wien_bridge()
    make_class_b()
    make_sallen_key()
    make_current_mirror()
    make_boost_converter()
    make_precision_rectifier()
    make_miller_effect()
    print('all 21 SVGs regenerated into', os.path.abspath(OUT))

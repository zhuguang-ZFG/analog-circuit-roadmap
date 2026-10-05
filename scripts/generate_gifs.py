# -*- coding: utf-8 -*-
"""
generate_gifs.py — 一键再生成《通往模拟电路之路》全部 7 张演示 GIF
用法:  python generate_gifs.py            # 输出到 ../assets/
依赖:  matplotlib, numpy, pillow
"""
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation

plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei']  # Linux 可换 Noto Sans CJK
plt.rcParams['axes.unicode_minus'] = False

OUT = os.path.join(os.path.dirname(__file__), '..', 'assets')
os.makedirs(OUT, exist_ok=True)

# ---- 深色科技风模板 ----
BG, GRID, TXT, DIM = '#0d1117', '#21262d', '#c9d1d9', '#8b949e'
CYAN, ORANGE, GREEN, RED, PURPLE, YELLOW, BLUE = ('#39d0d8', '#ffa657', '#3fb950',
                                                  '#f85149', '#d2a8ff', '#e3b341', '#58a6ff')


def style_ax(ax, title=''):
    ax.set_facecolor(BG)
    for s in ax.spines.values():
        s.set_color(GRID)
    ax.tick_params(colors=DIM, labelsize=9)
    ax.xaxis.label.set_color(TXT)
    ax.yaxis.label.set_color(TXT)
    ax.grid(color=GRID, alpha=0.7, lw=0.7)
    if title:
        ax.set_title(title, color=TXT, fontsize=11, pad=8)


def glow_plot(ax, x, y, color, lw=2.2):
    """发光曲线: 粗半透明底层 + 细亮芯 + 移动光点"""
    lg, = ax.plot([], [], color=color, lw=lw * 3.2, alpha=0.25, solid_capstyle='round')
    lm, = ax.plot([], [], color=color, lw=lw * 1.8, alpha=0.5, solid_capstyle='round')
    lc, = ax.plot([], [], color=color, lw=lw, solid_capstyle='round')
    dot, = ax.plot([], [], 'o', color='white', ms=7, mec=color, mew=2)
    for ln in (lg, lm, lc, dot):
        ln._data = (x, y)
    return lg, lm, lc, dot


def glow_upd(lines, n):
    lg, lm, lc, dot = lines
    x, y = lc._data
    for ln in (lg, lm, lc):
        ln.set_data(x[:n], y[:n])
    if n > 0:
        dot.set_data([x[n - 1]], [y[n - 1]])


def new_fig(w=10, h=5):
    fig = plt.figure(figsize=(w, h))
    fig.patch.set_facecolor(BG)
    return fig


def save(ani, name, fps=25):
    path = os.path.join(OUT, name)
    ani.save(path, writer=animation.PillowWriter(fps=fps), dpi=95)
    plt.close('all')
    print('saved', name)


# ================= GIF 1: RC 充电 =================
def gif_rc_charging():
    fig = new_fig(10.5, 4.8)
    gs = fig.add_gridspec(1, 2, width_ratios=[1, 1.7], wspace=0.15)
    ax1, ax2 = fig.add_subplot(gs[0]), fig.add_subplot(gs[1])
    fig.suptitle('RC 一阶电路：电容充电的指数人生', color=TXT, fontsize=15, y=0.97)
    ax1.set_xlim(0, 10); ax1.set_ylim(0, 10); ax1.axis('off'); ax1.set_facecolor(BG)
    w2 = dict(color=DIM, lw=1.8)
    ax1.text(1.2, 9.2, '阶跃 0→5V', color=RED, fontsize=11, weight='bold')
    ax1.plot([1.6, 1.6], [7.6, 8.6], **w2); ax1.plot([1.6, 4.2], [8.6, 8.6], **w2)
    ax1.add_patch(plt.Rectangle((4.2, 8.1), 2.0, 1.0, fill=False, ec=DIM, lw=1.8))
    ax1.text(5.2, 9.5, 'R = 1 kΩ', color=YELLOW, fontsize=11, ha='center')
    ax1.plot([6.2, 7.4], [8.6, 8.6], **w2); ax1.plot([7.4, 7.4], [8.6, 5.4], **w2)
    ax1.plot([6.7, 8.1], [5.4, 5.4], color=DIM, lw=2.6); ax1.plot([6.7, 8.1], [4.9, 4.9], color=DIM, lw=2.6)
    ax1.text(8.5, 5.1, 'C = 10 µF', color=CYAN, fontsize=11)
    ax1.plot([7.4, 7.4], [4.9, 1.6], **w2)
    ax1.plot([6.6, 8.2], [1.6, 1.6], color=DIM, lw=2.4)
    ax1.plot([6.9, 7.9], [1.3, 1.3], color=DIM, lw=2.4); ax1.plot([7.2, 7.6], [1.0, 1.0], color=DIM, lw=2.4)
    ax1.text(5.2, 7.2, 'τ = RC = 10 ms', color=GREEN, fontsize=10.5, ha='center')
    arrow, = ax1.plot([], [], '>', color=YELLOW, ms=11)
    ax1.barh(3.6, 0, left=6.7, height=1.0, color=CYAN, alpha=0.55)
    vc_txt = ax1.text(0.6, 2.6, '', color=CYAN, fontsize=12, weight='bold')
    t = np.linspace(0, 0.05, 600); vc = 5 * (1 - np.exp(-t / 0.01))
    ax2.set_xlim(0, 50); ax2.set_ylim(0, 5.6)
    ax2.set_xlabel('时间 (ms)'); ax2.set_ylabel('v$_C$ (V)'); style_ax(ax2)
    ax2.axhline(5, ls=':', color=DIM, lw=1); ax2.text(48, 5.12, '5V', color=DIM, fontsize=9, ha='right')
    ax2.plot([10, 10], [0, 5 * 0.632], ls='--', color=ORANGE, lw=1.4)
    ax2.plot([0, 10], [5 * 0.632, 5 * 0.632], ls='--', color=ORANGE, lw=1.4)
    ax2.annotate('t = τ：充到 63.2%', xy=(10, 5 * 0.632), xytext=(14.5, 2.1),
                 color=ORANGE, fontsize=10.5, arrowprops=dict(arrowstyle='->', color=ORANGE))
    ax2.text(24, 4.35, '$v_C(t) = V_S\\,(1-e^{-t/\\tau})$', color=CYAN, fontsize=13)
    state = {'fill': None}
    ln1 = glow_plot(ax2, t * 1000, vc, CYAN)

    def upd(f):
        n = min(f * 6, 599)
        glow_upd(ln1, n)
        if state['fill'] is not None:
            state['fill'].remove()
        state['fill'] = ax2.fill_between(t[:n] * 1000, vc[:n], color=CYAN, alpha=0.10)
        ax1.patches[-1].remove()
        ax1.barh(3.6, 1.4 * (vc[n] / 5), left=6.7, height=1.0, color=CYAN, alpha=0.6)
        ax1.patches[-1].set_clip_on(False)
        pos = 1.6 + 5.8 * ((f * 0.06) % 1.0)
        arrow.set_data([min(pos, 7.4)], [8.6 if pos < 6.2 else 8.6 - 2 * (pos - 6.2)])
        arrow.set_alpha(max(0.15, float(np.exp(-t[n] / 0.01))))
        vc_txt.set_text(f't = {t[n]*1000:4.1f} ms   $v_C$ = {vc[n]:.2f} V')

    save(animation.FuncAnimation(fig, upd, frames=120, interval=40), 'rc_charging.gif')


# ================= GIF 2: 整流滤波 =================
def gif_rectifier():
    fig = new_fig(10.5, 7.6)
    gs = fig.add_gridspec(3, 1, hspace=0.32, left=0.08, right=0.97, top=0.90, bottom=0.08)
    fig.suptitle('桥式全波整流 + 电容滤波：交流如何变成直流', color=TXT, fontsize=15)
    axes = [fig.add_subplot(gs[i]) for i in range(3)]
    tt = np.linspace(0, 0.08, 1600)
    vin = 10 * np.sin(2 * np.pi * 50 * tt)
    vrect = np.clip(np.abs(vin) - 1.4, 0, None)
    vfilt = np.zeros_like(tt); cur = 0
    for i, x in enumerate(vrect):
        if x >= cur:
            cur = x
        else:
            cur *= np.exp(-(tt[1] - tt[0]) / 0.012)
        vfilt[i] = cur
    specs = [(vin, CYAN, '① 变压器次级：50 Hz 正弦交流'),
             (vrect, ORANGE, '② 桥式整流：负半周被"翻转"，损失 2×0.7V 管压降'),
             (vfilt, GREEN, '③ 电容滤波：峰值充电、谷值放电 → 纹波 ΔV ≈ I/(f·C)')]
    lines = []
    for ax, (sig, c, name) in zip(axes, specs):
        style_ax(ax); ax.set_xlim(0, 80); ax.set_ylim(-11.5, 11.5); ax.set_ylabel('V', color=TXT)
        ax.text(1.5, 9.2, name, color=c, fontsize=11, weight='bold')
        lines.append(glow_plot(ax, tt * 1000, sig, c))
    axes[2].set_xlabel('时间 (ms)')
    axes[2].text(46, 5.4, '纹波峰峰值 ΔV', color=YELLOW, fontsize=10)
    ripple, = axes[2].plot([], [], color=YELLOW, lw=2)

    def upd(f):
        n = min(f * 14, 1599)
        for ln in lines:
            glow_upd(ln, n)
        if n > 800:
            ripple.set_data(tt[n - 160:n] * 1000, vfilt[n - 160:n])

    save(animation.FuncAnimation(fig, upd, frames=125, interval=40), 'rectifier_filter.gif')


# ================= GIF 3: 共射放大失真 =================
def gif_ce_amp():
    fig = new_fig(10.5, 7.4)
    gs = fig.add_gridspec(2, 1, height_ratios=[1, 1.9], hspace=0.25,
                          left=0.08, right=0.97, top=0.88, bottom=0.09)
    fig.suptitle('共射放大器：Q 点决定命运', color=TXT, fontsize=15)
    axa, axb = fig.add_subplot(gs[0]), fig.add_subplot(gs[1])
    tt = np.linspace(0, 0.04, 1200)
    vin = 0.02 * np.sin(2 * np.pi * 100 * tt)
    vok = 6 - 2.0 * np.sin(2 * np.pi * 100 * tt)
    vbad = np.clip(6 - 10.6 * np.sin(2 * np.pi * 100 * tt), 0.2, 11.8)
    style_ax(axa); axa.set_xlim(0, 40); axa.set_ylim(-0.055, 0.055)
    axa.set_ylabel('v$_{in}$ (V)', color=TXT)
    axa.text(1, 0.036, '基极输入：20 mV 正弦', color=BLUE, fontsize=11, weight='bold')
    style_ax(axb); axb.set_xlim(0, 40); axb.set_ylim(-1.2, 13.2)
    axb.set_ylabel('v$_{CE}$ (V)', color=TXT); axb.set_xlabel('时间 (ms)')
    axb.axhline(6, ls=':', color=DIM, lw=1.2)
    axb.text(0.8, 6.35, 'Q 点 = Vcc/2 = 6V（摆幅最大化）', color=DIM, fontsize=10)
    axb.axhline(12, ls=':', color=RED, lw=1.2); axb.axhline(0.2, ls=':', color=RED, lw=1.2)
    axb.text(27.5, 12.1, '截止区：晶体管关断 → 削顶', color=RED, fontsize=10)
    axb.text(27.5, -1.0, '饱和区：V$_{CE(sat)}$≈0.2V → 削底', color=RED, fontsize=10)
    ln_in = glow_plot(axa, tt * 1000, vin, BLUE)
    ln_ok = glow_plot(axb, tt * 1000, vok, GREEN)
    ln_bad = glow_plot(axb, tt * 1000, vbad, RED)
    axb.text(1, 10.9, '● 合适 Q 点：反相放大 ×100，波形完好', color=GREEN, fontsize=11, weight='bold')
    axb.text(1, 9.3, '● 输入过大/Q 点偏移：截止+饱和双重削波失真', color=RED, fontsize=11, weight='bold')

    def upd(f):
        n = min(f * 11, 1199)
        glow_upd(ln_in, n); glow_upd(ln_ok, n); glow_upd(ln_bad, n)

    save(animation.FuncAnimation(fig, upd, frames=115, interval=40), 'ce_amplifier_distortion.gif')


# ================= GIF 4: 比较器迟滞 =================
def gif_hysteresis():
    fig = new_fig(10.5, 8.2)
    gs = fig.add_gridspec(3, 1, hspace=0.30, left=0.08, right=0.97, top=0.90, bottom=0.08)
    fig.suptitle('比较器为什么需要迟滞？—— 噪声下的抖动 vs 施密特触发器', color=TXT, fontsize=14)
    axes = [fig.add_subplot(gs[i]) for i in range(3)]
    tt = np.linspace(0, 10, 2000)
    rng = np.random.default_rng(7)
    vsig = 2.5 + 2.3 * np.sin(2 * np.pi * 0.25 * tt) + 0.25 * rng.standard_normal(len(tt))
    VH, VL = 3.0, 2.0
    out_plain = (vsig > 2.5).astype(float) * 5
    out_sch = np.zeros(len(tt)); st = 0
    for i, x in enumerate(vsig):
        if st == 0 and x > VH:
            st = 1
        elif st == 1 and x < VL:
            st = 0
        out_sch[i] = st * 5
    style_ax(axes[0]); axes[0].set_xlim(0, 10); axes[0].set_ylim(-0.4, 5.6)
    axes[0].set_ylabel('输入 (V)', color=TXT)
    axes[0].axhline(2.5, ls='--', color=RED, lw=1.2)
    axes[0].text(8.55, 2.56, '单阈值 2.5V', color=RED, fontsize=9.5)
    axes[0].axhline(VH, ls=':', color=GREEN, lw=1.2); axes[0].axhline(VL, ls=':', color=GREEN, lw=1.2)
    axes[0].text(8.62, 3.12, 'V$_{TH+}$ = 3V', color=GREEN, fontsize=9.5)
    axes[0].text(8.62, 1.35, 'V$_{TH-}$ = 2V', color=GREEN, fontsize=9.5)
    axes[0].text(0.15, 4.9, '带噪声的慢变输入信号', color=CYAN, fontsize=11, weight='bold')
    l_sig = glow_plot(axes[0], tt, vsig, CYAN, lw=1.6)
    for ax, name, c in [(axes[1], '① 无迟滞：阈值附近噪声 → 输出疯狂抖动（误触发中断！）', RED),
                        (axes[2], '② 施密特触发器：双阈值迟滞 → 输出干净利落', GREEN)]:
        style_ax(ax); ax.set_ylim(-0.9, 6.0)
        ax.set_yticks([0, 5]); ax.set_yticklabels(['0V', '5V'])
        ax.text(0.15, 4.6, name, color=c, fontsize=10.5, weight='bold')
    axes[2].set_xlabel('时间 (s)')
    l_p = glow_plot(axes[1], tt, out_plain, RED, lw=1.6)
    l_s = glow_plot(axes[2], tt, out_sch, GREEN, lw=1.6)

    def upd(f):
        n = min(f * 17, 1999)
        glow_upd(l_sig, n); glow_upd(l_p, n); glow_upd(l_s, n)

    save(animation.FuncAnimation(fig, upd, frames=125, interval=40), 'comparator_hysteresis.gif')


# ================= GIF 5: 推挽 vs 开漏 =================
def gif_pushpull_opendrain():
    fig = new_fig(11, 6.8)
    gs = fig.add_gridspec(1, 2, wspace=0.18, left=0.06, right=0.98, top=0.86, bottom=0.10)
    fig.suptitle('推挽 vs 开漏：为什么开漏的上升沿"慢吞吞"？', color=TXT, fontsize=15)
    axL, axR = fig.add_subplot(gs[0]), fig.add_subplot(gs[1])
    for ax, name in [(axL, '推挽 Push-Pull：两个方向都主动驱动'),
                     (axR, '开漏 Open-Drain：只能拉低，靠上拉电阻回高')]:
        style_ax(ax); ax.set_xlim(0, 10); ax.set_ylim(0, 5.4)
        ax.set_ylabel('V$_{OUT}$', color=TXT)
        ax.set_title(name, color=TXT, fontsize=11.5, pad=10)
        ax.set_xticks([])
    tc = np.linspace(0, 10, 1000)
    sq = ((tc % 4) < 2).astype(float)
    v_push = 5 * sq.astype(float)
    v_od = np.zeros_like(tc); cur = 0
    for i, s in enumerate(sq):
        if s == 0:
            cur = 0
        else:
            cur = 5 - (5 - cur) * np.exp(-(tc[1] - tc[0]) / 0.35)
        v_od[i] = cur
    ln_pp = glow_plot(axL, tc, v_push, GREEN)
    ln_od = glow_plot(axR, tc, v_od, ORANGE)
    axL.text(5, 5.15, '上升沿：上管主动推 → 快、驱动强', color=GREEN, fontsize=10, ha='center')
    axR.text(5, 5.15, '上升沿：上拉电阻对总线电容充电 → RC 缓升', color=ORANGE, fontsize=10, ha='center')
    axL.annotate('陡', xy=(2.02, 2.5), xytext=(1.0, 3.6), color=CYAN, fontsize=11,
                 arrowprops=dict(arrowstyle='->', color=CYAN))
    axR.annotate('缓（RC 充电曲线）', xy=(2.6, 3.4), xytext=(3.2, 1.2), color=CYAN, fontsize=11,
                 arrowprops=dict(arrowstyle='->', color=CYAN))
    axR.text(5, 0.5, '↑ 上拉越小越快但越耗电\nI2C 常用 2.2~4.7kΩ', color=YELLOW, fontsize=10, ha='center')

    def upd(f):
        n = min(f * 9, 999)
        glow_upd(ln_pp, n); glow_upd(ln_od, n)

    save(animation.FuncAnimation(fig, upd, frames=118, interval=40), 'pushpull_vs_opendrain.gif')


# ================= GIF 6: 555 无稳态振荡 =================
def gif_555():
    fig = new_fig(10.5, 7.2)
    gs = fig.add_gridspec(2, 1, hspace=0.28, left=0.08, right=0.97, top=0.87, bottom=0.09)
    fig.suptitle('555 无稳态振荡器：电容在 1/3 与 2/3 Vcc 之间"荡秋千"', color=TXT, fontsize=15)
    axc, axq = fig.add_subplot(gs[0]), fig.add_subplot(gs[1])
    VCC = 9.0
    T1, T2 = 0.693 * 20e3 * 10e-6, 0.693 * 10e3 * 10e-6
    tt = np.linspace(0, (T1 + T2) * 3.2, 2000)
    vcap = np.zeros_like(tt); vq = np.zeros_like(tt)
    cur = VCC / 3; tprev = 0; charging = True
    for i, tnow in enumerate(tt):
        dt = tnow - tprev; tprev = tnow
        if charging:
            cur = VCC - (VCC - cur) * np.exp(-dt / T1)
            if cur >= 2 * VCC / 3:
                charging = False
        else:
            cur = VCC / 3 + (cur - VCC / 3) * np.exp(-dt / T2)
            if cur <= VCC / 3:
                charging = True
        vcap[i] = cur
        vq[i] = VCC if charging else 0.3
    style_ax(axc); axc.set_xlim(0, tt[-1] * 1000); axc.set_ylim(0, 9.9)
    axc.set_ylabel('C 电压 (V)', color=TXT)
    axc.axhline(VCC / 3, ls='--', color=PURPLE, lw=1.2)
    axc.axhline(2 * VCC / 3, ls='--', color=PURPLE, lw=1.2)
    axc.text(6.5, 3.35, '1/3 Vcc = 3V（触发阈值 TRIG）', color=PURPLE, fontsize=9.5)
    axc.text(6.5, 6.35, '2/3 Vcc = 6V（阈值 THRES）', color=PURPLE, fontsize=9.5)
    axc.text(0.4, 8.9, '① 电容经 R1+R2 充电 → 触及 2/3 Vcc 翻转', color=CYAN, fontsize=10.5)
    axc.text(0.4, 8.0, '② 电容经 R2 对地放电 → 跌至 1/3 Vcc 翻转', color=ORANGE, fontsize=10.5)
    ln_c = glow_plot(axc, tt * 1000, vcap, CYAN)
    style_ax(axq); axq.set_xlim(0, tt[-1] * 1000); axq.set_ylim(-1, 10.4)
    axq.set_ylabel('OUT (V)', color=TXT); axq.set_xlabel('时间 (ms)')
    axq.text(0.4, 9.2, '输出方波：充电期=高，放电期=低  f = 1.44/((R1+2R2)C)', color=GREEN, fontsize=10.5)
    ln_q = glow_plot(axq, tt * 1000, vq, GREEN)

    def upd(f):
        n = min(f * 16, 1999)
        glow_upd(ln_c, n); glow_upd(ln_q, n)

    save(animation.FuncAnimation(fig, upd, frames=128, interval=40), '555_astable.gif')


# ================= GIF 7: PCB 回流路径 =================
def gif_pcb_return_path():
    fig = new_fig(11, 7.2)
    gs = fig.add_gridspec(2, 1, hspace=0.42, left=0.05, right=0.97, top=0.88, bottom=0.07)
    fig.suptitle('PCB 黄金法则：回流电流永远贴着信号线走最小环路 —— 别在地平面开槽！',
                 color=TXT, fontsize=14)
    axT, axB = fig.add_subplot(gs[0]), fig.add_subplot(gs[1])
    for ax, name in [(axT, '① 完整地平面：回流紧贴信号正下方，环路面积≈0，EMI 最小'),
                     (axB, '② 地平面开槽：回流被迫绕到槽尽头，环路面积巨大 → 天线！EMI 暴增')]:
        ax.set_facecolor(BG); ax.set_xlim(0, 20); ax.set_ylim(0, 6); ax.axis('off')
        ax.set_title(name, color=TXT, fontsize=11.5, loc='left', pad=6)

    def draw_pcb(ax, slot=False):
        if slot:
            ax.add_patch(plt.Rectangle((0.5, 0.4), 8.5, 2.0, fc='#123a2a', ec=GREEN, lw=1.2))
            ax.add_patch(plt.Rectangle((11, 0.4), 8.5, 2.0, fc='#123a2a', ec=GREEN, lw=1.2))
            ax.add_patch(plt.Rectangle((9, 0.4), 2, 2.0, fc=BG, ec=RED, lw=1.6, ls='--'))
            ax.text(10, 2.9, '槽（地层断裂）', color=RED, fontsize=10, ha='center')
        else:
            ax.add_patch(plt.Rectangle((0.5, 0.4), 19, 2.0, fc='#123a2a', ec=GREEN, lw=1.2))
        ax.text(0.7, 1.2, 'GND 平面（内层）', color=GREEN, fontsize=9)
        ax.plot([0.5, 19.5], [4.4, 4.4], color=CYAN, lw=3.5, solid_capstyle='round')
        ax.text(0.7, 4.7, '信号线（顶层）', color=CYAN, fontsize=9)
        ax.text(0.6, 5.2, '源', color=TXT, fontsize=10)
        ax.text(19.0, 5.2, '负载', color=TXT, fontsize=10)

    draw_pcb(axT); draw_pcb(axB, slot=True)
    N = 7
    sig_T, = axT.plot([], [], 'o', color=CYAN, ms=8, mec='white')
    sig_B, = axB.plot([], [], 'o', color=CYAN, ms=8, mec='white')
    ret_T, = axT.plot([], [], 'o', color=ORANGE, ms=8, mec='white')
    ret_B, = axB.plot([], [], 'o', color=ORANGE, ms=8, mec='white')

    def slot_ret_xy(u):
        pts = [(19.5, 1.4), (11.6, 1.4), (11.6, 0.15), (8.4, 0.15), (8.4, 1.4), (0.5, 1.4)]
        segs = []
        total = 0
        for a, b in zip(pts[:-1], pts[1:]):
            L = float(np.hypot(b[0] - a[0], b[1] - a[1]))
            segs.append((a, b, L)); total += L
        d = u * total
        for a, b, L in segs:
            if d <= L:
                r = d / L if L > 0 else 0
                return a[0] + (b[0] - a[0]) * r, a[1] + (b[1] - a[1]) * r
            d -= L
        return pts[-1]

    axT.add_patch(plt.Rectangle((2, 1.4), 16, 3.0, fc=GREEN, alpha=0.08, ec=GREEN, lw=1.2, ls=':'))
    axT.text(10, 2.6, '环路面积≈0', color=GREEN, fontsize=10.5, ha='center', weight='bold')
    axB.add_patch(plt.Rectangle((8.4, 0.15), 3.2, 4.25, fc=RED, alpha=0.13, ec=RED, lw=1.5, ls=':'))
    axB.text(10, 4.9, '环路面积 = 天线', color=RED, fontsize=10.5, ha='center', weight='bold')
    axT.text(10, 5.6, '信号 →', color=CYAN, fontsize=9, ha='center')
    axB.text(10, 5.6, '回流 ← 绕远路', color=ORANGE, fontsize=9, ha='center')

    def upd(f):
        t7 = (f * 0.02) % 1.0
        sig_T.set_data(0.5 + 19 * ((np.arange(N) / N + t7) % 1.0), [4.4] * N)
        sig_B.set_data(0.5 + 19 * ((np.arange(N) / N + t7) % 1.0), [4.4] * N)
        ret_T.set_data(19.5 - 19 * ((np.arange(N) / N + t7) % 1.0), [1.4] * N)
        xyB = np.array([slot_ret_xy((i / N + t7) % 1.0) for i in range(N)])
        ret_B.set_data(xyB[:, 0], xyB[:, 1])

    save(animation.FuncAnimation(fig, upd, frames=130, interval=45), 'pcb_return_path.gif', fps=22)


if __name__ == '__main__':
    gif_rc_charging()
    gif_rectifier()
    gif_ce_amp()
    gif_hysteresis()
    gif_pushpull_opendrain()
    gif_555()
    gif_pcb_return_path()
    print('all GIFs regenerated into', os.path.abspath(OUT))

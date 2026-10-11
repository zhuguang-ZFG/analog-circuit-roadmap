#!/usr/bin/env python3
"""「自动导演」：把分镜表渲染成定时切换的导播页，直录成竖屏草片。

record_clip.py 解决的是「单镜头素材」（裸动画循环）；本脚本往上走一层——
按分镜表把 **标题卡 → 动画 → 数字卡 → 口诀卡 → 结尾卡** 串成一条完整的
竖屏草片（抖音 720x1280）。卡片沿用站点视觉语言：品牌靛蓝渐变 + 蓝图点阵 +
大字白字；动画以**内联 SVG**嵌进页面（SMIL 在页面上下文正常播放，
也避免了 file:// 子资源限制）。

用法：
    python video/director.py --demo ep04        # 内置 EP04《分压器带载》抖音草片
    python video/director.py --shots my.json    # 自定义分镜表，结构见 SHOTS_DOC

产出 video/samples/<name>-draft.webm。草片 = 节拍与字幕的核对基准 +
可以直接配音的底版；正式成片建议在剪映里用草片对轨后重排。
"""
from __future__ import annotations

import argparse
import json
import re
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SVG_DIR = ROOT / "assets" / "svg"
OUT_DIR = Path(__file__).resolve().parent / "samples"

W, H = 720, 1280

SHOTS_DOC = {
    "name": "输出文件名前缀",
    "shots": [
        {"type": "card", "seconds": 3, "eyebrow": "模拟电路动画课",
         "lines": ["接上负载那一刻", "5V 就没了"],
         "sub": "EP04 · 分压器带载"},
        {"type": "svg", "seconds": 12, "file": "divider-loading",
         "caption": "分压公式只在空载成立"},
        {"type": "num", "seconds": 4, "from": 5.0, "to": 3.3, "unit": "V",
         "sub": "R2∥RL = 5k · 塌了 33%", "bar": [1.0, 0.67]},
        {"type": "card", "seconds": 4,
         "lines": ["带载能力 ≈ **R1∥R2**"], "sub": "口诀"},
    ],
}
# lines 里用 **文字** 标重点（渲染成琥珀色大字）；num 镜头自动做
# 「从 from 数到 to」的计数动画，bar=[起,止] 画一根塌陷比例条。

EP04 = {
    "name": "ep04-divider",
    "shots": [
        {"type": "card", "seconds": 3, "eyebrow": "模拟电路动画课 · EP04",
         "lines": ["接上负载那一刻", "**5V 就没了**"]},
        {"type": "svg", "seconds": 13, "file": "divider-loading",
         "caption": "分压公式只在空载成立"},
        {"type": "num", "seconds": 4.5, "from": 5.0, "to": 3.3, "unit": "V",
         "sub": "R2∥RL = 5k · 塌了 **33%**", "bar": [1.0, 0.67]},
        {"type": "card", "seconds": 4.5,
         "lines": ["带载能力 ≈ **R1∥R2**"], "sub": "口诀"},
        {"type": "card", "seconds": 5,
         "lines": ["三条活路"],
         "sub": "负载阻抗 ≫ R2 · R1/R2 取小 · 后面跟一级运放缓冲"},
        {"type": "card", "seconds": 4.5,
         "lines": ["下一集", "你看到的怪波形", "可能是探头画的"],
         "sub": "合集：模拟电路动画课 · 全书开源免费",
         "cta": "关注 · 看下一集"},
    ],
}

PAGE = """<!DOCTYPE html>
<html lang="zh"><head><meta charset="utf-8">
<style>
  html,body {{ margin:0; width:{w}px; height:{h}px; overflow:hidden;
    font-family:"Microsoft YaHei",system-ui,sans-serif;
    background:#141c38; }}
  /* ---- 方向适配：横屏（B 站）字号整体上浮，SVG 舞台留边更多 ---- */
  body {{ --fs-line:72px; --fs-num:120px; --fs-sub:30px; --fs-eyebrow:26px;
         --fs-arrow:72px; --fs-caption:34px; }}
  body.h {{ --fs-line:92px; --fs-num:170px; --fs-sub:38px; --fs-eyebrow:30px;
          --fs-arrow:96px; --fs-caption:42px; }}
  /* ---- 幕容器与过渡：切幕 = 淡入 + 轻微缩放（1.04 → 1.0） ---- */
  .shot {{ position:fixed; inset:0; display:none; }}
  .shot.active {{ display:flex; animation:shotIn .5s cubic-bezier(.22,.9,.3,1) both; }}
  @keyframes shotIn {{ from {{ opacity:0; transform:scale(1.045); }}
                      to   {{ opacity:1; transform:scale(1); }} }}
  /* ---- 背景：靛蓝渐变 + 点阵缓慢漂移 + 底部晕影，静止画面永不死板 ---- */
  .bg {{ position:absolute; inset:0;
    background:
      radial-gradient(120% 90% at 100% 0%, rgba(94,122,255,.30), transparent 55%),
      linear-gradient(165deg,#1b2447 0%,#27357a 100%); }}
  .bg::before {{ content:""; position:absolute; inset:-40px;
    background-image:radial-gradient(rgba(255,255,255,.13) 1px, transparent 1.2px);
    background-size:18px 18px;
    -webkit-mask-image:linear-gradient(180deg,#000,transparent 85%);
    mask-image:linear-gradient(180deg,#000,transparent 85%);
    animation:drift 26s linear infinite; }}
  @keyframes drift {{ from {{ transform:translate(0,0); }} to {{ transform:translate(-18px,-18px); }} }}
  .bg::after {{ content:""; position:absolute; inset:0;
    background:radial-gradient(140% 110% at 50% 50%, transparent 60%, rgba(8,12,28,.5) 100%); }}
  /* ---- 文字入场：逐行错峰上滑；首行带强调色下划扫过 ---- */
  .card {{ flex-direction:column; justify-content:center; align-items:center;
    text-align:center; padding:60px; }}
  .stack {{ position:relative; display:flex; flex-direction:column;
    align-items:center; gap:30px;
    animation:floaty 7s ease-in-out infinite alternate; }}
  @keyframes floaty {{ from {{ transform:translateY(-7px); }}
                      to   {{ transform:translateY(7px); }} }}
  .bgart {{ position:absolute; inset:0; opacity:.22;
    filter:saturate(.8) blur(0.6px);
    animation:kenburns var(--dur,8s) ease-in-out infinite alternate; }}
  .bgart svg {{ width:100%; height:100%; }}
  .card .eyebrow {{ position:relative; color:#8fa5ff; font-size:var(--fs-eyebrow,26px); font-weight:700;
    letter-spacing:.35em; text-indent:.35em; animation:rise .55s .05s both; }}
  .card .lines {{ position:relative; }}
  .card .lines div {{ color:#fff; font-weight:800; line-height:1.32;
    font-size:var(--fs-line,72px); letter-spacing:.01em;
    text-shadow:0 6px 30px rgba(10,16,40,.55);
    animation:rise .6s both; }}
  .card .lines div:nth-child(2) {{ animation-delay:.14s; }}
  .card .lines div:nth-child(3) {{ animation-delay:.28s; }}
  .card .lines .hl {{ color:#ffc247; }}
  @keyframes rise {{ from {{ opacity:0; transform:translateY(46px); }}
                    to   {{ opacity:1; transform:translateY(0); }} }}
  .card .sub {{ position:relative; color:#aab7e8; font-size:var(--fs-sub,30px); line-height:1.75; max-width:86%;
    animation:rise .6s .42s both; }}
  .card .rule {{ position:relative; width:0; height:6px; border-radius:3px;
    background:linear-gradient(90deg,#5e7aff,#ffc247);
    animation:sweep .7s .3s cubic-bezier(.22,.9,.3,1) forwards; }}
  @keyframes sweep {{ to {{ width:220px; }} }}
  /* ---- 数字卡：计数跳字 + 塌陷条 ---- */
  .numrow {{ position:relative; display:flex; align-items:baseline; gap:26px;
    animation:rise .6s both; }}
  .numrow .n {{ font-size:var(--fs-num,120px); font-weight:800; color:#fff;
    font-variant-numeric:tabular-nums; text-shadow:0 8px 34px rgba(10,16,40,.6); }}
  .numrow .unit {{ font-size:calc(var(--fs-num,120px) * .42); color:#aab7e8; }}
  .numrow .n.bad {{ color:#ff8f6b; }}
  .numrow .arrow {{ font-size:var(--fs-arrow,72px); color:#ffc247; font-weight:800; }}
  .bar {{ position:relative; width:420px; height:26px; border-radius:13px;
    background:rgba(255,255,255,.14); overflow:hidden;
    animation:rise .6s .35s both; }}
  .bar i {{ position:absolute; inset:0; width:100%;
    background:linear-gradient(90deg,#5e7aff,#ff8f6b);
    border-radius:13px;
    animation:barShrink 1.5s .4s cubic-bezier(.25,.8,.3,1) forwards,
              barGlow 2.6s 2s ease-in-out infinite; }}
  @keyframes barShrink {{ from {{ transform:scaleX(1); }} to {{ transform:scaleX(var(--end,.67)); }} }}
  @keyframes barGlow {{ 0%,100% {{ box-shadow:0 0 0 rgba(255,143,107,0); }}
                        50% {{ box-shadow:0 0 26px rgba(255,143,107,.55); }} }}
  .numrow .n.bad {{ text-shadow:0 8px 34px rgba(10,16,40,.6); }}
  .count {{ animation:countGlow 2.6s 1.9s ease-in-out infinite; }}
  @keyframes countGlow {{ 0%,100% {{ text-shadow:0 8px 34px rgba(10,16,40,.6); }}
                          50% {{ text-shadow:0 0 30px rgba(255,143,107,.65); }} }}
  /* ---- SVG 幕：舞台缩放入场 + 字幕条上滑 ---- */
  .svgshot {{ flex-direction:column; background:#eef1f9; }}
  .svgshot .stage {{ flex:1; display:flex; align-items:center; justify-content:center;
    width:100%; animation:stageIn .6s cubic-bezier(.22,.9,.3,1) both; }}
  @keyframes stageIn {{ from {{ opacity:0; transform:scale(.965); }}
                       to   {{ opacity:1; transform:scale(1); }} }}
  .svgshot svg {{ width:94%; height:auto; border-radius:14px;
    box-shadow:0 12px 38px rgba(23,32,64,.20);
    animation:kenburns var(--dur,12s) ease-in-out infinite alternate; }}
  @keyframes kenburns {{ from {{ transform:scale(1); }}
                         to {{ transform:scale(1.045); }} }}
  .svgshot .caption {{ height:110px; display:flex; align-items:center; justify-content:center;
    width:100%; background:#1b2447; color:#fff; font-size:34px; font-weight:700;
    animation:capUp .5s .25s cubic-bezier(.22,.9,.3,1) both; }}
  body.h .svgshot {{ flex-direction:row; }}
  body.h .svgshot .stage {{ flex:1.45; padding:44px; }}
  body.h .svgshot .caption {{ width:32%; height:auto; flex-direction:column;
    justify-content:center; gap:18px; padding:0 40px;
    animation:rise .6s .25s both; }}
  body.h .svgshot .caption::before {{ content:"🎬"; font-size:44px; }}
  @keyframes capUp {{ from {{ transform:translateY(100%); }} to {{ transform:translateY(0); }} }}
  /* ---- 结尾卡：关注脉动 ---- */
  .card .cta {{ position:relative; margin-top:6px; padding:.5rem 1.6rem;
    border:2px solid #ffc247; border-radius:999px; color:#ffc247;
    font-size:30px; font-weight:800; animation:pulse 2s ease-in-out infinite; }}
  @keyframes pulse {{ 0%,100% {{ transform:scale(1); opacity:1; }}
                      50% {{ transform:scale(1.05); opacity:.82; }} }}
  /* ---- 每幕底部节奏条：进度即时长的体感 ---- */
  .shot .beat {{ position:absolute; left:0; bottom:0; height:8px; width:100%;
    background:linear-gradient(90deg,#5e7aff,#ffc247);
    transform-origin:left center; transform:scaleX(0); }}
  .shot.active .beat {{ animation:beat var(--dur,4s) linear forwards; }}
  @keyframes beat {{ from {{ transform:scaleX(0); }} to {{ transform:scaleX(1); }} }}
</style></head>
<body class="{cls}">
{shots}
<script>
  const durs = {durs};
  const shots = document.querySelectorAll('.shot');
  let i = 0;
  function show() {{
    shots.forEach((s, k) => s.classList.toggle('active', k === i));
    runCounts(shots[i]);
    /* 第 i 幕停留 durs[i]——写 durs[i-1] 会整体错一拍：
       首幕 0ms 直接跳过、每幕都播上一幕的时长（实测踩过）。 */
    if (i + 1 < shots.length) setTimeout(() => {{ i += 1; show(); }}, durs[i]);
  }}
  /* 数字卡：激活瞬间从 from 跳数到 to（ease-out，1.5s）——
     跳数的「动」是短视频数字表达的底线，静态两个数没有冲击力 */
  function runCounts(shot) {{
    shot.querySelectorAll('.count').forEach(el => {{
      const from = parseFloat(el.dataset.from), to = parseFloat(el.dataset.to);
      const dec = parseInt(el.dataset.dec || '1', 10);
      const t0 = performance.now(), D = 1500;
      function tick(t) {{
        const p = Math.min((t - t0) / D, 1);
        const e = 1 - Math.pow(1 - p, 3);
        el.textContent = (from + (to - from) * e).toFixed(dec);
        if (p < 1) requestAnimationFrame(tick);
      }}
      requestAnimationFrame(tick);
    }});
  }}
  show();
</script>
</body></html>"""


def hl(text: str) -> str:
    """lines 里的 **文字** → 琥珀色强调（`*` 先转义防误吞）。"""
    text = text.replace("*", "&#42;")
    return re.sub(r"&#42;&#42;(.+?)&#42;&#42;", r'<span class="hl">\1</span>', text)


def build_html(storyboard: dict, w: int = W, h: int = H, cls: str = "v") -> str:
    shots_html, durs = [], []
    for s in storyboard["shots"]:
        dur = s["seconds"]
        durs.append(int(dur * 1000))
        beat = f'<div class="beat" style="--dur:{dur}s"></div>'
        if s["type"] == "card":
            eyebrow = (f'<div class="eyebrow">{s["eyebrow"]}</div>' if s.get("eyebrow") else "")
            bgart = ""
            if s.get("bgSvg"):
                art = (SVG_DIR / (s["bgSvg"] + ".svg")).read_text(encoding="utf-8")
                bgart = f'<div class="bgart">{art}</div>'
            lines = "".join(f"<div>{hl(ln)}</div>" for ln in s["lines"])
            cta = f'<div class="cta">{s["cta"]}</div>' if s.get("cta") else ""
            inner = (f"{eyebrow}<div class=\"lines\">{lines}</div>"
                     f'<div class="rule"></div><div class="sub">{s.get("sub", "")}</div>'
                     f"{cta}")
            shots_html.append(
                f'<div class="shot card" style="--dur:{dur}s"><div class="bg"></div>'
                f'{bgart}<div class="stack">{inner}</div>{beat}</div>')
        elif s["type"] == "num":
            dec = s.get("dec", 1)
            bar = s.get("bar")
            bar_html = ""
            if bar:
                pct = bar[1] / bar[0] * 100 if bar[0] else 100
                bar_html = (f'<div class="bar"><i style="'
                            f"animation-duration:{dur}s;--end:{pct / 100:.2f}\"></i></div>")
            shots_html.append(
                f'<div class="shot card" style="--dur:{dur}s"><div class="bg"></div>'
                f'<div class="numrow"><span class="n" data-static="{s["from"]:.{dec}f}">'
                f'{s["from"]:.{dec}f}</span><span class="n unit">{s["unit"]}</span>'
                f'<span class="arrow">→</span>'
                f'<span class="n bad count" data-from="{s["from"]}" data-to="{s["to"]}" '
                f'data-dec="{dec}">{s["from"]:.{dec}f}</span>'
                f'<span class="n bad unit">{s["unit"]}</span></div>'
                f'{bar_html}<div class="sub">{hl(s.get("sub", ""))}</div>{beat}</div>')
        elif s["type"] == "svg":
            svg = (SVG_DIR / (s["file"] + ".svg")).read_text(encoding="utf-8")
            caption = f'<div class="caption">{s.get("caption", "")}</div>'
            shots_html.append(
                f'<div class="shot svgshot" style="--dur:{dur}s">'
                f'<div class="stage">{svg}</div>{caption}{beat}</div>')
        else:
            raise SystemExit(f"未知镜头类型：{s['type']}")
    total = sum(s["seconds"] for s in storyboard["shots"])
    print(f"分镜 {len(durs)} 幕，总时长 {total:.1f}s")
    return PAGE.format(w=w, h=h, cls=cls, shots="\n".join(shots_html), durs=json.dumps(durs))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--demo", choices=["ep04"], help="内置分镜：ep04 分压器带载")
    ap.add_argument("--shots", help="自定义分镜 JSON（结构见文件头 SHOTS_DOC；建议放 video/shots/）")
    ap.add_argument("--size", choices=["vertical", "horizontal"], default="vertical",
                    help="vertical=抖音 720x1280；horizontal=B 站 1920x1080")
    ap.add_argument("--cover", action="store_true",
                    help="只渲染首张标题卡并截图出封面 PNG（1080x1920 / 1620x910）")
    args = ap.parse_args()
    if args.demo == "ep04":
        storyboard = EP04
    elif args.shots:
        storyboard = json.loads(Path(args.shots).read_text(encoding="utf-8"))
    else:
        ap.error("--demo 或 --shots 二选一")

    w, h = (W, H) if args.size == "vertical" else (1920, 1080)
    cls = "v" if args.size == "vertical" else "h"
    if args.cover:
        storyboard = {**storyboard, "shots": storyboard["shots"][:1]}
        storyboard["shots"][0] = {**storyboard["shots"][0], "seconds": 2}
    html = build_html(storyboard, w=w, h=h, cls=cls)
    with tempfile.TemporaryDirectory() as tmp:
        page_file = Path(tmp) / "director.html"
        page_file.write_text(html, encoding="utf-8")

        from playwright.sync_api import sync_playwright

        OUT_DIR.mkdir(exist_ok=True)
        suffix = "" if args.size == "vertical" else "-h"
        out = OUT_DIR / (storyboard['name'] + f'-draft{suffix}.webm')
        with sync_playwright() as pw:
            browser = pw.chromium.launch(channel="chrome", headless=True)
            if args.cover:
                # 封面：同版式放大 1.5 倍截图（720x1280 → 1080x1920）
                scale = 1.5 if args.size == "vertical" else 1.0
                context = browser.new_context(
                    viewport={"width": w, "height": h}, device_scale_factor=scale)
                page = context.new_page()
                page.goto(page_file.as_uri())
                page.wait_for_timeout(1600)
                out = OUT_DIR / f"{storyboard['name']}-cover.png"
                page.screenshot(path=str(out))
                context.close()
                print(f"封面已出：{out.name}（{int(w * scale)}x{int(h * scale)}）")
                browser.close()
                return 0
            context = browser.new_context(
                viewport={"width": w, "height": h},
                record_video_dir=str(OUT_DIR),
                record_video_size={"width": w, "height": h},
            )
            page = context.new_page()
            page.goto(page_file.as_uri())
            total = sum(s["seconds"] for s in storyboard["shots"])
            page.wait_for_timeout(int((total + 0.8) * 1000))
            saved = Path(page.video.path())
            context.close()
            browser.close()
            saved.replace(out)
    size_mb = out.stat().st_size / 1048576
    print(f"草片已出：{out.name}（{w}x{h}，{total:.0f}s，{size_mb:.1f}MB）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

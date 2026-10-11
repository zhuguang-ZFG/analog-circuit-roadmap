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
        {"type": "card", "seconds": 3,
         "lines": ["接上负载那一刻", "5V 就没了"], "sub": "EP04 · 分压器带载"},
        {"type": "svg", "seconds": 12, "file": "divider-loading",
         "caption": "空载公式，只在空载成立"},
        {"type": "card", "seconds": 4,
         "lines": ["空载 5V → 带载 3.3V"], "sub": "塌了 33%"},
        {"type": "card", "seconds": 4,
         "lines": ["带载能力 ≈ R1∥R2"], "sub": "口诀"},
    ],
}

EP04 = {
    "name": "ep04-divider",
    "shots": [
        {"type": "card", "seconds": 3,
         "lines": ["接上负载那一刻", "5V 就没了"], "sub": "模拟电路动画课 · EP04"},
        {"type": "svg", "seconds": 13, "file": "divider-loading",
         "caption": "分压公式只在空载成立"},
        {"type": "card", "seconds": 4,
         "lines": ["空载 5V → 带载 3.3V"], "sub": "R2∥RL = 5k · 塌了 33%"},
        {"type": "card", "seconds": 4,
         "lines": ["带载能力 ≈ R1∥R2"], "sub": "口诀"},
        {"type": "card", "seconds": 6,
         "lines": ["三条活路"], "sub": "负载阻抗 ≫ R2 · R1/R2 取小 · 后面跟一级运放缓冲"},
        {"type": "card", "seconds": 4,
         "lines": ["下一集", "你看到的怪波形", "可能是探头画的"], "sub": "合集：模拟电路动画课 · 全书开源免费"},
    ],
}

PAGE = """<!DOCTYPE html>
<html lang="zh"><head><meta charset="utf-8">
<style>
  html,body {{ margin:0; width:{w}px; height:{h}px; overflow:hidden;
    font-family:"Microsoft YaHei",system-ui,sans-serif; }}
  .shot {{ position:fixed; inset:0; display:none; }}
  .shot.active {{ display:flex; }}
  .card {{ flex-direction:column; justify-content:center; align-items:center;
    gap:28px; text-align:center; padding:60px;
    background:
      radial-gradient(120% 90% at 100% 0%, rgba(94,122,255,.25), transparent 55%),
      linear-gradient(165deg,#1b2447 0%,#27357a 100%); }}
  .card::before {{ content:""; position:absolute; inset:0;
    background-image:radial-gradient(rgba(255,255,255,.13) 1px, transparent 1.2px);
    background-size:18px 18px;
    -webkit-mask-image:linear-gradient(180deg,#000,transparent 80%);
    mask-image:linear-gradient(180deg,#000,transparent 80%); }}
  .card .lines {{ position:relative; }}
  .card .lines div {{ color:#fff; font-size:64px; font-weight:800;
    line-height:1.35; letter-spacing:.01em; }}
  .card .sub {{ position:relative; color:#aab7e8; font-size:28px; line-height:1.6; }}
  .svgshot {{ flex-direction:column; background:#f6f7fb; }}
  .svgshot .stage {{ flex:1; display:flex; align-items:center; justify-content:center; width:100%; }}
  .svgshot svg {{ width:94%; height:auto; border-radius:14px;
    box-shadow:0 10px 34px rgba(23,32,64,.18); }}
  .svgshot .caption {{ height:96px; display:flex; align-items:center; justify-content:center;
    width:100%; background:#1b2447; color:#fff; font-size:32px; font-weight:700; }}
</style></head>
<body>
{shots}
<script>
  const durs = {durs};
  const shots = document.querySelectorAll('.shot');
  let i = 0;
  function show() {{
    shots.forEach((s, k) => s.classList.toggle('active', k === i));
    /* 第 i 幕停留 durs[i]——写 durs[i-1] 会整体错一拍：
       首幕 0ms 直接跳过、每幕都播上一幕的时长（实测踩过）。 */
    if (i + 1 < shots.length) setTimeout(() => {{ i += 1; show(); }}, durs[i]);
  }}
  show();
</script>
</body></html>"""


def build_html(storyboard: dict) -> str:
    shots_html, durs = [], []
    for s in storyboard["shots"]:
        durs.append(int(s["seconds"] * 1000))
        if s["type"] == "card":
            lines = "".join(f"<div>{ln}</div>" for ln in s["lines"])
            shots_html.append(
                f'<div class="shot card"><div class="lines">{lines}</div>'
                f'<div class="sub">{s.get("sub", "")}</div></div>')
        elif s["type"] == "svg":
            svg = (SVG_DIR / (s["file"] + ".svg")).read_text(encoding="utf-8")
            caption = f'<div class="caption">{s.get("caption", "")}</div>'
            shots_html.append(
                f'<div class="shot svgshot"><div class="stage">{svg}</div>{caption}</div>')
        else:
            raise SystemExit(f"未知镜头类型：{s['type']}")
    total = sum(s["seconds"] for s in storyboard["shots"])
    print(f"分镜 {len(durs)} 幕，总时长 {total:.0f}s")
    return PAGE.format(w=W, h=H, shots="\n".join(shots_html), durs=json.dumps(durs))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--demo", choices=["ep04"], help="内置分镜：ep04 分压器带载")
    ap.add_argument("--shots", help="自定义分镜 JSON（结构见文件头 SHOTS_DOC）")
    args = ap.parse_args()
    if args.demo == "ep04":
        storyboard = EP04
    elif args.shots:
        storyboard = json.loads(Path(args.shots).read_text(encoding="utf-8"))
    else:
        ap.error("--demo 或 --shots 二选一")

    html = build_html(storyboard)
    with tempfile.TemporaryDirectory() as tmp:
        page_file = Path(tmp) / "director.html"
        page_file.write_text(html, encoding="utf-8")

        from playwright.sync_api import sync_playwright

        OUT_DIR.mkdir(exist_ok=True)
        out = OUT_DIR / f"{storyboard['name']}-draft.webm"
        with sync_playwright() as pw:
            browser = pw.chromium.launch(channel="chrome", headless=True)
            context = browser.new_context(
                viewport={"width": W, "height": H},
                record_video_dir=str(OUT_DIR),
                record_video_size={"width": W, "height": H},
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
    print(f"草片已出：{out.name}（{W}x{H}，{total:.0f}s，{size_mb:.1f}MB）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

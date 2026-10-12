#!/usr/bin/env python3
"""把一张 SMIL 动画逐帧直录成视频样片（video/samples/）。

这是《模拟电路动画课》素材管线的「稳」路线（见本目录 README 第 3 节）：
Playwright 以动画文档本身为页面（file:// 即可，无需起服务器）。
**逐帧确定性采集**：暂停 SMIL 时钟、按帧号 setCurrentTime，截图吞吐与
时间轴解耦（与 director.py 同款方案），JPEG q95 帧直送 x264 CRF12——
不再有 Chromium 内置录屏 VP8 固定低码率的条带与糊字。

用法（需要 dev 依赖 playwright + 本机 Chrome，与 CI 同一套）：
    python video/record_clip.py --svg miller-plateau --seconds 12
    python video/record_clip.py --svg comparator-hysteresis --seconds 15 --scale 2

产出 video/samples/<stem>-sample.mp4；剪映/平台二压时直接用即可
（样片的用途是「确认节拍与字幕在成片里可读」，不是最终成片）。
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SVG_DIR = ROOT / "assets" / "svg"
OUT_DIR = Path(__file__).resolve().parent / "samples"

FPS = 30   # 平台原生帧率（与 director.py 一致）


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--svg", required=True, help="动画名（不带扩展名），如 miller-plateau")
    ap.add_argument("--seconds", type=float, default=12, help="录制时长（SMIL 按自身时钟逐帧推进）")
    ap.add_argument("--scale", type=float, default=1.0, help="整数倍超采样，2=1600px 宽的清晰版")
    args = ap.parse_args()

    svg = SVG_DIR / f"{args.svg}.svg"
    if not svg.is_file():
        print(f"动画不存在：{svg}", file=sys.stderr)
        return 1
    head = svg.read_text(encoding="utf-8")[:2000]
    box = re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', head)
    if not box:
        print("SVG 缺 viewBox，无法定画幅", file=sys.stderr)
        return 1
    width = round(float(box.group(1)) * args.scale)
    height = round(float(box.group(2)) * args.scale)

    import imageio_ffmpeg
    from playwright.sync_api import sync_playwright

    OUT_DIR.mkdir(exist_ok=True)
    out = OUT_DIR / f"{args.svg}-sample.mp4"
    n_frames = int(round(args.seconds * FPS))
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    proc = subprocess.Popen(
        [ff, "-y", "-f", "image2pipe", "-framerate", str(FPS), "-i", "-",
         "-c:v", "libx264", "-preset", "medium", "-crf", "12",
         "-pix_fmt", "yuv420p", str(out)],
        stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    with sync_playwright() as pw:
        browser = pw.chromium.launch(channel="chrome", headless=True)
        context = browser.new_context(viewport={"width": width, "height": height})
        page = context.new_page()
        page.goto(svg.as_uri())
        t0 = time.perf_counter()
        for k in range(n_frames):
            # 文档即 SVG 根元素：暂停后按全局时间逐帧推进
            page.evaluate("(t) => { const r = document.documentElement;"
                          " r.pauseAnimations(); r.setCurrentTime(t); }", k / FPS)
            proc.stdin.write(page.screenshot(type="jpeg", quality=95))
            if (k + 1) % 100 == 0:
                print(f"  采帧 {k + 1}/{n_frames}（{time.perf_counter() - t0:.0f}s）")
        context.close()
        browser.close()
    proc.stdin.close()
    if proc.wait() != 0:
        raise SystemExit(f"ffmpeg 编码失败：{out.name}")
    size_kb = out.stat().st_size // 1024
    print(f"已录制 {out.name}（{width}x{height}，{args.seconds}s，{size_kb}KB）")
    print("节拍核对提示：样片里应能看到每拍字幕完整可读；发现字幕被裁再调 --scale。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

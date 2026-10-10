#!/usr/bin/env python3
"""把一张 SMIL 动画直录成视频样片（video/samples/）。

这是《模拟电路动画课》素材管线的「稳」路线（见本目录 README 第 3 节）：
Playwright 以动画文档本身为页面（file:// 即可，无需起服务器），
SMIL 在文档上下文里自动循环播放，浏览器侧录像直接落成 WebM。

用法（需要 dev 依赖 playwright + 本机 Chrome，与 CI 同一套）：
    python video/record_clip.py --svg miller-plateau --seconds 12
    python video/record_clip.py --svg comparator-hysteresis --seconds 15 --scale 2

产出 video/samples/<stem>-sample.webm；剪映/平台二压时再转 mp4 即可
（样片的用途是「确认节拍与字幕在成片里可读」，不是最终成片）。
"""
from __future__ import annotations

import argparse
import re
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SVG_DIR = ROOT / "assets" / "svg"
OUT_DIR = Path(__file__).resolve().parent / "samples"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--svg", required=True, help="动画名（不带扩展名），如 miller-plateau")
    ap.add_argument("--seconds", type=float, default=12, help="录制时长（动画在文档里循环播）")
    ap.add_argument("--scale", type=float, default=1.0, help="整数倍超采样，2=1600px 宽的清晰版")
    args = ap.parse_args()

    svg = SVG_DIR / f"{args.svg}.svg"
    if not svg.is_file():
        print(f"动画不存在：{svg}", file=__import__("sys").stderr)
        return 1
    head = svg.read_text(encoding="utf-8")[:2000]
    box = re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', head)
    if not box:
        print("SVG 缺 viewBox，无法定画幅", file=__import__("sys").stderr)
        return 1
    width = round(float(box.group(1)) * args.scale)
    height = round(float(box.group(2)) * args.scale)

    from playwright.sync_api import sync_playwright

    OUT_DIR.mkdir(exist_ok=True)
    out = OUT_DIR / f"{args.svg}-sample.webm"
    with sync_playwright() as pw:
        browser = pw.chromium.launch(channel="chrome", headless=True)
        context = browser.new_context(
            viewport={"width": width, "height": height},
            record_video_dir=str(OUT_DIR),
            record_video_size={"width": width, "height": height},
        )
        page = context.new_page()
        page.goto(svg.as_uri())
        page.wait_for_timeout(int(args.seconds * 1000))
        saved = page.video.path()
        context.close()          # close 之后录像文件才落盘
        browser.close()
        saved = Path(saved)
        saved.replace(out)
    size_kb = out.stat().st_size // 1024
    print(f"已录制 {out.name}（{width}x{height}，{args.seconds}s，{size_kb}KB）")
    print("节拍核对提示：样片里应能看到每拍字幕完整可读；发现字幕被裁再调 --scale。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

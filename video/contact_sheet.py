#!/usr/bin/env python
"""验收帧拼图：成片抽 12 帧拼 3×4 网格（带时间码），一眼看全片版式。

动机：逐张看 12 张 1080×1920 全图又慢又费上下文；拼图先整版浏览，
可疑帧再回原目录单张放大。

用法：
  python video/contact_sheet.py video/samples/ep04-divider-final.mp4
  python video/contact_sheet.py out/v1.mp4 --times 2,7.2,15.8 --cols 3
  python video/contact_sheet.py in.mp4 --shots out/shots.json   # 按分镜起止点各取首帧+中段
输出：<video 同目录>/<name>-sheet.png
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

FF = "ffmpeg"


def duration(video: Path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(video)],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    return float(out)


def grab(video: Path, t: float, dst: Path) -> bool:
    r = subprocess.run([FF, "-v", "error", "-y", "-ss", f"{t:.3f}", "-i", str(video),
                        "-frames:v", "1", "-q:v", "2", str(dst)], capture_output=True)
    return r.returncode == 0 and dst.exists()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--times", default="", help="逗号分隔的秒数；缺省按 --shots 或均匀 12 点")
    ap.add_argument("--shots", default="", help="shots.json（[{id,start,end}]）取每镜首帧+中点")
    ap.add_argument("--cols", type=int, default=3)
    ap.add_argument("--cell", type=int, default=360, help="单格宽（高按画幅比例）")
    args = ap.parse_args()

    video = Path(args.video)
    if not video.exists():
        print(f"FAIL 找不到 {video}")
        return 2
    dur = duration(video)

    if args.times:
        times = [float(x) for x in args.times.split(",") if x.strip()]
    elif args.shots:
        shots = json.loads(Path(args.shots).read_text(encoding="utf-8"))
        times = []
        for s in shots:
            st, en = float(s["start"]), float(s["end"])
            times += [st + 0.15, (st + en) / 2]
    else:
        n = 12
        times = [dur * (i + 0.5) / n for i in range(n)]

    cols = max(1, args.cols)
    rows = (len(times) + cols - 1) // cols
    with tempfile.TemporaryDirectory() as tmp:
        cells = []
        for i, t in enumerate(times):
            p = Path(tmp) / f"f{i}.png"
            if grab(video, t, p):
                cells.append((t, Image.open(p).convert("RGB")))
            else:
                cells.append((t, None))
        if not cells:
            print("FAIL 未取到任何帧")
            return 2
        cw = args.cell
        ch = round(cw * cells[0][1].height / cells[0][1].width) if cells[0][1] else cw
        pad, label_h = 8, 26
        W = cols * cw + (cols + 1) * pad
        H = rows * (ch + label_h) + (rows + 1) * pad
        sheet = Image.new("RGB", (W, H), (18, 22, 34))
        draw = ImageDraw.Draw(sheet)
        for i, (t, im) in enumerate(cells):
            r, c = divmod(i, cols)
            x = pad + c * (cw + pad)
            y = pad + r * (ch + label_h + pad)
            if im is not None:
                sheet.paste(im.resize((cw, ch)), (x, y + label_h))
            draw.text((x + 2, y + 6), f"#{i}  {t:.2f}s", fill=(200, 210, 240))
        out = video.with_name(video.stem + "-sheet.png")
        sheet.save(out)
        print(f"{video.name}  时长 {dur:.1f}s  抽 {len(cells)} 帧 → {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python
"""静止检测闸（反 PPT 机器验证）：成片里连续 2 秒画面近乎不动 = FAIL。

口径（实测标定，勿凭感觉改）：
- 相邻帧差在**本管线不可用**：ShotShell 的 PCB 走线/点阵/光斑是常驻背景运动，
  实测旧成片相邻帧均差 0.06~0.11%，与「极缓推镜」的逐帧增量（0.111%）同量级，
  相邻帧判定分不开「有相机」和「死画面」。
- 因此按 **--gap 1.0s 的帧对**测量：相机累进 1 秒后位移明显，背景漂移因低透明度累积增量小。
- 字幕带（卡拉OK 逐字点亮）必须裁掉——它每帧都在变，会把死画面判绿。
  裁切几何取自 remotion/src/Subtitles.tsx：竖屏 Pill top=1425（1080×1920），
  横屏 top=height-215（1920×1080）。
- 双判定：帧对均差 + 窗口内是否有任何一帧对越阈（窗口内全部低于阈值才算静止）。
- **本闸职责边界**：抓「冻结/坏渲染」（丢帧、黑屏、组件没动起来），不是判 PPT 感——
  背景常驻漂移本身就有 0.25%/s 量级的帧对差，旧成片实测下限 0.247%（横）/0.384%（竖），
  相机版下限 0.945%。PPT 感由相机层（ShotShell cam）+ 人工审片负责。

用法：
  python video/check_still.py video/samples/ep04-divider-final.mp4
  python video/check_still.py out/v1.mp4 --gap 1.0 --window 2.0 --thresh 0.25
退出码：0 = 通过；1 = 存在静止窗（FAIL）。
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

import numpy as np

FF = "ffmpeg"


def probe_size(video: Path) -> tuple[int, int]:
    out = subprocess.run(
        [FF.replace("ffmpeg", "ffprobe"), "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width,height", "-of", "csv=p=0", str(video)],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    w, h = out.split(",")[:2]
    return int(w), int(h)


def frames_gray(video: Path, crop: str, scale: tuple[int, int], fps: float) -> np.ndarray:
    w, h = scale
    cmd = [FF, "-v", "error", "-i", str(video),
           "-vf", f"crop={crop},fps={fps},scale={w}:{h},format=gray",
           "-f", "rawvideo", "-pix_fmt", "gray", "-"]
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.uint8).reshape(-1, h, w).astype(np.int16)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--fps", type=float, default=30.0, help="采样帧率（默认成片 30）")
    ap.add_argument("--gap", type=float, default=1.0, help="帧对间隔秒（默认 1.0）")
    ap.add_argument("--window", type=float, default=2.0, help="静止窗长度秒（默认 2.0）")
    ap.add_argument("--thresh", type=float, default=0.20,
                    help="帧对均差下限%%（窗口内全部低于此值判静止；实测下限 0.247，默认 0.20）")
    ap.add_argument("--crop", default="", help="自定义裁切（默认自动裁字幕带）")
    args = ap.parse_args()

    video = Path(args.video)
    if not video.exists():
        print(f"FAIL 找不到文件: {video}")
        return 2

    w, h = probe_size(video)
    vertical = h > w
    band = 495 if vertical else 215  # Subtitles.tsx：竖屏 1920-1425=495；横屏 215
    crop = args.crop or f"{w}:{h - band}:0:0"
    small = (270, 356) if vertical else (480, 216)
    fr = frames_gray(video, crop, small, args.fps)
    n = len(fr)
    g = max(int(round(args.gap * args.fps)), 1)
    if n <= g:
        print(f"FAIL 帧数不足（{n}）")
        return 2

    diffs = np.abs(fr[g:] - fr[:-g]).mean(axis=(1, 2)) / 255 * 100  # 百分比
    win = max(int(round(args.window * args.fps)), 1)
    win = min(win, len(diffs))

    dead: list[tuple[float, float, float]] = []
    for i in range(0, len(diffs) - win + 1):
        seg = diffs[i:i + win]
        if float(seg.max()) < args.thresh:
            dead.append((i / args.fps, (i + win + g) / args.fps, float(seg.mean())))
    # 合并相邻静止窗
    merged: list[list[float]] = []
    for s, e, m in dead:
        if merged and s <= merged[-1][1] + 0.01:
            merged[-1][1] = e
            merged[-1][2] = min(merged[-1][2], m)
        else:
            merged.append([s, e, m])

    print(f"{video.name}  {w}x{h}  crop={crop}  帧对数={len(diffs)}  gap={args.gap}s  thresh={args.thresh}%")
    print(f"  帧对均差 %: min={diffs.min():.3f} p50={np.median(diffs):.3f} max={diffs.max():.3f}")
    if merged:
        for s, e, m in merged:
            print(f"  FAIL 静止窗 {s:6.2f}s → {e:6.2f}s（帧对均差均值 {m:.3f}% < {args.thresh}%）")
        print("结论：FAIL —— 上面这些窗口里画面几乎不动，补运动（相机推镜/元素让位）或延长该镜。")
        return 1
    print("结论：PASS —— 每 2s 窗口内都有可测的画面运动。")
    return 0


if __name__ == "__main__":
    sys.exit(main())

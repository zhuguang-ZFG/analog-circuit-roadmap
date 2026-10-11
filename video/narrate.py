#!/usr/bin/env python3
"""配音编排：分镜表 → 神经语音口播 → 时间轴自动对齐 → 出带配音的 MP4 草片。

管线（依赖 edge-tts 与 imageio-ffmpeg，均为开发侧工具）：
  1. 逐镜取 shots JSON 里的 `voice` 文本，edge-tts 合成 MP3（默认
     zh-CN-YunxiNeural，语速 +12%——短视频口播节奏）；
  2. 解码测时长，**自动重排时间轴**：每幕秒数 = max(原秒数, 口播 + 0.7s)，
     动画幕保底原有秒数（动画有自身的节拍）；
  3. 调 director.py 按新时间轴重录无声视频；
  4. 按同一时间轴把逐镜口播拼成整条音轨（幕首对齐，其余补静音）；
  5. ffmpeg 合成音视频 → video/samples/<name>-vo.mp4。

无声草片（<name>-draft.webm）保留：剪映精剪时对轨更灵活。
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SAMPLES = Path(__file__).resolve().parent / "samples"
TMP = Path(tempfile.gettempdir()) / "analog-vo"

LEAD = 0.35   # 每幕口播前的呼吸（秒）
TAIL = 0.35   # 口播后的收尾（秒）
RATE = "+12%"
VOICE = "zh-CN-YunxiNeural"


def ffmpeg_exe() -> str:
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


def synth(text: str, mp3: Path, voice: str, rate: str) -> None:
    import asyncio
    import edge_tts

    async def run() -> None:
        await edge_tts.Communicate(text, voice, rate=rate).save(str(mp3))

    asyncio.run(run())


def mp3_secs(mp3: Path, ff: str) -> float:
    wav = mp3.with_suffix(".wav")
    subprocess.run([ff, "-y", "-i", str(mp3), "-ar", "24000", "-ac", "1",
                    str(wav)], check=True, capture_output=True)
    with wave.open(str(wav), "rb") as w:
        return w.getnframes() / w.getframerate(), wav


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--shots", required=True, help="分镜 JSON（含 voice 字段）")
    ap.add_argument("--size", choices=["vertical", "horizontal"], default="vertical")
    ap.add_argument("--voice", default=VOICE)
    ap.add_argument("--rate", default=RATE)
    ap.add_argument("--no-render", action="store_true",
                    help="只测口播时长与时间轴，不出片")
    args = ap.parse_args()

    board = json.loads(Path(args.shots).read_text(encoding="utf-8"))
    name = board["name"]
    ff = ffmpeg_exe()
    TMP.mkdir(exist_ok=True)

    # 1) 逐镜配音 + 2) 时间轴对齐
    wavs, adjusted = [], []
    total_voice = 0.0
    for i, shot in enumerate(board["shots"], 1):
        text = shot.get("voice", "")
        if text:
            mp3 = TMP / f"{name}-{i}.mp3"
            synth(text, mp3, args.voice, args.rate)
            secs, wav = mp3_secs(mp3, ff)
            wavs.append((wav, secs))
            total_voice += secs
            need = secs + LEAD + TAIL
            new_secs = max(shot["seconds"], round(need, 2))
            mark = "" if new_secs <= shot["seconds"] + 0.01 else f"（原 {shot['seconds']}s → {new_secs}s）"
            print(f"  幕{i}: 口播 {secs:.1f}s{mark}")
            adjusted.append({**shot, "seconds": new_secs})
        else:
            wavs.append((None, shot["seconds"]))
            adjusted.append(dict(shot))
            print(f"  幕{i}: 无口播，保留 {shot['seconds']}s")
    board["shots"] = adjusted
    total = sum(s["seconds"] for s in board["shots"])
    print(f"口播合计 {total_voice:.1f}s → 成片 {total:.1f}s")

    adjusted_file = TMP / f"{name}-adjusted.json"
    adjusted_file.write_text(json.dumps(board, ensure_ascii=False), encoding="utf-8")
    if args.no_render:
        return 0

    # 3) 按新时间轴重录无声视频
    print("渲染视频…")
    subprocess.run([sys.executable, str(Path(__file__).parent / "director.py"),
                    "--shots", str(adjusted_file), "--size", args.size],
                   check=True)
    suffix = "" if args.size == "vertical" else "-h"
    silent = SAMPLES / f"{name}-draft{suffix}.webm"

    # 4) 按同一时间轴拼整条音轨（24kHz 单声道）
    print("拼音轨…")
    rate = 24000
    timeline_len = int(round(total * rate))
    import array
    timeline = array.array("h", [0]) * timeline_len
    offset = 0
    for (wav, _secs), shot in zip(wavs, board["shots"]):
        if wav is not None:
            with wave.open(str(wav), "rb") as w:
                frames = array.array("h", w.readframes(w.getnframes()))
            end = min(offset + len(frames), timeline_len)
            for k in range(offset, end):
                v = timeline[k] + frames[k - offset]
                timeline[k] = max(-32768, min(32767, v))   # 简单限幅
        offset += int(round(shot["seconds"] * rate))
    narration = TMP / f"{name}-narration.wav"
    with wave.open(str(narration), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(timeline.tobytes())

    # 5) 合成（vp8 → h264，音轨 AAC）
    suffix = "" if args.size == "vertical" else "-h"
    out = SAMPLES / f"{name}-vo{suffix}.mp4"
    subprocess.run([ff, "-y", "-i", str(silent), "-i", str(narration),
                    "-c:v", "libx264", "-preset", "medium", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-b:a", "128k", "-shortest", str(out)],
                   check=True, capture_output=True)
    print(f"带配音成片：{out.name}（{out.stat().st_size / 1048576:.1f}MB）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""成片母带：无声/口播草片 + 程序化 BGM + 烧录字幕 → 可发布 MP4。

发布标准的三块最后拼图，一条命令补齐：
  1. **烧录字幕**：按 timeline（narrate.py 落盘的对齐时间轴）给每一幕的
     口播文本烧 drawtext 字幕（抖音大量静音观看场景，字幕是硬需求）；
  2. **BGM**：bgm.py 程序化合成的垫乐压到口播之下（0.16 倍，零版权）；
  3. **封装**：h264 + AAC，输出 video/samples/<name>-final.mp4。

输入：samples/<name>-vo.mp4（narrate.py 产物）+ <name>-timeline.json。
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import wave
from pathlib import Path

HERE = Path(__file__).resolve().parent
SAMPLES = HERE / "samples"
sys.path.insert(0, str(HERE))

FONT = "C\\:/Windows/Fonts/msyh.ttc"
BGM_GAIN = 0.16


def wrap(text: str, width: int = 17) -> str:
    """口播文本按字数折行（CJK 无空格，按字符切）。"""
    return "\n".join(text[i:i + width] for i in range(0, len(text), width))


def chunk_voice(text: str, max_len: int = 30) -> list[str]:
    """口播文本按句切分，长句再按逗号二次切分到 ≤max_len。"""
    import re
    sentences = [s for s in re.split(r"(?<=[。！？；])", text) if s.strip()]
    chunks = []
    for s in sentences:
        if len(s) <= max_len:
            chunks.append(s)
            continue
        parts = [x for x in re.split(r"(?<=[，、])", s) if x.strip()]
        cur = ""
        for part in parts:
            if len(cur) + len(part) <= max_len:
                cur += part
            else:
                if cur:
                    chunks.append(cur)
                cur = part
        if cur:
            chunks.append(cur)
    return chunks


def subtitle_filters(board: dict, tmp: Path, size: int, y: str) -> list[str]:
    """句子级字幕：幕内按字数比例分配窗口——字幕节奏跟着口播走，
    不是一幕一条挂十秒（实测过，太钝）。"""
    filters = []
    t0 = 0.0
    idx = 0
    for shot in board["shots"]:
        dur = shot["seconds"]
        text = shot.get("voice", "")
        if text:
            chunks = chunk_voice(text)
            total_chars = sum(len(c) for c in chunks)
            speakable = max(dur - 0.35, 0.5)     # 幕首 0.2s + 尾 0.15s 不压字
            clock = t0 + 0.2
            for chunk in chunks:
                share = speakable * len(chunk) / total_chars
                tf = tmp / f"sub-{idx}.txt"
                idx += 1
                tf.write_text(wrap(chunk), encoding="utf-8")
                tf_q = str(tf).replace("\\", "/").replace(":", "\:")
                enable = f"between(t,{clock:.2f},{min(clock + share, t0 + dur - 0.1):.2f})"
                filters.append(
                    f"drawtext=fontfile='{FONT}':textfile='{tf_q}':"
                    f"fontsize={size}:fontcolor=white:borderw=4:"
                    f"bordercolor=black@0.75:line_spacing=10:"
                    f"x=(w-text_w)/2:y={y}:enable='{enable}'")
                clock += share
        t0 += dur
    return filters


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--shots", required=True, help="video/shots/*.json（名称来源）")
    ap.add_argument("--size", choices=["vertical", "horizontal"], default="vertical")
    ap.add_argument("--no-subs", action="store_true")
    args = ap.parse_args()

    suffix = "" if args.size == "vertical" else "-h"
    name = Path(args.shots).stem
    vo = SAMPLES / f"{name}-vo{suffix}.mp4"
    timeline = SAMPLES / f"{name}-timeline.json"
    if not vo.is_file() or not timeline.is_file():
        print("缺输入：先跑 narrate.py 生成 -vo.mp4 与 -timeline.json", file=sys.stderr)
        return 1
    board = json.loads(timeline.read_text(encoding="utf-8"))
    total = sum(s["seconds"] for s in board["shots"])

    import imageio_ffmpeg
    ff = imageio_ffmpeg.get_ffmpeg_exe()

    # BGM：与成片等长，淡出收尾
    from bgm import make_bgm
    import numpy as np
    data = (make_bgm(total) * 32767 * 0.9).astype(np.int16)
    bgm_wav = SAMPLES / f"{name}-bgm.wav"
    with wave.open(str(bgm_wav), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(44100)
        w.writeframes(data.tobytes())

    import tempfile
    out = SAMPLES / f"{name}-final{suffix}.mp4"
    with tempfile.TemporaryDirectory() as tmp:
        vf = "drawtext=fontfile='" + FONT + "':text=' ':x=0:y=0"
        if not args.no_subs:
            sub_size, sub_y = (38, "h-330") if args.size == "vertical" else (52, "h-175")
            subs = subtitle_filters(board, Path(tmp), sub_size, sub_y)
            vf = ",".join(subs) if subs else vf
        cmd = [ff, "-y", "-i", str(vo), "-i", str(bgm_wav),
               "-filter_complex",
               f"[1:a]volume={BGM_GAIN}[bg];[0:a][bg]amix=inputs=2:"
               f"duration=first:dropout_transition=0[a];"
               f"[0:v]{vf}[v]",
               "-map", "[v]", "-map", "[a]",
               "-c:v", "libx264", "-preset", "medium", "-pix_fmt", "yuv420p",
               "-c:a", "aac", "-b:a", "160k", "-shortest", str(out)]
        subprocess.run(cmd, check=True, capture_output=True)
    print(f"发布成片：{out.name}（{args.size}，{out.stat().st_size / 1048576:.1f}MB，"
          f"{total:.1f}s，含 BGM{' + 烧录字幕' if not args.no_subs else ''}）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

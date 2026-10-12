#!/usr/bin/env python3
"""成片母带：无声/口播草片 + 程序化 BGM + 烧录字幕 → 可发布 MP4。

发布标准的几块最后拼图，一条命令补齐：
  1. **烧录字幕**：按 timeline（narrate.py 落盘的对齐时间轴）给每一幕的
     口播文本烧 drawtext 字幕（抖音大量静音观看场景，字幕是硬需求）；
  2. **BGM**：bgm.py 程序化合成的垫乐压到口播之下（0.16 倍，零版权）；
  3. **响度归一化**：三轨混音后两遍 loudnorm 抬到 -16 LUFS / 真峰值 -1.5 dBTP，
     与短视频平台主流响度对齐（raw 混音约 -22 LUFS，手机上偏轻）；
  4. **封装**：h264（crf 20，扁平矢量画面足够）+ AAC，输出 video/samples/<name>-final.mp4。

输入：samples/<name>-vo.mp4（narrate.py 产物）+ <name>-timeline.json。
"""
from __future__ import annotations

import argparse
import array
import json
import subprocess
import sys
import wave
from pathlib import Path

HERE = Path(__file__).resolve().parent
SAMPLES = HERE / "samples"
sys.path.insert(0, str(HERE))

FONT = "C:/Windows/Fonts/msyh.ttc"   # 兜底字体原始路径（含 β 等快乐体缺字的分块）
# 字幕主字体：站酷快乐体（ZCOOL KuaiLe，OFL 1.1 免费商用，授权见 fonts/OFL-ZCOOL-KuaiLe.txt）
# 对全量口播文本做过字形覆盖核验：仅 β 缺字，命中 MISSING_KL 的分块回退 msyh。
# 注意：FONT 必须是未转义的原始路径——drawtext 的 ':'/'\\' 转义统一在 sub_font 做，
# 曾经把预转义的 "C\:/..." 再过一遍 replace 链得到 "C/\:/..." 双残路径，整段豆腐（ep15 实证）
KUAI_LE = (HERE / "fonts" / "ZCOOLKuaiLe-Regular.ttf").resolve()
MISSING_KL = set("β")


def sub_font(text: str) -> str:
    """挑字幕字体：快乐体为主，含缺字的分块回退微软雅黑。"""
    path = FONT if any(c in MISSING_KL for c in text) else str(KUAI_LE)
    return path.replace("\\", "/").replace(":", "\\:")


BGM_GAIN = 0.16


PUNC = "，。！？；、：…—"   # CJK 标点：折行避头点用


def wrap(text: str, width: int = 16) -> str:
    """口播文本按字数折行（CJK 无空格，按字符切）。
    行首不留标点：满宽时下一个是标点就连同后续标点（至多 2 个，防 ……/—— 拆开）
    一起归到上一行行尾（避头点）。宽度 16 + 最多 2 个标点 = 18 字 × 57px + 托板边距
    仍小于 1080，不会溢出竖屏。"""
    lines, cur = [], ""
    i, n = 0, len(text)
    while i < n:
        cur += text[i]
        i += 1
        if len(cur) == width:
            # 不在 ASCII 串中间断（数字/型号：0.01、1N4148 不能拆成 0.0|.01）：
            # 断点两侧都是 ASCII 字符时把断点后移过整个串（上限 width+8，防超长串顶穿）
            if i < n and cur[-1].isascii() and (cur[-1].isalnum() or cur[-1] in "._") \
                    and text[i].isascii() and (text[i].isalnum() or text[i] in "._"):
                while i < n and len(cur) < width + 8 \
                        and text[i].isascii() and (text[i].isalnum() or text[i] in "._"):
                    cur += text[i]
                    i += 1
            pulled = 0
            while i < n and pulled < 2 and text[i] in PUNC:
                cur += text[i]
                i += 1
                pulled += 1
            lines.append(cur)
            cur = ""
    if cur:
        lines.append(cur)
    return "\n".join(lines)


def chunk_voice(text: str, max_len: int = 30) -> list[str]:
    """口播文本按句切分，长句再按逗号二次切分到 ≤max_len。
    无逗号超长段（如 0.01 这类数字密集的句子）兜底按 max_len 硬切，
    保证任何字幕块 ≤2 行（wrap 宽 16 + 避头点 2 = 18 上限）。"""
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
    flat = []
    for c in chunks:
        while len(c) > max_len:
            cut = next((j for j in range(max_len, int(max_len * 0.6), -1)
                        if c[j - 1] in "，、："), max_len)
            # 同样不在数字/型号中间断
            while cut > 1 and c[cut - 1].isascii() and (c[cut - 1].isalnum() or c[cut - 1] in "._") \
                    and c[cut].isascii() and (c[cut].isalnum() or c[cut] in "._"):
                cut -= 1
            flat.append(c[:cut])
            c = c[cut:]
        if not c.strip(PUNC):   # 尾段只剩标点：并入上一块，不留孤标点块
            if flat:
                flat[-1] += c
        else:
            flat.append(c)
    return flat


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
                tf_q = str(tf).replace("\\", "/").replace(":", "\\:")
                enable = f"between(t,{clock:.2f},{min(clock + share, t0 + dur - 0.1):.2f})"
                filters.append(
                    f"drawtext=fontfile='{sub_font(chunk)}':textfile='{tf_q}':"
                    f"fontsize={size}:fontcolor=white:borderw=4:"
                    f"bordercolor=black@0.75:line_spacing=10:"
                    f"box=1:boxcolor=black@0.32:boxborderw=16:"
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
    import numpy as np
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    SR = 44100

    # 口播轨：从 vo.mp4 解码到 wav
    vo_wav = SAMPLES / f"{name}-vo-narr.wav"
    subprocess.run([ff, "-y", "-i", str(vo), "-ar", "44100", "-ac", "1",
                    str(vo_wav)], check=True, capture_output=True)

    # SFX 时间轴：标题幕 thud；其余幕转场 whoosh；数字幕跳数落定 pop
    from sfx import whoosh, pop, thud, sting, place
    sfx_track = np.zeros(int(total * SR) + SR)
    t0 = 0.0
    for shot in board["shots"]:
        if shot["type"] == "intro":
            place(sfx_track, sting(), t0 + 0.05)
        elif shot.get("eyebrow"):
            place(sfx_track, thud(), t0 + 0.02)
        else:
            place(sfx_track, whoosh(), t0)
        if shot["type"] == "num":
            place(sfx_track, pop(), t0 + 1.5)
        t0 += shot["seconds"]
    sfx_track = sfx_track[:int(total * SR)] * 0.5

    # BGM：与成片等长，淡出收尾
    from bgm import make_bgm
    data = (make_bgm(total) * 32767 * 0.9).astype(np.int16)
    bgm_wav = SAMPLES / f"{name}-bgm.wav"
    with wave.open(str(bgm_wav), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(44100)
        w.writeframes(data.tobytes())

    # 三轨 Python 混音：口播全量 + BGM 0.16 + SFX 0.5（简单限幅）
    with wave.open(str(vo_wav), "rb") as w:
        nar_rate = w.getframerate()
        narr = np.array(array.array("h", w.readframes(w.getnframes())), dtype=np.float64)
    if nar_rate != 44100:
        ratio = 44100 / nar_rate
        n_new = int(len(narr) * ratio)
        narr = np.interp(np.linspace(0, len(narr) - 1, n_new),
                         np.arange(len(narr)), narr)
    mix_len = max(len(narr), len(sfx_track), len(data))
    mix = np.zeros(mix_len)
    mix[:len(narr)] += narr
    mix[:len(data)] += data / 32767 * BGM_GAIN
    mix[:len(sfx_track)] += sfx_track
    peak = float(np.max(np.abs(mix))) or 1.0
    if peak > 0.97:
        mix *= 0.97 / peak
    final_wav = SAMPLES / f"{name}-final-audio.wav"
    with wave.open(str(final_wav), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(44100)
        w.writeframes((mix * 32767).astype(np.int16).tobytes())

    # 响度归一化：混音 raw ~-22 LUFS，抬到平台主流 -16 LUFS / 真峰值 -1.5 dBTP
    # （两遍 loudnorm：先测后线性增益，口播+垫乐内容 LRA≈6<7 不需要动态压）
    p1 = subprocess.run([ff, "-i", str(final_wav), "-af",
                         "loudnorm=I=-16:TP=-1.5:LRA=7:print_format=json",
                         "-f", "null", "-"], capture_output=True, text=True)
    stats = json.loads(p1.stderr[p1.stderr.rindex("{"):p1.stderr.rindex("}") + 1])
    ln = (f"loudnorm=I=-16:TP=-1.5:LRA=7:measured_I={stats['input_i']}"
          f":measured_TP={stats['input_tp']}:measured_LRA={stats['input_lra']}"
          f":measured_thresh={stats['input_thresh']}:offset={stats['target_offset']}"
          ":linear=true,aresample=44100")
    normed = final_wav.with_suffix(".norm.wav")
    subprocess.run([ff, "-y", "-i", str(final_wav), "-af", ln, str(normed)],
                   check=True, capture_output=True)
    normed.replace(final_wav)

    import tempfile
    out = SAMPLES / f"{name}-final{suffix}.mp4"
    with tempfile.TemporaryDirectory() as tmp:
        vf = "drawtext=fontfile='" + sub_font(" ") + "':text=' ':x=0:y=0"
        if not args.no_subs:
            # 横屏两行字幕块高约 175px，h-175 会把第二行推出底边（旧片已裁），h-240 留边
            sub_size, sub_y = (57, "h-495") if args.size == "vertical" else (52, "h-240")
            subs = subtitle_filters(board, Path(tmp), sub_size, sub_y)
            vf = ",".join(subs) if subs else vf
        cmd = [ff, "-y", "-i", str(vo), "-i", str(final_wav),
               "-vf", vf,
               "-map", "0:v", "-map", "1:a",
               "-c:v", "libx264", "-preset", "slow", "-crf", "20",
               "-pix_fmt", "yuv420p", "-movflags", "+faststart",
               "-c:a", "aac", "-b:a", "160k", "-shortest", str(out)]
        subprocess.run(cmd, check=True, capture_output=True)
    print(f"发布成片：{out.name}（{args.size}，{out.stat().st_size / 1048576:.1f}MB，"
          f"{total:.1f}s，含 BGM + 音效卡点{' + 烧录字幕' if not args.no_subs else ''}）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

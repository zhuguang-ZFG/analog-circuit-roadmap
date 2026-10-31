#!/usr/bin/env python3
"""配音编排：分镜表 → 神经语音口播 → 时间轴自动对齐 → 出带配音的 MP4 草片。

管线（依赖 edge-tts 与 imageio-ffmpeg，均为开发侧工具）：
  1. 逐镜取 shots JSON 里的 `voice` 文本，edge-tts 合成 MP3 + WordBoundary
     NDJSON（默认 zh-CN-YunxiNeural，语速 +12%）；quiz 的非空 answerVoice 独立合成；
  2. 解码测时长，**自动重排时间轴**：幕长至少覆盖 LEAD + 完整口播 + TAIL，
     quiz 在问题音频结束后等待 thinkSeconds（默认 2s），然后播答案。
     原 shots 字段保留；speech 为相对幕首秒数的 {text,start,end}[]，
     revealAt 为答案音频起点（仅独立答案模式生成）；
  3. 调 director.py 按新时间轴重录无声视频；
  4. 按同一真实时间轴拼整条音轨（含 LEAD、思考静音和完整尾音）；
  5. ffmpeg 合成音视频 → video/samples/<name>-vo.mp4。

无声草片（<name>-draft.mp4）保留：剪映精剪时对轨更灵活。
"""
from __future__ import annotations

import argparse
import array
import hashlib
import json
import math
import subprocess
import sys
import uuid
import wave
from pathlib import Path

from storyboard_lint import load_storyboard

ROOT = Path(__file__).resolve().parents[1]
SAMPLES = Path(__file__).resolve().parent / "samples"
# 口播缓存放项目内而非系统 TEMP：Windows 计划任务每周清 TEMP，
# 缓存丢失会静默回退 TTS 合成（2026-10-12 实证被 cleaner 清掉 24 个文件）
TMP = Path(__file__).parent / ".vo-cache"

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
        await edge_tts.Communicate(text, voice, rate=rate, boundary="WordBoundary").save(
            str(mp3), str(mp3.with_suffix(".words.ndjson")))

    asyncio.run(run())


def mp3_secs(mp3: Path, ff: str) -> tuple[float, Path]:
    wav = mp3.with_suffix(".wav")
    subprocess.run([ff, "-y", "-i", str(mp3), "-ar", "24000", "-ac", "1",
                    str(wav)], check=True, capture_output=True)
    with wave.open(str(wav), "rb") as w:
        return w.getnframes() / w.getframerate(), wav


def word_boundaries(metadata: Path, seconds: float) -> list[dict]:
    """edge-tts 7.3.1 save() 写 NDJSON；offset/duration 是 100ns tick，不是 ms。"""
    try:
        rows = [json.loads(line) for line in metadata.read_text(encoding="utf-8").splitlines()
                if line.strip()]
        words = []
        previous_end = 0.0
        for row in rows:
            if row.get("type") != "WordBoundary":
                continue
            text, offset, duration = row["text"], row["offset"], row["duration"]
            if not isinstance(text, str) or not text.strip():
                raise ValueError("空 WordBoundary 文本")
            if any(isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v)
                   for v in (offset, duration)):
                raise ValueError("WordBoundary 时间必须是有限数字")
            start, end = offset / 10_000_000, (offset + duration) / 10_000_000
            if start < previous_end - 1e-7 or end <= start or end > seconds + 1 / 24000:
                raise ValueError("WordBoundary 逆序、重叠或超出音频")
            words.append({"text": text, "start": start, "end": end})
            previous_end = end
        if not words:
            raise ValueError("没有 WordBoundary，不能把无元数据音频当作精确边界")
        return words
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
        raise ValueError(f"WordBoundary 元数据无效：{metadata}: {exc}") from exc


def cached_voice(text: str, name: str, voice: str, rate: str, ff: str) -> tuple[Path, float, list[dict]]:
    # 版本前缀隔离旧 text-only 缓存；voice/rate/边界模式均参与键，不删除旧音频。
    key = hashlib.sha256(json.dumps(["WordBoundary-v1", voice, rate, text],
                                   ensure_ascii=False).encode("utf-8")).hexdigest()[:20]
    stem = f"{name}-wb1-{key}"
    mp3 = TMP / f"{stem}.mp3"
    for candidate in sorted(TMP.glob(f"{stem}*.mp3")):
        wav, metadata = candidate.with_suffix(".wav"), candidate.with_suffix(".words.ndjson")
        if not wav.is_file() or not metadata.is_file():
            continue
        with wave.open(str(wav), "rb") as wf:
            seconds = wf.getnframes() / wf.getframerate()
        try:
            words = word_boundaries(metadata, seconds)
        except ValueError as exc:
            print(f"  缓存不能提供精确边界，将使用新键重生成：{exc}", file=sys.stderr)
            continue
        return wav, seconds, words
    # 部分缓存也不能覆盖：生成独立新键，完整缓存下次仍可发现和复用。
    if any(mp3.with_suffix(ext).exists() for ext in (".mp3", ".wav", ".words.ndjson")):
        mp3 = TMP / f"{stem}-{uuid.uuid4().hex}.mp3"
    synth(text, mp3, voice, rate)
    seconds, wav = mp3_secs(mp3, ff)
    return wav, seconds, word_boundaries(mp3.with_suffix(".words.ndjson"), seconds)


def stitch_audio(clips: list[tuple[Path, float]], total: float, out: Path) -> None:
    """把完整 24kHz 单声道 PCM 放到绝对秒数；越界报错，绝不静默截掉口播尾。"""
    rate = 24000
    timeline = array.array("h", [0]) * math.ceil(total * rate - 1e-7)
    for wav, start in clips:
        with wave.open(str(wav), "rb") as w:
            if (w.getframerate(), w.getnchannels(), w.getsampwidth()) != (rate, 1, 2):
                raise ValueError(f"拼接要求 24kHz/mono/16-bit PCM：{wav}")
            frames = array.array("h", w.readframes(w.getnframes()))
        offset = round(start * rate)
        if offset < 0 or offset + len(frames) > len(timeline):
            raise ValueError(f"音频超出时间轴，拒绝截尾：{wav}")
        for k, value in enumerate(frames, offset):
            timeline[k] = max(-32768, min(32767, timeline[k] + value))
    with wave.open(str(out), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(timeline.tobytes())


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--shots", required=True, help="分镜 JSON（含 voice 字段）")
    ap.add_argument("--size", choices=["vertical", "horizontal"], default="vertical")
    ap.add_argument("--voice", default=VOICE)
    ap.add_argument("--rate", default=RATE)
    ap.add_argument("--no-render", action="store_true",
                    help="只测口播时长与时间轴，不出片")
    ap.add_argument("--audio-only", action="store_true",
                    help="Remotion 管线：只出 timeline + narration.wav + vo-narr.wav，"
                         "跳过 director.py 逐帧渲染（等效 master.py 的 vo-narr 解码步骤）")
    args = ap.parse_args()

    board = load_storyboard(args.shots)
    name = board["name"]
    # 下载前验证整张分镜，避免后幕无效时前幕已联网。
    for i, shot in enumerate(board["shots"], 1):
        for field in ("voice", "answerVoice"):
            if not isinstance(shot.get(field, ""), str):
                raise ValueError(f"幕{i}: {field} 必须是字符串")
        if shot.get("answerVoice", "").strip():
            if shot.get("view") != "quiz":
                raise ValueError(f"幕{i}: 只有 view: quiz 允许 answerVoice")
            think = shot.get("thinkSeconds", 2.0)
            if isinstance(think, bool) or not isinstance(think, (int, float)) \
                    or not math.isfinite(think) or think < 0:
                raise ValueError(f"幕{i}: thinkSeconds 必须为非负有限秒数")
    ff = ffmpeg_exe()
    TMP.mkdir(exist_ok=True)
    if not args.audio_only and not args.no_render:
        # 仅重渲染时清陈旧产物：失败时绝不让 master 把新字幕烧到旧视频上（试点实测踩过）
        _sf = "" if args.size == "vertical" else "-h"
        for stale in (SAMPLES / f"{name}-draft{_sf}.mp4", SAMPLES / f"{name}-vo{_sf}.mp4"):
            stale.unlink(missing_ok=True)

    # 1) 逐镜配音 + 2) 时间轴对齐。question/answer 保持独立文本与音频。
    clips, adjusted = [], []
    total_voice, shot_offset = 0.0, 0.0
    for i, shot in enumerate(board["shots"], 1):
        current = {**shot, "speech": []}
        cursor, spoken_seconds = LEAD, 0.0
        has_answer = bool(shot.get("answerVoice", "").strip())
        for field in ("voice", "answerVoice"):
            if field == "answerVoice" and has_answer:
                cursor += shot.get("thinkSeconds", 2.0)
                # revealAt 就是答案 PCM 起点，不是答案第一个词或按幕长猜出的比例。
                current["revealAt"] = cursor
            text = shot.get(field, "")
            if not text.strip():
                continue
            wav, seconds, words = cached_voice(text, f"{name}-{i}-{field}", args.voice, args.rate, ff)
            clips.append((wav, shot_offset + cursor))
            current["speech"].extend({"text": word["text"],
                                      "start": round(cursor + word["start"], 7),
                                      "end": round(cursor + word["end"], 7)} for word in words)
            cursor += seconds
            spoken_seconds += seconds
        if spoken_seconds:
            # 向上取两位，不四舍五入截掉不足 0.01s 的尾音/TAIL。
            current["seconds"] = max(shot["seconds"], math.ceil((cursor + TAIL) * 100 - 1e-9) / 100)
            print(f"  幕{i}: 口播 {spoken_seconds:.1f}s → 幕长 {current['seconds']}s")
        else:
            print(f"  幕{i}: 无口播，保留 {shot['seconds']}s")
        adjusted.append(current)
        shot_offset += current["seconds"]
        total_voice += spoken_seconds
    board["shots"] = adjusted
    total = sum(s["seconds"] for s in board["shots"])
    print(f"口播合计 {total_voice:.1f}s → 成片 {total:.1f}s")

    adjusted_file = SAMPLES / f"{name}-timeline.json"
    adjusted_file.write_text(json.dumps(board, ensure_ascii=False), encoding="utf-8")
    if args.no_render:
        return 0

    # 3) 按新时间轴重录无声视频（--audio-only 跳过：Remotion 管线不用 director 成片）
    if not args.audio_only:
        print("渲染视频…")
        subprocess.run([sys.executable, str(Path(__file__).parent / "director.py"),
                        "--shots", str(adjusted_file), "--size", args.size],
                       check=True)
        suffix = "" if args.size == "vertical" else "-h"
        silent = SAMPLES / f"{name}-draft{suffix}.mp4"

    # 4) 按相同真实 offset 拼整条音轨（包括 LEAD 和 quiz 思考静音）。
    print("拼音轨…")
    narration = TMP / f"{name}-narration.wav"
    stitch_audio(clips, total, narration)

    if args.audio_only:
        # Remotion 管线入口：等效 master.py 的 vo-narr 解码（44.1k 单声道 wav）
        out = SAMPLES / f"{name}-vo-narr.wav"
        subprocess.run([ff, "-y", "-i", str(narration), "-ar", "44100", "-ac", "1", str(out)],
                       check=True, capture_output=True)
        print(f"音轨已就绪：{out.name}（{total:.1f}s）——下一步 make_subs.py / remix.py")
        return 0

    # 5) 合成：视频流直拷（director 已出 CRF12 高质中间片，不二次压缩），只封 AAC 音轨
    suffix = "" if args.size == "vertical" else "-h"
    out = SAMPLES / f"{name}-vo{suffix}.mp4"
    subprocess.run([ff, "-y", "-i", str(silent), "-i", str(narration),
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "128k", "-shortest", str(out)],
                   check=True, capture_output=True)
    print(f"带配音成片：{out.name}（{out.stat().st_size / 1048576:.1f}MB）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

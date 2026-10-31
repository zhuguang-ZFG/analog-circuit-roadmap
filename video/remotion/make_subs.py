#!/usr/bin/env python3
"""从当前 timeline 重建字幕，不以旧 subs.json 为文本源。

有 speech：按真实 WordBoundary 分窗；quiz 问题/答案独立，字幕不跨思考静音。
输出 {from,to,text,env,charFrames}：from/to 是全片 30fps 帧区间 [from,to)，
charFrames 是去换行后的每个 Unicode 字符相对 from 的点亮帧。
同一词内字符同时点亮，标点继承邻字；无法对齐报错，不伪造逐字时间。
无 speech 的旧素材：保留比例分窗与 10ms RMS/21 分位 env 兼容路径。
新旧字幕均保留 env，但新字幕高亮应优先消费 charFrames，而非靠能量猜词。

用法: python make_subs.py <ep-name>   (读 video/samples/<ep>-vo-narr.wav)
"""
import json
import math
import sys
import wave
import array
import unicodedata
from pathlib import Path

import numpy as np

ROOT = Path(__file__).parent.parent  # video/
SAMPLES = ROOT / "samples"
DATA = Path(__file__).parent / "public" / "data"
FPS = 30
Q = 20  # 分位点数-1


def envelope_quantiles(pcm: np.ndarray, sr: int, t0: float, t1: float) -> list[float]:
    """[t0,t1] 秒窗口内的能量 21 分位（窗口时间比例 0..1）。"""
    a, b = int(t0 * sr), min(int(t1 * sr), len(pcm))
    if b - a < sr * 0.05:
        return [i / Q for i in range(Q + 1)]
    seg = pcm[a:b]
    hop = int(sr * 0.01)  # 10ms
    n = len(seg) // hop
    rms = np.sqrt((seg[: n * hop].reshape(n, hop) ** 2).mean(axis=1))
    # 去底噪（中位数），防静音段累积虚假能量
    floor = np.median(rms)
    e = np.clip(rms - floor * 1.2, 0, None)
    # 削爆音：单个爆破音 hop 的 RMS 可达语音 16 倍，会把分位曲线坍缩成跳变
    nz = e[e > 0]
    if len(nz):
        e = np.minimum(e, np.percentile(nz, 92))
    # 3-hop 平滑，防爆音抖动
    e = np.convolve(e, np.ones(3) / 3, mode="same")
    cum = np.cumsum(e)
    total = cum[-1]
    if total <= 1e-9:  # 全静音 chunk：退回线性
        return [i / Q for i in range(Q + 1)]
    cum /= total
    out = []
    for q in range(Q + 1):
        idx = int(np.searchsorted(cum, q / Q, side="left"))
        idx = min(idx, n - 1)
        out.append(round(idx * hop / len(seg), 4))
    # 单调性兜底（searchsorted 边界）
    for i in range(1, len(out)):
        out[i] = max(out[i], out[i - 1])
    return out


def spoken_char(char: str) -> bool:
    """标点/空白不要求单独发音；数字、CJK、扩展 Unicode 字符均按 code point 对齐。"""
    return not char.isspace() and not unicodedata.category(char).startswith("P")


def align_characters(text: str, words: list[dict]) -> list[tuple[float, float]]:
    """逐字绑定真实词边界，不在多字词内部线性猜时间；标点继承相邻字。"""
    source = [i for i, char in enumerate(text) if spoken_char(char)]
    letters, times = [], []
    for word in words:
        for char in word["text"]:
            if spoken_char(char):
                letters.append(char)
                times.append((word["start"], word["end"]))
    expected = "".join(text[i] for i in source)
    actual = "".join(letters)
    if not source or actual != expected:
        raise ValueError(f"speech 无法对齐原文：期望 {expected!r}，边界文本 {actual!r}；请重新生成口播元数据")
    aligned = [None] * len(text)
    for index, timing in zip(source, times):
        aligned[index] = timing
    previous = times[0]  # 行首引号等继承第一个发音字。
    for i, timing in enumerate(aligned):
        if timing is not None:
            previous = timing
        else:
            aligned[i] = previous
    return aligned


def speech_windows(shot: dict, t0: float, chunk_voice, wrap) -> list[dict]:
    """speech 秒数相对幕首；from/to 为全片帧，[from,to)，charFrames 相对 from。"""
    words = shot["speech"]
    if not isinstance(words, list):
        raise ValueError("speech 必须是词边界数组")
    previous_end = 0.0
    for word in words:
        if not isinstance(word, dict) or not isinstance(word.get("text"), str):
            raise ValueError("speech 边界缺少 text")
        start, end = word.get("start"), word.get("end")
        if any(isinstance(v, bool) or not isinstance(v, (float, int)) or not math.isfinite(v)
               for v in (start, end)):
            raise ValueError("speech 边界时间必须是有限秒数")
        if start < previous_end - 1e-7 or end <= start or end > shot["seconds"] + 1e-7:
            raise ValueError("speech 边界逆序、重叠或超出幕长")
        previous_end = end

    voice, answer = shot.get("voice", ""), shot.get("answerVoice", "")
    if not isinstance(voice, str) or not isinstance(answer, str):
        raise ValueError("speech 对齐要求 voice/answerVoice 为字符串")
    groups = [(voice, words)]
    if answer.strip():
        reveal, think = shot.get("revealAt"), shot.get("thinkSeconds", 2.0)
        if shot.get("view") != "quiz":
            raise ValueError("speech: 只有 quiz 允许 answerVoice")
        if any(isinstance(v, bool) or not isinstance(v, (float, int)) or not math.isfinite(v)
               or v < 0 for v in (reveal, think)) or reveal > shot["seconds"]:
            raise ValueError("speech: quiz 需要有效 revealAt/thinkSeconds")
        question_words = [w for w in words if w["start"] < reveal]
        answer_words = [w for w in words if w["start"] >= reveal]
        if any(w["end"] > reveal - think + 1e-7 for w in question_words):
            raise ValueError("speech: 问题边界侵入 thinkSeconds 思考静音")
        groups = [(voice, question_words), (answer, answer_words)]

    subs = []
    for original, group_words in groups:
        # 原稿换行不是显示字符，重新交由产线 wrap 控制两行。
        text = original.replace("\r", "").replace("\n", "")
        if not text.strip() and not group_words:
            continue
        timings = align_characters(text, group_words)
        chunks = []
        consumed = 0
        for chunk in chunk_voice(text):
            # chunk_voice 可能滤掉纯空白/把闭引号切成独立块，保留原文并归回相邻块。
            index = text.find(chunk, consumed)
            if index < 0 or text[consumed:index].strip():
                raise ValueError("speech 切句无法对齐原文")
            end_index = index + len(chunk)
            chunk = text[consumed:index] + chunk
            consumed = end_index
            if chunks and not any(spoken_char(c) for c in chunk):
                chunks[-1] += chunk
            else:
                chunks.append(chunk)
        if not chunks or text[consumed:].strip():
            raise ValueError("speech 切句遗失原文")
        chunks[-1] += text[consumed:]
        cursor = 0
        for chunk in chunks:
            character_times = timings[cursor:cursor + len(chunk)]
            cursor += len(chunk)
            spoken = [i for i, char in enumerate(chunk) if spoken_char(char)]
            if not spoken:
                raise ValueError("speech 字幕块没有发音字符，无法确定词边界")
            first_spoken, last_spoken = spoken[0], spoken[-1]
            first, last = character_times[first_spoken][0], character_times[last_spoken][1]
            # 分窗只看发音字；句首空白/引号归本窗首词，不能继承上一窗的时间。
            character_times[:first_spoken] = [character_times[first_spoken]] * first_spoken
            # ceil 保证展示帧的采样时刻不早于开口，不在思考静音内残留字幕。
            start_frame = math.ceil((t0 + first) * FPS - 1e-7)
            end_frame = math.ceil((t0 + last) * FPS - 1e-7)
            if end_frame <= start_frame:
                raise ValueError("speech 字幕窗口不足一帧，无法提供精确高亮")
            wrapped = wrap(chunk)
            if len(wrapped.split("\n")) > 2:
                raise ValueError("speech 字幕折行超过两行，请缩短口播分句")
            if subs and start_frame < subs[-1]["to"]:
                raise ValueError("speech 词边界跨越切句，无法生成不重叠字幕；请调整分句")
            char_frames = [min(end_frame - start_frame - 1,
                               max(0, math.ceil((t0 + start) * FPS - 1e-7) - start_frame))
                           for start, _ in character_times]
            subs.append({"from": start_frame, "to": end_frame, "text": wrapped,
                         "charFrames": char_frames})
    return subs


def build_windows(name: str) -> list[dict]:
    """每次按当前 timeline 重建；有 speech 用词边界，无 speech 保留旧素材比例窗口。"""
    sys.path.insert(0, str(ROOT))
    from master import chunk_voice, wrap  # noqa: PLC0415 —— 复用产线同源切句
    board = json.loads((SAMPLES / f"{name}-timeline.json").read_text(encoding="utf-8"))
    subs: list[dict] = []
    t0 = 0.0
    for index, shot in enumerate(board["shots"], 1):
        dur = shot["seconds"]
        text = shot.get("voice", "")
        if "speech" in shot:
            try:
                subs.extend(speech_windows(shot, t0, chunk_voice, wrap))
            except ValueError as exc:
                raise ValueError(f"{name} 幕{index}: {exc}") from exc
        elif text:
            chunks = chunk_voice(text)
            total_chars = sum(len(c) for c in chunks)
            speakable = max(dur - 0.35, 0.5)
            clock = t0 + 0.2
            for chunk in chunks:
                share = speakable * len(chunk) / total_chars
                end = min(clock + share, t0 + dur - 0.1)
                subs.append({"from": round(clock * FPS), "to": round(end * FPS), "text": wrap(chunk)})
                clock += share
        t0 += dur
    return subs

def main() -> int:
    name = sys.argv[1] if len(sys.argv) > 1 else "ep04-divider"
    subs_p = DATA / f"{name.split('-')[0]}-subs.json"
    # 旧字幕是输出，不是文本源；改稿后必须重新切句、对齐并计算包络。
    subs = build_windows(name)
    with wave.open(str(SAMPLES / f"{name}-vo-narr.wav"), "rb") as w:
        sr = w.getframerate()
        pcm = np.array(array.array("h", w.readframes(w.getnframes())), dtype=np.float64) / 32767
    for s in subs:
        s["env"] = envelope_quantiles(pcm, sr, s["from"] / FPS, s["to"] / FPS)
    subs_p.write_text(json.dumps(subs, ensure_ascii=False), encoding="utf-8")
    # 同步 src/data 副本（TS import 用）
    (Path(__file__).parent / "src" / "data" / subs_p.name).write_text(
        json.dumps(subs, ensure_ascii=False), encoding="utf-8"
    )
    print(f"{len(subs)} 个字幕块已注入能量分位 → {subs_p.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

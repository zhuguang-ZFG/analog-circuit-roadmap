#!/usr/bin/env python3
"""字幕卡拉OK包络注入：给 epNN-subs.json 的每个 chunk 计算真实口播能量分位曲线。

问题：字幕扫字若按字数线性均摊，数字/逗号/停顿都会让扫字与真人发音脱节
（逗号不发音却占扫字时间 → 扫字滞后；chunk 首尾静音 → 扫字抢跑）。
做法：对每个 chunk 窗口内的口播 wav 做 10ms RMS 包络 → 累计能量 →
21 个分位点（能量达到 0%/5%/…/100% 时的窗口内时间比例）。前端扫字时，
第 k 字在 progress ≥ env 分位((k+0.5)/N) 时点亮。静音段不产能量 → 不占扫字时间，
数字念得快慢被真实录进曲线 —— 扫字天然跟嘴。

用法: python make_subs.py <ep-name>   (读 video/samples/<ep>-vo-narr.wav)
"""
import json
import sys
import wave
import array
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


def build_windows(name: str) -> list[dict]:
    """字幕窗口生成（master.py subtitle_filters 同款逻辑，无 drawtext 化的 JSON 版）：
    幕内 chunk_voice 切句 → wrap 折行 → 按字数比例分窗（幕首 0.2s 起、尾 0.1s 止）。"""
    sys.path.insert(0, str(ROOT))
    from master import chunk_voice, wrap  # noqa: PLC0415 —— 复用产线同源切句
    board = json.loads((SAMPLES / f"{name}-timeline.json").read_text(encoding="utf-8"))
    subs: list[dict] = []
    t0 = 0.0
    for shot in board["shots"]:
        dur = shot["seconds"]
        text = shot.get("voice", "")
        if text:
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
    subs = json.loads(subs_p.read_text(encoding="utf-8")) if subs_p.is_file() else build_windows(name)
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

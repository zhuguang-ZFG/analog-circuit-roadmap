#!/usr/bin/env python3
"""程序化 BGM：平和钢琴垫循环（零素材、零版权）。

编曲（72 BPM，Am–F–C–G，每和弦一小节）：
  - 长音垫 pad：双声部慢起慢收，跨小节 1.5× 交叠，连绵不断
  - 电钢琴琶音 epiano：四分音符疏朗上行，正弦+轻三次泛音，慢衰减
  - 次低音 subbass：根音全音符长鸣，只垫厚度不抢戏
  - 无鼓组——「平和」的核心就是去掉瞬态冲击
混音侧（remix.py）仍做 RMS 匹配：人声 −8dB 上垫 BGM。
"""
import numpy as np

SR = 44100
BPM = 72
BEAT = 60 / BPM               # 一拍秒数 ≈ 0.833s
BAR = 4 * BEAT                # 一小节 ≈ 3.33s

# Am F C G（A 小调流行进行），每和弦 [根, 三, 五]
CHORDS = {
    "Am": ([220.00, 261.63, 329.63], 110.00),
    "F":  ([174.61, 220.00, 261.63], 87.31),
    "C":  ([261.63, 329.63, 392.00], 130.81),
    "G":  ([196.00, 246.94, 293.66], 98.00),
}
PROG = ["Am", "F", "C", "G"]
# 疏朗琶音型：四分音符上行再回落（和弦音索引），第 4 拍休止留气口
ARP = [0, 1, 2, None]


def pad(chord: list, dur: float) -> np.ndarray:
    """柔和长音垫：基频 + 高八度轻泛音，0.9s 慢 attack / 长尾 release。"""
    n = int(dur * SR)
    t = np.arange(n) / SR
    out = np.zeros(n)
    for f in chord:
        out += np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * f * 2 * t)
    env = np.minimum(1, t / 0.9) * np.exp(-t * 0.35)
    return out * env / len(chord) * 0.34


def epiano(f: float, dur: float = 1.1) -> np.ndarray:
    """电钢琴单音：正弦主体 + 轻三次泛音提亮，慢指数衰减，柔柔地消失。"""
    n = int(dur * SR)
    t = np.arange(n) / SR
    sig = np.sin(2 * np.pi * f * t) + 0.25 * np.sin(2 * np.pi * f * 3 * t)
    return sig * np.exp(-t * 3.2) * 0.30


def subbass(root: float, dur: float) -> np.ndarray:
    """次低音长鸣：纯正弦根音，全音符铺底（手机扬声器靠它撑厚度）。"""
    n = int(dur * SR)
    t = np.arange(n) / SR
    env = np.minimum(1, t / 0.5) * np.exp(-t * 0.8)
    return np.sin(2 * np.pi * root * t) * env * 0.30


def make_bgm(duration: float) -> np.ndarray:
    total = np.zeros(int(duration * SR) + SR)

    def drop(seg: np.ndarray, at: float) -> None:
        i0 = int(at * SR)
        e0 = min(i0 + len(seg), len(total))
        if e0 > i0:
            total[i0:e0] += seg[:e0 - i0]

    pos = 0.0
    bar_i = 0
    while pos < duration:
        name = PROG[bar_i % len(PROG)]
        chord, root = CHORDS[name]
        # 长音垫跨小节交叠（1.6× 小节长），消除和弦接缝
        drop(pad(chord, min(BAR * 1.6, duration - pos) + 0.05), pos)
        # 次低音全音符
        drop(subbass(root, min(BAR, duration - pos)), pos)
        # 疏朗琶音：四分音符，第 4 拍休止
        for b in range(4):
            ci = ARP[b]
            if ci is None:
                continue
            drop(epiano(chord[ci] * 2), pos + b * BEAT)
        pos += BAR
        bar_i += 1
    # 收尾淡出
    fade = int(1.6 * SR)
    total[-fade:] *= np.linspace(1, 0, fade)
    peak = np.max(np.abs(total)) or 1.0
    return total / peak * 0.9


if __name__ == "__main__":
    import sys
    dur = float(sys.argv[1]) if len(sys.argv) > 1 else 30
    out = sys.argv[2] if len(sys.argv) > 2 else "bgm-test.wav"
    import wave
    data = (make_bgm(dur) * 32767 * 0.5).astype(np.int16)
    with wave.open(out, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(data.tobytes())
    print(f"bgm {dur}s -> {out}")

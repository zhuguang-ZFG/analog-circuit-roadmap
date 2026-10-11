#!/usr/bin/env python3
"""程序化 BGM：轻快的 Am-F-C-G 琶音垫乐（零素材、零版权）。

口播干音缺一层「氛围」，平台成片几乎都有 BGM。下载音乐有版权问题，
这里用 numpy 合成一段循环垫乐：柔和铺底和弦 + 八分音符琶音，
96 BPM、A 小调流行进行，混音时压到口播之下（master.py 负责）。
音色刻意保守——它是氛围，不是主角。
"""
import numpy as np

SR = 44100
BPM = 96
BAR = 4 * 60 / BPM            # 一小节秒数（4 拍）

# Am F C G（A 小调流行进行），每和弦用 [根, 三, 五] 与高八度琶音位
CHORDS = {
    "Am": [220.00, 261.63, 329.63],
    "F":  [174.61, 220.00, 261.63],
    "C":  [130.81, 164.81, 196.00],
    "G":  [196.00, 246.94, 293.66],
}
PROG = ["Am", "F", "C", "G"]


def pad(chord: list, dur: float) -> np.ndarray:
    """柔和铺底：基频 + 八度泛音，慢 attack / 慢 release。"""
    n = int(dur * SR)
    t = np.arange(n) / SR
    out = np.zeros(n)
    for f in chord:
        out += np.sin(2 * np.pi * f * t)
        out += 0.35 * np.sin(2 * np.pi * f * 2 * t)
    env = np.ones(n)
    a = int(0.45 * SR)
    r = int(0.7 * SR)
    env[:a] = np.linspace(0, 1, a) ** 2
    env[-r:] *= np.linspace(1, 0, r) ** 1.5
    return out * env / len(chord) * 0.34


def pluck(f: float, dur: float = 0.24) -> np.ndarray:
    """琶音拨弦：指数衰减正弦。"""
    n = int(dur * SR)
    t = np.arange(n) / SR
    return np.sin(2 * np.pi * f * t) * np.exp(-t * 14) * 0.5


def make_bgm(duration: float) -> np.ndarray:
    total = np.zeros(int(duration * SR) + SR)
    step = BAR / 2                       # 每和弦 2 秒（两拍一半? 一小节一半）
    step = BAR                            # 每和弦一小节
    eighth = BAR / 8
    pos = 0.0
    bar_i = 0
    while pos < duration:
        name = PROG[bar_i % len(PROG)]
        chord = CHORDS[name]
        seg = pad(chord, min(step, duration - pos) + 0.05)
        i0 = int(pos * SR)
        end = min(i0 + len(seg), len(total))
        total[i0:end] += seg[:end - i0]
        # 琶音：每小节 8 个八分音符，循环和弦音（高八度）
        for k in range(8):
            f = chord[k % 3] * 2
            p = pluck(f, 0.24)
            i1 = int((pos + k * eighth) * SR)
            e1 = min(i1 + len(p), len(total))
            if e1 > i1:
                total[i1:e1] += p[:e1 - i1] * 0.5
        pos += step
        bar_i += 1
    # 收尾淡出
    fade = int(1.6 * SR)
    total[-fade:] *= np.linspace(1, 0, fade)
    peak = np.max(np.abs(total)) or 1.0
    return (total / peak * 0.9)


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

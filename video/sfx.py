#!/usr/bin/env python3
"""程序化音效：转场 whoosh / 数字落定 pop / 标题落版 thud。

B 站高播放成片的听觉密度一半来自音效卡点——每个转场、每个数字
落地都有一声。这里用 numpy 合成四种通用音效（零素材零版权），
master.py 按时间轴把它们铺进成片：
  whoosh  转场扫风（噪声 + 上行扫频）
  pop     数字跳数落定（上行啁啾 + 快衰减）
  thud    标题落版低频顿（下坠正弦 + 噪声瞬态）
  ding    口诀/成功提示（双音钟声，备用）
"""
import numpy as np

SR = 44100


def _env(n: int, attack: float = 0.01, decay: float | None = None) -> np.ndarray:
    d = decay if decay is not None else n / SR
    env = np.ones(n)
    a = max(int(attack * SR), 1)
    env[:a] = np.linspace(0, 1, a)
    r = int(min(d, n / SR) * SR)
    env[-r:] *= np.exp(-np.linspace(0, 6, r))
    return env


def whoosh(dur: float = 0.32) -> np.ndarray:
    n = int(dur * SR)
    t = np.arange(n) / SR
    rng = np.random.default_rng(7)
    noise = rng.standard_normal(n)
    # 简易带通：噪声 × 汉宁窗 × 与扫频同形的幅度包络 → 「风」的听感
    window = np.sin(np.pi * t / dur) ** 2
    sweep = np.sin(2 * np.pi * (180 * t + 520 / (2 * dur) * t ** 2))
    out = noise * window * 0.5 + sweep * window * 0.22
    return out * _env(n, 0.02, dur * 0.9) * 0.55


def pop(dur: float = 0.14) -> np.ndarray:
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = 620 + (1250 - 620) * (t / dur)
    out = np.sin(2 * np.pi * f * t) * np.exp(-t * 26)
    return out * 0.6


def ding(dur: float = 0.6) -> np.ndarray:
    n = int(dur * SR)
    t = np.arange(n) / SR
    out = (np.sin(2 * np.pi * 1046.5 * t) + 0.6 * np.sin(2 * np.pi * 1568 * t))
    return out * np.exp(-t * 6) * 0.4


def thud(dur: float = 0.26) -> np.ndarray:
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = 95 - 45 * (t / dur)
    out = np.sin(2 * np.pi * f * t) * np.exp(-t * 16)
    rng = np.random.default_rng(11)
    click = rng.standard_normal(int(0.02 * SR)) * np.linspace(1, 0, int(0.02 * SR))
    out[:len(click)] += click * 0.35
    return out * 0.85


def place(track: np.ndarray, sound: np.ndarray, at: float) -> None:
    i0 = int(at * SR)
    end = min(i0 + len(sound), len(track))
    if end <= i0:
        return
    seg = sound[:end - i0]
    track[i0:end] += seg

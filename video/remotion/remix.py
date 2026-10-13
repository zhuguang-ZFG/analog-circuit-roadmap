#!/usr/bin/env python3
"""重混音（Remotion 管线用）：口播 + SFX 卡点 + BGM，两遍 loudnorm。
BGM 增益按 RMS 实测配比（目标比口播低 8dB——实测 0.16 固定增益听感≈无，
抖音向 BGM 要明显在场），不再用 master.py 的保守值。

用法: python video/remotion/remix.py ep04-divider [out.wav]
"""
import array, json, subprocess, sys, wave
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))
from bgm import make_bgm
from sfx import whoosh, pop, ding, thud, sting, riser, place

S = Path(__file__).parent.parent / "samples"
FF = r"C:/Users/zhugu/scoop/apps/python313/current/Lib/site-packages/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe"
SR = 44100
BGM_DELTA_DB = -8.0  # BGM RMS 目标 = 口播 RMS - 8dB


def main() -> int:
    name = sys.argv[1] if len(sys.argv) > 1 else "ep04-divider"
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(__file__).parent / "public" / "audio" / f"{name}-remix.wav"
    board = json.loads((S / f"{name}-timeline.json").read_text(encoding="utf-8"))
    total = sum(s["seconds"] for s in board["shots"])

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
            place(sfx_track, riser(), max(t0 - 0.75, 0.0))  # 高潮幕前的紧张爬升
            if shot.get("to") == 3.3:
                place(sfx_track, thud(), t0 + 5.5)  # -33% 章砸落
        if shot["type"] == "svg" and shot.get("file") == "divider-loading":
            place(sfx_track, ding(), t0 + 4.4)  # 绿勾落定「完美」
        t0 += shot["seconds"]
    sfx_track = sfx_track[:int(total * SR)] * 0.5

    with wave.open(str(S / f"{name}-vo-narr.wav"), "rb") as w:
        narr = np.array(array.array("h", w.readframes(w.getnframes())), dtype=np.float64) / 32767

    bgm = make_bgm(total)
    # 软压缩：tanh 压瞬态，让鼓点不冒头、平均响度更匀
    bgm = np.tanh(bgm * 1.8) / np.tanh(np.array(1.8))

    rms = lambda x: float(np.sqrt(np.mean(x ** 2)) + 1e-12)
    gain = rms(narr) / rms(bgm) * 10 ** (BGM_DELTA_DB / 20)
    print(f"口播 {20*np.log10(rms(narr)):.1f}dB | BGM {20*np.log10(rms(bgm)):.1f}dB → 增益 {gain:.3f}")

    mix_len = max(len(narr), len(sfx_track), len(bgm))
    mix = np.zeros(mix_len)
    mix[:len(narr)] += narr
    mix[:len(bgm)] += bgm * gain
    mix[:len(sfx_track)] += sfx_track
    peak = float(np.max(np.abs(mix))) or 1.0
    if peak > 0.97:
        mix *= 0.97 / peak

    out.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(out), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((mix * 32767).astype(np.int16).tobytes())

    p1 = subprocess.run([FF, "-i", str(out), "-af", "loudnorm=I=-16:TP=-1.5:LRA=7:print_format=json", "-f", "null", "-"],
                        capture_output=True, text=True)
    stats = json.loads(p1.stderr[p1.stderr.rindex("{"):p1.stderr.rindex("}") + 1])
    ln = (f"loudnorm=I=-16:TP=-1.5:LRA=7:measured_I={stats['input_i']}"
          f":measured_TP={stats['input_tp']}:measured_LRA={stats['input_lra']}"
          f":measured_thresh={stats['input_thresh']}:offset={stats['target_offset']}"
          ":linear=true,aresample=44100")
    tmp = out.with_suffix(".norm.wav")
    subprocess.run([FF, "-y", "-i", str(out), "-af", ln, str(tmp)], check=True, capture_output=True)
    tmp.replace(out)
    print("混音完成:", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

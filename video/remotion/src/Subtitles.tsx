import React from "react";
import {AbsoluteFill, Sequence, useCurrentFrame, useVideoConfig, spring} from "remotion";
import type {SubEntry} from "./episodes";
import {C} from "./theme";

/** 第 k 字（共 N 字）的点亮阈值（窗口时间比例 0..1）：
 *  有 env（口播能量 21 分位，make_subs.py 实测）→ 分位插值，扫字跟嘴；
 *  无 env → 线性兜底。 */
const charThreshold = (k: number, N: number, env?: number[]): number => {
  if (!env || env.length < 2) return (k + 0.5) / N;
  const x = ((k + 0.5) / N) * (env.length - 1);
  const i = Math.min(Math.floor(x), env.length - 2);
  return env[i] + (env[i + 1] - env[i]) * (x - i);
};

const LEAD = 2; // 提前 2 帧点亮——视觉先于听觉一点，同步感最好

/** 字幕托底块：逐块弹入 + 逐字卡拉OK（能量包络驱动）+ 数字/单位琥珀高亮。
 *  窗口由构建期预计算（master.py chunk_voice/wrap 同款逻辑），竖屏 top=1425。 */
const Pill: React.FC<{text: string; dur: number; env?: number[]}> = ({text, dur, env}) => {
  const frame = useCurrentFrame();
  const {fps, width, height} = useVideoConfig();
  const wide = width > height; // 横版 1920×1080：字幕带贴底、字号按 16:9 收一档
  const s = spring({frame, fps, config: {damping: 13, stiffness: 220, mass: 0.7}});
  const lines = text.split("\n");
  const N = lines.join("").length;
  let base = 0;
  return (
    <div style={{position: "absolute", top: wide ? height - 215 : 1425, width: "100%", display: "flex", justifyContent: "center"}}>
      <div
        style={{
          fontFamily: '"ZCOOL KuaiLe","Microsoft YaHei",sans-serif',
          fontSize: wide ? 46 : 57,
          lineHeight: 1.35,
          color: "#fff",
          textAlign: "center",
          whiteSpace: "pre-line",
          background: "rgba(0,0,0,.32)",
          backdropFilter: "blur(4px)",
          WebkitBackdropFilter: "blur(4px)",
          padding: "8px 16px",
          borderRadius: 10,
          opacity: s,
          transform: `scale(${0.92 + s * 0.08})`,
          textShadow:
            "2px 0 0 rgba(0,0,0,.75), -2px 0 0 rgba(0,0,0,.75), 0 2px 0 rgba(0,0,0,.75), 0 -2px 0 rgba(0,0,0,.75), 2px 2px 0 rgba(0,0,0,.75), -2px -2px 0 rgba(0,0,0,.75), 2px -2px 0 rgba(0,0,0,.75), -2px 2px 0 rgba(0,0,0,.75)",
        }}
      >
        {lines.map((ln, li) => {
          const start = base;
          base += ln.length;
          return (
            <div key={li}>
              {[...ln].map((ch, k) => {
                const gk = start + k;
                const on = frame >= charThreshold(gk, N, env) * dur - LEAD;
                const ascii = /[A-Za-z0-9._%Ωµμ\/×=+-]/.test(ch);
                return (
                  <span
                    key={k}
                    style={{
                      color: on ? (ascii ? C.accent : "#fff") : (ascii ? "rgba(255,194,71,.45)" : "rgba(255,255,255,.55)"),
                      transition: "color .08s",
                    }}
                  >
                    {ch}
                  </span>
                );
              })}
            </div>
          );
        })}
      </div>
    </div>
  );
};

export const Subtitles: React.FC<{data: SubEntry[]}> = ({data}) => (
  <AbsoluteFill style={{pointerEvents: "none"}}>
    {data.map((s, i) => (
      <Sequence key={i} from={s.from} durationInFrames={Math.max(s.to - s.from, 1)}>
        <Pill text={s.text} dur={s.to - s.from} env={s.env} />
      </Sequence>
    ))}
  </AbsoluteFill>
);

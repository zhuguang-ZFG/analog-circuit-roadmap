import React from "react";
import {useCurrentFrame, useVideoConfig, spring, interpolate} from "remotion";
import {C, FONT_MAIN} from "../theme";

/** 琥珀渐变关键词：落定后弹一下（对应 CSS hlPop），帧驱动。
 *  纵向渐变 + 柔光——比单色平涂更有「发光元件」感。 */
export const HlKeyword: React.FC<{popAt: number; children: React.ReactNode}> = ({popAt, children}) => {
  const frame = useCurrentFrame();
  const t = frame - popAt;
  const scale = t < 0 || t > 15 ? 1 : 1 + 0.18 * Math.sin((t / 15) * Math.PI);
  return (
    <span
      style={{
        display: "inline-block",
        transform: `scale(${scale})`,
        backgroundImage: "linear-gradient(180deg,#ffe08a 20%,#ffb347 90%)",
        WebkitBackgroundClip: "text",
        backgroundClip: "text",
        WebkitTextFillColor: "transparent",
        color: C.accent,
        filter: "drop-shadow(0 2px 10px rgba(255,194,71,.35))",
      }}
    >
      {children}
    </span>
  );
};

/** 逐字弹入（保留 **强调** 标记）：每字错峰 spring + 微旋转，
 *  比逐行入场更「活」——抖音信息卡的通行做法。 */
export const CascadeText: React.FC<{delay: number; popAt: number; children: string}> = ({delay, popAt, children}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  // 拆成 (字, 是否高亮) 序列
  const segs: Array<{ch: string; hl: boolean}> = [];
  let hl = false;
  for (const piece of children.split("**")) {
    for (const ch of piece) segs.push({ch, hl});
    hl = !hl;
  }
  return (
    <>
      {segs.map((s, i) => {
        const sp = spring({frame: frame - delay - i * 1.05, fps, config: {damping: 15, stiffness: 290, mass: 0.5}});
        const t = frame - popAt;
        const hlScale = s.hl && t >= 0 && t <= 15 ? 1 + 0.18 * Math.sin((t / 15) * Math.PI) : 1;
        return (
          <span
            key={i}
            style={{
              display: "inline-block",
              color: s.hl ? C.accent : undefined,
              opacity: sp,
              transform: `translateY(${(1 - sp) * 26}px) rotate(${(1 - sp) * -4}deg) scale(${sp * hlScale})`,
            }}
          >
            {s.ch === " " ? " " : s.ch}
          </span>
        );
      })}
    </>
  );
};

/** 节拍呼吸：与 BGM 72 BPM 同步的微妙缩放（帧驱动正弦衰减包络）。 */
export const useBeatPulse = (bpm = 72, amp = 0.010): number => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const beat = 60 / bpm;
  const phase = ((frame / fps) % beat) / beat; // 0..1 每拍
  return 1 + amp * Math.exp(-phase * 7);       // 击拍瞬间最大，指数回落
};

/** 解析台本里的 **强调** 标记 → HlKeyword（对应 director.py hl()） */
export function parseHl(text: string, popAt: number): React.ReactNode {
  const parts = text.split(/\*\*(.+?)\*\*/g);
  return parts.map((p, i) =>
    i % 2 === 1 ? (
      <HlKeyword key={i} popAt={popAt}>
        {p}
      </HlKeyword>
    ) : (
      <React.Fragment key={i}>{p}</React.Fragment>
    )
  );
}

/** 逐行错峰上滑入场（spring），对应 CSS rise 动画 */
export const RiseLine: React.FC<{delay: number; fontSize: number; children: React.ReactNode}> = ({
  delay,
  fontSize,
  children,
}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const s = spring({frame: frame - delay, fps, config: {damping: 15, stiffness: 120, mass: 0.9}});
  const ty = interpolate(s, [0, 1], [46, 0]);
  return (
    <div
      style={{
        color: C.ink,
        fontWeight: 800,
        lineHeight: 1.32,
        fontFamily: FONT_MAIN,
        fontSize,
        letterSpacing: ".01em",
        textShadow: "0 6px 30px rgba(10,16,40,.55)",
        opacity: s,
        transform: `translateY(${ty}px)`,
      }}
    >
      {children}
    </div>
  );
};

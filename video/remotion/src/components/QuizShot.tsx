import React from "react";
import {AbsoluteFill, useCurrentFrame, useVideoConfig, interpolate, spring} from "remotion";
import {C, FONT_MAIN} from "../theme";
import {ShotShell} from "./ShotShell";

export const quizRevealFrame = (durFrames: number, fps: number, revealAt?: number): number =>
  revealAt === undefined ? Math.max(durFrames - 3 * fps, Math.round(durFrames * 0.5)) : Math.round(revealAt * fps);

export const QuizShot: React.FC<{
  durFrames: number;
  q: string;
  options?: string[];
  answer?: number;
  explain?: string;
  revealAt?: number;
}> = ({durFrames, q, options = [], answer = 0, explain, revealAt}) => {
  const frame = useCurrentFrame();
  const {fps, width, height} = useVideoConfig();
  const wide = width > height;
  const revealF = quizRevealFrame(durFrames, fps, revealAt);
  const revealed = frame >= revealF;
  const popT = frame - revealF;
  const head = spring({frame, fps, config: {damping: 14, stiffness: 200}});
  const tick = revealF === 0 ? 0 : interpolate(frame, [0, revealF], [1, 0], {extrapolateLeft: "clamp", extrapolateRight: "clamp"});
  const hasOpts = options.length > 0;

  return (
    <ShotShell durFrames={durFrames}>
      <AbsoluteFill
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          paddingTop: wide ? 150 : 230,
          paddingInline: wide ? 140 : 70,
          fontFamily: FONT_MAIN,
        }}
      >
      <div
        style={{
          fontSize: wide ? 30 : 36,
          color: C.eyebrow,
          letterSpacing: 6,
          opacity: head,
          transform: `translateY(${(1 - head) * 18}px)`,
        }}
      >
        ⏸ 暂停 · 猜一猜
      </div>
      <div
        style={{
          marginTop: 46,
          fontSize: wide ? 52 : 62,
          lineHeight: 1.42,
          color: C.ink,
          textAlign: "center",
          fontWeight: 700,
          opacity: head,
          textShadow: "0 4px 24px rgba(0,0,0,.45)",
        }}
      >
        {q}
      </div>

      {hasOpts &&
        options.map((opt, i) => {
          const s = spring({frame: frame - i * 8 - 14, fps, config: {damping: 13, stiffness: 210}});
          const isAns = i === answer;
          const win = revealed && isAns;
          return (
            <div
              key={i}
              style={{
                marginTop: i === 0 ? (wide ? 42 : 84) : (wide ? 18 : 26),
                width: wide ? 1180 : 880,
                minHeight: wide ? 88 : 108,
                display: "flex",
                alignItems: "center",
                gap: 24,
                paddingInline: 34,
                borderRadius: 18,
                background: win ? "rgba(124,227,200,.14)" : "rgba(255,255,255,.07)",
                border: win ? `3px solid ${C.good}` : "2px solid rgba(255,255,255,.16)",
                opacity: s * (revealed && !isAns ? 0.35 : 1),
                transform: `scale(${s * (win && popT < 10 ? 1.04 : 1)})`,
              }}
            >
              <span
                style={{
                  flexShrink: 0,
                  width: wide ? 52 : 60,
                  height: wide ? 52 : 60,
                  borderRadius: "50%",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontSize: wide ? 28 : 32,
                  color: win ? "#0b2b22" : C.accent,
                  background: win ? C.good : "rgba(255,194,71,.16)",
                }}
              >
                {win ? "✓" : "ABC"[i]}
              </span>
              <span style={{fontSize: wide ? 40 : 46, color: C.ink}}>{opt}</span>
            </div>
          );
        })}

      <div
        style={{
          marginTop: hasOpts ? (wide ? 32 : 64) : 90,
          width: wide ? 640 : 560,
          height: 10,
          borderRadius: 5,
          background: "rgba(255,255,255,.12)",
          overflow: "hidden",
          opacity: revealed ? 0 : 1,
        }}
      >
        <div style={{width: `${tick * 100}%`, height: "100%", background: C.accent, borderRadius: 5}} />
      </div>

      {explain && hasOpts && (
        <div
          style={{
            marginTop: wide ? 30 : 54,
            maxWidth: wide ? 1100 : 860,
            fontSize: wide ? 32 : 38,
            lineHeight: 1.5,
            color: C.sub,
            textAlign: "center",
            opacity: revealed ? interpolate(popT, [4, 20], [0, 1], {extrapolateLeft: "clamp", extrapolateRight: "clamp"}) : 0,
            transform: `translateY(${revealed ? interpolate(popT, [4, 20], [14, 0], {extrapolateLeft: "clamp", extrapolateRight: "clamp"}) : 10}px)`,
          }}
        >
          {explain}
        </div>
      )}
      </AbsoluteFill>
    </ShotShell>
  );
};

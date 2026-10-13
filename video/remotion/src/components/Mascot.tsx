import React from "react";
import {useCurrentFrame, useVideoConfig, spring, interpolate} from "remotion";

const INK = "#0f1830";
const BLUSH = "#ff9d84";

/** 「小电」电子小人——从 director.py mascot() 逐像素移植，CSS 动画改帧驱动。 */
export const Mascot: React.FC<{mood?: string; width?: number}> = ({mood = "happy", width = 170}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  // bob 浮动（2.2s 周期）+ 眨眼（3s 周期，94% 处瞬闭）
  const bob = Math.sin((frame / fps) * ((2 * Math.PI) / 2.2)) * 6;
  const rot = Math.sin((frame / fps) * ((2 * Math.PI) / 2.2)) * -2;
  const blinkPhase = ((frame / fps) % 3) / 3;
  const eyeScale = blinkPhase > 0.94 ? 0.08 : 1;
  // wave 挥手 / cheer 欢呼
  const waveRot = mood === "wave" ? interpolate(Math.sin((frame / fps) * Math.PI * 2 * 0.9), [-1, 1], [-14, 16]) : 0;
  const cheerHop = mood === "cheer" ? Math.abs(Math.sin((frame / fps) * Math.PI * 2 * 0.55)) * -14 : 0;
  const cheerRot = mood === "cheer" ? Math.sin((frame / fps) * Math.PI * 2 * 0.55) * 3 : 0;

  const gradId = `mg-${mood}`;

  const brows = mood === "shocked" ? (
    <>
      <path d="M38 50 L54 46" stroke={INK} strokeWidth={4} strokeLinecap="round" />
      <path d="M82 50 L66 46" stroke={INK} strokeWidth={4} strokeLinecap="round" />
    </>
  ) : null;

  const eyes = mood === "shocked" ? (
    <>
      <circle cx={46} cy={64} r={7.5} fill={INK} />
      <circle cx={74} cy={64} r={7.5} fill={INK} />
      <circle cx={48.5} cy={61.5} r={2.6} fill="#fff" />
      <circle cx={76.5} cy={61.5} r={2.6} fill="#fff" />
    </>
  ) : mood === "cheer" ? (
    <g style={{transform: `scaleY(${eyeScale})`, transformOrigin: "60px 64px"}}>
      <path d="M40 64 Q46 58 52 64" stroke={INK} strokeWidth={4} fill="none" strokeLinecap="round" />
      <path d="M68 64 Q74 58 80 64" stroke={INK} strokeWidth={4} fill="none" strokeLinecap="round" />
    </g>
  ) : (
    <g style={{transform: `scaleY(${eyeScale})`, transformOrigin: "60px 64px"}}>
      <circle cx={46} cy={64} r={6.5} fill={INK} />
      <circle cx={74} cy={64} r={6.5} fill={INK} />
      <circle cx={48.5} cy={61.5} r={2.3} fill="#fff" />
      <circle cx={76.5} cy={61.5} r={2.3} fill="#fff" />
    </g>
  );

  const mouth =
    mood === "shocked" ? (
      <ellipse cx={60} cy={90} rx={9} ry={12} fill={INK} />
    ) : mood === "cheer" ? (
      <path d="M47 85 Q60 103 73 85 Q60 93 47 85 Z" fill={INK} />
    ) : (
      <path d={`M49 87 Q60 ${mood === "happy" ? 96 : 92} 71 87`} stroke={INK} strokeWidth={4} fill="none" strokeLinecap="round" />
    );

  const arm =
    mood === "cheer" ? (
      <g>
        <path d="M99 78 Q114 70 116 50" stroke={INK} strokeWidth={6} fill="none" strokeLinecap="round" />
        <circle cx={117} cy={47} r={8} fill="#ffc247" stroke={INK} strokeWidth={3} />
        <path d="M21 78 Q6 70 4 50" stroke={INK} strokeWidth={6} fill="none" strokeLinecap="round" />
        <circle cx={3} cy={47} r={8} fill="#ffc247" stroke={INK} strokeWidth={3} />
      </g>
    ) : mood === "wave" ? (
      <g style={{transform: `rotate(${waveRot}deg)`, transformOrigin: "97px 74px"}}>
        <path d="M97 74 Q116 62 112 42" stroke={INK} strokeWidth={6} fill="none" strokeLinecap="round" />
        <circle cx={112} cy={40} r={8} fill="#ffc247" stroke={INK} strokeWidth={3} />
      </g>
    ) : (
      <circle cx={102} cy={82} r={8} fill="#ffc247" stroke={INK} strokeWidth={3} />
    );

  const leftArm = mood === "cheer" ? null : (
    <circle cx={18} cy={82} r={8} fill="#ffc247" stroke={INK} strokeWidth={3} />
  );

  return (
    <div
      style={{
        width,
        transform: `translateY(${bob + cheerHop}px) rotate(${rot + cheerRot}deg)`,
        filter: "drop-shadow(0 10px 22px rgba(10,16,40,.45))",
      }}
    >
      <svg viewBox="0 0 130 132" role="img" aria-label="小电" width="100%">
        <defs>
          <linearGradient id={gradId} x1="0" y1="0" x2="1" y2="1">
            <stop offset="0" stopColor="#5e7aff" />
            <stop offset="1" stopColor="#27357a" />
          </linearGradient>
        </defs>
        <path d="M60 4 L50 20 L59 18 L53 33" fill="none" stroke="#ffc247" strokeWidth={5} strokeLinecap="round" strokeLinejoin="round" />
        <circle cx={60} cy={76} r={46} fill={`url(#${gradId})`} stroke={INK} strokeWidth={4} />
        <ellipse cx={30} cy={92} rx={9} ry={6} fill="#fff" opacity={0.25} />
        {brows}
        {eyes}
        <ellipse cx={33} cy={84} rx={8} ry={5} fill={BLUSH} opacity={0.6} />
        <ellipse cx={87} cy={84} rx={8} ry={5} fill={BLUSH} opacity={0.6} />
        {mouth}
        {leftArm}
        {arm}
      </svg>
    </div>
  );
};

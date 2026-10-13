import React from "react";
import {AbsoluteFill, useCurrentFrame, useVideoConfig, interpolate, spring} from "remotion";
import {ShotShell} from "./ShotShell";
import {Mascot} from "./Mascot";
import {parseHl} from "./anim";
import {C, FONT_MAIN} from "../theme";

/** 数字卡（对应 num 模板）：from → to 跳数（1.5s ease-out 三次方），落定弹跳+辉光，
 *  可选缩减条（bar: [满, 剩]）。对应 runCounts / barShrink / pop / countGlow。 */
export const NumShot: React.FC<{
  durFrames: number;
  from: number;
  to: number;
  unit: string;
  dec?: number;
  sub?: string;
  bar?: [number, number];
  mascot?: string;
}> = ({durFrames, from, to, unit, dec = 1, sub, bar, mascot}) => {
  const frame = useCurrentFrame();
  const {fps, width, height} = useVideoConfig();
  const wide = width > height; // 横版：吉祥物上移避开底部字幕带
  const D = 45; // 1.5s @30fps
  const p = Math.min(frame / D, 1);
  const e = 1 - Math.pow(1 - p, 3);
  const val = (from + (to - from) * e).toFixed(dec);
  const landed = p >= 1;
  // 落定弹跳（pop .4s: 1→1.24→1）
  const popT = frame - D;
  const pop = popT < 0 || popT > 12 ? 1 : 1 + 0.24 * Math.sin((popT / 12) * Math.PI);
  // 落定辉光呼吸
  const glow = landed ? 0.5 + 0.5 * Math.sin((frame / fps) * Math.PI * 2 * 1.1) : 0;
  const inSpring = spring({frame, fps, config: {damping: 15, stiffness: 110}});
  const barW = bar ? interpolate(frame, [0, durFrames], [1, bar[0] ? bar[1] / bar[0] : 1], {extrapolateRight: "clamp"}) : 1;

  return (
    <ShotShell durFrames={durFrames}>
      <AbsoluteFill style={{flexDirection: "column", justifyContent: "center", alignItems: "center", padding: 60, display: "flex"}}>
        <div
          style={{
            display: "flex",
            alignItems: "baseline",
            gap: 26,
            fontFamily: FONT_MAIN,
            opacity: inSpring,
            transform: `translateY(${interpolate(inSpring, [0, 1], [40, 0])}px) scale(${pop})`,
          }}
        >
          <span style={{fontSize: 120, color: C.sub, fontWeight: 800}}>{from.toFixed(dec)}</span>
          <span style={{fontSize: 50, color: C.sub}}>{unit}</span>
          <span style={{fontSize: 72, color: C.accent, fontWeight: 800}}>→</span>
          <span
            style={{
              fontSize: 120,
              fontWeight: 800,
              backgroundImage: "linear-gradient(180deg,#ffb08a 15%,#ff6b6b 90%)",
              WebkitBackgroundClip: "text",
              backgroundClip: "text",
              WebkitTextFillColor: "transparent",
              color: C.bad,
              filter: landed
                ? `drop-shadow(0 0 ${20 + glow * 14}px rgba(255,143,107,${0.4 + glow * 0.3}))`
                : "drop-shadow(0 8px 20px rgba(10,16,40,.6))",
            }}
          >
            {val}
          </span>
          <span style={{fontSize: 50, color: C.bad}}>{unit}</span>
        </div>
        {bar ? (
          <div style={{width: 620, height: 18, marginTop: 30, background: "rgba(255,255,255,.14)", borderRadius: 9, overflow: "hidden"}}>
            <div
              style={{
                height: "100%",
                width: "100%",
                transform: `scaleX(${barW})`,
                transformOrigin: "left center",
                background: `linear-gradient(90deg,${C.good},${C.bad})`,
                borderRadius: 9,
              }}
            />
          </div>
        ) : null}
        {sub ? (
          <div style={{marginTop: 34, color: C.sub, fontSize: 30, lineHeight: 1.75, maxWidth: "92%", textAlign: "center", fontFamily: FONT_MAIN}}>
            {parseHl(sub, 55)}
          </div>
        ) : null}
        {mascot ? (
          <div style={{position: "absolute", right: 40, bottom: wide ? 230 : 130}}>
            <Mascot mood={mascot} width={wide ? 120 : 150} />
          </div>
        ) : null}
      </AbsoluteFill>
    </ShotShell>
  );
};

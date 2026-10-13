import React from "react";
import {AbsoluteFill, useCurrentFrame, useVideoConfig, spring, interpolate} from "remotion";
import {ShotShell} from "./ShotShell";
import {Mascot} from "./Mascot";
import {CascadeText, useBeatPulse} from "./anim";
import {C, FONT_MAIN} from "../theme";

/** 标题幕（对应 intro 模板）：吉祥物弹入 + 系列名/集名/进度行错峰上浮 */
export const IntroShot: React.FC<{
  durFrames: number;
  series?: string;
  ep?: string;
  title?: string;
  progress?: string;
}> = ({durFrames, series = "模拟电路动画课", ep = "", title = "", progress = ""}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const pop = spring({frame: frame - 5, fps, config: {damping: 10, stiffness: 160, mass: 0.7}});
  const rise = (delay: number) => {
    const s = spring({frame: frame - delay, fps, config: {damping: 15, stiffness: 120, mass: 0.9}});
    return {opacity: s, transform: `translateY(${interpolate(s, [0, 1], [40, 0])}px)`};
  };
  // 标题强调色下划扫过（对应 sweep）
  const sweep = interpolate(frame, [18, 40], [0, 220], {extrapolateLeft: "clamp", extrapolateRight: "clamp"});
  return (
    <ShotShell durFrames={durFrames}>
      <AbsoluteFill style={{justifyContent: "center", alignItems: "center", gap: 30, display: "flex", flexDirection: "column"}}>
        <div style={{width: 230, transform: `scale(${pop})`}}>
          <Mascot mood="happy" width={230} />
        </div>
        <div
          style={{
            color: C.eyebrow,
            fontSize: 34,
            fontWeight: 800,
            letterSpacing: ".3em",
            textIndent: ".3em",
            ...rise(8),
          }}
        >
          {series}
        </div>
        <div style={{position: "relative", ...rise(14), transform: `${rise(14).transform} scale(${useBeatPulse()})`}}>
          <div style={{fontSize: 52, color: C.ink, fontWeight: 800, fontFamily: FONT_MAIN, textShadow: "0 6px 30px rgba(10,16,40,.55)"}}>
            {ep} · <CascadeText delay={10} popAt={32}>{`**${title}**`}</CascadeText>
          </div>
          <div
            style={{
              position: "absolute",
              left: 0,
              bottom: -10,
              height: 5,
              width: sweep,
              borderRadius: 3,
              background: C.accent,
            }}
          />
        </div>
        <div style={{color: C.sub, fontSize: 30, lineHeight: 1.75, whiteSpace: "nowrap", ...rise(20)}}>{progress}</div>
      </AbsoluteFill>
    </ShotShell>
  );
};

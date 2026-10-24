import React from "react";
import {AbsoluteFill, useCurrentFrame, useVideoConfig, spring, interpolate} from "remotion";
import {ShotShell} from "./ShotShell";
import {Mascot} from "./Mascot";
import {CascadeText} from "./anim";
import {C, FONT_MAIN} from "../theme";

/** 标题幕（对应 intro 模板）：开屏张力优先——白闪入场 + 超大标题渐变发光 + 闪电冲击环，
 *  系列名退居 eyebrow 胶囊。时长/数据不变，只重排视觉层级。 */
export const IntroShot: React.FC<{
  durFrames: number;
  series?: string;
  ep?: string;
  title?: string;
  progress?: string;
}> = ({durFrames, series = "模拟电路动画课", ep = "", title = "", progress = ""}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const pop = spring({frame: frame - 3, fps, config: {damping: 10, stiffness: 180, mass: 0.6}});
  const rise = (delay: number) => {
    const s = spring({frame: frame - delay, fps, config: {damping: 15, stiffness: 140, mass: 0.8}});
    return {opacity: s, transform: `translateY(${interpolate(s, [0, 1], [46, 0])}px)`};
  };
  // 开屏白闪：第 2~7 帧 0.5→0，制造「被抓住」的第一感
  const flash = interpolate(frame, [2, 7], [0.5, 0], {extrapolateLeft: "clamp", extrapolateRight: "clamp"});
  // 标题强调色下划扫过（对应 sweep），随大字更宽
  const sweep = interpolate(frame, [14, 34], [0, 340], {extrapolateLeft: "clamp", extrapolateRight: "clamp"});
  // 闪电冲击环：标题落定瞬间扩散一圈
  const ringT = frame - 12;
  const ringScale = ringT < 0 || ringT > 22 ? (ringT < 0 ? 0.2 : 1.6) : 0.2 + (ringT / 22) * 1.4;
  const ringOp = ringT < 0 || ringT > 22 ? 0 : 0.85 * (1 - ringT / 22);
  const wide = useVideoConfig().width > useVideoConfig().height;
  const titleSize = wide ? 64 : 84;
  return (
    <ShotShell durFrames={durFrames}>
      <AbsoluteFill style={{justifyContent: "center", alignItems: "center", gap: 26, display: "flex", flexDirection: "column"}}>
        {flash > 0 && <AbsoluteFill style={{background: "#fff8ea", opacity: flash}} />}
        <div style={{display: "flex", alignItems: "center", gap: 18, ...rise(2)}}>
          <div style={{width: 120, transform: `scale(${pop})`}}>
            <Mascot mood="shocked" width={120} />
          </div>
          <div
            style={{
              color: C.eyebrow,
              fontSize: 30,
              fontWeight: 800,
              letterSpacing: ".28em",
              textIndent: ".28em",
              opacity: 0.92,
              border: `2px solid ${C.accent}55`,
              borderRadius: 999,
              padding: "10px 26px",
              background: "rgba(10,16,40,.35)",
            }}
          >
            {series}
          </div>
        </div>
        <div style={{position: "relative", textAlign: "center", ...rise(8)}}>
          <div
            style={{
              fontSize: titleSize,
              color: C.ink,
              fontWeight: 800,
              fontFamily: FONT_MAIN,
              letterSpacing: ".02em",
              textShadow: `0 0 26px ${C.accent}66, 0 8px 34px rgba(10,16,40,.6)`,
            }}
          >
            {ep} · <CascadeText delay={6} popAt={26}>{`**${title}**`}</CascadeText>
          </div>
          <div
            style={{
              position: "absolute",
              left: "50%",
              transform: "translateX(-50%)",
              bottom: -14,
              height: 7,
              width: sweep,
              borderRadius: 4,
              background: `linear-gradient(90deg, ${C.accent}, ${C.good})`,
            }}
          />
          {ringOp > 0 && (
            <div
              style={{
                position: "absolute",
                left: "50%",
                top: "50%",
                width: 340,
                height: 340,
                marginLeft: -170,
                marginTop: -170,
                borderRadius: "50%",
                border: `5px solid ${C.accent}`,
                opacity: ringOp,
                transform: `scale(${ringScale})`,
              }}
            />
          )}
        </div>
        <div style={{color: C.sub, fontSize: 30, lineHeight: 1.75, whiteSpace: "nowrap", ...rise(16)}}>{progress}</div>
      </AbsoluteFill>
    </ShotShell>
  );
};

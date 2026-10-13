import React from "react";
import {AbsoluteFill, useCurrentFrame, useVideoConfig, interpolate, spring} from "remotion";
import {ShotShell} from "./ShotShell";
import {Mascot} from "./Mascot";
import {RiseLine, parseHl, CascadeText, useBeatPulse} from "./anim";
import {C, FONT_MAIN} from "../theme";

/** 文字卡（对应 card 模板）：eyebrow + 多行大字（**强调**）+ sub + 吉祥物气泡。
 *  动效：整体 kenburns 慢推、行错峰上浮、关键词落定弹跳、结论条扫入。 */
export const CardShot: React.FC<{
  durFrames: number;
  index: number;
  eyebrow?: string;
  lines?: string[];
  sub?: string;
  chip?: string;
  mascot?: string;
  bubble?: string;
  cta?: string;
}> = ({durFrames, index, eyebrow, lines = [], sub, chip, mascot, bubble, cta}) => {
  const frame = useCurrentFrame();
  const {fps, width, height} = useVideoConfig();
  const wide = width > height; // 横版：吉祥物上移避开底部字幕带
  // 内容区慢推（kenburns 1→1.06），入场 0.6s 后起步
  const kb = interpolate(frame, [18, durFrames], [1, 1.06], {extrapolateLeft: "clamp", extrapolateRight: "clamp"});
  const popAt = 24;
  const beatPulse = useBeatPulse();
  // 吉祥物弹入
  const mPop = spring({frame: frame - 15, fps, config: {damping: 11, stiffness: 170}});
  // 结论条（sub 含 ► 或全句）：扫入
  const subIn = spring({frame: frame - 25, fps, config: {damping: 16}});

  return (
    <ShotShell durFrames={durFrames}>
      <AbsoluteFill
        style={{
          flexDirection: "column",
          justifyContent: "center",
          alignItems: "center",
          textAlign: "center",
          padding: 60,
          display: "flex",
        }}
      >
        {/* 聚焦径向光：卡面主信息背后的深度光 */}
        <div
          style={{
            position: "absolute",
            left: "50%",
            top: "46%",
            width: 1100,
            height: 1100,
            marginLeft: -550,
            marginTop: -550,
            borderRadius: "50%",
            background: "radial-gradient(circle, rgba(94,122,255,.17), transparent 62%)",
            filter: "blur(30px)",
          }}
        />
        <div style={{display: "flex", flexDirection: "column", alignItems: "center", gap: 30, transform: `scale(${kb * beatPulse})`}}>
          {eyebrow ? (
            <RiseLine delay={2} fontSize={26}>
              <span
                style={{
                  color: C.eyebrow,
                  fontSize: 26,
                  letterSpacing: ".3em",
                  fontWeight: 700,
                  border: "1.5px solid rgba(143,165,255,.55)",
                  borderRadius: 999,
                  padding: "7px 24px",
                  paddingLeft: "calc(24px + .3em)",
                  background: "rgba(94,122,255,.10)",
                }}
              >
                {eyebrow}
              </span>
            </RiseLine>
          ) : null}
          {lines.map((ln, i) => (
            <RiseLine key={i} delay={0} fontSize={72}>
              <CascadeText delay={3 + i * 5} popAt={popAt}>{ln}</CascadeText>
            </RiseLine>
          ))}
          {chip ? (
            <div
              style={{
                opacity: subIn,
                transform: `scale(${0.7 + subIn * 0.3})`,
                background: "rgba(255,194,71,.14)",
                border: `2px solid ${C.accent}`,
                borderRadius: 14,
                padding: "10px 26px",
                fontSize: 44,
                fontWeight: 800,
                color: C.accent,
                fontFamily: FONT_MAIN,
              }}
            >
              {chip}
            </div>
          ) : null}
          {sub ? (
            <div
              style={{
                color: C.sub,
                fontSize: 30,
                lineHeight: 1.75,
                maxWidth: "92%",
                opacity: subIn,
                transform: `translateY(${interpolate(subIn, [0, 1], [24, 0])}px)`,
                fontFamily: FONT_MAIN,
              }}
            >
              {parseHl(sub, popAt + 6)}
            </div>
          ) : null}
          {cta ? (
            <Cta pulseFrame={frame} text={cta} />
          ) : null}
        </div>
        {mascot ? (
          <div style={{position: "absolute", right: 40, bottom: wide ? 230 : 130, transform: `scale(${mPop})`, textAlign: "center"}}>
            <Mascot mood={mascot} width={wide ? 120 : 150} />
            {bubble ? (
              <div
                style={{
                  marginTop: 6,
                  background: C.accent,
                  color: "#141c38",
                  fontFamily: FONT_MAIN,
                  fontWeight: 800,
                  fontSize: 26,
                  borderRadius: 16,
                  padding: "4px 14px",
                  opacity: mPop,
                }}
              >
                {bubble}
              </div>
            ) : null}
          </div>
        ) : null}
      </AbsoluteFill>
    </ShotShell>
  );
};

const Cta: React.FC<{pulseFrame: number; text: string}> = ({pulseFrame, text}) => {
  const pulse = 1 + 0.05 * Math.sin((pulseFrame / 30) * Math.PI * 2 * 0.5);
  return (
    <div
      style={{
        marginTop: 6,
        padding: ".5rem 1.6rem",
        border: `2px solid ${C.accent}`,
        borderRadius: 999,
        color: C.accent,
        fontSize: 30,
        fontWeight: 800,
        transform: `scale(${pulse})`,
        fontFamily: FONT_MAIN,
      }}
    >
      {text}
    </div>
  );
};

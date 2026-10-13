import React from "react";
import {AbsoluteFill, useCurrentFrame, interpolate, staticFile, Img} from "remotion";
import {ShotShell} from "./ShotShell";
import {Mascot} from "./Mascot";
import {C, FONT_MAIN} from "../theme";

const ORIGINS: Array<[string, string]> = [
  ["50%", "55%"],
  ["32%", "36%"],
  ["68%", "42%"],
  ["50%", "76%"],
  ["30%", "70%"],
];

/** SVG 图幕（对应 svgshot 模板）：白底电路图卡 + 底部解说条。
 *  动效：描画式入场（clipPath 左→右）+ 聚焦推拉（每幕不同原点，电影感）。 */
export const SvgShot: React.FC<{
  durFrames: number;
  index: number;
  file: string;
  caption?: string;
  mascot?: string;
}> = ({durFrames, index, file, caption, mascot}) => {
  const frame = useCurrentFrame();
  const [ox, oy] = ORIGINS[index % ORIGINS.length];
  // 描画入场 0.9s（27 帧），ease-out
  const wipe = interpolate(frame, [0, 27], [100, 0], {extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: (t) => 1 - Math.pow(1 - t, 3)});
  // 聚焦推拉：0.9s 后起步，1→1.09
  const zoom = interpolate(frame, [27, durFrames], [1, 1.09], {extrapolateLeft: "clamp", extrapolateRight: "clamp"});
  const capIn = interpolate(frame, [8, 22], [0, 1], {extrapolateLeft: "clamp", extrapolateRight: "clamp"});

  return (
    <ShotShell durFrames={durFrames}>
      <AbsoluteFill
        style={{
          background: `radial-gradient(120% 90% at 0% 0%, rgba(94,122,255,.30), transparent 55%),
                       linear-gradient(200deg, ${C.bg0} 0%, ${C.bg1} 100%)`,
          flexDirection: "column",
          display: "flex",
        }}
      >
        <div style={{flex: 1, display: "flex", alignItems: "center", justifyContent: "center", padding: "26px 0 10px", width: "100%"}}>
          <div
            style={{
              width: "94%",
              borderRadius: 14,
              overflow: "hidden",
              boxShadow: "0 12px 38px rgba(23,32,64,.20)",
              clipPath: `inset(0 ${wipe}% 0 0 round 14px)`,
              transform: `scale(${zoom})`,
              transformOrigin: `${ox} ${oy}`,
            }}
          >
            <Img src={staticFile(`svg/${file}.svg`)} style={{width: "100%", display: "block"}} />
          </div>
        </div>
        {caption ? (
          <div
            style={{
              height: 110,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              background: C.bg0,
              color: C.ink,
              fontSize: 34,
              fontWeight: 700,
              fontFamily: FONT_MAIN,
              opacity: capIn,
              transform: `translateY(${(1 - capIn) * 30}px)`,
            }}
          >
            {caption}
          </div>
        ) : null}
        {mascot ? (
          <div style={{position: "absolute", right: 16, bottom: 122}}>
            <Mascot mood={mascot} width={104} />
          </div>
        ) : null}
      </AbsoluteFill>
    </ShotShell>
  );
};

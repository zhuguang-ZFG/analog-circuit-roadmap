import React from "react";
import {AbsoluteFill, useCurrentFrame, interpolate} from "remotion";
import {C} from "../theme";

/** PCB 走线装饰：45° 折线 + 焊盘，双车道反向漂移（stroke-dash 流动）。
 *  低透明度垫底——模拟电路系列的视觉图腾。 */
const PcbTraces: React.FC = () => {
  const frame = useCurrentFrame();
  const dash = -frame * 0.55;
  const dash2 = frame * 0.38;
  const traces: Array<{d: string; color: string; off: number}> = [
    {d: "M -20 540 L 230 540 L 370 400 L 690 400", color: "#5e7aff", off: dash},
    {d: "M 1100 1310 L 870 1310 L 730 1450 L 430 1450", color: "#ffc247", off: dash2},
    {d: "M -20 1620 L 170 1620 L 290 1500 L 290 1250 L 430 1250", color: "#5e7aff", off: dash},
    {d: "M 1100 300 L 940 300 L 830 190 L 560 190", color: "#ffc247", off: dash2},
  ];
  const pads: Array<[number, number]> = [[230, 540], [690, 400], [870, 1310], [430, 1450], [290, 1250], [940, 300], [560, 190]];
  return (
    <svg style={{position: "absolute", inset: 0, width: "100%", height: "100%", opacity: 0.1}} viewBox="0 0 1080 1920" preserveAspectRatio="xMidYMid slice">
      {traces.map((t, i) => (
        <path key={i} d={t.d} fill="none" stroke={t.color} strokeWidth={5}
          strokeDasharray="16 12" strokeDashoffset={t.off} strokeLinecap="round" />
      ))}
      {pads.map(([cx, cy], i) => (
        <circle key={i} cx={cx} cy={cy} r={9} fill="none" stroke={i % 2 ? "#ffc247" : "#5e7aff"} strokeWidth={4} />
      ))}
    </svg>
  );
};

/** 幕壳：靛蓝渐变 + 漂移点阵 + PCB 走线 + 底部晕影 + 每幕底部节奏条（beat）。
 *  与 director.py .bg/.bg::before/.bg::after/.beat 对应。 */
export const ShotShell: React.FC<{durFrames: number; children: React.ReactNode}> = ({durFrames, children}) => {
  const frame = useCurrentFrame();
  const drift = (frame * 0.6) % 18; // 26s 周期的点阵漂移
  const beat = interpolate(frame, [0, durFrames], [0, 1], {extrapolateLeft: "clamp", extrapolateRight: "clamp"});
  return (
    <AbsoluteFill
      style={{
        background: `radial-gradient(120% 90% at 100% 0%, rgba(94,122,255,.30), transparent 55%),
                     linear-gradient(165deg, ${C.bg0} 0%, ${C.bg1} 100%)`,
        overflow: "hidden",
      }}
    >
      <div
        style={{
          position: "absolute",
          inset: -40,
          backgroundImage: "radial-gradient(rgba(255,255,255,.13) 1px, transparent 1.2px)",
          backgroundSize: "18px 18px",
          transform: `translate(${-drift}px, ${-drift}px)`,
          maskImage: "linear-gradient(180deg,#000,transparent 85%)",
          WebkitMaskImage: "linear-gradient(180deg,#000,transparent 85%)",
        }}
      />
      <div
        style={{
          position: "absolute",
          inset: 0,
          background: "radial-gradient(140% 110% at 50% 50%, transparent 60%, rgba(8,12,28,.5) 100%)",
        }}
      />
      <PcbTraces />
      {/* 两团漂移光斑：背景的「活物」，20s/26s 双周期缓慢游走 */}
      {[0, 1].map((k) => {
        const T = k === 0 ? 20 : 26;
        const ph = (frame / 30 / T) * Math.PI * 2;
        const x = 50 + Math.sin(ph + k * 2.4) * 34;
        const y = 42 + Math.cos(ph * 0.9 + k * 1.7) * 30;
        return (
          <div
            key={k}
            style={{
              position: "absolute",
              left: `${x}%`,
              top: `${y}%`,
              width: 620,
              height: 620,
              marginLeft: -310,
              marginTop: -310,
              borderRadius: "50%",
              background: k === 0
                ? "radial-gradient(circle, rgba(94,122,255,.20), transparent 65%)"
                : "radial-gradient(circle, rgba(255,194,71,.10), transparent 65%)",
              filter: "blur(60px)",
            }}
          />
        );
      })}
      {children}
      <div
        style={{
          position: "absolute",
          left: 0,
          bottom: 0,
          height: 8,
          width: "100%",
          background: `linear-gradient(90deg,#5e7aff,${C.accent})`,
          transformOrigin: "left center",
          transform: `scaleX(${beat})`,
        }}
      />
    </AbsoluteFill>
  );
};

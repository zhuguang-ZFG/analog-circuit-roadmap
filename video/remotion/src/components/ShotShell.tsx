import React from "react";
import {AbsoluteFill, useCurrentFrame, useVideoConfig, interpolate} from "remotion";
import {C} from "../theme";

/** PCB 走线装饰：45° 折线 + 焊盘，双车道反向漂移（stroke-dash 流动）。
 *  低透明度垫底——模拟电路系列的视觉图腾。横竖两套坐标，按画幅探针切换。 */
const TRACES: Record<"v" | "h", {traces: Array<{d: string; color: string; off: number}>; pads: Array<[number, number]>}> = {
  v: {
    traces: [
      {d: "M -20 540 L 230 540 L 370 400 L 690 400", color: "#5e7aff", off: 0},
      {d: "M 1100 1310 L 870 1310 L 730 1450 L 430 1450", color: "#ffc247", off: 1},
      {d: "M -20 1620 L 170 1620 L 290 1500 L 290 1250 L 430 1250", color: "#5e7aff", off: 0},
      {d: "M 1100 300 L 940 300 L 830 190 L 560 190", color: "#ffc247", off: 1},
    ],
    pads: [[230, 540], [690, 400], [870, 1310], [430, 1450], [290, 1250], [940, 300], [560, 190]],
  },
  h: {
    traces: [
      {d: "M -20 260 L 420 260 L 560 130 L 980 130", color: "#5e7aff", off: 0},
      {d: "M 1940 820 L 1520 820 L 1380 960 L 1020 960", color: "#ffc247", off: 1},
      {d: "M -20 880 L 260 880 L 380 1000 L 380 1200 L 520 1200", color: "#5e7aff", off: 0},
      {d: "M 1940 190 L 1700 190 L 1590 90 L 1160 90", color: "#ffc247", off: 1},
    ],
    pads: [[420, 260], [980, 130], [1520, 820], [1020, 960], [380, 1200], [1700, 190], [1160, 90]],
  },
};

const PcbTraces: React.FC = () => {
  const frame = useCurrentFrame();
  const {width, height} = useVideoConfig();
  const wide = width > height;
  const set = wide ? TRACES.h : TRACES.v;
  const dash = -frame * 0.55;
  const dash2 = frame * 0.38;
  return (
    <svg style={{position: "absolute", inset: 0, width: "100%", height: "100%", opacity: 0.1}} viewBox={wide ? "0 0 1920 1080" : "0 0 1080 1920"} preserveAspectRatio="xMidYMid slice">
      {set.traces.map((t, i) => (
        <path key={i} d={t.d} fill="none" stroke={t.color} strokeWidth={5}
          strokeDasharray="16 12" strokeDashoffset={t.off ? dash2 : dash} strokeLinecap="round" />
      ))}
      {set.pads.map(([cx, cy], i) => (
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
  const {width, height} = useVideoConfig();
  const wide = width > height; // 横版（-h 组合 1920×1080）：光斑/走线按 16:9 取参
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
        const blob = wide ? 400 : 620;
        return (
          <div
            key={k}
            style={{
              position: "absolute",
              left: `${x}%`,
              top: `${y}%`,
              width: blob,
              height: blob,
              marginLeft: -blob / 2,
              marginTop: -blob / 2,
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

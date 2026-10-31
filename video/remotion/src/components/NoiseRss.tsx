import React from "react";
import {useCurrentFrame, useVideoConfig} from "remotion";
import {C, FONT_MAIN} from "../theme";
import {ShotShell} from "./ShotShell";

export const rootSumSquares = (values: number[]): number => Math.hypot(...values);

export const rssStage = (frame: number, durFrames: number) => {
  const progress = Math.max(0, Math.min(1, frame / Math.max(1, durFrames - 1)));
  const count = [0.08, 0.2, 0.32, 0.44].filter((at) => progress >= at).length;
  const t = Math.max(0, Math.min(1, (progress - 0.56) / 0.28));
  return {count, variance: count, rms: rootSumSquares(Array<number>(count).fill(1)), merge: t * t * (3 - 2 * t)};
};

export const NoiseRss: React.FC<{durFrames: number}> = ({durFrames}) => {
  const frame = useCurrentFrame();
  const {width, height} = useVideoConfig();
  const wide = width > height;
  const state = rssStage(frame, durFrames);
  const colors = [C.accent, C.good, C.eyebrow, C.bad];
  const settled = state.merge > 0.98;
  const panelX = wide ? 1000 : 70;
  const panelY = wide ? 145 : 620;
  return (
    <ShotShell durFrames={durFrames} camera={false}>
      <div style={{position: "absolute", left: wide ? 110 : 65, right: wide ? 110 : 65, top: wide ? 130 : 170, fontFamily: FONT_MAIN}}>
        <div style={{fontSize: 26, letterSpacing: 5, color: C.accent}}>噪声账本 / 合账</div>
        <div style={{fontSize: wide ? 50 : 60, lineHeight: 1.3, marginTop: wide ? 12 : 16, color: C.ink}}>四份噪声，为什么不是四倍？</div>
        <div style={{fontSize: wide ? 26 : 28, marginTop: wide ? 12 : 16, color: C.sub}}>前提：互不相关 · 同一参考点 · 同一带宽</div>
        <svg role="img" aria-label="四个各为一微伏有效值的互不相关噪声，方差相加为四，开根得到两微伏有效值" viewBox={wide ? "0 0 1700 630" : "0 0 1000 1020"} style={{display: "block", width: "100%", height: wide ? 500 : 820, marginTop: wide ? 5 : 20}}>
          <defs>
            <pattern id="rss-ledger-grid" width="40" height="40" patternUnits="userSpaceOnUse">
              <path d="M 40 0 L 0 0 0 40" fill="none" stroke={C.sub} strokeOpacity="0.12" />
            </pattern>
          </defs>
          <rect x="40" y="75" width="900" height="435" rx="24" fill="url(#rss-ledger-grid)" stroke={C.sub} strokeOpacity="0.18" />
          <text x="70" y="118" fill={C.sub} fontSize="24">每格面积 = 1 µV²（方差）</text>
          {[0, 1, 2, 3].map((index) => {
            const active = index < state.count;
            const startX = 90 + index * 210;
            const endX = 340 + (index % 2) * 160;
            const endY = 140 + Math.floor(index / 2) * 160;
            const x = startX + (endX - startX) * state.merge;
            const y = 235 + (endY - 235) * state.merge;
            return (
              <g key={index} transform={`translate(${x} ${y})`} opacity={active ? 1 : 0.16}>
                <rect width="160" height="160" rx={14 * (1 - state.merge)} fill={colors[index]} fillOpacity={active ? 0.25 : 0.05} stroke={colors[index]} strokeWidth="3" />
                <text x="80" y="90" textAnchor="middle" fill={colors[index]} fontSize="45">1²</text>
                <text x="80" y="205" textAnchor="middle" fill={C.sub} fontSize="25" opacity={1 - state.merge}>源 {index + 1} · 1 µV</text>
              </g>
            );
          })}
          <path d="M 337 478 L 337 490 L 663 490 L 663 478" fill="none" stroke={C.good} strokeWidth="3" opacity={state.merge} />
          <text x="500" y="545" textAnchor="middle" fill={C.good} fontSize="30" opacity={state.merge}>面积 4 → 边长 √4 = 2</text>
          <g transform={`translate(${panelX} ${panelY})`}>
            <rect width={wide ? 620 : 860} height="290" rx="22" fill="#10172f" fillOpacity="0.65" stroke={C.sub} strokeOpacity="0.3" />
            <text x="35" y="54" fill={C.sub} fontSize="28">先平方记账，再开根结算</text>
            <text x="35" y="120" fill={C.ink} fontSize={wide ? 41 : 48}>Σ eᵢ² = {state.variance} µV²</text>
            <text x="35" y="213" fill={C.good} fontSize={wide ? 64 : 74} opacity={state.merge}>e总 = {state.rms.toFixed(0)} µV</text>
            <text x="35" y="262" fill={C.sub} fontSize="25">有效值（RMS），不是瞬时电压</text>
          </g>
          <text x={wide ? 1035 : 105} y={wide ? 495 : 980} fill={settled ? C.good : C.sub} fontSize={wide ? 31 : 35}>
            {settled ? "四个等量源 → 2 倍，而非 4 倍" : "只相加各项的平方，不直接相加电压"}
          </text>
        </svg>
      </div>
    </ShotShell>
  );
};

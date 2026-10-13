import React from "react";
import {AbsoluteFill, useCurrentFrame, useVideoConfig, interpolate, spring} from "remotion";
import {ShotShell} from "./ShotShell";
import {C, FONT_MAIN} from "../theme";

/** 分压器带载塌落幕（ep04 幕4）：直接继承幕3 场景——不切画面，
 *  RL 幽灵固化夹上、电流分流、Vout 当面 5.0→3.3、公式重算、-33% 盖章。
 *  口播（11.5s≈344 帧）：「接上 10k 负载，等于给 R2 并联一只 10k，R2 等效变 5k。
 *  再代分压式：10 乘 5 除以 15，等于 3.3V——塌了三分之一。」
 *  节拍：
 *  0-30    RL 固化（虚线→实线）+ 夹入弹跳
 *  25-60   并联算账：R2∥RL = 10k∥10k = 5k（R2 标签联动脉冲）
 *  55-90   电流分流：圆点一分为二进 RL 支路
 *  85-140  Vout 读数 5.0→3.3 当面跳变，绿→红
 *  130-165 分压式重算：10 × 5/15 = 3.3V
 *  165-200 「-33%」红章砸入 + 画面微震
 *  200+    红灯呼吸告警，收尾压暗 */

const NODE = {x: 400, y: 400};
const TOP_Y = 140, BOT_Y = 660, LEFT_X = 100;
// 主回路（同幕3）+ RL 支路
const MAIN: Array<[number, number, number, number]> = [
  [LEFT_X, TOP_Y, NODE.x, TOP_Y],
  [NODE.x, TOP_Y, NODE.x, NODE.y],
  [NODE.x, NODE.y, NODE.x, BOT_Y],
  [NODE.x, BOT_Y, LEFT_X, BOT_Y],
  [LEFT_X, BOT_Y, LEFT_X, TOP_Y],
];
const RL_SEGS: Array<[number, number, number, number]> = [
  [NODE.x, NODE.y, 640, NODE.y],
  [640, NODE.y, 640, BOT_Y],
  [640, BOT_Y, NODE.x, BOT_Y],
];
const MAIN_LEN = MAIN.map(([a, b, c, d]) => Math.hypot(c - a, d - b));
const MAIN_LOOP = MAIN_LEN.reduce((a, b) => a + b, 0);
const RL_LEN = RL_SEGS.map(([a, b, c, d]) => Math.hypot(c - a, d - b));
const RL_LOOP = RL_LEN.reduce((a, b) => a + b, 0);

function along(segs: Array<[number, number, number, number]>, lens: number[], total: number, d: number): [number, number] {
  let rest = ((d % total) + total) % total;
  for (let i = 0; i < segs.length; i++) {
    if (rest <= lens[i]) {
      const [x1, y1, x2, y2] = segs[i];
      const t = rest / lens[i];
      return [x1 + (x2 - x1) * t, y1 + (y2 - y1) * t];
    }
    rest -= lens[i];
  }
  return [segs[0][0], segs[0][1]];
}

const zigzag = (x: number, y1: number, y2: number): string => {
  const n = 6, amp = 22, step = (y2 - y1) / n;
  let d = `M${x} ${y1}`;
  for (let i = 0; i < n; i++) d += ` L${x + (i % 2 === 0 ? amp : -amp)} ${y1 + step * (i + 0.5)}`;
  return d + ` L${x} ${y2}`;
};

export const DividerCollapse: React.FC<{durFrames: number}> = ({durFrames}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const pop = (d: number, stiff = 170) =>
    spring({frame: frame - d, fps, config: {damping: 11, stiffness: stiff, mass: 0.8}});

  // RL 固化：0-30 虚线变实线、弹入
  const rlSolid = interpolate(frame, [8, 30], [0, 1], {extrapolateLeft: "clamp", extrapolateRight: "clamp"});
  const rlSnap = pop(8, 200);
  // 并联算账（25-60）+ R2 标签脉冲
  const fPar1 = pop(25), fPar2 = pop(45);
  const r2Pulse = frame >= 25 && frame < 60 ? 1 + 0.2 * Math.sin(((frame - 25) / 35) * Math.PI) : 1;
  // 分流（55 起）：主路 3 点 + RL 支路 2 点
  const splitOn = frame >= 55;
  const mainDots = [0, 1, 2].map((k) => along(MAIN, MAIN_LEN, MAIN_LOOP, frame * 4.2 + (k * MAIN_LOOP) / 3));
  const rlDots = [0, 1].map((k) => along(RL_SEGS, RL_LEN, RL_LOOP, frame * 4.2 + (k * RL_LOOP) / 2));
  // Vout 跳变 5.0→3.3（85-140），绿→红
  const vout = interpolate(frame, [85, 140], [5.0, 3.3], {extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: (t) => 1 - Math.pow(1 - t, 3)});
  const red = interpolate(frame, [100, 145], [0, 1], {extrapolateLeft: "clamp", extrapolateRight: "clamp"});
  const alarm = frame >= 145 ? 0.5 + 0.5 * Math.sin(((frame - 145) / fps) * Math.PI * 2 * 1.4) : 0;
  // 分压式重算（130-165）
  const fRe1 = pop(130), fRe2 = pop(150);
  // -33% 盖章（165-200）+ 震屏
  const stamp = spring({frame: frame - 165, fps, config: {damping: 8, stiffness: 260, mass: 1.1}});
  const shake = frame >= 170 && frame < 182 ? Math.sin(frame * 2.1) * 6 * (1 - (frame - 170) / 12) : 0;
  const dim = interpolate(frame, [durFrames - 30, durFrames - 6], [0, 0.3], {extrapolateLeft: "clamp", extrapolateRight: "clamp"});

  const chipColor = red > 0.5 ? C.bad : C.good;
  // 缓推 + 视线向读数芯片微移（聚焦叙事）
  const push = interpolate(frame, [0, durFrames], [1, 1.05], {extrapolateLeft: "clamp", extrapolateRight: "clamp"});
  const driftX = interpolate(frame, [0, durFrames], [0, -26], {extrapolateLeft: "clamp", extrapolateRight: "clamp"});
  return (
    <ShotShell durFrames={durFrames}>
      <AbsoluteFill style={{justifyContent: "flex-start", alignItems: "center", display: "flex", paddingTop: 130,
        transform: `scale(${push}) translateX(${driftX}px)`}}>
        <svg viewBox="0 0 900 760" width="94%" style={{transform: `translateX(${shake}px)`}}>
          {/* 主回路（幕3 遗产：全亮静态） */}
          {MAIN.map(([x1, y1, x2, y2], i) => (
            <line key={i} x1={x1} y1={y1} x2={x2} y2={y2} stroke="#8fa5ff" strokeWidth={6} strokeLinecap="round" />
          ))}
          <line x1={LEFT_X - 34} y1={TOP_Y - 14} x2={LEFT_X + 34} y2={TOP_Y - 14} stroke={C.accent} strokeWidth={6} strokeLinecap="round" />
          <line x1={LEFT_X - 16} y1={TOP_Y + 2} x2={LEFT_X + 16} y2={TOP_Y + 2} stroke={C.accent} strokeWidth={10} strokeLinecap="round" />
          <text x={LEFT_X} y={TOP_Y - 40} fill={C.accent} fontSize={44} fontWeight={800} textAnchor="middle" fontFamily={FONT_MAIN}>10V</text>
          <path d={zigzag(NODE.x, TOP_Y + 26, NODE.y - 26)} fill="none" stroke="#fff" strokeWidth={6} strokeLinejoin="round" />
          <text x={NODE.x - 46} y={TOP_Y + 140} fill="#fff" fontSize={42} fontWeight={800} fontFamily={FONT_MAIN} textAnchor="end">R1 10k</text>
          <path d={zigzag(NODE.x, NODE.y + 26, BOT_Y - 26)} fill="none" stroke="#fff" strokeWidth={6} strokeLinejoin="round" />
          <text x={NODE.x - 46} y={NODE.y + 140} fill="#fff" fontSize={42} fontWeight={800} fontFamily={FONT_MAIN} textAnchor="end"
            transform={`scale(${r2Pulse})`} style={{transformOrigin: `${NODE.x - 46}px ${NODE.y + 120}px`}}>
            R2 10k
          </text>
          <circle cx={NODE.x} cy={NODE.y} r={10} fill={C.accent} />
          <line x1={NODE.x - 26} y1={BOT_Y + 16} x2={NODE.x + 26} y2={BOT_Y + 16} stroke="#fff" strokeWidth={6} strokeLinecap="round" />
          <line x1={NODE.x - 16} y1={BOT_Y + 30} x2={NODE.x + 16} y2={BOT_Y + 30} stroke="#fff" strokeWidth={5} strokeLinecap="round" />
          <line x1={NODE.x - 7} y1={BOT_Y + 43} x2={NODE.x + 7} y2={BOT_Y + 43} stroke="#fff" strokeWidth={4} strokeLinecap="round" />
          {/* RL：固化夹入（虚线→实线，红→白） */}
          <g opacity={rlSolid} transform={`translate(${(1 - rlSnap) * 60}px 0) scale(${0.9 + rlSnap * 0.1})`}>
            <line x1={640} y1={NODE.y} x2={640} y2={NODE.y + 22} stroke={red > 0.4 ? "#fff" : C.bad} strokeWidth={6}
              strokeDasharray={rlSolid >= 1 ? "none" : "8 8"} />
            <path d={zigzag(640, NODE.y + 22, BOT_Y - 28)} fill="none"
              stroke={red > 0.4 ? "#fff" : C.bad} strokeWidth={6}
              strokeDasharray={rlSolid >= 1 ? "none" : "14 12"} strokeLinejoin="round" />
            <line x1={640} y1={BOT_Y - 28} x2={640} y2={BOT_Y} stroke={red > 0.4 ? "#fff" : C.bad}
              strokeWidth={6} strokeDasharray={rlSolid >= 1 ? "none" : "10 10"} />
            <text x={706} y={BOT_Y - 60} fill={red > 0.4 ? "#fff" : C.bad} fontSize={46} fontWeight={800} textAnchor="middle" fontFamily={FONT_MAIN}>
              RL 10k
            </text>
          </g>
          {/* Vout 读数芯片：当面跳变 */}
          <line x1={NODE.x} y1={NODE.y} x2={650} y2={NODE.y} stroke={C.accent} strokeWidth={5} />
          <g style={{filter: `drop-shadow(0 0 ${16 + alarm * 24}px rgba(255,143,107,${0.25 + alarm * 0.4}))`}}>
            <rect x={635} y={310} width={220} height={180} rx={22} fill="rgba(20,28,56,.92)" stroke={chipColor} strokeWidth={4} />
            <text x={745} y={372} fill={C.sub} fontSize={36} textAnchor="middle" fontFamily={FONT_MAIN}>Vout</text>
            <text x={745} y={452} fill={chipColor} fontSize={76} fontWeight={800} textAnchor="middle" fontFamily={FONT_MAIN}>
              {vout.toFixed(1)}V
            </text>
          </g>
          {/* 分流圆点 */}
          {mainDots.map(([cx, cy], k) => <circle key={`m${k}`} cx={cx} cy={cy} r={9} fill={C.accent} opacity={0.95} />)}
          {splitOn && rlDots.map(([cx, cy], k) => <circle key={`r${k}`} cx={cx} cy={cy} r={8} fill={C.good} opacity={0.9} />)}
          {/* -33% 盖章 */}
          {frame >= 165 && (
            <g transform={`translate(185 652) scale(${stamp}) rotate(${-12 * stamp})`} opacity={stamp * 0.94}>
              <rect x={-105} y={-58} width={210} height={116} rx={16} fill="none" stroke={C.bad} strokeWidth={9} />
              <text x={0} y={22} fill={C.bad} fontSize={62} fontWeight={800} textAnchor="middle" fontFamily={FONT_MAIN}>-33%</text>
            </g>
          )}
        </svg>

        {/* 算账面板：并联 → 重算 */}
        <div style={{marginTop: 30, display: "flex", flexDirection: "column", alignItems: "center", gap: 10,
          fontFamily: FONT_MAIN, fontWeight: 800, transform: `translateX(${shake}px)`}}>
          <div style={{opacity: fPar1, transform: `translateY(${interpolate(fPar1, [0, 1], [30, 0])}px)`, fontSize: 44, color: "#fff"}}>
            R2 ∥ RL = 10k ∥ 10k
          </div>
          <div style={{opacity: fPar2, transform: `translateY(${interpolate(fPar2, [0, 1], [30, 0])}px)`, fontSize: 44, color: "#fff"}}>
            = <span style={{color: C.accent}}>5k</span>
          </div>
          <div style={{opacity: fRe1, transform: `translateY(${interpolate(fRe1, [0, 1], [30, 0])}px)`, fontSize: 44, color: "#fff"}}>
            Vout = <span style={{color: C.accent}}>10</span> × 5 / 15
          </div>
          <div style={{opacity: fRe2, transform: `translateY(${interpolate(fRe2, [0, 1], [30, 0])}px) scale(${0.6 + fRe2 * 0.4})`,
            fontSize: 58, color: C.bad}}>
            = 3.3V ✗
          </div>
        </div>
        <AbsoluteFill style={{background: `rgba(8,12,28,${dim})`, pointerEvents: "none"}} />
      </AbsoluteFill>
    </ShotShell>
  );
};

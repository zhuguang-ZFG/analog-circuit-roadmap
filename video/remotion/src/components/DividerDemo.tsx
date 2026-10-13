import React from "react";
import {AbsoluteFill, useCurrentFrame, useVideoConfig, interpolate, spring} from "remotion";
import {ShotShell} from "./ShotShell";
import {C, FONT_MAIN} from "../theme";

/** 分压器定制演示幕 v2（ep04 幕3）：电路演出来 + 公式现场算账。
 *  设计要点（对着口播节拍）：
 *  - 导线逐段描画（5 段接力，不是一锅出）
 *  - 元件 spring 过冲弹入（生动活泼的底味）
 *  - 公式四步现场算：定义式 → 代入 → 化简 → 结果飞进读数芯片；
 *    代入时 R1/R2 标签同步脉冲高亮（公式↔电路联动）
 *  - 电流圆点带拖尾流动
 *  - 「完美」绿勾弹入（≤180 帧，卡在口播「完美」上）
 *  - 后段 RL 幽灵红闪 + 压暗收尾（悬念：空载前提） */

const NODE = {x: 400, y: 400};
const TOP_Y = 140, BOT_Y = 660, LEFT_X = 100;
const SEGS: Array<[number, number, number, number]> = [
  [LEFT_X, TOP_Y, NODE.x, TOP_Y],
  [NODE.x, TOP_Y, NODE.x, NODE.y],
  [NODE.x, NODE.y, NODE.x, BOT_Y],
  [NODE.x, BOT_Y, LEFT_X, BOT_Y],
  [LEFT_X, BOT_Y, LEFT_X, TOP_Y],
];
const SEGLEN = SEGS.map(([x1, y1, x2, y2]) => Math.hypot(x2 - x1, y2 - y1));
const LOOP = SEGLEN.reduce((a, b) => a + b, 0);

function pointAt(d: number): [number, number] {
  let rest = ((d % LOOP) + LOOP) % LOOP;
  for (let i = 0; i < SEGS.length; i++) {
    if (rest <= SEGLEN[i]) {
      const [x1, y1, x2, y2] = SEGS[i];
      const t = rest / SEGLEN[i];
      return [x1 + (x2 - x1) * t, y1 + (y2 - y1) * t];
    }
    rest -= SEGLEN[i];
  }
  return [SEGS[0][0], SEGS[0][1]];
}

const zigzag = (x: number, y1: number, y2: number): string => {
  const n = 6, amp = 22, step = (y2 - y1) / n;
  let d = `M${x} ${y1}`;
  for (let i = 0; i < n; i++) d += ` L${x + (i % 2 === 0 ? amp : -amp)} ${y1 + step * (i + 0.5)}`;
  return d + ` L${x} ${y2}`;
};

export const DividerDemo: React.FC<{durFrames: number}> = ({durFrames}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const pop = (d: number, stiff = 170) =>
    spring({frame: frame - d, fps, config: {damping: 11, stiffness: stiff, mass: 0.8}});

  // 导线逐段接力描画（每段 5.5 帧——开场 1s 内必须有完整回路）
  const segDraw = (i: number) =>
    interpolate(frame, [i * 5.5, i * 5.5 + 7], [1, 0], {extrapolateLeft: "clamp", extrapolateRight: "clamp"});

  // 公式四步（底部面板）——卡口播「输出 5V，完美」节奏
  const f1 = pop(50), f2 = pop(68), f3 = pop(86), f4 = pop(102);
  // 代入脉冲：R1/R2 标签在 f2 时刻联动放大
  const labelPulse = frame >= 68 && frame < 98 ? 1 + 0.22 * Math.sin(((frame - 68) / 30) * Math.PI) : 1;

  // Vout 芯片：105 弹入，108-128 数字 0→5.0 跳变，落定后绿辉光
  const chipIn = pop(105, 140);
  const voutVal = interpolate(frame, [108, 128], [0, 5.0], {extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: (t) => 1 - Math.pow(1 - t, 3)});
  const settled = frame >= 128;
  const chipGlow = settled ? 0.6 + 0.4 * Math.sin(((frame - 128) / fps) * Math.PI * 2 * 1.2) : 0;

  // 电流圆点（130 帧起）+ 拖尾
  const flowOn = frame >= 130;
  const dotSets = [0, 1, 2, 3, 4].map((k) => {
    const head = pointAt(frame * 4.2 + (k * LOOP) / 5);
    const t1 = pointAt(frame * 4.2 - 14 + (k * LOOP) / 5);
    const t2 = pointAt(frame * 4.2 - 28 + (k * LOOP) / 5);
    return {head, t1, t2};
  });

  // 绿勾（165-185，卡口播「完美」）
  const check = spring({frame: frame - 132, fps, config: {damping: 8, stiffness: 220}});

  // RL 幽灵悬念（195 帧起红闪 + 微晃）+ 收尾压暗
  const ghostT = frame - 195;
  // 幕尾 70 帧闪烁频率翻倍——「要出事了」的急促感，正好接幕4
  const gf = frame > durFrames - 70 ? 0.62 : 0.32;
  const ghost = ghostT >= 0 ? (Math.sin(frame * gf) > 0 ? 0.9 : 0.38) : 0;
  const ghostWob = ghostT >= 0 ? Math.sin(frame * 0.22) * 3 : 0;
  const dim = interpolate(frame, [durFrames - 35, durFrames - 6], [0, 0.38], {extrapolateLeft: "clamp", extrapolateRight: "clamp"});

  const wire = "#8fa5ff";
  // 全幕镜头缓推（1→1.035，电影感）
  const push = interpolate(frame, [0, durFrames], [1, 1.035], {extrapolateLeft: "clamp", extrapolateRight: "clamp"});

  return (
    <ShotShell durFrames={durFrames}>
      <AbsoluteFill style={{justifyContent: "flex-start", alignItems: "center", display: "flex", paddingTop: 130, transform: `scale(${push})`}}>
        <svg viewBox="0 0 900 760" width="94%">
          {/* 回路导线：逐段描画 */}
          {SEGS.map(([x1, y1, x2, y2], i) => (
            <line key={i} x1={x1} y1={y1} x2={x2} y2={y2} stroke={wire} strokeWidth={6} strokeLinecap="round"
              strokeDasharray={SEGLEN[i]} strokeDashoffset={SEGLEN[i] * segDraw(i)} />
          ))}
          {/* 电池 10V */}
          <g opacity={pop(16)} transform={`scale(${pop(16)})`} style={{transformOrigin: "100px 140px"}}>
            <line x1={LEFT_X - 34} y1={TOP_Y - 14} x2={LEFT_X + 34} y2={TOP_Y - 14} stroke={C.accent} strokeWidth={6} strokeLinecap="round" />
            <line x1={LEFT_X - 16} y1={TOP_Y + 2} x2={LEFT_X + 16} y2={TOP_Y + 2} stroke={C.accent} strokeWidth={10} strokeLinecap="round" />
            <text x={LEFT_X} y={TOP_Y - 40} fill={C.accent} fontSize={44} fontWeight={800} textAnchor="middle" fontFamily={FONT_MAIN}>10V</text>
          </g>
          {/* R1 / R2 */}
          <g opacity={pop(24)} transform={`scale(${pop(24)})`} style={{transformOrigin: "400px 270px"}}>
            <path d={zigzag(NODE.x, TOP_Y + 26, NODE.y - 26)} fill="none" stroke="#fff" strokeWidth={6} strokeLinejoin="round" />
            <text x={NODE.x - 46} y={TOP_Y + 140} fill="#fff" fontSize={42} fontWeight={800} fontFamily={FONT_MAIN} textAnchor="end"
              transform={`scale(${labelPulse})`} style={{transformOrigin: `${NODE.x - 46}px ${TOP_Y + 120}px`}}>
              R1 10k
            </text>
          </g>
          <g opacity={pop(32)} transform={`scale(${pop(32)})`} style={{transformOrigin: "400px 530px"}}>
            <path d={zigzag(NODE.x, NODE.y + 26, BOT_Y - 26)} fill="none" stroke="#fff" strokeWidth={6} strokeLinejoin="round" />
            <text x={NODE.x - 46} y={NODE.y + 140} fill="#fff" fontSize={42} fontWeight={800} fontFamily={FONT_MAIN} textAnchor="end"
              transform={`scale(${labelPulse})`} style={{transformOrigin: `${NODE.x - 46}px ${NODE.y + 120}px`}}>
              R2 10k
            </text>
          </g>
          {/* 节点 + GND */}
          <circle cx={NODE.x} cy={NODE.y} r={10} fill={C.accent} opacity={pop(40)} />
          <g opacity={pop(44)}>
            <line x1={NODE.x - 26} y1={BOT_Y + 16} x2={NODE.x + 26} y2={BOT_Y + 16} stroke="#fff" strokeWidth={6} strokeLinecap="round" />
            <line x1={NODE.x - 16} y1={BOT_Y + 30} x2={NODE.x + 16} y2={BOT_Y + 30} stroke="#fff" strokeWidth={5} strokeLinecap="round" />
            <line x1={NODE.x - 7} y1={BOT_Y + 43} x2={NODE.x + 7} y2={BOT_Y + 43} stroke="#fff" strokeWidth={4} strokeLinecap="round" />
          </g>
          {/* Vout 抽头 + 读数芯片 */}
          <line x1={NODE.x} y1={NODE.y} x2={650} y2={NODE.y} stroke={C.accent} strokeWidth={5}
            strokeDasharray={250} strokeDashoffset={250 * (1 - pop(46))} />
          <g opacity={chipIn} transform={`scale(${chipIn})`} style={{transformOrigin: "745px 400px"}}>
            <rect x={635} y={310} width={220} height={180} rx={22} fill="rgba(20,28,56,.92)"
              stroke={settled ? C.good : C.sub} strokeWidth={4}
              style={{filter: `drop-shadow(0 0 ${18 + chipGlow * 22}px rgba(124,227,200,${0.35 + chipGlow * 0.3}))`}} />
            <text x={745} y={372} fill={C.sub} fontSize={36} textAnchor="middle" fontFamily={FONT_MAIN}>Vout</text>
            <text x={745} y={452} fill={settled ? C.good : "#fff"} fontSize={76} fontWeight={800} textAnchor="middle" fontFamily={FONT_MAIN}>
              {voutVal.toFixed(1)}V
            </text>
          </g>
          {/* 电流圆点 + 拖尾 */}
          {flowOn && dotSets.map((d, k) => (
            <g key={k}>
              <circle cx={d.t2[0]} cy={d.t2[1]} r={4.5} fill={C.accent} opacity={0.25} />
              <circle cx={d.t1[0]} cy={d.t1[1]} r={6.5} fill={C.accent} opacity={0.5} />
              <circle cx={d.head[0]} cy={d.head[1]} r={9} fill={C.accent} opacity={0.95} />
            </g>
          ))}
          {/* 完美绿勾 */}
          {frame >= 128 && (
            <g transform={`translate(180 528) scale(${check})`} opacity={check}>
              <circle r={52} fill="none" stroke={C.good} strokeWidth={8} />
              <path d="M-26 4 L-6 26 L30 -18" fill="none" stroke={C.good} strokeWidth={10} strokeLinecap="round" strokeLinejoin="round" />
            </g>
          )}
          {/* RL 幽灵 */}
          {ghostT >= 0 && (
            <g opacity={ghost} transform={`rotate(${ghostWob} 640 520)`}>
              <line x1={640} y1={NODE.y} x2={640} y2={NODE.y + 22} stroke={C.bad} strokeWidth={6} strokeDasharray="8 8" />
              <path d={zigzag(640, NODE.y + 22, BOT_Y - 28)} fill="none" stroke={C.bad} strokeWidth={6} strokeDasharray="14 12" strokeLinejoin="round" />
              <line x1={640} y1={BOT_Y - 28} x2={640} y2={BOT_Y} stroke={C.bad} strokeWidth={6} strokeDasharray="10 10" />
              <text x={706} y={BOT_Y - 60} fill={C.bad} fontSize={46} fontWeight={800} textAnchor="middle" fontFamily={FONT_MAIN}>RL ?</text>
            </g>
          )}
        </svg>

        {/* 公式算账面板：四步现场推导 */}
        <div style={{
          marginTop: 30, display: "flex", flexDirection: "column", alignItems: "center", gap: 10,
          fontFamily: FONT_MAIN, fontWeight: 800,
        }}>
          <div style={{opacity: f1, transform: `translateY(${interpolate(f1, [0, 1], [30, 0])}px)`,
            fontSize: 40, color: C.sub}}>
            Vout = V × R2 / (R1 + R2)
          </div>
          <div style={{opacity: f2, transform: `translateY(${interpolate(f2, [0, 1], [30, 0])}px)`,
            fontSize: 44, color: "#fff"}}>
            = <span style={{color: C.accent}}>10</span> × <span style={{color: C.accent}}>10k</span> / (<span style={{color: C.accent}}>10k</span> + <span style={{color: C.accent}}>10k</span>)
          </div>
          <div style={{opacity: f3, transform: `translateY(${interpolate(f3, [0, 1], [30, 0])}px)`,
            fontSize: 44, color: "#fff"}}>
            = 10 × ½
          </div>
          <div style={{opacity: f4, transform: `translateY(${interpolate(f4, [0, 1], [30, 0])}px) scale(${0.6 + f4 * 0.4})`,
            fontSize: 58, color: C.good}}>
            = 5.0V ✓
          </div>
        </div>
        <AbsoluteFill style={{background: `rgba(8,12,28,${dim})`, pointerEvents: "none"}} />
      </AbsoluteFill>
    </ShotShell>
  );
};

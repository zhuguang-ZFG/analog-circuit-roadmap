import React, {useEffect, useState} from "react";
import {Audio, staticFile, AbsoluteFill, delayRender, continueRender, useCurrentFrame, interpolate} from "remotion";
import {TransitionSeries, springTiming} from "@remotion/transitions";
import {slide} from "@remotion/transitions/slide";
import {IntroShot} from "./components/IntroShot";
import {CardShot} from "./components/CardShot";
import {NumShot} from "./components/NumShot";
import {SvgShot} from "./components/SvgShot";
import {Subtitles} from "./Subtitles";
import {EPISODES, Shot} from "./episodes";

/** 常驻品牌角标（左上）：系列名 · 集号，低透明度毛玻璃胶囊，全片不动。
 *  抖音合集账号的通行做法——刷到任何一帧都知道是谁家的第几集。 */
const BrandBadge: React.FC<{series: string; ep: string}> = ({series, ep}) => {
  const frame = useCurrentFrame();
  const op = interpolate(frame, [8, 26], [0, 0.62], {extrapolateLeft: "clamp", extrapolateRight: "clamp"});
  if (!series) return null;
  return (
    <div
      style={{
        position: "absolute",
        top: 40,
        left: 44,
        zIndex: 20,
        opacity: op,
        display: "flex",
        alignItems: "center",
        gap: 10,
        fontFamily: '"ZCOOL KuaiLe","Microsoft YaHei",sans-serif',
        fontSize: 25,
        letterSpacing: ".12em",
        color: "rgba(255,255,255,.92)",
        background: "rgba(8,12,28,.38)",
        backdropFilter: "blur(5px)",
        WebkitBackdropFilter: "blur(5px)",
        border: "1px solid rgba(143,165,255,.28)",
        borderRadius: 999,
        padding: "7px 20px",
        pointerEvents: "none",
      }}
    >
      <span style={{color: "#ffc247"}}>⚡</span>
      <span>{series}</span>
      <span style={{color: "rgba(255,255,255,.5)"}}>·</span>
      <span style={{color: "#8fa5ff"}}>{ep}</span>
    </div>
  );
};

/** 逐幕精确时长（累计取整防漂移），Series 硬切保证音画对齐。
 *  音频用母带级混音成品 wav（口播+BGM+音效已过两遍 loudnorm）。
 *  ep prop 选集（注册表见 episodes.ts）；音画内容全部数据驱动。 */
export const Episode: React.FC<{ep?: string; cover?: boolean}> = ({ep = "ep04", cover = false}) => {
  const def = EPISODES[ep];
  if (!def) throw new Error(`unknown episode: ${ep}`);

  // 字体门控：快乐体 load 完才采帧（对应旧管线 document.fonts.ready 门控）
  const [handle] = useState(() => delayRender("loading ZCOOL KuaiLe"));
  useEffect(() => {
    const font = new FontFace("ZCOOL KuaiLe", `url(${staticFile("font/ZCOOLKuaiLe-Regular.ttf")})`);
    font
      .load()
      .then((f) => {
        document.fonts.add(f);
        continueRender(handle);
      })
      .catch(() => continueRender(handle)); // 字体失败也不能卡死流水线（雅黑兜底）
  }, [handle]);

  const shots = def.board.shots as Shot[];
  // 帧边界：round(t*fps) 差分，保证总长 = round(total*fps)
  const bounds: number[] = [0];
  let acc = 0;
  for (const s of shots) {
    acc += s.seconds;
    bounds.push(Math.round(acc * 30));
  }

  /* 真转场：相邻幕重叠 T 帧滑场。时长补偿——每幕（除末幕）+T 帧尾巴，
     使第 k 幕内容起点仍精确等于音频偏移 ΣD_j（S_k = Σ(D_j+T) − k·T = ΣD_j）。
     方向四向轮转（对应 CSS v1 的 DIRS）。 */
  const T = 9;
  const DIRS = ["from-bottom", "from-top", "from-left", "from-right"] as const;
  return (
    <AbsoluteFill style={{background: "#141c38"}}>
      <TransitionSeries>
        {shots.flatMap((s, i) => {
          const durFrames = Math.max(bounds[i + 1] - bounds[i], 1);
          const Custom = s.view ? def.customShots[s.view] : undefined;
          const el = (
            <TransitionSeries.Sequence key={`s${i}`} durationInFrames={durFrames + (i < shots.length - 1 ? T : 0)}>
              {Custom ? (
                <Custom durFrames={durFrames} />
              ) : s.type === "intro" ? (
                <IntroShot
                  durFrames={durFrames}
                  series={s.series as string}
                  ep={s.ep as string}
                  title={s.title as string}
                  progress={s.progress as string}
                />
              ) : s.type === "num" ? (
                <NumShot
                  durFrames={durFrames}
                  from={s.from as number}
                  to={s.to as number}
                  unit={s.unit as string}
                  dec={(s.dec as number) ?? 1}
                  sub={s.sub as string}
                  bar={s.bar as [number, number]}
                  mascot={s.mascot as string}
                />
              ) : s.type === "svg" ? (
                <SvgShot
                  durFrames={durFrames}
                  index={i}
                  file={s.file as string}
                  caption={s.caption as string}
                  mascot={s.mascot as string}
                />
              ) : (
                <CardShot
                  durFrames={durFrames}
                  index={i}
                  eyebrow={s.eyebrow as string}
                  lines={s.lines as string[]}
                  sub={s.sub as string}
                  chip={s.chip as string}
                  mascot={s.mascot as string}
                  bubble={s.bubble as string}
                  cta={s.cta as string}
                />
              )}
            </TransitionSeries.Sequence>
          );
          if (i >= shots.length - 1) return [el];
          return [
            el,
            <TransitionSeries.Transition
              key={`t${i}`}
              presentation={slide({direction: DIRS[i % 4]})}
              timing={springTiming({config: {damping: 200}, durationInFrames: T})}
            />,
          ];
        })}
      </TransitionSeries>
      <BrandBadge series={(shots[0].series as string) ?? ""} ep={(shots[0].ep as string) ?? ""} />
      {cover ? null : <Subtitles data={def.subs} />}
      <Audio src={staticFile(def.audio)} />
    </AbsoluteFill>
  );
};

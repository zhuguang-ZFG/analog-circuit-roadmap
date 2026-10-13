import React from "react";
import {Composition} from "remotion";
import {Episode} from "./Episode";
import {EPISODES, episodeFrames} from "./episodes";

/** 每集两个组合：`epNN` 竖屏（1080×1920，抖音）/ `epNN-h` 横屏（1920×1080，B 站）。
 *  同一 Episode 组件，画幅由 useVideoConfig 探测，组件内自行分支排版。 */
export const Root: React.FC = () => (
  <>
    {Object.keys(EPISODES).flatMap((ep) => [
      <Composition
        key={ep}
        id={ep}
        component={Episode}
        defaultProps={{ep}}
        durationInFrames={episodeFrames(ep)}
        fps={30}
        width={1080}
        height={1920}
      />,
      <Composition
        key={`${ep}-h`}
        id={`${ep}-h`}
        component={Episode}
        defaultProps={{ep}}
        durationInFrames={episodeFrames(ep)}
        fps={30}
        width={1920}
        height={1080}
      />,
    ])}
  </>
);

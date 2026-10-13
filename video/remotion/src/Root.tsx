import React from "react";
import {Composition} from "remotion";
import {Episode} from "./Episode";
import {EPISODES, episodeFrames} from "./episodes";

/** 每集一个组合，id = 注册表键（ep04 → `remotion render ep04`）。 */
export const Root: React.FC = () => (
  <>
    {Object.keys(EPISODES).map((ep) => (
      <Composition
        key={ep}
        id={ep}
        component={Episode}
        defaultProps={{ep}}
        durationInFrames={episodeFrames(ep)}
        fps={30}
        width={1080}
        height={1920}
      />
    ))}
  </>
);

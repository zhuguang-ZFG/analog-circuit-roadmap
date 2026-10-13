import React from "react";
import ep01Board from "./data/ep01.json";
import ep01Subs from "./data/ep01-subs.json";
import ep02Board from "./data/ep02.json";
import ep02Subs from "./data/ep02-subs.json";
import ep03Board from "./data/ep03.json";
import ep03Subs from "./data/ep03-subs.json";
import ep04Board from "./data/ep04.json";
import ep04Subs from "./data/ep04-subs.json";
import ep05Board from "./data/ep05.json";
import ep05Subs from "./data/ep05-subs.json";
import ep06Board from "./data/ep06.json";
import ep06Subs from "./data/ep06-subs.json";
import ep07Board from "./data/ep07.json";
import ep07Subs from "./data/ep07-subs.json";
import ep08Board from "./data/ep08.json";
import ep08Subs from "./data/ep08-subs.json";
import ep09Board from "./data/ep09.json";
import ep09Subs from "./data/ep09-subs.json";
import ep10Board from "./data/ep10.json";
import ep10Subs from "./data/ep10-subs.json";
import ep11Board from "./data/ep11.json";
import ep11Subs from "./data/ep11-subs.json";
import ep12Board from "./data/ep12.json";
import ep12Subs from "./data/ep12-subs.json";
import ep13Board from "./data/ep13.json";
import ep13Subs from "./data/ep13-subs.json";
import ep14Board from "./data/ep14.json";
import ep14Subs from "./data/ep14-subs.json";
import ep15Board from "./data/ep15.json";
import ep15Subs from "./data/ep15-subs.json";
import ep16Board from "./data/ep16.json";
import ep16Subs from "./data/ep16-subs.json";
import ep17Board from "./data/ep17.json";
import ep17Subs from "./data/ep17-subs.json";
import ep18Board from "./data/ep18.json";
import ep18Subs from "./data/ep18-subs.json";
import ep19Board from "./data/ep19.json";
import ep19Subs from "./data/ep19-subs.json";
import ep20Board from "./data/ep20.json";
import ep20Subs from "./data/ep20-subs.json";
import {DividerDemo} from "./components/DividerDemo";
import {DividerCollapse} from "./components/DividerCollapse";
import {FPS} from "./theme";

export type Shot = {type: string; seconds: number; view?: string; [k: string]: unknown};
export type SubEntry = {from: number; to: number; text: string; env?: number[]};

/** 本文件由 gen_registry.py 生成——换集跑一次即可，勿手改。 */
export type EpisodeDef = {
  board: {shots: Shot[]};
  subs: SubEntry[];
  audio: string; // staticFile 相对路径
  customShots: Record<string, React.FC<{durFrames: number}>>;
};
export const EPISODES: Record<string, EpisodeDef> = {
  ep01: {
    board: ep01Board as {shots: Shot[]},
    subs: ep01Subs as SubEntry[],
    audio: "audio/ep01-miller-remix.wav",
    customShots: {},
  },
  ep02: {
    board: ep02Board as {shots: Shot[]},
    subs: ep02Subs as SubEntry[],
    audio: "audio/ep02-virtual-short-remix.wav",
    customShots: {},
  },
  ep03: {
    board: ep03Board as {shots: Shot[]},
    subs: ep03Subs as SubEntry[],
    audio: "audio/ep03-hysteresis-remix.wav",
    customShots: {},
  },
  ep04: {
    board: ep04Board as {shots: Shot[]},
    subs: ep04Subs as SubEntry[],
    audio: "audio/ep04-divider-remix.wav",
    customShots: {demo: DividerDemo, collapse: DividerCollapse},
  },
  ep05: {
    board: ep05Board as {shots: Shot[]},
    subs: ep05Subs as SubEntry[],
    audio: "audio/ep05-probe-remix.wav",
    customShots: {},
  },
  ep06: {
    board: ep06Board as {shots: Shot[]},
    subs: ep06Subs as SubEntry[],
    audio: "audio/ep06-thermal-remix.wav",
    customShots: {},
  },
  ep07: {
    board: ep07Board as {shots: Shot[]},
    subs: ep07Subs as SubEntry[],
    audio: "audio/ep07-pullup-remix.wav",
    customShots: {},
  },
  ep08: {
    board: ep08Board as {shots: Shot[]},
    subs: ep08Subs as SubEntry[],
    audio: "audio/ep08-decoupling-remix.wav",
    customShots: {},
  },
  ep09: {
    board: ep09Board as {shots: Shot[]},
    subs: ep09Subs as SubEntry[],
    audio: "audio/ep09-electrolytic-remix.wav",
    customShots: {},
  },
  ep10: {
    board: ep10Board as {shots: Shot[]},
    subs: ep10Subs as SubEntry[],
    audio: "audio/ep10-flyback-remix.wav",
    customShots: {},
  },
  ep11: {
    board: ep11Board as {shots: Shot[]},
    subs: ep11Subs as SubEntry[],
    audio: "audio/ep11-crossover-remix.wav",
    customShots: {},
  },
  ep12: {
    board: ep12Board as {shots: Shot[]},
    subs: ep12Subs as SubEntry[],
    audio: "audio/ep12-555-remix.wav",
    customShots: {},
  },
  ep13: {
    board: ep13Board as {shots: Shot[]},
    subs: ep13Subs as SubEntry[],
    audio: "audio/ep13-buck-remix.wav",
    customShots: {},
  },
  ep14: {
    board: ep14Board as {shots: Shot[]},
    subs: ep14Subs as SubEntry[],
    audio: "audio/ep14-ldo-remix.wav",
    customShots: {},
  },
  ep15: {
    board: ep15Board as {shots: Shot[]},
    subs: ep15Subs as SubEntry[],
    audio: "audio/ep15-mirror-remix.wav",
    customShots: {},
  },
  ep16: {
    board: ep16Board as {shots: Shot[]},
    subs: ep16Subs as SubEntry[],
    audio: "audio/ep16-diffpair-remix.wav",
    customShots: {},
  },
  ep17: {
    board: ep17Board as {shots: Shot[]},
    subs: ep17Subs as SubEntry[],
    audio: "audio/ep17-bandgap-remix.wav",
    customShots: {},
  },
  ep18: {
    board: ep18Board as {shots: Shot[]},
    subs: ep18Subs as SubEntry[],
    audio: "audio/ep18-ground-remix.wav",
    customShots: {},
  },
  ep19: {
    board: ep19Board as {shots: Shot[]},
    subs: ep19Subs as SubEntry[],
    audio: "audio/ep19-debug-remix.wav",
    customShots: {},
  },
  ep20: {
    board: ep20Board as {shots: Shot[]},
    subs: ep20Subs as SubEntry[],
    audio: "audio/ep20-noise-remix.wav",
    customShots: {},
  },
};

export const episodeFrames = (ep: string): number =>
  Math.round(EPISODES[ep].board.shots.reduce((a, s) => a + s.seconds, 0) * FPS);

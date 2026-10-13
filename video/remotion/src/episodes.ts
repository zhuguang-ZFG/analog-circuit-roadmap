import React from "react";
import ep01Board from "./data/ep01.json";
import ep01Subs from "./data/ep01-subs.json";
import ep04Board from "./data/ep04.json";
import ep04Subs from "./data/ep04-subs.json";
import {DividerDemo} from "./components/DividerDemo";
import {DividerCollapse} from "./components/DividerCollapse";
import {FPS} from "./theme";

export type Shot = {type: string; seconds: number; view?: string; [k: string]: unknown};
export type SubEntry = {from: number; to: number; text: string; env?: number[]};

/** 每集一件：板书数据、字幕窗、母带音轨、定制戏眼组件。
 *  换集 = 新增一条注册 + 两个 data 文件，Episode/Root 零改动。
 *  戏眼：board 里带 "view" 字段的幕走 customShots[view]，其余按 type 走通用幕。 */
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
  ep04: {
    board: ep04Board as {shots: Shot[]},
    subs: ep04Subs as SubEntry[],
    audio: "audio/ep04-divider-v11-audio.wav",
    customShots: {demo: DividerDemo, collapse: DividerCollapse},
  },
};

export const episodeFrames = (ep: string): number =>
  Math.round(EPISODES[ep].board.shots.reduce((a, s) => a + s.seconds, 0) * FPS);

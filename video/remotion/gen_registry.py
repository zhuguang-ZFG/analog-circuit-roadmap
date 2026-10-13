#!/usr/bin/env python3
"""集注册表生成：扫描 src/data/epNN.json → 生成 episodes.ts。

换集流程收口为：
  1. python make_subs.py <ep-name>   （字幕窗 + 能量分位）
  2. python remix.py <ep-name>       （口播+BGM+音效母带）
  3. cp samples/<ep-name>-timeline.json src/data/epNN.json
  4. python gen_registry.py          （本脚本；episodes.ts 全量重建）
"""
import json
from pathlib import Path

SRC = Path(__file__).parent / "src"
# 定制戏眼组件挂载点（幕 board 带 view 字段的集在这里登记）
CUSTOM: dict[str, str] = {
    "ep04": '{demo: DividerDemo, collapse: DividerCollapse}',
}


def main() -> int:
    boards = sorted(SRC.glob("data/ep*.json"))
    boards = [b for b in boards if not b.name.endswith("-subs.json")]
    imports, entries = [], []
    for b in boards:
        key = b.stem
        name = json.loads(b.read_text(encoding="utf-8"))["name"]
        imports.append(f'import {key}Board from "./data/{key}.json";')
        imports.append(f'import {key}Subs from "./data/{key}-subs.json";')
        custom = CUSTOM.get(key, "{}")
        entries.append(
            f"  {key}: {{\n"
            f'    board: {key}Board as {{shots: Shot[]}},\n'
            f"    subs: {key}Subs as SubEntry[],\n"
            f'    audio: "audio/{name}-remix.wav",\n'
            f"    customShots: {custom},\n"
            f"  }},"
        )
    head = "\n".join([
        "import React from \"react\";",
        *imports,
        "import {DividerDemo} from \"./components/DividerDemo\";",
        "import {DividerCollapse} from \"./components/DividerCollapse\";",
        "import {FPS} from \"./theme\";",
        "",
        "export type Shot = {type: string; seconds: number; view?: string; [k: string]: unknown};",
        "export type SubEntry = {from: number; to: number; text: string; env?: number[]};",
        "",
        "/** 本文件由 gen_registry.py 生成——换集跑一次即可，勿手改。 */",
        "export type EpisodeDef = {",
        "  board: {shots: Shot[]};",
        "  subs: SubEntry[];",
        "  audio: string; // staticFile 相对路径",
        "  customShots: Record<string, React.FC<{durFrames: number}>>;",
        "};",
        "",
    ])
    body = (
        "export const EPISODES: Record<string, EpisodeDef> = {\n"
        + "\n".join(entries)
        + "\n};\n\n"
        + "export const episodeFrames = (ep: string): number =>\n"
        + "  Math.round(EPISODES[ep].board.shots.reduce((a, s) => a + s.seconds, 0) * FPS);\n"
    )
    (SRC / "episodes.ts").write_text(head + body, encoding="utf-8")
    print(f"episodes.ts 重建：{len(boards)} 集")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

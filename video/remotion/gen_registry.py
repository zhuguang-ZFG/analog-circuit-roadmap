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
import re
import sys

# Standalone script: import the shared Python contract, never generated TS.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from storyboard_lint import CUSTOM_VIEWS as CUSTOM, SVG_DIR, ValidationError, load_storyboard

SRC = Path(__file__).resolve().parent / "src"


def main() -> int:
    boards = sorted(SRC.glob("data/ep*.json"))
    boards = [b for b in boards if not b.name.endswith("-subs.json")]
    if not boards:
        print(f"{SRC / 'data'}: $: no episode storyboards found", file=sys.stderr)
        return 1
    imports, entries, errors = [], [], []
    components = set()
    for b in boards:
        key = b.stem
        # The filename also becomes a TypeScript identifier and import path.
        if not re.fullmatch(r"ep[0-9]+", key):
            errors.append(f"{b}: registration: expected epNN.json filename")
            continue
        views = CUSTOM.get(key, {})
        try:
            board = load_storyboard(b, svg_dir=SVG_DIR, custom_views=views)
        except ValidationError as exc:
            errors.append(str(exc))
            continue
        name = board["name"]
        imports.append(f'import {key}Board from "./data/{key}.json";')
        imports.append(f'import {key}Subs from "./data/{key}-subs.json";')
        custom = "{" + ", ".join(f"{view}: {component}" for view, component in views.items()) + "}"
        components.update(views.values())
        entries.append(
            f"  {key}: {{\n"
            f'    board: {key}Board as {{shots: Shot[]}},\n'
            f"    subs: {key}Subs as SubEntry[],\n"
            f'    audio: {json.dumps(f"audio/{name}-remix.wav")},\n'
            f"    customShots: {custom},\n"
            f"  }},"
        )
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1  # Keep the existing episodes.ts intact if any input is invalid.
    head = "\n".join([
        "import React from \"react\";",
        *imports,
        *(f'import {{{component}}} from "./components/{component}";' for component in sorted(components)),
        "import {FPS} from \"./theme\";",
        "",
        "export type Shot = {type: string; seconds: number; view?: string; [k: string]: unknown};",
        "export type SubEntry = {from: number; to: number; text: string; env?: number[]; charFrames?: number[]};",
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

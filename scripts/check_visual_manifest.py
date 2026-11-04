#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""视觉资产 manifest 闸：登记齐全、来源可回对、prompt 可追溯。

`--bootstrap-legacy`：把磁盘上尚未登记的 svg/图形/照片补成
`legacy-unreviewed` 条目（幂等，只增不改）。
默认模式：校验全部条目；任何违规退出码 1。
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "docs" / "superpowers" / "visual" / "visual-manifest.yml"
LOCK = ROOT / "docs" / "superpowers" / "visual" / "handraw-style-lock.md"

KINDS = {"figure", "animation", "photo"}
TYPES = {f"V{n}" for n in range(1, 7)} | {f"A{n}" for n in range(1, 6)}
STATUSES = ["legacy-unreviewed", "planned", "generated", "reviewed",
            "accepted", "published"]
REVIEWED = {"reviewed", "accepted", "published"}
SCORE_DIMS = ["教学必要性", "事实精度", "构图层级", "风格一致性", "印刷可读性"]
ANIM_DIMS = ["运动叙事", "交互节奏"]
NUMBER = re.compile(r"\d")

DISK_GLOBS = [
    ("assets/svg", "*.svg", "animation"),
    ("assets/figures", "*.svg", "figure"),
    ("assets/photos", "**/*.jpg", "photo"),
    ("assets/photos", "**/*.png", "photo"),
]


def load(path: Path = MANIFEST) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def dump(data: dict, path: Path = MANIFEST) -> None:
    path.write_text(
        yaml.safe_dump(data, allow_unicode=True, sort_keys=False, width=100),
        encoding="utf-8")


def disk_assets() -> list[tuple[Path, str]]:
    """调用期拼路径，保证测试替换 ROOT 后仍指向夹具目录。"""
    found = []
    for rel, pattern, kind in DISK_GLOBS:
        found += [(p, kind) for p in sorted((ROOT / rel).glob(pattern))]
    return found


def chapter_of(asset: Path) -> int:
    """正文里哪个章节引用了这个资产。"""
    rel = asset.relative_to(ROOT).as_posix()
    for doc in sorted((ROOT / "docs").glob("p*-ch*.md")):
        m = re.search(r"-ch(\d+)\.md$", doc.name)
        if m and rel in doc.read_text(encoding="utf-8"):
            return int(m.group(1))
    return -1


def legacy_id(asset: Path) -> str:
    stem = asset.stem.replace("_", "-")
    return f"legacy-{asset.parent.name}-{stem}"


def bootstrap(data: dict) -> int:
    data.setdefault("meta", {})
    data["meta"]["lock"] = LOCK.relative_to(
        Path(__file__).resolve().parents[1]).as_posix()
    data["meta"]["statuses"] = STATUSES
    assets = data.setdefault("assets", [])
    known = {a.get("output") for a in assets}
    added = 0
    for asset, kind in disk_assets():
        rel = asset.relative_to(ROOT).as_posix()
        if rel in known:
            continue
        n = chapter_of(asset)
        assets.append({
            "id": legacy_id(asset),
            "chapter": n if n >= 0 else 0,
            "kind": kind,
            "type": "A1" if kind == "animation" else "V6" if kind == "photo" else "V2",
            "anchor": "",
            "purpose": "改造前存量资产，待逐张审查（Rebuild/Retire/Keep）",
            "source_facts": [],
            "prompt_file": "",
            "output": rel,
            "print_fallback": "",
            "status": "legacy-unreviewed",
        })
        known.add(rel)
        added += 1
    return added


def front_matter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        return {}
    return yaml.safe_load(m.group(1)) or {}


def check(data: dict) -> list[str]:
    bad: list[str] = []
    assets = data.get("assets") or []
    ids = [a.get("id") for a in assets]
    dupes = {i for i in ids if ids.count(i) > 1}
    if dupes:
        bad.append(f"ID 重复: {sorted(dupes)}")
    if data.get("meta", {}).get("statuses") != STATUSES:
        bad.append("meta.statuses 与状态机不一致")
    for a in assets:
        tag = a.get("id") or "<无 id>"
        if a.get("status") not in STATUSES:
            bad.append(f"{tag}: 非法状态 {a.get('status')!r}")
        if a.get("kind") not in KINDS:
            bad.append(f"{tag}: 非法 kind {a.get('kind')!r}")
        if a.get("type") not in TYPES:
            bad.append(f"{tag}: 非法 type {a.get('type')!r}")
        ch = a.get("chapter")
        if not isinstance(ch, int) or not 0 <= ch <= 18:
            bad.append(f"{tag}: chapter {ch!r} 不在 0..18")
        output = a.get("output") or ""
        if output and not (ROOT / output).exists():
            bad.append(f"{tag}: output 不存在 {output}")
        if a.get("status") == "legacy-unreviewed":
            continue
        for field in ("anchor", "purpose", "style_id", "layout_id",
                      "color_ids", "source_facts", "prompt_file",
                      "print_fallback"):
            if not a.get(field):
                bad.append(f"{tag}: 缺 {field}")
        prompt = a.get("prompt_file")
        if prompt:
            path = ROOT / prompt
            if not path.exists():
                bad.append(f"{tag}: prompt 记录不存在 {prompt}")
            else:
                record = front_matter(path)
                if record.get("id") != a.get("id"):
                    bad.append(f"{tag}: prompt 记录 id 不匹配")
                if not record.get("zh_prompt") or not record.get("en_prompt"):
                    bad.append(f"{tag}: prompt 缺中/英文本")
                docs = " ".join(
                    (ROOT / f.split("#")[0]).read_text(encoding="utf-8")
                    for f in a.get("source_facts") or []
                    if (ROOT / f.split("#")[0]).exists())
                for num in record.get("numbers") or []:
                    if NUMBER.search(str(num)) and str(num) not in docs:
                        bad.append(f"{tag}: 数值 {num!r} 在来源正文里找不到")
        for fact in a.get("source_facts") or []:
            fpath, _, heading = fact.partition("#")
            path = ROOT / fpath
            if not path.exists():
                bad.append(f"{tag}: source_facts 文件不存在 {fpath}")
            elif heading and heading.strip() not in path.read_text(encoding="utf-8"):
                bad.append(f"{tag}: source_facts 锚点找不到 {heading!r}")
        if a.get("status") in REVIEWED:
            scores = a.get("review_scores") or {}
            dims = SCORE_DIMS + (ANIM_DIMS if a.get("kind") == "animation" else [])
            for dim in dims:
                val = scores.get(dim)
                if not isinstance(val, (int, float)) or val < 4:
                    bad.append(f"{tag}: 评分「{dim}」<4 或缺")
    registered = {a.get("output") for a in assets}
    for asset, _kind in disk_assets():
        rel = asset.relative_to(ROOT).as_posix()
        if rel not in registered:
            bad.append(f"磁盘资产未登记: {rel}")
    return bad


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--bootstrap-legacy", action="store_true")
    ap.add_argument("--manifest", type=Path, default=MANIFEST)
    args = ap.parse_args(argv)
    data = load(args.manifest) if args.manifest.exists() else {}
    if args.bootstrap_legacy:
        added = bootstrap(data)
        if added:
            dump(data, args.manifest)
        print(f"bootstrap: 新增 {added} 条 legacy-unreviewed，"
              f"共 {len(data.get('assets') or [])} 条")
        return 0
    bad = check(data)
    for line in bad:
        print("FAIL " + line)
    print(f"manifest: {'FAIL' if bad else 'PASS'}（{len(bad)} 项）")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())

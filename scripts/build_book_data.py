#!/usr/bin/env python3
"""从 docs/ 生成书内动画台账；种子索引与审读表只在缺失时写入。"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
BOOK = ROOT / "analog-book"
DOCS = ROOT / "docs"
DATA = BOOK / "data"
sys.path.insert(0, str(BOOK))

from book.data import pinyin_key  # noqa: E402

DEMO_HEAD = re.compile(r'^## (5\.\d+)\s+(.+?)\s*<a id="(demo\d+)"')
DEMO_IMG = re.compile(r'<img src="assets/svg/([\w\-]+\.svg)"[^>]*alt="([^"]*)"')
DEMO_LINK = re.compile(r"\[(5\.\d+)\]\((?:[\w\-]+\.md)?#(demo\d+)\)")
CHAPTER_ROW = re.compile(r"^\|\s*§(\d+)\s+(第\s*\d+\s*章[^|]*?)\s*\|")
LOOK_RE = re.compile(r"\*\*看点\*\*[：:]\s*(.+)")

CHAPTER_FILES = [
    "p1-01-ch0", "p1-02-ch1", "p1-03-ch2", "p1-04-ch3", "p1-05-ch4",
    "p1-06-ch5", "p1-07-ch6", "p1-08-ch7", "p1-09-ch8", "p1-10-ch9",
    "p1-11-ch10", "p2-01-ch11", "p2-02-ch12", "p2-03-ch13", "p3-01-ch14",
    "p3-02-ch15", "p4-01-ch16", "p4-02-ch17", "p4-03-ch18",
]

SEED_INDEX = [
    ("电压", "voltage", 0), ("欧姆定律", "Ohm's law", 0),
    ("恒压源", "ideal voltage source", 0), ("恒流源", "ideal current source", 0),
    ("分压器", "voltage divider", 1), ("戴维南等效", "Thevenin equivalent", 1),
    ("电容", "capacitor", 1), ("电感", "inductor", 1),
    ("阻抗", "impedance", 1), ("谐振", "resonance", 1),
    ("二极管", "diode", 2), ("正向压降", "forward voltage", 2),
    ("齐纳击穿", "Zener breakdown", 2),
    ("BJT", "bipolar junction transistor", 3),
    ("静态工作点", "quiescent point", 3), ("跨导", "transconductance", 3),
    ("MOSFET", "MOSFET", 4), ("阈值电压", "threshold voltage", 4),
    ("米勒效应", "Miller effect", 4),
    ("推挽输出", "push-pull output", 5), ("开漏输出", "open-drain output", 5),
    ("运算放大器", "operational amplifier", 6), ("虚短", "virtual short", 6),
    ("共模抑制比", "common-mode rejection ratio", 6),
    ("增益带宽积", "gain-bandwidth product", 6),
    ("比较器", "comparator", 7), ("迟滞", "hysteresis", 7),
    ("模拟开关", "analog switch", 8),
    ("电压基准", "voltage reference", 9),
    ("低压差稳压器", "low-dropout regulator", 9),
    ("555 定时器", "555 timer", 10), ("占空比", "duty cycle", 10),
    ("差分对", "differential pair", 11), ("电流镜", "current mirror", 11),
    ("Sallen-Key 滤波器", "Sallen-Key filter", 12),
    ("Buck 变换器", "buck converter", 13), ("相位裕度", "phase margin", 13),
    ("误差预算", "error budget", 14), ("回流路径", "return current path", 15),
    ("探头负载", "probe loading", 16),
]


def _plain(text):
    text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)
    text = text.replace("**", "").replace("`", "")
    return re.sub(r"\s+", " ", text).strip()


SENTENCE_END = "。；！？"
CLAUSE_END = "，、:"
TRAILING = "、，；：,;:（→"


def _last_unmatched(text, opening, closing):
    stack = []
    for index, char in enumerate(text):
        if char == opening:
            stack.append(index)
        elif char == closing and stack:
            stack.pop()
    return stack[-1] if stack else None


def summarize(text, limit=120):
    """按句末/分句边界截断，保证摘要不切断词、公式或括号。"""
    if len(text) <= limit:
        return text
    window = text[:limit - 1]
    cut = max(window.rfind(char) for char in SENTENCE_END)
    if cut < 0:
        cut = max(window.rfind(char) for char in CLAUSE_END)
    if cut >= 0:
        summary = window[:cut + 1]
    else:
        space = max(window.rfind(char) for char in " \t")
        summary = window[:space] if space >= 0 else window
    if summary.count("$") % 2:
        summary = summary[:summary.rfind("$")]
    while summary.count("（") > summary.count("）"):
        unmatched = _last_unmatched(summary, "（", "）")
        if unmatched is None:
            break
        summary = summary[:unmatched]
    summary = summary.rstrip()
    while summary and summary[-1] in TRAILING:
        summary = summary[:-1].rstrip()
    if not summary.endswith(("。", "！", "？")):
        summary += "…"
    return summary


def build_animations():
    lines = (DOCS / "p5-00-part5.md").read_text(encoding="utf-8").splitlines()
    chapter_of = {}
    for line in lines:
        match = CHAPTER_ROW.match(line)
        if match:
            for _num, demo in DEMO_LINK.findall(line):
                chapter_of[demo] = int(match.group(1))
    items, current, body = [], None, []

    def finish():
        nonlocal current, body
        if current is None:
            return
        if not current["svg"]:
            raise SystemExit(f'{current["anchor"]}: 缺少 SVG')
        look = None
        for line in body:
            found = LOOK_RE.search(line)
            if found:
                look = _plain(found.group(1))
                break
        if not look:
            look = current["title"]
        chapter = chapter_of.get(current["anchor"])
        if chapter is None:
            raise SystemExit(f'{current["anchor"]}: 章节映射表缺少该动画')
        items.append({
            "id": f"anim-{len(items) + 1:03d}",
            "file": "p5-00-part5.md",
            "title": current["title"],
            "chapter": chapter,
            "anchor": current["anchor"],
            "one_line": summarize(look),
            "static_svg": "assets/svg/" + current["svg"],
        })
        current, body = None, []

    for line in lines:
        match = DEMO_HEAD.match(line)
        if match:
            finish()
            current = {"num": match.group(1), "title": _plain(match.group(2)),
                       "anchor": match.group(3), "svg": ""}
            continue
        if current is not None:
            if not current["svg"]:
                image = DEMO_IMG.search(line)
                if image:
                    current["svg"] = image.group(1)
                    continue
            body.append(line)
    finish()
    if len(items) != 108:
        raise SystemExit(f"动画应为 108 条，解析到 {len(items)}")
    for item in items:
        if not (ROOT / item["static_svg"]).is_file():
            raise SystemExit(f'缺少图片 {item["static_svg"]}')
    return items


def build_index_terms():
    terms = []
    for term, english, chapter in SEED_INDEX:
        anchor = "page-" + CHAPTER_FILES[chapter]
        terms.append({"term": term, "english": english, "primary": anchor,
                      "anchors": [anchor], "see_also": []})
    return sorted(terms, key=lambda item: (pinyin_key(item["term"]), item["term"]))


def build_signoffs():
    return [{"chapter": i, "draft_version": "2.0.0-draft.1",
             "technical_reviewer": "", "editorial_reviewer": "",
             "safety_reviewer": "", "date": "2026-10-25", "open_issues": []}
            for i in range(19)]


def dump(path, value):
    text = yaml.safe_dump(value, allow_unicode=True, sort_keys=False, width=100)
    if path.is_file() and path.read_text(encoding="utf-8") == text:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return True


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    animations = build_animations()
    if args.check:
        path = DATA / "animations.yml"
        if not path.is_file():
            print("缺少 animations.yml，请运行 --write", file=sys.stderr)
            return 1
        current = yaml.safe_load(path.read_text(encoding="utf-8"))
        if current != animations:
            print("animations.yml 与 p5-00-part5.md 不一致，请运行 --write", file=sys.stderr)
            return 1
        return 0
    if not args.write:
        parser.error("需要 --write 或 --check")
    dump(DATA / "animations.yml", animations)
    for name, value in (("index-terms.yml", build_index_terms()),
                        ("chapter-signoff.yml", build_signoffs()),
                        ("sources.yml", []),
                        ("references.yml", [])):
        path = DATA / name
        if not path.exists():
            dump(path, value)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

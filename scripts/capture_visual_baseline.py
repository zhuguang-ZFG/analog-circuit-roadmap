"""补录冻结 SVG 的正文引用/打印回退，以及本地 PDF 对照；不改写原章节基线。"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / "docs/superpowers/visual/baseline-2026-11-04.json"
sys.path.insert(0, str(ROOT / "analog-book"))
from book.storyboard import build_storyboard, caption_beats
from book.svg_refine import is_animated_svg, refine_svg


def frozen_file(head: str, path: str) -> bytes:
    return subprocess.run(["git", "show", f"{head}:{path}"], cwd=ROOT,
                          check=True, capture_output=True).stdout


def enrich(data: dict) -> None:
    head = data["meta"]["head"]
    counts = Counter(src for chapter in data["chapters"] for src in chapter["assets"])
    rows = []
    for filename in data["inventory"]["svg_animations"]["sha256"]:
        path = f"assets/svg/{filename}"
        raw = frozen_file(head, path)
        text = raw.decode("utf-8")
        animated = is_animated_svg(text)
        printed = build_storyboard(text, refine_svg(text)) if animated else refine_svg(text)
        tree = ET.fromstring(printed)
        remaining = [node.tag for node in tree.iter()
                     if node.tag.rsplit("}", 1)[-1] in {"animate", "animateMotion", "animateTransform", "set"}]
        beats = len(caption_beats(text))
        rows.append({"path": path, "git_sha256": hashlib.sha256(raw).hexdigest(),
                     "body_references": counts[path],
                     "chapters": [c["chapter"] for c in data["chapters"] if path in c["assets"]],
                     "print_storyboard": {
                         "status": "pass" if not remaining else "fail-motion-remains",
                         "frames": min(beats, 5) if beats >= 2 else 3 if animated else 1,
                         "sha256": hashlib.sha256(printed.encode()).hexdigest(),
                         "viewBox": tree.get("viewBox")}})
    data["inventory"]["svg_animations"]["details"] = rows
    data["inventory"]["svg_animations"]["details_provenance"] = {
        "source_head": head, "measured_on": "2026-11-05",
        "method": "Frozen source rendered in memory by the recorded print pipeline; not a claim about an archived PDF.",
        "pipeline_sha256": {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
                            for name in ("analog-book/book/storyboard.py", "analog-book/book/svg_refine.py")}}


def pdf_record(path: Path) -> dict:
    from pypdf import PdfReader
    reader = PdfReader(path)
    sizes = Counter((round(float(p.mediabox.width), 2), round(float(p.mediabox.height), 2))
                    for p in reader.pages)
    return {"path": path.relative_to(ROOT).as_posix(), "bytes": path.stat().st_size,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "pages": len(reader.pages),
            "modified_utc": datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat(),
            "page_sizes_pt": [{"width": w, "height": h, "count": n} for (w, h), n in sizes.items()]}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--enrich", action="store_true", help="补充原基线；原有章节统计与 SHA 不动")
    ap.add_argument("--pdf-out", type=Path, default=ROOT / "build/visual-baseline/pdf-baseline-2026-11-05.json")
    args = ap.parse_args(argv)
    if args.enrich:
        data = json.loads(BASELINE.read_text(encoding="utf-8"))
        enrich(data)
        BASELINE.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(f"补录 {len(data['inventory']['svg_animations']['details'])} 张冻结 SVG")
    paths = [ROOT / "analog-book/dist/analog-circuit-book.pdf"] + [
        ROOT / f"analog-book/dist/print/volume-{i}/analog-circuit-book.pdf" for i in (1, 2)]
    report = {"measured_on": "2026-11-05", "scope": "Local artifacts at capture time; source commit not inferred.",
              "pdfs": [pdf_record(p) for p in paths if p.is_file()],
              "missing": [p.relative_to(ROOT).as_posix() for p in paths if not p.is_file()]}
    args.pdf_out.parent.mkdir(parents=True, exist_ok=True)
    args.pdf_out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for p in report["pdfs"]:
        print(f"{p['path']}: {p['pages']} 页 / {p['bytes']} bytes")
    print(f"PDF 对照 → {args.pdf_out.relative_to(ROOT)}")
    return int(bool(report["missing"]))


if __name__ == "__main__":
    raise SystemExit(main())

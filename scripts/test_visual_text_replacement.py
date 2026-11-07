#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""图文职责审计：replaces-text 记录须与正文、图注和实际字数一致。

同时报告两类文体问题（不阻断）：
- 图注整句复制正文；
- 同一公式出现在图前正文、图注、图后正文三处。
"""
from __future__ import annotations

import html
import re
import tempfile
import unittest
from pathlib import Path

import yaml

from visual_fidelity import source_excerpt

ROOT = Path(__file__).resolve().parents[1]
RECORD_GLOB = "docs/superpowers/visual/reviews/*/text-replacements.yml"
REQUIRED = ("id", "source", "before", "after", "caption",
            "removed_prose_chars", "relationship")
FIGURE = re.compile(r"<figure\b.*?</figure>", re.S | re.I)
CAPTION = re.compile(r"<figcaption\b[^>]*>(.*?)</figcaption>", re.S | re.I)
IMG = re.compile(r"<img\b[^>]*\bsrc\s*=\s*[\"']([^\"']+)[\"']", re.I)
TAG = re.compile(r"<[^>]+>")
FORMULA = re.compile(r"\$\$.+?\$\$|\$[^$\n]+\$")
SENTENCE = re.compile(r"[^。！？；\n]+[。！？；]?")
PARAGRAPH = re.compile(r"\n\s*\n")


def squash(text: str) -> str:
    """去掉空白与 Markdown 强调符，只比较实际文字。"""
    return re.sub(r"[\s*_`]+", "", text)


def nonws(text: str) -> int:
    return len(re.sub(r"\s", "", text))


def plain(text: str) -> str:
    return html.unescape(re.sub(r"\s+", " ", TAG.sub("", text))).strip()


def load_records(root: Path) -> list[tuple[str, str, dict]]:
    rows = []
    for path in sorted(root.glob(RECORD_GLOB)):
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        for index, record in enumerate(data.get("changes") or [], 1):
            rows.append((path.relative_to(root).as_posix(), f"#{index}", record))
    return rows


def manifest_outputs(root: Path) -> dict[str, str]:
    path = root / "docs" / "superpowers" / "visual" / "visual-manifest.yml"
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return {asset["id"]: str(asset.get("output") or "")
            for asset in data.get("assets") or [] if asset.get("id")}


def find_figure(doc: str, output: str) -> tuple[str, str] | None:
    for block in FIGURE.findall(doc):
        sources = IMG.findall(block)
        if any(src == output or Path(src).name == Path(output).name
               for src in sources):
            caption = CAPTION.search(block)
            return block, (plain(caption.group(1)) if caption else "")
    return None


def formulas(text: str) -> set[str]:
    return {re.sub(r"\s+", "", item) for item in FORMULA.findall(text)
            if len(re.sub(r"\s+", "", item)) >= 6}


def _paragraphs(text: str) -> list[str]:
    return [part.strip() for part in PARAGRAPH.split(text) if part.strip()]


def audit(root: Path = ROOT) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    outputs = manifest_outputs(root)
    for where, position, record in load_records(root):
        tag = f"{where}{position} {record.get('id', '?')}"
        if not isinstance(record, dict):
            errors.append(f"{tag}: 记录不是映射")
            continue
        missing = [key for key in REQUIRED
                   if not str(record.get(key, "")).strip()]
        if missing:
            errors.append(f"{tag}: 缺少字段 {', '.join(missing)}")
            continue
        if record["relationship"] != "replaces-text":
            errors.append(f"{tag}: relationship 须为 replaces-text")
        asset_id = str(record["id"])
        output = outputs.get(asset_id)
        if not output:
            errors.append(f"{tag}: manifest 中没有该 id 或缺少 output")
            continue
        reference = str(record["source"])
        filename = reference.partition("#")[0]
        try:
            excerpt = source_excerpt(root, reference)
        except ValueError as exc:
            errors.append(f"{tag}: {exc}")
            continue
        doc_path = root / filename
        if not doc_path.is_file():
            errors.append(f"{tag}: 正文文件不存在 {filename}")
            continue
        doc = doc_path.read_text(encoding="utf-8")
        figure = find_figure(doc, output)
        if figure is None:
            errors.append(f"{tag}: 正文里找不到 {output} 的 figure")
            continue
        block, caption = figure
        if squash(caption) != squash(str(record["caption"])):
            errors.append(f"{tag}: 记录图注与正文 figcaption 不一致")
        if squash(str(record["after"])) not in squash(excerpt):
            errors.append(f"{tag}: 精炼导读没有出现在来源小节")
        if squash(str(record["before"])) in squash(excerpt):
            errors.append(f"{tag}: 被替代的旧段落仍留在来源小节")
        try:
            declared = int(record["removed_prose_chars"])
        except (TypeError, ValueError):
            errors.append(f"{tag}: removed_prose_chars 不是整数")
            continue
        actual = nonws(str(record["before"])) - nonws(str(record["after"]))
        if declared != actual:
            errors.append(
                f"{tag}: removed_prose_chars={declared}，按记录文字应为 {actual}")

        body = plain(FIGURE.sub("", excerpt))
        caption_key = squash(caption)
        copied = sorted({squash(item) for item in SENTENCE.findall(body)
                         if len(squash(item)) >= 14
                         and squash(item) in caption_key})
        for item in copied:
            warnings.append(f"{tag}: 图注整句复制正文「{item[:24]}…」")

        start = doc.find(block)
        end = start + len(block)
        if start >= 0:
            before = [formulas(part) for part in _paragraphs(doc[:start])[-3:]]
            after = [formulas(part) for part in _paragraphs(doc[end:])[:3]]
            left = set().union(*before) if before else set()
            right = set().union(*after) if after else set()
            repeated = formulas(caption) & left & right
            for item in sorted(repeated):
                warnings.append(f"{tag}: 公式在图前、图注、图后各出现一次 {item}")
    return errors, warnings


class TextReplacementFixtureTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / "docs/superpowers/visual/reviews/demo").mkdir(parents=True)
        (self.root / "docs/superpowers/visual").mkdir(parents=True, exist_ok=True)

    def write(self, doc: str, record: dict, output="assets/figures/demo.svg",
              asset_id="demo"):
        (self.root / "docs/ch.md").write_text(doc, encoding="utf-8")
        manifest = {"assets": [{"id": asset_id, "output": output}]}
        (self.root / "docs/superpowers/visual/visual-manifest.yml").write_text(
            yaml.safe_dump(manifest, allow_unicode=True), encoding="utf-8")
        data = {"changes": [{"relationship": "replaces-text", **record}]}
        (self.root / "docs/superpowers/visual/reviews/demo/"
         "text-replacements.yml").write_text(
            yaml.safe_dump(data, allow_unicode=True), encoding="utf-8")

    def valid_record(self, **overrides):
        record = {
            "id": "demo",
            "source": "docs/ch.md#1.0",
            "before": "旧段落很长，解释得很啰嗦。",
            "after": "新导读一句话。",
            "caption": "图注说明。",
            "removed_prose_chars": 6,
            "relationship": "replaces-text",
        }
        record.update(overrides)
        return record

    def test_valid_record_has_no_findings(self):
        self.write(
            "## 1.0 演示\n\n新导读一句话。\n\n"
            '<figure><img src="assets/figures/demo.svg">'
            "<figcaption>图注说明。</figcaption></figure>\n",
            self.valid_record())
        errors, warnings = audit(self.root)
        self.assertEqual([], errors)
        self.assertEqual([], warnings)

    def test_caption_mismatch_is_error(self):
        self.write(
            "## 1.0 演示\n\n新导读一句话。\n\n"
            '<figure><img src="assets/figures/demo.svg">'
            "<figcaption>另一句图注。</figcaption></figure>\n",
            self.valid_record())
        errors, _ = audit(self.root)
        self.assertTrue(any("figcaption" in item for item in errors))

    def test_old_paragraph_still_present_is_error(self):
        self.write(
            "## 1.0 演示\n\n新导读一句话。旧段落很长，解释得很啰嗦。\n\n"
            '<figure><img src="assets/figures/demo.svg">'
            "<figcaption>图注说明。</figcaption></figure>\n",
            self.valid_record())
        errors, _ = audit(self.root)
        self.assertTrue(any("旧段落" in item for item in errors))

    def test_missing_refined_intro_is_error(self):
        self.write(
            "## 1.0 演示\n\n只有旧内容。\n\n"
            '<figure><img src="assets/figures/demo.svg">'
            "<figcaption>图注说明。</figcaption></figure>\n",
            self.valid_record())
        errors, _ = audit(self.root)
        self.assertTrue(any("精炼导读" in item for item in errors))

    def test_removed_chars_must_match_record(self):
        self.write(
            "## 1.0 演示\n\n新导读一句话。\n\n"
            '<figure><img src="assets/figures/demo.svg">'
            "<figcaption>图注说明。</figcaption></figure>\n",
            self.valid_record(removed_prose_chars=99))
        errors, _ = audit(self.root)
        self.assertTrue(any("removed_prose_chars" in item for item in errors))

    def test_unknown_asset_is_error(self):
        self.write(
            "## 1.0 演示\n\n新导读一句话。\n\n"
            '<figure><img src="assets/figures/demo.svg">'
            "<figcaption>图注说明。</figcaption></figure>\n",
            self.valid_record(id="missing"), asset_id="demo")
        errors, _ = audit(self.root)
        self.assertTrue(any("manifest" in item for item in errors))

    def test_caption_copying_body_sentence_warns(self):
        sentence = "电容鼓包通常说明纹波电流长期超标。"
        self.write(
            "## 1.0 演示\n\n新导读一句话。\n\n"
            f"<p>{sentence}</p>\n"
            '<figure><img src="assets/figures/demo.svg">'
            f"<figcaption>{sentence}</figcaption></figure>\n",
            self.valid_record(caption=sentence))
        _, warnings = audit(self.root)
        self.assertTrue(any("整句复制" in item for item in warnings))

    def test_formula_in_before_caption_after_warns(self):
        formula = r"$T_J = T_A + P \times \theta_{JA}$"
        self.write(
            "## 1.0 演示\n\n"
            f"新导读一句话。前面写 {formula}。\n\n"
            '<figure><img src="assets/figures/demo.svg">'
            f"<figcaption>图注说明 {formula}。</figcaption></figure>\n\n"
            f"后面再写 {formula}。\n",
            self.valid_record(caption=f"图注说明 {formula}。"))
        _, warnings = audit(self.root)
        self.assertTrue(any("公式" in item for item in warnings))


class RepositoryRecordTests(unittest.TestCase):
    def test_records_match_published_text(self):
        errors, _ = audit(ROOT)
        self.assertEqual([], errors)


if __name__ == "__main__":
    findings, notes = audit()
    for line in findings:
        print("FAIL " + line)
    for line in notes:
        print("WARN " + line)
    print(f"{len(findings)} errors, {len(notes)} warnings")
    unittest.main()

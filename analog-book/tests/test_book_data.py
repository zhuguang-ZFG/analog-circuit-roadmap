#!/usr/bin/env python3
"""数据台账：动画 108、索引、来源、审读、文献与拼音排序。"""
import copy
import sys
import tempfile
import unittest
from pathlib import Path

BOOK = Path(__file__).resolve().parent.parent
ROOT = BOOK.parent
sys.path.insert(0, str(BOOK))
sys.path.insert(0, str(ROOT / "scripts"))

from book import data  # noqa: E402
from book.manifest import BookError  # noqa: E402
import book_fixtures  # noqa: E402


_TEMPDIRS = []


def fixture_data():
    # 目录必须在断言期间保持存在；返回后由临时目录对象负责清理。
    tmp = tempfile.TemporaryDirectory()
    _TEMPDIRS.append(tmp)
    root = Path(tmp.name)
    data_dir = book_fixtures.write_data(root / "data")
    (root / "assets" / "svg").mkdir(parents=True)
    (root / "assets" / "svg" / "fixture.svg").write_text("<svg/>", encoding="utf-8")
    return (data.load_list(data_dir / "animations.yml"),
            data.load_list(data_dir / "index-terms.yml"),
            root)


class AnimationTests(unittest.TestCase):
    def test_fixture_has_108_and_covers_every_chapter(self):
        items, _, root = fixture_data()
        data.validate_animations(items, static_root=root)
        chapters = {item["chapter"] for item in items}
        self.assertEqual(set(range(19)), chapters)

    def test_rejects_duplicate_and_missing_file(self):
        items, _, root = fixture_data()
        broken = copy.deepcopy(items)
        broken[1]["anchor"] = broken[0]["anchor"]
        with self.assertRaisesRegex(BookError, "anchor"):
            data.validate_animations(broken, static_root=root)
        broken = copy.deepcopy(items)
        broken[0]["static_svg"] = "assets/svg/missing.svg"
        with self.assertRaisesRegex(BookError, "不存在"):
            data.validate_animations(broken, static_root=root)

    def test_real_generator_matches_committed_yaml(self):
        import build_book_data
        generated = build_book_data.build_animations()
        self.assertEqual(108, len(generated))
        committed = data.load_list(BOOK / "data" / "animations.yml")
        self.assertEqual(generated, committed)
        data.validate_animations(committed)


class IndexTests(unittest.TestCase):
    def test_anchors_must_exist_and_terms_are_unique(self):
        terms = [{"term": "米勒效应", "english": "Miller effect",
                  "primary": "page-p1-01-ch0", "anchors": ["page-p1-01-ch0"],
                  "see_also": []}]
        data.validate_index_terms(terms, {"page-p1-01-ch0"})
        with self.assertRaisesRegex(BookError, "锚点"):
            data.validate_index_terms(terms, {"page-other"})
        duplicated = terms + copy.deepcopy(terms)
        with self.assertRaisesRegex(BookError, "重复"):
            data.validate_index_terms(duplicated, {"page-p1-01-ch0"})

    def test_final_requires_300_terms(self):
        anchor = "page-p1-01-ch0"
        terms = [{"term": f"术语{i:03d}", "english": f"Term {i}",
                  "primary": anchor, "anchors": [anchor], "see_also": []}
                 for i in range(300)]
        data.validate_index_terms(terms, {anchor}, final=True)
        with self.assertRaisesRegex(BookError, "300"):
            data.validate_index_terms(terms[:-1], {anchor}, final=True)

    def test_pinyin_sorting_and_sections(self):
        terms = [{"term": "欧姆定律", "english": "Ohm's law",
                  "primary": "p", "anchors": ["p"], "see_also": []},
                 {"term": "米勒效应", "english": "Miller effect",
                  "primary": "p", "anchors": ["p"], "see_also": []}]
        self.assertTrue(data.pinyin_key("米勒效应").startswith("mile"))
        sections = data.index_sections(terms)
        self.assertEqual(["M", "O"], [letter for letter, _ in sections])
        self.assertEqual("米勒效应", sections[0][1][0]["term"])


class SourceTests(unittest.TestCase):
    def source(self, **overrides):
        item = {"id": "ch06-datasheet-lm358", "chapter": 6,
                "claim": "LM358 的 GBW 约 0.7MHz", "source_type": "数据手册",
                "citation": "Texas Instruments, LM358 datasheet, 2023",
                "url_or_doi": "https://example.test/lm358.pdf",
                "verified_on": "2026-10-20", "verifier": "zuguang"}
        item.update(overrides)
        return item

    def test_final_requires_all_used_and_no_unused(self):
        item = self.source()
        data.validate_sources([item], {"ch06-datasheet-lm358"}, final=True)
        with self.assertRaisesRegex(BookError, "未使用"):
            data.validate_sources([item], set(), final=True)
        with self.assertRaisesRegex(BookError, "不存在"):
            data.validate_sources([item], {"ch06-datasheet-lm358", "missing"},
                                  final=True)

    def test_rejects_unknown_type_and_bad_date(self):
        with self.assertRaisesRegex(BookError, "source_type"):
            data.validate_sources([self.source(source_type="博客")])
        with self.assertRaisesRegex(BookError, "verified_on"):
            data.validate_sources([self.source(verified_on="2026/10/20")])

    def test_marks_in_fragments(self):
        fragment = ('<sup class="source-ref" data-source="ch06-datasheet-lm358"></sup>'
                    '<p data-source="ch06-datasheet-lm358">x</p>')
        self.assertEqual({"ch06-datasheet-lm358"}, data.used_source_ids(fragment))


class SignoffAndReferenceTests(unittest.TestCase):
    def test_signoff_draft_then_final(self):
        items = [{"chapter": i, "draft_version": "2.0.0-draft.1",
                  "technical_reviewer": "", "editorial_reviewer": "",
                  "safety_reviewer": "", "date": "2026-10-25",
                  "open_issues": []} for i in range(19)]
        data.validate_signoffs(items)
        with self.assertRaisesRegex(BookError, "technical_reviewer"):
            data.validate_signoffs(items, final=True)
        for item in items:
            item.update(technical_reviewer="t", editorial_reviewer="e",
                        safety_reviewer="s")
        data.validate_signoffs(items, final=True)
        items[0]["open_issues"] = ["待核"]
        with self.assertRaisesRegex(BookError, "open_issues"):
            data.validate_signoffs(items, final=True)

    def test_references_final_minimum(self):
        item = {"id": "ref-001", "authors": "Horowitz, P.; Hill, W.",
                "title": "The Art of Electronics", "edition": "3rd",
                "publisher": "Cambridge University Press", "year": 2015,
                "isbn_or_url": "978-0521809269", "chapters": [1, 6, 11, 12]}
        data.validate_references([item])
        with self.assertRaisesRegex(BookError, "100"):
            data.validate_references([item], final=True)
        hundred = [dict(item, id=f"ref-{i:03d}", title=f"Book {i}")
                   for i in range(100)]
        data.validate_references(hundred, final=True)


if __name__ == "__main__":
    unittest.main()

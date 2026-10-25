#!/usr/bin/env python3
"""篇首插图与 19 章「先建立直觉」导读。"""
import re
import sys
import unittest
from pathlib import Path

BOOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BOOK))

from book import illustrations, intuition  # noqa: E402
from book.manifest import BookError  # noqa: E402

PART_NAMES = ["part-i.svg", "part-ii.svg", "part-iii.svg", "part-iv.svg",
              "part-v.svg"]
PART_PREFIXES = ["pi-", "pii-", "piii-", "piv-", "pv-"]
FORBIDDEN_TEXT = ("$", "\\", "**", "`", "\n")


class ChapterLeadTests(unittest.TestCase):
    def test_every_chapter_has_a_plain_lead(self):
        self.assertEqual(set(range(19)), set(intuition.CHAPTER_LEADS))
        for chapter, text in sorted(intuition.CHAPTER_LEADS.items()):
            self.assertGreaterEqual(len(text), 20, chapter)
            self.assertLessEqual(len(text), 110, chapter)
            self.assertTrue(text.endswith("。"), chapter)
            for token in FORBIDDEN_TEXT:
                self.assertNotIn(token, text, (chapter, token))

    def test_leads_are_unique(self):
        leads = list(intuition.CHAPTER_LEADS.values())
        self.assertEqual(19, len(set(leads)))

    def test_chapter_lead_html_is_scoped_and_escaped(self):
        page = intuition.chapter_lead(0)
        self.assertIn('class="chapter-intuition"', page)
        self.assertIn('class="ci-no" aria-hidden="true">00<', page)
        self.assertIn('class="ci-label">先建立直觉', page)
        self.assertIn('class="ci-text"', page)
        self.assertIn(intuition.CHAPTER_LEADS[0], page)
        with self.assertRaises(BookError):
            intuition.chapter_lead(19)


class PartArtTests(unittest.TestCase):
    def test_part_art_files_cover_all_five_parts(self):
        for name in PART_NAMES:
            svg = illustrations.part_art(name)
            self.assertTrue(svg.startswith("<svg"), name)
            self.assertIn('viewBox="0 0 760 260"', svg, name)
            self.assertIn('class="part-art-svg"', svg, name)

    def test_part_art_has_no_remote_or_active_content(self):
        for name in PART_NAMES:
            svg = illustrations.part_art(name)
            lowered = svg.lower()
            for token in ("<script", "<style", "<image", "<foreignobject",
                          "<iframe", "href=", "xlink:", "data:", "@import"):
                self.assertNotIn(token, lowered, (name, token))
            self.assertIsNone(re.search(r"\son[a-z]+\s*=", lowered), name)
            urls = set(re.findall(r"https?://[^\"'\s>]+", svg))
            self.assertLessEqual(urls, {"http://www.w3.org/2000/svg"}, name)
            for reference in re.findall(r"url\(([^)]*)\)", svg):
                self.assertTrue(reference.strip().startswith("#"),
                                (name, reference))

    def test_part_art_ids_are_unique_across_parts(self):
        seen: set[str] = set()
        for name, prefix in zip(PART_NAMES, PART_PREFIXES):
            for identifier in re.findall(r'id="([^"]+)"',
                                         illustrations.part_art(name)):
                self.assertTrue(identifier.startswith(prefix),
                                (name, identifier))
                self.assertNotIn(identifier, seen, (name, identifier))
                seen.add(identifier)

    def test_part_art_rejects_bad_names_and_missing_files(self):
        self.assertEqual("", illustrations.part_art(""))
        for name in ("../part-i.svg", "part-vi.svg", "part-i.txt",
                     "part-ix.svg", "part-i.svg/extra"):
            with self.assertRaises(BookError, msg=name):
                illustrations.part_art(name)

    def test_part_art_is_latin_only(self):
        for name in PART_NAMES:
            svg = illustrations.part_art(name)
            self.assertIsNone(re.search(r"[\u4e00-\u9fff]", svg), name)


if __name__ == "__main__":
    unittest.main()

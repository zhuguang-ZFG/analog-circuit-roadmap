#!/usr/bin/env python3
"""16K 上下卷：页面选取、各卷自有目录/索引、跨卷链接降级与分卷审计。"""
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

BOOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BOOK))

from book import assemble  # noqa: E402
from book.manifest import BookError, validate_manifest  # noqa: E402
import book_fixtures  # noqa: E402


class VolumeSplitTests(unittest.TestCase):
    """分卷必须重新装配，而不是截断已排好的单卷产物。"""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        root = Path(cls.tmp.name)
        manifest = book_fixtures.manifest()
        book_fixtures.write_docs(root / "docs")
        site = book_fixtures.write_site(root / "site")
        data = book_fixtures.write_data(root / "data")
        validate_manifest(manifest, docs_dir=root / "docs")
        cls.docs = root / "docs"
        cls.site = site
        cls.data = data
        cls.manifest = manifest
        cls.full = cls._build(root / "dist" / "full", None)
        cls.vol1 = cls._build(root / "dist" / "v1", 1)
        cls.vol2 = cls._build(root / "dist" / "v2", 2)

    @classmethod
    def _build(cls, out: Path, volume):
        path = assemble.build_html(
            out, cls.site, cls.data, cls.docs, cls.manifest,
            rebuild_site=False, final=False, volume=volume)
        model = json.loads((out / "book-model.json").read_text(encoding="utf-8"))
        return {"html": path.read_text(encoding="utf-8"), "model": model,
                "out": out, "path": path}

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def _ids(self, build):
        return [page["id"] for page in build["model"]["pages"]]

    def test_volumes_cover_every_body_page_exactly_once(self):
        full_ids = self._ids(self.full)
        front = full_ids[:full_ids.index("part-i")]
        body1 = self._ids(self.vol1)[len(front):]
        body2 = self._ids(self.vol2)[len(front):]
        shared = sorted(assemble.VOLUME_COMMON_BACK_IDS)
        # 参考文献与索引是两卷都要带的公共后页，正文页不得重复。
        self.assertEqual(shared, sorted(set(body1) & set(body2)))
        rebuilt = [pid for pid in body1 if pid not in assemble.VOLUME_COMMON_BACK_IDS] + body2
        self.assertEqual(full_ids[len(front):], rebuilt)

    def test_each_volume_keeps_front_matter_and_label(self):
        for volume, build in ((1, self.vol1), (2, self.vol2)):
            with self.subTest(volume=volume):
                ids = self._ids(build)
                self.assertEqual("half-title", ids[0])
                self.assertIn("book-toc", ids)
                self.assertIn("list-of-figures", ids)
                self.assertIn("list-of-tables", ids)
                self.assertEqual(volume, build["model"]["volume"])
                self.assertEqual(assemble.VOLUME_LABELS[volume],
                                 build["model"]["volume_label"])

    def test_volume_split_happens_at_the_part_boundary(self):
        ids1 = self._ids(self.vol1)
        ids2 = self._ids(self.vol2)
        body1 = [pid for pid in ids1
                 if pid not in assemble.VOLUME_COMMON_BACK_IDS]
        front_len = ids1.index("part-i")
        self.assertEqual(assemble.VOLUME1_LAST_ID, body1[-1])
        self.assertEqual(assemble.VOLUME2_FIRST_ID, ids2[front_len])
        self.assertNotIn("part-iii", ids1)
        self.assertNotIn(assemble.VOLUME1_LAST_ID, ids2)

    def test_page_numbers_are_renumbered_per_volume(self):
        for build in (self.vol1, self.vol2):
            with self.subTest(volume=build["model"]["volume"]):
                numbers = [page["index"] for page in build["model"]["pages"]]
                self.assertEqual(list(range(len(numbers))), numbers)
                self.assertEqual(len(numbers), build["model"]["expected_pages"])

    def test_cross_volume_links_are_degraded_not_dangling(self):
        # 分卷审计禁止悬空 href="#…"；跨卷目标必须降级为「见上/下卷」提示。
        all_pages = self.full["model"]["pages"]
        for volume, other_label in ((1, "下卷"), (2, "上卷")):
            with self.subTest(volume=volume):
                pages = assemble._select_volume_pages(all_pages, volume)
                kept = {page["id"] for page in pages}
                outside = next(page for page in all_pages
                               if page["id"] not in kept)
                probe = {"id": "probe", "stem": "probe", "group": "body",
                         "html": '<a href="#%s">见该页</a>'
                                 '<a href="#probe">见本页</a>' % outside["id"]}
                assemble._externalize_cross_volume_links(
                    [*pages, probe], all_pages, volume)
                self.assertIn('class="book-cross-volume"', probe["html"])
                self.assertIn("（见%s）" % other_label, probe["html"])
                self.assertIn('href="#probe"', probe["html"])
                self.assertNotIn('href="#%s"' % outside["id"], probe["html"])

    def test_volume_index_only_lists_anchors_present_in_that_volume(self):
        full_terms = self.full["model"]["stats"]["index_terms_total"]
        for build in (self.vol1, self.vol2):
            model = build["model"]
            with self.subTest(volume=model["volume"]):
                anchors = set()
                for page in model["pages"]:
                    anchors.add(page["id"])
                    anchors.update(m.group(2) for m in
                                   assemble.ID_ATTR_RE.finditer(page["html"]))
                self.assertLessEqual(model["stats"]["index_terms"], full_terms)
                index_page = next(page for page in model["pages"]
                                  if page["id"] == "book-index")
                targets = set(re.findall(r'href="#([^"]+)"',
                                         index_page["html"]))
                self.assertTrue(targets <= anchors,
                                "分卷索引出现本卷不存在的锚点: %s"
                                % sorted(targets - anchors)[:5])

    def test_audit_uses_the_volume_page_count(self):
        for build in (self.vol1, self.vol2):
            with self.subTest(volume=build["model"]["volume"]):
                report = assemble.audit_html(
                    build["html"], build["model"], final=False)
                self.assertEqual([], report["errors"])
                self.assertNotIn("逻辑页应为", " ".join(report["warnings"]),
                                 "分卷审计不应再按 77 页整卷基准报警")

    def test_unknown_volume_is_rejected(self):
        with self.assertRaises(BookError):
            assemble._select_volume_pages(self.full["model"]["pages"], 3)


if __name__ == "__main__":
    unittest.main()

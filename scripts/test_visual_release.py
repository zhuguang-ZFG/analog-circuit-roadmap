"""Regression coverage for release counts that could otherwise report false green."""
import copy
from pathlib import Path
import tempfile
import unittest

import check_visual_manifest as manifest
import check_visual_release as release
from review_visuals_agent import score_total


class VisualReleaseTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / 'review.md').write_text('Reviewed all frames and calculations.', encoding='utf-8')
        (self.root / 'motion.svg').write_text(
            '<svg xmlns="http://www.w3.org/2000/svg"><circle cx="0">'
            '<animate attributeName="cx" from="0" to="100" dur="2s"/>'
            '</circle></svg>', encoding='utf-8')
        self.asset = {'id': 'motion', 'kind': 'animation', 'output': 'motion.svg',
                      'status': 'accepted',
                      'review_scores': dict.fromkeys(manifest.SCORE_DIMS + manifest.ANIM_DIMS, 5),
                      'review_record': {'record': 'review.md',
                                        'asset_sha256': release.digest(self.root / 'motion.svg')}}

    def run_inventory(self, *assets):
        return release.inventory({'assets': list(assets)}, self.root)

    def test_bundle_and_duplicate_registration_do_not_multiply_count(self):
        self.asset.update(reduced_motion='static.svg', storyboard='storyboard.svg')
        duplicate = {**self.asset, 'id': 'duplicate'}
        accepted, errors = self.run_inventory(self.asset, duplicate)
        self.assertEqual({'motion.svg'}, accepted['animation'])
        self.assertTrue(any('duplicate main output' in e for e in errors))

    def test_copying_animation_under_another_filename_is_not_independent(self):
        (self.root / 'copy.svg').write_bytes((self.root / 'motion.svg').read_bytes())
        accepted, errors = self.run_inventory(self.asset, {**self.asset, 'id': 'copy', 'output': 'copy.svg'})
        self.assertEqual(1, len(accepted['animation']))
        self.assertTrue(any('duplicate animation bytes' in e for e in errors))

    def test_static_svg_cannot_masquerade_as_animation(self):
        (self.root / 'motion.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg"/>', encoding='utf-8')
        self.asset['review_record']['asset_sha256'] = release.digest(self.root / 'motion.svg')
        accepted, errors = self.run_inventory(self.asset)
        self.assertFalse(accepted['animation'])
        self.assertTrue(any('static output' in e for e in errors))

    def test_changing_accepted_bytes_requires_new_review(self):
        path = self.root / 'motion.svg'
        path.write_text(path.read_text().replace('100', '200'))
        accepted, errors = self.run_inventory(self.asset)
        self.assertFalse(accepted['animation'])
        self.assertTrue(any('reviewed bytes differ' in e for e in errors))

    def test_review_total_uses_all_seven_dimensions(self):
        scores = self.asset['review_scores']
        scores[manifest.ANIM_DIMS[-1]] = 4
        self.assertEqual(34, score_total('animation', scores))
        self.assertEqual(25, score_total('figure', scores))
        accepted, errors = self.run_inventory(self.asset)
        self.assertEqual({'motion.svg'}, accepted['animation'])
        self.assertEqual([], errors)

    def test_all_fours_fail_animation_total_even_when_each_dimension_passes(self):
        self.asset['review_scores'] = dict.fromkeys(self.asset['review_scores'], 4)
        accepted, errors = self.run_inventory(self.asset)
        self.assertFalse(accepted['animation'])
        self.assertTrue(any('below 30/35' in e for e in errors))

    def test_review_report_and_pending_status_are_not_optional(self):
        pending = {**self.asset, 'status': 'generated'}
        accepted, _ = self.run_inventory(pending)
        self.assertFalse(accepted['animation'])
        (self.root / 'review.md').unlink()
        accepted, errors = self.run_inventory(self.asset)
        self.assertFalse(accepted['animation'])
        self.assertTrue(any('missing review evidence' in e for e in errors))

    def test_legacy_inventory_uses_frozen_list_and_checks_replacement_acceptance(self):
        baseline = {'inventory': {'svg_animations': {'sha256': {'old.svg': 'original'}}}}
        old = {'id': 'old', 'output': 'assets/svg/old.svg',
               'legacy_disposition': {'action': 'rebuild', 'reason': 'Incorrect circuit',
                                      'record': 'review.md', 'replacement': 'motion.svg'}}
        data = {'assets': [old, self.asset]}
        self.assertEqual([], release.legacy_errors(data, baseline, self.root))
        data['assets'][1]['status'] = 'generated'
        self.assertTrue(any('replacement lacks acceptance' in e
                            for e in release.legacy_errors(data, baseline, self.root)))
        data['assets'] = [self.asset]
        self.assertTrue(any('missing individual' in e
                            for e in release.legacy_errors(data, baseline, self.root)))


if __name__ == '__main__':
    unittest.main()

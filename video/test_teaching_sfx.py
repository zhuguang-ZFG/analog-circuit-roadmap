import importlib.util
import unittest
from pathlib import Path

SPEC = importlib.util.spec_from_file_location("remix", Path(__file__).parent / "remotion" / "remix.py")
remix = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(remix)


class TeachingSfxTests(unittest.TestCase):
    def cues(self, shot):
        self.assertTrue(hasattr(remix, "teaching_cues"), "teaching cues must follow the actual scene timeline")
        return remix.teaching_cues(shot)

    def test_answer_cue_follows_spoken_answer_not_scene_tail(self):
        cues = self.cues({"view": "quiz", "seconds": 15, "revealAt": 8.2})
        self.assertEqual([name for name, _ in cues], ["riser", "ding"])
        self.assertAlmostEqual(cues[0][1], 7.45)
        self.assertAlmostEqual(cues[1][1], 8.2)

    def test_short_answer_lead_never_places_sound_before_shot(self):
        self.assertEqual(self.cues({"view": "quiz", "seconds": 3, "revealAt": 0.4}), [("riser", 0), ("ding", 0.4)])

    def test_rss_cues_stretch_with_the_teaching_animation(self):
        cues = self.cues({"view": "noise-rss", "seconds": 10})
        self.assertEqual([name for name, _ in cues], ["pop", "pop", "pop", "pop", "ding"])
        for (_, actual), wanted in zip(cues, [0.8, 2, 3.2, 4.4, 8.4]):
            self.assertAlmostEqual(actual, wanted)

    def test_existing_shots_do_not_gain_duplicate_cues(self):
        self.assertEqual(self.cues({"type": "card", "seconds": 5}), [])
        self.assertEqual(self.cues({"view": "quiz", "seconds": 9}), [])


if __name__ == "__main__":
    unittest.main()

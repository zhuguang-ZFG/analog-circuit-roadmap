"""Offline storyboard preflight contracts; never launch a browser or render media."""
from __future__ import annotations

import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True
VIDEO = Path(__file__).resolve().parent
ROOT = VIDEO.parent
SVG_DIR = ROOT / "assets" / "svg"
LINT = VIDEO / "storyboard_lint.py"
sys.path.insert(0, str(VIDEO))


def board_with(*shots, name="ep20-test"):
    return {"name": name, "shots": list(shots)}


def card(**overrides):
    return {"type": "card", "seconds": 2, "lines": ["Test"], **overrides}


def number(**overrides):
    return {"type": "num", "seconds": 2, "from": 0, "to": 4.1,
            "unit": "mV", **overrides}


class StoryboardTests(unittest.TestCase):
    def setUp(self):
        self.assertTrue(LINT.is_file(), "missing storyboard_lint.py preflight")
        import storyboard_lint
        self.lint = storyboard_lint

    def errors(self, board, **kwargs):
        result = self.lint.validate_storyboard(board, svg_dir=SVG_DIR, **kwargs)
        self.assertIsInstance(result, list)
        self.assertTrue(all(isinstance(error, str) for error in result))
        return result

    def assertInvalid(self, board, field, **kwargs):
        errors = self.errors(board, **kwargs)
        self.assertTrue(any(field in error for error in errors), errors)

    def test_all_twenty_source_and_registered_boards_are_valid(self):
        sources = sorted((VIDEO / "shots").glob("ep*.json"))
        registered = sorted(p for p in (VIDEO / "remotion/src/data").glob("ep*.json")
                            if not p.name.endswith("-subs.json"))
        self.assertEqual(len(sources), 20)
        self.assertEqual(len(registered), 20)
        for path in sources + registered:
            with self.subTest(path=path):
                board = json.loads(path.read_text(encoding="utf-8"))
                views = (self.lint.custom_views_for_name(board["name"])
                         if path in sources else self.lint.CUSTOM_VIEWS.get(path.stem, {}))
                self.assertEqual(self.errors(board, custom_views=views), [])

    def test_board_and_shots_shapes(self):
        for value in (None, [], "text", 1):
            with self.subTest(value=value):
                self.assertInvalid(value, "$")
        for value in (None, [], {}, "shots"):
            with self.subTest(shots=value):
                self.assertInvalid({"name": "ep20-test", "shots": value}, "shots")
        self.assertInvalid({"name": "ep20-test"}, "shots")
        self.assertInvalid(board_with(None), "shots[0]")

    def test_names_cannot_escape_paths_or_inject_typescript(self):
        for value in (None, "", " ", "../escape", "..\\escape", "/tmp/escape",
                      "D:escape", "ep20/escape", "ep20\\escape", "ep20\n",
                      'ep20\";throw Error(1);//', "ep20`", "ep20.svg", "CON", "nul"):
            with self.subTest(name=value):
                self.assertInvalid(board_with(card(), name=value), "name")
        self.assertEqual(self.errors(board_with(card(), name="ep20-noise_v2")), [])

    def test_seconds_must_be_finite_positive_numbers(self):
        for value in (-1, 0, float("nan"), float("inf"), -float("inf"),
                      True, "2", None, 1e308, 10 ** 400):
            with self.subTest(seconds=str(value)):
                self.assertInvalid(board_with(card(seconds=value)), "shots[0].seconds")
        shot = card()
        del shot["seconds"]
        self.assertInvalid(board_with(shot), "shots[0].seconds")

    def test_frame_rounding_matches_javascript_and_cumulative_bounds(self):
        self.assertInvalid(board_with(number(seconds=0.01)), "shots[0].seconds")
        # JS Math.round(0.5) = 1, unlike Python round(0.5).
        self.assertEqual(self.errors(board_with(number(seconds=1 / 60))), [])
        # Each rounds to one frame separately, but the second cumulative delta is zero.
        self.assertInvalid(board_with(number(seconds=0.02), number(seconds=0.02),
                                      number()), "shots[1].seconds")

    def test_transition_only_needs_nine_frames_on_last_of_multiple_shots(self):
        self.assertEqual(self.errors(board_with(number(seconds=1 / 30))), [])
        self.assertEqual(self.errors(board_with(number(seconds=1 / 30),
                                               number(seconds=9 / 30))), [])
        self.assertInvalid(board_with(number(), number(seconds=8 / 30)),
                           "shots[1].seconds")
        # Fractional cumulative boundary, not independent rounding of the last shot.
        self.assertEqual(self.errors(board_with(number(seconds=1.01),
                                               number(seconds=8.4 / 30))), [])

    def test_actual_card_and_svg_interpolation_boundaries(self):
        self.assertInvalid(board_with(card(seconds=18 / 30)), "shots[0].seconds")
        self.assertEqual(self.errors(board_with(card(seconds=19 / 30))), [])
        svg = {"type": "svg", "seconds": 27 / 30, "file": "noise-budget"}
        self.assertInvalid(board_with(svg), "shots[0].seconds")
        svg["seconds"] = 28 / 30
        self.assertEqual(self.errors(board_with(svg)), [])
        # Built-in/custom views bypass CardShot's interpolation entirely.
        self.assertEqual(self.errors(board_with(card(view="quiz", q="?", seconds=1 / 30))), [])
        self.assertEqual(self.errors(board_with(card(view="noise-rss", seconds=1 / 30))), [])

    def test_types_and_views_do_not_silently_fall_back(self):
        for value in (None, "", "typo", [], {}):
            with self.subTest(type=value):
                self.assertInvalid(board_with(card(type=value)), "shots[0].type")
            with self.subTest(view=value):
                self.assertInvalid(board_with(card(view=value)), "shots[0].view")
        for view in ("quiz", "noise-rss"):
            self.assertInvalid(board_with(number(view=view, q="?")), "shots[0].type")

    def test_custom_views_are_scoped_to_real_episode_registration(self):
        board = board_with(card(view="demo"), name="ep04-divider")
        self.assertInvalid(board, "shots[0].view")
        allowed = self.lint.custom_views_for_name(board["name"])
        self.assertEqual(self.errors(board, custom_views=allowed), [])
        for name in ("ep20-noise", "ep040-divider", "not-ep04", None, []):
            with self.subTest(name=name):
                self.assertEqual(dict(self.lint.custom_views_for_name(name)), {})
        self.assertInvalid(board_with(card(view="demo")), "shots[0].view",
                           custom_views=self.lint.custom_views_for_name("ep20-noise"))

    def test_numeric_fields_and_decimal_precision_match_renderers(self):
        for field in ("from", "to"):
            for value in (None, "4", True, float("nan"), float("inf"), 10 ** 400):
                with self.subTest(field=field, value=str(value)):
                    self.assertInvalid(board_with(number(**{field: value})), "shots[0]." + field)
            shot = number()
            del shot[field]
            self.assertInvalid(board_with(shot), "shots[0]." + field)
        for value in (None, "", "  ", 1):
            self.assertInvalid(board_with(number(unit=value)), "shots[0].unit")
        for value in (-1, 101, 1.5, "1", True, None):
            self.assertInvalid(board_with(number(dec=value)), "shots[0].dec")
        for dec in (0, 1, 100):
            self.assertEqual(self.errors(board_with(number(dec=dec))), [])
        for bar in ([], [1], [1, 2, 3], "1,2", [1, "2"], [1, float("nan")]):
            self.assertInvalid(board_with(number(bar=bar)), "shots[0].bar")
        self.assertEqual(self.errors(board_with(number(bar=[0, 0]))), [])

    def test_svg_and_background_assets_are_safe_existing_stems(self):
        for field, shot in (("file", {"type": "svg", "seconds": 2}), ("bgSvg", card())):
            for value in (None, "", "../noise-budget", "..\\noise-budget", "/noise-budget",
                          "noise-budget.svg", "not-an-existing-asset", 'noise\"budget'):
                with self.subTest(field=field, value=value):
                    self.assertInvalid(board_with({**shot, field: value}), "shots[0]." + field)
            self.assertEqual(self.errors(board_with({**shot, field: "noise-budget"})), [])
        self.assertInvalid(board_with({"type": "svg", "seconds": 2}), "shots[0].file")

    def test_card_lines_and_intro_title_and_optional_text_types(self):
        for value in (None, "one line", [1], ["ok", {}]):
            self.assertInvalid(board_with(card(lines=value)), "shots[0].lines")
        self.assertInvalid(board_with({"type": "card", "seconds": 2}), "shots[0].lines")
        self.assertEqual(self.errors(board_with(card(lines=[]))), [])
        for value in (None, "", " ", 7):
            self.assertInvalid(board_with({"type": "intro", "seconds": 2, "title": value}),
                               "shots[0].title")
        self.assertEqual(self.errors(board_with({"type": "intro", "seconds": 2, "title": "Title"})), [])
        for field in ("eyebrow", "sub", "chip", "bubble", "cta", "mascot",
                      "series", "ep", "progress", "caption"):
            with self.subTest(field=field):
                self.assertInvalid(board_with(card(**{field: {}})), "shots[0]." + field)

    def test_quiz_thinking_mode_and_noise_view_need_no_extra_fields(self):
        for extra in ({}, {"options": []}):
            self.assertEqual(self.errors(board_with({"type": "card", "view": "quiz",
                             "seconds": 2, "q": "Think", **extra})), [])
        self.assertEqual(self.errors(board_with({"type": "card", "view": "noise-rss", "seconds": 2})), [])
        self.assertEqual(self.errors(board_with(card(view="quiz", q="?",
                                                   options=["A", "B", "C"], answer=2))), [])

    def test_quiz_question_options_and_zero_based_answer(self):
        self.assertInvalid(board_with(card(view="quiz")), "shots[0].q")
        self.assertInvalid(board_with(card(view="quiz", q={})), "shots[0].q")
        for options in (None, "ABC", [1], ["A", "B", "C", "D"]):
            self.assertInvalid(board_with(card(view="quiz", q="?", options=options)), "shots[0].options")
        self.assertInvalid(board_with(card(view="quiz", q="?", options=["A"])), "shots[0].answer")
        for answer in (-1, 2, 0.5, "0", True, None):
            self.assertInvalid(board_with(card(view="quiz", q="?", options=["A", "B"], answer=answer)),
                               "shots[0].answer")
        self.assertInvalid(board_with(card(view="quiz", q="?", explain={})), "shots[0].explain")

    def test_quiz_reveal_accepts_absence_zero_subframe_and_last_scene_frame(self):
        for extra in ({}, {"revealAt": 0}, {"revealAt": 0.001},
                      {"revealAt": 1 / 60}, {"revealAt": 59 / 30}):
            with self.subTest(extra=extra):
                self.assertEqual(self.errors(board_with(card(view="quiz", q="?",
                                 options=["A", "B"], answer=1, **extra))), [])

    def test_quiz_reveal_must_be_finite_nonboolean_and_inside_scene(self):
        for value in (None, "0", "0.001", True, False, [], {}, float("nan"),
                      float("inf"), -float("inf"), -0.001, 2, 2.1, 1e308, 10 ** 400):
            with self.subTest(revealAt=str(value)):
                self.assertInvalid(board_with(card(view="quiz", q="?", revealAt=value)),
                                   "shots[0].revealAt")

    def test_quiz_reveal_must_leave_an_actual_frame_after_rounding(self):
        # Both times precede seconds=2 but round to frame 60, outside [0, 59].
        for value in (59.5 / 30, 1.999):
            with self.subTest(revealAt=value):
                self.assertInvalid(board_with(card(view="quiz", q="?", revealAt=value)),
                                   "shots[0].revealAt")

    def test_quiz_reveal_uses_cumulative_scene_frames_not_transition_padding(self):
        # Independent rounding gives 31 frames, but cumulative bounds are [1, 31].
        quiz = card(view="quiz", q="?", seconds=1.02, revealAt=1)
        for tail in ((), (number(),)):
            with self.subTest(nonfinal=bool(tail)):
                self.assertInvalid(board_with(number(seconds=0.02), quiz, *tail),
                                   "shots[1].revealAt")
        # Conversely this scene has 31 actual frames, not its independent 30.
        self.assertEqual(self.errors(board_with(number(seconds=1.01),
                         card(view="quiz", q="?", seconds=1.01, revealAt=1))), [])
        self.assertEqual(self.errors(board_with(number(seconds=0.02),
                         {**quiz, "revealAt": 29 / 30})), [])

    def test_validation_does_not_mutate_or_enforce_content_style(self):
        board = board_with(card(lines=["long " * 1000] * 10, seconds=600, extra={"editor": "notes"}),
                           number(seconds=900))
        original = copy.deepcopy(board)
        self.assertEqual(self.errors(board), [])
        self.assertEqual(board, original)

    def test_accumulates_actionable_shot_and_field_diagnostics(self):
        errors = self.errors(board_with(card(view="typo", seconds=-1), number(to="bad")))
        for field in ("shots[0].view", "shots[0].seconds", "shots[1].to"):
            self.assertTrue(any(field in error for error in errors), errors)


class EntryPointTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="storyboard-test-", dir=VIDEO / ".tmp")
        self.addCleanup(self.tmp.cleanup)
        self.work = Path(self.tmp.name)

    def write_board(self, name, board):
        path = self.work / name
        path.write_text(json.dumps(board), encoding="utf-8")
        return path

    def run_python(self, *args):
        return subprocess.run([sys.executable, "-B", *map(str, args)], cwd=self.work,
                              env={**os.environ, "PYTHONIOENCODING": "utf-8"},
                              capture_output=True, text=True, encoding="utf-8", timeout=20)

    def test_cli_defaults_find_twenty_boards_independent_of_cwd(self):
        self.assertTrue(LINT.is_file(), "missing storyboard_lint.py CLI")
        result = self.run_python(LINT)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("20", result.stdout)
        self.assertIn("ep20-noise.json", result.stdout)

    def test_cli_checks_multiple_files_and_reports_json_io_and_schema_errors(self):
        self.assertTrue(LINT.is_file(), "missing storyboard_lint.py CLI")
        good = self.write_board("good.json", board_with(card()))
        bad = self.write_board("bad.json", board_with(card(view="unknown")))
        broken = self.work / "broken.json"
        broken.write_text("{not json", encoding="utf-8")
        missing = self.work / "missing.json"
        result = self.run_python(LINT, good, bad, broken, missing)
        output = result.stdout + result.stderr
        self.assertNotEqual(result.returncode, 0, output)
        for path in (good, bad, broken, missing):
            self.assertIn(str(path), output)
        self.assertIn("shots[0].view", output)
        self.assertIn("JSON", output)
        self.assertNotIn("Traceback", output)

    def test_director_rejects_before_build_html_even_for_cover(self):
        # Replacing the expensive boundary makes this test safe even on the old code.
        # If validation is missing, the explicit sentinel fails the assertion.
        runner = (f"import sys; sys.path.insert(0, {str(VIDEO)!r}); import director; "
                  "director.build_html=lambda *a,**k: sys.exit('BUILD_REACHED'); "
                  "sys.argv=['director', *sys.argv[1:]]; sys.exit(director.main())")
        for cover in (False, True):
            path = self.write_board("bad-director.json", board_with(card(), card(view="typo")))
            result = self.run_python("-c", runner, "--shots", path, *(["--cover"] if cover else []))
            output = result.stdout + result.stderr
            self.assertNotEqual(result.returncode, 0, output)
            self.assertIn(str(path), output)
            self.assertIn("shots[1].view", output)
            self.assertNotIn("BUILD_REACHED", output)
            self.assertNotIn("Traceback", output)

    def test_director_reports_invalid_json_without_traceback(self):
        path = self.work / "broken.json"
        path.write_text("[", encoding="utf-8")
        result = self.run_python(VIDEO / "director.py", "--shots", path)
        output = result.stdout + result.stderr
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(str(path), output)
        self.assertIn("JSON", output)
        self.assertNotIn("Traceback", output)

    def registry_run(self, boards):
        data = self.work / "data"
        data.mkdir(exist_ok=True)
        for key, board in boards.items():
            (data / f"{key}.json").write_text(json.dumps(board), encoding="utf-8")
        output = self.work / "episodes.ts"
        if not output.exists():
            output.write_text("KEEP EXISTING REGISTRY", encoding="utf-8")
        runner = (f"import sys; sys.path.insert(0, {str(VIDEO / 'remotion')!r}); "
                  f"import gen_registry; from pathlib import Path; gen_registry.SRC=Path({str(self.work)!r}); "
                  "sys.exit(gen_registry.main())")
        return self.run_python("-c", runner), output

    def test_registry_rejects_unknown_views_without_overwriting_output(self):
        result, output = self.registry_run({"ep20": board_with(card(view="typo"))})
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn(str(self.work / "data/ep20.json"), result.stderr)
        self.assertIn("shots[0].view", result.stderr)
        self.assertEqual(output.read_text(encoding="utf-8"), "KEEP EXISTING REGISTRY")

    def test_registry_uses_registration_key_not_spoofed_board_name_for_custom_views(self):
        result, output = self.registry_run({"ep20": board_with(card(view="demo"), name="ep04-divider")})
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("shots[0].view", result.stderr)
        self.assertEqual(output.read_text(encoding="utf-8"), "KEEP EXISTING REGISTRY")

    def test_registry_rejects_injected_name_without_overwriting_output(self):
        result, output = self.registry_run({"ep20": board_with(card(), name='ep20\";alert(1);//')})
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("name", result.stderr)
        self.assertEqual(output.read_text(encoding="utf-8"), "KEEP EXISTING REGISTRY")

    def test_registry_rejects_unsafe_registration_filename(self):
        result, output = self.registry_run({"ep20-invalid-key": board_with(card())})
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("ep20-invalid-key.json", result.stderr)
        self.assertIn("registration", result.stderr)
        self.assertEqual(output.read_text(encoding="utf-8"), "KEEP EXISTING REGISTRY")

    def test_registry_empty_scan_does_not_erase_existing_registry(self):
        result, output = self.registry_run({})
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(output.read_text(encoding="utf-8"), "KEEP EXISTING REGISTRY")

    def test_registry_reports_malformed_json_and_later_bad_board(self):
        data = self.work / "data"
        data.mkdir()
        broken = data / "ep01.json"
        broken.write_text("{", encoding="utf-8")
        result, output = self.registry_run({"ep20": board_with(card(view="typo"))})
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(str(broken), result.stderr)
        self.assertIn("JSON", result.stderr)
        self.assertIn("shots[0].view", result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        self.assertEqual(output.read_text(encoding="utf-8"), "KEEP EXISTING REGISTRY")

    def test_one_mapping_drives_validation_and_component_imports(self):
        self.assertTrue(LINT.is_file(), "missing structured custom view registry")
        import storyboard_lint
        sys.path.insert(0, str(VIDEO / "remotion"))
        import gen_registry
        data = self.work / "data"
        data.mkdir()
        (data / "ep19.json").write_text(json.dumps(board_with(card(view="meter"))), encoding="utf-8")
        with patch.dict(storyboard_lint.CUSTOM_VIEWS, {"ep19": {"meter": "MeterShot"}}), \
                patch.object(gen_registry, "SRC", self.work):
            self.assertEqual(gen_registry.main(), 0)
        text = (self.work / "episodes.ts").read_text(encoding="utf-8")
        self.assertIn("meter: MeterShot", text)
        self.assertIn('import {MeterShot} from "./components/MeterShot";', text)

    def test_registry_serializes_structured_custom_views_and_builtin_views(self):
        result, output = self.registry_run({
            "ep04": board_with(card(view="demo"), card(view="collapse"), name="ep04-divider"),
            "ep20": board_with(card(view="quiz", q="?"), card(view="noise-rss")),
        })
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        text = output.read_text(encoding="utf-8")
        self.assertIn("demo: DividerDemo", text)
        self.assertIn("collapse: DividerCollapse", text)
        self.assertIn('import {DividerDemo} from "./components/DividerDemo";', text)
        self.assertIn('audio: "audio/ep04-divider-remix.wav"', text)
        self.assertIn("customShots: {}", text)

    def test_director_builds_legal_custom_and_builtin_drafts_without_rendering(self):
        self.assertTrue(LINT.is_file(), "missing shared view validation")
        import director
        boards = [board_with(card(view="demo"), card(view="collapse"), name="ep04-divider"),
                  board_with({"type": "card", "seconds": 2, "view": "noise-rss"},
                             {"type": "card", "seconds": 2, "view": "quiz", "q": "?"})]
        # Only font embedding is replaced; real HTML construction stays under test.
        with patch.object(director, "kuaile_face", return_value=""):
            for board in boards:
                self.assertIn("<html", director.build_html(board))


if __name__ == "__main__":
    unittest.main()

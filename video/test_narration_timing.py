# -*- coding: utf-8 -*-
"""离线时序回归：只替换 TTS 网络边界，JSON/NDJSON/PCM/ffmpeg 均真实运行。"""
import array
import contextlib
import hashlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import wave

VIDEO = Path(__file__).resolve().parent
sys.path.insert(0, str(VIDEO))
sys.path.insert(0, str(VIDEO / "remotion"))
import narrate
import make_subs
from storyboard_lint import ValidationError


def write_pcm(path, samples, sr=24000):
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sr)
        wav.writeframes(array.array("h", samples).tobytes())


def read_pcm(path):
    with wave.open(str(path), "rb") as wav:
        return wav.getframerate(), array.array("h", wav.readframes(wav.getnframes()))


class DownloadFixture:
    """save 的离线替身：实际写音频与 NDJSON，默认模拟旧 API 的句边界。"""
    def __init__(self, text, voice, *, rate, boundary="SentenceBoundary"):
        self.text, self.voice, self.rate, self.boundary = text, voice, rate, boundary

    async def save(self, audio_fname, metadata_fname=None):
        # WAV 容器故意命名 .mp3：ffmpeg 按真实容器探测，保留精确 PCM 断言。
        is_answer = self.text == "答案。"
        value = -2300 if is_answer else 1200
        count = 12000 if is_answer else 24000
        write_pcm(Path(audio_fname), [value] * count)
        if metadata_fname is not None:
            event = {"type": self.boundary, "offset": 1_000_000,
                     "duration": 3_000_000 if is_answer else 8_000_000,
                     "text": self.text.rstrip("。？")}
            Path(metadata_fname).write_text(json.dumps(event, ensure_ascii=False) + "\n",
                                            encoding="utf-8")


class TimingFiles(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="narration-test-", dir=VIDEO / ".tmp")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.samples = self.root / "samples"
        self.cache = self.root / "cache"
        self.data = self.root / "remotion" / "public" / "data"
        self.src_data = self.root / "remotion" / "src" / "data"
        for directory in (self.samples, self.cache, self.data, self.src_data):
            directory.mkdir(parents=True)
        self.name = "ep99-timing"
        self.board_path = self.root / "board.json"

    def run_narrate(self, shots, *args, downloader=DownloadFixture):
        # Timing fixtures still obey the shared rendering contract; explicit fields win.
        shots = [{"type": "card", "lines": [], **shot} for shot in shots]
        for shot in shots:
            if shot.get("view") == "quiz":
                shot.setdefault("q", "问题？")
                if shot.get("options"):
                    shot.setdefault("answer", 0)
        self.board_path.write_text(json.dumps({"name": self.name, "custom": {"keep": True},
                                               "shots": shots}, ensure_ascii=False), encoding="utf-8")
        with patch.object(narrate, "SAMPLES", self.samples), patch.object(narrate, "TMP", self.cache), \
                patch("edge_tts.Communicate", downloader), \
                patch.object(sys, "argv", ["narrate.py", "--shots", str(self.board_path), *args]), \
                contextlib.redirect_stdout(io.StringIO()):
            result = narrate.main()
        self.assertEqual(result, 0)
        return json.loads((self.samples / f"{self.name}-timeline.json").read_text(encoding="utf-8"))

    def write_timeline(self, shots):
        (self.samples / f"{self.name}-timeline.json").write_text(
            json.dumps({"name": self.name, "shots": shots}, ensure_ascii=False), encoding="utf-8")

    def windows(self, shots):
        self.write_timeline(shots)
        with patch.object(make_subs, "SAMPLES", self.samples):
            return make_subs.build_windows(self.name)

    def run_subs(self):
        with patch.object(make_subs, "SAMPLES", self.samples), \
                patch.object(make_subs, "DATA", self.data), \
                patch.object(make_subs, "__file__", str(self.root / "remotion" / "make_subs.py")), \
                patch.object(sys, "argv", ["make_subs.py", self.name]), \
                contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(make_subs.main(), 0)
        return json.loads((self.data / "ep99-subs.json").read_text(encoding="utf-8"))

    def seed_old_videos(self):
        videos = {self.samples / f"{self.name}-{kind}{suffix}.mp4":
                  f"old {kind}{suffix}".encode()
                  for kind in ("draft", "vo") for suffix in ("", "-h")}
        for path, content in videos.items():
            path.write_bytes(content)
        return videos

    def assert_preflight_rejected(self, shots, message, *args):
        # A missing cache catches mkdir-before-validation; snapshots catch deletes/writes.
        self.cache = self.root / "uncreated-cache"
        self.seed_old_videos()
        def snapshot():
            return {path.relative_to(self.root): path.read_bytes() if path.is_file() else None
                    for path in self.root.rglob("*") if path != self.board_path}
        def forbidden_download(*args, **kwargs):
            raise AssertionError("invalid storyboard reached TTS")
        before = snapshot()
        with patch.object(narrate, "synth", wraps=narrate.synth) as tts, \
                patch.object(narrate, "ffmpeg_exe", wraps=narrate.ffmpeg_exe) as ff:
            with self.assertRaisesRegex(ValidationError, message):
                self.run_narrate(shots, *args, downloader=forbidden_download)
            tts.assert_not_called()
            ff.assert_not_called()
        self.assertFalse(self.cache.exists())
        self.assertEqual(snapshot(), before)

    def test_invalid_name_preflight_has_no_tts_or_output_side_effects(self):
        self.name = "../escape"
        for args in ((), ("--no-render",), ("--audio-only",)):
            with self.subTest(args=args):
                self.assert_preflight_rejected([{"seconds": 2, "voice": "问题？"}],
                                               "name: expected a safe filename stem", *args)

    def test_invalid_later_view_preflight_has_no_tts_or_output_side_effects(self):
        for args in ((), ("--no-render",), ("--audio-only",)):
            with self.subTest(args=args):
                self.assert_preflight_rejected(
                    [{"seconds": 2, "voice": "问题？"},
                     {"seconds": 2, "view": "unknown-view", "voice": "后文。"}],
                    r"shots\[1\]\.view: unknown view", *args)

    def test_non_rendering_modes_preserve_old_video_artifacts(self):
        for args in (("--audio-only",), ("--no-render",), ("--audio-only", "--no-render")):
            for size in ("vertical", "horizontal"):
                with self.subTest(args=args, size=size):
                    videos = self.seed_old_videos()
                    self.run_narrate([{"seconds": 2, "voice": "问题？"}], *args, "--size", size)
                    for path, content in videos.items():
                        self.assertTrue(path.is_file(), path.name)
                        self.assertEqual(path.read_bytes(), content)

    def test_normal_rendering_still_cleans_only_selected_size_before_tts(self):
        def stopped_download(*args, **kwargs):
            raise RuntimeError("stop before TTS")
        for size, removed in (("vertical", ""), ("horizontal", "-h")):
            with self.subTest(size=size):
                videos = self.seed_old_videos()
                with self.assertRaisesRegex(RuntimeError, "stop before TTS"):
                    self.run_narrate([{"seconds": 2, "voice": "问题？"}], "--size", size,
                                     downloader=stopped_download)
                for path, content in videos.items():
                    if path.name in (f"{self.name}-draft{removed}.mp4", f"{self.name}-vo{removed}.mp4"):
                        self.assertFalse(path.exists(), path.name)
                    else:
                        self.assertEqual(path.read_bytes(), content)
                self.assertFalse((self.samples / f"{self.name}-timeline.json").exists())

    def test_existing_subtitles_are_rebuilt_from_current_voice(self):
        self.write_timeline([{"seconds": 3, "voice": "新文稿。"}])
        (self.data / "ep99-subs.json").write_text(
            json.dumps([{"from": 0, "to": 90, "text": "旧文稿。"}]), encoding="utf-8")
        write_pcm(self.samples / f"{self.name}-vo-narr.wav", [0] * 72000)
        subs = self.run_subs()
        self.assertEqual([s["text"] for s in subs], ["新文稿。"])
        self.assertEqual(subs, json.loads((self.src_data / "ep99-subs.json").read_text(encoding="utf-8")))
        self.assertEqual(len(subs[0]["env"]), 21)
        self.assertNotIn("charFrames", subs[0])

    def test_real_pcm_has_lead_both_segments_pause_and_tail(self):
        original = {"seconds": 1, "voice": "问题？", "view": "quiz", "answerVoice": "答案。",
                    "options": ["甲", "乙"], "custom": {"nested": [1, 2]}}
        board = self.run_narrate([original, {"seconds": 2, "voice": "后文。"},
                                  {"seconds": 1, "custom": "silent"}], "--audio-only")
        shot = board["shots"][0]
        self.assertAlmostEqual(shot["seconds"], 4.2)
        self.assertAlmostEqual(shot.get("revealAt", -1), 3.35)
        for key in ("voice", "answerVoice", "view", "options", "custom"):
            self.assertEqual(shot[key], original[key])
        self.assertEqual(board["custom"], {"keep": True})
        self.assertEqual(board["shots"][2].get("speech"), [])
        sr, pcm = read_pcm(self.cache / f"{self.name}-narration.wav")
        self.assertEqual(sr, 24000)
        self.assertEqual(len(pcm), 172800)  # 4.2 + 2 + 1 秒
        for a, b, value in ((0, 8400, 0), (8400, 32400, 1200), (32400, 80400, 0),
                            (80400, 92400, -2300), (92400, 109200, 0),
                            (109200, 133200, 1200), (133200, 172800, 0)):
            self.assertTrue(all(x == value for x in pcm[a:b]), (a, b, value))
        self.assertTrue((self.samples / f"{self.name}-vo-narr.wav").is_file())

    def test_word_boundary_ticks_are_seconds_relative_to_shot_including_lead(self):
        shot = self.run_narrate([{"seconds": 1, "view": "quiz", "voice": "问题？",
                                 "answerVoice": "答案。"}], "--no-render")["shots"][0]
        self.assertEqual(shot.get("speech"), [
            {"text": "问题", "start": 0.45, "end": 1.25},
            {"text": "答案", "start": 3.45, "end": 3.75}])
        self.assertFalse((self.cache / f"{self.name}-narration.wav").exists())

    def test_custom_pause_and_original_minimum_duration(self):
        shot = self.run_narrate([{"seconds": 9, "view": "quiz", "voice": "问题？",
                                 "answerVoice": "答案。", "thinkSeconds": 0.75}],
                               "--no-render")["shots"][0]
        self.assertEqual(shot.get("revealAt"), 2.1)
        self.assertEqual(shot["seconds"], 9)
        self.assertEqual(shot["thinkSeconds"], 0.75)

    def test_answer_voice_rejected_outside_quiz_and_invalid_pause(self):
        for extra in ({}, {"view": "quiz", "thinkSeconds": -1},
                      {"view": "quiz", "thinkSeconds": float("nan")}):
            with self.subTest(extra=extra), self.assertRaisesRegex(ValueError, "quiz|thinkSeconds"):
                self.run_narrate([{"seconds": 2, "voice": "问题？", "answerVoice": "答案。", **extra}],
                                 "--no-render")

    def test_cache_changes_for_voice_rate_and_text_and_reuses_complete_cache(self):
        variants = [("甲。", "zh-CN-YunxiNeural", "+12%"),
                    ("甲。", "zh-CN-XiaoxiaoNeural", "+12%"),
                    ("甲。", "zh-CN-XiaoxiaoNeural", "+8%"),
                    ("乙。", "zh-CN-XiaoxiaoNeural", "+8%")]
        for text, voice, rate in variants:
            self.run_narrate([{"seconds": 2, "voice": text}], "--no-render", "--voice", voice, "--rate", rate)
        self.assertEqual(len(list(self.cache.glob("*.mp3"))), 4)
        def offline(*args, **kwargs):
            raise AssertionError("完整缓存不应联网")
        self.run_narrate([{"seconds": 2, "voice": "乙。"}], "--no-render", "--voice",
                         "zh-CN-XiaoxiaoNeural", "--rate", "+8%", downloader=offline)

    def test_missing_boundary_regenerates_new_key_without_deleting_old_audio(self):
        shots = [{"seconds": 2, "voice": "问题？"}]
        self.run_narrate(shots, "--no-render")
        audio = next(self.cache.glob("*.mp3"))
        before = audio.read_bytes()
        # 模拟旧缓存/缺元数据，只移除本测试创建的 NDJSON，不触碰任何用户文件。
        for metadata in self.cache.iterdir():
            if metadata.suffix not in (".mp3", ".wav"):
                metadata.unlink()
        board = self.run_narrate(shots, "--no-render")
        self.assertEqual(len(list(self.cache.glob("*.mp3"))), 2)
        self.assertEqual(audio.read_bytes(), before)
        self.assertTrue(board["shots"][0].get("speech"))

    def test_legacy_text_hash_audio_is_preserved(self):
        key = hashlib.sha1("问题？".encode("utf-8")).hexdigest()[:10]
        old = self.cache / f"{self.name}-1-{key}.mp3"
        old.write_bytes(b"old user audio")
        write_pcm(old.with_suffix(".wav"), [700] * 24000)
        self.run_narrate([{"seconds": 2, "voice": "问题？"}], "--no-render")
        self.assertEqual(old.read_bytes(), b"old user audio")
        self.assertEqual(len(list(self.cache.glob("*.mp3"))), 2)

    def test_missing_download_metadata_is_not_claimed_as_exact(self):
        class NoMetadata(DownloadFixture):
            async def save(self, audio_fname, metadata_fname=None):
                await super().save(audio_fname, None)
        with self.assertRaisesRegex(ValueError, "WordBoundary|元数据"):
            self.run_narrate([{"seconds": 2, "voice": "问题？"}], "--no-render", downloader=NoMetadata)

    def test_char_frames_follow_word_starts_with_punctuation_digits_and_unicode(self):
        subs = self.windows([{"seconds": 5, "voice": "“电压12伏，𠮷好！”", "speech": [
            {"text": "电压", "start": 0.4, "end": 0.8},
            {"text": "12", "start": 0.9, "end": 1.1},
            {"text": "伏", "start": 1.2, "end": 1.5},
            {"text": "𠮷好", "start": 1.8, "end": 2.0}]}])
        self.assertEqual(len(subs), 1)
        self.assertEqual(subs[0]["text"], "“电压12伏，𠮷好！”")
        self.assertEqual((subs[0]["from"], subs[0]["to"]), (12, 60))
        # 同一词内不伪造字符时间：电/压、1/2、𠮷/好同时点亮，标点继承邻字。
        self.assertEqual(subs[0].get("charFrames"), [0, 0, 0, 15, 15, 24, 24, 42, 42, 42, 42])

    def test_sentence_prefixes_use_current_window_word_times(self):
        cases = [(" 下一段。", [0, 0, 0, 18, 18]),
                 ("“下一段。”", [0, 0, 0, 18, 18, 18]),
                 (" “下一段。”", [0, 0, 0, 0, 18, 18, 18]),
                 ("\t\u3000「下一段。」  ", [0, 0, 0, 0, 0, 18, 18, 18, 18, 18])]
        for following, frames in cases:
            with self.subTest(following=following):
                text = "第一段。" + following
                subs = self.windows([{"seconds": 2, "voice": ""},
                                     {"seconds": 4, "voice": text, "speech": [
                                         {"text": "第一", "start": 0.4, "end": 0.8},
                                         {"text": "段", "start": 0.9, "end": 1.2},
                                         {"text": "下一", "start": 2.4, "end": 2.8},
                                         {"text": "段", "start": 3.0, "end": 3.2}]}])
                self.assertEqual(subs, [
                    {"from": 72, "to": 96, "text": "第一段。", "charFrames": [0, 0, 15, 15]},
                    {"from": 132, "to": 156, "text": following, "charFrames": frames}])
                self.assertEqual("".join(s["text"].replace("\n", "") for s in subs), text)
                # The entire gap between the two real speech segments has no subtitle.
                self.assertTrue(all(not any(s["from"] <= f < s["to"] for s in subs)
                                    for f in range(96, 132)))
                for sub in subs:
                    self.assertEqual(len(sub["charFrames"]), len(sub["text"].replace("\n", "")))

    def test_prefixed_unicode_window_keeps_exact_codepoint_word_frames(self):
        subs = self.windows([{"seconds": 3, "voice": "第一段。 “𠮷12伏。” ", "speech": [
            {"text": "第一段", "start": 0.4, "end": 1.2},
            {"text": "𠮷", "start": 1.8, "end": 2.0},
            {"text": "12", "start": 2.1, "end": 2.3},
            {"text": "伏", "start": 2.4, "end": 2.6}]}])
        self.assertEqual(subs, [
            {"from": 12, "to": 36, "text": "第一段。", "charFrames": [0, 0, 0, 0]},
            {"from": 54, "to": 78, "text": " “𠮷12伏。” ",
             "charFrames": [0, 0, 0, 9, 9, 18, 18, 18, 18]}])
        self.assertEqual(len(subs[1]["charFrames"]), len(subs[1]["text"]))

    def test_sentence_prefix_does_not_allow_a_word_to_cross_windows(self):
        with self.assertRaisesRegex(ValueError, "词边界跨越切句"):
            self.windows([{"seconds": 3, "voice": "第一段。 “下一段。”", "speech": [
                {"text": "第一段下一段", "start": 0.4, "end": 1.2}]}])

    def test_wrap_newlines_not_counted_and_no_more_than_two_lines(self):
        text = "电路输入输出检查需要注意每一个节点电压。下一句。"
        spoken = [c for c in text if c not in "。"]
        events = [{"text": c, "start": 0.4 + i * 0.1, "end": 0.5 + i * 0.1}
                  for i, c in enumerate(spoken)]
        subs = self.windows([{"seconds": 6, "voice": text, "speech": events}])
        self.assertTrue(any("\n" in s["text"] for s in subs))
        self.assertEqual("".join(s["text"].replace("\n", "") for s in subs), text)
        for sub in subs:
            self.assertLessEqual(len(sub["text"].splitlines()), 2)
            frames = sub.get("charFrames", [])
            self.assertEqual(len(frames), len(sub["text"].replace("\n", "")))
            self.assertEqual(frames, sorted(frames))
            self.assertTrue(all(isinstance(f, int) and 0 <= f < sub["to"] - sub["from"] for f in frames))

    def test_question_and_answer_windows_never_swallow_quiz_pause(self):
        subs = self.windows([{"seconds": 2, "voice": ""},
                             {"seconds": 5, "view": "quiz", "voice": "问题？",
                              "answerVoice": "答案。", "revealAt": 3.35, "speech": [
                                  {"text": "问题", "start": 0.45, "end": 1.25},
                                  {"text": "答案", "start": 3.45, "end": 3.75}]}])
        self.assertEqual([s["text"] for s in subs], ["问题？", "答案。"])
        self.assertEqual([(s["from"], s["to"]) for s in subs], [(74, 98), (164, 173)])
        self.assertTrue(all(s["to"] <= 101 or s["from"] >= 161 for s in subs))

    def test_unalignable_or_invalid_speech_fails_instead_of_falling_back(self):
        cases = [[], [{"text": "旧文稿", "start": 0.4, "end": 1}],
                 [{"text": "新文稿", "start": 1, "end": 0.4}],
                 [{"text": "新文稿", "start": 0.4, "end": 9}],
                 [{"text": "新文稿", "start": float("nan"), "end": 1}]]
        for events in cases:
            with self.subTest(events=events), self.assertRaisesRegex(ValueError, "speech|对齐|边界"):
                self.windows([{"seconds": 3, "voice": "新文稿。", "speech": events}])

    def test_precise_main_keeps_envelope_and_character_frames(self):
        self.write_timeline([{"seconds": 2, "voice": "问题？", "speech": [
            {"text": "问题", "start": 0.4, "end": 1.2}]}])
        write_pcm(self.samples / f"{self.name}-vo-narr.wav", [0] * 9600 + [1200] * 19200 + [0] * 19200)
        sub = self.run_subs()[0]
        self.assertEqual(sub.get("charFrames"), [0, 0, 0])
        self.assertEqual(len(sub["env"]), 21)

    def test_legacy_timeline_retains_proportional_windows(self):
        subs = self.windows([{"seconds": 3, "voice": "旧素材。"}, {"seconds": 1, "voice": ""}])
        self.assertEqual(subs, [{"from": 6, "to": 86, "text": "旧素材。"}])


if __name__ == "__main__":
    unittest.main()

"""V2 时间轴与静帧的一致性；不把画面内容重复抄进测试。"""
import json
import importlib
import sys
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.visuals.timeline import Beat, Timeline
from scripts.visuals.render import Layer, scene_svg, static_svg, storyboard_svg
from scripts.visuals.primitives import current_flow, reveal_path, parameter_sweep, camera, combine

NS = {"s": "http://www.w3.org/2000/svg"}


def fixture():
    beats = tuple(Beat(f"拍{i}", i, i + 1, f"第{i}拍的说明 & <变化>", hold=i == 5)
                  for i in range(6))
    tl = Timeline(960, 620, 6, beats, "标题 & <参数>")
    layers = [Layer(None, '<text x="10" y="20">常驻</text>')]
    layers += [Layer(b.name, f'<circle data-sample="{i}" cx="{100 + i}" cy="100" r="10"/>', (3, 4))
               for i, b in enumerate(beats)]
    return tl, layers


class AnimationV2Tests(unittest.TestCase):
    def test_final_caption_waits_for_its_beat(self):
        tl, layers = fixture()
        tree = ET.fromstring(scene_svg(tl, layers))
        final = next(n for n in tree.iter() if n.get("data-caption") == "拍5")
        self.assertEqual("0", final.get("opacity"))
        self.assertEqual("5s", final.find("s:animate", NS).get("begin"))

    def test_storyboard_never_contains_next_beats_geometry(self):
        tl, layers = fixture()
        tree = ET.fromstring(storyboard_svg(tl, layers))
        frames = [n for n in tree.iter() if n.get("data-storyboard-beat")]
        self.assertEqual(5, len(frames))
        for frame in frames:
            index = frame.get("data-storyboard-beat")[1:]
            self.assertEqual([index], [n.get("data-sample") for n in frame.iter() if n.get("data-sample")])

    def test_unselected_storyboard_beat_still_keeps_its_caption(self):
        tl, layers = fixture()
        text = "".join(ET.fromstring(storyboard_svg(tl, layers)).itertext())
        for beat in tl.beats:
            self.assertIn(beat.caption, text)

    def test_static_keeps_only_final_and_persistent_layers_with_final_transform(self):
        tl, layers = fixture()
        tree = ET.fromstring(static_svg(tl, layers))
        self.assertEqual(["5"], [n.get("data-sample") for n in tree.iter() if n.get("data-sample")])
        self.assertTrue(any(n.get("transform") == "translate(3 4)" for n in tree.iter()))
        self.assertFalse(any(n.tag.rsplit("}", 1)[-1].startswith("animate") for n in tree.iter()))

    def test_timeline_metadata_is_parseable_and_complete(self):
        tl, layers = fixture()
        tree = ET.fromstring(scene_svg(tl, layers))
        data = json.loads(tree.find("s:metadata", NS).text)
        self.assertEqual(6, data["duration"])
        self.assertEqual([b.name for b in tl.beats], [b["name"] for b in data["beats"]])

    def test_invalid_timeline_rejected(self):
        tl, _ = fixture()
        with self.assertRaises(ValueError):
            Timeline(960, 620, 99, tl.beats, "broken")
        with self.assertRaises(ValueError):
            Timeline(960, 620, 6, tl.beats[:-1], "broken")

    def test_symptom_record_survives_final_and_print_frames(self):
        from scripts.visuals.scenes.ch17_symptom_four_fields import FIELDS, scene

        tl, layers = scene()
        values = [field[1] for field in FIELDS]
        final = ET.fromstring(static_svg(tl, layers))
        final_text = {node.text for node in final.findall('.//s:text', NS)}
        self.assertEqual(set(values), set(values) & final_text,
                         '结论静帧必须保留四项已填写记录')

        completed = {tl.beats[0].name: 0, tl.beats[-1].name: len(values)}
        completed.update((beat.name, index)
                         for index, beat in enumerate(tl.beats[1:-1], 1))
        storyboard = ET.fromstring(storyboard_svg(tl, layers))
        for frame in storyboard.iter():
            beat = frame.get('data-storyboard-beat')
            if beat is None:
                continue
            with self.subTest(beat=beat):
                frame_text = {node.text for node in frame.findall('.//s:text', NS)}
                self.assertEqual(set(values[:completed[beat]]), set(values) & frame_text,
                                 '分镜须保留已填记录，且不能提前显示后续记录')

    def test_sample_hold_final_frame_keeps_full_trace(self):
        from scripts.visuals.scenes.ch08_sample_hold_v2 import scene

        tl, layers = scene()
        static = static_svg(tl, layers)
        for segment in ('M110,400', '520,180', 'L700,180', '864,220'):
            with self.subTest(segment=segment):
                self.assertIn(segment, static, '结论帧必须保留完整采样周期波形')

    def test_transfer_gate_final_frame_keeps_envelope(self):
        from scripts.visuals.scenes.ch08_transfer_gate_v2 import scene

        tl, layers = scene()
        static = static_svg(tl, layers)
        self.assertIn('M96,410 C180,410 240,380', static, '结论帧必须保留并联包络曲线')
        self.assertIn('20→26.7→20Ω', static, '结论帧必须保留包络标注')

    def test_mux_final_frame_keeps_timing_story(self):
        from scripts.visuals.scenes.ch08_mux_address_glitch_v2 import scene

        tl, layers = scene()
        static = static_svg(tl, layers)
        for needle in ('011', '111', '100', 'M120,440'):
            with self.subTest(needle=needle):
                self.assertIn(needle, static, '结论帧必须保留地址时序与 INH 脉冲')

    def test_virtual_short_final_frame_keeps_both_readings(self):
        from scripts.visuals.scenes.ch17_virtual_short_probe import scene

        tl, layers = scene()
        static = static_svg(tl, layers)
        for needle in ('2.500V', '2.508V', '8mV'):
            with self.subTest(needle=needle):
                self.assertIn(needle, static, '结论帧必须保留两次读数与压差')
        self.assertNotIn('读数：—', static, '结论帧不得退回占位读数')

    def test_source_types_final_frame_keeps_three_curves(self):
        from scripts.visuals.scenes.ch00_source_types_v2 import scene

        tl, layers = scene()
        static = static_svg(tl, layers)
        for needle in ('x1="260" y1="180" x2="260" y2="410"',   # 恒压竖线
                       'x1="120" y1="250" x2="660" y2="250"',   # 恒流水平线
                       'x1="120" y1="180" x2="470" y2="188"'):  # 真实源斜线
            with self.subTest(needle=needle):
                self.assertIn(needle, static, '结论帧不能只剩空坐标轴')

    def test_divider_loading_final_frame_keeps_load_branch(self):
        from scripts.visuals.scenes.ch00_divider_loading_v2 import scene

        tl, layers = scene()
        static = static_svg(tl, layers)
        self.assertIn('RL 10kΩ', static, '结论帧必须保留负载支路')
        self.assertIn('<rect x="624" y="380" width="32" height="46"', static, '负载电阻要画出来')

    def test_all_real_scenes_reproduce_checked_in_triplets(self):
        root = Path(__file__).resolve().parents[1]
        for source in sorted((root / 'scripts/visuals/scenes').glob('ch*.py')):
            module = importlib.import_module('scripts.visuals.scenes.' + source.stem)
            if not hasattr(module, 'scene'):  # 同目录允许静态插图场景。
                continue
            tl, layers = module.scene()
            for suffix, build in [('', scene_svg), ('-static', static_svg), ('-storyboard', storyboard_svg)]:
                output = root / 'assets/svg-v2' / (source.stem.replace('_', '-') + suffix + '.svg')
                self.assertEqual(build(tl, layers), output.read_text(encoding='utf-8'), str(output))

    def test_moving_primitives_have_static_print_snapshots(self):
        tl, _ = fixture()
        graphic = combine(current_flow('M0 0L10 10', 5, .8),
                          reveal_path('M0 0L10 10', 5, .8),
                          parameter_sweep(20, 10, 30, 5, .8, '末值'),
                          camera('<rect width="10" height="10"/>', 5, .8, dx=5))
        animated = scene_svg(tl, [Layer('拍5', graphic)])
        static = static_svg(tl, [Layer('拍5', graphic)])
        self.assertIn('<animateMotion', animated)
        self.assertNotIn('<animate', static)
        self.assertIn('cx="30"', static)


if __name__ == "__main__":
    unittest.main()

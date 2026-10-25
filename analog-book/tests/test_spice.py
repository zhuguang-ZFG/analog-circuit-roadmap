#!/usr/bin/env python3
"""SPICE 骨架：schema、测量解析、容差比较、真实运行与出图。"""
import json
import os
import re
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import plot_sim  # noqa: E402
import run_spice  # noqa: E402

REQUIRE = os.environ.get("BOOK_REQUIRE_NGSPICE") == "1"
NGSPICE = run_spice.find_ngspice()


class SchemaTests(unittest.TestCase):
    def test_discovers_the_rc_case(self):
        cases = run_spice.discover_cases()
        self.assertEqual(1, len(cases))
        case = cases[0]
        self.assertEqual("rc.cir", case.deck.name)
        self.assertEqual({"vfinal", "vhalf", "trise"}, set(case.spec["metrics"]))

    def test_deck_has_no_external_models(self):
        text = (ROOT / "assets" / "spice" / "ch01" / "rc.cir").read_text(
            encoding="utf-8")
        self.assertIn(".control", text)
        self.assertIn("wrdata", text)
        self.assertNotIn(".include", text.lower())
        self.assertNotIn(".lib", text.lower())
        self.assertNotIn("http", text.lower())
        self.assertIn("PULSE(", text)

    def test_tran_step_is_positive(self):
        text = (ROOT / "assets" / "spice" / "ch01" / "rc.cir").read_text(
            encoding="utf-8")
        match = re.search(r"^\s*\.tran\s+(\S+)", text, re.M)
        self.assertIsNotNone(match, "deck 缺少 .tran 指令")
        number = re.match(r"([-+]?(?:\d+\.?\d*|\.\d+))", match.group(1))
        self.assertIsNotNone(number, "TSTEP 不是数值")
        self.assertGreater(float(number.group(1)), 0,
                           "TSTEP 必须大于 0，ngspice 拒绝 TSTEP=0")

    def test_rejects_negative_tolerance(self):
        spec = json.loads(
            (ROOT / "assets" / "spice" / "ch01" / "assert.json").read_text(
                encoding="utf-8"))
        spec["metrics"]["vfinal"]["tolerance"] = -1
        with self.assertRaises(ValueError):
            run_spice.validate_spec(spec, Path("rc.cir"))

    def test_rejects_orphan_assertion(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "assert.json").write_text("{}", encoding="utf-8")
            with self.assertRaises(ValueError):
                run_spice.discover_cases(root)


class ParsingTests(unittest.TestCase):
    def test_parses_measurements_in_scientific_notation(self):
        text = """
vfinal = 5.000000e+00
vhalf = 7.034000e-05
trise = 2.197000e-04
"""
        values = run_spice.parse_measurements(text)
        self.assertAlmostEqual(5.0, values["vfinal"])
        self.assertAlmostEqual(70.34e-6, values["vhalf"])
        self.assertAlmostEqual(219.7e-6, values["trise"])

    def test_compare_accepts_inside_tolerance(self):
        expected = {"vfinal": {"expected": 5.0, "tolerance": 0.02}}
        self.assertEqual([], run_spice.compare_metrics({"vfinal": 5.01}, expected))

    def test_compare_rejects_outside_tolerance_and_missing(self):
        expected = {"vfinal": {"expected": 5.0, "tolerance": 0.02}}
        self.assertTrue(run_spice.compare_metrics({"vfinal": 5.1}, expected))
        self.assertTrue(run_spice.compare_metrics({}, expected))

    def test_load_data_skips_header_and_requires_rows(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "rc.dat"
            path.write_text("time v(out)\n0 0\n1e-6 0.1\n2e-6 0.2\n",
                            encoding="utf-8")
            rows = run_spice.load_data(path, min_rows=3)
            self.assertEqual(3, len(rows))
            self.assertAlmostEqual(0.2, rows[-1][1])
            with self.assertRaises(ValueError):
                run_spice.load_data(path, min_rows=10)


@unittest.skipIf(NGSPICE is None and not REQUIRE,
                 "未安装 ngspice；设置 BOOK_REQUIRE_NGSPICE=1 可强制")
class SimulationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if NGSPICE is None:
            raise RuntimeError("BOOK_REQUIRE_NGSPICE=1 但找不到 ngspice")
        cls.tmp = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.tmp.cleanup)
        cls.out = Path(cls.tmp.name)
        case = run_spice.discover_cases()[0]
        cls.result = run_spice.run_case(case, NGSPICE, output_dir=cls.out)
        cls.case = case

    def test_metrics_match_rc_theory(self):
        self.assertEqual([], self.result["problems"], self.result["log"])
        self.assertAlmostEqual(5.0, self.result["metrics"]["vfinal"], delta=0.02)
        self.assertAlmostEqual(69.3e-6, self.result["metrics"]["vhalf"],
                               delta=5e-6)
        self.assertAlmostEqual(219.7e-6, self.result["metrics"]["trise"],
                               delta=20e-6)

    def test_data_is_written_and_monotonic(self):
        path = self.out / self.case.spec["data"]
        rows = run_spice.load_data(path, min_rows=200)
        self.assertGreaterEqual(len(rows), 200)
        self.assertTrue(all(b[0] > a[0] for a, b in zip(rows, rows[1:])))
        self.assertAlmostEqual(5.0, rows[-1][1], delta=0.03)

    def test_plot_is_generated_from_simulation_data(self):
        path = self.out / self.case.spec["data"]
        output = self.out / "rc-step.svg"
        plot_sim.plot(path, output, "RC 一阶阶跃响应")
        text = output.read_text(encoding="utf-8")
        self.assertIn("<svg", text)
        self.assertIn("ngspice", text)
        self.assertIn("RC 一阶阶跃响应", text)


if __name__ == "__main__":
    unittest.main()

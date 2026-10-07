"""Regenerate SVGs in a temporary directory and check the published assets.

Run: python -B -m unittest discover -s scripts -p test_svg_assets.py -v
Requires the generator's existing NumPy dependency. No repository file is written.
"""
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]


class SvgAssetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        temporary = tempfile.TemporaryDirectory(prefix="analog-svg-parity-")
        cls.addClassCleanup(temporary.cleanup)
        work = Path(temporary.name)
        scripts = work / "scripts"
        scripts.mkdir()
        generator = scripts / "generate_svgs.py"
        shutil.copyfile(ROOT / "scripts" / "generate_svgs.py", generator)
        result = subprocess.run(
            [sys.executable, "-B", str(generator)], cwd=work,
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=60,
        )
        if result.returncode:
            raise RuntimeError("SVG generator failed:\n" + result.stdout + result.stderr)
        cls.expected = {p.name: p for p in (work / "assets" / "svg").glob("*.svg")}
        if not cls.expected:
            raise AssertionError("The generator produced no SVG assets")
        cls.actual = {p.name: p for p in (ROOT / "assets" / "svg").glob("*.svg")}

    def test_asset_inventory(self):
        self.assertEqual(set(self.actual), set(self.expected),
                         "Published SVG inventory must match the generator")

    def test_asset_content(self):
        for name in sorted(self.actual.keys() & self.expected.keys()):
            with self.subTest(asset=name):
                # Universal newlines avoid platform-only LF/CRLF differences.
                actual = self.actual[name].read_text(encoding="utf-8")
                expected = self.expected[name].read_text(encoding="utf-8")
                self.assertEqual(actual, expected,
                                 "Regenerate the SVG after changing its source")

    def test_svg_documents(self):
        for name, path in sorted(self.actual.items()):
            with self.subTest(asset=name):
                root = ET.parse(path).getroot()
                self.assertEqual(root.tag, "{http://www.w3.org/2000/svg}svg")
                for elem in root.iter():
                    for v in elem.attrib.values():
                        self.assertNotRegex(v, r'\{[A-Za-z_]\w*\}',
                                            f"{name}: literal brace marker in attribute")


if __name__ == "__main__":
    unittest.main()

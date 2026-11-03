#!/usr/bin/env python3
from __future__ import annotations
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import check_chapter_contract  # noqa: E402

VALID = """<a id="ch1"></a>
## 第 1 章 无源元件的真实面目

<!-- slot:hook -->
### 1.1 钩子现象
灯一闪。

<!-- slot:intuition -->
### 1.2 直觉
先想回路。

<!-- slot:quant -->
### 1.3 定量推导
> **口诀**：电阻吃电压。
**算一笔**：R = 1 kΩ，V = 5 V，则 I = 5 mA。

<!-- slot:limits -->
### 1.4 失效边界
频率高了模型崩。

<!-- slot:lab -->
### 1.5 动手验证
<figure><img src="assets/figures/ch01-hero-parasitics.svg"></figure>
> **图问**：图中寄生从哪一端先夺权？

<!-- slot:selfcheck -->
### 1.6 自检
### 验收清单
- [ ] 观察：摸温度
- [ ] 计算：算 τ
- [ ] 测量：示波器看波形
"""


class ChapterContractTests(unittest.TestCase):
    def test_valid_fixture_all_true(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "ch.md"
            p.write_text(VALID, encoding="utf-8")
            result = check_chapter_contract.scan_chapter(p)
            self.assertTrue(all(result.values()), result)

    def test_empty_file_all_false(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "ch.md"
            p.write_text("", encoding="utf-8")
            result = check_chapter_contract.scan_chapter(p)
            self.assertFalse(any(result.values()), result)


if __name__ == "__main__":
    unittest.main()

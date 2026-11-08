# 代理审图报告（2026-11-07）

> **性质**：用户于 2026-11-07 选择「授权代理审图」。本报告是机器辅助评分，**不是人工签字**；manifest 逐条写明 `reviewed_by: agent-proxy`，用户保留抽检、否决和回退权。

- 待审 `generated`：**129** 张
- 可推进：**129** 张；阻断：**0** 张
- 逐图分数：`docs/superpowers/visual/reviews/agent-review-2026-11-07.csv`

## 评分口径

| 维度 | 5 分 | 4 分 | 阻断 |
|---|---|---|---|
| 教学必要性 | 所在章最长无图段 >1500 | 其余 | — |
| 事实精度 | 有 source_facts 与 prompt | 缺其一 | 缺 source_facts / prompt 文件 |
| 构图层级 | 版面 bounds=pass 且文本 ≥8（动画 ≥4 拍） | 文本 4–7 或动画 3 拍 | bounds 失败 / 文本 <4 / 缺 beats |
| 风格一致性 | style_id 在锁定集合且 layout/color 齐全 | 缺 layout 或 color | style_id 不在锁定集合 |
| 印刷可读性 | 最小字号 ≥9.0pt（动画有 print fallback 与 reduced_motion） | 8.5–9.0pt / 缺其一 | <8.5pt |
| 运动叙事 | ≥4 拍且结论帧有效 | 3 拍 | 缺结论帧 / <3 拍 |
| 交互节奏 | 6–20s 且 3–5 拍 | 4–30s 且 2–6 拍 | 超出范围 |

## 分章统计

| 章 | 静态 | 动画 | 小计 |
|---:|---:|---:|---:|
| 0 | 0 | 4 | 4 |
| 1 | 5 | 0 | 5 |
| 2 | 8 | 0 | 8 |
| 3 | 7 | 0 | 7 |
| 4 | 5 | 0 | 5 |
| 5 | 4 | 0 | 4 |
| 6 | 3 | 0 | 3 |
| 7 | 3 | 0 | 3 |
| 8 | 0 | 4 | 4 |
| 9 | 4 | 0 | 4 |
| 10 | 6 | 0 | 6 |
| 11 | 7 | 0 | 7 |
| 12 | 6 | 0 | 6 |
| 13 | 8 | 0 | 8 |
| 14 | 7 | 0 | 7 |
| 15 | 19 | 0 | 19 |
| 16 | 8 | 0 | 8 |
| 17 | 1 | 4 | 5 |
| 18 | 16 | 0 | 16 |

## 阻断项

无。

## 逐图分数

| id | 章 | 类型 | 必要性 | 事实 | 构图 | 风格 | 印刷 | 叙事 | 节奏 | 合计 |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `ch17-virtual-short-test` | 17 | V3 | 5 | 5 | 5 | 5 | 4 | — | — | 24 |
| `ch17-symptom-four-fields` | 17 | A5 | 5 | 5 | 5 | 5 | 5 | 5 | 4 | 34 |
| `ch17-esr-sweep` | 17 | A3 | 5 | 5 | 5 | 5 | 5 | 5 | 5 | 35 |
| `ch17-virtual-short-probe` | 17 | A5 | 5 | 5 | 5 | 5 | 5 | 5 | 5 | 35 |
| `ch17-subharmonic-edge` | 17 | A4 | 5 | 5 | 5 | 5 | 5 | 5 | 4 | 34 |
| `ch00-current-loop-v2` | 0 | A1 | 4 | 5 | 5 | 5 | 5 | 5 | 5 | 34 |
| `ch00-divider-derivation-v2` | 0 | A2 | 4 | 5 | 5 | 5 | 5 | 5 | 5 | 34 |
| `ch00-divider-loading-v2` | 0 | A4 | 4 | 5 | 5 | 5 | 5 | 5 | 5 | 34 |
| `ch00-source-types-v2` | 0 | A1 | 4 | 5 | 5 | 5 | 5 | 5 | 5 | 34 |
| `ch08-transfer-gate-v2` | 8 | A1 | 4 | 5 | 5 | 5 | 5 | 5 | 5 | 34 |
| `ch08-mux-address-glitch-v2` | 8 | A4 | 4 | 5 | 5 | 5 | 5 | 5 | 5 | 34 |
| `ch08-charge-injection-v2` | 8 | A4 | 4 | 5 | 5 | 5 | 5 | 5 | 5 | 34 |
| `ch08-sample-hold-v2` | 8 | A1 | 4 | 5 | 5 | 5 | 5 | 5 | 5 | 34 |
| `ch18-power-three-touchpoints` | 18 | V4 | 5 | 5 | 5 | 5 | 4 | — | — | 24 |
| `ch18-dmm-averaging` | 18 | V4 | 5 | 5 | 5 | 5 | 4 | — | — | 24 |
| `ch18-probe-loading` | 18 | V4 | 5 | 5 | 5 | 5 | 4 | — | — | 24 |
| `ch18-reset-clock-enable` | 18 | V5 | 5 | 5 | 5 | 5 | 4 | — | — | 24 |
| `ch18-measurement-snr` | 18 | V4 | 5 | 5 | 5 | 5 | 4 | — | — | 24 |
| `ch18-ground-lead-inductance` | 18 | V4 | 5 | 5 | 5 | 5 | 4 | — | — | 24 |
| `ch14-thermal-budget` | 14 | V3 | 5 | 5 | 5 | 5 | 4 | — | — | 24 |
| `ch14-ltspice-five` | 14 | V5 | 5 | 5 | 5 | 5 | 4 | — | — | 24 |
| `ch14-tolerance-three` | 14 | V4 | 5 | 5 | 5 | 5 | 4 | — | — | 24 |
| `ch14-dft-testpoints` | 14 | V4 | 5 | 5 | 5 | 5 | 4 | — | — | 24 |
| `ch18-assumption-tree` | 18 | V4 | 5 | 5 | 5 | 5 | 4 | — | — | 24 |
| `ch18-fault-record` | 18 | V4 | 5 | 5 | 5 | 5 | 4 | — | — | 24 |
| `ch18-two-way-validation` | 18 | V4 | 5 | 5 | 5 | 5 | 4 | — | — | 24 |
| `ch14-derating-margin` | 14 | V4 | 5 | 5 | 5 | 5 | 4 | — | — | 24 |
| `ch15-trace-drop` | 15 | V4 | 5 | 5 | 5 | 5 | 4 | — | — | 24 |
| `ch13-h-bridge-states` | 13 | V4 | 5 | 5 | 5 | 5 | 4 | — | — | 24 |
| `ch13-current-sense-sides` | 13 | V4 | 5 | 5 | 5 | 5 | 4 | — | — | 24 |
| `ch13-opto-ctr` | 13 | V4 | 5 | 5 | 5 | 5 | 4 | — | — | 24 |
| `ch15-layout-ten-questions` | 15 | V4 | 5 | 5 | 5 | 5 | 4 | — | — | 24 |
| `ch15-crystal-three-no` | 15 | V4 | 5 | 5 | 5 | 5 | 4 | — | — | 24 |
| `ch15-four-zones` | 15 | V4 | 5 | 5 | 5 | 5 | 4 | — | — | 24 |
| `ch16-bisect-injection` | 16 | V3 | 5 | 5 | 5 | 5 | 4 | — | — | 24 |
| `ch16-case-triage` | 16 | V4 | 5 | 5 | 5 | 5 | 4 | — | — | 24 |
| `ch18-predict-before-probe` | 18 | V4 | 5 | 5 | 5 | 5 | 4 | — | — | 24 |
| `ch18-first-minute` | 18 | V4 | 5 | 5 | 5 | 5 | 4 | — | — | 24 |
| `ch18-four-wire` | 18 | V4 | 5 | 5 | 5 | 5 | 4 | — | — | 24 |
| `ch14-arrhenius-ten-degree` | 14 | V4 | 5 | 5 | 5 | 5 | 4 | — | — | 24 |
| `ch18-swap-discipline` | 18 | V4 | 5 | 5 | 5 | 5 | 4 | — | — | 24 |
| `ch18-component-signatures` | 18 | V4 | 5 | 5 | 5 | 5 | 4 | — | — | 24 |
| `ch18-temp-spray` | 18 | V4 | 5 | 5 | 5 | 5 | 4 | — | — | 24 |
| `ch16-instrument-trust` | 16 | V4 | 5 | 5 | 5 | 5 | 4 | — | — | 24 |
| `ch16-postmortem-split` | 16 | V4 | 5 | 5 | 5 | 5 | 4 | — | — | 24 |
| `ch15-thermal-relief` | 15 | V4 | 5 | 5 | 5 | 5 | 4 | — | — | 24 |
| `ch15-via-parallel` | 15 | V3 | 5 | 5 | 5 | 5 | 4 | — | — | 24 |
| `ch15-crosstalk-3w` | 15 | V4 | 5 | 5 | 5 | 5 | 4 | — | — | 24 |
| `ch15-testpoint-rules` | 15 | V5 | 5 | 5 | 5 | 5 | 4 | — | — | 24 |
| `ch15-panelization` | 15 | V4 | 5 | 5 | 5 | 5 | 4 | — | — | 24 |
| `ch15-dfm-limits` | 15 | V4 | 5 | 5 | 5 | 5 | 4 | — | — | 24 |
| `ch15-failure-signatures` | 15 | V5 | 5 | 5 | 5 | 5 | 4 | — | — | 24 |
| `ch16-first-question` | 16 | V4 | 5 | 5 | 5 | 5 | 4 | — | — | 24 |
| `ch16-probe-compensation` | 16 | V4 | 5 | 5 | 5 | 5 | 4 | — | — | 24 |
| `ch15-adc-straddle` | 15 | V4 | 5 | 5 | 5 | 5 | 4 | — | — | 24 |
| `ch15-return-review` | 15 | V4 | 5 | 5 | 5 | 5 | 4 | — | — | 24 |
| `ch15-ground-grid` | 15 | V4 | 5 | 5 | 5 | 5 | 4 | — | — | 24 |
| `ch16-bandwidth-five` | 16 | V4 | 5 | 5 | 5 | 5 | 4 | — | — | 24 |
| `ch01-e24-ladder` | 1 | V4 | 5 | 5 | 5 | 5 | 4 | — | — | 24 |
| `ch04-gate-window` | 4 | V4 | 5 | 5 | 5 | 5 | 4 | — | — | 24 |
| `ch04-deadtime-ledger` | 4 | V4 | 5 | 5 | 5 | 5 | 4 | — | — | 24 |
| `ch05-tristate-handover` | 5 | V4 | 5 | 5 | 5 | 5 | 4 | — | — | 24 |
| `ch07-hysteresis-window` | 7 | V4 | 5 | 5 | 5 | 5 | 4 | — | — | 24 |
| `ch09-esr-window` | 9 | V4 | 5 | 5 | 5 | 5 | 4 | — | — | 24 |
| `ch05-rp-power` | 5 | V4 | 5 | 5 | 5 | 5 | 4 | — | — | 24 |
| `ch09-reference-ladder` | 9 | V4 | 5 | 5 | 5 | 5 | 4 | — | — | 24 |
| `ch10-monostable-budget` | 10 | V4 | 5 | 5 | 5 | 5 | 4 | — | — | 24 |
| `ch10-recovery-gap` | 10 | V4 | 5 | 5 | 5 | 5 | 4 | — | — | 24 |
| `ch11-mirror-three-errors` | 11 | V4 | 5 | 5 | 5 | 5 | 4 | — | — | 24 |
| `ch12-tia-three-way` | 12 | V4 | 5 | 5 | 5 | 5 | 4 | — | — | 24 |
| `ch12-switch-cap` | 12 | V4 | 5 | 5 | 5 | 5 | 4 | — | — | 24 |
| `ch12-input-types` | 12 | V4 | 5 | 5 | 5 | 5 | 4 | — | — | 24 |
| `ch06-bias-balance` | 6 | V4 | 5 | 5 | 5 | 5 | 4 | — | — | 24 |
| `ch02-esd-chain` | 2 | V4 | 5 | 5 | 5 | 5 | 4 | — | — | 24 |
| `ch02-zener-budget` | 2 | V4 | 5 | 5 | 5 | 5 | 4 | — | — | 24 |
| `ch02-junction-margin` | 2 | V4 | 5 | 5 | 5 | 5 | 4 | — | — | 24 |
| `ch02-parallel-hog` | 2 | V4 | 5 | 5 | 5 | 5 | 4 | — | — | 24 |
| `ch03-switch-budget` | 3 | V4 | 5 | 5 | 5 | 5 | 4 | — | — | 24 |
| `ch03-low-high-side` | 3 | V4 | 5 | 5 | 5 | 5 | 4 | — | — | 24 |
| `ch03-reverse-beta` | 3 | V4 | 5 | 5 | 5 | 5 | 4 | — | — | 24 |
| `ch03-config-impedance` | 3 | V4 | 5 | 5 | 5 | 5 | 4 | — | — | 24 |
| `ch03-early-effect` | 3 | V4 | 5 | 5 | 5 | 5 | 4 | — | — | 24 |
| `ch11-miller-bandwidth` | 11 | V4 | 5 | 5 | 5 | 5 | 4 | — | — | 24 |
| `ch13-compliance-ceiling` | 13 | V4 | 5 | 5 | 5 | 5 | 4 | — | — | 24 |
| `ch13-current-sense-budget` | 13 | V4 | 5 | 5 | 5 | 5 | 4 | — | — | 24 |
| `ch01-electrolytic-life` | 1 | V4 | 5 | 5 | 5 | 5 | 4 | — | — | 24 |
| `ch01-derating-product` | 1 | V4 | 5 | 5 | 5 | 5 | 4 | — | — | 24 |
| `ch04-dvdt-false-turnon` | 4 | V4 | 5 | 5 | 5 | 5 | 4 | — | — | 24 |
| `ch06-slew-vs-gbw` | 6 | V4 | 5 | 5 | 5 | 5 | 4 | — | — | 24 |
| `ch07-pullup-three-accounts` | 7 | V4 | 5 | 5 | 5 | 5 | 4 | — | — | 24 |
| `ch07-threshold-budget` | 7 | V4 | 5 | 5 | 5 | 5 | 4 | — | — | 24 |
| `ch10-astable-reverse-design` | 10 | V4 | 5 | 5 | 5 | 5 | 4 | — | — | 24 |
| `ch10-duty-fifty-paths` | 10 | V4 | 5 | 5 | 5 | 5 | 4 | — | — | 24 |
| `ch05-shoot-through-ledger` | 5 | V4 | 5 | 5 | 5 | 5 | 4 | — | — | 24 |
| `ch05-ab-bias-thermal` | 5 | V4 | 5 | 5 | 5 | 5 | 4 | — | — | 24 |
| `ch09-ldo-four-accounts` | 9 | V4 | 5 | 5 | 5 | 5 | 4 | — | — | 24 |
| `ch11-two-stage-margin` | 11 | V4 | 5 | 5 | 5 | 5 | 4 | — | — | 24 |
| `ch12-switched-cap-equivalent` | 12 | V4 | 5 | 5 | 5 | 5 | 4 | — | — | 24 |
| `ch12-input-stage-source-z` | 12 | V4 | 5 | 5 | 5 | 5 | 4 | — | — | 24 |
| `ch11-phase-margin-table` | 11 | V4 | 5 | 5 | 5 | 5 | 4 | — | — | 24 |
| `ch06-741-four-blocks` | 6 | V4 | 5 | 5 | 5 | 5 | 4 | — | — | 24 |
| `ch01-thevenin-two-load` | 1 | V4 | 5 | 5 | 5 | 5 | 4 | — | — | 24 |
| `ch02-rectifier-voltage-ledger` | 2 | V4 | 5 | 5 | 5 | 5 | 4 | — | — | 24 |
| `ch02-protection-order` | 2 | V4 | 5 | 5 | 5 | 5 | 4 | — | — | 24 |
| `ch11-noise-three-taxes` | 11 | V4 | 5 | 5 | 5 | 5 | 4 | — | — | 24 |
| `ch12-riso-feedback-point` | 12 | V4 | 5 | 5 | 5 | 5 | 4 | — | — | 24 |
| `ch13-audio-class-heat` | 13 | V4 | 5 | 5 | 5 | 5 | 4 | — | — | 24 |
| `ch11-diffpair-four-beats` | 11 | V4 | 5 | 5 | 5 | 5 | 4 | — | — | 24 |
| `ch02-bridge-junction-ledger` | 2 | V4 | 5 | 5 | 5 | 5 | 4 | — | — | 24 |
| `ch04-thermal-chain-ledger` | 4 | V4 | 5 | 5 | 5 | 5 | 4 | — | — | 24 |
| `ch01-q-selectivity-map` | 1 | V4 | 5 | 5 | 5 | 5 | 4 | — | — | 24 |
| `ch02-diode-fault-order` | 2 | V4 | 5 | 5 | 5 | 5 | 4 | — | — | 24 |
| `ch15-radiated-loop-area` | 15 | V4 | 5 | 5 | 5 | 5 | 4 | — | — | 24 |
| `ch09-tl431-divider-floor` | 9 | V4 | 5 | 5 | 5 | 5 | 4 | — | — | 24 |
| `ch13-crystal-neg-resistance` | 13 | V4 | 5 | 5 | 5 | 5 | 4 | — | — | 24 |
| `ch13-sampling-quantization` | 13 | V4 | 5 | 5 | 5 | 5 | 4 | — | — | 24 |
| `ch14-pt100-error-budget` | 14 | V4 | 5 | 5 | 5 | 5 | 4 | — | — | 24 |
| `ch10-555-fault-tree` | 10 | V4 | 5 | 5 | 5 | 5 | 4 | — | — | 24 |
| `ch10-555-threshold-clamp` | 10 | V4 | 5 | 5 | 5 | 5 | 4 | — | — | 24 |
| `ch03-ce-swing-budget` | 3 | V4 | 5 | 5 | 5 | 5 | 4 | — | — | 24 |
| `ch15-return-mirror` | 15 | V4 | 5 | 5 | 5 | 5 | 4 | — | — | 24 |
| `ch15-ground-bounce-ledger` | 15 | V4 | 5 | 5 | 5 | 5 | 4 | — | — | 24 |
| `ch15-ground-freq-split` | 15 | V4 | 5 | 5 | 5 | 5 | 4 | — | — | 24 |
| `ch15-stackup-bridge` | 15 | V4 | 5 | 5 | 5 | 5 | 4 | — | — | 24 |
| `ch16-record-card` | 16 | V4 | 5 | 5 | 5 | 5 | 4 | — | — | 24 |
| `ch11-noise-identify` | 11 | V4 | 5 | 5 | 5 | 5 | 4 | — | — | 24 |
| `ch04-channel-formation` | 4 | V4 | 5 | 5 | 5 | 5 | 4 | — | — | 24 |
| `ch03-region-check` | 3 | V4 | 5 | 5 | 5 | 5 | 4 | — | — | 24 |
| `ch18-williams-workbench` | 18 | V1 | 5 | 5 | 5 | 5 | 4 | — | — | 24 |

2026-11-07 算术勘误：动画合计改为五项通用分加两项动画分；原始逐维分数保持不变。本次仅修正合计，不代表重新审图。

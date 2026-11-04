---
id: ch17-virtual-short-probe
generator: svg-v2-scene
reference_policy: none
numbers:
- 8mV
zh_prompt: |
  风格名称：几何图式叙事。主题色：象牙白（Ivory）、佩恩灰（Payne's grey）、赭石（Ochre）。
  动画类型：A5 操作演示。节拍 5：认脚 → 量V− → 量V+ → 算压差 → 判读（结论停留）。
  画面：中央运放三角形（V−/V+ 引脚标注）；右上万用表卡依次出现读数——第一步表笔落 V− 读数 2.500V（蓝色探针圈），第二步表笔落 V+ 读数 2.508V（红色探针圈），压差卡「2.508 − 2.500 = 8mV」（赭石）；结论帧绿色判读卡「压差 8mV 远小于几十 mV 阈值 → 虚短成立；运放两输入端近似等电位，反馈在正常工作——问题不在运放，嫌疑移交：供电、前级信号、输出负载」。
en_prompt: |
  Style name: Geometric Diagrammatic Narrative. Theme color: Ivory, Payne's grey, Ochre.
  Animation type: A5 procedure demo. Five beats: identify pins → probe V− → probe V+ → difference → verdict (hold final frame).
  Canvas: an op-amp triangle center stage with V−/V+ pins; a multimeter card top-right fills in readings — probe lands on V− (blue probe ring) reading 2.500V, then on V+ (red ring) reading 2.508V; an ochre card computes "2.508 − 2.500 = 8mV"; the final green verdict card: "8mV is far below the tens-of-mV threshold → virtual short holds; both inputs sit at nearly the same potential and the feedback is working — the fault is not the op-amp. Hand the suspects on: supply, preceding stage, output load."
  beats: [认脚, 量V−, 量V+, 算压差, 判读]
  duration: 7.5s
  reduced_motion: assets/svg-v2/ch17-virtual-short-probe-static.svg
  storyboard: assets/svg-v2/ch17-virtual-short-probe-storyboard.svg
---

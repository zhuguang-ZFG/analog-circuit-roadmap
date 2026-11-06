# 待审图清单（119 张 generated）

本页只索引**尚未人工签核**的手绘候选：全部 `status: generated`，`review_scores` 为空，
因此**未插入正文**——正文只接受 `accepted`（否则 `build_book.py` 抛 `BookError`）。

## 口径声明

- 本包是**几何与数字证据包**，不含图像阅读结论：视觉模型当前不可用，没有读过任何一张图。
- 每张图已过：出画布 0、文字互压 0、后画矩形不盖字、16K/138mm 最小字号 ≥ 8.5pt、
  图内数字 ⊆ anchor 原文、alt 数字 ⊆ 图面数字。
- 审图请对照 `contact-pending.html`（一页 24 张，带 manifest 元数据与评分栏）。

## 签核方式

1. 在 `contact-pending.html` 里按五项打分（布局 / 可读性 / 术语准确 / 数字一致 / 图注一致）。
2. 五项都 ≥4 的，把 `status: generated` 改为 `accepted`，补 `review_scores`、`status_history`、
   `review_record`（含 reviewer 与日期），`asset_sha256` 必须按当前 SVG 字节重算。
3. 任何一张重绘后 SHA 变化，签核作废，必须回退 `generated`。

## 清单

| # | 章 | anchor | id | 用途 | 源事实数 |
|---:|---:|---|---|---|---:|
| 1 | 0 | 0.2 | `ch00-current-loop-v2` | 闭合回路中的约定电流与串联压降（Task 8 正文试片，待风格复评） | 1 |
| 2 | 0 | 0.3 | `ch00-divider-derivation-v2` | 空载分压公式的逐步推导（Task 8 正文试片，待风格复评） | 1 |
| 3 | 0 | 0.3 | `ch00-divider-loading-v2` | 分压器从空载到带载的塌陷与输出电阻判据 | 1 |
| 4 | 0 | 0.6 | `ch00-source-types-v2` | 恒压源与恒流源的 V-I 曲线、输出阻抗与接法 | 1 |
| 5 | 1 | 1.1 | `ch01-e24-ladder` | E24 档位与 3.3k 的来历 | 1 |
| 6 | 1 | 1.4 | `ch01-thevenin-two-load` | 戴维南等效与两负载法实测内阻 | 1 |
| 7 | 1 | 1.5 | `ch01-q-selectivity-map` | Q 是挑频率的锐度，不是越高越好 | 1 |
| 8 | 1 | 1.7 | `ch01-derating-product` | 降容是乘法：三项八折只剩一半 | 1 |
| 9 | 1 | 1.7 | `ch01-electrolytic-life` | 10°C 翻倍法则下的电解电容寿命账 | 1 |
| 10 | 2 | 2.10 | `ch02-rectifier-voltage-ledger` | 桥式整流的电压分账与峰值电流 | 1 |
| 11 | 2 | 2.11.3 | `ch02-esd-chain` | IEC 8kV 的 24A 分账 | 1 |
| 12 | 2 | 2.12 | `ch02-bridge-junction-ledger` | 桥堆与整流管的四个数与结温账 | 1 |
| 13 | 2 | 2.13 | `ch02-diode-fault-order` | 二极管排故的三步顺序 | 1 |
| 14 | 2 | 2.8 | `ch02-protection-order` | 接口保护三件套的先后次序 | 1 |
| 15 | 2 | 2.9 | `ch02-junction-margin` | 结温余量只剩 3°C | 1 |
| 16 | 2 | 2.9 | `ch02-parallel-hog` | 并联二极管的热抢流 | 1 |
| 17 | 2 | 2.9 | `ch02-zener-budget` | 稳压管的限流电阻与最坏功耗 | 1 |
| 18 | 3 | 3.1 | `ch03-early-effect` | 厄利效应与输出阻抗 | 1 |
| 19 | 3 | 3.2 | `ch03-reverse-beta` | C/E 反接为什么β只剩个位数 | 1 |
| 20 | 3 | 3.3 | `ch03-config-impedance` | 三种组态共用一条阻抗折算律 | 1 |
| 21 | 3 | 3.5 | `ch03-low-high-side` | 低边与高边开关的参考点 | 1 |
| 22 | 3 | 3.5 | `ch03-switch-budget` | 继电器基极电阻的两笔账 | 1 |
| 23 | 3 | 3.9 | `ch03-ce-swing-budget` | 共射级的摆幅预算与削波方向 | 1 |
| 24 | 4 | 4.3 | `ch04-dvdt-false-turnon` | dv/dt 误导通的定量图像 | 1 |
| 25 | 4 | 4.4 | `ch04-deadtime-ledger` | 死区损耗的明账 | 1 |
| 26 | 4 | 4.4 | `ch04-gate-window` | 栅极保护的电压窗 | 1 |
| 27 | 4 | 4.5 | `ch04-thermal-chain-ledger` | 热失效的热阻链与四种测量自欺 | 1 |
| 28 | 5 | 5.2 | `ch05-rp-power` | 上拉电阻自己的功耗 | 1 |
| 29 | 5 | 5.4 | `ch05-tristate-handover` | 三态总线的交接时序 | 1 |
| 30 | 5 | 5.6 | `ch05-ab-bias-thermal` | AB 类偏置的热耦合与散热器两笔账 | 1 |
| 31 | 5 | 5.6 | `ch05-shoot-through-ledger` | 推挽正常半周与直通的电流功率对账 | 1 |
| 32 | 6 | 6.1 | `ch06-741-four-blocks` | 741 内部四级的分工与补偿代价 | 1 |
| 33 | 6 | 6.3 | `ch06-bias-balance` | 输入偏置电流与平衡电阻 | 1 |
| 34 | 6 | 6.7 | `ch06-slew-vs-gbw` | 压摆率与全功率带宽的两套物理 | 1 |
| 35 | 7 | 7.2 | `ch07-pullup-three-accounts` | 上拉电阻同时挂在三本账上 | 1 |
| 36 | 7 | 7.2 | `ch07-threshold-budget` | 阈值精度的误差预算排序 | 1 |
| 37 | 7 | 7.3 | `ch07-hysteresis-window` | 迟滞窗口与两个阈值 | 1 |
| 38 | 8 | 8.1 | `ch08-transfer-gate-v2` | 传输门的阈值缺口与互补并联（技术原型，待风格复评） | 1 |
| 39 | 8 | 8.2 | `ch08-mux-address-glitch-v2` | 4051 地址跳变的路过通道与 INH 对策（技术原型，待风格复评） | 1 |
| 40 | 8 | 8.4 | `ch08-sample-hold-v2` | 采样保持四拍与一个电容的三笔账（技术原型，待风格复评） | 1 |
| 41 | 8 | 8.6 | `ch08-charge-injection-v2` | 关断瞬间电荷注入的两路分账（技术原型，待风格复评） | 1 |
| 42 | 9 | 9.1 | `ch09-reference-ladder` | 基准选型的精度阶梯 | 1 |
| 43 | 9 | 9.2 | `ch09-tl431-divider-floor` | TL431 分压电阻的下限 | 1 |
| 44 | 9 | 9.3 | `ch09-esr-window` | LDO 的 ESR 稳定窗口 | 1 |
| 45 | 9 | 9.4 | `ch09-ldo-four-accounts` | 7805 四种死法对应的四本账 | 1 |
| 46 | 10 | 10.1 | `ch10-555-threshold-clamp` | 555 的两条门限与占空比 | 1 |
| 47 | 10 | 10.3 | `ch10-555-fault-tree` | 555 故障图谱五站定位 | 1 |
| 48 | 10 | 10.4 | `ch10-astable-reverse-design` | 按 38kHz 目标反推 555 元件值 | 1 |
| 49 | 10 | 10.4 | `ch10-duty-fifty-paths` | 准 50% 占空比的三条路与两个极端 | 1 |
| 50 | 10 | 10.5 | `ch10-monostable-budget` | 单稳态 1.1RC 的误差预算 | 1 |
| 51 | 10 | 10.5 | `ch10-recovery-gap` | 单稳态恢复时间与连发触发 | 1 |
| 52 | 11 | 11.10 | `ch11-noise-three-taxes` | 三种噪声税与信噪比算例 | 1 |
| 53 | 11 | 11.11 | `ch11-two-stage-margin` | 两级放大器四项指标的余量对账 | 1 |
| 54 | 11 | 11.3 | `ch11-mirror-three-errors` | 电流镜的三笔误差 | 1 |
| 55 | 11 | 11.5 | `ch11-miller-bandwidth` | 米勒电容把带宽压到 15.8kHz | 1 |
| 56 | 11 | 11.5 | `ch11-phase-margin-table` | 相位裕度与阻尼比过冲的换算 | 1 |
| 57 | 11 | 11.7 | `ch11-diffpair-four-beats` | 差分对的四拍：尾电流只准重新分配 | 1 |
| 58 | 12 | 12.10 | `ch12-tia-three-way` | TIA 的增益带宽稳定三角 | 1 |
| 59 | 12 | 12.12 | `ch12-switch-cap` | 开关电容的等效电阻 | 1 |
| 60 | 12 | 12.12 | `ch12-switched-cap-equivalent` | 开关电容等效电阻的来历与代价 | 1 |
| 61 | 12 | 12.13 | `ch12-input-stage-source-z` | 按源阻抗选运放输入级 | 1 |
| 62 | 12 | 12.13 | `ch12-input-types` | 按源阻抗选输入级 | 1 |
| 63 | 12 | 12.9 | `ch12-riso-feedback-point` | 隔离电阻的反馈取点与相位裕度 | 1 |
| 64 | 13 | 13.10 | `ch13-crystal-neg-resistance` | 晶振起振的负阻裕度 | 1 |
| 65 | 13 | 13.11 | `ch13-opto-ctr` | 隔离三条路线与 CTR | 1 |
| 66 | 13 | 13.5.1 | `ch13-compliance-ceiling` | 恒流源的合规电压天花板 | 1 |
| 67 | 13 | 13.6 | `ch13-sampling-quantization` | 采样率与量化台阶的两道账 | 1 |
| 68 | 13 | 13.7 | `ch13-h-bridge-states` | H 桥四拍 | 1 |
| 69 | 13 | 13.8 | `ch13-current-sense-budget` | 10mΩ 分流电阻的两笔账 | 1 |
| 70 | 13 | 13.8 | `ch13-current-sense-sides` | 低侧与高侧电流检测 | 1 |
| 71 | 13 | 13.9 | `ch13-audio-class-heat` | B 类与 D 类推同一只喇叭的热账 | 1 |
| 72 | 14 | 14.10 | `ch14-tolerance-three` | WC、RSS 与 3σ | 1 |
| 73 | 14 | 14.12 | `ch14-pt100-error-budget` | PT100 的误差预算与比率测量 | 1 |
| 74 | 14 | 14.2 | `ch14-arrhenius-ten-degree` | 结温与失效率 | 1 |
| 75 | 14 | 14.2 | `ch14-derating-margin` | 常用降额线 | 1 |
| 76 | 14 | 14.5 | `ch14-thermal-budget` | LDO 的热阻预算 | 1 |
| 77 | 14 | 14.6 | `ch14-ltspice-five` | LTspice 五种分析 | 1 |
| 78 | 14 | 14.8 | `ch14-dft-testpoints` | 测试点与量产测试 | 1 |
| 79 | 15 | 15.1 | `ch15-adc-straddle` | ADC 骑跨分区线 | 1 |
| 80 | 15 | 15.1 | `ch15-crystal-three-no` | 晶振布局三不 | 1 |
| 81 | 15 | 15.1 | `ch15-four-zones` | 四区分团的三条约定 | 1 |
| 82 | 15 | 15.1 | `ch15-layout-ten-questions` | 布局十问 | 1 |
| 83 | 15 | 15.1 | `ch15-trace-drop` | 电源走线的压降账 | 1 |
| 84 | 15 | 15.3 | `ch15-crosstalk-3w` | 串扰三招与包地边界 | 1 |
| 85 | 15 | 15.3 | `ch15-via-parallel` | 过孔并联与电感 | 1 |
| 86 | 15 | 15.4 | `ch15-dfm-limits` | DFM 四个数 | 1 |
| 87 | 15 | 15.4 | `ch15-panelization` | V-cut 与邮票孔 | 1 |
| 88 | 15 | 15.4 | `ch15-testpoint-rules` | 测试点三条规矩 | 1 |
| 89 | 15 | 15.4 | `ch15-thermal-relief` | 热焊盘的两难 | 1 |
| 90 | 15 | 15.5 | `ch15-failure-signatures` | 翻车案例分诊 | 1 |
| 91 | 15 | 15.6 | `ch15-radiated-loop-area` | 回路面积决定辐射等级 | 1 |
| 92 | 15 | 15.7 | `ch15-ground-grid` | 双层板地网 | 1 |
| 93 | 15 | 15.7 | `ch15-return-review` | 回流审查五步 | 1 |
| 94 | 16 | 16.1 | `ch16-first-question` | 排故第一问 | 1 |
| 95 | 16 | 16.3 | `ch16-bandwidth-five` | 示波器带宽五倍规则 | 1 |
| 96 | 16 | 16.3 | `ch16-instrument-trust` | 仪器信任链 | 1 |
| 97 | 16 | 16.3 | `ch16-probe-compensation` | 探头补偿三种方波 | 1 |
| 98 | 16 | 16.5 | `ch16-bisect-injection` | 信号注入与二分 | 1 |
| 99 | 16 | 16.5 | `ch16-case-triage` | 三个案例的分诊 | 1 |
| 100 | 16 | 16.8 | `ch16-postmortem-split` | 根因与触发条件 | 1 |
| 101 | 17 | 17.1 | `ch17-esr-sweep` | ESR 参数扫描——纹波爬升 400mV、内部生热、容量蒸发至三成、闭环 | 1 |
| 102 | 17 | 17.1 | `ch17-symptom-four-fields` | 症状四空格操作演示——多少/何时/多常/改了什么，四空填满才许动烙铁 | 1 |
| 103 | 17 | 17.2 | `ch17-virtual-short-probe` | 虚短探针操作演示——量V−、量V+、压差 8mV、判读移交嫌疑 | 1 |
| 104 | 17 | 17.4 | `ch17-subharmonic-edge` | 次谐波振荡失效边界——占空比推过 50%、一宽一窄、f_sw/2 分量、斜坡补偿 | 1 |
| 105 | 18 | 18.1 | `ch18-component-signatures` | 元件失效签名 | 1 |
| 106 | 18 | 18.1 | `ch18-dmm-averaging` | 万用表的平均滤镜 | 1 |
| 107 | 18 | 18.1 | `ch18-fault-record` | 可复用的故障档案字段 | 1 |
| 108 | 18 | 18.1 | `ch18-first-minute` | 60 秒目检 | 1 |
| 109 | 18 | 18.1 | `ch18-four-wire` | 两线法与四线法 | 1 |
| 110 | 18 | 18.1 | `ch18-power-three-touchpoints` | 先量电源的三处触点 | 1 |
| 111 | 18 | 18.1 | `ch18-probe-loading` | 探头电容把拐点拉低 | 1 |
| 112 | 18 | 18.1 | `ch18-reset-clock-enable` | 不启动的三板斧 | 1 |
| 113 | 18 | 18.1 | `ch18-swap-discipline` | 交换法三条纪律 | 1 |
| 114 | 18 | 18.1 | `ch18-temp-spray` | 温度手段与安全边界 | 1 |
| 115 | 18 | 18.2 | `ch18-ground-lead-inductance` | 探头地线的假振铃 | 1 |
| 116 | 18 | 18.2 | `ch18-measurement-snr` | 源头放大锁住信噪比 | 1 |
| 117 | 18 | 18.2 | `ch18-predict-before-probe` | 下探头前先预测 | 1 |
| 118 | 18 | 18.3 | `ch18-assumption-tree` | 假设树与互斥分支 | 1 |
| 119 | 18 | 18.3 | `ch18-two-way-validation` | 正向、反向与边界验证 | 1 |

## 分布

| 章 | 张数 |
|---:|---:|
| 0 | 4 |
| 1 | 5 |
| 2 | 8 |
| 3 | 6 |
| 4 | 4 |
| 5 | 4 |
| 6 | 3 |
| 7 | 3 |
| 8 | 4 |
| 9 | 4 |
| 10 | 6 |
| 11 | 6 |
| 12 | 6 |
| 13 | 8 |
| 14 | 7 |
| 15 | 15 |
| 16 | 7 |
| 17 | 4 |
| 18 | 15 |
| **合计** | **119** |


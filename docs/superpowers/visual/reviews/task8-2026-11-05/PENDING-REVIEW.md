# 待审图清单（119 张 generated）

本页索引 119 张 `status: generated` 的手绘候选，但**它们并不是同一种状态**：

| 子集 | 张数 | 是否已在正文里 |
|---|---:|---|
| `kind: figure`（figures-v2） | 107 | **未插入**。`content.py:_asset_path` 要求 `accepted`/`published`，否则抛 `BookError: V2 插图尚未通过审图` |
| `kind: animation`（svg-v2） | 12 | **已插入且读者可见**（`docs/` 里已有 `assets/svg-v2/<id>.svg` 的 `<img>`）。动画不校验状态，只要求 `storyboard` 回退存在——12 张都满足 |

所以待审队列里有两种目的：107 张图的分数决定它**能否进书**；12 张动画的分数只是**补签记录**，
不影响它们此刻是否显示。别把这两件事混在一张表里读。

## 近期修订（会改变已发布字节，审图请以本页下方清单为准）

| 日期 | 资产 | 改了什么 | 证据 |
|---|---|---|---|
| 2026-11-06 | `ch17-symptom-four-fields` | 结论帧原本四行全空：每拍只画当拍一行、且不保留，播完右侧仍是「（待填写）」。改为累积重画前 N 行，未填行才画占位；结论帧四行全留 | 浏览器 `setCurrentTime(9.5)`：修前已填 0 行、占位 4；修后已填 4、占位 0。逐拍实测 0→1→2→3→4 行、占位 4→3→2→1→0。静态回退与分镜同步重建，分镜逐格 0/1/2/3/4 |
| 2026-11-06 | `ch17-esr-sweep` | 结论帧的容量条是空框，「只剩标称三成」没有图形证据；闭环卡底边又被字幕条切掉。改为结论拍保留 30% 填充与标注，画布 620→660 | 浏览器终帧：容量条 1 条填充、卡底 572 < 字幕条 596；静态回退含填充与标注 |
| 2026-11-06 | `ch08-mux-address-glitch-v2` | 结论帧的地址时间线、通道行与 INH 脉冲全空，只剩坐标轴与对策卡；对策卡还压在字幕条下。改为结论拍重画 011→111→100 + 通道 7 标记 + INH 脉冲，画布 620→660；并把 `011` 的说明从被 `111` 框压住的位置移到框下方 | 浏览器终帧文字含 011/111/100/通道7/INH；截图无裁切；静态回退含 `M120,440` 脉冲 |
| 2026-11-06 | `ch17-virtual-short-probe` | 万用表两行读数原本常驻「-」，各拍只覆盖自己那行；结论拍两行都退回 `-`，屏幕上看不到任何读数。改为读数逐拍累积（未测写「—」），结论拍保留 2.500V / 2.508V / 压差 8mV | 静态回退含三项且不含「读数：—」；浏览器终帧截图三处数值俱在 |
| 2026-11-06 | `ch08-transfer-gate-v2` | R_ON 曲线只在「互补并联」拍画过，结论拍只剩空坐标轴；且底部说明卡 y=548–596 压在字幕条 556–590 底下（文字被盖）。改为结论拍保留并联包络，画布 620→660、卡片上移到 544–592 | 浏览器终帧：包络 path 命中 True，卡片整块可见；静态回退含 `M96,410 C180,410 240,380` 与 `20→26.7→20Ω` |
| 2026-11-06 | `ch17-subharmonic-edge` | 「SW 节点波形」窗在最后三拍全空：波形按拍重画、补偿拍与结论拍都不带波形。改为补偿拍保留待修的一宽一窄，结论拍画回规整波形并把旋钮移回 40% | 浏览器实测 7.2s/9.2s 均可见波形 path；静态回退含波形、`40%` 与外框；分镜 5 格全含波形 |
| 2026-11-06 | `ch08-sample-hold-v2` | 波形原本按拍拆成三段、互不保留，「再采样」拍干脆不含波形——播完只剩空坐标轴。改为每拍重画整条已发生波形，结论帧呈现完整一个采样周期（上升→保持→下垂） | 浏览器实测终帧：修前可见波形段 0，修后 1 条完整曲线；静态回退含三段端点 `M110,400` / `L700,180` / `864,220` |

## 已有证据的**实际覆盖范围**

各项检查覆盖到哪些条目并不相同，逐项写明：

| 检查 | 覆盖 | 结论 |
|---|---|---|
| 数字双向溯源（图内数字 ⊆ anchor 原文、alt/prompt 数字 ⊆ 图面数字） | **全部 119 张** | `check_visual_manifest.py` 对每条带 `prompt_file` 的资产都跑 `number_gaps` 与 `visible_number_gaps`，PASS（0 项） |
| 登记齐全 / prompt id 与中英文本 / status_history 与评分区间 | **全部 119 张** | 同上，manifest 闸 PASS |
| 出画布、文字互压、后画矩形盖字 | **107 张 figures-v2**（`audit_visual_geometry.py` 全库 361 张、缺陷 0） | 见下注① |
| 出画布（字框出 viewBox） | 12 张 svg-v2 动画：一次性脚本补测，**全部 0 处** | 该项与显示状态无关；这 12 张已在正文显示，故该结论直接对读者可见面成立 |
| 文字互压 / 后画矩形盖字 | 12 张 svg-v2 动画：**不作缺陷判定** | 这些 SVG 按 `data-beat` 分组做 opacity 动画，不同节拍互斥显示；静态 DOM 度量无法区分，须动态审图 |
| 16K/138mm 最小印刷字号 ≥ 8.5pt 与版面 `bounds` | **107 张 figures-v2**：逐图 `*.audit.json` | 最小值 **8.606 pt**（阈值 8.5），`bounds` 全部 pass；该证据只覆盖 figures-v2 |
| 同上 | 12 张 svg-v2 动画：**无 `*.audit.json`** | 未记录，本包不作该项声明 |

① 该 361 张的统计口径是 `figures-v2`/`figures`/`svg` 三个目录，`svg-v2` 不在其中；
因此 107 张 `figures-v2` 候选的几何检查由这一次全库运行覆盖；12 张 `svg-v2` 动画的出画布另有补测（0 处），互压/遮字则因分节拍互斥无法静态判定。

视觉模型当前不可用，本包**不含任何图像阅读结论**。

## 签核方式（口径以 `scripts/check_visual_manifest.py` 为准）

1. 五项评分，每项必须落在 **4~5**：`教学必要性`、`事实精度`、`构图层级`、`风格一致性`、`印刷可读性`。
2. **动画（本队列 12 张，`kind: animation`）另加两项**：`运动叙事`、`交互节奏`，且七项合计 **≥ 30/35**。
   评这两项需要动态入口（`storyboard` / `reduced_motion` / `preview`），静态 fallback 不足以评。
3. 先把 `review_scores` 写进 manifest 条目，**再**迁移状态。顺序颠倒会被拒：
   `--transition` 只在 `check()` 全过时才写盘，评分缺失时报
   `FAIL <ID>: 评分「构图层级」须在 4..5 内`，文件保持原样。
   ```bash
   python scripts/check_visual_manifest.py --transition <ID> reviewed
   python scripts/check_visual_manifest.py --transition <ID> accepted
   ```
   `status_history` 必须恰好落在 `["planned","generated","reviewed","accepted"]` 上；
   越级或回退会被拒。`--previous <旧 manifest>` 可选，用来额外禁止一次跳多级。
4. `asset_sha256` 必须按**当前 SVG 字节**重算（CRLF→LF 归一），不得沿用旧签核的值。
5. 任何一张重绘后 SHA 变化，签核作废，必须退回 `generated` 并重新逐级迁移。

## 清单

| # | 章 | anchor | id | 类型 | 用途 | 源事实数 |
|---:|---:|---|---|---|---|---:|
| 1 | 0 | 0.2 | `ch00-current-loop-v2` | A1 | 闭合回路中的约定电流与串联压降（Task 8 正文试片，待风格复评） | 1 |
| 2 | 0 | 0.3 | `ch00-divider-derivation-v2` | A2 | 空载分压公式的逐步推导（Task 8 正文试片，待风格复评） | 1 |
| 3 | 0 | 0.3 | `ch00-divider-loading-v2` | A4 | 分压器从空载到带载的塌陷与输出电阻判据 | 1 |
| 4 | 0 | 0.6 | `ch00-source-types-v2` | A1 | 恒压源与恒流源的 V-I 曲线、输出阻抗与接法 | 1 |
| 5 | 1 | 1.1 | `ch01-e24-ladder` | V4 | E24 档位与 3.3k 的来历 | 1 |
| 6 | 1 | 1.4 | `ch01-thevenin-two-load` | V4 | 戴维南等效与两负载法实测内阻 | 1 |
| 7 | 1 | 1.5 | `ch01-q-selectivity-map` | V4 | Q 是挑频率的锐度，不是越高越好 | 1 |
| 8 | 1 | 1.7 | `ch01-derating-product` | V4 | 降容是乘法：三项八折只剩一半 | 1 |
| 9 | 1 | 1.7 | `ch01-electrolytic-life` | V4 | 10°C 翻倍法则下的电解电容寿命账 | 1 |
| 10 | 2 | 2.10 | `ch02-rectifier-voltage-ledger` | V4 | 桥式整流的电压分账与峰值电流 | 1 |
| 11 | 2 | 2.11.3 | `ch02-esd-chain` | V4 | IEC 8kV 的 24A 分账 | 1 |
| 12 | 2 | 2.12 | `ch02-bridge-junction-ledger` | V4 | 桥堆与整流管的四个数与结温账 | 1 |
| 13 | 2 | 2.13 | `ch02-diode-fault-order` | V4 | 二极管排故的三步顺序 | 1 |
| 14 | 2 | 2.8 | `ch02-protection-order` | V4 | 接口保护三件套的先后次序 | 1 |
| 15 | 2 | 2.9 | `ch02-junction-margin` | V4 | 结温余量只剩 3°C | 1 |
| 16 | 2 | 2.9 | `ch02-parallel-hog` | V4 | 并联二极管的热抢流 | 1 |
| 17 | 2 | 2.9 | `ch02-zener-budget` | V4 | 稳压管的限流电阻与最坏功耗 | 1 |
| 18 | 3 | 3.1 | `ch03-early-effect` | V4 | 厄利效应与输出阻抗 | 1 |
| 19 | 3 | 3.2 | `ch03-reverse-beta` | V4 | C/E 反接为什么β只剩个位数 | 1 |
| 20 | 3 | 3.3 | `ch03-config-impedance` | V4 | 三种组态共用一条阻抗折算律 | 1 |
| 21 | 3 | 3.5 | `ch03-low-high-side` | V4 | 低边与高边开关的参考点 | 1 |
| 22 | 3 | 3.5 | `ch03-switch-budget` | V4 | 继电器基极电阻的两笔账 | 1 |
| 23 | 3 | 3.9 | `ch03-ce-swing-budget` | V4 | 共射级的摆幅预算与削波方向 | 1 |
| 24 | 4 | 4.3 | `ch04-dvdt-false-turnon` | V4 | dv/dt 误导通的定量图像 | 1 |
| 25 | 4 | 4.4 | `ch04-deadtime-ledger` | V4 | 死区损耗的明账 | 1 |
| 26 | 4 | 4.4 | `ch04-gate-window` | V4 | 栅极保护的电压窗 | 1 |
| 27 | 4 | 4.5 | `ch04-thermal-chain-ledger` | V4 | 热失效的热阻链与四种测量自欺 | 1 |
| 28 | 5 | 5.2 | `ch05-rp-power` | V4 | 上拉电阻自己的功耗 | 1 |
| 29 | 5 | 5.4 | `ch05-tristate-handover` | V4 | 三态总线的交接时序 | 1 |
| 30 | 5 | 5.6 | `ch05-ab-bias-thermal` | V4 | AB 类偏置的热耦合与散热器两笔账 | 1 |
| 31 | 5 | 5.6 | `ch05-shoot-through-ledger` | V4 | 推挽正常半周与直通的电流功率对账 | 1 |
| 32 | 6 | 6.1 | `ch06-741-four-blocks` | V4 | 741 内部四级的分工与补偿代价 | 1 |
| 33 | 6 | 6.3 | `ch06-bias-balance` | V4 | 输入偏置电流与平衡电阻 | 1 |
| 34 | 6 | 6.7 | `ch06-slew-vs-gbw` | V4 | 压摆率与全功率带宽的两套物理 | 1 |
| 35 | 7 | 7.2 | `ch07-pullup-three-accounts` | V4 | 上拉电阻同时挂在三本账上 | 1 |
| 36 | 7 | 7.2 | `ch07-threshold-budget` | V4 | 阈值精度的误差预算排序 | 1 |
| 37 | 7 | 7.3 | `ch07-hysteresis-window` | V4 | 迟滞窗口与两个阈值 | 1 |
| 38 | 8 | 8.1 | `ch08-transfer-gate-v2` | A1 | 传输门的阈值缺口与互补并联（技术原型，待风格复评） | 1 |
| 39 | 8 | 8.2 | `ch08-mux-address-glitch-v2` | A4 | 4051 地址跳变的路过通道与 INH 对策（技术原型，待风格复评） | 1 |
| 40 | 8 | 8.4 | `ch08-sample-hold-v2` | A1 | 采样保持四拍与一个电容的三笔账（技术原型，待风格复评） | 1 |
| 41 | 8 | 8.6 | `ch08-charge-injection-v2` | A4 | 关断瞬间电荷注入的两路分账（技术原型，待风格复评） | 1 |
| 42 | 9 | 9.1 | `ch09-reference-ladder` | V4 | 基准选型的精度阶梯 | 1 |
| 43 | 9 | 9.2 | `ch09-tl431-divider-floor` | V4 | TL431 分压电阻的下限 | 1 |
| 44 | 9 | 9.3 | `ch09-esr-window` | V4 | LDO 的 ESR 稳定窗口 | 1 |
| 45 | 9 | 9.4 | `ch09-ldo-four-accounts` | V4 | 7805 四种死法对应的四本账 | 1 |
| 46 | 10 | 10.1 | `ch10-555-threshold-clamp` | V4 | 555 的两条门限与占空比 | 1 |
| 47 | 10 | 10.3 | `ch10-555-fault-tree` | V4 | 555 故障图谱五站定位 | 1 |
| 48 | 10 | 10.4 | `ch10-astable-reverse-design` | V4 | 按 38kHz 目标反推 555 元件值 | 1 |
| 49 | 10 | 10.4 | `ch10-duty-fifty-paths` | V4 | 准 50% 占空比的三条路与两个极端 | 1 |
| 50 | 10 | 10.5 | `ch10-monostable-budget` | V4 | 单稳态 1.1RC 的误差预算 | 1 |
| 51 | 10 | 10.5 | `ch10-recovery-gap` | V4 | 单稳态恢复时间与连发触发 | 1 |
| 52 | 11 | 11.10 | `ch11-noise-three-taxes` | V4 | 三种噪声税与信噪比算例 | 1 |
| 53 | 11 | 11.11 | `ch11-two-stage-margin` | V4 | 两级放大器四项指标的余量对账 | 1 |
| 54 | 11 | 11.3 | `ch11-mirror-three-errors` | V4 | 电流镜的三笔误差 | 1 |
| 55 | 11 | 11.5 | `ch11-miller-bandwidth` | V4 | 米勒电容把带宽压到 15.8kHz | 1 |
| 56 | 11 | 11.5 | `ch11-phase-margin-table` | V4 | 相位裕度与阻尼比过冲的换算 | 1 |
| 57 | 11 | 11.7 | `ch11-diffpair-four-beats` | V4 | 差分对的四拍：尾电流只准重新分配 | 1 |
| 58 | 12 | 12.10 | `ch12-tia-three-way` | V4 | TIA 的增益带宽稳定三角 | 1 |
| 59 | 12 | 12.12 | `ch12-switch-cap` | V4 | 开关电容的等效电阻 | 1 |
| 60 | 12 | 12.12 | `ch12-switched-cap-equivalent` | V4 | 开关电容等效电阻的来历与代价 | 1 |
| 61 | 12 | 12.13 | `ch12-input-stage-source-z` | V4 | 按源阻抗选运放输入级 | 1 |
| 62 | 12 | 12.13 | `ch12-input-types` | V4 | 按源阻抗选输入级 | 1 |
| 63 | 12 | 12.9 | `ch12-riso-feedback-point` | V4 | 隔离电阻的反馈取点与相位裕度 | 1 |
| 64 | 13 | 13.10 | `ch13-crystal-neg-resistance` | V4 | 晶振起振的负阻裕度 | 1 |
| 65 | 13 | 13.11 | `ch13-opto-ctr` | V4 | 隔离三条路线与 CTR | 1 |
| 66 | 13 | 13.5.1 | `ch13-compliance-ceiling` | V4 | 恒流源的合规电压天花板 | 1 |
| 67 | 13 | 13.6 | `ch13-sampling-quantization` | V4 | 采样率与量化台阶的两道账 | 1 |
| 68 | 13 | 13.7 | `ch13-h-bridge-states` | V4 | H 桥四拍 | 1 |
| 69 | 13 | 13.8 | `ch13-current-sense-budget` | V4 | 10mΩ 分流电阻的两笔账 | 1 |
| 70 | 13 | 13.8 | `ch13-current-sense-sides` | V4 | 低侧与高侧电流检测 | 1 |
| 71 | 13 | 13.9 | `ch13-audio-class-heat` | V4 | B 类与 D 类推同一只喇叭的热账 | 1 |
| 72 | 14 | 14.10 | `ch14-tolerance-three` | V4 | WC、RSS 与 3σ | 1 |
| 73 | 14 | 14.12 | `ch14-pt100-error-budget` | V4 | PT100 的误差预算与比率测量 | 1 |
| 74 | 14 | 14.2 | `ch14-arrhenius-ten-degree` | V4 | 结温与失效率 | 1 |
| 75 | 14 | 14.2 | `ch14-derating-margin` | V4 | 常用降额线 | 1 |
| 76 | 14 | 14.5 | `ch14-thermal-budget` | V3 | LDO 的热阻预算 | 1 |
| 77 | 14 | 14.6 | `ch14-ltspice-five` | V5 | LTspice 五种分析 | 1 |
| 78 | 14 | 14.8 | `ch14-dft-testpoints` | V4 | 测试点与量产测试 | 1 |
| 79 | 15 | 15.1 | `ch15-adc-straddle` | V4 | ADC 骑跨分区线 | 1 |
| 80 | 15 | 15.1 | `ch15-crystal-three-no` | V4 | 晶振布局三不 | 1 |
| 81 | 15 | 15.1 | `ch15-four-zones` | V4 | 四区分团的三条约定 | 1 |
| 82 | 15 | 15.1 | `ch15-layout-ten-questions` | V4 | 布局十问 | 1 |
| 83 | 15 | 15.1 | `ch15-trace-drop` | V4 | 电源走线的压降账 | 1 |
| 84 | 15 | 15.3 | `ch15-crosstalk-3w` | V4 | 串扰三招与包地边界 | 1 |
| 85 | 15 | 15.3 | `ch15-via-parallel` | V3 | 过孔并联与电感 | 1 |
| 86 | 15 | 15.4 | `ch15-dfm-limits` | V4 | DFM 四个数 | 1 |
| 87 | 15 | 15.4 | `ch15-panelization` | V4 | V-cut 与邮票孔 | 1 |
| 88 | 15 | 15.4 | `ch15-testpoint-rules` | V5 | 测试点三条规矩 | 1 |
| 89 | 15 | 15.4 | `ch15-thermal-relief` | V4 | 热焊盘的两难 | 1 |
| 90 | 15 | 15.5 | `ch15-failure-signatures` | V5 | 翻车案例分诊 | 1 |
| 91 | 15 | 15.6 | `ch15-radiated-loop-area` | V4 | 回路面积决定辐射等级 | 1 |
| 92 | 15 | 15.7 | `ch15-ground-grid` | V4 | 双层板地网 | 1 |
| 93 | 15 | 15.7 | `ch15-return-review` | V4 | 回流审查五步 | 1 |
| 94 | 16 | 16.1 | `ch16-first-question` | V4 | 排故第一问 | 1 |
| 95 | 16 | 16.3 | `ch16-bandwidth-five` | V4 | 示波器带宽五倍规则 | 1 |
| 96 | 16 | 16.3 | `ch16-instrument-trust` | V4 | 仪器信任链 | 1 |
| 97 | 16 | 16.3 | `ch16-probe-compensation` | V4 | 探头补偿三种方波 | 1 |
| 98 | 16 | 16.5 | `ch16-bisect-injection` | V3 | 信号注入与二分 | 1 |
| 99 | 16 | 16.5 | `ch16-case-triage` | V4 | 三个案例的分诊 | 1 |
| 100 | 16 | 16.8 | `ch16-postmortem-split` | V4 | 根因与触发条件 | 1 |
| 101 | 17 | 17.1 | `ch17-esr-sweep` | A3 | ESR 参数扫描——纹波爬升 400mV、内部生热、容量蒸发至三成、闭环 | 1 |
| 102 | 17 | 17.1 | `ch17-symptom-four-fields` | A5 | 症状四空格操作演示——多少/何时/多常/改了什么，四空填满才许动烙铁 | 1 |
| 103 | 17 | 17.2 | `ch17-virtual-short-probe` | A5 | 虚短探针操作演示——量V−、量V+、压差 8mV、判读移交嫌疑 | 1 |
| 104 | 17 | 17.4 | `ch17-subharmonic-edge` | A4 | 次谐波振荡失效边界——占空比推过 50%、一宽一窄、f_sw/2 分量、斜坡补偿 | 1 |
| 105 | 18 | 18.1 | `ch18-component-signatures` | V4 | 元件失效签名 | 1 |
| 106 | 18 | 18.1 | `ch18-dmm-averaging` | V4 | 万用表的平均滤镜 | 1 |
| 107 | 18 | 18.1 | `ch18-fault-record` | V4 | 可复用的故障档案字段 | 1 |
| 108 | 18 | 18.1 | `ch18-first-minute` | V4 | 60 秒目检 | 1 |
| 109 | 18 | 18.1 | `ch18-four-wire` | V4 | 两线法与四线法 | 1 |
| 110 | 18 | 18.1 | `ch18-power-three-touchpoints` | V4 | 先量电源的三处触点 | 1 |
| 111 | 18 | 18.1 | `ch18-probe-loading` | V4 | 探头电容把拐点拉低 | 1 |
| 112 | 18 | 18.1 | `ch18-reset-clock-enable` | V5 | 不启动的三板斧 | 1 |
| 113 | 18 | 18.1 | `ch18-swap-discipline` | V4 | 交换法三条纪律 | 1 |
| 114 | 18 | 18.1 | `ch18-temp-spray` | V4 | 温度手段与安全边界 | 1 |
| 115 | 18 | 18.2 | `ch18-ground-lead-inductance` | V4 | 探头地线的假振铃 | 1 |
| 116 | 18 | 18.2 | `ch18-measurement-snr` | V4 | 源头放大锁住信噪比 | 1 |
| 117 | 18 | 18.2 | `ch18-predict-before-probe` | V4 | 下探头前先预测 | 1 |
| 118 | 18 | 18.3 | `ch18-assumption-tree` | V4 | 假设树与互斥分支 | 1 |
| 119 | 18 | 18.3 | `ch18-two-way-validation` | V4 | 正向、反向与边界验证 | 1 |

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

| 类型 | 张数 | 说明 |
|---|---:|---|
| V4 | 100 | 静态手绘主图 |
| V5 | 4 | 流程／决策图 |
| V3 | 3 | 定量曲线图 |
| A1–A5 | 12 | 动画（需动态入口才能评「运动叙事／交互节奏」） |
| **合计** | **119** | 其中 figures-v2 107 张、svg-v2 12 张 |


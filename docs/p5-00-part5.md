# 第五篇：动画演示中心 🎬

> 全部 103 张 SVG 动画（SMIL，浏览器直接播放）位于 `assets/svg/` 目录，由 `scripts/generate_svgs.py` 一键生成（仓库铁律：两者始终同步）；配套 Falstad 在线电路可实时交互。

<details>
<summary>🗺️ 动画速查：按章节 —— 103 张全索引（点击展开）</summary>

| 章 | 动画（点击直达） |
|---|---|
| §0 第 0 章 电路直觉学前班：先上车，再赶路 🍼 | [5.39](p5-00-part5.md#demo39) · [5.78](p5-00-part5.md#demo78) · [5.87](p5-00-part5.md#demo87) · [5.89](p5-00-part5.md#demo89) |
| §1 第 1 章 无源元件的真实面目 | [5.36](p5-00-part5.md#demo36) · [5.43](p5-00-part5.md#demo43) · [5.60](p5-00-part5.md#demo60) · [5.79](p5-00-part5.md#demo79) · [5.101](p5-00-part5.md#demo101) · [5.103](p5-00-part5.md#demo103) |
| §2 第 2 章 二极管：单向导电的物理本质 | [5.2](p5-00-part5.md#demo2) · [5.31](p5-00-part5.md#demo31) · [5.46](p5-00-part5.md#demo46) · [5.56](p5-00-part5.md#demo56) · [5.61](p5-00-part5.md#demo61) · [5.83](p5-00-part5.md#demo83) |
| §3 第 3 章 BJT 三极管：完整概念体系 | [5.3](p5-00-part5.md#demo3) · [5.40](p5-00-part5.md#demo40) · [5.41](p5-00-part5.md#demo41) · [5.66](p5-00-part5.md#demo66) · [5.67](p5-00-part5.md#demo67) · [5.70](p5-00-part5.md#demo70) · [5.74](p5-00-part5.md#demo74) · [5.81](p5-00-part5.md#demo81) |
| §4 第 4 章 MOSFET：电压控制的开关王者 | [5.44](p5-00-part5.md#demo44) · [5.57](p5-00-part5.md#demo57) · [5.68](p5-00-part5.md#demo68) · [5.82](p5-00-part5.md#demo82) · [5.92](p5-00-part5.md#demo92) |
| §5 第 5 章 输出结构彻底讲透：推挽、开漏、上拉下拉 | [5.5](p5-00-part5.md#demo5) · [5.51](p5-00-part5.md#demo51) · [5.53](p5-00-part5.md#demo53) · [5.62](p5-00-part5.md#demo62) |
| §6 第 6 章 运算放大器：从内部结构到参数字典 | [5.37](p5-00-part5.md#demo37) · [5.45](p5-00-part5.md#demo45) · [5.63](p5-00-part5.md#demo63) · [5.71](p5-00-part5.md#demo71) · [5.72](p5-00-part5.md#demo72) · [5.75](p5-00-part5.md#demo75) · [5.93](p5-00-part5.md#demo93) |
| §7 第 7 章 比较器：专为"判决"而生 | [5.4](p5-00-part5.md#demo4) · [5.35](p5-00-part5.md#demo35) · [5.47](p5-00-part5.md#demo47) · [5.54](p5-00-part5.md#demo54) · [5.76](p5-00-part5.md#demo76) |
| §8 第 8 章 模拟开关与多路复用器：CMOS 传输门 | [5.22](p5-00-part5.md#demo22) · [5.50](p5-00-part5.md#demo50) · [5.69](p5-00-part5.md#demo69) · [5.84](p5-00-part5.md#demo84) · [5.94](p5-00-part5.md#demo94) |
| §9 第 9 章 电压基准与稳压器：系统的"定盘星" | [5.20](p5-00-part5.md#demo20) · [5.21](p5-00-part5.md#demo21) · [5.25](p5-00-part5.md#demo25) · [5.55](p5-00-part5.md#demo55) · [5.73](p5-00-part5.md#demo73) · [5.85](p5-00-part5.md#demo85) · [5.95](p5-00-part5.md#demo95) |
| §10 第 10 章 555 定时器：最经典的混合信号芯片 | [5.1](p5-00-part5.md#demo1) · [5.6](p5-00-part5.md#demo6) · [5.30](p5-00-part5.md#demo30) · [5.58](p5-00-part5.md#demo58) · [5.77](p5-00-part5.md#demo77) · [5.86](p5-00-part5.md#demo86) |
| §11 第 11 章 放大电路拓扑：三种组态与四大积木 | [5.8](p5-00-part5.md#demo8) · [5.9](p5-00-part5.md#demo9) · [5.13](p5-00-part5.md#demo13) · [5.16](p5-00-part5.md#demo16) · [5.48](p5-00-part5.md#demo48) · [5.64](p5-00-part5.md#demo64) |
| §12 第 12 章 运放应用电路族：两条公理推演一切 | [5.10](p5-00-part5.md#demo10) · [5.15](p5-00-part5.md#demo15) · [5.17](p5-00-part5.md#demo17) · [5.24](p5-00-part5.md#demo24) · [5.27](p5-00-part5.md#demo27) · [5.32](p5-00-part5.md#demo32) · [5.33](p5-00-part5.md#demo33) · [5.34](p5-00-part5.md#demo34) · [5.52](p5-00-part5.md#demo52) · [5.59](p5-00-part5.md#demo59) |
| §13 第 13 章 电源与信号产生电路 | [5.11](p5-00-part5.md#demo11) · [5.12](p5-00-part5.md#demo12) · [5.14](p5-00-part5.md#demo14) · [5.18](p5-00-part5.md#demo18) · [5.19](p5-00-part5.md#demo19) · [5.23](p5-00-part5.md#demo23) · [5.26](p5-00-part5.md#demo26) · [5.28](p5-00-part5.md#demo28) · [5.29](p5-00-part5.md#demo29) · [5.65](p5-00-part5.md#demo65) · [5.80](p5-00-part5.md#demo80) |
| §14 第 14 章 电路设计方法论 | [5.42](p5-00-part5.md#demo42) · [5.88](p5-00-part5.md#demo88) · [5.98](p5-00-part5.md#demo98) |
| §15 第 15 章 PCB 绘制注意事项 | [5.7](p5-00-part5.md#demo7) · [5.90](p5-00-part5.md#demo90) · [5.96](p5-00-part5.md#demo96) · [5.100](p5-00-part5.md#demo100) |
| §16 第 16 章 排故五步法 | [5.38](p5-00-part5.md#demo38) · [5.49](p5-00-part5.md#demo49) · [5.99](p5-00-part5.md#demo99) |
| §17 第 17 章 故障模式速查总表 | [5.91](p5-00-part5.md#demo91) · [5.102](p5-00-part5.md#demo102) |
| §18 第 18 章 大师的排故智慧 | [5.97](p5-00-part5.md#demo97) |

</details>
## 5.1 RC 充电 <a id="demo1"></a>

<p align="center"><img src="assets/svg/rc-charge.svg" width="720" alt="RC 充电动画：水桶与细水管"></p>




**看点**：电流箭头随充电逐渐变慢（alpha 衰减）——$i_C=(V_S-v_C)/R$ 随电容电压升高而减小，这正是指数曲线的成因。τ 时刻恰好充到 63.2%。

🔗 Falstad 交互：`Circuits → Basics → RC Circuit`

## 5.2 桥式整流与滤波 <a id="demo2"></a>

<p align="center"><img src="assets/svg/bridge-rectifier.svg" width="720" alt="桥式整流滤波SVG动画"></p>

**看点**：负半周被"翻转"上来；滤波电容在峰值充电（跟随橙色）、谷值放电（绿色自由衰减）——纹波大小正比于负载电流、反比于电容。

🔗 Falstad 交互：`Circuits → Diodes → Full-Wave Rectifier`

## 5.3 共射放大器失真 <a id="demo3"></a>

<p align="center"><img src="assets/svg/bjt-amplify.svg" width="720" alt="共射放大器SVG动画"></p>

**看点**：绿线 Q 点居中，波形完好；红线摆幅过大，顶部被截止区"削平"、底部撞饱和压降。**静态工作点是放大器的第一设计。**

🔗 Falstad 交互：`Circuits → Transistors → Common-Emitter Amp`

## 5.4 比较器迟滞 <a id="demo4"></a>

<p align="center"><img src="assets/svg/comparator-hysteresis.svg" width="720" alt="比较器迟滞SVG动画"></p>

**看点**：同一路带噪信号——红色无迟滞输出在阈值附近疯狂抖动；绿色施密特输出干净利落。**正反馈不是振荡的代名词，用得对就是抗噪利器。**

🔗 Falstad 交互：`Circuits → Op-Amps → Comparator → Hysteresis`

## 5.5 推挽 vs 开漏 <a id="demo5"></a>

<p align="center"><img src="assets/svg/pushpull-opendrain.svg" width="720" alt="推挽开漏SVG动画"></p>

**看点**：推挽上升沿陡峭（上管主动驱动）；开漏上升沿是 RC 充电曲线（上拉电阻对总线电容充电）——这就是 I2C 高速模式要减小上拉电阻的原因。

## 5.6 555 无稳态振荡 <a id="demo6"></a>

<p align="center"><img src="assets/svg/ne555-astable.svg" width="720" alt="555无稳态SVG动画"></p>

**看点**：电容电压（青色）在 1/3 与 2/3 Vcc 两条紫色阈值线之间荡秋千；输出（绿色）同步翻转。充电经 R1+R2、放电只经 R2 → 占空比永远 >50%。

🔗 Falstad 交互：`Circuits → 555 Timer Chip → Astable Multivibrator`

## 5.7 PCB 回流路径 <a id="demo7"></a>

<p align="center"><img src="assets/svg/pcb-return-path.svg" width="720" alt="回流路径SVG动画"></p>

**看点**：红色信号粒子向前、绿色回流粒子紧贴其正下方反向回家（环路面积≈0）；地平面开槽后，紫色回流被迫绕到槽底走大圈，阴影区域就是 EMI 天线。


## 5.8 差分对：差模放大、共模抑制 <a id="demo8"></a>

<p align="center"><img src="assets/svg/diff-pair.svg" width="720" alt="差分对SVG动画"></p>

**看点**：幕 1 差模——绿粒子左管多吃、灰粒子右管挨饿，两集电极一升一降拉开输出；幕 2 共模——蓝粒子两边同涨，尾电流源"总量钉死"，谁也多吃不了。底部红绿分配条就是 CMRR 的物理图像。→ 正文 [第 11 章](p2-00-part2.md#ch11)

## 5.9 乙类推挽与交越失真 <a id="demo9"></a>

<p align="center"><img src="assets/svg/class-b-crossover.svg" width="720" alt="乙类推挽SVG动画"></p>

**看点**：正半周绿粒子 NPN 推、负半周红粒子 PNP 拉——交接区 ±0.7V 两管全关，输出波形过零处摔出一个豁口。甲乙类偏置就是给两管"预热身"。→ 正文 [11.4 推挽输出级](p2-00-part2.md#ch11)

## 5.10 Sallen-Key 二阶低通 <a id="demo10"></a>

<p align="center"><img src="assets/svg/sallen-key.svg" width="720" alt="Sallen-Key SVG动画"></p>

**看点**：绿线 Q=0.707 最平坦，红虚线 Q=3 在 fc 处鼓包——同一张电路，Q 值决定"平"还是"峰"。C1 顶帽正反馈是峰化的来源，Q 再大就变振荡器。→ 正文 [12.5 有源滤波](p2-01-ch11.md#ch12)

## 5.11 Buck 降压：伏秒平衡 <a id="demo11"></a>

<p align="center"><img src="assets/svg/buck-converter.svg" width="720" alt="Buck 降压SVG动画"></p>

**看点**：开关闭合绿粒子灌能、断开红粒子经二极管续流；开关节点方波被电感惯性碾成三角电流、再被电容碾成直流。占空比 42% × 12V = 5V，一个字：伏秒平衡。→ 正文 [13.2 Buck](p2-02-ch12.md#ch13)

## 5.12 文氏桥振荡器：起振与稳幅 <a id="demo12"></a>

<p align="center"><img src="assets/svg/wien-bridge.svg" width="720" alt="文氏桥SVG动画"></p>

**看点**：右侧波形从噪声种子指数长大、到包络线封顶——f₀ 处 RC 网络相移 0°、衰减 1/3，增益=3 恰好补平；幅度停在哪儿？灯泡发热升阻把增益自动摁回 3。→ 正文 [13.4 文氏桥](p2-02-ch12.md#ch13)

## 5.13 电流镜：共用 V_BE 的复印机 <a id="demo13"></a>

<p align="center"><img src="assets/svg/current-mirror.svg" width="720" alt="电流镜SVG动画"></p>

**看点**：绿粒子经 R_SET 流入二极管接法的 Q1，自动建立 V_BE；幕 2 蓝粒子从负载侧流入 Q2——同一根基极线把 V_BE 一送二，电流被原样复印。→ 正文 [11.3 电流镜](p2-00-part2.md#ch11)

## 5.14 Boost 升压：电感叠罗汉 <a id="demo14"></a>

<p align="center"><img src="assets/svg/boost-converter.svg" width="720" alt="Boost升压SVG动画"></p>

**看点**：开关闭合绿粒子给电感"打气"（输出靠电容撑）；断开瞬间电感极性翻转与 12V 串联叠加，红粒子顶开二极管直灌 24V。伏秒平衡：Vout=Vin/(1−D)。→ 正文 [13.3 Boost](p2-02-ch12.md#ch13)

## 5.15 精密整流：借增益消灭 0.7V <a id="demo15"></a>

<p align="center"><img src="assets/svg/precision-rectifier.svg" width="720" alt="精密整流SVG动画"></p>

**看点**：±100mV 小信号，普通二极管整流输出一条死线；运放把二极管塞进反馈环，等效死区 0.7V÷10万=7µV——输出半波分毫毕现。→ 正文 [12.6 精密整流](p2-01-ch11.md#ch12)

## 5.16 米勒效应：10pF 变身 1nF <a id="demo16"></a>

<p align="center"><img src="assets/svg/miller-effect.svg" width="720" alt="米勒效应SVG动画"></p>

**看点**：IN 只摆 1mV、OUT 反相摆 100mV——跨接电容两端实际承受 101 倍摆幅，输入源仿佛对着 1nF 充电。高频滚降的元凶，也是密勒补偿的原理。→ 正文 [11.5 频率响应](p2-00-part2.md#ch11)

## 5.17 仪表放大器：三道防线挡共模 <a id="demo17"></a>

<p align="center"><img src="assets/svg/instrumentation-amp.svg" width="720" alt="仪表放大器SVG动画"></p>

**看点**：差模时 R_G 有电流（红粒子下流）、v1/v2 反向拉大；共模时 R_G 两端同升同降、无电流、前级增益=1——共模在源头就被"放生"，再被减法器剪掉。→ 正文 [12.3 节三运放仪放](p2-01-ch11.md#ch12)

## 5.18 LC 谐振：电场磁场荡秋千 <a id="demo18"></a>

<p align="center"><img src="assets/svg/rlc-resonance.svg" width="720" alt="LC谐振SVG动画"></p>

**看点**：底部两条能量条此消彼长——磁场能 ½LI² 与电场能 ½CV² 每秒倒腾 2f₀ 次；右侧 Q 高峰尖 vs Q 低峰胖，f₀ 处感抗容抗正负抵消电流冲顶。→ 正文 [13.4 的延伸阅读段](p2-02-ch12.md#ch13)

## 5.19 SAR ADC：四位天平 <a id="demo19"></a>

<p align="center"><img src="assets/svg/sar-adc.svg" width="720" alt="SAR ADC SVG动画"></p>

**看点**：紫阶梯四拍逼近蓝输入线——试 8 太沉退、试 4 太轻留、试 6 太沉退、试 5 留下：0101。二分查找的硬件版，N 位只要 N 拍。→ 正文 [13.6 ADC](p2-02-ch12.md#ch13)

## 5.20 带隙基准：一正一负凑直线 <a id="demo20"></a>

<p align="center"><img src="assets/svg/bandgap.svg" width="720" alt="带隙基准SVG动画"></p>

**看点**：红线 V_BE 下坡、绿线 K·ΔV_BE 上坡——给绿线配好权重，两斜率恰好抵消，蓝线 1.25V 全温区纹丝不动。基准芯片的全部物理就这三条线。→ 正文 [9.1 带隙基准](p1-09-ch8.md#ch9)

## 5.21 TL431：自带标尺的比较器 <a id="demo21"></a>

<p align="center"><img src="assets/svg/tl431.svg" width="720" alt="TL431 SVG动画"></p>

**看点**：REF 高过 2.5V 一瞬，红粒子从阴极猛灌——"会变身"的全貌：内部带隙当标尺、运放当裁判、NPN 当执行。分压采样一接，Vout=2.5×(1+R1/R2)。→ 正文 [9.2 TL431](p1-09-ch8.md#ch9)

## 5.22 采样保持：给 SAR 按下暂停键 <a id="demo22"></a>

<p align="center"><img src="assets/svg/sample-hold.svg" width="720" alt="采样保持SVG动画"></p>

**看点**：绿粒子充电追踪（采样相）→ 开关断开电容记住（保持相）；阶梯波形微微下垂——那就是 droop，漏电正在偷走你记住的电压。→ 正文 [8.4 采样保持](p1-08-ch7.md#ch8)

## 5.23 电荷泵：电容斗提机 <a id="demo23"></a>

<p align="center"><img src="assets/svg/charge-pump.svg" width="720" alt="电荷泵SVG动画"></p>

**看点**：相1 绿粒子灌满 C1（下端接地），相2 下端被抬到 Vin、上端 2Vin 红粒子倒进 C2 水库——几轮之后输出爬满 2Vin。不用电感的升压。→ 正文 [13.3 电荷泵](p2-02-ch12.md#ch13)

## 5.24 一阶 RC 低通与波特图 <a id="demo24"></a>

<p align="center"><img src="assets/svg/rc-lowpass.svg" width="720" alt="RC低通SVG动画"></p>

**看点**：fc 竖线恰好穿过 −3dB 交点；高频正弦进、缩小且滞后的绿波出——一颗极点的全部人生：−20dB/dec 与最多 −90°。→ 正文 [12.5 有源滤波](p2-01-ch11.md#ch12)

## 5.25 齐纳稳压：电压溢流阀 <a id="demo25"></a>

<p align="center"><img src="assets/svg/zener-regulator.svg" width="720" alt="齐纳稳压SVG动画"></p>

**看点**：输入正弦抖、输出一根直线——水位到顶开闸，多余的压降全落在 Rs 上。负载抢流？齐纳少吸让位。→ 正文 [9.1 齐纳](p1-09-ch8.md#ch9)

## 5.26 恒流源：电压横扫，电流平躺 <a id="demo26"></a>

<p align="center"><img src="assets/svg/constant-current.svg" width="720" alt="恒流源SVG动画"></p>

**看点**：V_CE 扫过全程，I 线纹丝平躺——斜率≈0 就是"输出阻抗极高"的图形化。基准钉 V_B、R_E 钉电流、管子吸收全部波动。→ 正文 [13.5 恒流源](p2-02-ch12.md#ch13)

## 5.27 峰值检测：单向记忆 <a id="demo27"></a>

<p align="center"><img src="assets/svg/peak-detector.svg" width="720" alt="峰值检测SVG动画"></p>

**看点**：灰波创新高，绿线立刻跳上跟住；灰波回落，绿线平台守住——泄放电阻让它缓缓遗忘。只许上不许下，这就是峰值表和 AGC 的心脏。→ 正文 [12.6 峰值检测](p2-01-ch11.md#ch12)

## 5.28 反相 Buck-Boost：正进负出 <a id="demo28"></a>

<p align="center"><img src="assets/svg/inverting-buckboost.svg" width="720" alt="反相Buck-Boost SVG动画"></p>

**看点**：闭合时电感从 +12V 储能（绿粒子下灌），断开瞬间电感把节点拽向负压、经朝左二极管倒向负输出（红粒子）——输出电容下极板才是地。→ 正文 [13.3 Buck-Boost](p2-02-ch12.md#ch13)

## 5.29 H 桥：电流听指挥掉头 <a id="demo29"></a>

<p align="center"><img src="assets/svg/h-bridge.svg" width="720" alt="H桥SVG动画"></p>

**看点**：绿粒子沿 +12V→Q1→电机→Q4→GND 对角线走；红帧整体掉头；警示帧同臂直通；紫帧电感电流经体二极管流回电源（D3 出 +12V、D2 进地，方向分毫不差）。→ 正文 [13.7 H 桥](p2-02-ch12.md#ch13)

## 5.30 555 单稳态：一触发，亮一拍 <a id="demo30"></a>

<p align="center"><img src="assets/svg/ne555-monostable.svg" width="720" alt="555单稳态SVG动画"></p>

**看点**：按下触发按钮，OUT 拉高一整个 t=1.1·RC≈1.1s——右边波形里 OUT 高台与 Vc 指数爬升严格对齐，2Vcc/3 虚线正好压在充电终点。→ 正文 [10.5 单稳态](p1-10-ch9.md#ch10)

## 5.31 削波与钳位：闸门与垫脚石 <a id="demo31"></a>

<p align="center"><img src="assets/svg/clipper-clamper.svg" width="720" alt="削波钳位SVG动画"></p>

**看点**：左边红粒子从二极管闸门泄流削平顶底，右边绿粒子把 C 充成"串联电池"——同一个 0.7V，限幅动幅度、钳位动直流，一张图分清。→ 正文 [2.7 限幅与钳位](p1-02-ch1.md#ch2)

## 5.32 负反馈：十万倍的蛮力，被一根线驯成 6 倍 <a id="demo32"></a>

<p align="center"><img src="assets/svg/neg-feedback.svg" width="720" alt="负反馈SVG动画"></p>

**看点**：输出的一小份经反馈线"押"回反相端，把十万倍的开环蛮力驯成稳稳的 6 倍——输入输出波形完全重合，只差幅度。→ 正文 [12.1 方法论](p2-01-ch11.md#ch12)

## 5.33 积分器：方波换三角波 <a id="demo33"></a>

<p align="center"><img src="assets/svg/integrator.svg" width="720" alt="积分器SVG动画"></p>

**看点**：恒定电压灌进 RC，输出匀速爬坡——方波的两个电平正好对应三角波的上坡与下坡。→ 正文 [12.4 积分器与微分器](p2-01-ch11.md#ch12)

## 5.34 单电源虚地：给信号造一个假地 <a id="demo34"></a>

<p align="center"><img src="assets/svg/virtual-ground.svg" width="720" alt="单电源虚地SVG动画"></p>

**看点**：两枚 10k 电阻分压造出 6V 中点，耦合电容把信号"骑"上 6V——灰信号撞地削平 vs 绿信号全程完好。→ 正文 [12.8 单电源运放](p2-01-ch11.md#ch12)

## 5.35 迟滞振荡器：方波自己弹出来 <a id="demo35"></a>

<p align="center"><img src="assets/svg/schmitt-osc.svg" width="720" alt="迟滞振荡器SVG动画"></p>

**看点**：Vc 在 ±3V 门槛间指数弹跳、比较器翻转不停——迟滞比较器加一根 RC，输出方波自动循环。→ 正文 [7.3 迟滞](p1-07-ch6.md#ch7)

## 5.36 阻抗随频率：电容降价、电感涨价 <a id="demo36"></a>

<p align="center"><img src="assets/svg/impedance-freq.svg" width="720" alt="阻抗随频率SVG动画"></p>

**看点**：橙色扫线从左到右扫频——蓝色 Zc 一路降、红色 Zl 一路升，5kHz 交点就是 LC 谐振；一枚电容的"身份"随频率而变。→ 正文 [1.3 真实电感](p1-01-ch0.md#ch1)

## 5.37 运放内部：三级流水线攒出 20 万倍 <a id="demo37"></a>

<p align="center"><img src="assets/svg/opamp-internals.svg" width="720" alt="运放内部框图SVG动画"></p>

**看点**：粒子从 IN 流到 OUT——① 只认差模 ② 扛下全部增益（密勒补偿）③ 输出低阻，④ 偏置镜供水；每个 datasheet 参数都对得上位置。→ 正文 [6.1 解剖一只 741](p1-06-ch5.md#ch6)

## 5.38 排故五步法：把玄学拆成实验 <a id="demo38"></a>

<p align="center"><img src="assets/svg/debug-flow.svg" width="720" alt="排故五步法SVG动画"></p>

**看点**：橙框巡游五步、粒子沿流程走一圈——先问后拆、二分砍半、单变量、修根因、回归验证。→ 正文 [16.1 五步法详解](p4-00-part4.md#ch16)

## 5.39 分压器：带载就塌的三分之一 <a id="demo39"></a>

<p align="center"><img src="assets/svg/divider-loading.svg" width="720" alt="分压器带载塌陷SVG动画"></p>

**看点**：空载指针到中点 6V，接上 RL 后指针矮到 4V——分压公式只在空载时成立。→ 正文 [0.3 分压器](p1-00-part1.md#ch0)

## 5.40 BJT 三个工作区：负载线切过哪里 <a id="demo40"></a>

<p align="center"><img src="assets/svg/bjt-regions.svg" width="720" alt="BJT三个工作区SVG动画"></p>

**看点**：紫色圆点沿负载线来回扫——左端饱和（β 失效）、中段放大、右端截止。→ 正文 [3.2 三个工作区](p1-03-ch2.md#ch3)

## 5.41 热失控：自己给自己加速的正反馈 <a id="demo41"></a>

<p align="center"><img src="assets/svg/thermal-runaway.svg" width="720" alt="BJT热失控SVG动画"></p>

**看点**：红色转圈箭头绕着四个环节越转越快，结点越烧越大——唯一的刹车是射极电阻。→ 正文 [3.7 热失控](p1-03-ch2.md#ch3)

## 5.42 PT100 信号链：把信号顶到接近满量程 <a id="demo42"></a>

<p align="center"><img src="assets/svg/signal-chain.svg" width="720" alt="PT100信号链全链SVG动画"></p>

**看点**：绿色粒子逐级流过四环，蓝色线代表放大后的 1.54V（满量程 75%），贴地红线是"不放大就看不见"。→ 正文 [14.4 信号链实例](p3-00-part3.md#ch14)

## 5.43 真实电容阻抗频谱：谷底定去耦 <a id="demo43"></a>

<p align="center"><img src="assets/svg/capacitor-parasitics.svg" width="720" alt="真实电容阻抗频谱SVG动画"></p>

**看点**：蓝线（100nF MLCC）谷底 0.3Ω@22.5MHz，灰线（10µF 电解）谷底 1Ω@356kHz；过了自谐振，电容就变成了电感。→ 正文 [1.2 真实电容](p1-01-ch0.md#ch1)

## 5.44 米勒平台：开通那 700ns 里最贵的 410ns <a id="demo44"></a>

<p align="center"><img src="assets/svg/miller-plateau.svg" width="720" alt="MOSFET米勒平台SVG动画"></p>

**看点**：四条波形同屏——$V_{GS}$ 在 2.9V 被钉住 160ns，$V_{DS}$ 猛跌，$P=V·I$ 只在重叠区鼓包。→ 正文 [4.3 米勒平台](p1-04-ch3.md#ch4)

## 5.45 运放阶跃：直线爬坡，不是指数 <a id="demo45"></a>

<p align="center"><img src="assets/svg/opamp-slew.svg" width="720" alt="运放阶跃响应SVG动画"></p>

**看点**：蓝色实线 2µs 直线爬坡 vs 灰色虚线 1.1µs 指数——差的那 1.5µs 全是压摆率买的。→ 正文 [6.7 阶跃响应](p1-06-ch5.md#ch6)

## 5.46 二极管伏安特性：60mV 换十倍电流 <a id="demo46"></a>

<p align="center"><img src="assets/svg/diode-iv.svg" width="720" alt="二极管伏安特性SVG动画"></p>

**看点**：红蓝两条指数曲线，60℃ 那条整条左移 70mV——测温、稳压、温度传感全靠这条曲线。→ 正文 [2.2 伏安特性](p1-02-ch1.md#ch2)

## 5.47 运放 vs 比较器：快的不一定能用 <a id="demo47"></a>

<p align="center"><img src="assets/svg/comparator-opamp.svg" width="720" alt="运放与比较器对比SVG动画"></p>

**看点**：绿色游标 1.3µs 直接跳变，蓝色 4µs 慢慢爬；真正的坑是开漏输出的 2.2ms 上升沿。→ 正文 [7.1 为什么不能混用](p1-07-ch6.md#ch7)

## 5.48 噪声三税种：不能消灭，只能谈判 <a id="demo48"></a>

<p align="center"><img src="assets/svg/noise-budget.svg" width="720" alt="噪声谱与噪声预算SVG动画"></p>

**看点**：BJT 与 MOSFET 的 1/f 拐角差一个量级；1kΩ·1MHz 折算 4.1µV，×1000 后就是 4.1mV。→ 正文 [11.6 噪声](p2-00-part2.md#ch11)

## 5.49 探头是负载：测量本身在改电路 <a id="demo49"></a>

<p align="center"><img src="assets/svg/probe-loading.svg" width="720" alt="探头负载与测量安全SVG动画"></p>

**看点**：×1 探头在 100kΩ 节点上造成 9% 分压误差并把 f_c 压到 16kHz；另附电流档短路与地夹短路的两个「一按就出事」。→ 正文 [16.3 测量铁律](p4-00-part4.md#ch16)

## 5.50 传输门：一只管子总有一段使不上劲 <a id="demo50"></a>

<p align="center"><img src="assets/svg/transfer-gate.svg" width="720" alt="CMOS传输门SVG动画"></p>

**看点**：红线上翘（N 管高端罢工）、蓝线左端翘（P 管低端罢工），绿线并联后全程平坦 20~27Ω——这就是「N 管送低、P 管送高」。→ 正文 [8.1 传输门原理](p1-08-ch7.md#ch8)

## 5.51 三态总线：谁说话，谁闭嘴 <a id="demo51"></a>

<p align="center"><img src="assets/svg/tristate-bus.svg" width="720" alt="三态总线SVG动画"></p>

**看点**：两个驱动器共享一根总线，粒子显示谁在推电流；两个同时驱动就是直通电流（第四格）。→ 正文 [5.4 三态与高阻](p1-05-ch4.md#ch5)

## 5.52 三种基本拓扑：同一只运放的三条路 <a id="demo52"></a>

<p align="center"><img src="assets/svg/three-topologies.svg" width="720" alt="三种基本拓扑对比SVG动画"></p>

**看点**：反相/同相/差分并排——同一组电阻比例都是 10 倍增益，差别只在输入阻抗、共模与服务代价。→ 正文 [12.2 三个基本拓扑](p2-01-ch11.md#ch12)

## 5.53 推挽输出级：直通电流从哪来 <a id="demo53"></a>

<p align="center"><img src="assets/svg/pushpull-stage.svg" width="720" alt="推挽输出级SVG动画"></p>

**看点**：上管供流/下管吸流两个方向都主动；两个推挽直连 = 100mA 短路，换班瞬间还有直通电流。→ 正文 [5.1 推挽输出](p1-05-ch4.md#ch5)

## 5.54 解剖 LM393：开漏输出的三个红利 <a id="demo54"></a>

<p align="center"><img src="assets/svg/lm393-inside.svg" width="720" alt="LM393内部解剖SVG动画"></p>

**看点**：粒子从 PNP 输入级流到开漏输出管；上拉接任意电压 → 电平转换，多路并联 → 线与。→ 正文 [7.2 解剖 LM393](p1-07-ch6.md#ch7)

## 5.55 齐纳 vs 带隙：两套温漂账 <a id="demo55"></a>

<p align="center"><img src="assets/svg/ref-showdown.svg" width="720" alt="齐纳与带隙对比SVG动画"></p>

**看点**：齐纳的抛物线温漂（5.6V 才触底）对带隙的平直线（3ppm/℃）；配比 K=2/0.177≈11.3 的来龙去脉。→ 正文 [9.1 齐纳 vs 带隙](p1-09-ch8.md#ch9)

## 5.56 PN 结：一堵会自己调节高度的墙 <a id="demo56"></a>

<p align="center"><img src="assets/svg/pn-junction.svg" width="720" alt="PN结形成SVG动画"></p>

**看点**：载流子扩散进耗尽层、电场把后来的往回推；三步（复合→建墙→平衡）就是内建电势的由来。→ 正文 [2.1 PN 结的形成](p1-02-ch1.md#ch2)

## 5.57 MOSFET 输出特性：饱和反而是放大区 <a id="demo57"></a>

<p align="center"><img src="assets/svg/mosfet-curves.svg" width="720" alt="MOSFET输出特性SVG动画"></p>

**看点**：四条曲线（四个 V_GS）+ 夹断点虚线；左边可变电阻、右边恒流源——别与 BJT 的"饱和"混淆。→ 正文 [4.2 输出特性](p1-04-ch3.md#ch4)

## 5.58 555 三种模式：同一颗芯三副面孔 <a id="demo58"></a>

<p align="center"><img src="assets/svg/555-modes.svg" width="720" alt="555三种模式SVG动画"></p>

**看点**：无稳态连续方波 / 单稳态一个脉冲 / 双稳态保持——差异只在电容接哪只脚。→ 正文 [10.2 三种模式](p1-10-ch9.md#ch10)

## 5.59 负反馈四种拓扑：稳定什么就采样什么 <a id="demo59"></a>

<p align="center"><img src="assets/svg/feedback-topo.svg" width="720" alt="负反馈四拓扑SVG动画"></p>

**看点**：2×2 四格卡片把四种拓扑的「钉死的量 / 受控源身份 / 阻抗走向」一次摊开。→ 正文 [12.7 负反馈四种拓扑](p2-01-ch11.md#ch12)

## 5.60 真实电阻：高频时它不再是「一个电阻」 <a id="demo60"></a>

<p align="center"><img src="assets/svg/resistor-model.svg" width="720" alt="真实电阻等效模型SVG动画"></p>

**看点**：理想 1kΩ 与真实电阻在 0.8GHz 前几乎重合、之后下坠到 1GHz 的 575Ω、3.6GHz 探底 ≈49Ω，再被引线电感拉回上升；两个寄生夺权点 f₁/f₂。→ 正文 [1.1 真实电阻](p1-01-ch0.md#ch1)

## 5.61 特殊二极管家族：压降与速度的地图 <a id="demo61"></a>

<p align="center"><img src="assets/svg/diode-family.svg" width="720" alt="特殊二极管家族SVG动画"></p>

**看点**：六族按「压降 × 速度」定位——肖特基左上、LED 下方、TVS 右上，位置即岗位。→ 正文 [2.4 特殊二极管](p1-02-ch1.md#ch2)

## 5.62 上拉电阻：4.7k 是怎么算出来的 <a id="demo62"></a>

<p align="center"><img src="assets/svg/pullup-sizing.svg" width="720" alt="上拉电阻取值SVG动画"></p>

**看点**：t_r≈0.8473·R·C 与 I=V/R 两条约束交叉出 4.7k；标准/快速模式的上限一目了然。→ 正文 [5.3 上拉与下拉](p1-05-ch4.md#ch5)

## 5.63 LM358：单电源双运放的两条边界 <a id="demo63"></a>

<p align="center"><img src="assets/svg/lm358-dual.svg" width="720" alt="LM358双运放SVG动画"></p>

**看点**：PNP 输入级让共模含地；输出非轨到轨（5V 供电只剩 3.5V）——摆幅账要提前扣。→ 正文 [6.2 LM358](p1-06-ch5.md#ch6)

## 5.64 三种组态：一只管子的三种人生 <a id="demo64"></a>

<p align="center"><img src="assets/svg/bjt-configs.svg" width="720" alt="BJT三种组态SVG动画"></p>

**看点**：共射/共集/共基并排——增益、阻抗、相位、用途四行对照；级联心法一句话。→ 正文 [11.1 三种组态](p2-00-part2.md#ch11)

## 5.65 分立串联稳压：LDO 的祖爷爷 <a id="demo65"></a>

<p align="center"><img src="assets/svg/discrete-ldo.svg" width="720" alt="分立串联稳压SVG动画"></p>

**看点**：齐纳基准 + 射随器调整管 + 顺带负反馈；Vout=V_Z−0.7V 的直流账与双重温漂。→ 正文 [13.1 分立串联稳压](p2-02-ch12.md#ch13)

## 5.66 BJT 放大原理：99% 的电子成了 I_C <a id="demo66"></a>

<p align="center"><img src="assets/svg/bjt-transport.svg" width="720" alt="BJT载流子输运SVG动画"></p>

**看点**：电子从发射区注入基区、绝大多数被集电结扫走、只有 1% 复合形成 I_B——β 的物理来源。→ 正文 [3.1 载流子输运](p1-03-ch2.md#ch3)

## 5.67 BJT 开关：Rb 怎么算、二极管为什么不能省 <a id="demo67"></a>

<p align="center"><img src="assets/svg/bjt-switch.svg" width="720" alt="BJT驱动继电器SVG动画"></p>

**看点**：强制 β=10 → I_B=7mA → R_B≈371Ω（就近取 360Ω）三步账；线圈反电动势与续流回路。→ 正文 [3.5 BJT 作开关](p1-03-ch2.md#ch3)

## 5.68 体二极管与栅极保护：MOS 的两条命门 <a id="demo68"></a>

<p align="center"><img src="assets/svg/body-diode.svg" width="720" alt="MOSFET体二极管SVG动画"></p>

**看点**：体二极管既是死区续流的功臣、也断了「反向阻断」的路；栅氧层 ±20V 的脆弱与防护。→ 正文 [4.4 体二极管](p1-04-ch3.md#ch4)

## 5.69 CD4051：八路传感器共用一个 ADC <a id="demo69"></a>

<p align="center"><img src="assets/svg/mux-4051.svg" width="720" alt="CD4051多路复用SVG动画"></p>

**看点**：3 位地址选 8 路、通道双向、切换时的电荷注入与 Ron 变化。→ 正文 [8.2 CD4066 与 CD4051](p1-08-ch7.md#ch8)

## 5.70 达林顿管：β 相乘与三笔代价 <a id="demo70"></a>

<p align="center"><img src="assets/svg/darlington.svg" width="720" alt="达林顿管SVG动画"></p>

**看点**：前级发射极电流就是后级基极电流；β≈β₁β₂ 换来的 1.4V / 0.9V / 慢三笔代价。→ 正文 [3.6 达林顿管](p1-03-ch2.md#ch3)

## 5.71 Datasheet 六参数优先级 <a id="demo71"></a>

<p align="center"><img src="assets/svg/datasheet-params.svg" width="720" alt="Datasheet六参数SVG动画"></p>

**看点**：六个参数按「会咬人」排序，每个都标出咬点与选型公式——五十页只读这六行。→ 正文 [6.3 Datasheet 参数](p1-06-ch5.md#ch6)

## 5.72 运放选型地图：速度 × 精度 <a id="demo72"></a>

<p align="center"><img src="assets/svg/opamp-map.svg" width="720" alt="运放选型地图SVG动画"></p>

**看点**：七款常见运放按 GBW 与 V_OS 定位——斩波零漂在最高精度区、741/LM358 在左下角。→ 正文 [6.4 常用运放选型](p1-06-ch5.md#ch6)

## 5.73 7805/AMS1117 四种翻车 <a id="demo73"></a>

<p align="center"><img src="assets/svg/ldo-failures.svg" width="720" alt="线性稳压故障地图SVG动画"></p>

**看点**：热账 2.1W、纹波谷值、ESR 振荡、上电过冲——四种死法的账都在图里。→ 正文 [9.4 7805/AMS1117 故障](p1-09-ch8.md#ch9)

## 5.74 BJT 在线速判：三个电压定故障 <a id="demo74"></a>

<p align="center"><img src="assets/svg/bjt-diagnosis.svg" width="720" alt="BJT在线速判SVG动画"></p>

**看点**：正常态两条判据 + 六种异常读数各自的故障定位与下一步动作。→ 正文 [3.8 BJT 故障速查](p1-03-ch2.md#ch3)

## 5.75 运放的六个经典坑 <a id="demo75"></a>

<p align="center"><img src="assets/svg/opamp-pitfalls.svg" width="720" alt="运放六个坑SVG动画"></p>

**看点**：按现场频率排序的六个坑；诊断顺序「输出电平 → 输入端压差 → 最后才怀疑运放」。→ 正文 [6.6 运放故障案例](p1-06-ch5.md#ch6)

## 5.76 比较器的五个坑：忘接上拉排第一 <a id="demo76"></a>

<p align="center"><img src="assets/svg/comparator-pitfalls.svg" width="720" alt="比较器五个坑SVG动画"></p>

**看点**：开漏的两个后果（没上拉就没高电平 / 上拉位置决定电平）与三条红利。→ 正文 [7.4 比较器故障案例](p1-07-ch6.md#ch7)

## 5.77 555 参数与三个坑 <a id="demo77"></a>

<p align="center"><img src="assets/svg/ne555-params.svg" width="720" alt="555参数与三个坑SVG动画"></p>

**看点**：双极版 vs CMOS 版参数对照；5 脚为什么必须接 10nF、容性负载振荡、电源毛刺。→ 正文 [10.3 参数与故障](p1-10-ch9.md#ch10)

## 5.78 恒压源与恒流源：看 V-I 曲线认性格 <a id="demo78"></a>

<p align="center"><img src="assets/svg/source-types.svg" width="720" alt="恒压源与恒流源SVG动画"></p>

**看点**：竖直=恒压、水平=恒流，斜率就是内阻；1mΩ 与 100mΩ 两台电源的账一目了然。→ 正文 [0.6 恒压源与恒流源](p1-00-part1.md#ch0)

## 5.79 戴维南与诺顿：两个数定性格 <a id="demo79"></a>

<p align="center"><img src="assets/svg/thevenin-norton.svg" width="720" alt="戴维南与诺顿等效SVG动画"></p>

**看点**：12V/10k/10k 网络 → V_th=6V、I_N=1.2mA、R_th=5kΩ；带载误差只看 R_th 与 R_L 之比。→ 正文 [1.4 戴维南与诺顿](p1-01-ch0.md#ch1)

## 5.80 恒流源的合规电压 <a id="demo80"></a>

<p align="center"><img src="assets/svg/compliance-voltage.svg" width="720" alt="恒流源合规电压SVG动画"></p>

**看点**：2.0V + 0.1V + 0.7V = 2.8V 的合规账；负载超过 R_L,max 电流就塌——这就是 4~20mA 环流用 24V 的原因。→ 正文 [13.5 恒流源家族](p2-02-ch12.md#ch13)

## 5.81 共射放大器四拍：输入升、输出降 <a id="demo81"></a>

<p align="center"><img src="assets/svg/ce-dynamic.svg" width="720" alt="共射放大器四拍拆解SVG动画"></p>

**看点**：一个正弦周期拆成四拍；上行余量 6V、下行余量 4V → 对称摆幅 8.0Vpp；Q 点偏置就是「余量分配器」。→ 正文 [3.9 动态分析](p1-03-ch2.md#ch3)

## 5.82 MOSFET 开通四拍：栅极电荷如何变成热 <a id="demo82"></a>

<p align="center"><img src="assets/svg/mosfet-four-beats.svg" width="720" alt="MOSFET开通四拍SVG动画"></p>

**看点**：① 延时只充 $C_{GS}$；② $I_D$ 上升而 $V_{DS}$ 仍是 20V；③ $Q_{gd}=1.6nC$ 搬出 Miller 平台；④ 完全增强后只剩 0.75W 导通损耗。→ 正文 [4.6 动态分析](p1-04-ch3.md#ch4)

## 5.83 整流滤波电源四拍：从空电容到稳态纹波 <a id="demo83"></a>

<p align="center"><img src="assets/svg/rectifier-filter-beats.svg" width="720" alt="整流滤波电源四拍拆解SVG动画"></p>

**看点**：① 初始态电容放空；② 浪涌充电 10~50A；③ 稳态峰值充电 5~10A、导通角~20%；④ 谷值放电电容独供负载。→ 正文 [2.6 动态分析](p1-02-ch1.md#ch2)


## 5.84 模拟开关开合四拍：电荷注入如何毁掉采样精度 <a id="demo84"></a>

<p align="center"><img src="assets/svg/analog-switch-beats.svg" width="720" alt="模拟开关开合四拍拆解SVG动画"></p>

**看点**：① 栅极驱动开启、$R_{on}$→45Ω；② 沟道存 $Q_{ch}=0.2pC$；③ 关断注入 $\Delta V=10mV$（=20 LSB）；④ dummy 管反向抵消。→ 正文 [8.6 动态分析](p1-08-ch7.md#ch8)

**怎么看**：沿竖直时间游标同时看蓝色 $V_C$ 与紫色 EN 圆点；EN 在 8ms 变低时，$V_C$ 同时跳低 10mV。下方字幕切到「保持」，此后缓慢下垂是保持期的另一种误差。波形展示未补偿情况，第四张卡片说明 dummy 管的改进思路。

## 5.85 LDO 负载瞬态四拍：一次唤醒为何把 MCU 打到复位 <a id="demo85"></a>

<p align="center"><img src="assets/svg/ldo-transient-beats.svg" width="720" alt="LDO负载瞬态四拍拆解SVG动画"></p>

**看点**：① ESR 瞬跳 25mV；② 电容放电 245mV；③ 环路接管回升；④ 重新锁定（可能过冲）。总跌落 270mV ＞ 3.3V 复位阈值 165mV。→ 正文 [9.5 动态分析](p1-09-ch8.md#ch9)

**怎么看**：竖游标上的两点对应同一时刻。5µs 时负载电流跳高，输出先因 ESR 跳低；5–10µs 电容继续供电，10µs 后环路接管，30µs 后进入新的稳态。字幕随这四段切换；恢复曲线用于说明因果，实际过冲与恢复时间要看所选 LDO 和外围参数。

## 5.86 555 无稳态四拍：电容荡秋千，输出跳方波 <a id="demo86"></a>

<p align="center"><img src="assets/svg/555-astable-beats.svg" width="720" alt="555无稳态四拍拆解SVG动画"></p>

**看点**：① 上电 OUT 高；② 充电 541µs（走 R1+R2）；③ 放电 471µs（只走 R2）；④ 循环 → ≈990Hz、占空比 53%。→ 正文 [10.4 动态分析](p1-10-ch9.md#ch10)

**怎么看**：竖游标同时指向电容电压和 OUT，充到 6V 的那一刻 OUT 翻低，降回 3V 后下一周期 OUT 翻高。字幕同步显示充电或放电；下方波形是稳态周期，上方第一张卡片单独说明从 0V 开始的首次上电。

## 5.87 水路 = 电路：全书通用比喻 <a id="demo87"></a>

<p align="center"><img src="assets/svg/water-analogy.svg" width="720" alt="水路=电路通用比喻SVG动画"></p>

**看点**：环形水路走一圈，八个词一次记住——电压/电流/电阻/电容/电感/二极管/MOSFET/地。→ 正文 [0.1](p1-00-part1.md#ch0)

## 5.88 树状供电：逐级净化 <a id="demo88"></a>

<p align="center"><img src="assets/svg/power-tree.svg" width="720" alt="树状供电逐级净化SVG动画"></p>

**看点**：输入 → 储能 → 稳压 → 去耦，每一级替下一级挡脏；去耦电容就近放。→ 正文 [14.3](p3-00-part3.md#ch14)

## 5.89 电压降：同一股电流，谁 R 大谁分得多 <a id="demo89"></a>

<p align="center"><img src="assets/svg/voltage-drop.svg" width="720" alt="电压降SVG动画"></p>

**看点**：串联 4kΩ+1kΩ 分 5V，各得 4V/1V；右侧电压剖面把「竖降=跨电阻、横走=沿导线」画清楚。→ 正文 [0.2 欧姆定律](p1-00-part1.md#ch0)

## 5.90 PCB 布线四招：45° 拐角 / 过孔 / 差分对 / 包地 <a id="demo90"></a>

<p align="center"><img src="assets/svg/pcb-routing.svg" width="720" alt="PCB布线四招SVG动画"></p>

**看点**：90° 尖角 vs 45° 折角、过孔 1nH+0.5pF、差分对等长紧邻、敏感线包地——四条规则的物理来源一屏看懂。→ 正文 [15.3 布线规则](p3-01-ch14.md#ch15)




## 5.91 故障速查：症状 → 嫌疑 → 验证 <a id="demo91"></a>

<p align="center"><img src="assets/svg/fault-lookup.svg" width="720" alt="故障速查SVG动画：症状→嫌疑→验证三列链路"></p>

**看点**：四类故障四条链路，粒子从症状流向头号嫌疑再到验证手段；底部紫色条是「不该振荡却振荡」的固定排查顺序。**先量电源——近一半故障藏在这里。** → 正文 [17.1 电源类](p4-01-ch16.md#ch17)

## 5.92 MOSFET 开关：沟道形成与导通 <a id="demo92"></a>

<p align="center"><img src="assets/svg/mosfet-switch.svg" width="720" alt="MOSFET 开关动画：沟道形成与导通"></p>

**看点**：$V_{GS}=0$ 两个背靠背 PN 结挡路；$V_{GS}>V_{TH}$ 栅极电场召唤电子形成 N 型沟道，S-D 导通——沟道电阻随 $V_{GS}$ 连续可调。**电压控制，不取栅流。** → 正文 [4.1 沟道形成原理](p1-04-ch3.md#ch4)

## 5.93 反相放大器：虚短虚断 <a id="demo93"></a>

<p align="center"><img src="assets/svg/opamp-inverting.svg" width="720" alt="反相放大器动画：虚短虚断"></p>

**看点**：$V_+≈V_-$ 与输入端不取电流，两条公理把五个拓扑变成五个"不用背的形状"。**先讲清公理凭什么成立，再看电路。** → 正文 [6.5 经典应用电路原理](p1-06-ch5.md#ch6)

## 5.94 模拟开关：电荷注入 <a id="demo94"></a>

<p align="center"><img src="assets/svg/analog-switch.svg" width="720" alt="模拟开关动画：电荷注入"></p>

**看点**：关断瞬间沟道里攒的电荷"无家可归"，被挤进保持电容——$ΔV=Q/C$ 是采样电路里最隐蔽的误差源（Charge Injection）。**别在 ADC 转换中途切通道。** → 正文 [8.3 关键参数解析](p1-08-ch7.md#ch8)

## 5.95 LDO 负反馈：闭环控制 <a id="demo95"></a>

<p align="center"><img src="assets/svg/ldo-feedback.svg" width="720" alt="LDO负反馈动画"></p>

**看点**：LDO 不是"稳压元件"而是闭环控制系统——误差放大器每秒纠正几千次。**输出电容 ESR 为什么能把它逼疯（环路稳定性），一眼看懂。** → 正文 [9.3 LDO 线性稳压器剖析](p1-09-ch8.md#ch9)

## 5.96 去耦电容：本地水库 <a id="demo96"></a>

<p align="center"><img src="assets/svg/cap-decoupling.svg" width="720" alt="去耦电容动画：贴脸放的真正原因"></p>

**看点**：去耦电容不是"滤波"而是**本地水库**——ns 级电流尖峰面前，10cm 走线电感就是断路。**"100nF 贴脸 <3mm"不是建议，是铁律。** → 正文 [15.1 布局](p3-01-ch14.md#ch15)

## 5.97 大师的排故智慧：三份心法，一条军规 <a id="demo97"></a>

<p align="center"><img src="assets/svg/master-wisdom.svg" width="720" alt="大师排故智慧SVG动画：三份心法一条军规"></p>

**看点**：Pease（先量电源/怀疑仪器）、Williams（预测波形/最小化复现）、共通（慢观察/快假设/严验证）三栏金句；底部军规条粒子链。**排故不是体力活，是科学方法。** → 正文 [18.1 Bob Pease](p4-02-ch17.md#ch18)

## 5.98 从需求到打样：六步流程 <a id="demo98"></a>

<p align="center"><img src="assets/svg/design-flow.svg" width="720" alt="从需求到打样六步流程SVG动画：一链加回炉回环"></p>

**看点**：需求指标 → 拓扑选择 → 器件选型 → 仿真验证 → 降额与保护 → 打样测试六步一链，粒子从头走到尾；仿真不过沿橙色回环回炉。**流程是螺旋不是直线。** → 正文 [14.1 设计流程](p3-00-part3.md#ch14)

## 5.99 思维工具箱：四暗器 <a id="demo99"></a>

<p align="center"><img src="assets/svg/thinking-toolbox.svg" width="720" alt="思维工具箱SVG动画：四暗器何时用"></p>

**看点**：内外归因 / 对比法 / 极限法 / 隔离法四色卡片，粒子沿外框环绕；「何时用」一行小字。**先内外、再对比、极限逼、隔离切。** → 正文 [16.2 思维工具箱](p4-00-part4.md#ch16)

## 5.100 一点接地：让大电流别踩小信号的路 <a id="demo100"></a>

<p align="center"><img src="assets/svg/ground-star.svg" width="720" alt="一点接地SVG动画：共用地线vs星形接地"></p>

**看点**：左红「共用地线」负载地与信号地共用一段 AB，10A×0.01Ω=100mV 压降踩进信号基准；右绿「星形一点接地」各自到汇点互不污染。**地不是"0V 参考点"，是电流回家的路。** → 正文 [15.2 接地](p3-01-ch14.md#ch15)

## 5.101 变压器：电压换电流 <a id="demo101"></a>

<p align="center"><img src="assets/svg/transformer.svg" width="720" alt="变压器SVG动画：电压换电流"></p>

**看点**：变比 1:2 升压——紫色磁通粒子沿磁芯搬能量，红/绿电流粒子同步进出；电压翻倍处电流减半。**初次级只有磁通耦合，没有导线相连。** → 正文 [1.3 真实电感与变压器](p1-01-ch0.md#ch1)

## 5.102 排故决策树：从「上电无反应」到具体表项 <a id="demo102"></a>

<p align="center"><img src="assets/svg/diagnosis-tree.svg" width="720" alt="排故决策树SVG动画：从「上电无反应」一路走到具体表项"></p>

**看点**：决策脊柱一路向下——「输入电压？」「电源轨？」「复位/时钟？」每问一个「否」就横向落到一张速查表（17.1/17.3）；四问皆「是」却功能异常，则按表现分四叶：完全不动→17.3、读数不对→17.2、时好时坏→17.6→17.4、发热异常→17.5。**先定方向、再查细节——顺序本身就是方法论。** → 正文 [17.8 分诊决策树](p4-01-ch16.md#ch17)

## 5.103 电容直流偏压：标称容量 ≠ 工作容量 <a id="demo103"></a>

<p align="center"><img src="assets/svg/cap-derating.svg" width="720" alt="电容直流偏压降容教学动画：5V 时 10µF × 26% = 2.6µF"></p>

**看点**：圆点匀速扫过偏压轴，红线和 5V 工作点来自同一组教学数据；假设保持率为 26%，10µF 就变为 2.6µF，同纹波电流且忽略 ESR 时容性纹波增至约 3.85 倍。**曲线不是实测值，X5R/X7R 也不是降容等级**；C0G 仅作归一化参考。→ 正文 [1.7 电容直流偏压降容](p1-02-ch1.md#cap-dc-bias)

## 5.104 Falstad 内置示例地图（全部带动画）

| 主题 | 菜单路径 |
|---|---|
| 欧姆定律/分压 | Circuits → Basics |
| RC/RLC 暂态与谐振 | Circuits → Basics → RLC |
| 二极管整流全家桶 | Circuits → Diodes |
| 晶体管放大器 | Circuits → Transistors |
| 运放全家桶（跟随/反相/积分/滤波） | Circuits → Op-Amps |
| 555 系列 | Circuits → 555 Timer Chip |
| 开关电源 Buck/Boost | Circuits → Power Converters |

---

<a id="part6"></a>

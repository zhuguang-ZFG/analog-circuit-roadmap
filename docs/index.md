# 通往模拟电路之路 🛤️

> 从欧姆定律到芯片内部结构，一份把原理推导、器件剖析、故障分析和动画演示连起来的模拟电路学习指南。

<div class="learning-hero" markdown="1">

<p class="learning-eyebrow">理解原理 · 观察变化 · 动手验证</p>

## 从看懂一张电路图开始

电流为什么这样流？波形为什么变了？电路为什么没有按预期工作？沿着一条清晰的路线，用动画建立直觉，用计算和测量检验理解。

<p class="learning-actions">
  <a class="learning-primary" href="p1-01-ch0.md#ch0">从第 0 章开始 →</a>
  <a href="p1-02-ch1.md#rc-study">先体验 RC 互动课</a>
</p>

**19 章核心内容** · **108 张原理动画** · **3 个可控教学样板** · **58 道章节题 + 34 道专题题**

</div>

## 找到适合你的起点

<div class="learning-paths" markdown="1">

<div class="learning-path" markdown="1">

### 01 · 从零建立直觉

**适合：刚开始学电路。**

先理解电压、电流和回路，再认识真实元件。遇到公式，先问它在描述什么变化。

[电路直觉](p1-01-ch0.md#ch0) → [无源元件](p1-02-ch1.md#ch1) → [二极管](p1-03-ch2.md#ch2)

**阶段目标**：能解释分压器接上负载后，输出为什么会下降。

</div>

<div class="learning-path" markdown="1">

### 02 · 从单片机走向模拟

**适合：会用 MCU，想读懂外围电路。**

从熟悉的 GPIO 出发，弄清接口、放大与布局之间的关系。

[推挽与开漏](p1-06-ch5.md#ch5) → [运放基础](p1-07-ch6.md#ch6) → [运放电路族](p2-02-ch12.md#ch12) → [PCB 实战](p3-02-ch15.md#ch15)

**阶段目标**：能说明上拉电阻的作用，并检查信号是否超出运放的工作范围。

</div>

<div class="learning-path" markdown="1">

### 03 · 带着工程问题来

**适合：正在调板，或需要复习。**

先定位症状，再回到原理；保留测量条件，一次验证一个假设。

[按需求找电路](p0-04-by-need.md) → [故障速查](p4-02-ch17.md#ch17) → [排故五步法](p4-01-ch16.md#ch16)

**阶段目标**：写下一条可验证的故障假设，以及支持或推翻它的测量结果。

</div>

</div>

## 先学会一个电路

三个样板都把动画、实物、测量接线和就地自测放在一起。在线站支持暂停、阶段定位和局部放大。

<div class="learning-lessons" markdown="1">

<div class="learning-lesson" markdown="1">

<a href="p1-02-ch1.md#rc-study"><img src="assets/svg/rc-charge.svg" width="360" alt="RC 充电电路与电容电压随时间变化的曲线"></a>

### RC 充放电

看电压如何变化，对照时间常数，再按接线说明测一次。

[开始 RC 互动课 →](p1-02-ch1.md#rc-study)

</div>

<div class="learning-lesson" markdown="1">

<a href="p1-05-ch4.md#mosfet-study"><img src="assets/svg/mosfet-four-beats.svg" width="360" alt="MOSFET 开通过程中的栅极电压、漏极电压与电流波形"></a>

### MOSFET 开关

暂停在米勒平台，比较栅极电压、漏极电压和电流。

[开始 MOSFET 互动课 →](p1-05-ch4.md#mosfet-study)

</div>

<div class="learning-lesson" markdown="1">

<a href="p1-07-ch6.md#lm358-study"><img src="assets/svg/lm358-dual.svg" width="360" alt="LM358 双运放引脚、内部结构与输入输出边界示意"></a>

### LM358 跟随器

认识引脚，检查输入与输出边界，理解为什么输出跟不上。

[开始 LM358 互动课 →](p1-07-ch6.md#lm358-study)

</div>

</div>

## 每章这样学

1. **带着问题看动画**：先预测哪个量会变、往哪个方向变，再播放核对。
2. **对照原理算一笔**：写下单位、供电、负载和所用假设，别只记结论。
3. **合上正文做自测**：在线站每章末尾都有对应题目入口；做错后回到该章复习。
4. **用实验检验理解**：参考 [里程碑项目](p8-03-s8-3.md)，把计算、仿真与实测放在一起比较。

题目是帮助你发现薄弱环节的工具；做对题并不代替实验和设计评审。元件参数请结合具体型号与工作条件核对 [官方资料](p6-03-s6-3.md)。

## 随手可查的工具

| 想解决什么 | 从这里进入 |
|---|---|
| 看清完整学习顺序 | [学习路线图](p0-06-roadmap.md#roadmap) · [全书目录](p0-07-toc.md#toc) · [三条时间线](p0-03-timeline.md) |
| 找一个电路或动画 | [情景导航](p0-04-by-need.md) · [动画演示中心](p5-00-part5.md#part5)（在线站侧栏另有可筛选画廊） |
| 遇到陌生术语 | [模拟黑话速查](p8-10-s8-10.md#sec810) · [元件标识速查](p6-05-s6-5.md) |
| 查型号和参数条件 | [常用芯片](p6-02-s6-2.md) · [Datasheet 阅读法](p6-04-s6-4.md) · [原厂应用笔记](p8-08-s8-8.md#sec88) |
| 检验自己是否理解 | [章节自测与专题加练](p9-00-quiz.md#part9) · [动手项目](p8-03-s8-3.md) |

在线站顶部支持全文搜索，可以从“去耦电容”“相位裕度”“LM358”等具体术语开始。

<a id="news"></a>
## 最近更新

- **v3.33 · 学习体验与中文搜索**：重新组织学习入口；修正章节跳转，每章串起正文、自测与下一章，保留旧链接入口；补齐中文分词与领域术语词典。
- **v3.32 · 五张新动画**：运放输入级、晶体振荡器、光耦、误差预算与探头地线环，[查看动画与讲解](p5-00-part5.md#demo104)。
- **v3.31 · 三个教学样板**：RC、MOSFET、LM358 支持动画控制，配套实物、接线与自测。

[查看完整更新日志 →](p9-12-changelog.md)

---

[在线知识站](https://zhuguang-ZFG.github.io/analog-circuit-roadmap/) · [参与共建](CONTRIBUTING.md) · [CC BY-SA 4.0](LICENSE)

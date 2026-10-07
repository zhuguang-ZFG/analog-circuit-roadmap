# 通往模拟电路之路 🛤️

> 一份由社区资源滋养的模拟电路（Analog Circuits）系统学习指南
> 仿《通往 AGI 之路》知识体系风格 —— 从欧姆定律到芯片内部结构
> 特色：**原理推导 + 器件内部剖析 + 故障分析 + 动画演示**
> 最后更新：2026-10

---

<p align="center">
  <img src="assets/svg/comparator-hysteresis.svg" width="720" alt="动画演示：比较器迟滞原理">
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-CC_BY--SA_4.0-lightgrey.svg" alt="License"></a>
  <img src="https://img.shields.io/badge/SVG动画-102张-3fb950.svg" alt="SVG">
  <img src="https://img.shields.io/badge/章节-9篇19章-58a6ff.svg" alt="chapters">
  <img src="https://img.shields.io/badge/最近更新-2026.10-f0883e.svg" alt="updated">
  <a href="https://zhuguang-ZFG.github.io/analog-circuit-roadmap/"><img src="https://img.shields.io/badge/在线站点-waytoagi式知识站-blueviolet.svg" alt="site"></a>
</p>

<p align="center">
🧭 <a href="p0-05-picks.md#roadmap">路线图</a> · 📑 <a href="p0-06-roadmap.md#toc">目录</a> · 🔬 <a href="p0-07-toc.md#part1">器件原理</a> · ⚡ <a href="p1-11-ch10.md#part2">电路拓扑</a> · 🛠️ <a href="p2-03-ch13.md#part3">设计与PCB</a> · 🩺 <a href="p3-02-ch15.md#part4">排故方法</a> · 🎬 <a href="p4-03-ch18.md#part5">动画中心</a> · 🧩 <a href="p5-00-part5.md#part6">图鉴速查</a> · 📺 <a href="p6-05-s6-5.md#part7">视频</a> · 📚 <a href="p7-02-s7-2.md#part8">路线索引</a> · 🧪 <a href="p9-00-quiz.md">自测题库</a>
</p>

<a id="news"></a>
## 📰 更新速递

> 每次回来先看这一屏；完整历史见 [🗓️ 更新日志](p9-12-changelog.md)。

| 日期 | 更新 | 直达 |
|---|---|---|
| 2026-10 | **v3.21 内容补强**：第 17 章升级为「故障速查总表」四列大表 + 分诊决策树动画（第 102 张）；补齐 5 个缺失主题小节；自测题库加 **15 道专题加练** | [v3.21](p9-12-changelog.md) |
| 2026-10 | 新增 **§12.10 跨阻放大器 TIA**：$V_{out}=-I_{ph}R_f$、补偿电容公式、四个必踩的坑 | [12.10](p2-01-ch11.md#ch12) |
| 2026-10 | 新增 **§13.8 电流检测**（低侧/高侧、开尔文连接）与 **§13.9 音频功放与 THD**（A/B/AB/D 效率账、交越失真） | [13.8](p2-02-ch12.md#ch13) · [13.9](p2-02-ch12.md#ch13) |
| 2026-10 | 新增 **§14.5 热设计**（$T_J=T_A+P\sum\theta$ 倒推散热器）与 **§14.6 LTspice 实操方法论**（五种分析 + 五个常见坑） | [14.5](p3-00-part3.md#ch14) · [14.6](p3-00-part3.md#ch14) |
| 2026-10 | **v3.20 站点化 + 工程化**：正文拆为 `docs/` 单一数据源，README 由脚本生成；上线在线知识站（侧栏目录 · 全文搜索 · 动画画廊） | [v3.20](p9-12-changelog.md) |
| 2026-10 | 新增 **第九篇 自测与练习**：19 章 × 3 题，答案折叠，先算再对 | [🧪 自测题库](p9-00-quiz.md) |
| 2026-10 | 新增 **§2.8 接口保护三件套**：TVS + 限流电阻 + 钳位二极管，含 ESD 8kV 算一笔 | [2.8](p1-02-ch1.md#ch2) |
| 2026-10 | 新增 **§12.9 稳定性实战**：容性负载/长电缆为什么会振，隔离电阻与噪声增益两招 | [12.9](p2-01-ch11.md#ch12) |
| 2026-10 | 新增 **§15.6 EMC/EMI**：三要素、十条硬规矩、三个真实整改现场 | [15.6](p3-01-ch14.md#ch15) |

**三个新入口**：🌐 [在线知识站](https://zhuguang-ZFG.github.io/analog-circuit-roadmap/)（可搜索、可深浅色切换）· 🎬 [动画画廊](p5-00-part5.md)（102 张按章筛选）· 🧪 [自测题库](p9-00-quiz.md)（19 章 × 3 题 + 15 道专题加练）

<a id="preface"></a>

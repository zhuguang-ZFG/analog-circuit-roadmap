# 视觉优先彻底改造 Implementation Plan

> **状态**：执行中（规格已 Accepted）。Wave 1 = Task 0–3 基础设施 + ch17 试点章手绘图波次；其余章节的批量生产待 ch17 接触表经用户确认后展开。

**Goal:** 把当前“文字为主、图作为补充”的教材改造成“图承担推理、文字负责精确补充”的视觉教材；使用 `yang0/handraw-style` 规划并生成静态视觉底图，以模块化 SVG 动画 V2 承担动态机理，最终在站点、离线书、PDF、视频和社媒五线保持一致。

**Current baseline:** 452,536 正文字符；54 静态分析图、32 照片、114 个正文内嵌动画实例；200 个正文视觉锚点；153 个独立 SVG；19/19 章最长无图段 >3000 字；旧生成器 9589 行。

**Exit:** ≥390 个正文视觉锚点、≥220 个独立动画、19/19 章最长无图段 ≤1500 字、所有视觉资产有 handraw-style 记录与事实来源、A4/16K/网页/无障碍全绿。

---

## Global Constraints

- `docs/*.md` 仍是唯一内容源。
- 当前未提交视频和 PDF 只作基线，不在本计划 Accepted 前推送。
- `handraw-style` 只参与视觉规划、风格/图型/色彩选择和视觉底图生成；公式、电路、中文标注与数值由确定性 SVG/HTML 绘制。
- 每张图先规划再生成，禁止批量“看标题出图”。
- 每个旧动画必须逐张审查，禁止全库统一换色冒充重做。
- 先三章试片，用户确认后才进入全书波次。
- 视觉增加必须伴随文字替换；不得只加图不减文。
- 新旧资产并存迁移，禁止一次性覆盖导致无法回滚。
- 不提交 handraw-style 外部仓库副本；项目只记录 URL、commit、选择结果、提示词与最终资产。
- 每个 Task 单独提交；发布前不 push，除非用户再次明确授权。

---

## Target File Structure

```text
docs/superpowers/visual/
  baseline-2026-11-04.json
  visual-manifest.yml
  animation-v2-manifest.yml
  handraw-style-lock.md
  quality-rubric.md
  chapter-backlog/
    ch00.yml ... ch18.yml
  prompts/
  reviews/
scripts/
  audit_visual_density.py
  check_visual_manifest.py
  build_visual_contact_sheet.py
  visuals/
    tokens.py
    primitives.py
    timeline.py
    layouts.py
    render.py
    scenes/
assets/
  figures-v2/
  svg-v2/
  storyboards-v2/
scripts/test_visual_density.py
scripts/test_visual_manifest.py
scripts/test_visual_distribution.py
scripts/test_animation_v2.py
scripts/test_visual_fidelity.py
scripts/test_print_storyboard_v2.py
scripts/test_visual_player.py
```

---

## Task 0: 冻结当前发布动作与保存基线

**Files:**
- Modify: `docs/superpowers/checklists/ship-gate.md`
- Create: `docs/superpowers/visual/baseline-2026-11-04.json`
- Create: `docs/superpowers/visual/quality-rubric.md`

- [ ] 在 ship-gate 文首标记“视觉彻底改造 Draft 期间不发布”。
- [ ] 记录当前 19 章字符、静态图、照片、内嵌动画、最长无图段。
- [ ] 记录当前 153 张 SVG 文件清单、SHA-256、正文引用数和打印分镜状态。
- [ ] 保存当前 A4 PDF、16K 双卷页数与文件尺寸，仅作对照，不入 Git。
- [ ] 写 35 分视觉质量量规：教学必要性、事实精度、构图层级、风格一致性、印刷可读性、运动叙事、交互节奏。

**Exit:** 基线可复现；后续每波能比较“增了什么、删了什么、文字减了多少”。

**Commit:** `docs: 冻结视觉改造基线与质量量规`

---

## Task 1: 锁定 handraw-style 工具链

**Files:**
- Create: `docs/superpowers/visual/handraw-style-lock.md`
- Create: `docs/superpowers/visual/prompts/README.md`
- Create: `scripts/test_handraw_prompt_records.py`

- [ ] 记录上游 `https://github.com/yang0/handraw-style` 与使用 commit `572dff8f8cc1dc16ff9bef1422e90b3dfc42284d`。
- [ ] 记录实际使用的 `styles.json`、`layouts.json`、`colors.json` 哈希。
- [ ] 说明本地上游全库校验当前因无关文件中的绝对路径泄漏失败；项目 CI 只校验被使用条目，不依赖上游全库通过。
- [ ] 定义 prompt 记录格式：原始主题、style_id、layout_id、color_ids、参考图策略、中文 prompt、英文 prompt、生成模型、输出文件。
- [ ] 写测试：任一 `figures-v2` 或动画关键帧没有 prompt 记录即失败。
- [ ] 不把用户机器绝对路径写进项目 prompt；参考图只记录上游相对路径与 commit。

**Exit:** handraw-style 的使用是可追溯、可升级、可复现的，不是“口头说用了”。

**Commit:** `chore: 锁定 handraw-style 版本与提示词记录契约`

---

## Task 2: 视觉密度审计器与永久闸

**Files:**
- Create: `scripts/audit_visual_density.py`
- Create: `scripts/test_visual_density.py`
- Create: `scripts/test_visual_distribution.py`
- Modify: `Makefile`

- [ ] 扫描 `docs/p*-ch*.md` 中实际内嵌的 figures/photos/svg-v2；链接不计数。
- [ ] 输出每章字符数、视觉类型数、每个 H2 的视觉覆盖、最长无图段和聚集位置。
- [ ] 视觉间距少于 400 字时报“堆图”；超过 1200 字警告，超过 1500 字失败。
- [ ] H2 正文超过 800 字无图直接失败。
- [ ] 写夹具测试，覆盖 HTML `<img>`、Markdown 图片、链接冒充图、代码块和公式块。
- [ ] 增加 `make visual-audit` 与 `make visual-ship`。

**Exit:** 旧树预期失败；三章试片后对应章节转绿；全书完成时 19/19 转绿。

**Commit:** `test: 视觉密度与章节分布永久闸`

---

## Task 3: Manifest、事实源与审图状态机

**Files:**
- Create: `docs/superpowers/visual/visual-manifest.yml`
- Create: `docs/superpowers/visual/animation-v2-manifest.yml`
- Create: `scripts/check_visual_manifest.py`
- Create: `scripts/test_visual_manifest.py`
- Create: `scripts/test_visual_fidelity.py`

- [ ] 定义静态资产字段：ID、章、锚点、类型、职责、style/layout/color、来源、prompt、输出、替代文本、状态、评分。
- [ ] 定义动画字段：上述字段 + 节拍、时长、参数、结论帧、reduced-motion、print fallback。
- [ ] 状态只允许 `planned → generated → reviewed → accepted → published`；禁止越级。
- [ ] 检查 docs 锚点与来源存在。
- [ ] 图中每个数字必须在 `source_facts` 的正文片段中找到，或标为示意。
- [ ] 旧 153 张动画先全部登记为 `legacy-unreviewed`。

**Exit:** 无 manifest 资产不能进入正文。

**Commit:** `feat: 视觉资产 manifest 与事实一致性闸`

---

## Task 4: 三章风格试片与用户确认

**Scope:** ch0、ch8、ch17。

**Files:**
- Create: `docs/superpowers/visual/chapter-backlog/ch00.yml`
- Create: `docs/superpowers/visual/chapter-backlog/ch08.yml`
- Create: `docs/superpowers/visual/chapter-backlog/ch17.yml`
- Create: `docs/superpowers/visual/reviews/pilot-contact-sheet.html`
- Create: `docs/superpowers/visual/reviews/pilot-decision.md`

- [ ] 用 article-illustration-planner 标出每章 12–20 个候选点位。
- [ ] 每个点位写清：要替代的文字、保留的公式/数字、图型 ID、图片类型。
- [ ] 从 handraw-style 全库动态推荐 3 套视觉方向；FA-029 只作为其中一套技术图候选。
- [ ] 每套各做 3 张代表图：现象主图、定量图、失效对比图。
- [ ] 关键文字和电路用 SVG overlay 重绘，不直接采用 AI 图中文字。
- [ ] 生成原版/候选 A/B/C 接触表，按 35 分量规打分。
- [ ] 用户选择主风格、辅助风格和色彩；未确认前停止批量生产。

**Exit:** 一份明确的 `pilot-decision.md`，锁定主视觉语言和允许的辅助语言。

**Commit:** `design: 三章视觉试片与 handraw 风格决策`

---

## Task 5: 静态插图生产管线

**Files:**
- Create: `scripts/build_visual_contact_sheet.py`
- Create: `scripts/compose_technical_overlay.py`
- Create: `assets/figures-v2/`
- Modify: `scripts/test_figures.py`

- [ ] 定义底图 + 技术 overlay 双层文件规范。
- [ ] overlay 负责：电路、公式、坐标、参数、中文标注和编号。
- [ ] 输出 1448×1086 或等比例 SVG/WebP；印刷有效宽度下最小正文 8.5pt。
- [ ] 保留纯 SVG 版本供印刷；站点可发布 WebP 预览。
- [ ] 检查画布内文字、对比度、字号、图片 alt、色盲可辨性。
- [ ] 自动生成每波接触表，人工一次看 12–24 张，不逐文件盲审。

**Exit:** 静态图能批量生产，但任何图仍必须逐项经过 manifest 与人工评分。

**Commit:** `feat: handraw 底图与技术 overlay 静态插图管线`

---

## Task 6: 动画生成器 V2 骨架

**Files:**
- Create: `scripts/visuals/tokens.py`
- Create: `scripts/visuals/primitives.py`
- Create: `scripts/visuals/timeline.py`
- Create: `scripts/visuals/layouts.py`
- Create: `scripts/visuals/render.py`
- Create: `scripts/visuals/scenes/`
- Create: `scripts/test_animation_v2.py`
- Create: `assets/svg-v2/`

- [ ] 从旧 9589 行生成器抽出 token、图元、时间轴、布局和输出层。
- [ ] 场景文件按章拆分；单文件建议不超过 500 行。
- [ ] 时间轴使用命名 beat，不直接散写 keyTimes。
- [ ] 内置 ease-in-out、progressive reveal、focus、camera、parameter sweep、conclusion hold。
- [ ] 默认只播放一次；结论帧停留。
- [ ] 自动生成 reduced-motion 版本和 3–5 格打印分镜。
- [ ] 先移植 3 个代表动画：电流流动、公式推导、参数扫描。
- [ ] V2 与旧动画可同时存在，manifest 决定正文引用。

**Exit:** 三类动画在同一框架下可复用，但画面不再同模板同节奏。

**Commit:** `feat: 模块化 SVG 动画 V2 引擎`

---

## Task 7: 网页动画播放器

**Files:**
- Create: `scripts/site_media/visual-player.js`
- Modify: `scripts/site_media/learning.js`
- Modify: `scripts/build_site.py`
- Create: `scripts/test_visual_player.py`
- Modify: `scripts/test_reduced_motion.py`

- [ ] 构建时把带 `data-visual-player` 的动画转成播放器外壳。
- [ ] 支持播放、暂停、重播、0.5×/1×/1.5×、节拍跳转。
- [ ] 显示当前节拍名称和总进度。
- [ ] 键盘可操作，按钮有 aria-label，焦点顺序正确。
- [ ] reduced-motion 默认显示结论关键帧。
- [ ] 无 JS 保留静态图、图注和动画中心链接。
- [ ] 移动端不遮正文，不自动无限循环。

**Exit:** 动画变成可控演示，不再只是页面里自动闪动的 GIF 替代品。

**Commit:** `feat: 章节动画播放器与减弱动效回退`

---

## Task 8: 三章试点正文改造

**Files:**
- Modify: `docs/p1-01-ch0.md`
- Modify: `docs/p1-09-ch8.md`
- Modify: `docs/p4-02-ch17.md`
- Create/Modify: 对应 `assets/figures-v2/`、`assets/svg-v2/`、storyboards、prompts、manifest

- [ ] ch0 从 8 个视觉锚点提升到 ≥18，最长无图段 ≤1200。
- [ ] ch8 从 12 提升到 ≥32，覆盖模拟开关、采样保持、注入、时钟馈通、失效边界。
- [ ] ch17 从 4 提升到 ≥18，把 15308 字断层拆成症状图、测点图、决策树、逼现流程和回归闭环。
- [ ] 每章至少 6 张静态图、4 个 V2 动画。
- [ ] 删除被图替代的重复文字，章字符数下降 10%–25%。
- [ ] 逐图跑 35 分量规；任一维度 <4 返工。
- [ ] 重建站点、离线书和试点 PDF，人工翻页。

**Exit:** 用户确认“这才是要的书籍质量”。未确认则回 Task 4，不得扩到全书。

**Commit:** `content: ch0 ch8 ch17 视觉优先试点改造`

---

## Task 9: 高断层章节波次

**Scope:** ch18、ch15、ch16、ch10、ch2。

- [ ] 每章先出 backlog，再生成资产。
- [ ] 每章达到 spec 预算，最长无图段 ≤1500。
- [ ] 优先替代：长列表、连续定义、排故文字链、设计步骤和失效边界。
- [ ] 每章完成后单独跑视觉审计、链接、事实一致性和打印分镜。
- [ ] 每章单独提交，便于回滚。

**Commits:** `content: chN 视觉优先改造（图替繁文+动画V2）`

---

## Task 10: 其余章节全覆盖

**Scope:** ch1、ch3–ch7、ch9、ch11–ch14。

- [ ] 按每章预算补齐静态图和动画。
- [ ] 确保每个 >800 字 H2 有视觉锚点。
- [ ] 复用视觉图型但不复制内容构图；同一篇连续三图不得同布局。
- [ ] 每章字符数、视觉数和删改段落写进波次报告。
- [ ] 每章独立提交。

**Exit:** 19/19 章密度闸全绿。

---

## Task 11: 153 张旧动画逐张处置 + 扩到 220

**Files:**
- Modify: `docs/superpowers/visual/animation-v2-manifest.yml`
- Modify/Create: `assets/svg-v2/`
- Modify: `docs/p5-00-part5.md`
- Modify: 19 章动画入口

- [ ] 为 153 张旧动画逐张标记 Rebuild / Retire / Keep after review。
- [ ] Keep 必须重新过 35 分量规，不允许默认通过。
- [ ] 重复主题合并，正文入口指向最强版本。
- [ ] 新增不足的 A1–A5 类型，独立动画总数 ≥220。
- [ ] 每章至少 6 个高价值动画或动态演示；设计/排故章可用操作动画替代纯机理动画。
- [ ] 动画中心按章、类型、难度和失效边界重新筛选。
- [ ] 旧链接保留映射或明确重定向。

**Exit:** 220 是经过审查的动画，不是 220 个模板复制品。

**Commit:** `feat: 动画库 V2 全量重审与扩容`

---

## Task 12: 文字瘦身与图文职责审计

**Files:**
- Modify: 19 章 docs
- Create: `scripts/test_visual_text_replacement.py`

- [ ] 每张标为 `replaces-text` 的图必须有被删段落记录与精炼导读。
- [ ] 检测图注是否复制正文完整句子。
- [ ] 检测同一公式是否在相邻正文、图注、字幕三次重复。
- [ ] 保留公式、量化判据、典型值/保证值区分和来源。
- [ ] 全书正文字符原则上下降 10%–20%，不能靠删知识点完成。
- [ ] 人工抽检每章首、中、尾三段，防止“前密后空”。

**Exit:** 图真正替代文字，而不是让书更厚。

**Commit:** `edit: 全书图替繁文与重复说明瘦身`

---

## Task 13: 印刷、离线与 PDF

**Files:**
- Modify: `analog-book/book/storyboard.py`
- Modify: `analog-book/styles/print.css`
- Modify: `analog-book/tests/test_storyboard.py`
- Create: `scripts/test_print_storyboard_v2.py`

- [ ] V2 动画自动出 3–5 格关键帧分镜。
- [ ] 静态图在 16K 有效版心内文字 ≥8.5pt。
- [ ] 长图避免整图缩小；必要时拆上下半页。
- [ ] A4、16K 双卷重建；每卷 ≤700 页。
- [ ] 灰度打印仍能区分正常/异常、输入/输出、前/后状态。
- [ ] 随机抽 50 张图检查断页、裁切、字号和图注对应。
- [ ] 生成最终本地 PDF，保存路径和 SHA-256。

**Exit:** PDF 人工翻阅签字，不以“构建成功”代替质量确认。

**Commit:** `build: 视觉 V2 印刷分镜与 PDF 适配`

---

## Task 14: 视频与社媒同源派生

**Files:**
- Modify: `video/shots/*.json`
- Modify: `video/remotion/src/`
- Modify: 社媒模板与样例

- [ ] 视频主视觉引用 accepted 的 V2 资产，不再单独设计另一套图。
- [ ] 章节动画节拍可转换为视频分镜，但视频允许重新剪辑时长。
- [ ] 社媒卡只抽取教材结论，不新增数字。
- [ ] handraw-style 的风格/layout/color 记录沿用教材 manifest。
- [ ] 现有 40 个成片先作为旧基线；视觉改造完成后再决定重渲范围。

**Exit:** 教材、动画、视频和社媒看起来属于同一个产品。

**Commit:** `feat: 视觉 V2 五线同源派生`

---

## Task 15: 全量质量门禁与发布

**Files:**
- Modify: `Makefile`
- Modify: `.github/workflows/tests.yml`
- Modify: `.github/workflows/book.yml`
- Modify: `docs/superpowers/checklists/ship-gate.md`

- [ ] `make visual-ship` 聚合密度、manifest、事实、动画、播放器、印刷和人工评分闸。
- [ ] 19/19 章最长无图段 ≤1500。
- [ ] 视觉锚点 ≥390；动画 ≥220。
- [ ] 153 张旧动画处置率 100%。
- [ ] 静态图/动画无缺 prompt、无缺来源、无缺 print fallback。
- [ ] 跑站点静态/浏览器测试、书测试、PDF 结构、Remotion 冒烟。
- [ ] 生成 A4 与 16K 本地 PDF，人工确认。
- [ ] 用户确认三章试片和最终 PDF。
- [ ] 清理临时文件，只暂存 manifest 允许的产物。
- [ ] 分任务提交；最后经用户明确授权再 push。
- [ ] 监控 GitHub Actions 至 tests、links、book、book-print、pages 全绿。

**Final commit:** `release: 视觉优先彻底改造完成`

---

## Recommended Execution Order

```text
Task 0–3  基线、工具锁、审计、manifest
    ↓
Task 4    三章风格试片
    ↓ 用户确认
Task 5–7  静态管线、动画 V2、播放器
    ↓
Task 8    ch0/ch8/ch17 完整试点
    ↓ 用户确认
Task 9–10 全书波次
    ↓
Task 11–12 动画全审 + 文字瘦身
    ↓
Task 13–14 印刷与五线派生
    ↓
Task 15   全闸、PDF、提交、推送、CI
```

---

## Plan Review Checklist

- [x] 量化了“图少”和“分布差”，没有只写审美口号
- [x] 同时覆盖静态图数量、动画数量和两者质量
- [x] 153 张旧动画全部进入逐张处置，不默认保留
- [x] handraw-style 有版本锁、ID、prompt 和参考图隔离规则
- [x] 公式、电路、中文不交给生图模型猜
- [x] 先三章试片、两次用户确认，再批量生产
- [x] 图替繁文，禁止只加图不减文
- [x] 网页、无障碍、打印、PDF、视频和社媒全部纳入
- [x] 最终提交推送仍需用户明确授权

---

*计划到此为止；未 Accepted 前不执行批量视觉生产。*

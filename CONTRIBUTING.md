# 参与共建 🤝

本指南是开放知识库，欢迎一切形式的贡献。

## 你可以贡献什么

| 类型 | 举例 | 渠道 |
|---|---|---|
| 🐛 纠错 | 公式错误、参数过时、链接失效（附 datasheet 页码最佳） | Issue |
| 🔧 故障案例 | 你的真实翻车现场——症状/根因/解法三要素 | PR 或 Issue |
| 📺 资源 | 高质量视频/论文/应用笔记（注明为什么好） | PR |
| 🎬 动画 | 新主题 SVG 动画（见下方铁律） | PR |
| ✍️ 章节 | 新器件/新拓扑深度解析（遵循统一结构） | PR |
| 🧪 题目 | 自测题库新增好题（含答案与解析） | PR |

> 📮 **不想写代码？两条最快的路**：
> 1. **提 Issue**——[纠错](https://github.com/zhuguang-ZFG/analog-circuit-roadmap/issues/new?template=content-fix.yml)（错别字 / 公式 / 事实 / 失效链接）
>    或 [建议](https://github.com/zhuguang-ZFG/analog-circuit-roadmap/issues/new?template=new-topic.yml)（新增主题 / 动画 / 资源）。
>    模板已把"位置 / 问题类型 / 依据"列好，填完即可，不需要懂 Git。
> 2. **在线站每页右上角有 ✎「编辑此页」**，直接跳到该页对应的 `docs/xxx.md` 开 PR；
>    页面底部还有「参与共建」快捷入口。发现一处错字，30 秒就能改完。

## 仓库铁律（PR 前自查）

0. **`docs/` 是唯一数据源，不要直接改 `README.md`**——README 由 `scripts/build_readme.py` 从 `docs/` 拼出，改完必须重跑（CI 会比对，漂移即红灯）
1. **`assets/svg/` 内文件必须 == `scripts/generate_svgs.py` 的输出**——改图先改脚本，再 `python3 generate_svgs.py` 重跑，绝不允许只改 SVG 文件不回灌脚本
2. **外链必须可达**：提交前自行 HTTP 验证；CI（lychee）会对 README.md 全量外链做检查，红灯的 PR 无法合并
3. **实物图仅用公有领域 / CC 授权**（Wikimedia Commons 优先），并在图注注明来源
4. **统一结构**：新器件章遵循「物理原理 → 数学模型 → 内部电路 → 关键参数 → 典型应用 → 故障模式 → 动态分析 → 配套视频」
5. **文风**：说人话、给数量级、每图配"💎 精髓"或"怎么看"段——参考现有章节
6. **跨页跳转用锚点**：`docs/` 是多页站点，`#ch3` 这类锚点要写成 `p1-04-ch3.md#ch3`（拼回 README 时脚本会自动还原成 `#ch3`）

## 三种产物，一条流水线

| 产物 | 生成命令 | 说明 |
|---|---|---|
| `README.md` | `python scripts/build_readme.py` | 单文件版，给 GitHub 阅读 |
| `build/docs/` + `build/mkdocs.yml` | `python scripts/build_site.py` | 站点源：内容页 + 动画画廊 + 主题配置 |
| `build/site/`（在线站） | `python scripts/build_site.py --build` | MkDocs Material 静态站，`main` 推送后自动部署 Pages |

新增一个章节 = 在 `docs/` 里加一个 `pN-MM-slug.md`（文件名前缀决定它在目录与侧栏里的位置），
然后跑一次 `build_readme.py`；导航与动画卡片由脚本自动生成，无需手工维护索引。
初次切分可复用 `python scripts/split_readme.py`（会把 README 拆成 docs 并改写锚点链接）。

## 本地检查

在仓库根目录运行（四项检查与 CI 完全一致）：

```bash
python -B -m unittest discover -s scripts -p 'test_docs_sync.py'    # docs → README 可 1:1 重建
python -B -m unittest discover -s scripts -p 'test_docs_links.py'   # 跨页锚点 / SVG 引用 / 标题
python -B -m unittest discover -s scripts -p 'test_readme_links.py' # README 锚点完整性
python -B -m unittest discover -s scripts -p 'test_svg_assets.py'   # SVG 与生成器逐字节一致
```

`test_svg_assets.py` 使用生成器已有的 NumPy 依赖，在临时目录执行生成器，检查 SVG 文件集合、内容一致性和 XML 格式；不会覆盖仓库产物，忽略跨平台 LF/CRLF 差异。`test_waveform_timing.py` 需要 Playwright 和已安装的 Google Chrome，检查五张时间轴图（模拟开关、LDO、555、整流滤波、MOSFET 四拍）的时间轴、跳变、循环与圆点同步，以及 7 站点（comparator/wien/integrator/LDO/miller/peak/neg-feedback）的 x-匀速配速（delta=0.6px）。

这组测试已在 CI 中强制执行：`.github/workflows/tests.yml` 在每次推送和 PR 上运行 SVG 一致性检查（NumPy）、docs 单一数据源校验、站点可构建性与 Chromium 时间轴回归；`.github/workflows/links.yml` 用 lychee 巡检全量外链；`.github/workflows/pages.yml` 在 `main` 推送后部署 GitHub Pages。

使用 OMP 的 `task_verify` 时，从本仓库根目录启动会话。检查命令由本机 `task-verification-policy.json` 登记；新增或修改测试、检查参数和策略后，须审核并在下一用户轮建立基线。干净且本轮未修改的仓库返回 `not-required`，不表示测试已执行。

## 站点体验（`build_site.py` 生成，改这里就改全站）

| 能力 | 实现位置 | 说明 |
|---|---|---|
| 🎬 动画画廊 + 放大播放 | `gallery.md` / `gallery.js` / `gallery.css` | 102 张卡片，按章筛选 + 关键字搜索；「▶ 放大播放」弹窗全尺寸观看（SMIL 自动播放，Esc 关闭） |
| ✎ 编辑此页 | `mkdocs.yml` 的 `edit_uri` | 每页右上角直达 `docs/` 里对应的 Markdown |
| ✍️ 参与共建页脚 | `FEEDBACK_FOOTER` 常量 | 每页底部追加纠错 / 建议 / 共建指南入口（只加在站点产物，`docs/` 保持干净） |
| 🔎 SEO | `OVERRIDES_MAIN_HTML` + `ROBOTS_TXT` | og/twitter 社交卡片 meta、`robots.txt`；`sitemap.xml` 由 MkDocs 依 `site_url` 自动生成 |
| 📮 Issue 模板 | `.github/ISSUE_TEMPLATE/*.yml` | 纠错 / 建议两张表单 + 联系入口；PR 模板见 `.github/pull_request_template.md` |

> 💬 **评论区（可选）**：本站预留了 giscus（GitHub Discussions 评论）的接入位置。
> 仓库 ID 为 `R_kgDOU8y93w`。若要开启：① 在仓库 Settings 打开 Discussions 并建一个
> `Announcements` 分类；② 在 <https://giscus.app> 授权 giscus App 并取得 `data-category-id`；
> ③ 在 `scripts/build_site.py` 的 `FEEDBACK_FOOTER` 后追加 giscus 的 `<script>` 片段并重跑生成脚本。
> 未安装 giscus App 时不要打开，否则页面上会出现报错的空评论框。

## 流程

Fork → 特性分支 → 提交（commit message 中英文皆可，说明 why）→ PR。
文档许可 CC BY-SA 4.0，贡献即表示同意按此许可发布。

# handraw-style 工具链锁定

- **上游**：https://github.com/yang0/handraw-style
- **锁定提交**：`572dff8f8cc1dc16ff9bef1422e90b3dfc42284d`（v1.9.8）
- **本地安装形态**：以 skill 包安装（含 `images/` 画廊与编号参考图）。安装根
  因机器而异，**项目文件与 CI 一律不写绝对路径**；需要核对时在安装根执行：

  ```bash
  git rev-parse HEAD          # 必须等于上面的锁定提交
  ls references               # styles.json / layouts.json / colors.json
  ```

  2026-11-04 验证：本地安装根 HEAD = `572dff8`，与锁定一致。
- **权威数据**：`styles_200_reorganized.md`（367 风格）、
  `skills/handdraw-style-prompter/references/layouts.json`（170 图型）、
  `references/colors.json`（36 主题色）。`*.json` 是生成索引，升级上游后
  须重跑上游 `build_library.py` / `build_layout_gallery.py` / `build_color_gallery.py`。
- **全库校验边界**：上游完整校验含与本项目无关的绝对路径条目，不作为 CI
  前提；本项目只校验**实际使用的条目存在**（见下）。

## 已使用的条目

| 类别 | ID | 用途 |
|---|---|---|
| 风格 | FA-029 Geometric Diagrammatic Narrative | 技术图主风格候选（线条＋几何叙事） |
| 图型 | IG-002 / IG-004 / IG-008 / IG-009 / IG-011 / IG-012 / IG-014 / IG-015 / IG-019 / IG-024 / IG-026 / IG-027 / IG-028 / IG-032 / IG-033 | 按信息结构选择，见规格 §5.3 |
| 色彩 | C-30 象牙白（纸） / C-31 佩恩灰（墨） / C-29 赭石（重点） | 全书基础纸墨 |

每一项视觉资产在 `visual-manifest.yml` 登记 `style_id` / `layout_id` /
`color_ids`；新增 ID 必须先确认存在于上游索引，禁止发明。

## 底图与生成边界（本项目实测约束）

本环境**没有可调用的生图模型**，且规格 §3.3 硬规则要求公式、器件参数、
引脚名、波形坐标与中文正文由确定性 SVG/HTML 图层绘制。因此当前生产路径是
**确定性手绘风 SVG**（`scripts/visuals/static_fig.py` 皮肤 + 手工底稿）：

- 风格参考只影响线条、媒介、质感和色彩，不进入 AI 生成中文；
- 每条 prompt 记录仍按上游双语提示词格式落盘（`prompts/<id>.md`），
  将来接入生图模型时可直接作为底图提示词复用；
- 上游的「底图 + 技术 overlay」双层管线（计划里的 `assets/figures-v2/`）
  在有生图模型后启用；当前新图**直接落 `assets/figures/`**，理由：
  `analog-book/book/fonts.py` 只对 `assets/svg` 与 `assets/figures` 做
  缺字子集，`scripts/test_figures.py` 的离线/越界/图注闸也只扫描
  `assets/figures`。落别处会绕过字形子集与全部既有闸。

## 提示词记录契约

`docs/superpowers/visual/prompts/<id>.md`，YAML front matter：

```yaml
---
id: ch17-cause-frequency
generator: deterministic-svg-v1   # 或外部模型名（接入生图后）
reference_policy: none            # none | upstream-relative-path
numbers: ["41%", "23%", "18%", "9%", "6%", "3%"]
zh_prompt: |
  风格名称：几何图式叙事。主题色：象牙白（Ivory）。
  ……画面主题与必须出现的数值……
en_prompt: |
  Style name: Geometric Diagrammatic Narrative. Theme color: Ivory.
  ……
---
```

硬规则（`scripts/check_visual_manifest.py` 强制）：

- `numbers` 里的每个字符串必须能在 `source_facts` 指向的正文文件中找到；
- 上游相对图路（参考图）只允许记录相对路径与锁定提交，不允许绝对路径；
- 无 prompt 记录的资产不得进入正文。

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

## 仓库铁律（PR 前自查）

1. **`assets/svg/` 内文件必须 == `scripts/generate_svgs.py` 的输出**——改图先改脚本，再 `python3 generate_svgs.py` 重跑，绝不允许只改 SVG 文件不回灌脚本
2. **外链必须可达**：提交前自行 HTTP 验证；CI（lychee）会对 README.md 全量外链做检查，红灯的 PR 无法合并
3. **实物图仅用公有领域 / CC 授权**（Wikimedia Commons 优先），并在图注注明来源
4. **统一结构**：新器件章遵循「物理原理 → 数学模型 → 内部电路 → 关键参数 → 典型应用 → 故障模式 → 动态分析 → 配套视频」
5. **文风**：说人话、给数量级、每图配"💎 精髓"或"怎么看"段——参考现有章节

## 本地检查

在仓库根目录运行：

```bash
python -B -m unittest discover -s scripts -p 'test_*.py' -v
```

`test_svg_assets.py` 使用生成器已有的 NumPy 依赖，在临时目录执行生成器，检查 SVG 文件集合、内容一致性和 XML 格式；不会覆盖仓库产物，忽略跨平台 LF/CRLF 差异。`test_waveform_timing.py` 需要 Playwright 和已安装的 Google Chrome，检查五张时间轴图（模拟开关、LDO、555、整流滤波、MOSFET 四拍）的时间轴、跳变、循环与圆点同步。

这组测试已在 CI 中强制执行：`.github/workflows/tests.yml` 在每次推送和 PR 上运行 SVG 一致性检查（NumPy）与 Chromium 时间轴回归。

使用 OMP 的 `task_verify` 时，从本仓库根目录启动会话。检查命令由本机 `task-verification-policy.json` 登记；新增或修改测试、检查参数和策略后，须审核并在下一用户轮建立基线。干净且本轮未修改的仓库返回 `not-required`，不表示测试已执行。

## 流程

Fork → 特性分支 → 提交（commit message 中英文皆可，说明 why）→ PR。
文档许可 CC BY-SA 4.0，贡献即表示同意按此许可发布。

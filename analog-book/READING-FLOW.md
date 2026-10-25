# 离线整书阅读流更新说明

- 日期：2026-10-25
- 适用产物：`dist/analog-circuit-book.html`、`dist/analog-circuit-book.pdf`
- 对应提交：`b730b23`（feat(book): 页尾连续翻页与正文链接样式）

## 1. 这次解决的阅读断点

此前每页末尾只有“↑ 返回目录”。读者读完一章想接着读下一章，必须先回到目录再找下一页，手机上尤其割裂。

这次把翻页动作放到每页末尾，并补齐正文链接与键盘可读性，让离线书更接近一本可以顺着读下去的书，而不是一组需要反复导航的网页。

## 2. 页尾连续翻页

每页正文结束后新增：

```text
← 上一篇   第一篇：器件深度原理解析          全书目录          第 1 章 无源元件的真实面目   下一篇 →
```

- **连续阅读**：上一篇 / 下一篇按整书顺序连接，不按“篇”重置。
- **跨篇不断流**：例如第一篇导读的上一篇接续前言篇的最后一页。
- **边界正确**：全书 60 页共 59 组 `prev` / `next`；前言没有上一篇，末尾来源页没有下一篇。
- **手机布局**：左右翻页并排，目录按钮单独居中换行；长标题省略显示，不挤压操作区。
- **屏幕阅读器**：使用 `nav[aria-label="翻页"]`，链接带 `rel="prev"` / `rel="next"`。
- **打印安全**：页尾导航只在屏幕显示，PDF 中不出现。

## 3. 正文链接与阅读样式

- 正文链接补上暖色下划线，悬停时加深；不再只靠颜色区分链接。
- 章末学习导航按钮保持无下划线，避免把按钮误读成正文链接。
- 全站补齐 `:focus-visible` 焦点环，键盘 `Tab` 浏览时有清晰落点。
- 文本选中改为浅暖色底，保持正文墨色对比。
- 打印样式继续让正文链接继承文字色，PDF 不因下划线产生额外视觉噪声。

## 4. 键盘与既有阅读能力

本轮不改变既有交互，仍可使用：

- `Ctrl/Cmd + K` 或 `/` 聚焦全文搜索；
- 方向键选择搜索结果，回车跳转；
- `Tab` 首先到达“跳到目录”；
- 页眉阅读进度条；
- 屏幕右下角回到顶部。

## 5. 验收记录

| 检查 | 结果 |
|---|---|
| 整书单元与结构测试 | 24 项通过 |
| 浏览器离线回归（MathJax、搜索、页尾翻页、进度、回顶） | 通过 |
| PDF 结构（书签、页码、正文 10.5pt、目录点线） | 通过，453 页 |
| PDF 页尾导航泄漏检查 | 未发现“上一篇 / 下一篇”文本 |
| GitHub Actions | [40149061618](https://github.com/zhuguang-ZFG/analog-circuit-roadmap/actions/runs/40149061618) 全绿并部署成功 |

浏览器回归会实际点击“下一篇”进入下一章，再点击“上一篇”返回，确认 URL hash 与滚动位置都正确。

## 6. 发布与国内镜像

- GitHub Pages：<https://zhuguang-zfg.github.io/analog-circuit-roadmap/book/>
- 国内镜像：<https://aliyun-hutuji.donglicao.com/analog-circuit-roadmap/book/>

2026-10-25 09:17（CST）已将最新 `index.html`、`analog-circuit-book.html`、`analog-circuit-book.pdf`、`og-cover.png` 同步到国内镜像，并在覆盖前备份旧书目录。

镜像校验：

- 书页 HTML 为最新构建，包含 60 个页尾导航、59 组上一页/下一页；
- PDF 可下载，大小 43,774,071 字节；
- `book/og-cover.png` 返回 `200 image/png`，尺寸 1200×630。

### `og-cover.png` 404 的根因与修复

镜像同步脚本用 `wget` 递归抓站内链接，但分享图只写在 `<meta property="og:image">` 里，爬虫不会把它当作可下载链接；固定补抓清单也只列了站点根部的 `assets/og-cover.png`，漏了 `/book/og-cover.png`。

已修复 VPS 上的 `/opt/analog-book/sync.sh`：固定补抓清单加入 `book/og-cover.png`，同时显式补抓书目录的三个入口文件，避免依赖递归发现。修改前的脚本已备份到 `/opt/analog-book/backups/`。cron 仍为每 6 小时一次。

## 7. 维护约定

- 新增或删除内容页只需改 `manifest.json`；页尾翻页由构建器按整书顺序自动生成，不需要手工维护相邻关系。
- 修改 `styles/book.css` 时，打印样式区要同步确认 `.book-page-nav` 仍在隐藏列表里。
- 更换分享图时，要同时确认 `scripts/publish_book.py` 会把图复制到 `book/`，并确认镜像脚本的固定补抓清单仍包含 `book/og-cover.png`。
- 构建与测试命令见 [`README.md`](README.md)；设计背景见 [`../docs/superpowers/specs/2026-10-24-offline-book-and-repo-polish-design.md`](../docs/superpowers/specs/2026-10-24-offline-book-and-repo-polish-design.md)。

## 8. 相关文件

- `build_book.py`：页尾导航生成、前后页顺序、PDF 隐藏规则接线
- `styles/book.css`：翻页布局、链接下划线、焦点与选区、移动端与打印样式
- `tests/test_build.py`：60 页导航、59 组前后链、首末页边界、打印隐藏
- `tests/test_browser_book.py`：下一页 / 上一页真实点击与滚动验证

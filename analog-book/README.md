# 离线整书

从 `docs/` 构建《通往模拟电路之路》的单文件 HTML 与 A4 PDF。内容源仍在 `docs/`，本目录只放构建器、清单与样式。

## 构建

在仓库根目录运行：

```bash
pip install -r requirements.txt -r analog-book/requirements.txt
python -m playwright install chromium   # 也可复用本机 Edge / Chrome
python analog-book/build_book.py        # 站点 + HTML
python analog-book/build_book.py --pdf  # 追加 PDF
python analog-book/build_book.py --check --no-build  # 只审计已有产物
```

Windows 上装了 GNU Make 时可用 `make book` / `make book-pdf` / `make book-check`；本仓库用 `mingw32-make` 验证。

- 默认调用 `scripts/build_site.py --build`；`--no-build` 复用 `build/site`。自定义 `--site-dir` 只能配合 `--no-build`。
- 产物在 `analog-book/dist/`（gitignored）：`analog-circuit-book.html`、`analog-circuit-book.pdf`。
- 新增/删除内容页必须同步 `manifest.json`，否则整书审计失败。
- 书内禁止远程图片、外链样式/脚本、iframe/video；第三方资产先本地化并登记 `docs/p9-14-credits.md`。
- 页眉内置离线全文搜索：`Ctrl/Cmd+K` 或 `/` 聚焦，方向键选择、回车跳转；索引在首次输入时从正文构建，不增加网络依赖。
- Mermaid 路线图使用 `static/roadmap.svg`；改 `docs/p0-06-roadmap.md` 后必须重新生成 `roadmap.source.txt` / `roadmap.svg`。
- 缺 Playwright/PyMuPDF 时 HTML 仍可构建；PDF 相关测试自动 skip。
- PDF 默认优先本机 Edge/Chrome，找不到时回退 Playwright 自带 Chromium；可用 `--browser <path>` 指定浏览器。
- 审计会检查远程资源、重复 ID、跨页锚点、页面数与 20 MB 体积上限；`--check` 不重新构建。

## 测试

```bash
python -B -m unittest discover -s analog-book/tests -p test_build.py -v
python -B -m unittest discover -s analog-book/tests -p test_browser_book.py -v
python -B -m unittest discover -s analog-book/tests -p test_pdf.py -v
```

`test_browser_book.py` 需要 Playwright 与可用的 Chromium/Chrome；`test_pdf.py` 需要先生成 PDF 和 PyMuPDF。

设计说明见 [`../docs/superpowers/specs/2026-10-24-offline-book-and-repo-polish-design.md`](../docs/superpowers/specs/2026-10-24-offline-book-and-repo-polish-design.md)，实施计划见 [`../docs/superpowers/plans/2026-10-24-offline-book-and-repo-polish.md`](../docs/superpowers/plans/2026-10-24-offline-book-and-repo-polish.md)。

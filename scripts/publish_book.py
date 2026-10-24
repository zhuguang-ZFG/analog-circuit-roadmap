#!/usr/bin/env python3
"""Copy the built offline book into the Pages site tree."""
import argparse
import html
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_HTML = ROOT / "analog-book" / "dist" / "analog-circuit-book.html"
DEFAULT_PDF = ROOT / "analog-book" / "dist" / "analog-circuit-book.pdf"
DEFAULT_SITE = ROOT / "build" / "site"
BOOK_DIR_NAME = "book"


def _meta(document: str, name: str) -> str:
    match = re.search(
        r'<meta name="%s" content="([^"]*)"' % re.escape(name), document)
    return html.unescape(match.group(1)) if match else ""


def _human_size(size: int) -> str:
    if size >= 1024 * 1024:
        return "%.1f MB" % (size / (1024 * 1024))
    return "%d KB" % max(1, round(size / 1024))


def _landing(version: str, date: str, html_name: str, pdf_name: str,
             html_size: int, pdf_size: int) -> str:
    meta = " · ".join(part for part in (
        ("版本 " + version) if version else "", date) if part)
    meta_html = f'<p class="meta">{html.escape(meta)}</p>' if meta else ""
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light dark">
<title>离线整书 · 通往模拟电路之路</title>
<style>
:root {{ color-scheme: light dark; }}
* {{ box-sizing: border-box; }}
body {{
  margin: 0; background: #fffdf8; color: #1f2933; line-height: 1.7;
  font-family: -apple-system, "Segoe UI", "PingFang SC", "Microsoft YaHei",
    "Noto Sans CJK SC", sans-serif;
}}
main {{ max-width: 720px; margin: 0 auto; padding: 12vh 24px 64px; }}
.kicker {{ margin: 0 0 8px; color: #b45309; font-size: 14px; letter-spacing: .08em; }}
h1 {{ margin: 0 0 12px; font-size: clamp(2.2rem, 7vw, 3.4rem); line-height: 1.1; }}
.meta {{ margin: 0 0 20px; color: #52606d; font-size: 14px; }}
.formats {{ list-style: none; margin: 28px 0; padding: 0; display: grid; gap: 12px; }}
.formats a {{
  display: flex; justify-content: space-between; gap: 16px;
  padding: 16px 18px; border: 1px solid #d9e2ec; border-radius: 10px;
  background: #fff; color: #b45309; text-decoration: none; font-weight: 600;
}}
.formats a:hover {{ border-color: #b45309; }}
.formats span {{ color: #52606d; font-weight: 400; font-variant-numeric: tabular-nums; }}
.note {{ color: #52606d; font-size: 14px; }}
.back {{ margin-top: 36px; }}
.back a {{ color: #b45309; }}
@media (prefers-color-scheme: dark) {{
  body {{ background: #14181d; color: #e8edf2; }}
  .meta, .note, .formats span {{ color: #9aa7b4; }}
  .formats a {{ background: #1d232b; border-color: #323c47; color: #f0c38a; }}
  .kicker, .back a {{ color: #f0c38a; }}
}}
</style>
</head>
<body>
<main>
<p class="kicker">通往模拟电路之路</p>
<h1>离线整书</h1>
{meta_html}
<p>单文件 HTML 适合浏览器离线阅读；A4 PDF 带书签、页眉与印刷页码。</p>
<ul class="formats">
<li><a href="{html.escape(html_name)}"><strong>单文件 HTML</strong><span>{_human_size(html_size)}</span></a></li>
<li><a href="{html.escape(pdf_name)}"><strong>A4 PDF</strong><span>{_human_size(pdf_size)}</span></a></li>
</ul>
<p class="note">每次 main 分支构建自动更新。</p>
<p class="back"><a href="../index.html">返回在线站</a></p>
</main>
</body>
</html>
"""


def publish(html_path: Path, pdf_path: Path, site_dir: Path) -> Path:
    for path in (html_path, pdf_path):
        if not path.is_file() or path.stat().st_size == 0:
            raise FileNotFoundError(f"整书产物不存在或为空: {path}")
    if not (site_dir / "index.html").is_file():
        raise FileNotFoundError(f"站点产物不存在，请先构建站点: {site_dir}")
    target = site_dir / BOOK_DIR_NAME
    target.mkdir(parents=True, exist_ok=True)
    shutil.copy2(html_path, target / html_path.name)
    shutil.copy2(pdf_path, target / pdf_path.name)
    version = _meta(html_path.read_text(encoding="utf-8"), "book-version")
    date = _meta(html_path.read_text(encoding="utf-8"), "book-date")
    (target / "index.html").write_text(
        _landing(version, date, html_path.name, pdf_path.name,
                 html_path.stat().st_size, pdf_path.stat().st_size),
        encoding="utf-8", newline="\n")
    return target


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--html", type=Path, default=DEFAULT_HTML)
    parser.add_argument("--pdf", type=Path, default=DEFAULT_PDF)
    parser.add_argument("--site-dir", type=Path, default=DEFAULT_SITE)
    args = parser.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    try:
        target = publish(args.html, args.pdf, args.site_dir)
    except FileNotFoundError as exc:
        print(f"publish error: {exc}", file=sys.stderr)
        return 1
    print(f"published {target} ({args.html.name}, {args.pdf.name})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

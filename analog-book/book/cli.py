"""16K 整书构建入口：HTML、审计、PDF 与印刷封面。"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import config
from .assemble import build_html, check_html
from .cover import build_cover, inspect_cover
from .manifest import BookError, load_manifest, validate_manifest
from .pdf import build_pdf, check_pdf
from .report import write_report
from .sample import build_sample


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path, default=config.DIST_DIR)
    parser.add_argument("--site-dir", type=Path, default=config.SITE_DIR)
    parser.add_argument("--no-build", action="store_true", help="复用已有站点产物")
    parser.add_argument("--check", action="store_true", help="只审计已有整书")
    parser.add_argument("--pdf", action="store_true", help="生成 16K 内文 PDF")
    parser.add_argument("--cover", action="store_true", help="生成印刷封面（隐含 --pdf）")
    parser.add_argument("--report", action="store_true",
                        help="从已有 HTML/PDF/封面写构建报告与印刷规格")
    parser.add_argument("--sample", action="store_true", help="生成九页 16K 样张")
    parser.add_argument("--browser")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.sample:
            build_sample(args.out_dir / "sample", browser_override=args.browser)
            return 0
        manifest = load_manifest()
        validate_manifest(manifest)
        final = manifest["release"]["edition_status"] == "final"
        if args.report:
            if check_html(args.out_dir, manifest, final=final) != 0:
                return 1
            model = json.loads(
                (args.out_dir / config.MODEL_NAME).read_text(encoding="utf-8"))
            pdf_path = args.out_dir / config.PDF_NAME
            cover_path = args.out_dir / config.COVER_PDF_NAME
            for path in (pdf_path, cover_path):
                if not path.is_file():
                    raise BookError(
                        f"--report 需要先运行 --pdf --cover：缺少 {path.name}")
            pdf_report = check_pdf(pdf_path, model, manifest)
            cover_report = inspect_cover(
                cover_path, pdf_report["pages"], manifest)
            summary = write_report(
                args.out_dir, model, manifest, pdf_report, cover_report,
                pdf_path=pdf_path, cover_path=cover_path)
            print(f"report: {summary['pdf_pages']} pages, "
                  f"spine {summary['cover']['spine_mm']:.2f} mm")
            return 0
        if args.check:
            return check_html(args.out_dir, manifest, final=final)
        html_path = build_html(args.out_dir, args.site_dir, config.DATA_DIR,
                               config.DOCS, manifest, rebuild_site=not args.no_build,
                               final=final)
        if not (args.pdf or args.cover):
            return 0
        pdf_path = build_pdf(html_path, args.out_dir, manifest,
                             browser_override=args.browser)
        if not args.cover:
            return 0
        model = json.loads(
            (args.out_dir / config.MODEL_NAME).read_text(encoding="utf-8"))
        report = check_pdf(pdf_path, model, manifest)
        if report["problems"]:
            raise BookError("; ".join(report["problems"]))
        _html, cover_pdf, _preview = build_cover(
            args.out_dir, report["pages"], manifest,
            browser_override=args.browser)
        cover_report = inspect_cover(cover_pdf, report["pages"], manifest)
        if cover_report["problems"]:
            raise BookError("; ".join(cover_report["problems"]))
        return 0
    except (BookError, ValueError) as exc:
        print(f"book build error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

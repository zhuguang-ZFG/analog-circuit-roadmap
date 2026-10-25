#!/usr/bin/env python3
"""把 ngspice 的 wrdata 输出画成 SVG；图只来自实际仿真数据。"""
from __future__ import annotations

import argparse
from pathlib import Path


def load_data(path: Path) -> list[tuple[float, float]]:
    rows = []
    for line in Path(path).read_text(encoding="utf-8", errors="replace").splitlines():
        parts = line.replace(",", " ").split()
        if len(parts) < 2:
            continue
        try:
            rows.append((float(parts[0]), float(parts[1])))
        except ValueError:
            continue
    if not rows:
        raise ValueError(f"{path}: 没有可绘制的数据")
    return rows


def plot(csv_path: Path, output: Path, title: str) -> Path:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    rows = load_data(csv_path)
    seconds = [row[0] * 1e3 for row in rows]
    voltage = [row[1] for row in rows]
    figure, axes = plt.subplots(figsize=(6.4, 3.6), dpi=150)
    axes.plot(seconds, voltage, color="#b45309", linewidth=1.4)
    axes.axhline(5.0, color="#d9e2ec", linewidth=0.8, linestyle="--")
    axes.set_title(title, fontsize=11, color="#1f2933")
    axes.set_xlabel("时间 / ms", fontsize=9)
    axes.set_ylabel("v(out) / V", fontsize=9)
    axes.grid(True, color="#e5e7eb", linewidth=0.5)
    axes.text(0.99, 0.04, "数据：ngspice 仿真 " + Path(csv_path).name,
              transform=axes.transAxes, ha="right", va="bottom",
              fontsize=7, color="#52606d")
    figure.tight_layout()
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output, format="svg", bbox_inches="tight")
    plt.close(figure)
    return output


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("data", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--title", default="仿真结果")
    args = parser.parse_args(argv)
    try:
        plot(args.data, args.output, args.title)
    except (ValueError, ImportError) as exc:
        print(f"plot error: {exc}")
        return 1
    print(f"plot  {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

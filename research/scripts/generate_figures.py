from __future__ import annotations

import argparse
import csv
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a comparison figure from saved experiment metrics.")
    parser.add_argument("table", type=Path, help="CSV created by generate_outputs.py")
    parser.add_argument("--output", type=Path, default=Path("research/figures/accuracy_comparison.svg"))
    args = parser.parse_args()
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        plt = None

    rows = list(csv.DictReader(args.table.open(encoding="utf-8")))
    if not rows:
        raise SystemExit("No saved metrics found; run an experiment first.")
    labels = [row["experiment_id"] for row in rows]
    top1 = [float(row["top_1_accuracy"]) for row in rows if row["top_1_accuracy"] not in ("", "None")]
    if len(top1) != len(rows):
        raise SystemExit("Accuracy values are incomplete; no figure was generated.")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if plt is None:
        if args.output.suffix.lower() != ".svg":
            raise SystemExit("matplotlib is unavailable; use an .svg output or install research requirements.")
        width, height, bar_width, gap = 760, 320, 80, 40
        bars = []
        for index, value in enumerate(top1):
            x = 40 + index * (bar_width + gap)
            bar_height = int(value * 220)
            y = 260 - bar_height
            bars.append(
                f'<rect x="{x}" y="{y}" width="{bar_width}" height="{bar_height}" fill="#2a8c8c"/>'
                f'<text x="{x + bar_width / 2}" y="285" text-anchor="middle" font-size="11">{labels[index]}</text>'
            )
        svg = (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
            f'viewBox="0 0 {width} {height}"><text x="40" y="24" font-size="16">'
            "Saved DiagnoSure experiment results</text>{}"
            '<line x1="40" y1="260" x2="720" y2="260" stroke="#333"/>'
            "</svg>"
        ).format("".join(bars))
        args.output.write_text(svg, encoding="utf-8")
        print(args.output)
        return
    figure, axis = plt.subplots(figsize=(max(6, len(labels) * 2), 4))
    axis.bar(labels, top1, color="#2a8c8c")
    axis.set_ylim(0, 1)
    axis.set_ylabel("Top-1 accuracy")
    axis.set_title("Saved DiagnoSure experiment results")
    axis.tick_params(axis="x", rotation=25)
    figure.tight_layout()
    figure.savefig(args.output, dpi=300)
    print(args.output)


if __name__ == "__main__":
    main()

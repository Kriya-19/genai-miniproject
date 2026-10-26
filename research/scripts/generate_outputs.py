from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate CSV tables from saved research metrics.")
    parser.add_argument("results_root", type=Path)
    parser.add_argument("--output", type=Path, default=Path("research/tables"))
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    rows = []
    for metrics_path in sorted(args.results_root.glob("*/metrics.json")):
        metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
        rows.append({
            "experiment_id": metrics_path.parent.name,
            "cases": metrics.get("cases"),
            "coverage": metrics.get("coverage"),
            "top_1_accuracy": metrics.get("top_1_accuracy"),
            "top_5_accuracy": metrics.get("top_5_accuracy"),
            "failure_rate": metrics.get("failure_rate"),
            "median_latency_ms": (metrics.get("latency_ms") or {}).get("median"),
            "p95_latency_ms": (metrics.get("latency_ms") or {}).get("p95"),
        })
    output = args.output / "experiment_summary.csv"
    with output.open("w", newline="", encoding="utf-8") as handle:
        fields = list(rows[0]) if rows else [
            "experiment_id", "cases", "coverage", "top_1_accuracy",
            "top_5_accuracy", "failure_rate", "median_latency_ms", "p95_latency_ms",
        ]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    print(json.dumps({"rows": len(rows), "output": str(output)}, indent=2))


if __name__ == "__main__":
    main()

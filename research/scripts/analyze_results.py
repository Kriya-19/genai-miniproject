from __future__ import annotations

import argparse
import json
from pathlib import Path

from research.lib import summarize


def main() -> None:
    parser = argparse.ArgumentParser(description="Recompute metrics from saved case results.")
    parser.add_argument("results_dir", type=Path)
    args = parser.parse_args()
    metrics = summarize(args.results_dir / "case_results.jsonl")
    (args.results_dir / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()

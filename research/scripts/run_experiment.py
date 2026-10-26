from __future__ import annotations

import argparse
import json
from pathlib import Path

from research.lib import environment, experiment_id, load_cases, run


def main() -> None:
    parser = argparse.ArgumentParser(description="Run DiagnoSure research evaluation.")
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--pipeline", choices=("full", "primary"), default="full")
    parser.add_argument("--name", default="evaluation")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--results-root", type=Path, default=Path("research/results"))
    args = parser.parse_args()
    cases = load_cases(args.dataset)
    config = {"name": args.name, "pipeline": args.pipeline, "seed": args.seed}
    run_id = f"{args.name}-{args.pipeline}-{experiment_id(config, cases)}"
    output_dir = args.results_root / run_id
    (output_dir / "config.json").parent.mkdir(parents=True, exist_ok=True)
    (output_dir / "config.json").write_text(json.dumps(config, indent=2), encoding="utf-8")
    (output_dir / "environment.json").write_text(json.dumps(environment(), indent=2), encoding="utf-8")
    (output_dir / "dataset_manifest.json").write_text(
        json.dumps({"path": str(args.dataset.resolve()), "case_ids": [case["id"] for case in cases]}, indent=2),
        encoding="utf-8",
    )
    metrics = run(config, cases, output_dir)
    (output_dir / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print(json.dumps({"experiment_id": run_id, **metrics}, indent=2))


if __name__ == "__main__":
    main()

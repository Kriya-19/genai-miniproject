import json
from pathlib import Path

from research.lib import load_cases, summarize


def test_smoke_dataset_has_reference_labels():
    cases = load_cases(Path("research/data/smoke_cases.jsonl"))
    assert len(cases) == 2
    assert all(case["reference_labels"] for case in cases)


def test_metrics_are_recomputed_from_saved_jsonl(tmp_path):
    results = tmp_path / "case_results.jsonl"
    results.write_text(
        "\n".join([
            json.dumps({"case_id": "a", "status": "completed", "predicted_labels": ["X"], "reference_labels": ["X"], "duration_ms": 10}),
            json.dumps({"case_id": "b", "status": "failed", "predicted_labels": [], "reference_labels": ["Y"], "duration_ms": 20}),
        ]),
        encoding="utf-8",
    )
    metrics = summarize(results)
    assert metrics["coverage"] == 0.5
    assert metrics["top_1_accuracy"] == 1.0
    assert metrics["failure_rate"] == 0.5

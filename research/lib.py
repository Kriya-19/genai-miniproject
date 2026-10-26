from __future__ import annotations

import asyncio
import hashlib
import json
import os
import platform
import random
import sys
import time
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


def load_cases(path: Path) -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            item = json.loads(line)
            if not isinstance(item, dict) or not item.get("id") or not item.get("text"):
                raise ValueError(f"{path}:{line_number} requires id and text")
            labels = item.get("reference_labels", [])
            if isinstance(labels, str):
                labels = [labels]
            if not isinstance(labels, list):
                raise ValueError(f"{path}:{line_number} reference_labels must be a list")
            cases.append({
                "id": str(item["id"]),
                "text": str(item["text"]),
                "reference_labels": [str(label) for label in labels if str(label).strip()],
                "source": item.get("source", "unspecified"),
            })
    return cases


def experiment_id(config: dict[str, Any], cases: list[dict[str, Any]]) -> str:
    payload = json.dumps({"config": config, "cases": cases}, sort_keys=True).encode()
    return hashlib.sha256(payload).hexdigest()[:12]


def _import_model() -> tuple[Any, Any, Any]:
    root = str(ROOT)
    if root not in sys.path:
        sys.path.insert(0, root)
    from model.agent import OrchestratorAgent
    from model.diagnosis import DiagnosisAgent
    from model.symptoms import EnhancedSymptomParser
    return OrchestratorAgent, DiagnosisAgent, EnhancedSymptomParser


async def _run_primary(text: str) -> dict[str, Any]:
    _, diagnosis_class, parser_class = _import_model()
    parser = parser_class()
    diagnosis = diagnosis_class()
    parsed = parser.extract_symptoms_from_text(text)
    symptoms = parsed.get("symptoms", []) if isinstance(parsed, dict) else []
    result = await diagnosis.diagnose({
        "symptoms": symptoms,
        "demographics": {},
        "allergies": ["no"],
        "past_diseases": ["no"],
        "medications": ["no"],
    })
    return {
        "status": "success",
        "pipeline": "primary_diagnosis_agent",
        "symptom_extraction": parsed,
        **result,
    }


async def _run_full(text: str) -> dict[str, Any]:
    orchestrator_class, _, _ = _import_model()
    agent = orchestrator_class(enable_voice=False)
    try:
        return await agent.process_natural_language_input(text)
    finally:
        cleanup = getattr(agent, "cleanup", None)
        if cleanup is not None:
            await cleanup()


def _labels(result: dict[str, Any]) -> list[str]:
    top = result.get("top_diagnosis") or {}
    ordered = [top.get("condition")] if isinstance(top, dict) else []
    for item in result.get("top_5_diagnoses", result.get("all_diagnoses", [])) or []:
        if isinstance(item, dict):
            ordered.append(item.get("condition"))
    return [str(label).strip() for label in ordered if label and str(label).strip()]


def run(config: dict[str, Any], cases: list[dict[str, Any]], output_dir: Path) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    random.seed(int(config.get("seed", 42)))
    pipeline = config.get("pipeline", "full")
    runner = _run_full if pipeline == "full" else _run_primary
    checkpoint_path = output_dir / "checkpoint.json"
    completed = {}
    if checkpoint_path.exists():
        completed = json.loads(checkpoint_path.read_text(encoding="utf-8"))
    results_path = output_dir / "case_results.jsonl"
    existing_ids = set(completed)
    mode = "a" if results_path.exists() else "w"
    with results_path.open(mode, encoding="utf-8") as results_file:
        for case in cases:
            if case["id"] in existing_ids:
                continue
            started = time.perf_counter()
            row: dict[str, Any] = {
                "case_id": case["id"],
                "reference_labels": case["reference_labels"],
                "pipeline": pipeline,
                "input_text": case["text"],
                "status": "failed",
            }
            try:
                result = asyncio.run(runner(case["text"]))
                row.update({
                    "status": "completed" if result.get("status") != "error" else "failed",
                    "predicted_labels": _labels(result),
                    "output": result,
                })
                if result.get("status") == "error":
                    row["error"] = result.get("error_message", "pipeline returned an error")
            except Exception as exc:
                row["error"] = f"{type(exc).__name__}: {exc}"
            row["duration_ms"] = round((time.perf_counter() - started) * 1000, 2)
            results_file.write(json.dumps(row, ensure_ascii=False, default=str) + "\n")
            results_file.flush()
            completed[case["id"]] = row["status"]
            checkpoint_path.write_text(json.dumps(completed, indent=2), encoding="utf-8")
    return summarize(output_dir / "case_results.jsonl")


def summarize(results_path: Path) -> dict[str, Any]:
    rows = [
        json.loads(line) for line in results_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    valid = [row for row in rows if row.get("status") == "completed" and row.get("predicted_labels")]
    top1 = sum(bool(set(row["predicted_labels"][:1]) & set(row["reference_labels"])) for row in valid)
    top5 = sum(bool(set(row["predicted_labels"][:5]) & set(row["reference_labels"])) for row in valid)
    durations = sorted(float(row.get("duration_ms", 0)) for row in rows)
    return {
        "cases": len(rows),
        "completed": len([row for row in rows if row.get("status") == "completed"]),
        "valid_predictions": len(valid),
        "coverage": len(valid) / len(rows) if rows else 0.0,
        "top_1_accuracy": top1 / len(valid) if valid else None,
        "top_5_accuracy": top5 / len(valid) if valid else None,
        "failure_rate": (len(rows) - len(valid)) / len(rows) if rows else 0.0,
        "latency_ms": {
            "median": durations[len(durations) // 2] if durations else None,
            "p95": durations[min(len(durations) - 1, int(len(durations) * 0.95))] if durations else None,
        },
    }


def environment() -> dict[str, Any]:
    return {
        "python": sys.version,
        "platform": platform.platform(),
        "working_directory": str(Path.cwd()),
        "external_credentials_loaded": bool(os.getenv("DXGPT_API_KEY")),
    }

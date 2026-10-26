# Experiments and artifacts

The package produces three artifact classes:

## Code

- `research/scripts/prepare_dataset.py` validates and normalizes JSONL.
- `research/scripts/run_experiment.py` invokes the actual full orchestrator or
  primary diagnosis baseline.
- `research/scripts/analyze_results.py` recomputes metrics from saved JSONL.
- `research/scripts/generate_outputs.py` creates CSV comparison tables from
  saved metrics; no table is generated from manually entered values.
- `research/scripts/generate_figures.py` creates a PNG from the saved CSV table
  when matplotlib is installed.
- `research/lib.py` contains checkpointing, invocation, label extraction and
  metrics.

## Evidence

Each run is stored in `research/results/<experiment-id>/`:

- `config.json`, `environment.json`, `dataset_manifest.json`
- `case_results.jsonl` with raw model output, labels, status, duration and errors
- `checkpoint.json` for safe resume
- `metrics.json` with computed coverage, accuracy, failures and latency

Generated files are evidence only after the command has actually been run.
This repository does not contain fabricated results.

## Documentation

See `IMPLEMENTATION_AUDIT.md`, `RESEARCH_PROTOCOL.md`, `DATASET_CARD.md`,
`REPRODUCIBILITY.md` and `LIMITATIONS.md`.

## Planned extensions

Analysis scripts can be extended with paired bootstrap intervals, confusion
matrices, tables and figures after a sufficiently large labelled dataset is
available. They must read saved evidence rather than hard-code values.

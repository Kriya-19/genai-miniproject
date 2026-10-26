# Reproducibility

Run commands from the repository root with the existing `.venv`. Do not copy
the private root `.env` into source or results.

## Validate a dataset

```powershell
.\.venv\Scripts\python.exe -m research.scripts.prepare_dataset research\data\smoke_cases.jsonl research\data\smoke_cases.normalized.jsonl
```

## Software smoke tests

The primary baseline avoids the external literature providers:

```powershell
.\.venv\Scripts\python.exe -m research.scripts.run_experiment --dataset research\data\smoke_cases.jsonl --pipeline primary --name smoke
```

The full smoke run invokes the actual orchestrator and may call DXGPT,
PubMed and ClinicalTrials.gov:

```powershell
.\.venv\Scripts\python.exe -m research.scripts.run_experiment --dataset research\data\smoke_cases.jsonl --pipeline full --name smoke
```

Resume the same command after interruption. Existing case IDs are read from
`checkpoint.json` and are not re-run.

## Confirmatory evaluation

After review of the dataset license, protocol and expected external API cost:

```powershell
.\.venv\Scripts\python.exe -m research.scripts.run_experiment --dataset C:\path\to\prepared.jsonl --pipeline primary --name confirmatory
.\.venv\Scripts\python.exe -m research.scripts.run_experiment --dataset C:\path\to\prepared.jsonl --pipeline full --name confirmatory
```

The runner records Python/platform information and whether `DXGPT_API_KEY` was
present, but never records the secret itself. External APIs and model services
can change, so bit-for-bit reproducibility is not guaranteed.

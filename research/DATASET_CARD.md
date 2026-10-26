# Dataset card

## Current dataset

No public clinical benchmark is bundled. `research/data/smoke_cases.jsonl` is a
two-case synthetic fixture used only to verify parsing, execution, checkpointing
and metric generation. Its labels were written for software tests and are not
clinical evidence.

## Required evaluation data

Supply a legally usable, de-identified dataset with free-text case
descriptions, reference diagnoses and licensing terms. A researcher must
select and document the dataset before a confirmatory run; this repository does
not silently download or redistribute one.

Each JSONL row must contain:

```json
{"id":"case-001","text":"de-identified case text","reference_labels":["diagnosis"],"source":"dataset/version"}
```

`id` must be unique. Original reference labels are preserved; label mapping and
exclusions must be documented in the resulting manifest.

## Risks and generalizability

The model's local fallback contains only a small sample condition set.
External DXGPT and public evidence providers introduce version, availability,
language and network variation. Dataset prevalence, demographic coverage,
clinical setting and label quality may not represent the intended users.
Results cannot establish safety, clinical utility or generalizability.

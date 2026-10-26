# Paper handoff

## Recommended title

**DiagnoSure: An Integrated Multi-Agent Workflow for Evidence-Supported
Preliminary Medical Decision Support**

## Problem and motivation

Symptom-based decision-support prototypes often separate diagnostic ranking,
evidence retrieval, explanation and patient record utilities. DiagnoSure
implements these stages in one sequential application while exposing their
limitations and external dependencies.

## Contribution statement

The demonstrated contribution is an implementation and evaluation framework
for tracing one symptom description through specialized diagnostic and
evidence-retrieval components into a persisted, patient-facing result. It is
not a claim of diagnostic superiority or clinical effectiveness.

## Abstract outline

1. Motivation and intended-use boundary.
2. System: parser, diagnosis agent, literature/case retrieval, explanation,
   warnings and backend persistence.
3. Evaluation: primary-vs-full smoke workflow and future labelled evaluation.
4. Report only measured metrics from saved evidence.
5. Limitations: external APIs, no clinical validation, generated explanations.

## Section outline

- Introduction: problem, motivation, cautious contributions.
- Related work: medical LLMs, retrieval, explainability, patient systems.
- Method: actual sequence and failure behavior in `METHODOLOGY.md`.
- Implementation: versions, APIs, persistence and frontend in
  `IMPLEMENTATION_DETAILS.md`.
- Evaluation: dataset card, protocol, baseline, metrics and saved results.
- Discussion: traceability/completeness hypotheses and runtime trade-offs.
- Ethics and limitations: `ETHICS_AND_LIMITATIONS.md`.
- Conclusion: integration demonstrated; clinical claims remain future work.

## Available findings

- Functional tests and builds pass as recorded in
  `FUNCTIONAL_EVALUATION.md`.
- The full and primary runners completed two synthetic smoke cases.
- Both runs had 1.0 coverage and 0.5 top-1/top-5 accuracy on that fixture.
- Those figures are software evidence only and must not be presented as
  clinical performance.

## Claim-evidence matrix

| Proposed paper claim | Supporting source/evidence | Verification | Safe wording |
|---|---|---|---|
| DiagnoSure has a sequential integrated workflow | `model/agent.py`, architecture diagram | verified by source inspection and smoke logs | “implements a sequential workflow” |
| Full workflow returns evidence and explanation fields | orchestrator outputs and normalizer | full smoke run | “can return retrieved summaries and generated explanations” |
| Full workflow is more accurate | no adequate clinical benchmark | not verified | do not claim |
| Full workflow is slower/different reliability | saved smoke metrics and external dependencies | exploratory only | “may incur additional latency and failure modes” |
| System is clinically safe | no clinical validation | not verified | do not claim |
| Research runner is reproducible | config, manifest, environment, checkpoint outputs | verified by tests and runs | “records reproducibility metadata and supports resume” |

## Tables and figures

Use the feature/agent inventories, experiment summary and architecture/
sequence diagrams. Treat `accuracy_comparison.svg` as a synthetic smoke-test
engineering artifact unless replaced by a properly powered evaluation.

## Future work

Obtain a licensed de-identified labelled dataset, predeclare label mapping,
add paired statistical analysis, conduct qualified evidence review, and add
verified research-only component flags before claiming ablation findings.

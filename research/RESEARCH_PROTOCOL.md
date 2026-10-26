# Research protocol

## Research questions and hypotheses

- **RQ1:** Can the implemented diagnostic, evidence-retrieval, case-study and
  explanation components be integrated into one coherent preliminary workflow?
- **RQ2:** Does the full workflow provide more complete evidence and explanation
  fields than the primary diagnosis component alone?
- **RQ3:** What runtime, reliability and evidence-availability trade-offs arise
  from the integrated workflow?
- **RQ4:** Which limitations affect traceability, reliability and clinical
  interpretation?

- H1: The full orchestrator has higher top-5 label coverage than the primary
  diagnosis-agent baseline on the same labelled cases.
- H2: The full orchestrator has no claimed top-1 improvement unless measured
  from a predeclared, independent dataset.
- H3: The full orchestrator has higher latency and a different failure profile
  because it calls external evidence services.

These are hypotheses, not results. RQ1 is supported by implementation tracing;
RQ2-RQ4 require a labelled dataset, saved per-case outputs and structured
evidence/explanation review.

## Independent variables

- Pipeline: `full` or `primary`.
- Dataset version and split.
- Seed (recorded, although external model calls may remain nondeterministic).
- Runtime/network configuration.

## Outcomes

Primary outcomes are top-1 accuracy, top-5 accuracy and valid-prediction
coverage. Secondary outcomes are failure rate, per-case duration, median and
p95 latency, evidence presence, and source counts where returned.
Confidence values are not probabilities, so ROC-AUC and calibration metrics are
not used.

## Case rules

Use only de-identified cases with a documented reference diagnosis. Preserve
original labels and record normalization. Exclude cases with no usable text or
ambiguous labels, with an explicit reason in the dataset manifest. Do not tune
prompts or configuration on the final test split.

## Baseline

The baseline uses the actual `EnhancedSymptomParser` followed by the actual
`DiagnosisAgent.diagnose`, with the same empty/default demographic context
currently supplied by the production orchestrator. The full condition uses the
actual `OrchestratorAgent`. This is a comparable primary-agent baseline, not a
fabricated prediction or a published-number comparison.

## Ablations

Literature, case-study, and explainability removal are currently **blocked**:
the orchestrator has no supported feature flags and downstream outputs are
assembled inside its method. The package must not report these as ablation
results. A future research-only orchestrator configuration can add them after
verifying that removed outputs cannot influence predictions.

## Statistical plan

Report paired per-case results, coverage and failures. For a sufficiently large
labelled dataset, compute paired bootstrap confidence intervals and McNemar's
test for top-1 disagreements. Small smoke runs are software verification only
and must not receive confidence intervals or clinical interpretation.

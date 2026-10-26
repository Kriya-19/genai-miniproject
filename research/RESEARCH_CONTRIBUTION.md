# Research contribution and claim boundaries

## Defensible contribution

DiagnoSure implements an integrated preliminary decision-support workflow that
passes one natural-language symptom description through symptom extraction,
diagnostic ranking, public biomedical evidence retrieval, case-report retrieval,
explainability formatting, and safety-warning rules. The backend preserves this
result with the patient's diagnosis case and exposes it alongside patient-facing
health utilities.

The strongest defensible contribution is therefore **workflow integration and
traceability of heterogeneous outputs**, not a new diagnostic model or a claim
of clinical superiority.

## Common capabilities

Natural-language symptom input, ranked differentials, retrieval from PubMed,
clinical evidence summaries, patient records, authentication, and video
consultation are all established capabilities in the wider literature and
software ecosystem. Multi-agent medical reasoning is not itself a novel claim.

## DiagnoSure-specific engineering decisions

- A production adapter connects the unchanged model repository to FastAPI.
- The orchestrator executes diagnostic ranking before evidence searches and
  then constructs an explanation from those outputs.
- The backend stores the normalized result and exposes literature, case-study,
  recommendations, warnings and limitations together.
- The same application connects diagnosis cases to a patient health passport,
  records, clinic search, reminders and consultations.

These are integration decisions. They become scientific findings only after
controlled evaluation.

## Hypotheses, not findings

The full workflow may produce more complete evidence and explanation outputs
than the primary diagnosis component, but this requires a labelled dataset and
structured evidence-quality review. It may also be slower and more failure
prone because of external calls. The current two-case smoke runs do not test
these claims.

## Intro-ready statement

“We present DiagnoSure, an implementation study of an integrated preliminary
medical decision-support workflow that combines symptom-based diagnostic
ranking with biomedical literature retrieval, clinical case-report retrieval,
explainability formatting, safety warnings, and patient-facing health
utilities. We characterize its interfaces, dependencies, reliability and
evidence traceability rather than claiming clinical efficacy.”

# Ethics and limitations

DiagnoSure is preliminary medical decision support. It must not replace a
qualified clinician or be used as the sole basis for urgent care decisions.
Generated diagnoses, recommendations and explanations can be wrong or
unsupported.

Literature summaries are generated from public retrieval results and a simple
relevance score; retrieval does not prove that a source supports every claim.
Case reports are not representative evidence of treatment effectiveness.
Safety warnings are a small deterministic rule set and are not a complete
triage system.

The application has authentication and user-scoped database queries, but this
document does not claim security certification, HIPAA/GDPR compliance or
clinical-device compliance. Health records, uploaded files, QR links and
external providers require deployment-specific privacy review, consent,
retention controls and access testing.

No prospective evaluation, clinician adjudication, clinical trial or
population-level validation has been performed in this repository. The
bundled smoke cases are synthetic software fixtures. Dataset bias,
demographic coverage, label quality, language coverage and external-service
drift remain unresolved.

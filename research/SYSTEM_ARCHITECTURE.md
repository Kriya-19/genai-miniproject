# System architecture

## Runtime flow

The React frontend calls FastAPI through `frontend/src/services/apiClient.js`.
Authenticated diagnosis requests reach `POST /api/analyze`, which creates a
`DiagnosisCase`, calls `DiagnosisService`, and then `AgentAdapter`. The adapter
imports `model.agent.OrchestratorAgent` lazily so model initialization does not
occur during unrelated backend imports.

The orchestrator is sequential: symptom extraction, diagnosis, literature,
case-study retrieval, and explanation. Literature and case-study calls are
conditional on successful intermediate inputs, but are not parallelized.
Failures in those retrieval stages are logged and represented as unavailable
evidence; the orchestrator can still return a diagnosis report.

## Application surfaces

Authentication and patient profile/health-passport routes use SQLAlchemy
models in SQLite by default, with PostgreSQL retained through configuration.
Health records and shares are persisted in the database; uploaded files are
stored under the configured upload directory. Clinic search uses public
OpenStreetMap/Overpass and Nominatim services. Consultations generate Jitsi
rooms; public Jitsi's moderator policy remains an external limitation.
Reminders use persisted records and an APScheduler development scheduler.
Research scripts are isolated under `research/` and do not write production
records.

See [figures/architecture.mmd](figures/architecture.mmd) and
[figures/agent_sequence.mmd](figures/agent_sequence.mmd).

## Agent table

| Component | Source | Receives | Produces | Failure behavior |
|---|---|---|---|---|
| Symptom parser | `model/symptoms.py` `EnhancedSymptomParser` | sentence | symptom dictionaries | orchestrator returns error if extraction fails |
| Diagnosis agent | `model/diagnosis.py` `DiagnosisAgent` | symptoms and default context | top diagnosis and ordered differential | optional DXGPT failure falls back to local condition database |
| Literature agent | `model/literature_agent.py` `LiteratureAgent` | diagnoses and extracted symptoms | PubMed/trial records and summary | empty evidence when retrieval fails |
| Case-study agent | `model/case_study_agent.py` `CaseStudyAgent` | diagnoses and symptoms | PubMed case reports and summary | empty evidence when retrieval fails |
| Explainability agent | `model/explainability.py` `ExplainabilityAgent` | diagnoses and evidence summaries | natural-language report | fallback text if report generation fails |
| Safety rules | `model/agent.py` `_get_safety_warnings` | sentence and symptoms | red-flag warnings | deterministic rules; not clinical triage |
| Backend normalizer | `backend/app/services/diagnosis_service.py` | raw model result | persisted API result | marks case failed on unhandled exception |

## Failure and trust boundaries

External model and biomedical APIs are unavailable dependencies. Public
provider results can be stale, incomplete, rate-limited or unavailable. The
backend authentication boundary protects patient routes, but this handoff is
not a security certification or regulatory assessment.

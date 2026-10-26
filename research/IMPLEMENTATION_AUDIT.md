# DiagnoSure implementation audit

## Scope and evidence

This audit is based on the source currently in `model/`, the backend adapter and
diagnosis service. The `model/` directory was not changed by the research
package. Names and behavior below describe the implementation, not an intended
architecture.

## Actual workflow

`POST /api/analyze` sends the user's natural-language sentence to
`DiagnosisService`, which calls `AgentAdapter`, which imports
`model.agent.OrchestratorAgent` and invokes
`process_natural_language_input`. The orchestrator:

1. Extracts symptoms with `EnhancedSymptomParser`.
2. Applies hard-coded safety-warning rules.
3. Calls `DiagnosisAgent.diagnose`.
4. Searches PubMed and ClinicalTrials.gov with `LiteratureAgent`.
5. Searches PubMed case reports with `CaseStudyAgent`.
6. Builds a textual report with `ExplainabilityAgent`.
7. Returns the report, top diagnosis, ordered differential, evidence summaries
   and safety warnings.

The backend normalizes and persists a subset of this output in its own SQLite
case table. Research runs call the model interfaces directly and do not write
to the production database.

## Components

| Component | Input | Output | Dependencies |
|---|---|---|---|
| `EnhancedSymptomParser` | free text | extracted symptom dictionaries | model code and NLP resources |
| `DiagnosisAgent` | symptoms and empty/default patient context | top diagnosis and up to five ranked diagnoses | local sample-condition fallback; optional DXGPT API |
| `LiteratureAgent` | diagnoses and symptoms | PubMed/trial evidence and a summary | public NCBI/ClinicalTrials APIs |
| `CaseStudyAgent` | diagnoses and symptoms | PubMed case reports and a summary | public NCBI API |
| `ExplainabilityAgent` | diagnoses and evidence summaries | textual report | Python only |
| `OrchestratorAgent` | natural-language sentence | complete result dictionary | all components above |

The primary `DiagnosisAgent` is independently callable. The orchestrator does
not expose feature flags for removing literature, case-study, or explainability
agents. Consequently those ablations are not represented as completed
experiments; adding them would require modifying the protected model code or
risking a false ablation.

## Scoring and evidence

The local fallback uses bounded symptom overlap and a deterministic
`RandomForestClassifier` is initialized, while the diagnosis method first
attempts the optional DXGPT API. Returned confidence/ranking scores are not
calibrated probabilities. Literature relevance is a term-overlap score over
retrieved titles/abstracts. The explainability report is generated text; its
presence is not evidence that claims are clinically correct.

## Research questions supported now

- **RQ1:** Yes, if an appropriate de-identified labelled dataset is supplied.
- **RQ2:** Yes: compare the full orchestrator with the primary diagnosis-agent
  baseline on identical cases.
- **RQ3:** Not yet for individual downstream agents because production code
  lacks research-only feature flags. This limitation is recorded rather than
  simulated.
- **RQ4:** Partly: output presence, source counts and structured human-review
  fields can be collected; clinical factuality requires qualified reviewers.
- **RQ5:** Yes: completion, failure, latency and external-service errors are
  recorded per case.

## Important limitations

The system is a decision-support prototype, not a validated clinical device.
The available local condition database is tiny, external model/API behavior may
change, literature calls are network-dependent, and the smoke fixture is
synthetic. No clinical performance claim should be made from the fixture.

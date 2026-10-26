# Methodology

## Problem and intended use

The implementation accepts a free-text health concern and produces preliminary
ranked diagnostic suggestions, retrieved evidence summaries, recommendations,
limitations and safety warnings. It is decision support, not a confirmed
diagnosis or a substitute for clinical care.

## Algorithm

```text
input sentence
create processing case
symptoms = EnhancedSymptomParser.extract(sentence)
if extraction fails: return error and mark case failed
warnings = deterministic red-flag rules(sentence, symptoms)
diagnoses = DiagnosisAgent.diagnose(symptoms, empty/default context)
if external DXGPT returns no result:
    diagnoses = local condition overlap fallback
literature = LiteratureAgent.process(diagnoses, symptoms)
if literature fails: literature = empty evidence
case_reports = CaseStudyAgent.process(diagnoses, symptoms)
if case_reports fails: case_reports = empty evidence
report = ExplainabilityAgent.generate(top diagnosis, differential, summaries)
append warnings to report
return raw output
normalize output for the API
persist normalized JSON and completion status
```

Diagnosis ordering is inherited from the model's returned confidence/ranking
values. Those values are not calibrated probabilities. Literature relevance is
computed by the literature agent from query-term overlap with retrieved
metadata/text; it is not a validated evidence-quality score.

## Data and context

The current orchestrator supplies empty demographics and default “no”
allergy/history/medication values to the diagnosis agent. The backend stores
the user's passport separately; the current model invocation does not
automatically merge the full passport into this diagnosis context.

## Implementation mapping

| Method step | Source |
|---|---|
| Request validation | `backend/app/schemas.py` |
| Case persistence | `backend/app/services/diagnosis_service.py` |
| Model import boundary | `backend/app/integrations/agent_adapter.py` |
| Orchestration | `model/agent.py` |
| Symptom extraction | `model/symptoms.py` |
| Ranking/fallback | `model/diagnosis.py` |
| Literature retrieval | `model/literature_agent.py` |
| Case retrieval | `model/case_study_agent.py` |
| Report generation | `model/explainability.py` |
| API normalization | `backend/app/services/diagnosis_service.py` |

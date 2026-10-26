# Functional evaluation

The following checks use synthetic data or existing non-destructive tests.
They are software checks, not clinical validation.

| ID | Objective | Setup | Expected | Observed status |
|---|---|---|---|---|
| F-001 | backend health/auth contract | `backend/tests/test_api.py` | API health and auth behavior | PASS: included test suite |
| F-002 | research dataset parsing | two-case smoke JSONL | two valid labelled rows | PASS |
| F-003 | primary pipeline invocation | primary smoke command | both cases complete with predictions | PASS: 2/2, coverage 1.0 |
| F-004 | full orchestrator invocation | full smoke command | orchestrator stages execute and save outputs | PASS: 2/2, coverage 1.0 |
| F-005 | checkpoint resume | rerun same experiment | completed IDs are skipped | Implemented; not separately timed in this handoff |
| F-006 | metric recomputation | research unit test | metrics derive from JSONL | PASS |
| F-007 | empty diagnosis input | API schema/unit behavior | validation error or explicit failure | Covered by request validation; broader test is future work |
| F-008 | evidence provider failure | model exception handling | evidence marked unavailable, diagnosis may continue | Implemented in orchestrator; isolated fault injection not run |
| F-009 | red-flag warning | synthetic breathing/chest-pain text | warning appended | Implemented in model; isolated test is future work |
| F-010 | frontend production build | `npm run build` | Vite build completes | PASS |

The two smoke runs performed public evidence/API calls for the full pipeline.
No patient records, notifications or real consultations were used.

## Illustrative cases

The smoke fixture includes a synthetic influenza-like case and a
common-cold-like case. Their observed outputs are saved under
`research/results/`; they must not be interpreted as clinical evidence.

An ambiguous case and an urgent-warning case are protocol examples only until
run and saved as evidence. The expected behavior is a ranked differential with
uncertainty and a warning, not a definitive diagnosis.

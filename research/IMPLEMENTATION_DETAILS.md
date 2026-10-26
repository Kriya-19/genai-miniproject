# Implementation details

## Verified stack

The repository contains Python model code, a FastAPI/SQLAlchemy/Alembic
backend, and a React/Vite frontend. Production requirements are listed in
`backend/requirements.txt`; the research runner itself uses the Python
standard library, with optional pandas, scikit-learn, SciPy and matplotlib
listed in `research/requirements-research.txt`.

The verified local environment used for the smoke runs was Python 3.13.11.
Exact model-service versions and hardware are not asserted here because they
are not stable repository facts.

## Configuration and dependencies

The backend defaults to `backend/diagnosure.db`; `DATABASE_URL` can select
PostgreSQL. Authentication uses a JWT secret configured through environment
variables. Secrets are intentionally omitted from this document. The model
may use `DXGPT_API_KEY`; without a usable external result, `DiagnosisAgent`
uses its local condition fallback.

Evidence retrieval depends on public PubMed, ClinicalTrials.gov and NCBI
endpoints. Clinic search depends on OpenStreetMap providers. Consultations
depend on Jitsi. These services can fail or change independently.

## Startup

From the repository root:

```powershell
.\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
Set-Location frontend
npm run dev -- --host 0.0.0.0
```

Research commands are documented in [REPRODUCIBILITY.md](REPRODUCIBILITY.md).

## Relevant API surfaces

Authentication: `/api/auth/register`, `/api/auth/login`, `/api/auth/me`.
Diagnosis: `/api/analyze`, `/api/cases`, `/api/cases/{case_id}/results`.
Passport/records: `/api/patients/me/passport`,
`/api/patients/me/records`, `/api/patients/me/passport.pdf`.
Clinics: `/api/clinics`. Consultations: `/api/consultations`.
Reminders: `/api/reminders`. Research status: `/api/research/{metric}`.

## Compatibility limitations

The full orchestrator performs network calls and can take tens of seconds or
longer. The public Jitsi deployment does not grant a DiagnoSure doctor account
moderator rights. Public map and literature providers can rate-limit requests.

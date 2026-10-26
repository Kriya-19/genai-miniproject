# DiagnoSure backend

From the repository root in PowerShell:

```powershell
.\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
Copy-Item backend\.env.example backend\.env
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --app-dir backend
```

Open Swagger at <http://127.0.0.1:8000/docs>. SQLite is the development default; set
`DATABASE_URL` to PostgreSQL before production use. The diagnosis adapter lazily calls
the unchanged `model.agent.OrchestratorAgent` with voice disabled. Live clinic search,
notifications, PostgreSQL, and external literature services require their providers.

## Free/open-source integrations

- **Clinic finder:** `GET /api/clinics` uses OpenStreetMap Overpass. Results are
  cached in memory for `OVERPASS_CACHE_TTL_SECONDS`, requests are spaced by
  `OVERPASS_MIN_INTERVAL_SECONDS`, and responses include OpenStreetMap attribution
  and a Leaflet-compatible tile URL. Public Overpass capacity is limited; use a
  self-hosted Overpass instance for higher volume. `MAPS_PROVIDER` can disable or
  replace this provider later.
- **Video consultations:** consultation creation generates a unique Jitsi room and
  returns `video_provider`, `video_room`, and `video_url`. A frontend can embed
  Jitsi with its free IFrame API and `https://meet.jit.si/external_api.js`.
  The provider is replaceable through `JITSI_PROVIDER` and `JITSI_BASE_URL`.
- **Reminders:** APScheduler runs in development and records local reminder events.
  No notification is claimed as delivered. Set `NOTIFICATION_PROVIDER=fcm` only
  when an FCM adapter and credentials are intentionally added. Disable the in-process
  scheduler in multi-worker deployments and use one dedicated scheduler process.
- **Health Passport:** uploaded documents remain in the private local
  `UPLOAD_DIR` and are available only through authenticated download routes.
  They are not mounted as static files.
- **Diagnosis:** the unchanged local Python multi-agent pipeline is used; no paid
  AI API is introduced.

These integrations are suitable for a zero-cost local demonstration, not production
healthcare deployment. Public services have rate limits and availability constraints;
Jitsi/Overpass traffic, privacy, authentication, encryption, retention, abuse
prevention, consent, auditability, and regulatory controls require additional review.

On startup, the application creates the local SQLite database in `backend\diagnosure.db`
and applies the existing Alembic migrations automatically. No manual database creation
is needed. To apply the migration explicitly, run:

```powershell
.\.venv\Scripts\python.exe -m alembic -c backend\alembic.ini upgrade head
```

This is decision support, not a confirmed diagnosis. Ranking scores are not probabilities.
Production healthcare deployment requires privacy, security, clinical and regulatory review.

Run the backend tests with:

```powershell
.\.venv\Scripts\python.exe -m pytest backend\tests -q
```

# API contracts

Interactive OpenAPI documentation is available at `/docs`.

- `POST /api/auth/register`, `POST /api/auth/login`, `GET /api/auth/me`
- `POST /api/analyze`, `GET /api/cases/{case_id}`, `/results`, `/status`
- `GET/POST /api/patients/me/records`, `GET/DELETE /api/patients/me/records/{record_id}`
- `POST /api/patients/me/records/upload`, `GET /api/patients/me/records/{record_id}/download`
- `POST/GET /api/patients/me/shares`, `DELETE /api/patients/me/shares/{share_id}`
- `GET/POST /api/consultations`, `WS /api/consultations/{consultation_id}/ws`
- `GET /api/clinics?latitude=...&longitude=...` returns OpenStreetMap Overpass results,
  Leaflet-compatible tile configuration, and required attribution.
- Consultation responses include `video_provider`, `video_room`, and `video_url`.
  The prototype frontend can load `https://meet.jit.si/external_api.js` and initialize
  `new JitsiMeetExternalAPI(video_provider_host, { roomName: video_room, parentNode })`.
- `GET/POST /api/reminders`, `PATCH/DELETE /api/reminders/{reminder_id}`, `POST /api/reminders/{reminder_id}/complete`
- `GET /api/research/summary`, `/baseline`, `/ablations`

Protected routes use `Authorization: Bearer <access_token>`. Diagnosis results explicitly
preserve ranking scores, safety warnings, limitations, and unavailable provider states.

# Proposed API contracts (frontend expectations; not yet implemented)
Base URL: `VITE_API_BASE_URL` (default `http://localhost:8000/api`). JSON, ISO-8601 timestamps, string IDs. Auth: `Authorization: Bearer <token>` on every endpoint except sign-in.
Errors: HTTP 4xx/5xx with `{"detail":"message"}`. Uploads use `multipart/form-data`.

| Method & path | Request | Response |
|---|---|---|
| POST `/analyze` | `{age,sex|null,conditions[],medications[],allergies[],symptoms[{name,duration,severity,onset}],additional_symptoms[],negative_symptoms[],history,notes,use_health_passport}` | `{case_id,status}` |
| GET `/cases` | - | `[{case_id,created_at,status,top}]` |
| GET `/cases/{caseId}` | - | Diagnosis result (below) |
| GET `/research/summary` | - | `{is_sample:false,metrics:[{metric,baseline,multi}]}` |
| GET `/research/baseline` | - | `{is_sample,rows:[{metric,baseline,multi}]}` |
| GET `/research/ablations` | - | `{is_sample,rows:[{config,top1,top5}]}` |
| GET `/consultations` | - | `{items:[{id,doctor,specialty,scheduledAt,type:"video"|"audio",status:"scheduled|completed|cancelled",reason,caseId|null}],doctors:[{id,name,specialty,slots[]}]}` |
| POST `/consultations` | `{doctorId,slot,type,reason,shareReport,shareCaseId|null,consent}` | consultation |
| GET `/consultations/{id}` | - | consultation |
| GET `/consultations/{id}/join` | - | `{consultation_id,room,ice_servers[],token}` |
| DELETE `/consultations/{id}` | - | cancelled consultation |
| GET `/patients/me` | - | `{id,name,age,sex,lastUpdated}` |
| GET `/patients/me/health-summary` | - | `{conditions[],allergies[],medications[],vaccinations[{name,date}],aiSummary:{generated,verified,text,sources[]},lastUpdated}` |
| GET `/patients/me/records?q=&category=` | - | `[{id,title,category:"lab|prescription|consultation|vaccination|condition|other",date,origin:"patient|clinician|ocr",fileType,size,notes|null}]` |
| POST `/patients/me/records` | multipart: `file,title,category,date` | record |
| GET / PATCH / DELETE `/patients/me/records/{id}` | PATCH `{title?,notes?}` | record / `{ok}` |
| GET `/patients/me/shares` | - | `[{id,recipient,recordIds[],createdAt,expiresAt,status:"active|revoked|expired"}]` |
| POST `/patients/me/shares` | `{recordIds[],recipient,expiresAt}` | share (backend may add secure `link`) |
| DELETE `/patients/me/shares/{id}` | - | share |
| GET `/clinics?q=&type=&specialty=&lat=&lng=&radiusKm=` | - | `[{id,name,type,address,lat,lng,phone|null,specialties[],distanceKm|null}]` |
| GET `/clinics/{id}` | - | facility |
| GET `/reminders?status=` | - | `[{id,kind:"medication|followup",title,instructions,times[],startDate,endDate,frequency,timezone,reference,status,history[{at,event}]}]` |
| POST `/reminders` | reminder fields | reminder |
| PATCH `/reminders/{id}` | partial fields, optional `action:"skipped|snoozed"` | reminder |
| POST `/reminders/{id}/complete` | - | reminder |
| DELETE `/reminders/{id}` | - | cancelled reminder |
| GET / PATCH `/reminders/preferences` | `{browser,reminders,appointments,followups,quietStart,quietEnd}` | preferences |
| GET `/auth/me`, POST `/auth/sign-in`, POST `/auth/sign-out` | sign-in `{email,password}` | user `{id,name,role,email,language,timezone}` |

## Diagnosis result
```json
{"case_id":"","status":"completed","created_at":"","symptoms":[],"history_used":[],
 "differential_diagnoses":[{"condition":"","rank":1,"ranking_score":0.0,"score_type":"ranking_score","evidence_quality":null,
  "supporting_evidence":[],"contradictory_evidence":[],"sources":[{"title":"","details":"","url":null,"summary":"","relation":""}],
  "explanation":"","uncertainty":""}],
 "case_comparisons":[],"safety_warnings":[],"missing_information":[],"limitations":[]}
```
`ranking_score` is a ranking value, not a calibrated probability.

import json
import base64
import io
import html
import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone, timedelta
from pathlib import Path
from uuid import uuid4

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, Response, StreamingResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from .config import get_settings
from .database import get_db, initialize_database
from .integrations.clinic_provider import ClinicProviderUnavailable, OverpassClinicProvider
from .integrations.video_provider import JitsiVideoProvider
from .integrations.agent_adapter import AgentUnavailableError
from .models import Consultation, DiagnosisCase, HealthRecord, HealthRecordShare, Reminder, User
from .schemas import (
    AnalyzeRequest, ConsultationCreate, ConsultationUpdate, HealthRecordCreate, HealthRecordResponse,
    LoginRequest, RegisterRequest, ReminderCreate, ReminderUpdate, TokenResponse, UserResponse,
    PatientUpdate,
)
from .security import create_token, current_user, hash_password, optional_current_user, verify_password
from jose import jwt
from .services.diagnosis_service import DiagnosisService
from .services.reminder_scheduler import ReminderScheduler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
settings = get_settings()
clinic_provider = OverpassClinicProvider(settings)
jitsi_provider = JitsiVideoProvider(settings.jitsi_provider, settings.jitsi_base_url)
reminder_scheduler = ReminderScheduler(settings)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    initialize_database()
    if settings.enable_reminder_scheduler:
        reminder_scheduler.start()
    yield
    if settings.enable_reminder_scheduler:
        reminder_scheduler.shutdown()


app = FastAPI(title=settings.app_name, version="1.0.0", lifespan=lifespan)
allowed_origins = {
    settings.frontend_origin.rstrip("/"),
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://192.168.31.238:5173",
}
app.add_middleware(
    CORSMiddleware,
    allow_origins=sorted(allowed_origins),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
diagnosis_service = DiagnosisService()


@app.exception_handler(HTTPException)
async def http_error_handler(_, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"error": {"code": "HTTP_ERROR", "message": str(exc.detail), "details": []}})


@app.get("/health")
def health():
    return {"status": "ok", "database": "configured", "model": "lazy-loaded"}


@app.post("/api/auth/register", response_model=TokenResponse, status_code=201)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    if db.scalar(select(User).where(User.email == request.email.lower())):
        raise HTTPException(409, "Email is already registered")
    user = User(
        email=request.email.lower(), password_hash=hash_password(request.password),
        full_name=request.full_name, role=request.role, age=request.age, sex=request.sex,
        allergies=json.dumps(request.allergies), conditions=json.dumps(request.conditions),
        medications=json.dumps(request.medications), medical_history=request.medical_history,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return TokenResponse(access_token=create_token(user), user=user)


@app.post("/api/auth/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == request.email.lower()))
    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(401, "Invalid email or password")
    return TokenResponse(access_token=create_token(user), user=user)


@app.post("/api/auth/logout")
def logout(_: User = Depends(current_user)):
    return {"status": "logged_out", "message": "Discard the access token on the client."}


@app.get("/api/auth/me", response_model=UserResponse)
def me(user: User = Depends(current_user)):
    return user


@app.post("/api/analyze")
async def analyze(
    request: AnalyzeRequest,
    db: Session = Depends(get_db),
    user: User | None = Depends(optional_current_user),
):
    try:
        return await diagnosis_service.analyze(request, db, user.id if user else None)
    except AgentUnavailableError as exc:
        raise HTTPException(503, str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(502, str(exc)) from exc


def owned_or_404(db: Session, record_id: str, user: User) -> HealthRecord:
    record = db.get(HealthRecord, record_id)
    if not record or record.user_id != user.id:
        raise HTTPException(404, "Health record not found")
    return record


@app.get("/api/patients/me")
def patient_profile(user: User = Depends(current_user)):
    return {
        "id": user.id, "email": user.email, "full_name": user.full_name, "role": user.role,
        "age": user.age, "sex": user.sex,
        "allergies": json.loads(user.allergies or "[]"),
        "conditions": json.loads(user.conditions or "[]"),
        "medications": json.loads(user.medications or "[]"),
        "medical_history": user.medical_history,
    }


def passport_payload(user: User) -> dict:
    return {
        "id": user.id,
        "name": user.full_name,
        "age": user.age,
        "sex": user.sex,
        "allergies": json.loads(user.allergies or "[]"),
        "conditions": json.loads(user.conditions or "[]"),
        "medications": json.loads(user.medications or "[]"),
        "medical_history": user.medical_history,
    }


def passport_share_token(user: User) -> str:
    expiry = datetime.now(timezone.utc) + timedelta(hours=24)
    return jwt.encode({"sub": user.id, "purpose": "health_passport", "exp": expiry}, settings.jwt_secret_key, algorithm="HS256")


@app.get("/api/patients/me/passport")
def passport_summary(user: User = Depends(current_user)):
    token = passport_share_token(user)
    share_url = f"{settings.passport_share_base_url.rstrip('/')}/api/passport/shared/{token}"
    try:
        import qrcode
        image = qrcode.make(share_url)
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        qr_code = "data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode()
    except ImportError as exc:
        raise HTTPException(503, "QR generation is unavailable; install backend dependencies.") from exc
    return {"passport": passport_payload(user), "share_url": share_url, "qr_code_data_url": qr_code, "expires_in_hours": 24}


@app.get("/api/passport/shared/{token}")
def shared_passport(token: str, db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=["HS256"])
        if payload.get("purpose") != "health_passport":
            raise HTTPException(403, "Invalid passport link")
        user = db.get(User, payload.get("sub"))
    except Exception as exc:
        raise HTTPException(403, "This passport link is invalid or expired") from exc
    if user is None:
        raise HTTPException(404, "Patient not found")
    data = passport_payload(user)
    def items(values: list[str]) -> str:
        return "".join(f"<li>{html.escape(value)}</li>" for value in values) or "<li>None recorded</li>"
    return HTMLResponse(f"""<!doctype html>
<html><head><meta name="viewport" content="width=device-width,initial-scale=1">
<title>DiagnoSure Health Passport</title>
<style>body{{font-family:Arial,sans-serif;max-width:720px;margin:2rem auto;padding:1rem;color:#17324d}}
section{{border:1px solid #d5e0e8;border-radius:12px;padding:1rem;margin:1rem 0}}
h1{{color:#123d62}}dt{{font-weight:bold;margin-top:.7rem}}dd{{margin:.2rem 0}}
a{{display:inline-block;background:#1769aa;color:white;padding:.7rem 1rem;border-radius:8px;text-decoration:none}}</style>
</head><body><h1>DiagnoSure Health Passport</h1>
<p>Read-only passport. Verify the patient's identity before using this information.</p>
<section><dl><dt>Patient</dt><dd>{html.escape(data["name"])}</dd>
<dt>Age</dt><dd>{html.escape(str(data["age"] or "Not provided"))}</dd>
<dt>Sex</dt><dd>{html.escape(str(data["sex"] or "Not provided"))}</dd></dl></section>
<section><h2>Allergies</h2><ul>{items(data["allergies"])}</ul>
<h2>Conditions</h2><ul>{items(data["conditions"])}</ul>
<h2>Medications</h2><ul>{items(data["medications"])}</ul>
<h2>Medical history</h2><p>{html.escape(data["medical_history"] or "None recorded")}</p></section>
<a href="/api/passport/shared/{token}/pdf">Download PDF</a>
</body></html>""")


@app.get("/api/patients/me/passport.pdf")
def passport_pdf(user: User = Depends(current_user), db: Session = Depends(get_db)):
    return build_passport_pdf(user, db)


def build_passport_pdf(user: User, db: Session):
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
    except ImportError as exc:
        raise HTTPException(503, "PDF generation is unavailable; install backend dependencies.") from exc
    records = db.scalars(select(HealthRecord).where(HealthRecord.user_id == user.id).order_by(HealthRecord.created_at.desc())).all()
    data = passport_payload(user)
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    _, height = A4
    y = height - 50
    pdf.setTitle("DiagnoSure Health Passport")
    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(45, y, "DiagnoSure Health Passport")
    y -= 35
    pdf.setFont("Helvetica", 11)
    for label, value in (("Patient", data["name"]), ("Email", user.email), ("Age", data["age"] or "Not provided"), ("Sex", data["sex"] or "Not provided")):
        pdf.drawString(45, y, f"{label}: {value}")
        y -= 18
    for label, values in (("Allergies", data["allergies"]), ("Conditions", data["conditions"]), ("Medications", data["medications"])):
        pdf.setFont("Helvetica-Bold", 11)
        pdf.drawString(45, y, label)
        y -= 16
        pdf.setFont("Helvetica", 10)
        pdf.drawString(60, y, ", ".join(values) or "None recorded")
        y -= 20
    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawString(45, y, "Health records")
    y -= 16
    pdf.setFont("Helvetica", 10)
    for record in records:
        if y < 55:
            pdf.showPage()
            y = height - 50
        pdf.drawString(60, y, f"{record.title} ({record.category})")
        y -= 16
    pdf.setFont("Helvetica-Oblique", 9)
    pdf.drawString(45, 35, "Private clinical information. Confirm patient identity before use.")
    pdf.save()
    buffer.seek(0)
    return StreamingResponse(buffer, media_type="application/pdf", headers={"Content-Disposition": 'attachment; filename="diagnosure-health-passport.pdf"'})


def shared_passport_user(token: str, db: Session) -> User:
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=["HS256"])
        if payload.get("purpose") != "health_passport":
            raise HTTPException(403, "Invalid passport link")
        user = db.get(User, payload.get("sub"))
    except Exception as exc:
        raise HTTPException(403, "This passport link is invalid or expired") from exc
    if user is None:
        raise HTTPException(404, "Patient not found")
    return user


@app.get("/api/passport/shared/{token}/pdf")
def shared_passport_pdf(token: str, db: Session = Depends(get_db)):
    return build_passport_pdf(shared_passport_user(token, db), db)


@app.patch("/api/patients/me")
def update_patient(request: PatientUpdate, user: User = Depends(current_user), db: Session = Depends(get_db)):
    if request.full_name is not None:
        user.full_name = request.full_name
    db.commit()
    db.refresh(user)
    return patient_profile(user)


@app.get("/api/patients/me/records", response_model=list[HealthRecordResponse])
def list_records(user: User = Depends(current_user), db: Session = Depends(get_db)):
    return list(db.scalars(select(HealthRecord).where(HealthRecord.user_id == user.id).order_by(HealthRecord.created_at.desc())))


@app.post("/api/patients/me/records", response_model=HealthRecordResponse, status_code=201)
def create_record(request: HealthRecordCreate, user: User = Depends(current_user), db: Session = Depends(get_db)):
    record = HealthRecord(user_id=user.id, **request.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@app.get("/api/patients/me/records/{record_id}", response_model=HealthRecordResponse)
def get_record(record_id: str, user: User = Depends(current_user), db: Session = Depends(get_db)):
    return owned_or_404(db, record_id, user)


@app.patch("/api/patients/me/records/{record_id}", response_model=HealthRecordResponse)
def update_record(record_id: str, request: HealthRecordCreate, user: User = Depends(current_user), db: Session = Depends(get_db)):
    record = owned_or_404(db, record_id, user)
    for key, value in request.model_dump().items():
        setattr(record, key, value)
    db.commit()
    db.refresh(record)
    return record


@app.delete("/api/patients/me/records/{record_id}", status_code=204)
def delete_record(record_id: str, user: User = Depends(current_user), db: Session = Depends(get_db)):
    record = owned_or_404(db, record_id, user)
    db.delete(record)
    db.commit()


@app.post("/api/patients/me/records/upload", response_model=HealthRecordResponse, status_code=201)
async def upload_record(
    category: str,
    title: str,
    file: UploadFile = File(...),
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    allowed = {".pdf", ".png", ".jpg", ".jpeg"}
    extension = Path(file.filename or "").suffix.lower()
    if extension not in allowed:
        raise HTTPException(400, "Only PDF, PNG and JPEG files are accepted")
    content = await file.read(settings.max_upload_size_mb * 1024 * 1024 + 1)
    if len(content) > settings.max_upload_size_mb * 1024 * 1024:
        raise HTTPException(413, "Uploaded file is too large")
    safe_name = f"{uuid4().hex}{extension}"
    target = settings.upload_path / safe_name
    target.write_bytes(content)
    record = HealthRecord(user_id=user.id, category=category, title=title, details="", file_path=safe_name)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@app.get("/api/patients/me/records/{record_id}/download")
def download_record(record_id: str, user: User = Depends(current_user), db: Session = Depends(get_db)):
    from fastapi.responses import FileResponse
    record = owned_or_404(db, record_id, user)
    if not record.file_path:
        raise HTTPException(404, "This record has no document")
    path = settings.upload_path / Path(record.file_path).name
    if not path.is_file():
        raise HTTPException(404, "Document is unavailable")
    return FileResponse(path)


@app.post("/api/patients/me/shares", status_code=201)
def create_share(record_id: str, doctor_id: str, expires_at: datetime, user: User = Depends(current_user), db: Session = Depends(get_db)):
    owned_or_404(db, record_id, user)
    doctor = db.get(User, doctor_id)
    if not doctor or doctor.role != "doctor":
        raise HTTPException(404, "Authorized doctor not found")
    if expires_at <= datetime.now(timezone.utc):
        raise HTTPException(400, "Share must expire in the future")
    share = HealthRecordShare(owner_id=user.id, doctor_id=doctor_id, record_id=record_id, expires_at=expires_at)
    db.add(share)
    db.commit()
    db.refresh(share)
    return share


@app.get("/api/patients/me/shares")
def list_shares(user: User = Depends(current_user), db: Session = Depends(get_db)):
    return list(db.scalars(select(HealthRecordShare).where(HealthRecordShare.owner_id == user.id)))


@app.delete("/api/patients/me/shares/{share_id}", status_code=204)
def revoke_share(share_id: str, user: User = Depends(current_user), db: Session = Depends(get_db)):
    share = db.get(HealthRecordShare, share_id)
    if not share or share.owner_id != user.id:
        raise HTTPException(404, "Share not found")
    share.revoked = True
    db.commit()


@app.get("/api/cases/{case_id}")
def get_case(case_id: str, user: User = Depends(current_user), db: Session = Depends(get_db)):
    case = db.get(DiagnosisCase, case_id)
    if not case or case.user_id != user.id:
        raise HTTPException(404, "Case not found")
    return {"case_id": case.id, "status": case.status, "created_at": case.created_at}


@app.get("/api/cases")
def list_cases(user: User = Depends(current_user), db: Session = Depends(get_db)):
    cases = db.scalars(
        select(DiagnosisCase).where(DiagnosisCase.user_id == user.id).order_by(DiagnosisCase.created_at.desc())
    ).all()
    return [
        {
            "case_id": case.id,
            "status": case.status,
            "created_at": case.created_at,
            "top": (json.loads(case.result_json).get("differential_diagnoses") or [{}])[0].get("condition")
            if case.result_json else None,
        }
        for case in cases
    ]


@app.get("/api/cases/{case_id}/results")
def get_case_results(case_id: str, user: User = Depends(current_user), db: Session = Depends(get_db)):
    case = db.get(DiagnosisCase, case_id)
    if not case or case.user_id != user.id or not case.result_json:
        raise HTTPException(404, "Case results not found")
    return json.loads(case.result_json)


@app.get("/api/cases/{case_id}/status")
def get_case_status(case_id: str, user: User = Depends(current_user), db: Session = Depends(get_db)):
    return get_case(case_id, user, db)


@app.get("/api/consultations")
def consultations(user: User = Depends(current_user), db: Session = Depends(get_db)):
    return list(db.scalars(select(Consultation).where((Consultation.patient_id == user.id) | (Consultation.doctor_id == user.id))))


@app.get("/api/doctors")
def doctors(user: User = Depends(current_user), db: Session = Depends(get_db)):
    return [
        {"id": doctor.id, "name": doctor.full_name, "specialty": "Healthcare consultation"}
        for doctor in db.scalars(select(User).where(User.role == "doctor").order_by(User.full_name))
    ]


@app.post("/api/consultations", status_code=201)
def create_consultation(request: ConsultationCreate, user: User = Depends(current_user), db: Session = Depends(get_db)):
    if request.doctor_id and (not db.get(User, request.doctor_id) or db.get(User, request.doctor_id).role != "doctor"):
        raise HTTPException(404, "Doctor not found")
    video = jitsi_provider.create_room()
    item = Consultation(
        patient_id=user.id,
        **video,
        **request.model_dump(),
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@app.patch("/api/consultations/{consultation_id}/status")
def update_consultation_status(consultation_id: str, request: ConsultationUpdate, user: User = Depends(current_user), db: Session = Depends(get_db)):
    item = get_consultation(consultation_id, user, db)
    if user.role != "doctor" or item.doctor_id != user.id:
        raise HTTPException(403, "Only the assigned doctor can update consultation status")
    if request.status not in {"accepted", "completed", "cancelled"}:
        raise HTTPException(422, "Doctor status must be accepted, completed, or cancelled")
    item.status = request.status
    if request.notes is not None:
        item.notes = request.notes
    db.commit()
    db.refresh(item)
    return item


@app.get("/api/consultations/{consultation_id}")
def get_consultation(consultation_id: str, user: User = Depends(current_user), db: Session = Depends(get_db)):
    item = db.get(Consultation, consultation_id)
    if not item or user.id not in {item.patient_id, item.doctor_id}:
        raise HTTPException(404, "Consultation not found")
    return item


@app.patch("/api/consultations/{consultation_id}")
def update_consultation(consultation_id: str, request: ConsultationUpdate, user: User = Depends(current_user), db: Session = Depends(get_db)):
    item = get_consultation(consultation_id, user, db)
    for key, value in request.model_dump(exclude_unset=True).items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return item


@app.delete("/api/consultations/{consultation_id}", status_code=204)
def cancel_consultation(consultation_id: str, user: User = Depends(current_user), db: Session = Depends(get_db)):
    item = get_consultation(consultation_id, user, db)
    item.status = "cancelled"
    db.commit()


@app.get("/api/consultations/{consultation_id}/join")
def consultation_join(consultation_id: str, user: User = Depends(current_user), db: Session = Depends(get_db)):
    item = get_consultation(consultation_id, user, db)
    return {
        "consultation_id": item.id,
        "video_provider": item.video_provider,
        "room": item.video_room,
        "video_url": item.video_url,
        "moderator_required": item.video_provider == "jitsi",
        "moderator_instructions": "On meet.jit.si, the doctor must sign in to become the room moderator. The patient can then join the same room.",
        "jitsi_external_api": "https://meet.jit.si/external_api.js",
    }


@app.get("/api/patients/me/health-summary")
def health_summary(user: User = Depends(current_user), db: Session = Depends(get_db)):
    records = db.scalars(select(HealthRecord).where(HealthRecord.user_id == user.id)).all()
    return {
        "conditions": json.loads(user.conditions or "[]") + [r.details for r in records if r.category == "condition"],
        "allergies": json.loads(user.allergies or "[]") + [r.details for r in records if r.category == "allergy"],
        "medications": json.loads(user.medications or "[]") + [r.details for r in records if r.category == "medication"],
        "medical_history": user.medical_history,
        "vaccinations": [{"name": r.title, "date": r.created_at} for r in records if r.category == "vaccination"],
        "aiSummary": {"text": "No generated health summary is available.", "sources": []},
    }


@app.get("/api/clinics")
async def clinics(latitude: float | None = None, longitude: float | None = None, radius_km: float = 25):
    if latitude is None or longitude is None:
        raise HTTPException(422, "latitude and longitude are required")
    if settings.maps_provider not in {"", "osm_overpass"}:
        return {"status": "provider_unavailable", "clinics": [], "message": f"Unsupported maps provider: {settings.maps_provider}"}
    if radius_km <= 0 or radius_km > 100:
        raise HTTPException(422, "radius_km must be between 0 and 100")
    try:
        results = await clinic_provider.search(latitude, longitude, radius_km)
    except ClinicProviderUnavailable as exc:
        return {"status": "provider_unavailable", "clinics": [], "message": exc.message}
    return {
        "status": "completed",
        "provider": "osm_overpass",
        "tile_url": settings.maps_tile_url,
        "attribution": "© OpenStreetMap contributors",
        "clinics": results,
    }


@app.get("/api/reminders")
def reminders(user: User = Depends(current_user), db: Session = Depends(get_db)):
    return list(db.scalars(select(Reminder).where(Reminder.user_id == user.id).order_by(Reminder.scheduled_at)))


@app.post("/api/reminders", status_code=201)
def create_reminder(request: ReminderCreate, user: User = Depends(current_user), db: Session = Depends(get_db)):
    item = Reminder(user_id=user.id, **request.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@app.get("/api/reminders/{reminder_id}")
def get_reminder(reminder_id: str, user: User = Depends(current_user), db: Session = Depends(get_db)):
    item = db.get(Reminder, reminder_id)
    if not item or item.user_id != user.id:
        raise HTTPException(404, "Reminder not found")
    return item


@app.patch("/api/reminders/{reminder_id}")
def update_reminder(reminder_id: str, request: ReminderUpdate, user: User = Depends(current_user), db: Session = Depends(get_db)):
    item = db.get(Reminder, reminder_id)
    if not item or item.user_id != user.id:
        raise HTTPException(404, "Reminder not found")
    for key, value in request.model_dump(exclude_unset=True).items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return item


@app.post("/api/reminders/{reminder_id}/complete")
def complete_reminder(reminder_id: str, user: User = Depends(current_user), db: Session = Depends(get_db)):
    item = update_reminder(reminder_id, ReminderUpdate(active=False), user, db)
    item.completed_at = datetime.now(timezone.utc)
    db.commit()
    return item


@app.post("/api/reminders/{reminder_id}/snooze")
def snooze_reminder(reminder_id: str, minutes: int = 30, user: User = Depends(current_user), db: Session = Depends(get_db)):
    if minutes < 1 or minutes > 24 * 60:
        raise HTTPException(422, "minutes must be between 1 and 1440")
    item = get_reminder(reminder_id, user, db)
    item.scheduled_at = datetime.now(timezone.utc) + timedelta(minutes=minutes)
    db.commit()
    db.refresh(item)
    return item


@app.get("/api/reminders/preferences")
def reminder_preferences(user: User = Depends(current_user)):
    return {
        "user_id": user.id,
        "notification_provider": settings.notification_provider,
        "status": "configured" if settings.notification_provider == "local" else "not_configured",
        "browser": False,
        "reminders": True,
        "appointments": True,
        "followups": True,
        "quietStart": "22:00",
        "quietEnd": "07:00",
    }


@app.patch("/api/reminders/preferences")
def update_reminder_preferences(user: User = Depends(current_user), db: Session = Depends(get_db)):
    return reminder_preferences(user)


@app.delete("/api/reminders/{reminder_id}", status_code=204)
def delete_reminder(reminder_id: str, user: User = Depends(current_user), db: Session = Depends(get_db)):
    item = db.get(Reminder, reminder_id)
    if not item or item.user_id != user.id:
        raise HTTPException(404, "Reminder not found")
    db.delete(item)
    db.commit()


@app.get("/api/research/{metric}")
def research(metric: str):
    if metric not in {"summary", "baseline", "ablations"}:
        raise HTTPException(404, "Research endpoint not found")
    return {"status": "not_available", "metric": metric, "message": "No reproducible evaluation dataset is configured."}


@app.websocket("/api/consultations/{consultation_id}/ws")
async def consultation_socket(websocket: WebSocket, consultation_id: str, db: Session = Depends(get_db)):
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=1008)
        return
    try:
        user = current_user(token, db)
    except HTTPException:
        await websocket.close(code=1008)
        return
    consultation = db.get(Consultation, consultation_id)
    if not consultation or user.id not in {consultation.patient_id, consultation.doctor_id}:
        await websocket.close(code=1008)
        return
    await websocket.accept()
    try:
        while True:
            message = await websocket.receive_json()
            if not isinstance(message, dict) or message.get("type") not in {"offer", "answer", "ice-candidate"}:
                await websocket.send_json({"error": {"code": "INVALID_SIGNAL", "message": "Unsupported signaling payload"}})
                continue
            await websocket.send_json({"type": "signaling", "consultation_id": consultation_id, "payload": message})
    except WebSocketDisconnect:
        return

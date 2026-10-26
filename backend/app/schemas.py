from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class ErrorBody(BaseModel):
    code: str
    message: str
    details: list[Any] = []


class RegisterRequest(BaseModel):
    email: str
    password: str = Field(min_length=8)
    full_name: str = Field(min_length=1, max_length=200)
    role: Literal["patient", "doctor"] = "patient"
    age: int | None = Field(default=None, ge=0, le=130)
    sex: str | None = None
    allergies: list[str] = []
    conditions: list[str] = []
    medications: list[str] = []
    medical_history: str = Field(default="", max_length=10000)


class LoginRequest(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    email: str
    full_name: str
    role: str


class PatientUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=1, max_length=200)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class AnalyzeRequest(BaseModel):
    natural_language_input: str = Field(default="", max_length=10000)
    symptoms: list[dict[str, Any]] = []
    age: int | None = Field(default=None, ge=0, le=130)
    sex: str | None = None
    medical_history: list[str] = []
    current_medications: list[str] = []
    allergies: list[str] = []
    additional_notes: str = Field(default="", max_length=10000)
    use_health_passport: bool = False
    conditions: list[str] = []
    additional_symptoms: list[str] = []
    negative_symptoms: list[str] = []
    history: str = ""
    notes: str = ""

    def clinical_text(self) -> str:
        if self.natural_language_input.strip():
            return self.natural_language_input.strip()
        symptoms = ", ".join(
            str(item.get("name", item.get("symptom", ""))) for item in self.symptoms
        )
        parts = [f"Symptoms: {symptoms}" if symptoms else ""]
        if self.age is not None:
            parts.append(f"Age: {self.age}")
        if self.sex:
            parts.append(f"Sex: {self.sex}")
        history = self.medical_history or self.conditions
        if history:
            parts.append(f"Medical history: {', '.join(history)}")
        if self.current_medications:
            parts.append(f"Current medications: {', '.join(self.current_medications)}")
        if self.allergies:
            parts.append(f"Allergies: {', '.join(self.allergies)}")
        if self.additional_notes:
            parts.append(self.additional_notes)
        if self.additional_symptoms:
            parts.append(f"Additional symptoms: {', '.join(self.additional_symptoms)}")
        if self.negative_symptoms:
            parts.append(f"Absent symptoms: {', '.join(self.negative_symptoms)}")
        if self.history:
            parts.append(self.history)
        if self.notes:
            parts.append(self.notes)
        return ". ".join(part for part in parts if part)


class HealthRecordCreate(BaseModel):
    category: str = Field(min_length=1, max_length=40)
    title: str = Field(min_length=1, max_length=200)
    details: str = ""


class HealthRecordResponse(HealthRecordCreate):
    model_config = ConfigDict(from_attributes=True)
    id: str
    created_at: datetime


class ConsultationUpdate(BaseModel):
    scheduled_at: datetime | None = None
    status: Literal["requested", "accepted", "completed", "cancelled"] | None = None
    notes: str | None = None


class ConsultationCreate(BaseModel):
    scheduled_at: datetime
    doctor_id: str | None = None
    notes: str = ""


class ReminderCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    reminder_type: Literal["medication", "follow_up", "general"]
    scheduled_at: datetime
    recurrence: Literal["daily", "weekly", "monthly"] | None = None


class ReminderUpdate(BaseModel):
    title: str | None = None
    scheduled_at: datetime | None = None
    recurrence: Literal["daily", "weekly", "monthly"] | None = None
    active: bool | None = None

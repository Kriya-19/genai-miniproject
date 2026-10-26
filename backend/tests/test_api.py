import sys
from uuid import uuid4

sys.path.insert(0, ".")

from fastapi.testclient import TestClient

from app.main import app, diagnosis_service


async def fake_analysis(_: str):
    return {
        "status": "success",
        "symptom_extraction": {"extracted_symptoms": [{"symptom": "cough"}]},
        "top_5_diagnoses": [{"condition": "Common Cold", "confidence": 0.8}],
        "safety_warnings": [],
        "report": "Decision support output",
    }


def test_health_and_openapi():
    with TestClient(app) as client:
        assert client.get("/health").json()["status"] == "ok"
        assert client.get("/openapi.json").status_code == 200


def test_authenticated_analysis_is_persisted():
    diagnosis_service.adapter.analyze = fake_analysis
    email = f"{uuid4()}@example.com"
    with TestClient(app) as client:
        response = client.post(
            "/api/auth/register",
            json={"email": email, "password": "password123", "full_name": "Test User"},
        )
        assert response.status_code == 201
        headers = {"Authorization": f"Bearer {response.json()['access_token']}"}
        response = client.post(
            "/api/analyze",
            headers=headers,
            json={"symptoms": [{"name": "cough"}]},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "completed"
        assert body["differential_diagnoses"][0]["score_type"] == "ranking_score"
        assert client.get(f"/api/cases/{body['case_id']}", headers=headers).status_code == 200

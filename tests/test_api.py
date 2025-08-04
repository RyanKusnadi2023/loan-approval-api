import pytest
from fastapi.testclient import TestClient
from app.main import app

# Create a TestClient for our FastAPI app
client = TestClient(app)

# A valid payload matching LoanApplication schema
def valid_payload():
    return {
        "person_age": 35.0,
        "person_gender": "male",
        "person_education": "Bachelor",
        "person_income": 60000.0,
        "person_emp_exp": 10,
        "person_home_ownership": "RENT",
        "loan_amnt": 10000.0,
        "loan_intent": "PERSONAL",
        "loan_int_rate": 12.5,
        "loan_percent_income": 0.15,
        "cb_person_cred_hist_length": 4.0,
        "credit_score": 720,
        "previous_loan_defaults_on_file": "No"
    }


def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Running"
    assert "message" in data


def test_predict_success():
    response = client.post("/predict", json=valid_payload())
    assert response.status_code == 200
    data = response.json()
    # The API should return prediction, confidence, and status
    assert set(data.keys()) == {"prediction", "confidence", "status"}
    assert isinstance(data["prediction"], int)
    assert isinstance(data["confidence"], float)
    assert data["status"] in ("Approved", "Rejected")


def test_predict_invalid_type():
    # person_age must be > 0, so -1 should cause a 422
    bad = valid_payload()
    bad["person_age"] = -1
    response = client.post("/predict", json=bad)
    assert response.status_code == 422


def test_predict_missing_field():
    # Remove a required field
    bad = valid_payload()
    bad.pop("loan_amnt")
    response = client.post("/predict", json=bad)
    assert response.status_code == 422


def test_predict_extra_field():
    # Extra unexpected field should also 422 or ignore based on config
    payload = valid_payload()
    payload["unexpected"] = "value"
    response = client.post("/predict", json=payload)
    assert response.status_code in (422, 200)
    # If the app is set to ignore extra, ensure correct keys
    if response.status_code == 200:
        data = response.json()
        assert set(data.keys()) == {"prediction", "confidence", "status"}

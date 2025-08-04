import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch, MagicMock, mock_open
from app.schemas import validate_payload
from app import services

@pytest.fixture
def valid_payload():
    return {
        "person_age": 30,
        "person_gender": "male",
        "person_education": "Bachelor",
        "person_income": 50000,
        "person_emp_exp": 5,
        "person_home_ownership": "OWN",
        "loan_amnt": 10000,
        "loan_intent": "PERSONAL",
        "loan_int_rate": 10.5,
        "loan_percent_income": 0.2,
        "cb_person_cred_hist_length": 3,
        "credit_score": 700,
        "previous_loan_defaults_on_file": "No"
    }

@pytest.fixture
def mock_logger():
    return MagicMock()

# ---------- Schema Validation Tests ----------
def test_valid_payload(valid_payload, mock_logger):
    is_valid, errors = validate_payload(valid_payload, mock_logger)

    assert is_valid is True
    assert errors is None
    mock_logger.info.assert_called_once_with("Payload validated successfully.")

def test_invalid_age_payload(valid_payload, mock_logger):
    invalid_payload = valid_payload.copy()
    invalid_payload["person_age"] = -5

    is_valid, errors = validate_payload(invalid_payload, mock_logger)

    assert is_valid is False
    assert errors is not None
    assert any(e["loc"] == ("person_age",) and e["type"] == "greater_than" for e in errors)
    mock_logger.warning.assert_called()

def test_missing_field_payload(valid_payload, mock_logger):
    invalid_payload = valid_payload.copy()
    invalid_payload.pop("loan_amnt")

    is_valid, errors = validate_payload(invalid_payload, mock_logger)

    assert is_valid is False
    assert any(e["loc"] == ("loan_amnt",) and e["type"] == "missing" for e in errors)
    mock_logger.warning.assert_called()

def test_invalid_enum_payload(valid_payload, mock_logger):
    invalid_payload = valid_payload.copy()
    invalid_payload["person_gender"] = "other"

    is_valid, errors = validate_payload(invalid_payload, mock_logger)

    assert is_valid is False
    assert any(e["loc"] == ("person_gender",) and e["type"] == "literal_error" for e in errors)
    mock_logger.warning.assert_called()
    
def test_invalid_type_payload(valid_payload, mock_logger):
    invalid_payload = valid_payload.copy()
    invalid_payload["credit_score"] = "high"

    is_valid, errors = validate_payload(invalid_payload, mock_logger)

    assert is_valid is False
    assert any(e["loc"] == ("credit_score",) for e in errors)

def test_unexpected_error(mock_logger):
    invalid_payload = "this is not a dict"

    is_valid, errors = validate_payload(invalid_payload, mock_logger)

    assert is_valid is False
    assert "error" in errors
    mock_logger.exception.assert_called()

def test_multiple_errors_payload(valid_payload, mock_logger):
    invalid_payload = valid_payload.copy()
    invalid_payload["person_age"] = -10
    invalid_payload["person_income"] = -100

    is_valid, errors = validate_payload(invalid_payload, mock_logger)

    assert is_valid is False
    assert len(errors) >= 2

@pytest.mark.parametrize("field", [
    "person_income", "person_emp_exp", "loan_int_rate", 
    "loan_percent_income", "cb_person_cred_hist_length", "credit_score"
])
def test_zero_values_allowed(valid_payload, mock_logger, field):
    valid_payload[field] = 0
    is_valid, errors = validate_payload(valid_payload, mock_logger)
    assert is_valid is True
    assert errors is None

# ---------- Services Tests ----------
def test_load_resources_success(mock_logger):
    mock_model = MagicMock()
    mock_scaler = MagicMock()
    mock_features = ['f1', 'f2']

    fake_yaml = {
        "gender_map": {"male": 1, "female": 0},
        "default_map": {"Yes": 1, "No": 0},
        "education_order": {"High School": 0, "Bachelor": 1},
        "home_ownership_options": ["RENT", "OWN"],
        "loan_intent_options": ["PERSONAL", "EDUCATION"]
    }

    with patch("app.services.joblib.load", side_effect=[mock_model, mock_scaler, mock_features]), \
         patch("builtins.open", mock_open(read_data="config")), \
         patch("app.services.yaml.safe_load", return_value=fake_yaml):

        services.load_resources(mock_logger)

        assert services.model == mock_model
        assert services.scaler == mock_scaler
        assert services.features == mock_features
        assert services.gender_map == fake_yaml["gender_map"]

def test_preprocess_input_success(valid_payload, mock_logger):
    services.gender_map = {"male": 1, "female": 0}
    services.default_map = {"Yes": 1, "No": 0}
    services.education_order = {"Bachelor": 1}
    services.home_ownership_options = ["RENT", "OWN"]
    services.loan_intent_options = ["EDUCATION", "PERSONAL"]
    services.features = [
        'person_age', 'person_gender', 'person_education', 'person_income',
        'person_emp_exp', 'loan_amnt', 'loan_int_rate', 'loan_percent_income',
        'cb_person_cred_hist_length', 'credit_score', 'previous_loan_defaults_on_file',
        'person_home_ownership_OWN', 'loan_intent_PERSONAL'
    ]

    df = services.preprocess_input(valid_payload, mock_logger)

    assert isinstance(df, pd.DataFrame)
    assert set(df.columns) == set(services.features)
    assert df.shape == (1, len(services.features))

def test_predict_success(mock_logger):
    services.scaler = MagicMock()
    services.model = MagicMock()

    df = pd.DataFrame([[1]*13], columns=[
        'person_age', 'person_gender', 'person_education', 'person_income',
        'person_emp_exp', 'loan_amnt', 'loan_int_rate', 'loan_percent_income',
        'cb_person_cred_hist_length', 'credit_score', 'previous_loan_defaults_on_file',
        'person_home_ownership_OWN', 'loan_intent_PERSONAL'
    ])

    services.scaler.transform.return_value = df.values
    services.model.predict_proba.return_value = np.array([[0.1, 0.9]])

    result = services.predict(df, mock_logger)

    assert result["prediction"] == 1
    assert abs(result["confidence"] - 0.9) < 1e-5

def test_predict_model_not_loaded(mock_logger):
    services.scaler = None
    df = pd.DataFrame([[1]*3])
    
    with pytest.raises(RuntimeError):
        services.predict(df, mock_logger)
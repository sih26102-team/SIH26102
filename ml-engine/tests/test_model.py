import pytest
import joblib
import pandas as pd
import os

@pytest.fixture(scope="module")
def ml_engine():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(current_dir, "..", "models", "model.pkl")
    return joblib.load(model_path)

def test_massive_overspend_blocked(ml_engine):
    # Payload 1: Blatant Theft
    payload = pd.DataFrame({
        'sanctioned_amount': [2000000],
        'expenditure': [50000000],
        'progress_percent': [100.0],
        'burn_rate': [50000000 / 101.0]
    })
    prediction = ml_engine.predict(payload)
    assert prediction[0] == -1, "VULNERABILITY: Model allowed massive overspending."

def test_contextual_fraud_blocked(ml_engine):
    # Payload 2: Siphoning
    payload = pd.DataFrame({
        'sanctioned_amount': [200000],
        'expenditure': [2000000],
        'progress_percent': [10.0],
        'burn_rate': [2000000 / 11.0]
    })
    prediction = ml_engine.predict(payload)
    assert prediction[0] == -1, "VULNERABILITY: Model failed to catch contextual siphoning."

def test_ghost_project_blocked(ml_engine):
    # Payload 3: Ghost Project (High Spend, Zero Progress)
    payload = pd.DataFrame({
        'sanctioned_amount': [1500000],
        'expenditure': [15000000],
        'progress_percent': [0.0],
        'burn_rate': [15000000 / 1.0]
    })
    prediction = ml_engine.predict(payload)
    assert prediction[0] == -1, "VULNERABILITY: Model allowed a Ghost Project."

def test_normal_spending_allowed(ml_engine):
    # Payload 4: Safe Normal Project
    payload = pd.DataFrame({
        'sanctioned_amount': [1000000],
        'expenditure': [476918],
        'progress_percent': [43.0],
        'burn_rate': [476918 / 44.0]
    })
    prediction = ml_engine.predict(payload)
    assert prediction[0] == 1, "VULNERABILITY: Model is flagging legitimate projects."
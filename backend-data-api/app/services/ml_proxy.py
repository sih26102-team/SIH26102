import requests

from app.core.config import settings
from app.core.exceptions import MLServiceError
from app.core.logging_config import logger


def score_transaction(transaction_payload: dict) -> dict:
    
    url = f"{settings.ML_SERVICE_URL}/predict"
    try:
        response = requests.post(
            url,
            json=transaction_payload,
            timeout=settings.ML_SERVICE_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as exc:
        logger.error(f"ML service call failed: {exc}")
        raise MLServiceError(detail="Could not reach anomaly-scoring service") from exc


def score_transactions_batch(transaction_payloads: list[dict]) -> list[dict]:
    url = f"{settings.ML_SERVICE_URL}/predict/batch"
    try:
        response = requests.post(
            url,
            json={"transactions": transaction_payloads},
            timeout=settings.ML_SERVICE_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        return response.json().get("results", [])
    except requests.exceptions.RequestException as exc:
        logger.error(f"ML batch service call failed: {exc}")
        raise MLServiceError(detail="Could not reach anomaly-scoring service") from exc

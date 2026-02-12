import json

from src.services.ingress.handler import lambda_handler


def test_ingress_returns_200_and_event_id(monkeypatch) -> None:
    monkeypatch.delenv("QUEUE_URL", raising=False)

    response = lambda_handler({"hello": "world"}, None)

    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert body["message"] == "Phase 0 ingress skeleton is healthy."
    assert "event_id" in body


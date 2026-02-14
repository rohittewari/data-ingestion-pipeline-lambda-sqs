import json
from unittest.mock import MagicMock, patch

from src.services.consumer.handler import _build_projection, _extract_event_envelope, lambda_handler


def _sns_wrapped_record(message_id: str = "m-1") -> dict[str, str]:
    envelope = {
        "event_id": "e-1",
        "event_version": "v1",
        "ingested_at": "2026-02-12T10:00:00Z",
        "user_id": "user-123",
        "payload": {
            "event_type": "user.created",
            "source": "user-service",
            "occurred_at": "2026-02-12T10:00:00Z",
            "payload": {"user_id": "123"},
        },
    }
    sns_body = {
        "Type": "Notification",
        "MessageId": "sns-1",
        "TopicArn": "arn:aws:sns:us-east-1:123456789012:event-pipeline-topic-dev",
        "Message": json.dumps(envelope),
    }
    return {"messageId": message_id, "body": json.dumps(sns_body)}


def test_extract_event_envelope_supports_sns_wrapped_messages() -> None:
    record = _sns_wrapped_record()

    result = _extract_event_envelope(record)

    assert result["event_id"] == "e-1"
    assert result["event_version"] == "v1"
    assert result["payload"]["event_type"] == "user.created"


def test_build_projection_extracts_projection_fields() -> None:
    event_envelope = {
        "event_id": "e-1",
        "event_version": "v1",
        "ingested_at": "2026-02-12T10:00:00Z",
        "user_id": "user-123",
        "payload": {
            "event_type": "user.created",
            "source": "user-service",
            "occurred_at": "2026-02-12T10:00:00Z",
            "payload": {"user_id": "123"},
        },
    }

    projection = _build_projection(event_envelope)

    assert projection["event_type"] == "user.created"
    assert projection["source"] == "user-service"
    assert projection["occurred_at"] == "2026-02-12T10:00:00Z"
    assert projection["user_id"] == "user-123"
    assert projection["payload"] == {"user_id": "123"}


@patch("src.services.consumer.handler._persist_event")
@patch("src.services.consumer.handler._get_db_engine")
def test_consumer_processes_batch_records(
    mock_get_db_engine: MagicMock,
    mock_persist_event: MagicMock,
    monkeypatch,
) -> None:
    monkeypatch.setenv("DB_URL", "postgresql://user:pass@localhost:5432/events")
    monkeypatch.setenv("CONSUMER_NAME", "projection-consumer")

    mock_get_db_engine.return_value = MagicMock()
    event = {
        "Records": [
            _sns_wrapped_record("m-1"),
            _sns_wrapped_record("m-2"),
        ]
    }

    response = lambda_handler(event, None)

    assert response["processed_count"] == 2
    assert response["failed_count"] == 0
    assert response["batchItemFailures"] == []
    assert mock_persist_event.call_count == 2


@patch("src.services.consumer.handler._get_db_engine")
def test_consumer_returns_failure_for_invalid_record(
    mock_get_db_engine: MagicMock,
    monkeypatch,
) -> None:
    monkeypatch.setenv("DB_URL", "postgresql://user:pass@localhost:5432/events")
    mock_get_db_engine.return_value = MagicMock()
    event = {"Records": [{"messageId": "m-bad", "body": "not-json"}]}

    response = lambda_handler(event, None)

    assert response["processed_count"] == 0
    assert response["failed_count"] == 1
    assert response["batchItemFailures"] == [{"itemIdentifier": "m-bad"}]


def test_consumer_fails_batch_when_db_url_missing(monkeypatch) -> None:
    monkeypatch.delenv("DB_URL", raising=False)
    event = {"Records": [_sns_wrapped_record("m-1"), _sns_wrapped_record("m-2")]}

    response = lambda_handler(event, None)

    assert response["processed_count"] == 0
    assert response["failed_count"] == 2
    assert response["batchItemFailures"] == [
        {"itemIdentifier": "m-1"},
        {"itemIdentifier": "m-2"},
    ]

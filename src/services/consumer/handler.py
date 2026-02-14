import json
import os
from datetime import UTC, datetime
from functools import lru_cache
from typing import Any

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine


@lru_cache(maxsize=1)
def _get_db_engine(db_url: str) -> Engine:
    return create_engine(db_url, pool_pre_ping=True)


def _parse_iso8601(timestamp: str) -> datetime:
    return datetime.fromisoformat(timestamp.replace("Z", "+00:00"))


def _extract_event_envelope(record: dict[str, Any]) -> dict[str, Any]:
    body = record.get("body", "{}")

    try:
        decoded_body = json.loads(body)
    except json.JSONDecodeError as exc:
        raise ValueError("Invalid SQS message JSON") from exc

    if not isinstance(decoded_body, dict):
        raise ValueError("Invalid SQS message: expected JSON object")

    # Messages from SNS subscriptions arrive in SQS with an SNS wrapper.
    message = decoded_body.get("Message", decoded_body)
    if isinstance(message, str):
        try:
            message = json.loads(message)
        except json.JSONDecodeError as exc:
            raise ValueError("Invalid SNS message body JSON") from exc

    if not isinstance(message, dict):
        raise ValueError("Invalid event envelope: expected JSON object")

    required_fields = {"event_id", "event_version", "ingested_at", "payload"}
    missing_fields = required_fields.difference(message.keys())
    if missing_fields:
        missing = ", ".join(sorted(missing_fields))
        raise ValueError(f"Missing required envelope field(s): {missing}")

    return message


def _build_projection(event_envelope: dict[str, Any]) -> dict[str, Any]:
    event_payload = event_envelope.get("payload", {})
    if not isinstance(event_payload, dict):
        event_payload = {"raw_payload": event_payload}

    return {
        "event_type": event_payload.get("event_type"),
        "source": event_payload.get("source"),
        "occurred_at": event_payload.get("occurred_at"),
        "user_id": event_envelope.get("user_id"),
        "payload": event_payload.get("payload"),
    }


def _persist_event(
    engine: Engine,
    event_envelope: dict[str, Any],
    projection: dict[str, Any],
    consumer_name: str,
) -> None:
    with engine.begin() as connection:
        connection.execute(
            text(
                """
                INSERT INTO raw_events (event_id, event_version, payload_json, ingested_at)
                VALUES (:event_id, :event_version, :payload_json, :ingested_at)
                ON CONFLICT (event_id) DO NOTHING
                """
            ),
            {
                "event_id": event_envelope["event_id"],
                "event_version": event_envelope["event_version"],
                "payload_json": json.dumps(event_envelope, separators=(",", ":")),
                "ingested_at": _parse_iso8601(event_envelope["ingested_at"]),
            },
        )

        connection.execute(
            text(
                """
                INSERT INTO projections (consumer_name, event_id, projection_json, processed_at)
                VALUES (:consumer_name, :event_id, :projection_json, :processed_at)
                ON CONFLICT (consumer_name, event_id) DO NOTHING
                """
            ),
            {
                "consumer_name": consumer_name,
                "event_id": event_envelope["event_id"],
                "projection_json": json.dumps(projection, separators=(",", ":")),
                "processed_at": datetime.now(UTC),
            },
        )


def lambda_handler(event: dict[str, Any], _context: Any) -> dict[str, Any]:
    records = event.get("Records", [])
    consumer_name = os.getenv("CONSUMER_NAME", "default-consumer")
    db_url = os.getenv("DB_URL", "")

    processed_count = 0
    failed_count = 0
    batch_item_failures: list[dict[str, str]] = []

    if not db_url and records:
        print("DB_URL is not configured for consumer Lambda.")
        return {
            "processed_count": 0,
            "failed_count": len(records),
            "batchItemFailures": [
                {"itemIdentifier": record.get("messageId", "")} for record in records
            ],
        }

    db_engine = _get_db_engine(db_url) if db_url else None

    for record in records:
        message_id = record.get("messageId", "")
        try:
            event_envelope = _extract_event_envelope(record)
            projection = _build_projection(event_envelope)
            if db_engine is None:
                raise ValueError("Database engine is not available")

            _persist_event(db_engine, event_envelope, projection, consumer_name)
            processed_count += 1
        except Exception as exc:  # noqa: BLE001
            failed_count += 1
            batch_item_failures.append({"itemIdentifier": message_id})
            print(f"Failed to process record {message_id}: {exc}")

    return {
        "processed_count": processed_count,
        "failed_count": failed_count,
        "batchItemFailures": batch_item_failures,
    }

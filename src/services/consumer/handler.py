import json
from typing import Any


def lambda_handler(event: dict[str, Any], _context: Any) -> dict[str, Any]:
    records = event.get("Records", [])
    processed = []

    for record in records:
        body = record.get("body", "{}")
        try:
            payload = json.loads(body)
        except json.JSONDecodeError:
            payload = {"raw_body": body}

        processed.append({"message_id": record.get("messageId"), "payload": payload})

    return {"processed_count": len(processed), "processed_records": processed}


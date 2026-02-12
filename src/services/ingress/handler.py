import json
import os
import uuid
from typing import Any

import boto3


def lambda_handler(event: dict[str, Any], _context: Any) -> dict[str, Any]:
    event_id = str(uuid.uuid4())
    envelope = {"event_id": event_id, "event_version": "v1", "payload": event}

    queue_url = os.getenv("QUEUE_URL", "")
    if queue_url:
        sqs_client = boto3.client("sqs")
        sqs_client.send_message(
            QueueUrl=queue_url,
            MessageBody=json.dumps(envelope),
        )

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(
            {
                "message": "Phase 0 ingress skeleton is healthy.",
                "event_id": event_id,
            }
        ),
    }


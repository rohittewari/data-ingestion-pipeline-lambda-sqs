"""
Ingress Lambda Handler for Event Ingestion API

Responsibilities:
- Parse incoming API Gateway events
- Validate required payload fields
- Generate event_id and versioned envelope
- Publish to SNS topic
- Return appropriate status codes (202, 400, 401)
"""

import json
import os
import uuid
from typing import Any, Dict, Optional
from datetime import datetime, timezone

import boto3
from botocore.exceptions import ClientError


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    API Gateway Lambda Handler for POST /v1/events
    
    Args:
        event: API Gateway proxy integration event
        context: Lambda context
        
    Returns:
        API Gateway response format with status code and body
    """
    try:
        # Extract request body
        body = event.get("body")
        if not body:
            return _error_response(400, "Request body is required")
        
        # Parse JSON payload
        try:
            payload = json.loads(body) if isinstance(body, str) else body
        except json.JSONDecodeError:
            return _error_response(400, "Invalid JSON in request body")
        
        # Validate required fields
        validation_error = _validate_payload(payload)
        if validation_error:
            return _error_response(400, validation_error)
        
        # Generate event_id
        event_id = str(uuid.uuid4())
        
        # Get user_id from authorizer context (passed by Lambda Authorizer)
        user_id = event.get("requestContext", {}).get("authorizer", {}).get("user_id", "unknown")
        
        # Build event envelope
        envelope = {
            "event_id": event_id,
            "event_version": "v1",
            "ingested_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "user_id": user_id,
            "payload": payload
        }
        
        # Publish to SNS (configured to forward to SQS)
        sns_topic_arn = os.getenv("SNS_TOPIC_ARN", "")
        if sns_topic_arn:
            sns_client = boto3.client("sns")
            try:
                sns_client.publish(
                    TopicArn=sns_topic_arn,
                    Message=json.dumps(envelope),
                    MessageAttributes={
                        "event_type": {"DataType": "String", "StringValue": payload.get("event_type", "")},
                        "event_id": {"DataType": "String", "StringValue": event_id},
                    }
                )
            except ClientError as e:
                print(f"Error publishing to SNS: {e}")
                return _error_response(500, "Failed to publish event")
        
        # Return 202 Accepted
        return {
            "statusCode": 202,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "message": "Event accepted for processing",
                "event_id": event_id,
                "ingested_at": envelope["ingested_at"]
            })
        }
    
    except Exception as e:
        print(f"Unexpected error in ingress handler: {e}")
        return _error_response(500, "Internal server error")


def _validate_payload(payload: Dict[str, Any]) -> Optional[str]:
    """
    Validate required fields in the event payload
    
    Args:
        payload: The event payload to validate
        
    Returns:
        Error message if validation fails, None if valid
    """
    if not isinstance(payload, dict):
        return "Invalid payload: request body must be a JSON object"

    required_fields = {
        "event_type": str,
        "occurred_at": str,
        "source": str,
        "payload": (dict, type(None))  # payload can be optional object or null
    }
    
    for field, expected_type in required_fields.items():
        if field not in payload:
            return f"Missing required field: {field}"
        
        value = payload[field]
        if value is None and field == "payload":
            # payload can be null
            continue
        
        if isinstance(expected_type, tuple):
            if not isinstance(value, expected_type):
                return f"Invalid type for field '{field}': expected {expected_type}, got {type(value).__name__}"
        else:
            if not isinstance(value, expected_type):
                return f"Invalid type for field '{field}': expected {expected_type.__name__}, got {type(value).__name__}"
    
    # Validate that occurred_at is a valid ISO 8601 timestamp
    try:
        datetime.fromisoformat(payload["occurred_at"].replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return "Invalid ISO 8601 timestamp for 'occurred_at' field"
    
    return None


def _error_response(status_code: int, message: str) -> Dict[str, Any]:
    """
    Generate an error response
    
    Args:
        status_code: HTTP status code
        message: Error message
        
    Returns:
        API Gateway response format
    """
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({
            "error": message,
            "status_code": status_code
        })
    }


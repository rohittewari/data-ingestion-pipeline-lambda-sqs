"""
Tests for Ingress Lambda Handler
Tests payload validation, authorization, and event publishing
"""

import json
import pytest
from unittest.mock import patch, MagicMock
from src.services.ingress.handler import lambda_handler, _validate_payload, _error_response


class TestIngresHandler:
    """Test Ingress Lambda Handler"""
    
    def _create_event(self, body=None, user_id="test-user"):
        """Helper to create API Gateway event"""
        return {
            "body": json.dumps(body) if body else None,
            "requestContext": {
                "authorizer": {
                    "user_id": user_id
                }
            }
        }
    
    @patch("src.services.ingress.handler.boto3.client")
    def test_valid_payload_returns_202_with_event_id(self, mock_boto3_client, monkeypatch):
        """
        GIVEN a valid event payload
        WHEN lambda_handler is called
        THEN it should return 202 Accepted with event_id
        """
        # Arrange
        monkeypatch.setenv("SNS_TOPIC_ARN", "arn:aws:sns:us-east-1:123456789012:event-pipeline-topic-dev")
        valid_payload = {
            "event_type": "user.created",
            "occurred_at": "2026-02-12T10:00:00Z",
            "source": "user-service",
            "payload": {"user_id": "123", "email": "user@example.com"}
        }
        event = self._create_event(valid_payload)
        mock_sns = MagicMock()
        mock_boto3_client.return_value = mock_sns
        
        # Act
        response = lambda_handler(event, None)
        
        # Assert
        assert response["statusCode"] == 202
        body = json.loads(response["body"])
        assert "event_id" in body
        assert body["message"] == "Event accepted for processing"
        assert "ingested_at" in body
        mock_sns.publish.assert_called_once()
    
    def test_missing_required_field_returns_400(self):
        """
        GIVEN a payload missing a required field
        WHEN lambda_handler is called
        THEN it should return 400 with error message
        """
        # Arrange: Missing event_type
        invalid_payload = {
            "occurred_at": "2026-02-12T10:00:00Z",
            "source": "user-service",
            "payload": {}
        }
        event = self._create_event(invalid_payload)
        
        # Act
        response = lambda_handler(event, None)
        
        # Assert
        assert response["statusCode"] == 400
        body = json.loads(response["body"])
        assert "error" in body
        assert "event_type" in body["error"]
    
    def test_invalid_json_returns_400(self):
        """
        GIVEN invalid JSON in request body
        WHEN lambda_handler is called
        THEN it should return 400 with error message
        """
        # Arrange
        event = {
            "body": "not valid json {",
            "requestContext": {"authorizer": {"user_id": "test-user"}}
        }
        
        # Act
        response = lambda_handler(event, None)
        
        # Assert
        assert response["statusCode"] == 400
        body = json.loads(response["body"])
        assert "Invalid JSON" in body["error"]

    def test_non_object_json_payload_returns_400(self):
        """
        GIVEN a valid JSON body that is not an object
        WHEN lambda_handler is called
        THEN it should return 400 with descriptive payload error
        """
        # Arrange
        event = {
            "body": "123",
            "requestContext": {"authorizer": {"user_id": "test-user"}}
        }

        # Act
        response = lambda_handler(event, None)

        # Assert
        assert response["statusCode"] == 400
        body = json.loads(response["body"])
        assert "JSON object" in body["error"]
    
    def test_empty_body_returns_400(self):
        """
        GIVEN no request body
        WHEN lambda_handler is called
        THEN it should return 400 with error message
        """
        # Arrange
        event = self._create_event(None)
        
        # Act
        response = lambda_handler(event, None)
        
        # Assert
        assert response["statusCode"] == 400
        body = json.loads(response["body"])
        assert "Request body is required" in body["error"]
    
    def test_invalid_occurred_at_timestamp_returns_400(self):
        """
        GIVEN an invalid ISO 8601 timestamp for occurred_at
        WHEN lambda_handler is called
        THEN it should return 400 with error message
        """
        # Arrange
        invalid_payload = {
            "event_type": "user.created",
            "occurred_at": "not-a-timestamp",
            "source": "user-service",
            "payload": {}
        }
        event = self._create_event(invalid_payload)
        
        # Act
        response = lambda_handler(event, None)
        
        # Assert
        assert response["statusCode"] == 400
        body = json.loads(response["body"])
        assert "Invalid ISO 8601" in body["error"]


class TestPayloadValidation:
    """Test payload validation function"""
    
    def test_valid_payload_passes_validation(self):
        """Valid payload should return None (no error)"""
        valid_payload = {
            "event_type": "user.created",
            "occurred_at": "2026-02-12T10:00:00Z",
            "source": "user-service",
            "payload": {"user_id": "123"}
        }
        result = _validate_payload(valid_payload)
        assert result is None
    
    def test_null_payload_field_is_allowed(self):
        """Payload field can be null"""
        payload = {
            "event_type": "user.created",
            "occurred_at": "2026-02-12T10:00:00Z",
            "source": "user-service",
            "payload": None
        }
        result = _validate_payload(payload)
        assert result is None
    
    def test_missing_field_returns_error(self):
        """Missing required field should return error"""
        invalid_payload = {
            "event_type": "user.created",
            "source": "user-service"
        }
        result = _validate_payload(invalid_payload)
        assert result is not None
        assert "occurred_at" in result
    
    def test_wrong_field_type_returns_error(self):
        """Wrong field type should return error"""
        invalid_payload = {
            "event_type": 123,  # Should be string
            "occurred_at": "2026-02-12T10:00:00Z",
            "source": "user-service",
            "payload": {}
        }
        result = _validate_payload(invalid_payload)
        assert result is not None
        assert "event_type" in result and "Invalid type" in result


class TestErrorResponse:
    """Test error response helper"""
    
    def test_error_response_format(self):
        """Error response should have correct format"""
        response = _error_response(400, "Test error")
        assert response["statusCode"] == 400
        body = json.loads(response["body"])
        assert body["error"] == "Test error"
        assert body["status_code"] == 400

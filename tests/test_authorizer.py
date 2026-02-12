"""
Tests for Lambda Authorizer
TDD Approach: Tests first, then implementation
"""

import pytest
import json
from src.auth.lambda_authorizer import lambda_authorizer
from src.auth.jwt_handler import generate_token


class TestLambdaAuthorizer:
    """Test Lambda Authorizer for API Gateway"""
    
    def test_valid_token_returns_allow_policy(self):
        """
        GIVEN a valid JWT token in Authorization header
        WHEN lambda_authorizer is called
        THEN it should return Allow policy
        """
        # Arrange: Create a valid token
        user_id = "user-123"
        token = generate_token(user_id=user_id)
        
        # Create API Gateway event with Authorization header
        event = {
            "type": "TOKEN",
            "authorizationToken": f"Bearer {token}",
            "methodArn": "arn:aws:execute-api:us-east-1:123456789012:abcdef/stage/GET/resource"
        }
        
        # Act: Call the authorizer
        response = lambda_authorizer(event, None)
        
        # Assert: Should return Allow policy
        assert response["principalId"] == user_id
        assert response["policyDocument"]["Statement"][0]["Effect"] == "Allow"
        assert "Invoke" in response["policyDocument"]["Statement"][0]["Action"]
    
    def test_invalid_token_returns_deny_policy(self):
        """
        GIVEN an invalid JWT token in Authorization header
        WHEN lambda_authorizer is called
        THEN it should return Deny policy
        """
        # Arrange: Create an invalid token by tampering with it
        token = generate_token(user_id="user-123")
        parts = token.split(".")
        invalid_token = f"{parts[0]}.{parts[1]}.invalid-signature"
        
        # Create API Gateway event
        event = {
            "type": "TOKEN",
            "authorizationToken": f"Bearer {invalid_token}",
            "methodArn": "arn:aws:execute-api:us-east-1:123456789012:abcdef/stage/GET/resource"
        }
        
        # Act: Call the authorizer
        response = lambda_authorizer(event, None)
        
        # Assert: Should return Deny policy
        assert response["principalId"] == "user"
        assert response["policyDocument"]["Statement"][0]["Effect"] == "Deny"
    
    def test_missing_authorization_header_returns_deny(self):
        """
        GIVEN no Authorization header
        WHEN lambda_authorizer is called
        THEN it should return Deny policy
        """
        # Arrange: Event with no Authorization header
        event = {
            "type": "TOKEN",
            "authorizationToken": "",
            "methodArn": "arn:aws:execute-api:us-east-1:123456789012:abcdef/stage/GET/resource"
        }
        
        # Act: Call the authorizer
        response = lambda_authorizer(event, None)
        
        # Assert: Should return Deny policy
        assert response["policyDocument"]["Statement"][0]["Effect"] == "Deny"
    
    def test_malformed_bearer_token_returns_deny(self):
        """
        GIVEN a malformed Bearer token (missing 'Bearer ' prefix)
        WHEN lambda_authorizer is called
        THEN it should return Deny policy
        """
        # Arrange: Event with malformed token
        event = {
            "type": "TOKEN",
            "authorizationToken": "InvalidFormat-token-here",  # Missing 'Bearer '
            "methodArn": "arn:aws:execute-api:us-east-1:123456789012:abcdef/stage/GET/resource"
        }
        
        # Act: Call the authorizer
        response = lambda_authorizer(event, None)
        
        # Assert: Should return Deny policy
        assert response["policyDocument"]["Statement"][0]["Effect"] == "Deny"
    
    def test_expired_token_returns_deny(self):
        """
        GIVEN an expired JWT token
        WHEN lambda_authorizer is called
        THEN it should return Deny policy
        """
        # Arrange: Create an expired token
        expired_token = generate_token(user_id="user-123", expires_in_hours=-1)
        
        event = {
            "type": "TOKEN",
            "authorizationToken": f"Bearer {expired_token}",
            "methodArn": "arn:aws:execute-api:us-east-1:123456789012:abcdef/stage/GET/resource"
        }
        
        # Act: Call the authorizer
        response = lambda_authorizer(event, None)
        
        # Assert: Should return Deny policy
        assert response["policyDocument"]["Statement"][0]["Effect"] == "Deny"

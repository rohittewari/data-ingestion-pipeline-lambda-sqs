"""
Tests for JWT authentication utilities
TDD Approach: Write test first, see it fail, then implement
"""

import pytest
from datetime import datetime, timedelta
from src.auth.jwt_handler import validate_token, generate_token, extract_user_id


class TestJWTValidation:
    """Test JWT token validation"""
    
    def test_valid_token_is_accepted(self):
        """
        GIVEN a valid JWT token
        WHEN validate_token is called
        THEN it should return True
        """
        # Arrange: Create a valid token
        valid_token = generate_token(user_id="test-user-123")
        
        # Act: Validate the token
        result = validate_token(valid_token)
        
        # Assert: Token should be valid
        assert result is True
    
    def test_invalid_token_is_rejected(self):
        """
        GIVEN a token with invalid signature
        WHEN validate_token is called
        THEN it should return False
        """
        # Arrange: Generate a valid token then tamper with it
        valid_token = generate_token(user_id="test-user-123")
        parts = valid_token.split(".")
        
        # Tamper with the signature
        tampered_signature = "invalid-signature-xyz123"
        tampered_token = f"{parts[0]}.{parts[1]}.{tampered_signature}"
        
        # Act: Validate the tampered token
        result = validate_token(tampered_token)
        
        # Assert: Token should be invalid
        assert result is False
    
    def test_expired_token_is_rejected(self):
        """
        GIVEN an expired JWT token
        WHEN validate_token is called
        THEN it should return False
        """
        # Arrange: Generate a token that expires in -1 hours (already expired)
        expired_token = generate_token(user_id="test-user-123", expires_in_hours=-1)
        
        # Act: Validate the expired token
        result = validate_token(expired_token)
        
        # Assert: Token should be invalid (expired)
        assert result is False
    
    def test_malformed_token_is_rejected(self):
        """
        GIVEN a malformed token (missing parts)
        WHEN validate_token is called
        THEN it should return False
        """
        # Arrange: Create various malformed tokens
        malformed_tokens = [
            "invalid",  # No dots
            "part1.part2",  # Only 2 parts
            "part1.part2.part3.part4",  # Too many parts
            "",  # Empty string
        ]
        
        # Act & Assert: All should be invalid
        for token in malformed_tokens:
            result = validate_token(token)
            assert result is False, f"Token '{token}' should be invalid but was accepted"


class TestJWTExtraction:
    """Test extracting user_id from JWT token"""
    
    def test_extract_user_id_from_valid_token(self):
        """
        GIVEN a valid JWT token
        WHEN extract_user_id is called
        THEN it should return the user_id from the token
        """
        # Arrange: Create a valid token
        user_id = "specific-user-456"
        token = generate_token(user_id=user_id)
        
        # Act: Extract user_id
        extracted_user_id = extract_user_id(token)
        
        # Assert: Should extract the correct user_id
        assert extracted_user_id == user_id
    
    def test_extract_user_id_from_invalid_token_returns_none(self):
        """
        GIVEN an invalid JWT token
        WHEN extract_user_id is called
        THEN it should return None
        """
        # Arrange: Create an invalid token
        valid_token = generate_token(user_id="test-user-123")
        parts = valid_token.split(".")
        invalid_token = f"{parts[0]}.{parts[1]}.invalid-signature"
        
        # Act: Try to extract user_id
        extracted_user_id = extract_user_id(invalid_token)
        
        # Assert: Should return None for invalid token
        assert extracted_user_id is None


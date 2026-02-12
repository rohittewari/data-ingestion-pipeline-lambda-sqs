"""
JWT Authentication Handler
Proper JWT implementation with base64url encoding
"""

import json
import hmac
import hashlib
import base64
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional


class JWTHandler:
    """Simple JWT implementation for testing (not for production)"""
    
    SECRET_KEY = "dev-secret-key-phase1"  # Change in production!
    
    @staticmethod
    def _base64url_encode(data: bytes) -> str:
        """Encode bytes to base64url string without padding"""
        return base64.urlsafe_b64encode(data).rstrip(b'=').decode('utf-8')
    
    @staticmethod
    def _base64url_decode(data: str) -> bytes:
        """Decode base64url string to bytes (add padding if needed)"""
        padding = 4 - len(data) % 4
        data_padded = data + '=' * padding
        return base64.urlsafe_b64decode(data_padded)
    
    @staticmethod
    def generate_token(user_id: str, expires_in_hours: int = 24) -> str:
        """
        Generate a proper JWT token with base64url encoding
        
        Args:
            user_id: User identifier
            expires_in_hours: Token expiration time in hours
            
        Returns:
            JWT token string in format: header.payload.signature
        """
        # Create header
        header = {
            "alg": "HS256",
            "typ": "JWT"
        }
        
        # Create payload
        now = datetime.now(timezone.utc)
        payload = {
            "user_id": user_id,
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(hours=expires_in_hours)).timestamp())
        }
        
        # Encode header and payload using base64url
        header_bytes = json.dumps(header, separators=(',', ':')).encode('utf-8')
        payload_bytes = json.dumps(payload, separators=(',', ':')).encode('utf-8')
        
        header_encoded = JWTHandler._base64url_encode(header_bytes)
        payload_encoded = JWTHandler._base64url_encode(payload_bytes)
        
        # Create signature
        message = f"{header_encoded}.{payload_encoded}"
        signature_bytes = hmac.new(
            JWTHandler.SECRET_KEY.encode(),
            message.encode(),
            hashlib.sha256
        ).digest()  # Use digest() instead of hexdigest() for proper JWT
        
        signature_encoded = JWTHandler._base64url_encode(signature_bytes)
        
        # Return complete JWT token
        token = f"{message}.{signature_encoded}"
        return token
    
    @staticmethod
    def validate_token(token: str) -> bool:
        """
        Validate a JWT token
        
        Args:
            token: JWT token string in format: header.payload.signature
            
        Returns:
            True if valid and not expired, False otherwise
        """
        try:
            # Split token into 3 parts
            parts = token.split(".")
            if len(parts) != 3:
                return False
            
            header_encoded, payload_encoded, signature_encoded = parts
            
            # Verify signature
            message = f"{header_encoded}.{payload_encoded}"
            expected_signature_bytes = hmac.new(
                JWTHandler.SECRET_KEY.encode(),
                message.encode(),
                hashlib.sha256
            ).digest()
            
            expected_signature_encoded = JWTHandler._base64url_encode(expected_signature_bytes)
            
            if signature_encoded != expected_signature_encoded:
                return False
            
            # Decode and parse payload to check expiration
            try:
                payload_bytes = JWTHandler._base64url_decode(payload_encoded)
                payload = json.loads(payload_bytes.decode('utf-8'))
            except Exception:
                return False
            
            # Check expiration
            exp = payload.get("exp")
            if exp is None:
                return False
            
            if datetime.now(timezone.utc).timestamp() > exp:
                return False
            
            return True
        
        except Exception:
            return False


# Export functions for easier importing
def generate_token(user_id: str, expires_in_hours: int = 24) -> str:
    """Generate a JWT token"""
    return JWTHandler.generate_token(user_id, expires_in_hours)


def validate_token(token: str) -> bool:
    """Validate a JWT token"""
    return JWTHandler.validate_token(token)


def extract_user_id(token: str) -> Optional[str]:
    """
    Extract user_id from a JWT token
    
    Args:
        token: JWT token string
        
    Returns:
        user_id if token is valid, None otherwise
    """
    try:
        # First validate the token
        if not validate_token(token):
            return None
        
        # Split token and decode payload
        parts = token.split(".")
        if len(parts) != 3:
            return None
        
        payload_encoded = parts[1]
        payload_bytes = JWTHandler._base64url_decode(payload_encoded)
        payload = json.loads(payload_bytes.decode('utf-8'))
        
        return payload.get("user_id")
    
    except Exception:
        return None

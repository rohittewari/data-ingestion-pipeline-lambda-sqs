"""
Lambda Authorizer for API Gateway
Validates JWT tokens from Authorization header
"""

import json
from typing import Any, Dict
from src.auth.jwt_handler import validate_token, extract_user_id


def lambda_authorizer(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    API Gateway Lambda Authorizer
    Validates JWT token from Authorization header
    
    Args:
        event: API Gateway Authorizer event
        context: Lambda context
        
    Returns:
        API Gateway policy document (Allow or Deny)
    """
    
    # Extract the authorization token from the event
    auth_token = event.get("authorizationToken", "").strip()
    method_arn = event.get("methodArn", "")
    
    # Parse the Bearer token
    try:
        # Expected format: "Bearer <token>"
        parts = auth_token.split(" ")
        if len(parts) != 2 or parts[0].lower() != "bearer":
            return _deny_policy("user", method_arn)
        
        token = parts[1]
    except Exception:
        return _deny_policy("user", method_arn)
    
    # Validate the token
    if not validate_token(token):
        return _deny_policy("user", method_arn)
    
    # Extract user_id from token
    user_id = extract_user_id(token)
    if not user_id:
        return _deny_policy("user", method_arn)
    
    # Token is valid, return Allow policy
    return _allow_policy(user_id, method_arn)


def _allow_policy(principal_id: str, method_arn: str) -> Dict[str, Any]:
    """
    Generate an Allow policy
    
    Args:
        principal_id: The user/principal ID
        method_arn: The API Gateway method ARN
        
    Returns:
        Allow policy document
    """
    # Extract the API Gateway API ID from the method ARN
    # ARN format: arn:aws:execute-api:region:account-id:api-id/stage/method/resource
    arn_parts = method_arn.split(":")
    api_gateway_arn = ":".join(arn_parts[:-1]) + ":*"
    
    return {
        "principalId": principal_id,
        "policyDocument": {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "execute-api:Invoke",
                    "Effect": "Allow",
                    "Resource": api_gateway_arn
                }
            ]
        },
        "context": {
            "user_id": principal_id
        }
    }


def _deny_policy(principal_id: str, method_arn: str) -> Dict[str, Any]:
    """
    Generate a Deny policy
    
    Args:
        principal_id: The user/principal ID
        method_arn: The API Gateway method ARN
        
    Returns:
        Deny policy document
    """
    # Extract the API Gateway API ID from the method ARN
    arn_parts = method_arn.split(":")
    api_gateway_arn = ":".join(arn_parts[:-1]) + ":*"
    
    return {
        "principalId": principal_id,
        "policyDocument": {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "execute-api:Invoke",
                    "Effect": "Deny",
                    "Resource": api_gateway_arn
                }
            ]
        }
    }

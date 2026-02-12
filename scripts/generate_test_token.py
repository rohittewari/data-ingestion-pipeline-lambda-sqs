#!/usr/bin/env python3
"""
Generate test JWT tokens for local testing

Usage:
    python scripts/generate_test_token.py [user_id] [hours]

Examples:
    python scripts/generate_test_token.py                    # Default: user-123, 24 hours
    python scripts/generate_test_token.py test-user          # Custom user
    python scripts/generate_test_token.py test-user 1        # Custom user, 1 hour expiry
"""

import sys
from pathlib import Path

# Add src directory to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.auth.jwt_handler import generate_token


def main():
    """Generate a test JWT token"""
    
    # Parse arguments
    user_id = "user-123"  # Default user
    expires_in_hours = 24  # Default expiration
    
    if len(sys.argv) > 1:
        user_id = sys.argv[1]
    
    if len(sys.argv) > 2:
        try:
            expires_in_hours = int(sys.argv[2])
        except ValueError:
            print(f"Error: Invalid hours value '{sys.argv[2]}'. Must be an integer.")
            sys.exit(1)
    
    # Generate token
    token = generate_token(user_id=user_id, expires_in_hours=expires_in_hours)
    
    # Display token and usage
    print(f"\n{'='*70}")
    print(f"JWT Token Generated Successfully")
    print(f"{'='*70}")
    print(f"\nUser ID: {user_id}")
    print(f"Expires in: {expires_in_hours} hours")
    print(f"\n{'Token:'}\n{token}")
    
    print(f"\n{'='*70}")
    print(f"Usage with curl:")
    print(f"{'='*70}\n")
    print(f"curl -X POST http://localhost:3000/v1/events \\")
    print(f"  -H \"Authorization: Bearer {token}\" \\")
    print(f"  -H \"Content-Type: application/json\" \\")
    print(f"  -d '{{'")
    print(f"    \"event_type\": \"user.created\",")
    print(f"    \"occurred_at\": \"2026-02-12T10:00:00Z\",")
    print(f"    \"source\": \"user-service\",")
    print(f"    \"payload\": {{'")
    print(f"      \"user_id\": \"123\",")
    print(f"      \"email\": \"user@example.com\"")
    print(f"    }}")
    print(f"  }}'")
    
    print(f"\n{'='*70}\n")


if __name__ == "__main__":
    main()

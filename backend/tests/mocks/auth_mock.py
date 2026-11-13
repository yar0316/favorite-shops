"""
Local testing mock for Firebase Auth.
This file is mounted into the Docker container during local development
to bypass actual Firebase authentication.
"""
from typing import Dict, Any

def verify_token(id_token: str) -> Dict[str, Any]:
    """
    Mock implementation of Firebase verify_token.
    Returns a dummy decoded token.
    """
    print(f"[MOCK] verify_token called with: {id_token}")
    return {
        "uid": "test-user-uid",
        "name": "Local Test User",
        "email": "test@example.com",
        "picture": "https://example.com/dummy.png"
    }

def get_user_id_from_event(event: Dict[str, Any]) -> str:
    """
    Mock implementation of get_user_id_from_event.
    Always returns the dummy uid regardless of the header,
    unless no header is provided at all (to simulate basic validation).
    """
    auth_header = event.get("headers", {}).get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise ValueError("Missing or invalid Authorization header")
    
    print("[MOCK] get_user_id_from_event bypassed, returning 'test-user-uid'")
    return "test-user-uid"

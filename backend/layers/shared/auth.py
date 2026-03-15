import firebase_admin
from firebase_admin import auth, credentials
from typing import Dict, Any, Optional

# Firebase Admin SDKの初期化
try:
    firebase_admin.get_app()
except ValueError:
    firebase_admin.initialize_app()

def verify_token(id_token: str) -> Dict[str, Any]:
    """
    Firebase IDトークンを検証し、デコードされたクレームを返す。
    """
    try:
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token
    except Exception as e:
        raise ValueError(f"Invalid token: {str(e)}")

def get_user_id_from_event(event: Dict[str, Any]) -> str:
    """
    API GatewayイベントのAuthorizationヘッダーからトークンを抽出し、検証してUIDを返す。
    """
    auth_header = event.get("headers", {}).get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise ValueError("Missing or invalid Authorization header")
    
    token = auth_header.split(" ")[1]
    decoded = verify_token(token)
    return decoded["uid"]

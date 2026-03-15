import json
from typing import Any, Dict
from pydantic import ValidationError
from .models import AuthRequest
from .service import AuthService

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    API Gatewayからのリクエストを受け取りAuthServiceへディスパッチする。
    """
    try:
        body = json.loads(event.get("body", "{}"))
        auth_req = AuthRequest(**body)
    except (json.JSONDecodeError, ValidationError, TypeError) as e:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": str(e)})
        }

    service = AuthService()
    try:
        result = service.authenticate(id_token=auth_req.idToken)
        return {
            "statusCode": 200,
            "body": result.model_dump_json()
        }
    except ValueError as e:
        return {
            "statusCode": 401,
            "body": json.dumps({"error": str(e)})
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Internal Server Error"})
        }

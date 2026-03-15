import json
from typing import Any, Dict
from pydantic import ValidationError
from layers.shared.auth import get_user_id_from_event
from .models import UserProfileUpdate
from .service import UserService

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    API Gatewayからのリクエストを受け取り、認証後にUserServiceへディスパッチする。
    """
    try:
        user_id = get_user_id_from_event(event)
    except ValueError as e:
        return {
            "statusCode": 401,
            "body": json.dumps({"error": str(e)})
        }
    
    method = event.get("httpMethod")
    service = UserService()

    try:
        if method == "GET":
            result = service.get_profile(user_id)
            return {
                "statusCode": 200,
                "body": result.model_dump_json()
            }
        elif method == "PUT":
            body = json.loads(event.get("body", "{}"))
            profile_update = UserProfileUpdate(**body)
            result = service.update_profile(user_id, profile_update)
            return {
                "statusCode": 200,
                "body": result.model_dump_json()
            }
        else:
            return {
                "statusCode": 405,
                "body": json.dumps({"error": "Method Not Allowed"})
            }
    except ValueError as e:
        return {
            "statusCode": 404,
            "body": json.dumps({"error": str(e)})
        }
    except (json.JSONDecodeError, ValidationError) as e:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": str(e)})
        }
    except Exception as e:
        print(f"Unhandled error: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Internal Server Error"})
        }

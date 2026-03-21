import json
from typing import Any, Dict
from layers.shared.response import handle_errors, success, error
from .models import UserProfileUpdate
from .service import UserService


@handle_errors
def handler(event: Dict[str, Any], context: Any, user_id: str) -> Dict[str, Any]:
    """
    API Gatewayからのリクエストを受け取り、UserServiceへディスパッチする。
    認証チェックとエラーハンドリングは handle_errors デコレータが担当。
    """
    method = event.get("httpMethod")
    service = UserService()

    if method == "GET":
        result = service.get_profile(user_id)
        return success(result.model_dump_json())
    elif method == "PUT":
        body = json.loads(event.get("body", "{}"))
        profile_update = UserProfileUpdate(**body)
        result = service.update_profile(user_id, profile_update)
        return success(result.model_dump_json())
    else:
        return error("Method Not Allowed", 405)


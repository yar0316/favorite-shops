import json
from typing import Any, Dict
from layers.shared.response import handle_errors, success, error
from .models import GroupCreate, JoinRequest
from .service import GroupService


@handle_errors
def handler(event: Dict[str, Any], context: Any, user_id: str) -> Dict[str, Any]:
    """
    API Gatewayからのリクエストを受け取り、GroupServiceへディスパッチする。
    認証チェックとエラーハンドリングは handle_errors デコレータが担当。
    """
    method = event.get("httpMethod")
    path_params = event.get("pathParameters") or {}
    path = event.get("path", "")
    service = GroupService()

    if method == "POST":
        body = json.loads(event.get("body", "{}"))
        if path == "/groups/join":
            join_req = JoinRequest(**body)
            result = service.join_group(user_id, join_req.code)
            return success(result.model_dump_json())
        elif "groupId" in path_params and path.endswith("/invite"):
            result = service.create_invitation(path_params["groupId"])
            return success(result.model_dump_json(), 201)
        else:
            group_create = GroupCreate(**body)
            result = service.create_group(user_id, group_create)
            return success(result.model_dump_json(), 201)
    elif method == "GET":
        if "groupId" in path_params:
            result = service.get_group_members(path_params["groupId"])
            return success(json.dumps([m.model_dump() for m in result]))
        else:
            result = service.list_groups(user_id)
            return success(json.dumps([g.model_dump() for g in result], default=str))
    else:
        return error("Method Not Allowed", 405)


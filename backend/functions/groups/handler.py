import json
from typing import Any, Dict
from pydantic import ValidationError
from layers.shared.auth import get_user_id_from_event
from .models import GroupCreate, JoinRequest
from .service import GroupService

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    API Gatewayからのリクエストを受け取り、認証後にGroupServiceへディスパッチする。
    """
    try:
        user_id = get_user_id_from_event(event)
    except ValueError as e:
        return {
            "statusCode": 401,
            "body": json.dumps({"error": str(e)})
        }
    
    method = event.get("httpMethod")
    path_params = event.get("pathParameters") or {}
    path = event.get("path", "")
    service = GroupService()

    try:
        if method == "POST":
            body = json.loads(event.get("body", "{}"))
            if path == "/groups/join":
                join_req = JoinRequest(**body)
                result = service.join_group(user_id, join_req.code)
                return {
                    "statusCode": 200,
                    "body": result.model_dump_json()
                }
            elif "groupId" in path_params and path.endswith("/invite"):
                result = service.create_invitation(path_params["groupId"])
                return {
                    "statusCode": 201,
                    "body": result.model_dump_json()
                }
            else:
                group_create = GroupCreate(**body)
                result = service.create_group(user_id, group_create)
                return {
                    "statusCode": 201,
                    "body": result.model_dump_json()
                }
        elif method == "GET":
            if "groupId" in path_params:
                # メンバー一覧取得
                result = service.get_group_members(path_params["groupId"])
                return {
                    "statusCode": 200,
                    "body": json.dumps([m.model_dump() for m in result])
                }
            else:
                # 参加グループ一覧取得
                result = service.list_groups(user_id)
                return {
                    "statusCode": 200,
                    "body": json.dumps([g.model_dump() for g in result], default=str)
                }
        else:
            return {
                "statusCode": 405,
                "body": json.dumps({"error": "Method Not Allowed"})
            }
    except ValueError as e:
        return {
            "statusCode": 400,
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

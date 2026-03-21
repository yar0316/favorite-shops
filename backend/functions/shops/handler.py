import json
from typing import Any, Dict
from layers.shared.response import handle_errors, success, error
from .models import ShopCreate
from .service import ShopService


@handle_errors
def handler(event: Dict[str, Any], context: Any, user_id: str) -> Dict[str, Any]:
    """
    API Gatewayからのリクエストを受け取り、ShopServiceへディスパッチする。
    認証チェックとエラーハンドリングは handle_errors デコレータが担当。
    """
    method = event.get("httpMethod")
    path_params = event.get("pathParameters") or {}
    query_params = event.get("queryStringParameters") or {}
    service = ShopService()

    group_id = path_params.get("groupId")
    if not group_id:
        return error("Missing groupId", 400)

    if method == "POST":
        body = json.loads(event.get("body", "{}"))
        shop_create = ShopCreate(**body)
        result = service.create_shop(user_id, group_id, shop_create)
        return success(result.model_dump_json(), 201)
    elif method == "GET":
        shop_id = path_params.get("shopId")
        if shop_id:
            result = service.get_shop(group_id, shop_id)
            return success(result.model_dump_json())
        else:
            cuisine_genre = query_params.get("cuisineGenre")
            result = service.list_shops(user_id, group_id, cuisine_genre)
            return success(result.model_dump_json())
    else:
        return error("Method Not Allowed", 405)


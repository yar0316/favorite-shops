import json
from typing import Any, Dict
from layers.shared.response import handle_errors, success, error
from .models import MenuCreate
from .service import MenuService

@handle_errors
def handler(event: Dict[str, Any], context: Any, user_id: str) -> Dict[str, Any]:
    """
    API Gatewayからのリクエストを受け取り、MenuServiceへディスパッチする。
    認証チェックとエラーハンドリングは handle_errors デコレータが担当。
    """
    method = event.get("httpMethod")
    path_params = event.get("pathParameters") or {}
    service = MenuService()

    shop_id = path_params.get("shopId")
    if not shop_id:
        return error("Missing shopId", 400)

    # Note: 権限チェックは MenuService 内で実行されるため、グループIDが必要
    # リクエストのpathParameterにgroupIdを含めるか、shop情報からgroupIdを引いて確認する。
    # 現在のパス /groups/{groupId}/shops/{shopId}/menus と仮定
    group_id = path_params.get("groupId")
    if not group_id:
        return error("Missing groupId", 400)

    if method == "POST":
        body = json.loads(event.get("body", "{}"))
        menu_create = MenuCreate(**body)
        result = service.add_menu(user_id, group_id, shop_id, menu_create)
        return success(result.model_dump_json(), 201)
    elif method == "GET":
        # GET /menus の一覧取得
        result = service.list_menus(shop_id)
        return success(json.dumps([m.model_dump() for m in result]))
    elif method == "DELETE":
        menu_id = path_params.get("menuId")
        if not menu_id:
            return error("Missing menuId", 400)
        service.delete_menu(user_id, group_id, shop_id, menu_id)
        return success(json.dumps({"message": "Deleted successfully"}), 200)
    else:
        return error("Method Not Allowed", 405)


import json
from typing import Any, Dict
from pydantic import ValidationError
from layers.shared.auth import get_user_id_from_event
from .models import ShopCreate
from .service import ShopService

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    API Gatewayからのリクエストを受け取り、認証後にShopServiceへディスパッチする。
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
    query_params = event.get("queryStringParameters") or {}
    service = ShopService()

    group_id = path_params.get("groupId")
    if not group_id:
        # /users/me/shops などのマイスペース対応は、group_idをユーザーIDに置き換える想定で設計可能
        # 今回はパスパラメータにgroupIdがあることを前提とする
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Missing groupId"})
        }

    try:
        if method == "POST":
            body = json.loads(event.get("body", "{}"))
            shop_create = ShopCreate(**body)
            result = service.create_shop(user_id, group_id, shop_create)
            return {
                "statusCode": 201,
                "body": result.model_dump_json()
            }
        elif method == "GET":
            shop_id = path_params.get("shopId")
            if shop_id:
                # 詳細取得
                result = service.get_shop(group_id, shop_id)
                return {
                    "statusCode": 200,
                    "body": result.model_dump_json()
                }
            else:
                # 一覧取得
                cuisine_genre = query_params.get("cuisineGenre")
                result = service.list_shops(group_id, cuisine_genre)
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

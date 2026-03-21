"""handler共通のレスポンス構築・エラーハンドリングモジュール"""
import json
from functools import wraps
from pydantic import ValidationError
from layers.shared.auth import get_user_id_from_event


def success(body, status_code=200):
    """正常レスポンスを構築する"""
    return {
        "statusCode": status_code,
        "body": body if isinstance(body, str) else json.dumps(body)
    }


def error(message: str, status_code: int):
    """エラーレスポンスを構築する"""
    return {
        "statusCode": status_code,
        "body": json.dumps({"error": message})
    }


def handle_errors(func):
    """
    handler関数をラップし、認証チェックと共通エラーハンドリングを適用するデコレータ。
    ラップされた関数は (event, context, user_id) のシグネチャで呼ばれる。
    """
    @wraps(func)
    def wrapper(event, context):
        # 認証チェック
        try:
            user_id = get_user_id_from_event(event)
        except ValueError as e:
            return error(str(e), 401)

        # ビジネスロジック実行
        try:
            return func(event, context, user_id)
        except PermissionError as e:
            return error(str(e), 403)
        except (json.JSONDecodeError, ValidationError) as e:
            return error(str(e), 400)
        except ValueError as e:
            return error(str(e), 404)
        except Exception as e:
            print(f"Unhandled error: {str(e)}")
            return error("Internal Server Error", 500)
    return wrapper

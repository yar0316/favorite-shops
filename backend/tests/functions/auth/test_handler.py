import pytest
import json
from unittest.mock import patch, MagicMock

# =========================================================================
# 【仕様定義（インターフェース）】
# このテストが期待するRequest/Responseモデル（Pydantic等で後ほど実装）
# =========================================================================
class MockAuthRequest:
    def __init__(self, id_token: str):
        self.id_token = id_token

class MockAuthResponse:
    def __init__(self, user_id: str, name: str, picture: str, is_new_user: bool):
        self.user_id = user_id
        self.name = name
        self.picture = picture
        self.is_new_user = is_new_user

# =========================================================================
# これから実装する関数をインポート（TDDのRedフェーズのため、最初はModuleNotFoundErrorになる）
# =========================================================================
from functions.auth.handler import handler

# =========================================================================
# 【テストケース（詳細設計）】
# POST /auth/token
# 概要：FirebaseのIDトークンを受け取り、検証し、ユーザー情報を返す。
#      初回ログイン時はユーザープロフィールの登録とマイスペースの自動作成を行う。
# =========================================================================

class TestAuthTokenAPI:

    @patch("functions.auth.service.db_client.get_item")
    def test_正常系_既存ユーザーがログインしてプロフィールを取得できること(self, mock_get_item, mock_firebase_verify):
        """
        正常系：既存ユーザーのログイン
        - 有効なIDトークンを送信する
        - Firebase検証が成功しUIDが返る
        - DynamoDB(USER#uid PROFILE)から既存データが取得できる
        - 新規作成処理(create_user)は呼ばれない
        - ユーザー情報と is_new_user=False が返る
        """
        # 1. モックの振る舞い定義（Given）
        mock_firebase_verify.return_value = {"uid": "user123", "name": "Existing User", "picture": "http://img"}
        mock_get_item.return_value = {
            "Item": {
                "PK": {"S": "USER#user123"},
                "SK": {"S": "PROFILE"},
                "name": {"S": "Existing User"}
            }
        }
        
        # 2. テスト対象の実行（When）
        event = {
            "httpMethod": "POST",
            "body": json.dumps({"idToken": "valid_token"})
        }
        response = handler(event, {})
        
        # 3. 期待結果の検証（Then）
        assert response["statusCode"] == 200
        body = json.loads(response["body"])
        assert body["user_id"] == "user123"
        assert body["name"] == "Existing User"
        assert body["is_new_user"] is False
        
        mock_firebase_verify.assert_called_once_with("valid_token")
        mock_get_item.assert_called_once()

    @patch("functions.auth.service.db_client.get_item")
    @patch("functions.auth.service.db_client.transact_write_items")
    def test_正常系_新規ユーザーの初回ログイン時にプロフィールとマイスペースが作成されること(self, mock_transact_write, mock_get_item, mock_firebase_verify):
        """
        正常系：新規ユーザーの初回登録
        - 有効なIDトークンを送信する
        - Firebase検証が成功しUIDが返る
        - DynamoDB(USER#uid PROFILE)からデータが取得できない（Noneが返る）
        - ユーザー情報(PROFILE)の作成が一度呼ばれる
        - マイスペース(個人のMy Shops群)の作成処理が一度呼ばれる
        - ユーザー情報と is_new_user=True が返る
        """
        # Given
        mock_firebase_verify.return_value = {"uid": "new999", "name": "New User", "picture": "http://img"}
        mock_get_item.return_value = {}  # DynamoDBから取得できない（未登録）
        
        # When
        event = {
            "httpMethod": "POST",
            "body": json.dumps({"idToken": "new_valid_token"})
        }
        response = handler(event, {})

        # Then
        assert response["statusCode"] == 200
        body = json.loads(response["body"])
        assert body["user_id"] == "new999"
        assert body["name"] == "New User"
        assert body["is_new_user"] is True
        
        mock_firebase_verify.assert_called_once_with("new_valid_token")
        mock_get_item.assert_called_once()
        mock_transact_write.assert_called_once()  # 新規作成トランザクションが呼ばれること

    def test_異常系_無効なトークンが送信された場合は401エラーになること(self, mock_firebase_verify):
        """
        異常系：無効なIDトークン
        - 無効なトークンや期限切れトークンを送信する
        - Firebase検証でエラー（ValueError等）が発生する
        - 401 Unauthorized エラーが返る
        """
        # Given
        mock_firebase_verify.side_effect = ValueError("Invalid token")
        
        # When
        event = {
            "httpMethod": "POST",
            "body": json.dumps({"idToken": "invalid_or_expired_token"})
        }
        response = handler(event, {})

        # Then
        assert response["statusCode"] == 401
        body = json.loads(response["body"])
        assert "error" in body
        
        mock_firebase_verify.assert_called_once_with("invalid_or_expired_token")

    def test_異常系_トークンがリクエストに含まれずバリデーションエラーとなること(self):
        """
        異常系：リクエストバリデーションエラー
        - body またはヘッダーに idToken が含まれていないリクエスト
        - PydanticのValidationError等が発生し、400 Bad Request が返る
        """
        # When
        # bodyが空、あるいは必要なidTokenが存在しない
        event = {
            "httpMethod": "POST",
            "body": json.dumps({})
        }
        response = handler(event, {})

        # Then
        assert response["statusCode"] == 400
        body = json.loads(response["body"])
        assert "error" in body

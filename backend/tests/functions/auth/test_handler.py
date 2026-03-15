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
# これから実装する関数群（TDDのRedフェーズのため、最初はModuleNotFoundErrorになる）
# =========================================================================
from functions.auth.service import AuthService
from functions.auth.models import AuthRequest, AuthResponse

# =========================================================================
# 【テストケース（詳細設計）】
# AuthService.authenticate(id_token: str) -> AuthResponse
# 概要：FirebaseのIDトークンを受け取り、検証し、ユーザー情報を返す。
#      初回ログイン時はユーザープロフィールの登録とマイスペースの自動作成を行う。
# =========================================================================

class TestAuthService:

    @patch("functions.auth.service.db_client.get_item")
    def test_正常系_既存ユーザーがログインしてプロフィールを取得できること(self, mock_get_item, mock_firebase_verify):
        """
        正常系：既存ユーザーのログイン
        - 有効なIDトークンを渡す
        - Firebase検証が成功しUIDが返る
        - DynamoDB(USER#uid PROFILE)から既存データが取得できる
        - ユーザー情報と is_new_user=False が返る
        """
        # 1. モックの振る舞い定義（Given）
        mock_firebase_verify.return_value = {"uid": "user123", "name": "Existing User", "picture": "http://img"}
        mock_get_item.return_value = {
            "Item": {
                "PK": {"S": "USER#user123"},
                "SK": {"S": "PROFILE"},
                "name": {"S": "Existing User"},
                "picture": {"S": "http://img"}
            }
        }
        
        # 2. テスト対象の実行（When）
        service = AuthService()
        response = service.authenticate(id_token="valid_token")
        
        # 3. 期待結果の検証（Then）
        assert response.user_id == "user123"
        assert response.name == "Existing User"
        assert response.is_new_user is False
        
        mock_firebase_verify.assert_called_once_with("valid_token")
        mock_get_item.assert_called_once()

    @patch("functions.auth.service.db_client.get_item")
    @patch("functions.auth.service.db_client.transact_write_items")
    def test_正常系_新規ユーザーの初回ログイン時にプロフィールとマイスペースが作成されること(self, mock_transact_write, mock_get_item, mock_firebase_verify):
        """
        正常系：新規ユーザーの初回登録
        - 有効なIDトークンを渡す
        - Firebase検証が成功しUIDが返る
        - DynamoDB(USER#uid PROFILE)からデータが取得できない（未登録）
        - ユーザー情報(PROFILE)とマイスペースの作成が同時に行われる(transact_write_items)
        - ユーザー情報と is_new_user=True が返る
        """
        # Given
        mock_firebase_verify.return_value = {"uid": "new999", "name": "New User", "picture": "http://img"}
        mock_get_item.return_value = {}  # DynamoDBから取得できない（未登録）
        
        # When
        service = AuthService()
        response = service.authenticate(id_token="new_valid_token")

        # Then
        assert response.user_id == "new999"
        assert response.name == "New User"
        assert response.is_new_user is True
        
        mock_firebase_verify.assert_called_once_with("new_valid_token")
        mock_get_item.assert_called_once()
        mock_transact_write.assert_called_once()  # 新規作成トランザクションが呼ばれること

    def test_異常系_無効なトークンが渡された場合は認証エラーになること(self, mock_firebase_verify):
        """
        異常系：無効なIDトークン
        - 無効なトークンを渡す
        - Firebase検証でエラー（ValueError等）が発生する
        - 例外（ValueError または独自定義の AuthError等）が送出される
        """
        # Given
        mock_firebase_verify.side_effect = ValueError("Invalid token")
        
        # When & Then
        service = AuthService()
        with pytest.raises(ValueError, match="Invalid token"):
            service.authenticate(id_token="invalid_or_expired_token")
        
        mock_firebase_verify.assert_called_once_with("invalid_or_expired_token")

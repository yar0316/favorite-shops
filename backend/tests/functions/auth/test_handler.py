import pytest
import json
from unittest.mock import patch, MagicMock
from functions.auth.handler import handler
from functions.auth.models import AuthResponse

# =========================================================================
# 【テストケース（詳細設計）】
# POST /auth/token (API Gateway Handler層のテスト)
# 概要：API Gatewayからのイベントを受け取り、AuthServiceを呼び出し、
#      正しいHTTPステータスコードとJSONレスポンスを返すかを検証する。
# =========================================================================

class TestAuthHandler:

    @patch("functions.auth.handler.AuthService")
    def test_正常系_有効なトークンを受け取り200OKとユーザー情報をJSONで返すこと(self, mock_auth_service_class):
        """
        正常系：ハンドラ層
        - API GatewayからのJSONイベントをパースする
        - AuthService.authenticate() を呼び出す
        - AuthResponse を dict に変換し、statusCode 200 と共に返す
        """
        # Given: AuthServiceが正常なAuthResponseを返すとスタブ化
        mock_service_instance = MagicMock()
        mock_service_instance.authenticate.return_value = AuthResponse(
            user_id="user123",
            name="Test User",
            picture="http://img",
            is_new_user=False
        )
        mock_auth_service_class.return_value = mock_service_instance

        event = {
            "httpMethod": "POST",
            "body": json.dumps({"idToken": "valid_token"})
        }

        # When
        response = handler(event, {})

        # Then
        assert response["statusCode"] == 200
        body = json.loads(response["body"])
        assert body["user_id"] == "user123"
        assert body["name"] == "Test User"
        assert body["is_new_user"] is False
        
        # AuthServiceが正しく呼び出されたか検証
        mock_service_instance.authenticate.assert_called_once_with(id_token="valid_token")

    @patch("functions.auth.handler.AuthService")
    def test_異常系_無効なトークンが送信された場合401エラーレスポンスを返すこと(self, mock_auth_service_class):
        """
        異常系：ハンドラ層
        - AuthService.authenticate() が ValueError を送出する
        - statusCode 401 とエラーメッセージのJSONを返す
        """
        # Given: AuthServiceがValueErrorを送出する
        mock_service_instance = MagicMock()
        mock_service_instance.authenticate.side_effect = ValueError("Invalid token")
        mock_auth_service_class.return_value = mock_service_instance

        event = {
            "httpMethod": "POST",
            "body": json.dumps({"idToken": "invalid_token"})
        }

        # When
        response = handler(event, {})

        # Then
        assert response["statusCode"] == 401
        body = json.loads(response["body"])
        assert "error" in body
        assert body["error"] == "Invalid token"

    def test_異常系_リクエストボディが不正な場合は400エラーレスポンスを返すこと(self):
        """
        異常系：ハンドラ層（バリデーション）
        - bodyが存在しない、または idToken が含まれていない
        - statusCode 400 を返す
        """
        # When
        event = {
            "httpMethod": "POST",
            "body": "{}"  # idTokenがない空JSON
        }
        response = handler(event, {})

        # Then
        assert response["statusCode"] == 400
        body = json.loads(response["body"])
        assert "error" in body

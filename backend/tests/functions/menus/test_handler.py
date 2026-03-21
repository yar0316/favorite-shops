import json
import pytest
from unittest.mock import patch, MagicMock
from functions.menus.handler import handler
from functions.menus.models import MenuResponse

class TestMenuHandler:

    @patch("functions.menus.handler.MenuService")
    @patch("layers.shared.response.get_user_id_from_event")
    def test_正常系_メニューを登録し201を返すこと(self, mock_get_uid, mock_menu_service_class):
        # Given
        mock_get_uid.return_value = "user123"
        mock_service = MagicMock()
        mock_service.add_menu.return_value = MenuResponse(
            id="menu123", shop_id="shop123", name="絶品チャーハン", photo_url="http://img/rice"
        )
        mock_menu_service_class.return_value = mock_service

        event = {
            "httpMethod": "POST",
            "pathParameters": {"groupId": "group123", "shopId": "shop123"},
            "body": json.dumps({"name": "絶品チャーハン", "photo_url": "http://img/rice"}),
            "headers": {"Authorization": "Bearer valid_token"}
        }

        # When
        response = handler(event, {})

        # Then
        assert response["statusCode"] == 201
        body = json.loads(response["body"])
        assert body["id"] == "menu123"
        assert body["name"] == "絶品チャーハン"

    @patch("functions.menus.handler.MenuService")
    @patch("layers.shared.response.get_user_id_from_event")
    def test_正常系_メニュー一覧を取得し200を返すこと(self, mock_get_uid, mock_menu_service_class):
        # Given
        mock_get_uid.return_value = "user123"
        mock_service = MagicMock()
        mock_service.list_menus.return_value = [
            MenuResponse(id="menu123", shop_id="shop123", name="ラーメン")
        ]
        mock_menu_service_class.return_value = mock_service

        event = {
            "httpMethod": "GET",
            "pathParameters": {"groupId": "group123", "shopId": "shop123"},
            "headers": {"Authorization": "Bearer valid_token"}
        }

        # When
        response = handler(event, {})

        # Then
        assert response["statusCode"] == 200
        body = json.loads(response["body"])
        assert len(body) == 1
        assert body[0]["name"] == "ラーメン"

    def test_異常系_認証ヘッダーがない場合は401を返すこと(self):
        # When
        event = {
            "httpMethod": "GET",
            "pathParameters": {"groupId": "group123", "shopId": "shop123"},
            "headers": {}  # No Auth
        }
        response = handler(event, {})

        # Then
        assert response["statusCode"] == 401

    @patch("layers.shared.response.get_user_id_from_event")
    def test_異常系_リクエストボディが不正な場合は400を返すこと(self, mock_get_uid):
        # Given: 認証は通過する
        mock_get_uid.return_value = "user123"

        # When
        event = {
            "httpMethod": "POST",
            "pathParameters": {"groupId": "group123", "shopId": "shop123"},
            "body": "{}",  # nameがない空JSON
            "headers": {"Authorization": "Bearer valid_token"}
        }
        response = handler(event, {})

        # Then
        assert response["statusCode"] == 400
        body = json.loads(response["body"])
        assert "error" in body

    @patch("functions.menus.handler.MenuService")
    @patch("layers.shared.response.get_user_id_from_event")
    def test_異常系_非メンバーが操作した場合は403を返すこと(self, mock_get_uid, mock_menu_service_class):
        """
        認可エラー：
        - 非メンバーがメニュー登録しようとした場合
        - ServiceがPermissionErrorを送出 → handlerは403を返す
        """
        # Given: MenuServiceがPermissionErrorを送出
        mock_get_uid.return_value = "outsider"
        mock_service = MagicMock()
        mock_service.add_menu.side_effect = PermissionError("Not a member of this group")
        mock_menu_service_class.return_value = mock_service

        event = {
            "httpMethod": "POST",
            "pathParameters": {"groupId": "group123", "shopId": "shop123"},
            "body": json.dumps({"name": "絶品チャーハン", "photo_url": "http://img/rice"}),
            "headers": {"Authorization": "Bearer valid_token"}
        }

        # When
        response = handler(event, {})

        # Then
        assert response["statusCode"] == 403
        body = json.loads(response["body"])
        assert "error" in body

import json
import pytest
from unittest.mock import patch, MagicMock
from functions.menus.handler import handler
from functions.menus.models import MenuResponse

class TestMenuHandler:

    @patch("functions.menus.handler.MenuService")
    @patch("functions.menus.handler.get_user_id_from_event")
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
            "pathParameters": {"shopId": "shop123"},
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
    @patch("functions.menus.handler.get_user_id_from_event")
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
            "pathParameters": {"shopId": "shop123"},
            "headers": {"Authorization": "Bearer valid_token"}
        }

        # When
        response = handler(event, {})

        # Then
        assert response["statusCode"] == 200
        body = json.loads(response["body"])
        assert len(body) == 1
        assert body[0]["name"] == "ラーメン"

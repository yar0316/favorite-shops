import json
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime
from functions.shops.handler import handler
from functions.shops.models import ShopResponse

class TestShopHandler:

    @patch("functions.shops.handler.ShopService")
    @patch("functions.shops.handler.get_user_id_from_event")
    def test_正常系_お店を登録し201を返すこと(self, mock_get_uid, mock_shop_service_class):
        # Given
        mock_get_uid.return_value = "user123"
        mock_service = MagicMock()
        mock_service.create_shop.return_value = ShopResponse(
            id="shop123", group_id="group123", name="テスト飯屋", area="渋谷",
            cuisine_genres=["和食"], drink_genres=["日本酒"], created_by="user123",
            created_at=datetime.now(), updated_at=datetime.now()
        )
        mock_shop_service_class.return_value = mock_service

        event = {
            "httpMethod": "POST",
            "pathParameters": {"groupId": "group123"},
            "body": json.dumps({"name": "テスト飯屋", "area": "渋谷", "cuisine_genres": ["和食"], "drink_genres": ["日本酒"]}),
            "headers": {"Authorization": "Bearer valid_token"}
        }

        # When
        response = handler(event, {})

        # Then
        assert response["statusCode"] == 201
        body = json.loads(response["body"])
        assert body["id"] == "shop123"
        assert body["name"] == "テスト飯屋"

    @patch("functions.shops.handler.ShopService")
    @patch("functions.shops.handler.get_user_id_from_event")
    def test_正常系_お店一覧を取得し200を返すこと(self, mock_get_uid, mock_shop_service_class):
        # Given
        mock_get_uid.return_value = "user123"
        mock_service = MagicMock()
        mock_service.list_shops.return_value = MagicMock(
            model_dump_json=lambda: json.dumps({"shops": [], "total": 0})
        )
        mock_shop_service_class.return_value = mock_service

        event = {
            "httpMethod": "GET",
            "pathParameters": {"groupId": "group123"},
            "headers": {"Authorization": "Bearer valid_token"}
        }

        # When
        response = handler(event, {})

        # Then
        assert response["statusCode"] == 200
        body = json.loads(response["body"])
        assert "shops" in body
        assert "total" in body

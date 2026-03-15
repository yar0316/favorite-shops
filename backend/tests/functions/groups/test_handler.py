import json
import pytest
from unittest.mock import patch, MagicMock
from functions.groups.handler import handler
from functions.groups.models import GroupResponse

class TestGroupHandler:

    @patch("functions.groups.handler.GroupService")
    @patch("functions.groups.handler.get_user_id_from_event")
    def test_正常系_グループを作成し201を返すこと(self, mock_get_uid, mock_group_service_class):
        # Given
        mock_get_uid.return_value = "user123"
        mock_service = MagicMock()
        mock_service.create_group.return_value = GroupResponse(
            id="group123", name="美食部", owner_id="user123", created_at="2026-03-15T00:00:00"
        )
        mock_group_service_class.return_value = mock_service

        event = {
            "httpMethod": "POST",
            "path": "/groups",
            "body": json.dumps({"name": "美食部"}),
            "headers": {"Authorization": "Bearer valid_token"}
        }

        # When
        response = handler(event, {})

        # Then
        assert response["statusCode"] == 201
        body = json.loads(response["body"])
        assert body["id"] == "group123"
        assert body["name"] == "美食部"

    @patch("functions.groups.handler.GroupService")
    @patch("functions.groups.handler.get_user_id_from_event")
    def test_正常系_招待コードで参加し200を返すこと(self, mock_get_uid, mock_group_service_class):
        # Given
        mock_get_uid.return_value = "user123"
        mock_service = MagicMock()
        mock_service.join_group.return_value = GroupResponse(
            id="group123", name="美食部", owner_id="owner", created_at="2026-03-15T00:00:00"
        )
        mock_group_service_class.return_value = mock_service

        event = {
            "httpMethod": "POST",
            "path": "/groups/join",
            "body": json.dumps({"code": "INVITE123"}),
            "headers": {"Authorization": "Bearer valid_token"}
        }

        # When
        response = handler(event, {})

        # Then
        assert response["statusCode"] == 200
        body = json.loads(response["body"])
        assert body["id"] == "group123"
        
    def test_異常系_認証ヘッダーがない場合は401を返すこと(self):
        # When
        event = {
            "httpMethod": "GET",
            "path": "/groups",
            "headers": {} # No Auth
        }
        response = handler(event, {})

        # Then
        assert response["statusCode"] == 401

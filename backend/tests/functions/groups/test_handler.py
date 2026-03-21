import json
import pytest
from unittest.mock import patch, MagicMock
from functions.groups.handler import handler
from functions.groups.models import GroupResponse

class TestGroupHandler:

    @patch("functions.groups.handler.GroupService")
    @patch("layers.shared.response.get_user_id_from_event")
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
    @patch("layers.shared.response.get_user_id_from_event")
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

    @patch("layers.shared.response.get_user_id_from_event")
    def test_異常系_リクエストボディが不正な場合は400を返すこと(self, mock_get_uid):
        # Given: 認証は通過する
        mock_get_uid.return_value = "user123"

        # When
        event = {
            "httpMethod": "POST",
            "path": "/groups",
            "body": "{}",  # nameがない空JSON
            "headers": {"Authorization": "Bearer valid_token"}
        }
        response = handler(event, {})

        # Then
        assert response["statusCode"] == 400
        body = json.loads(response["body"])
        assert "error" in body

    @patch("functions.groups.handler.GroupService")
    @patch("layers.shared.response.get_user_id_from_event")
    def test_異常系_非メンバーがグループ操作した場合は403を返すこと(self, mock_get_uid, mock_group_service_class):
        """
        認可エラー：
        - 非メンバーが招待コード発行やメンバー一覧閲覧をしようとした場合
        - ServiceがPermissionErrorを送出 → handlerは403を返す
        """
        # Given: GroupServiceがPermissionErrorを送出
        mock_get_uid.return_value = "outsider"
        mock_service = MagicMock()
        mock_service.create_invitation.side_effect = PermissionError("Not a member of this group")
        mock_group_service_class.return_value = mock_service

        event = {
            "httpMethod": "POST",
            "path": "/groups/group123/invite",
            "pathParameters": {"groupId": "group123"},
            "body": "{}",
            "headers": {"Authorization": "Bearer valid_token"}
        }

        # When
        response = handler(event, {})

        # Then
        assert response["statusCode"] == 403
        body = json.loads(response["body"])
        assert "error" in body

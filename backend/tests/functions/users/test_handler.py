import json
import pytest
from unittest.mock import patch, MagicMock
from functions.users.handler import handler
from functions.users.models import UserProfileResponse

class TestUserHandler:

    @patch("functions.users.handler.UserService")
    @patch("functions.users.handler.get_user_id_from_event")
    def test_正常系_自分のプロフィールを取得できること(self, mock_get_uid, mock_user_service_class):
        # Given
        mock_get_uid.return_value = "user123"
        mock_service = MagicMock()
        mock_service.get_profile.return_value = UserProfileResponse(
            user_id="user123", name="Test User", picture="http://img", email="test@example.com"
        )
        mock_user_service_class.return_value = mock_service

        event = {
            "httpMethod": "GET",
            "headers": {"Authorization": "Bearer valid_token"}
        }

        # When
        response = handler(event, {})

        # Then
        assert response["statusCode"] == 200
        body = json.loads(response["body"])
        assert body["user_id"] == "user123"
        assert body["name"] == "Test User"
        
        mock_get_uid.assert_called_once_with(event)
        mock_service.get_profile.assert_called_once_with("user123")

import pytest
from unittest.mock import patch, MagicMock
from functions.users.service import UserService
from functions.users.models import UserProfileUpdate

class TestUserService:

    @patch("functions.users.service.db_client.get_item")
    def test_正常系_ユーザープロフィールが取得できること(self, mock_get_item):
        # Given
        mock_get_item.return_value = {
            "Item": {
                "PK": {"S": "USER#user123"},
                "SK": {"S": "PROFILE"},
                "name": {"S": "Test User"},
                "picture": {"S": "http://img"},
                "email": {"S": "test@example.com"}
            }
        }
        
        # When
        service = UserService()
        response = service.get_profile(user_id="user123")
        
        # Then
        assert response.user_id == "user123"
        assert response.name == "Test User"
        assert response.email == "test@example.com"
        mock_get_item.assert_called_once()

    @patch("functions.users.service.db_client.update_item")
    def test_正常系_ユーザープロフィールが更新できること(self, mock_update_item):
        # Given
        mock_update_item.return_value = {
            "Attributes": {
                "PK": {"S": "USER#user123"},
                "SK": {"S": "PROFILE"},
                "name": {"S": "Updated Name"},
                "picture": {"S": "http://new-img"},
                "email": {"S": "test@example.com"}
            }
        }
        
        # When
        service = UserService()
        update_data = UserProfileUpdate(name="Updated Name", picture="http://new-img")
        response = service.update_profile(user_id="user123", profile=update_data)
        
        # Then
        assert response.name == "Updated Name"
        assert response.picture == "http://new-img"
        mock_update_item.assert_called_once()

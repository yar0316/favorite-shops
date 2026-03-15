import json
import pytest
from unittest.mock import patch, MagicMock
from functions.upload.handler import handler
from functions.upload.models import PresignedUrlResponse

class TestUploadHandler:

    @patch("functions.upload.handler.UploadService")
    @patch("functions.upload.handler.get_user_id_from_event")
    def test_正常系_署名付きURLを取得し200を返すこと(self, mock_get_uid, mock_upload_service_class):
        # Given
        mock_get_uid.return_value = "user123"
        mock_service = MagicMock()
        mock_service.get_presigned_url.return_value = PresignedUrlResponse(
            upload_url="https://s3.signed-url", file_key="uuid-test.jpg"
        )
        mock_upload_service_class.return_value = mock_service

        event = {
            "httpMethod": "POST",
            "body": json.dumps({"file_name": "test.jpg", "content_type": "image/jpeg"}),
            "headers": {"Authorization": "Bearer valid_token"}
        }

        # When
        response = handler(event, {})

        # Then
        assert response["statusCode"] == 200
        body = json.loads(response["body"])
        assert body["upload_url"] == "https://s3.signed-url"
        assert body["file_key"] == "uuid-test.jpg"

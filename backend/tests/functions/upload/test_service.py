import pytest
import os
from unittest.mock import patch, MagicMock
from functions.upload.service import UploadService

class TestUploadService:

    @patch("functions.upload.service.s3_client.generate_presigned_url")
    def test_正常系_署名付きURLを生成できること(self, mock_gen_url):
        # Given
        os.environ["S3_BUCKET_NAME"] = "test-bucket"
        mock_gen_url.return_value = "https://s3.amazonaws.com/test-bucket/uuid-file.jpg?Signature=..."
        
        # When
        service = UploadService()
        response = service.get_presigned_url(file_name="test.jpg", content_type="image/jpeg")
        
        # Then
        assert "test-bucket" in response.upload_url
        assert response.file_key.endswith(".jpg")
        
        # S3クライアントが正しい引数で呼ばれているか
        mock_gen_url.assert_called_once()
        args = mock_gen_url.call_args[1]
        assert args["ClientMethod"] == "put_object"
        assert args["Params"]["Bucket"] == "test-bucket"
        assert args["Params"]["ContentType"] == "image/jpeg"
        assert "ExpiresIn" in args

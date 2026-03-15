import os
import boto3
import uuid
from .models import PresignedUrlResponse

S3_BUCKET = os.environ.get("S3_BUCKET_NAME", "favorite-shops-assets")
s3_client = boto3.client("s3")

class UploadService:
    def get_presigned_url(self, file_name: str, content_type: str) -> PresignedUrlResponse:
        """
        S3の署名付きURLを生成して返す。
        """
        # TODO: Implement
        pass

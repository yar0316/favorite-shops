import boto3
import os

TABLE_NAME = os.environ.get("DYNAMODB_TABLE", "favorite-shops-test")
db_client = boto3.client("dynamodb", region_name=os.environ.get("AWS_DEFAULT_REGION", "ap-northeast-1"))

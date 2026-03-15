import os
from layers.shared.db import db_client
from .models import UserProfileResponse, UserProfileUpdate

TABLE_NAME = os.environ.get("DYNAMODB_TABLE", "favorite-shops-test")

class UserService:
    def get_profile(self, user_id: str) -> UserProfileResponse:
        """
        DynamoDBからユーザープロフィールを取得する。
        """
        response = db_client.get_item(
            TableName=TABLE_NAME,
            Key={
                "PK": {"S": f"USER#{user_id}"},
                "SK": {"S": "PROFILE"}
            }
        )
        
        if "Item" not in response:
            raise ValueError("User profile not found")
        
        item = response["Item"]
        return UserProfileResponse(
            user_id=user_id,
            name=item["name"]["S"],
            picture=item.get("picture", {"S": ""})["S"],
            email=item.get("email", {"S": ""})["S"]
        )

    def update_profile(self, user_id: str, profile: UserProfileUpdate) -> UserProfileResponse:
        """
        DynamoDBのユーザープロフィールを更新する。
        """
        update_expr = "SET #name = :name, picture = :picture"
        attr_names = {"#name": "name"}
        attr_values = {
            ":name": {"S": profile.name},
            ":picture": {"S": profile.picture or ""}
        }
        
        response = db_client.update_item(
            TableName=TABLE_NAME,
            Key={
                "PK": {"S": f"USER#{user_id}"},
                "SK": {"S": "PROFILE"}
            },
            UpdateExpression=update_expr,
            ExpressionAttributeNames=attr_names,
            ExpressionAttributeValues=attr_values,
            ReturnValues="ALL_NEW"
        )
        
        item = response["Attributes"]
        return UserProfileResponse(
            user_id=user_id,
            name=item["name"]["S"],
            picture=item.get("picture", {"S": ""})["S"],
            email=item.get("email", {"S": ""})["S"]
        )

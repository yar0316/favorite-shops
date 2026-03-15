import os
import uuid
import boto3
import firebase_admin
from firebase_admin import auth, credentials
from .models import AuthResponse

# Firebase Admin SDKの初期化（一度だけ実行）
try:
    firebase_admin.get_app()
except ValueError:
    # サービスアカウント情報は実行環境の環境変数等で指定される想定
    # 本番ではデフォルトのクレデンシャルを使用
    firebase_admin.initialize_app()

from layers.shared.db import db_client
TABLE_NAME = os.environ.get("DYNAMODB_TABLE", "favorite-shops-test")

class AuthService:
    def authenticate(self, id_token: str) -> AuthResponse:
        """
        Firebase IDトークンを検証し、ユーザー情報を取得・登録するビジネスロジック。
        初回ログイン時はユーザープロフィールの登録とマイスペースの自動作成を行う。
        """
        try:
            decoded_token = auth.verify_id_token(id_token)
        except Exception as e:
            raise ValueError(f"Invalid token: {str(e)}")

        uid = decoded_token["uid"]
        name = decoded_token.get("name", "Unknown User")
        picture = decoded_token.get("picture", "")

        # 既存ユーザーのプロフィール確認
        response = db_client.get_item(
            TableName=TABLE_NAME,
            Key={
                "PK": {"S": f"USER#{uid}"},
                "SK": {"S": "PROFILE"}
            }
        )

        if "Item" in response:
            return AuthResponse(
                user_id=uid,
                name=response["Item"]["name"]["S"],
                picture=response["Item"]["picture"]["S"],
                is_new_user=False
            )
        
        # 新規ユーザー：プロフィール作成とマイスペース作成（トランザクション）
        my_space_id = str(uuid.uuid4())
        
        db_client.transact_write_items(
            TransactItems=[
                {
                    "Put": {
                        "TableName": TABLE_NAME,
                        "Item": {
                            "PK": {"S": f"USER#{uid}"},
                            "SK": {"S": "PROFILE"},
                            "name": {"S": name},
                            "picture": {"S": picture},
                            "email": {"S": decoded_token.get("email", "")}
                        }
                    }
                },
                {
                    "Put": {
                        "TableName": TABLE_NAME,
                        "Item": {
                            "PK": {"S": f"USER#{uid}"},
                            "SK": {"S": f"GROUP#{my_space_id}"},
                            "groupName": {"S": "マイスペース"},
                            "role": {"S": "OWNER"}
                        }
                    }
                },
                {
                    "Put": {
                        "TableName": TABLE_NAME,
                        "Item": {
                            "PK": {"S": f"GROUP#{my_space_id}"},
                            "SK": {"S": "META"},
                            "groupName": {"S": "マイスペース"},
                            "owner": {"S": uid}
                        }
                    }
                },
                {
                    "Put": {
                        "TableName": TABLE_NAME,
                        "Item": {
                            "PK": {"S": f"GROUP#{my_space_id}"},
                            "SK": {"S": f"MEMBER#{uid}"},
                            "name": {"S": name},
                            "role": {"S": "OWNER"}
                        }
                    }
                }
            ]
        )

        return AuthResponse(
            user_id=uid,
            name=name,
            picture=picture,
            is_new_user=True
        )

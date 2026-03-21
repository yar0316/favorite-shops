import uuid
from firebase_admin import auth
from .models import AuthResponse
from layers.shared.auth import verify_token
from layers.shared.db import db_client, TABLE_NAME

# ドメイン固有のDynamoDBキープレフィックス
_USER_PK = "USER#"
_GROUP_PK = "GROUP#"
_MEMBER_SK = "MEMBER#"
_PROFILE_SK = "PROFILE"
_META_SK = "META"

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
                "PK": {"S": f"{_USER_PK}{uid}"},
                "SK": {"S": _PROFILE_SK}
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
                            "PK": {"S": f"{_USER_PK}{uid}"},
                            "SK": {"S": _PROFILE_SK},
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
                            "PK": {"S": f"{_USER_PK}{uid}"},
                            "SK": {"S": f"{_GROUP_PK}{my_space_id}"},
                            "groupName": {"S": "マイスペース"},
                            "role": {"S": "OWNER"}
                        }
                    }
                },
                {
                    "Put": {
                        "TableName": TABLE_NAME,
                        "Item": {
                            "PK": {"S": f"{_GROUP_PK}{my_space_id}"},
                            "SK": {"S": _META_SK},
                            "groupName": {"S": "マイスペース"},
                            "owner": {"S": uid}
                        }
                    }
                },
                {
                    "Put": {
                        "TableName": TABLE_NAME,
                        "Item": {
                            "PK": {"S": f"{_GROUP_PK}{my_space_id}"},
                            "SK": {"S": f"{_MEMBER_SK}{uid}"},
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


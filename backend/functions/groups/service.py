import random
import string
import uuid
from datetime import datetime
from typing import List
from layers.shared.db import db_client, TABLE_NAME
from layers.shared.membership import verify_membership
from .models import GroupCreate, GroupResponse, GroupMemberResponse, InvitationResponse

# ドメイン固有のDynamoDBキープレフィックス
_GROUP_PK = "GROUP#"
_USER_PK = "USER#"
_MEMBER_SK = "MEMBER#"
_INVITE_PK = "INVITE#"
_META_SK = "META"

class GroupService:
    def create_group(self, user_id: str, group: GroupCreate) -> GroupResponse:
        """
        グループを作成し、作成者をオーナーとしてメンバー登録する（トランザクション）。
        """
        group_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        db_client.transact_write_items(
            TransactItems=[
                {
                    "Put": {
                        "TableName": TABLE_NAME,
                        "Item": {
                            "PK": {"S": f"{_GROUP_PK}{group_id}"},
                            "SK": {"S": _META_SK},
                            "groupName": {"S": group.name},
                            "owner": {"S": user_id},
                            "createdAt": {"S": now}
                        }
                    }
                },
                {
                    "Put": {
                        "TableName": TABLE_NAME,
                        "Item": {
                            "PK": {"S": f"{_GROUP_PK}{group_id}"},
                            "SK": {"S": f"{_MEMBER_SK}{user_id}"},
                            "role": {"S": "OWNER"},
                            "joinedAt": {"S": now}
                        }
                    }
                },
                {
                    "Put": {
                        "TableName": TABLE_NAME,
                        "Item": {
                            "PK": {"S": f"{_USER_PK}{user_id}"},
                            "SK": {"S": f"{_GROUP_PK}{group_id}"},
                            "groupName": {"S": group.name},
                            "role": {"S": "OWNER"}
                        }
                    }
                }
            ]
        )
        
        return GroupResponse(
            id=group_id,
            name=group.name,
            owner_id=user_id,
            created_at=datetime.fromisoformat(now)
        )

    def list_groups(self, user_id: str) -> List[GroupResponse]:
        """
        ユーザーが参加しているグループの一覧を取得する。
        """
        response = db_client.query(
            TableName=TABLE_NAME,
            KeyConditionExpression="PK = :pk AND begins_with(SK, :sk)",
            ExpressionAttributeValues={
                ":pk": {"S": f"{_USER_PK}{user_id}"},
                ":sk": {"S": _GROUP_PK}
            }
        )
        
        groups = []
        for item in response.get("Items", []):
            group_id = item["SK"]["S"].replace(_GROUP_PK, "")
            groups.append(GroupResponse(
                id=group_id,
                name=item["groupName"]["S"],
                owner_id="", # list_groups時点では詳細不要な想定
                created_at=datetime.now() # クエリ結果に含める場合は設計変更が必要
            ))
        return groups

    def get_group_members(self, user_id: str, group_id: str) -> List[GroupMemberResponse]:
        verify_membership(user_id, group_id)
        # ... (略)
        return members

    def create_invitation(self, user_id: str, group_id: str) -> InvitationResponse:
        """
        有効期限付き招待コードを生成する。
        """
        verify_membership(user_id, group_id)
        # 8文字のランダムな英数字
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        # 24時間後を有効期限に設定
        expires_at = datetime.now().timestamp() + (24 * 3600)
        
        # グループ情報を取得（後で参加時にグループ名を引き継ぐため）
        meta = db_client.get_item(
            TableName=TABLE_NAME,
            Key={"PK": {"S": f"{_GROUP_PK}{group_id}"}, "SK": {"S": _META_SK}}
        )
        group_name = meta.get("Item", {}).get("groupName", {"S": "Shared Group"})["S"]

        db_client.put_item(
            TableName=TABLE_NAME,
            Item={
                "PK": {"S": f"{_INVITE_PK}{code}"},
                "SK": {"S": _META_SK},
                "group_id": {"S": group_id},
                "groupName": {"S": group_name},
                "expiresAt": {"N": str(int(expires_at))}
            }
        )
        return InvitationResponse(
            code=code,
            group_id=group_id,
            expires_at=datetime.fromtimestamp(expires_at)
        )

    def join_group(self, user_id: str, code: str) -> GroupResponse:
        """
        招待コードを使ってグループに参加する（トランザクション）。
        """
        # コードの存在チェック
        response = db_client.get_item(
            TableName=TABLE_NAME,
            Key={"PK": {"S": f"{_INVITE_PK}{code}"}, "SK": {"S": _META_SK}}
        )
        if "Item" not in response:
            raise ValueError("Invalid or expired invitation code")
        
        item = response["Item"]
        group_id = item["group_id"]["S"]
        group_name = item["groupName"]["S"]
        now = datetime.now().isoformat()

        db_client.transact_write_items(
            TransactItems=[
                {
                    "Put": {
                        "TableName": TABLE_NAME,
                        "Item": {
                            "PK": {"S": f"{_GROUP_PK}{group_id}"},
                            "SK": {"S": f"{_MEMBER_SK}{user_id}"},
                            "role": {"S": "MEMBER"},
                            "joinedAt": {"S": now}
                        }
                    }
                },
                {
                    "Put": {
                        "TableName": TABLE_NAME,
                        "Item": {
                            "PK": {"S": f"{_USER_PK}{user_id}"},
                            "SK": {"S": f"{_GROUP_PK}{group_id}"},
                            "groupName": {"S": group_name},
                            "role": {"S": "MEMBER"}
                        }
                    }
                }
            ]
        )
        return GroupResponse(
            id=group_id,
            name=group_name,
            owner_id="unknown", # 必要ならメタから取得
            created_at=datetime.now()
        )

"""グループメンバーシップ確認の共通モジュール"""
from layers.shared.db import db_client, TABLE_NAME

# PKプレフィックス（クロスドメインで使用されるもののみ）
_USER_PK = "USER#"
_GROUP_SK = "GROUP#"


def verify_membership(user_id: str, group_id: str) -> None:
    """
    ユーザーが指定グループのメンバーであることを確認する。
    メンバーでない場合は PermissionError を送出する。
    """
    response = db_client.get_item(
        TableName=TABLE_NAME,
        Key={
            "PK": {"S": f"{_USER_PK}{user_id}"},
            "SK": {"S": f"{_GROUP_SK}{group_id}"}
        }
    )
    if "Item" not in response:
        raise PermissionError("Not a member of this group")

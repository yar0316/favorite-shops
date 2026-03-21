import uuid
from typing import List
from layers.shared.db import db_client, TABLE_NAME
from layers.shared.membership import verify_membership
from .models import MenuCreate, MenuResponse

# ドメイン固有のDynamoDBキープレフィックス
_SHOP_PK = "SHOP#"
_MENU_SK = "MENU#"

class MenuService:
    def add_menu(self, user_id: str, group_id: str, shop_id: str, menu: MenuCreate) -> MenuResponse:
        """
        おすすめメニューを登録する。
        """
        verify_membership(user_id, group_id)
        
        menu_id = str(uuid.uuid4())
        
        item = {
            "PK": {"S": f"{_SHOP_PK}{shop_id}"},
            "SK": {"S": f"{_MENU_SK}{menu_id}"},
            "name": {"S": menu.name},
        }
        if menu.photo_url:
            item["photo_url"] = {"S": str(menu.photo_url)}
            
        db_client.put_item(
            TableName=TABLE_NAME,
            Item=item
        )
        
        return MenuResponse(
            id=menu_id,
            shop_id=shop_id,
            name=menu.name,
            photo_url=menu.photo_url
        )

    def list_menus(self, shop_id: str) -> List[MenuResponse]:
        """
        お店のおすすめメニュー一覧を取得する。
        """
        response = db_client.query(
            TableName=TABLE_NAME,
            KeyConditionExpression="PK = :pk AND begins_with(SK, :sk)",
            ExpressionAttributeValues={
                ":pk": {"S": f"{_SHOP_PK}{shop_id}"},
                ":sk": {"S": _MENU_SK}
            }
        )
        
        menus = []
        for item in response.get("Items", []):
            menu_id = item["SK"]["S"].replace(_MENU_SK, "")
            menus.append(MenuResponse(
                id=menu_id,
                shop_id=shop_id,
                name=item["name"]["S"],
                photo_url=item.get("photo_url", {}).get("S")
            ))
        return menus

    def delete_menu(self, user_id: str, group_id: str, shop_id: str, menu_id: str):
        """
        おすすめメニューを削除する。
        """
        verify_membership(user_id, group_id)
        
        db_client.delete_item(
            TableName=TABLE_NAME,
            Key={
                "PK": {"S": f"{_SHOP_PK}{shop_id}"},
                "SK": {"S": f"{_MENU_SK}{menu_id}"}
            }
        )

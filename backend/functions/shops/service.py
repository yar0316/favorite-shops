import uuid
from datetime import datetime
from typing import Optional
from layers.shared.db import db_client, TABLE_NAME
from layers.shared.membership import verify_membership
from .models import ShopCreate, ShopResponse, ShopListResponse, ParsedShopResponse

# ドメイン固有のDynamoDBキープレフィックス
_GROUP_PK = "GROUP#"
_SHOP_SK = "SHOP#"

class ShopService:
    def create_shop(self, user_id: str, group_id: str, shop: ShopCreate) -> ShopResponse:
        """
        グループにお店を登録する。
        """
        verify_membership(user_id, group_id)
        
        shop_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        item = {
            "PK": {"S": f"{_GROUP_PK}{group_id}"},
            "SK": {"S": f"{_SHOP_SK}{shop_id}"},
            "name": {"S": shop.name},
            "area": {"S": shop.area},
            "cuisine_genres": {"SS": shop.cuisine_genres},
            "drink_genres": {"SS": shop.drink_genres},
            "created_by": {"S": user_id},
            "created_at": {"S": now},
            "updated_at": {"S": now}
        }
        
        if shop.address: item["address"] = {"S": shop.address}
        if shop.comment: item["comment"] = {"S": shop.comment}
        if shop.photos: item["photos"] = {"SS": shop.photos}
        if shop.external_link: item["external_link"] = {"S": shop.external_link}
        if shop.latitude is not None: item["latitude"] = {"N": str(shop.latitude)}
        if shop.longitude is not None: item["longitude"] = {"N": str(shop.longitude)}

        db_client.put_item(
            TableName=TABLE_NAME,
            Item=item
        )
        
        return ShopResponse(
            id=shop_id,
            group_id=group_id,
            created_by=user_id,
            created_at=datetime.fromisoformat(now),
            updated_at=datetime.fromisoformat(now),
            **shop.model_dump()
        )

    def list_shops(self, user_id: str, group_id: str, cuisine_genre: Optional[str] = None) -> ShopListResponse:
        """
        グループ内のお店一覧を取得する。
        """
        verify_membership(user_id, group_id)
        
        # クエリのベース
        params = {
            "TableName": TABLE_NAME,
            "KeyConditionExpression": "PK = :pk AND begins_with(SK, :sk)",
            "ExpressionAttributeValues": {
                ":pk": {"S": f"{_GROUP_PK}{group_id}"},
                ":sk": {"S": _SHOP_SK}
            }
        }

        # ジャンルフィルタ（簡易実装：FilterExpressionを使用）
        if cuisine_genre:
            params["FilterExpression"] = "contains(cuisine_genres, :c)"
            params["ExpressionAttributeValues"][":c"] = {"S": cuisine_genre}

        response = db_client.query(**params)
        
        shops = []
        for item in response.get("Items", []):
            shops.append(self._item_to_shop_response(item))
            
        return ShopListResponse(shops=shops, total=response.get("Count", 0))

    def get_shop(self, group_id: str, shop_id: str) -> ShopResponse:
        """
        お店の詳細を取得する。
        """
        response = db_client.get_item(
            TableName=TABLE_NAME,
            Key={
                "PK": {"S": f"{_GROUP_PK}{group_id}"},
                "SK": {"S": f"{_SHOP_SK}{shop_id}"}
            }
        )
        
        if "Item" not in response:
            raise ValueError("Shop not found")
            
        return self._item_to_shop_response(response["Item"])

    def parse_url(self, url: str) -> ParsedShopResponse:
        """
        URLを解析して店名や住所、位置情報などを取得する。
        """
        # TODO: Implement URL parsing logic
        pass

    def _item_to_shop_response(self, item: dict) -> ShopResponse:
        shop_id = item["SK"]["S"].replace(_SHOP_SK, "")
        group_id = item["PK"]["S"].replace(_GROUP_PK, "")
        
        return ShopResponse(
            id=shop_id,
            group_id=group_id,
            name=item["name"]["S"],
            area=item["area"]["S"],
            address=item.get("address", {}).get("S"),
            cuisine_genres=list(item["cuisine_genres"]["SS"]),
            drink_genres=list(item["drink_genres"]["SS"]),
            comment=item.get("comment", {}).get("S"),
            photos=list(item.get("photos", {}).get("SS", [])),
            external_link=item.get("external_link", {}).get("S"),
            latitude=float(item["latitude"]["N"]) if "latitude" in item else None,
            longitude=float(item["longitude"]["N"]) if "longitude" in item else None,
            created_by=item["created_by"]["S"],
            created_at=datetime.fromisoformat(item["created_at"]["S"]),
            updated_at=datetime.fromisoformat(item["updated_at"]["S"])
        )

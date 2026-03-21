import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock
from functions.shops.service import ShopService
from functions.shops.models import ShopCreate

class TestShopService:

    @patch("functions.shops.service.verify_membership")
    @patch("functions.shops.service.db_client.put_item")
    def test_正常系_お店を登録できること(self, mock_put, mock_verify):
        # Given: メンバーシップ確認は通過する
        mock_verify.return_value = None
        shop_data = ShopCreate(
            name="テスト飯屋",
            area="渋谷",
            cuisine_genres=["和食"],
            drink_genres=["ビール"]
        )

        # When
        service = ShopService()
        response = service.create_shop(user_id="user123", group_id="group123", shop=shop_data)

        # Then: 設計通りのPK/SK変換ロジックを検証
        mock_put.assert_called_once()
        put_item = mock_put.call_args[1]["Item"]

        # 1. PKが所属グループIDを指しているか (GROUP#id)
        assert put_item["PK"]["S"] == "GROUP#group123"
        # 2. SKがお見せ自身のIDを指しているか (SHOP#id)
        sk = put_item["SK"]["S"]
        assert sk.startswith("SHOP#")
        assert len(sk) > 30 # UUIDの長さ

        # 一貫性チェック
        assert response.id == sk.replace("SHOP#", "")
        assert response.group_id == "group123"


    @patch("functions.shops.service.verify_membership")
    @patch("functions.shops.service.db_client.query")
    def test_正常系_グループ内のお店一覧を取得できること(self, mock_query, mock_verify):
        # Given: メンバーシップ確認は通過する
        mock_verify.return_value = None
        mock_query.return_value = {
            "Items": [
                {
                    "PK": {"S": "GROUP#group123"},
                    "SK": {"S": "SHOP#shop123"},
                    "name": {"S": "Test Shop"},
                    "area": {"S": "Shibuya"},
                    "cuisine_genres": {"SS": ["Japanese"]},
                    "drink_genres": {"SS": ["Beer"]},
                    "created_by": {"S": "user123"},
                    "created_at": {"S": "2026-03-15T00:00:00Z"},
                    "updated_at": {"S": "2026-03-15T00:00:00Z"}
                }
            ],
            "Count": 1
        }
        
        # When
        service = ShopService()
        response = service.list_shops(user_id="user123", group_id="group123")
        
        # Then
        assert response.total == 1
        assert response.shops[0].name == "Test Shop"
        mock_query.assert_called_once()

    @patch("functions.shops.service.ShopService.parse_url")
    def test_正常系_GoogleマップのURLを解析できること(self, mock_parse):
        # Given
        url = "https://maps.google.com/?q=Test+Shop"
        mock_parse.return_value = {
            "name": "Test Shop",
            "area": "Shibuya",
            "cuisine_genres": ["Japanese"],
            "drink_genres": ["Beer"],
            "latitude": 35.6580,
            "longitude": 139.7016
        }
        
        # When
        service = ShopService()
        response = service.parse_url(url)
        
        # Then
        assert response["name"] == "Test Shop"
        assert response["latitude"] == 35.6580

    @patch("functions.shops.service.verify_membership")
    @patch("functions.shops.service.db_client.put_item")
    def test_異常系_非メンバーがお店を登録しようとした場合はPermissionErrorになること(self, mock_put, mock_verify):
        """
        認可チェック：
        - user_id が group_id のメンバーでない場合
        - verify_membership が PermissionError を送出
        """
        # Given: ユーザーがグループに所属していない
        mock_verify.side_effect = PermissionError("Not a member of this group")
        
        shop_data = ShopCreate(
            name="テスト飯屋", area="渋谷",
            cuisine_genres=["和食"], drink_genres=["ビール"]
        )

        # When & Then
        service = ShopService()
        with pytest.raises(PermissionError, match="Not a member of this group"):
            service.create_shop(user_id="outsider", group_id="group123", shop=shop_data)
        
        # DB書き込みが行われていないことを検証
        mock_put.assert_not_called()

    @patch("functions.shops.service.verify_membership")
    @patch("functions.shops.service.db_client.query")
    def test_異常系_非メンバーがお店一覧を取得しようとした場合はPermissionErrorになること(self, mock_query, mock_verify):
        """
        認可チェック：
        - verify_membership が PermissionError を送出
        - 非メンバーはグループ内のお店情報にアクセスできない
        """
        # Given: ユーザーがグループに所属していない
        mock_verify.side_effect = PermissionError("Not a member of this group")

        # When & Then
        service = ShopService()
        with pytest.raises(PermissionError, match="Not a member of this group"):
            service.list_shops(user_id="outsider", group_id="group123")
        
        # クエリが実行されていないことを検証
        mock_query.assert_not_called()

import pytest
from unittest.mock import patch, MagicMock
from functions.menus.service import MenuService
from functions.menus.models import MenuCreate

class TestMenuService:

    @patch("functions.menus.service.verify_membership")
    @patch("functions.menus.service.db_client.put_item")
    def test_正常系_お店にメニューを登録できること(self, mock_put, mock_verify):
        # Given: メンバーである
        mock_verify.return_value = None
        menu_data = MenuCreate(name="絶品チャーハン", photo_url="http://img/rice")
        
        # When
        service = MenuService()
        response = service.add_menu(user_id="user123", group_id="group123", shop_id="shop123", menu=menu_data)
        
        # Then
        assert response.name == "絶品チャーハン"
        assert response.shop_id == "shop123"
        
        # 設計通りのデータ構造（PK/SK）に変換されてDBへ送られているか検証
        mock_put.assert_called_once()
        put_item = mock_put.call_args[1]["Item"]
        
        # 1. PKが SHOP# プレフィックス付きで正しく構築されているか
        assert put_item["PK"]["S"] == "SHOP#shop123"
        # 2. SKが MENU# プレフィックス + 生成されたUUID形式になっているか
        sk = put_item["SK"]["S"]
        assert sk.startswith("MENU#")
        assert len(sk) > 30 # UUIDが含まれる十分な長さ
        # 3. レスポンスのIDとSKのID部分が一致しているか（一貫性）
        assert response.id == sk.replace("MENU#", "")

    @patch("functions.menus.service.db_client.query")
    def test_正常系_お店のメニュー一覧を取得できること(self, mock_query):
        # Given
        mock_query.return_value = {
            "Items": [
                {
                    "PK": {"S": "SHOP#shop123"},
                    "SK": {"S": "MENU#menu1"},
                    "name": {"S": "ラーメン"},
                    "photo_url": {"S": "http://img/ramen"}
                }
            ],
            "Count": 1
        }
        
        # When
        service = MenuService()
        response = service.list_menus(shop_id="shop123")
        
        # Then
        assert len(response) == 1
        assert response[0].name == "ラーメン"
        mock_query.assert_called_once()

    @patch("functions.menus.service.verify_membership")
    @patch("functions.menus.service.db_client.delete_item")
    def test_正常系_メニューを削除できること(self, mock_delete, mock_verify):
        # Given: メンバーである
        mock_verify.return_value = None

        # When
        service = MenuService()
        service.delete_menu(user_id="user123", group_id="group123", shop_id="shop123", menu_id="menu1")
        
        # Then
        mock_delete.assert_called_once_with(
            TableName="favorite-shops-test",
            Key={
                "PK": {"S": "SHOP#shop123"},
                "SK": {"S": "MENU#menu1"}
            }
        )

    @patch("functions.menus.service.verify_membership")
    @patch("functions.menus.service.db_client.put_item")
    def test_異常系_非メンバーがメニューを登録しようとした場合はPermissionErrorになること(self, mock_put, mock_verify):
        """
        認可チェック：
        - verify_membership が PermissionError を送出
        - 非メンバーはメニュー操作ができない
        """
        # Given: ユーザーがグループに所属していない
        mock_verify.side_effect = PermissionError("Not a member of this group")

        menu_data = MenuCreate(name="絶品チャーハン", photo_url="http://img/rice")

        # When & Then
        service = MenuService()
        with pytest.raises(PermissionError, match="Not a member of this group"):
            service.add_menu(user_id="outsider", group_id="group123", shop_id="shop123", menu=menu_data)

        # DB書き込みが行われていないことを検証
        mock_put.assert_not_called()

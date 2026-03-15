import os
from typing import List
from layers.shared.db import db_client
from .models import MenuCreate, MenuResponse

TABLE_NAME = os.environ.get("DYNAMODB_TABLE", "favorite-shops-test")

class MenuService:
    def add_menu(self, shop_id: str, menu: MenuCreate) -> MenuResponse:
        """
        おすすめメニューを登録する。
        """
        # TODO: Implement
        pass

    def list_menus(self, shop_id: str) -> List[MenuResponse]:
        """
        お店のおすすめメニュー一覧を取得する。
        """
        # TODO: Implement
        pass

    def delete_menu(self, shop_id: str, menu_id: str):
        """
        おすすめメニューを削除する。
        """
        # TODO: Implement
        pass

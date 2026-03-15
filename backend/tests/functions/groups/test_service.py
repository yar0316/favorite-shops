import pytest
from unittest.mock import patch, MagicMock
from functions.groups.service import GroupService
from functions.groups.models import GroupCreate

class TestGroupService:

    @patch("functions.groups.service.db_client.transact_write_items")
    def test_正常系_グループを作成できること(self, mock_transact):
        # Given
        group_data = GroupCreate(name="美食部")
        
        # When
        service = GroupService()
        response = service.create_group(user_id="user123", group=group_data)
        
        # Then: 設計通りのシングルテーブル・トランザクション構造（3つのアイテム）を検証
        mock_transact.assert_called_once()
        items = mock_transact.call_args[1]["TransactItems"]
        assert len(items) == 3
        
        # 1. グループメタ情報の検証（PK: GROUP#id, SK: META）
        meta = items[0]["Put"]
        assert meta["Item"]["PK"]["S"].startswith("GROUP#")
        assert meta["Item"]["SK"]["S"] == "META"
        group_id = meta["Item"]["PK"]["S"].replace("GROUP#", "")
        
        # 2. グループメンバー（グループ視点）の検証（PK: GROUP#id, SK: MEMBER#user）
        member_list = items[1]["Put"]
        assert member_list["Item"]["PK"]["S"] == f"GROUP#{group_id}"
        assert member_list["Item"]["SK"]["S"] == "MEMBER#user123"
        
        # 3. ユーザーの所属リスト（ユーザー視点）の検証（PK: USER#id, SK: GROUP#id）
        user_list = items[2]["Put"]
        assert user_list["Item"]["PK"]["S"] == "USER#user123"
        assert user_list["Item"]["SK"]["S"] == f"GROUP#{group_id}"
        
        # 一貫性チェック
        assert response.id == group_id

    @patch("functions.groups.service.db_client.query")
    def test_正常系_参加しているグループ一覧を取得できること(self, mock_query):
        # ... (略)
        pass

    @patch("functions.groups.service.db_client.get_item")
    @patch("functions.groups.service.db_client.put_item")
    def test_正常系_有効期限付き招待コードを生成できること(self, mock_put, mock_get):
        # Given: グループIDを指定
        mock_get.return_value = {
            "Item": {
                "groupName": {"S": "Test Group"}
            }
        }
        # When: 招待コードを生成
        service = GroupService()
        response = service.create_invitation(group_id="group123")
        
        # Then: 
        # - 8文字程度のランダム文字列が生成されている
        assert len(response.code) >= 6
        assert response.group_id == "group123"
        # - db_client.put_item が呼ばれ、TTL(ExpiresAt)が設定されている
        mock_put.assert_called_once()
        args = mock_put.call_args[1]["Item"]
        assert args["PK"]["S"] == f"INVITE#{response.code}"
        assert "TTL" in args # DynamoDB TTL属性
        assert "ExpiresAt" in args

    @patch("functions.groups.service.db_client.get_item")
    @patch("functions.groups.service.db_client.transact_write_items")
    def test_正常系_有効な招待コードでグループに参加できること(self, mock_transact, mock_get_item):
        # Given: 有効なコードが存在する
        mock_get_item.return_value = {
            "Item": {
                "PK": {"S": "INVITE#ABC-123"},
                "group_id": {"S": "group-X"},
                "groupName": {"S": "Shared Group"}
            }
        }
        
        # When: コードを指定して参加
        service = GroupService()
        response = service.join_group(user_id="user456", code="ABC-123")
        
        # Then:
        # - トランザクションで所属情報が書き込まれる
        mock_transact.assert_called_once()
        # - 所属したグループ情報が返る
        assert response.id == "group-X"
        assert response.name == "Shared Group"

    @patch("functions.groups.service.db_client.get_item")
    def test_異常系_存在しないコードまたは期限切れの場合はエラーになること(self, mock_get_item):
        # Given: コードが見つからない
        mock_get_item.return_value = {}
        
        # When & Then
        service = GroupService()
        with pytest.raises(ValueError, match="Invalid or expired invitation code"):
            service.join_group(user_id="user456", code="INVALID")

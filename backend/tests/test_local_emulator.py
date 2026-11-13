import importlib.util
from pathlib import Path
from unittest.mock import Mock


def test_ローカルテーブルを本番と同じキーとインデックスで作成する():
    path = Path(__file__).parents[1] / "local-emulator" / "init_table.py"
    assert path.exists(), "初期化スクリプトが必要"
    spec = importlib.util.spec_from_file_location("init_table", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    client = Mock()
    module.create_table(client)
    request = client.create_table.call_args.kwargs
    assert request["TableName"] == "favorite-shops-local"
    assert request["KeySchema"] == [{"AttributeName": "PK", "KeyType": "HASH"}, {"AttributeName": "SK", "KeyType": "RANGE"}]
    assert request["GlobalSecondaryIndexes"][0]["IndexName"] == "GSI1"
    assert request["GlobalSecondaryIndexes"][0]["KeySchema"] == [{"AttributeName": "GSI1PK", "KeyType": "HASH"}, {"AttributeName": "GSI1SK", "KeyType": "RANGE"}]

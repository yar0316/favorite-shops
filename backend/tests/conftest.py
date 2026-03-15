import os
import pytest
from botocore.stub import Stubber

# 実際のLambda実装（これから作る）やモックするboto3クライアントなどのダミー定義
# backend-test実行時は実装コードが存在しない前提なので、ここで仮のinterfaceを定義して読み込むか、
# 存在していれば実体をimportするように振る舞う。
# 今回はPydanticモデル等のインターフェース設計も兼ねる。

os.environ["DYNAMODB_TABLE"] = "favorite-shops-test"
os.environ["ENVIRONMENT"] = "test"

@pytest.fixture
def dynamodb_stub():
    """
    DynamoDBのboto3クライアントをモック（stubber）化して提供する。
    実際の詳細実装時に、テスト対象モジュールから import したクライアントにアタッチする。
    """
    # 抽象化されたフィクスチャ
    pass

@pytest.fixture
def mock_firebase_verify():
    """
    Firebase Admin SDKのトークン検証関数(verify_id_token)をモック化するフィクスチャ。
    全ドメインの認証テストで共通して利用可能。
    """
    with patch("functions.auth.service.firebase_admin.auth.verify_id_token") as mock:
        yield mock

# Backend Testing Guide

バックエンド（AWS Lambda）の機能は、FastAPIやコンテナ等を使わず、シンプルなハンドラ関数として実装されています。
そのため、テスト環境は **`uv` を用いたローカルのPython仮想環境** だけで完結します（Docker等は不要です）。

## 前提条件
- [uv](https://github.com/astral-sh/uv) がインストールされていること
- Python 3.13 以上がインストールされていること

## セットアップ手順

1. **バックエンドディレクトリへ移動**
   ```bash
   cd backend
   ```

2. **仮想環境の作成と依存関係のインストール**
   ```bash
   # 仮想環境を作成（Python 3.13指定）
   uv venv --python 3.13
   
   # アクティベート (Windows)
   .venv\Scripts\activate
   # アクティベート (Mac/Linux)
   # source .venv/bin/activate
   
   # 依存ライブラリのインストール
   # ※まだpyproject.tomlがない場合は、この後作成します
   uv pip install pytest boto3 pydantic
   ```

## テストの実行方法

Smallテスト（外部依存をすべてモック化したテスト）は、以下のコマンドで高速に実行できます。

```bash
# 全てのテストを実行
pytest tests/

# 特定のドメイン（例: auth）のテストだけを実行
pytest tests/functions/auth/

# プリント文等の標準出力を表示しながら実行
pytest -s tests/
```

## 今後のライブラリ追加について

`backend-dev` スキルで実装を進める際、新しく必要なパッケージ（例: `firebase-admin`等）が出てきた場合は、AIが `uv pip install <package>` を実行して仮想環境に追加していきます。

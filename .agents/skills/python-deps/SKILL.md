---
name: python-deps
description: Pythonのパッケージ管理や独立したツールの実行において pip の代わりに uv および uvx を使用するためのルールと手順を提供するスキルです。「Pythonのパッケージを追加して」「pytestを実行して」「依存関係をインストールして」などの、Python環境・パッケージ操作、またはスクリプト実行が要求された際に使用してください。
---

# Python パッケージ管理スキル (python-deps)

Python プロジェクトにおいて、環境構築やパッケージ管理を行う際は、遅い `pip` に代わり高速な `uv` を使用します。本スキルは、Python関連の操作で一貫して `uv` や `uvx` を使うためのガイドラインです。

## 前提条件

- [uv](https://github.com/astral-sh/uv) がインストールされていること
- 常に `pip` コマンドの代わりに `uv` サブコマンドを使用する

## ルールと使用例

### 1. グローバルツールの実行 (`uvx` の利用)
独立したPythonツール（例：`black`, `pytest`, `mypy`, `ruff` など）を実行する場合、`pip install` ではなく `uvx` を使ってオンデマンドで実行します。
- テスト実行: `uvx pytest tests/`
- フォーマッター: `uvx ruff format .` もしくは `uvx black .`
- 静的解析: `uvx mypy .`

### 2. プロジェクトの依存関係管理 (`uv add` / `uv pip`)
要件に応じて依存関係をインストールする際も `uv` を介します。
- `requirements.txt` を使ったインストール: `uv pip install -r requirements.txt`
- パッケージ追加: `uv pip install <package>`

### 3. AWS Lambda用のビルドとパッケージング
バックエンドの Lambda 用依存レイヤーを構築する際も `pip install -t ...` ではなく `uv pip install -t ...` を使用してビルドを高速化します。

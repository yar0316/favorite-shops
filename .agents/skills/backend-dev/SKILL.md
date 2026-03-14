---
name: backend-dev
description: バックエンド（AWS Lambda + API Gateway + DynamoDB）の機能実装を行うスキルです。バックエンドのAPI追加・変更を行う際に使用してください。
metadata:
  short-description: バックエンド機能拡張 / Backend feature development
---

# バックエンド実装（backend-dev）スキル

AWS Lambda + DynamoDB のバックエンド機能を実装・修正する際のスキルです。

## 前提条件

実装を開始する前に、必ず以下のドキュメントおよび**作成済みのSmallテスト**を確認してください。
- `docs/features/favorite-shops/architecture.md`
- `docs/features/favorite-shops/database-design.md`
- `tests/functions/<domain>/` 配下の pytest ファイル（詳細設計相当）

※もし対象機能のテストコード（詳細設計）がまだ存在しない場合は、先に **backend-test** スキルを使用してテスト（振る舞い仕様）を定義・合意してから実装に進んでください。

## ワークフロー

### 1. 対象ドメインと要件の確認

ユーザーにどの機能（ドメイン）を実装・修正するか確認します。
すでに `requirements.md` やタスク指示が存在する場合はそれを読み込みます。

### 2. 詳細設計（Smallテスト）の確認と実装方針の立案

対象機能に関する `tests/functions/<domain>/` 配下のテストコードを読み込みます。
このテストが満たすべき**振る舞い（契約）**となります。
テストケース（正常系・異常系）から、どのようなバリデーションやモック化された外部呼び出しが必要になるかを分析し、実装方針を立てます。

**【重要】テストコードの変更禁止**
- すでに合意されたテストコード（仕様）を、実装都合で勝手に書き換えてはいけません。
- テストコードはあくまで「実装結果を確認する（pytestを実行する）」ためにのみ使用し、編集対象には含めないでください。

### 3. 実装の基本ルール

以下のルールに厳密に従って `functions/<domain>/` 配下にコードを実装します。

1. **ドメイン単位の独立性**
   - 新しいリソース操作を追加する場合は、既存のLambdaハンドラに無理に混ぜず、API Gatewayのパス単位で適切な Lambda 関数（ドメイン）を判断してください。
2. **HTTPメソッドによるルーティング**
   - 1つの Lambda `handler.py` の中で `event["httpMethod"]` を使って CRUD 操作を分岐させてください。これ以上の複雑なWebフレームワーク（FastAPI等）は使用しません。
3. **Pydanticによる型定義**
   - `models.py` で Request / Response オブジェクトおよび DB エンティティを Pydantic v2 で厳密に定義してください。
4. **Lambda Layer の活用**
   - 共通処理（DB初期化、認証検証、共通ユーティリティ）は `layers/shared/` に配置・参照してください。
5. **型の強制**
   - Python 3.12+ の型ヒントを完備し、mypy (strict) をパスするコードを書いてください。

### 4. DynamoDB (Single Table Design) のアクセスパターン実装

データベース（DynamoDB）操作は `database-design.md` の PK/SK 設計に完全に従ってください。
- 新しいエンティティを追加する場合は、勝手にテーブル設計を変えず、まず `database-design.md` の更新を提案してください。
- RDBライクな結合（JOIN）は避け、フロントエンドで並列取得するか、Lambda側で1回の Query で関連アイテムをまとめて取得する設計にしてください。

### 5. レビューと完了

テストが通過し、仕様を満たしていることを確認した後、ユーザーにレビューを依頼します。

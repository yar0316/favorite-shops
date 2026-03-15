---
name: infra-dev
description: AWSリソース（API Gateway, DynamoDB, S3, IAMなど）をTerraformで構築・変更するスキルです。「インフラ設計書を変更して」「追加リソースが必要」「Terraformでインフラを構築して」などの要望があった際に使用してください。
---

# インフラ実装（infra-dev）スキル

Terraform を用いた AWS リソースプロビジョニングおよびインフラコードの修正を行うスキルです。

## 前提条件

実装を開始する前に、必ず以下のドキュメントを確認してください。
- `docs/features/favorite-shops/infrastructure.md`
- `docs/features/favorite-shops/architecture.md`
- `docs/features/favorite-shops/database-design.md`

## ワークフロー

### 1. 対象リソースと要件の確認

ユーザーにどのインフラリソースを追加・変更するか確認します。
関連する設計書（`infrastructure.md` 等）の要件と一致しているかチェックし、設計と異なる場合はまずドキュメントの更新を合意してください。

### 2. 環境別の構成ルール

このプロジェクトは `test` と `prod` の環境分離を行っています。コードは以下の構成に従って記述してください。
- `terraform/modules/` : 共通化されたモジュール（DynamoDB, S3, IAM, API Gatewayなど）を配置します。
- `terraform/environments/test/` : テスト環境固有のエントリポイントです。tfstate は S3 で管理します。
- `terraform/environments/prod/` : 本番環境固有のエントリポイントです。

### 3. Terraform実装の基本ルール

1. **tfstate のリモート管理**
   - 状態ファイル（`.tfstate`）は S3 バックエンドで管理されます（`favorite-shops-tfstate` バケット利用）。ステートロックには DynamoDB を使用します。
2. **モジュール化の徹底**
   - リソースは可能な限りモジュールとして切り出し、再利用可能に設計します。直接 `environments/` にリソース定義をハードコードせず、`modules/` 側の変数を渡す形で構成します。
3. **最小権限の原則（Least Privilege）**
   - IAM ロールおよびポリシーは、必要最低限の権限（例: 特定のDynamoDBテーブルへの `PutItem`, `GetItem`, `Query` のみで `Scan` は許可しない等）のみ付与してください。
   - `architecture.md` に記載されたセキュリティ設計を厳守してください。
4. **Lambda等との連携**
   - API Gateway のルーティングに Lambda ドメインを追加する場合などは、他ドメインに影響を与えないよう設定してください。

### 4. プラン作成と確認

コード変更後、`terraform validate` と `terraform plan`（環境固有のディレクトリ内で）を実行し、意図した変更が反映されるかプレビューを確認します。エラーがあれば修正します。

### 5. レビューと完了

変更内容と`terraform plan` の結果をユーザーに提示し、レビューを依頼してください。（`terraform apply` をAI自体が自動実行するかどうかは、ユーザーの指示に従います）。

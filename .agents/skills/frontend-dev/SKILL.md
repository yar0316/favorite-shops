---
name: frontend-dev
description: フロントエンド（Flutter + Riverpod）の機能や画面を実装・修正するスキルです。画面の追加やUIコンポーネントの操作を行う際に使用してください。
metadata:
  short-description: フロントエンド機能実装 / Frontend feature development
---

# フロントエンド実装（frontend-dev）スキル

Flutter アプリケーションのUIおよび状態管理・API連携を実装・修正する際のスキルです。

## 前提条件

実装を開始する前に、必ず以下のドキュメントを確認してください。
- `docs/features/favorite-shops/architecture.md`
- `docs/features/favorite-shops/client-architecture.md`

## ワークフロー

### 1. 対象ドメインと要件の確認

ユーザーにどの画面・機能を実装するか確認します。
関連する `requirements.md` やタスクが存在する場合はそれを読み込み、UIのイメージや状態管理の方針を立てます。

### 2. ディレクトリとUIコンポーネント配置ルールの確認

`client-architecture.md` に記載された構成ルール（`group_space` を起点とするネスト構造）に従ってファイルを配置します。
- UIコンポーネント（Widget）は以下の3層のルールに従って**必ず**分割・配置してください。
  1. `shared/components/` : アプリ全体で使い回す汎用Widget
  2. `features/<feature>/components/` : 機能（ドメイン）内で使い回す共通Widget
  3. `features/<feature>/<screen>/components/` : その画面固有だが、長さを抑えるために切り出したWidget
- `utils/` などの曖昧なフォルダは作成してはいけません。

### 3. 実装の基本ルール

以下のアーキテクチャルールに厳密に従ってコードを生成します。

1. **画面単位の状態管理とRiverpod**
   - 画面（Screen）と状態（Provider）をセットで作成し、各画面の状態管理は対応する Provider が担います。
   - API通信と状態管理は `AsyncNotifierProvider`（または `NotifierProvider`）に統一してください。
2. **Repository パターン**
   - API通信やローカルストレージへのアクセスは Repository に隠蔽し、Provider からそれを呼び出してください。
3. **Pydanticベースのモデルとの対応**
   - バックエンドのPydanticモデル定義（`architecture.md` 参照）と対応する型の Dart モデルを `freezed` や `json_serializable` 等を用いて堅牢に定義してください。
4. **並列データ取得**
   - 画面の描画に複数APIが必要な場合、Riverpodの仕組みを用いてAPIを並列取得し、クライアントに結合の責務を持たせてください。
5. **go_routerとディープリンク**
   - ルーティングは `go_router` で宣言的に行います。`group_space`（親コンテナ・ShellRoute等）内に各ドメインの画面（Tabs）がネストされる構造を正しく設定してください。

### 4. テストと表示の確認

必要に応じてWidgetテストやProviderの単体テストを記述し、UIや状態管理が想定通り動作することを確認します。

### 5. レビューと完了

実装が完了し要件を満たすことを確認した後、変更内容を添えてユーザーにレビューを依頼します。

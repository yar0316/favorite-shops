# favorite-shops - データベース設計書

## メタデータ

| 項目 | 内容 |
|------|------|
| ステータス | Draft |
| 作成日 | 2026-03-14 |
| 更新日 | 2026-03-14 |
| 親ドキュメント | [architecture.md](./architecture.md) |

---

## 1. 概要

Amazon DynamoDB を使用し、**シングルテーブルデザイン**を採用する。

### 選定理由

- サーバレスアーキテクチャ（Lambda）との相性が良い
- 永久無料枠（25GB, 25 WCU/RCU）で十分なキャパシティ
- アクセスパターンが明確で、複雑なJOINが不要

### テーブル命名

| 環境 | テーブル名 |
|------|-----------|
| 本番 | `favorite-shops-prod` |
| テスト | `favorite-shops-test` |

---

## 2. テーブル構造方針

### PK / SK パターン

シングルテーブルで複数エンティティを管理する。PK / SK のプレフィックスでエンティティ種別を区別する。

| PK パターン | SK パターン | エンティティ |
|------------|-----------|-------------|
| `USER#{userId}` | `PROFILE` | ユーザー |
| `USER#{userId}` | `GROUP#{groupId}` | グループ所属 |
| `USER#{userId}` | `SHOP-STATUS#{shopId}` | 自分の「行った/行きたい」ステータス管理（マイスペース用） |
| `GROUP#{groupId}` | `META` | グループ |
| `GROUP#{groupId}` | `MEMBER#{userId}` | グループメンバー |
| `GROUP#{groupId}` | `SHOP#{shopId}` | お店 |
| `SHOP#{shopId}` | `MENU#{menuId}` | おすすめメニュー |
| `SHOP#{shopId}` | `RANK#{userId}` | ランク（ユーザーごと） |
| `INVITE#{code}` | `META` | 招待コード |

### GSI（グローバルセカンダリインデックス）

| GSI名 | PK | SK | 用途 |
|--------|-----|-----|------|
| GSI1 | `GSI1PK` | `GSI1SK` | 逆引き・ソート用（例: お店を作成日時順で取得） |

---

## 3. アクセスパターン

| # | パターン | クエリ |
|---|----------|--------|
| 1 | ユーザープロフィール取得 | PK=`USER#{userId}`, SK=`PROFILE` |
| 2 | ユーザーの参加グループ一覧 | PK=`USER#{userId}`, SK begins_with `GROUP#` |
| 3 | グループのお店一覧 | PK=`GROUP#{groupId}`, SK begins_with `SHOP#` |
| 4 | グループのメンバー一覧 | PK=`GROUP#{groupId}`, SK begins_with `MEMBER#` |
| 5 | お店のメニュー一覧 | PK=`SHOP#{shopId}`, SK begins_with `MENU#` |
| 6 | お店のランク一覧（全メンバー） | PK=`SHOP#{shopId}`, SK begins_with `RANK#` |
| 7 | マイスペースのお店一覧 | PK=`USER#{userId}`, SK begins_with `SHOP-STATUS#` |
| 8 | 招待コード検証 | PK=`INVITE#{code}`, SK=`META` |
| 9 | お店一覧（日時順） | GSI1 利用 |

---

## 4. 設計方針

### 非正規化

DynamoDB では JOIN ができないため、表示に必要な情報を各アイテムに非正規化して持たせる（例: マイスペースのお店一覧 `SHOP-STATUS` アイテムに `shopName`, `area` などの基本情報を含める）。

非正規化データの更新は**ベストエフォート**とし、表示上の軽微な差異は許容する。

### TTL（有効期限）

招待コードに `expiresAt` を TTL 属性として設定し、期限切れアイテムを DynamoDB が自動削除する。

### 属性の詳細について

各エンティティの属性詳細は**コード（Pydantic モデル）を Single Source of Truth** とする。FastAPI の OpenAPI ドキュメント（Swagger UI）で最新の属性定義を確認可能。

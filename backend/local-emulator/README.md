## AWS Emulator でローカル動作確認

Docker Desktop の Linux コンテナを起動し、`backend` で実行します。AWS Emulator は AWS 公式 RPM からビルドされます（x86_64 用）。初回はイメージの取得とビルドに時間がかかります。

```powershell
cd backend
docker compose -f docker-compose.emulator.yml up --build -d
```

起動時に `favorite-shops-local` テーブルと `GSI1` を作成します。AWS の認証情報をマウントせず、Emulator が生成する認証情報と証明書を専用 Docker ボリュームで共有します。各 Lambda は Emulator にだけ接続し、認証はローカル用モックです。Lambda の各ポートと Emulator はローカルホストに限定します。Emulator のテレメトリーはオフです。

PowerShell から Lambda 実行 API を直接呼び出す例です。HTTP の外側の結果ではなく、返却された `statusCode` と `body` を確認してください。

```powershell
function Invoke-LocalLambda($port, $event) {
  $json = $event | ConvertTo-Json -Depth 20 -Compress
  Invoke-RestMethod -Uri "http://127.0.0.1:$port/2015-03-31/functions/function/invocations" -Method Post -ContentType 'application/json; charset=utf-8' -Body ([System.Text.Encoding]::UTF8.GetBytes($json))
}
$login = Invoke-LocalLambda 8081 @{httpMethod='POST'; body=(@{idToken='local'} | ConvertTo-Json -Compress)}
$login
$space = ($login.body | ConvertFrom-Json).my_space_id
$headers = @{Authorization='Bearer local'}
$shop = @{name='ローカル確認'; area='東京'; cuisine_genres=@('和食'); drink_genres=@('お茶')} | ConvertTo-Json -Compress
Invoke-LocalLambda 8083 @{httpMethod='POST'; headers=$headers; pathParameters=@{groupId=$space}; body=$shop}
Invoke-LocalLambda 8083 @{httpMethod='GET'; headers=$headers; pathParameters=@{groupId=$space}}
```

停止は `docker compose -f docker-compose.emulator.yml down`。Emulator のデータはメモリ内にあり、停止すると失われます。起動しない場合は `docker compose -f docker-compose.emulator.yml logs` で確認してください。

この構成は API Gateway、実 Firebase 認証、IAM 権限、画像アップロードの検証を行いません。AWS Emulator の DynamoDB の機能は AWS と完全には一致しないため、対応していない操作があれば実 AWS の test 環境でも確認してください。既存の `docker-compose.yml` は実 AWS test テーブル向けの別構成です。

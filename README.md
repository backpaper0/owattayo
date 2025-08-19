# Owattayo

Claude Codeの作業完了を通知するFastAPIアプリケーションです。Discordウェブフックとブラウザ通知（Server-Sent Events）の両方をサポートします。

## 機能

- **デュアル通知システム**
  - Discordウェブフック通知
  - ブラウザ通知（リアルタイム）
- **Claude Codeログファイル処理**
  - JSON Lines形式のファイルを読み取り
  - 最後のユーザーメッセージを抽出
- **日本語Webインターフェース**
  - 通知ログの表示
  - 接続状態の監視
  - ブラウザ通知の許可管理

## セットアップ

### 必要な環境
- Python 3.12
- uv（パッケージマネージャー）

### インストール

```bash
# 依存関係のインストール
uv sync
```

### 環境変数設定

`.env`ファイルを作成して以下の設定を行います：

```bash
# DiscordのウェブフックURL。Discordを用いた通知を行わない場合は空にする
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/your-webhook-url
# 通知のタイトル
TITLE=Claude Code work completed.
# 通知の本文テンプレート。作業のトリガーとなったプロンプトを埋め込むことができる
MESSAGE_TEMPLATE=prompt: {prompt}
```

## 実行方法

### 開発サーバー

```bash
uv run fastapi dev
```

### Docker

```bash
# イメージをビルド
docker build -t owattayo .

# コンテナを実行
docker run -p 8000:8000 owattayo
```

## API

### エンドポイント

- `POST /notify`: 通知を送信するメインエンドポイント
- `GET /notifications`: Server-Sent Eventsによるリアルタイム通知
- `GET /`: 静的ファイル（Webインターフェース）

### 使用例

```bash
# 基本的な通知
curl -X POST http://localhost:8000/notify

# Claude Codeログファイルを指定した通知
curl -X POST http://localhost:8000/notify \
  -H "Content-Type: application/json" \
  -d '{"transcript_path": "/path/to/transcript.jsonl"}'
```

## Claude Codeとの連携

Claude CodeのHookシステムと組み合わせて使用します：

```json
{
  "hooks": {
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "curl -X POST http://localhost:8000/notify -H \"Content-Type: application/json\" -d @-"
          }
        ]
      }
    ]
  }
}
```

## ファイル構成

```
/
├── main.py              # メインアプリケーション
├── pyproject.toml       # 依存関係とメタデータ
├── uv.lock             # 依存関係ロックファイル
├── Dockerfile          # Dockerイメージ設定
├── static/
│   ├── index.html      # Webインターフェース
│   └── favicon.svg     # ファビコン
└── .devcontainer/      # 開発コンテナ設定
```

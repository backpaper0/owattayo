# Owattayo

> [!NOTE]
> 「[Claude Codeをなるべく安全に動かすためのDev Containerを構築した](https://zenn.dev/backpaper0/articles/038838c4cec2a8)」からこのリポジトリを訪れた方へ。
> 記事を書いてからも開発を進めているため、本リポジトリの内容は記事の内容と乖離していると思います。
> 記事執筆時点の本リポジトリがどのような状態だったか見たい場合は[`v1`タグ](https://github.com/backpaper0/owattayo/tree/v1)をご覧ください。

Claude Codeの作業完了を通知するFastAPIアプリケーションです。Discordウェブフックとブラウザ通知（Server-Sent Events）の両方をサポートし、Claude Codeのhookシステムと連携して自動的に通知を送信します。

## 機能

- **デュアル通知システム**
  - Discordウェブフック通知（オプション）
  - Server-Sent Eventsによるリアルタイムブラウザ通知
- **Claude Code統合**
  - Stopフック経由で自動通知
  - トランスクリプトファイル解析（JSON Lines形式）
  - ユーザープロンプトの自動抽出
- **日本語Webインターフェース**
  - リアルタイム接続状態監視
  - ブラウザ通知の許可管理
  - 通知ログの表示

## セットアップ

### 必要な環境
- Python 3.12+
- uv（パッケージマネージャー）

### インストール

```bash
# 依存関係のインストール
uv sync

# 仮想環境をアクティブ化（必要に応じて）
source .venv/bin/activate
```

### 環境変数設定

`.env`ファイルを作成して以下の設定を行います：

```bash
# Discordウェブフック通知（オプション）
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/your-webhook-url

# 通知設定
TITLE=Claude Code work completed.
MESSAGE_TEMPLATE=prompt: {prompt}
```

### 設定項目

- `DISCORD_WEBHOOK_URL`: Discord通知用ウェブフックURL（未設定の場合はDiscord通知無効）
- `TITLE`: 通知タイトル（デフォルト: "Claude Code work completed."）
- `MESSAGE_TEMPLATE`: メッセージテンプレート（`{prompt}`でユーザープロンプトを埋め込み可能）

## 実行方法

### 開発サーバー

```bash
# 自動リロード付きで開発サーバーを起動
uv run fastapi dev
```

### Docker

```bash
# イメージをビルド
docker build -t owattayo .

# コンテナを実行
docker run -p 8000:8000 owattayo
```

アプリケーションは http://localhost:8000 でアクセス可能です。

## API仕様

### エンドポイント

| エンドポイント | メソッド | 説明 |
|---|---|---|
| `/notify` | POST | Claude Code完了通知の受信・処理 |
| `/notifications` | GET | Server-Sent Eventsストリーム |
| `/` | GET | 日本語Webインターフェース |

### リクエスト形式

```json
{
  "transcript_path": "/path/to/transcript.jsonl",
  "notifier": "workspace-name",
  "prompt": "直接指定されたプロンプト（オプション）"
}
```

### 使用例

```bash
# 基本的な通知
curl -X POST http://localhost:8000/notify

# トランスクリプトファイル指定
curl -X POST http://localhost:8000/notify \
  -H "Content-Type: application/json" \
  -d '{"transcript_path": "/path/to/transcript.jsonl", "notifier": "my-project"}'
```

## Claude Code連携

### Hookシステム設定

Claude Codeの設定ファイルに以下を追加：

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

### 動作の流れ

1. Claude Codeでタスクが完了
2. Stopフックが自動実行
3. トランスクリプトデータがPOST `/notify`に送信
4. 最後のユーザープロンプトを抽出
5. Discord・ブラウザに通知配信

## アーキテクチャ

### コア要素

- **Settings Management**: `.env`ファイルによる設定管理
- **Event Processing**: Claude Code StopEventの処理・トランスクリプト解析
- **Notification Manager**: SSEクライアント管理・ブロードキャスト
- **API Endpoints**: REST API・SSEストリーム・静的ファイル配信
- **Web Interface**: 日本語UI・リアルタイム通知表示

### ファイル構成

```
/
├── main.py              # 単一ファイルFastAPIアプリケーション
├── pyproject.toml       # プロジェクト設定・依存関係
├── uv.lock             # 依存関係ロックファイル
├── Dockerfile          # コンテナ設定
├── CLAUDE.md           # Claude Code向け開発ガイド
├── static/
│   ├── index.html      # 日本語Webインターフェース
│   └── favicon.svg     # ファビコン
└── .devcontainer/      # VS Code Dev Container設定
    ├── devcontainer.json
    └── compose.yaml
```

## トランスクリプト処理

JSON Lines形式のClaude Codeトランスクリプトから、ツール実行結果を除外してユーザーの最終プロンプトのみを抽出します。

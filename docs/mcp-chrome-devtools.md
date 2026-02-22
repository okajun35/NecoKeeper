# Codex用 Chrome DevTools MCP 手順

このドキュメントは、Codex セッションから `chrome-devtools` MCP を使うための
最短手順と確認方法をまとめたものです。

## 前提

- Codex の `chrome-devtools` MCP は **既存の Chrome/Chromium に接続**します。
- この環境は X が無いため **headless + remote debugging 必須**です。
- Codex 側設定は `~/.codex/config.toml` を使用します（Kiro とは別）。

## Codex 側の設定（1回だけ）

`~/.codex/config.toml` の `chrome-devtools` を以下にします:

```toml
[mcp_servers.chrome-devtools]
command = "npx"
args = ["chrome-devtools-mcp@latest", "--headless=true", "--browserUrl=http://127.0.0.1:9222"]
```

変更後は Codex セッションを再起動します。

## 毎回の起動手順（ユーザー側）

1) Chrome を起動（別ターミナル推奨）

```bash
google-chrome --headless=new --remote-debugging-port=9222 \
  --user-data-dir=/tmp/chrome-mcp --no-sandbox --disable-dev-shm-usage
```

2) 起動確認

```bash
curl -s http://127.0.0.1:9222/json/version
```

JSON が返れば準備完了です。Codex に「起動済み」と伝えてください。

## Codex 側の操作（再起動後）

Codex は以下の流れで接続を確認します。

1) `mcp__chrome-devtools__new_page` で対象ページを開く
2) `mcp__chrome-devtools__take_snapshot` で要素を取得
3) 必要に応じて `click` / `fill` / `press_key` を実行

## よくあるエラーと対処

- `Could not connect to Chrome ... 9222`
  → Chrome が起動していない / ポートが開いていない
  → `curl` で 9222 が開いているか確認

- `Missing X server to start the headful browser`
  → headless 設定が反映されていない
  → `~/.codex/config.toml` を再確認し、Codex 再起動

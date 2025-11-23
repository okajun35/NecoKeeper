# Chrome DevTools MCP セットアップガイド

このドキュメントは、Chrome DevTools MCPサーバーの接続手順をまとめたものです。

## 前提条件

- Node.js / npm がインストール済み
- Kiro IDE が起動している
- WSL環境（Linux）で動作

## 接続手順

### 1. MCP設定ファイルの確認

`.kiro/settings/mcp.json` に以下の設定があることを確認：

```json
{
  "mcpServers": {
    "chrome-devtools": {
      "command": "npx",
      "args": ["-y", "chrome-devtools-mcp@latest", "--headless=true"],
      "disabled": false,
      "autoApprove": [
        "list_pages",
        "navigate_page",
        "take_snapshot",
        "evaluate_script",
        "take_screenshot",
        "click",
        "list_console_messages",
        "get_console_message",
        "list_network_requests",
        "get_network_request",
        "new_page",
        "fill",
        "fill_form",
        "resize_page",
        "select_page",
        "wait_for",
        "handle_dialog",
        "press_key"
      ]
    }
  }
}
```

**重要**: WSL環境では `--headless=true` が必須です。

### 2. 既存のプロセスとキャッシュをクリア

接続エラーが発生した場合、以下のコマンドを実行：

```bash
# Chrome DevTools MCPプロセスを終了
pkill -f chrome-devtools-mcp

# キャッシュディレクトリを削除
rm -rf /home/<user>/.cache/chrome-devtools-mcp/chrome-profile
```

### 3. MCPサーバーを再接続

Kiro IDEで以下の操作を実行：

1. サイドバーの「MCP Servers」ビューを開く
2. `chrome-devtools` サーバーを見つける
3. 「Reconnect」ボタンをクリック

### 4. 接続確認

Kiro AIに以下のコマンドを実行させて接続を確認：

```javascript
// ページ一覧を取得
await mcp_chrome_devtools_list_pages()
```

成功すると以下のような出力が得られます：

```
# list_pages response
## Pages
0: about:blank [selected]
```

## トラブルシューティング

### エラー: "The browser is already running"

**原因**: 既存のChromeプロセスが残っている

**解決策**:
```bash
pkill -f chrome-devtools-mcp
rm -rf /home/<user>/.cache/chrome-devtools-mcp/chrome-profile
```

その後、Kiro IDEでMCPサーバーを再接続。

### エラー: "Missing X server to start the headful browser"

**原因**: ヘッドレスモードが無効になっている

**解決策**: `.kiro/settings/mcp.json` の `args` に `--headless=true` を追加：

```json
"args": ["-y", "chrome-devtools-mcp@latest", "--headless=true"]
```

### エラー: MCPサーバーが起動しない

**原因**: Node.js / npm が正しくインストールされていない

**解決策**:
```bash
# Node.jsのバージョン確認
node --version
npm --version

# npxが使えるか確認
npx --version
```

## 使用例

### ページに移動

```javascript
await mcp_chrome_devtools_navigate_page({
  type: "url",
  url: "http://localhost:8000/admin/login"
})
```

### ページのスナップショット取得

```javascript
await mcp_chrome_devtools_take_snapshot()
```

### フォーム入力

```javascript
await mcp_chrome_devtools_fill_form({
  elements: [
    { uid: "1_6", value: "admin@example.com" },
    { uid: "1_8", value: "admin123" }
  ]
})
```

### ボタンクリック

```javascript
await mcp_chrome_devtools_click({ uid: "1_9" })
```

### スクリーンショット撮影

```javascript
await mcp_chrome_devtools_take_screenshot()
```

### 要素が表示されるまで待機

```javascript
await mcp_chrome_devtools_wait_for({
  text: "Dashboard",
  timeout: 5000
})
```

### ネットワークリクエスト監視

```javascript
await mcp_chrome_devtools_list_network_requests()
```

### コンソールログ確認

```javascript
await mcp_chrome_devtools_list_console_messages()
```

## 定期メンテナンス

Chrome DevTools MCPを長時間使用する場合、定期的に以下を実行することを推奨：

```bash
# 1日1回程度
pkill -f chrome-devtools-mcp
rm -rf /home/<user>/.cache/chrome-devtools-mcp/chrome-profile
```

その後、Kiro IDEでMCPサーバーを再接続。

## 参考リンク

- [Chrome DevTools MCP GitHub](https://github.com/modelcontextprotocol/servers/tree/main/src/chrome-devtools)
- [Model Context Protocol 公式ドキュメント](https://modelcontextprotocol.io/)

---

**最終更新**: 2025-11-23
**動作確認環境**: WSL2 (Ubuntu 24.04), Node.js v20+

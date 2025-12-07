# NecoKeeper MCP Tools

このドキュメントは、NecoKeeperプロジェクトで利用可能なMCP（Model Context Protocol）ツールについて説明します。

## 概要

NecoKeeperには、Claude（AI）が自然言語で猫の管理を行うためのMCPツールが実装されています。これらのツールは、Automation APIを通じてNecoKeeperと連携します。

## 利用可能なツール

### 1. register_cat - 猫の登録

**用途**: 新しい猫をシステムに登録する

**必須パラメータ**:
- `name`: 猫の名前（1-100文字）
- `gender`: 性別（`male`, `female`, `unknown`）
- `pattern`: 柄・模様
- `tail_length`: 尻尾の長さ
- `age`: 年齢・大きさ

**任意パラメータ**:
- `status`: ステータス（デフォルト: "保護中"）
- `color`: 毛色
- `collar`: 首輪の情報
- `ear_cut`: 耳カットの有無（デフォルト: false）
- `features`: 特徴・性格
- `protected_at`: 保護日（YYYY-MM-DD形式）

**戻り値**:
```json
{
  "animal_id": 42,
  "name": "たま",
  "public_url": "http://localhost:8000/public/care?animal_id=42"
}
```

**使用例**:
```
ユーザー: "たまという名前のキジトラの猫を登録してください。オスで、尻尾は長く、成猫です。"

Claude: register_catツールを呼び出し、以下のパラメータで登録:
- name: "たま"
- gender: "male"
- pattern: "キジトラ"
- tail_length: "長い"
- age: "成猫"
```

### 2. generate_qr_card - 単一QRカードPDFの生成

**用途**: 登録済みの猫の単一QRカード付きPDF（A6サイズ）を生成する

**必須パラメータ**:
- `animal_id`: 猫のID（整数）

**戻り値**:
```json
{
  "pdf_path": "/path/to/NecoKeeper/tmp/qr/qr_card_42.pdf",
  "animal_id": 42
}
```

**使用例**:
```
ユーザー: "たまのQRカードを生成してください"

Claude: generate_qr_cardツールを呼び出し、animal_id=42でPDFを生成
```

**注意点**:
- PDFは`tmp/qr/qr_card_{animal_id}.pdf`に保存される
- A6サイズの単一QRカード
- 猫の写真、名前、ID、QRコードが含まれる
- ディレクトリが存在しない場合は自動作成される
- 既存のPDFは上書きされる

### 3. generate_qr - QRコードグリッドPDFの生成

**用途**: 登録済みの複数の猫のQRコード付きPDF（A4サイズ、2×5枚）を生成する

**必須パラメータ**:
- `animal_id`: 猫のID（整数）

**戻り値**:
```json
{
  "pdf_path": "/path/to/NecoKeeper/tmp/qr/qr_42.pdf",
  "animal_id": 42
}
```

**使用例**:
```
ユーザー: "たまのQRコードグリッドを生成してください"

Claude: generate_qrツールを呼び出し、animal_id=42でPDFを生成
```

**注意点**:
- PDFは`tmp/qr/qr_{animal_id}.pdf`に保存される
- A4サイズの面付けPDF（2×5枚、最大10枚）
- 複数の猫のQRカードを一度に印刷できる
- ディレクトリが存在しない場合は自動作成される
- 既存のPDFは上書きされる

### 4. upload_cat_image - 猫の画像アップロード

**用途**: 登録済みの猫のプロフィール画像をアップロードする

**必須パラメータ**:
- `animal_id`: 猫のID（整数）
- `image_path`: ローカル画像ファイルのパス（絶対パスまたは相対パス）

**戻り値**:
```json
{
  "image_url": "http://localhost:8000/media/animals/42/gallery/uuid.jpg",
  "animal_id": 42
}
```

**使用例**:
```
ユーザー: "たまの画像をアップロードしてください。パスは /home/user/tama.jpg です"

Claude: upload_cat_imageツールを呼び出し、画像をアップロード
```

**注意点**:
- 対応形式: JPEG、PNG、WebP
- 最大ファイルサイズ: 5MB（デフォルト）
- 最大画像枚数: 20枚/猫（デフォルト）
- 画像は`media/animals/{animal_id}/gallery/`にUUIDベースのファイル名で保存される
- 画像は自動的に最適化される

## 典型的なワークフロー

### シナリオ1: 新しい猫の完全登録

```
1. ユーザー: "新しい猫を登録したいです。名前はミケで、三毛猫のメスです"
   → Claude: register_catで登録

2. ユーザー: "ミケの写真をアップロードしてください。/path/to/mike.jpg"
   → Claude: upload_cat_imageで画像アップロード

3. ユーザー: "ミケのQRカードを作ってください"
   → Claude: generate_qr_cardでPDF生成（A6サイズ、単一カード）
```

### シナリオ2: 複数の猫を一括登録

```
ユーザー: "3匹の猫を登録してください。
         1. たま（オス、キジトラ、成猫）
         2. クロ（メス、黒猫、子猫）
         3. シロ（不明、白猫、成猫）"

Claude:
1. register_catを3回呼び出し
2. 各猫のIDを記録
3. 必要に応じてQRコードを生成
```

## 技術的な詳細

### 認証

MCPツールは内部的にAutomation APIを使用します：

- **認証方式**: Automation API Key（`X-Automation-Key`ヘッダー）
- **環境変数**: `AUTOMATION_API_KEY`（最低32文字）
- **設定**: `.env`ファイルで`ENABLE_AUTOMATION_API=true`が必要

### エンドポイント

MCPツールは以下のAutomation APIエンドポイントを使用：

| ツール | エンドポイント | メソッド |
|--------|--------------|----------|
| register_cat | `/api/automation/animals` | POST |
| generate_qr_card | `/api/automation/pdf/qr-card` | POST |
| generate_qr | `/api/automation/pdf/qr-card-grid` | POST |
| upload_cat_image | `/api/automation/animals/{id}/images` | POST |

### エラーハンドリング

MCPツールは以下のエラーを適切に処理します：

1. **ネットワークエラー**: API接続失敗
2. **認証エラー**: API Key不正または期限切れ
3. **バリデーションエラー**: 不正なパラメータ
4. **ファイルエラー**: 画像ファイルが見つからない、形式不正
5. **リソースエラー**: 猫が存在しない（404）

エラー発生時は、ユーザーに分かりやすいメッセージを返します。

## 使用時の注意点

### DO（推奨）

- ✅ ユーザーが提供した情報を正確にパラメータに変換する
- ✅ 登録後のanimal_idを記録し、後続の操作で使用する
- ✅ エラーが発生した場合は、具体的な原因をユーザーに説明する
- ✅ 画像パスは絶対パスで指定する（相対パスも可能だが推奨しない）
- ✅ 複数の操作を行う場合は、各ステップの結果を確認する

### DON'T（非推奨）

- ❌ 必須パラメータを省略しない
- ❌ 不正な値（空文字列、nullなど）を送信しない
- ❌ animal_idを間違えない（登録時の戻り値を使用）
- ❌ 存在しない画像パスを指定しない
- ❌ エラーを無視して次の操作に進まない

## トラブルシューティング

### 問題: "Authentication error: Invalid or expired token"

**原因**: API Keyが設定されていない、または不正

**解決方法**:
1. `.env`ファイルに`AUTOMATION_API_KEY`が設定されているか確認
2. API Keyが32文字以上であることを確認
3. `ENABLE_AUTOMATION_API=true`が設定されているか確認
4. NecoKeeper APIを再起動

### 問題: "Network error: Could not connect to NecoKeeper API"

**原因**: NecoKeeper APIが起動していない

**解決方法**:
1. NecoKeeper APIが起動しているか確認: `curl http://localhost:8000/docs`
2. `NECOKEEPER_API_URL`が正しいか確認（デフォルト: `http://localhost:8000`）
3. ファイアウォールがポート8000をブロックしていないか確認

### 問題: "File error: Image file not found"

**原因**: 画像ファイルのパスが不正

**解決方法**:
1. ファイルパスが正しいか確認（絶対パスを推奨）
2. ファイルが存在するか確認: `ls -la /path/to/image.jpg`
3. ファイルの読み取り権限があるか確認

### 問題: 猫が見つからない（404エラー）

**原因**: 指定したanimal_idが存在しない

**解決方法**:
1. register_catの戻り値からanimal_idを正確に取得
2. データベースに猫が登録されているか確認
3. 別の猫のIDと混同していないか確認

## 開発者向け情報

### ファイル構造

```
app/mcp/
├── __init__.py          # パッケージ初期化
├── __main__.py          # エントリーポイント
├── config.py            # 設定管理
├── api_client.py        # Automation API クライアント
├── server.py            # MCPサーバー（FastMCP）
├── error_handler.py     # エラーハンドリング
├── tools/                  # ツール実装
│   ├── register_cat.py     # 猫登録ツール
│   ├── generate_qr_card.py # 単一QRカード生成ツール
│   ├── generate_qr.py      # QRグリッド生成ツール
│   └── upload_image.py     # 画像アップロードツール
└── README.md            # 詳細ドキュメント
```

### テスト

```bash
# MCPツールのテストを実行
pytest tests/mcp/ -v

# 統合テストを実行
pytest tests/mcp/test_integration.py -v

# カバレッジ付きで実行
pytest tests/mcp/ --cov=app/mcp --cov-report=html
```

### デバッグ

デバッグログを有効化：

```bash
# .envファイルに追加
MCP_LOG_LEVEL=DEBUG
MCP_LOG_FILE=logs/mcp-server.log

# ログを確認
tail -f logs/mcp-server.log
```

## 関連ドキュメント

- **MCP Server README**: `app/mcp/README.md` - 詳細な技術ドキュメント
- **Automation API README**: `app/api/automation/README.md` - API仕様
- **Design Document**: `.kiro/specs/claude-mcp-integration/design.md` - 設計書
- **Requirements**: `.kiro/specs/claude-mcp-integration/requirements.md` - 要件定義

## まとめ

NecoKeeper MCPツールを使用することで、Claudeは自然言語で猫の管理を行えます。ユーザーの指示を適切に解釈し、正しいパラメータでツールを呼び出すことで、効率的な猫の登録・管理が可能になります。

エラーが発生した場合は、ユーザーに分かりやすく説明し、適切な解決方法を提案してください。

---

**最終更新**: 2024-12-02
**バージョン**: 1.1.0

## 変更履歴

### v1.1.0 (2024-12-02)
- ✨ `generate_qr_card`ツールを追加（単一QRカード、A6サイズ）
- 🐛 画像パス処理を修正（`media/`プレフィックスの問題を解決）
- 📝 `generate_qr`を`generate_qr`（グリッド）と`generate_qr_card`（単一）に分離

### v1.0.0 (2024-11-29)
- 🎉 初回リリース
- ✨ `register_cat`、`generate_qr`、`upload_cat_image`ツールを実装

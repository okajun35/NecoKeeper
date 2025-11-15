# Public フォーム 404エラー修正手順

## 現在の状況

以下の3つの404エラーが発生しています：
1. `/static/images/default.svg` - デフォルト画像（✅ 修正済み）
2. `/static/icons/icon-*.png` - PWAアイコン（❌ 未作成）
3. `/static/js/sw.js` - Service Worker（✅ パス修正済み）

## 修正内容

### ✅ 完了した修正

1. **Service Worker登録コード追加**
   - `app/templates/public/care_form.html` にService Worker登録コードを追加
   - パス: `/static/js/sw.js`

2. **デフォルト画像作成**
   - `app/static/images/default.svg` を作成（猫のシルエット）
   - HTMLで参照するパスを修正

### ❌ 残っている問題: PWAアイコン

PWAアイコンが存在しないため、以下のいずれかの方法で対応してください：

## 解決方法

### 方法1: PWAアイコンを手動で作成（推奨）

1. **Pythonスクリプトで作成**（最も簡単）:
   ```bash
   # プロジェクトルートで実行
   python create_icons_simple.py
   ```

2. **オンラインツールで作成**:
   - https://www.pwabuilder.com/imageGenerator にアクセス
   - 512x512pxの画像をアップロード
   - すべてのサイズをダウンロード
   - `app/static/icons/` に配置

3. **手動でコピー**（開発用の簡易対応）:
   - 任意の正方形PNG画像を用意
   - 以下のファイル名でコピー:
     - `icon-72x72.png`
     - `icon-96x96.png`
     - `icon-128x128.png`
     - `icon-144x144.png`
     - `icon-152x152.png`
     - `icon-192x192.png`
     - `icon-384x384.png`
     - `icon-512x512.png`

### 方法2: PWA機能を一時的に無効化

開発中でPWA機能が不要な場合、manifest.jsonの参照を削除：

```html
<!-- この行をコメントアウト -->
<!-- <link rel="manifest" href="/static/manifest.json"> -->
```

## 動作確認

1. サーバーを起動:
   ```bash
   uvicorn app.main:app --reload
   ```

2. ブラウザでアクセス:
   ```
   http://localhost:8000/public/care-form?animal_id=1
   ```

3. DevToolsで確認:
   - Console: エラーがないか確認
   - Network: 404エラーがないか確認
   - Application > Manifest: アイコンが表示されるか確認

## トラブルシューティング

### アイコンが404エラーのまま

- ファイル名が正確か確認（`icon-144x144.png`）
- ファイルが `app/static/icons/` に配置されているか確認
- サーバーを再起動

### Service Workerが登録されない

- ブラウザのキャッシュをクリア
- DevTools > Application > Service Workers で確認
- HTTPSまたはlocalhostで実行しているか確認

### デフォルト画像が表示されない

- `app/static/images/default.svg` が存在するか確認
- ブラウザのキャッシュをクリア

## 詳細ドキュメント

- PWAアイコンの詳細: `docs/setup-pwa-icons.md`
- アイコン生成スクリプト: `scripts/create_placeholder_icons.py`

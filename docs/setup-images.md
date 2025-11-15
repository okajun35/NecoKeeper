# 画像ファイルのセットアップ

Public フォームで使用する画像ファイルの準備手順です。

## 1. デフォルト猫画像

**配置場所**: `app/static/images/default.jpg`

**推奨仕様**:
- サイズ: 400x400px（正方形）
- フォーマット: JPEG または PNG
- ファイルサイズ: 100KB以下
- 内容: 猫のシルエット、プレースホルダー画像

**作成方法**:
```bash
# ImageMagick を使用する場合
convert -size 400x400 xc:lightgray \
  -gravity center \
  -pointsize 48 \
  -annotate +0+0 '🐱' \
  app/static/images/default.jpg

# または、フリー素材サイトからダウンロード
# - Unsplash: https://unsplash.com/s/photos/cat
# - Pixabay: https://pixabay.com/images/search/cat/
```

## 2. PWA アイコン

**配置場所**: `app/static/icons/`

**必要なサイズ**:
- icon-72x72.png
- icon-96x96.png
- icon-128x128.png
- icon-144x144.png
- icon-152x152.png
- icon-192x192.png
- icon-384x384.png
- icon-512x512.png

**作成手順**:

### ステップ1: マスター画像を作成（512x512px）

デザインツールで作成:
- Figma, Canva, Photoshop など
- 背景色: #4f46e5（Indigo）
- アイコン: 猫のシルエットまたはロゴ
- 余白: 各辺から10%程度

### ステップ2: 各サイズにリサイズ

**ImageMagick を使用**:
```bash
# マスター画像から各サイズを生成
for size in 72 96 128 144 152 192 384 512; do
  convert app/static/icons/icon-512x512.png \
    -resize ${size}x${size} \
    app/static/icons/icon-${size}x${size}.png
done
```

**オンラインツールを使用**:
- [RealFaviconGenerator](https://realfavicongenerator.net/)
- [PWA Asset Generator](https://www.pwabuilder.com/)

### ステップ3: 配置

すべてのアイコンを `app/static/icons/` に配置します。

## 3. 簡易セットアップ（開発用）

開発環境では、単色のプレースホルダー画像で代用できます：

```bash
# デフォルト猫画像（グレー背景）
mkdir -p app/static/images
convert -size 400x400 xc:lightgray \
  -gravity center \
  -pointsize 72 \
  -fill gray \
  -annotate +0+0 '🐱' \
  app/static/images/default.jpg

# PWA アイコン（Indigo背景）
mkdir -p app/static/icons
for size in 72 96 128 144 152 192 384 512; do
  convert -size ${size}x${size} xc:'#4f46e5' \
    -gravity center \
    -pointsize $((size/4)) \
    -fill white \
    -annotate +0+0 '🐱' \
    app/static/icons/icon-${size}x${size}.png
done
```

## 4. Service Worker のエラーについて

**エラー**: `GET /serviceworker.js HTTP/1.1 404 Not Found`

**原因**: ブラウザが古いキャッシュから `/serviceworker.js` を探している

**対応**:
1. **現在の実装は正しい**: `/static/js/sw.js` を使用
2. **404エラーは無視してOK**: 実際の Service Worker は正常に登録されている
3. **キャッシュをクリア**: ブラウザのキャッシュをクリアすればエラーが消える

**確認方法**:
```javascript
// Console で実行
navigator.serviceWorker.getRegistrations().then(registrations => {
  console.log('登録済み Service Worker:', registrations);
});
```

## 5. 404エラーを解消する方法

### オプション1: 画像を無視する（開発環境）

`.gitignore` に追加済みなので、画像ファイルは各自で準備します。

### オプション2: プレースホルダー画像を生成

Python スクリプトで生成:

```python
from PIL import Image, ImageDraw, ImageFont

# デフォルト猫画像
img = Image.new('RGB', (400, 400), color='lightgray')
draw = ImageDraw.Draw(img)
draw.text((200, 200), '🐱', fill='gray', anchor='mm')
img.save('app/static/images/default.jpg')
```

### オプション3: SVG プレースホルダー

```html
<!-- SVG プレースホルダー -->
<svg width="400" height="400" xmlns="http://www.w3.org/2000/svg">
  <rect width="400" height="400" fill="#e5e7eb"/>
  <text x="200" y="200" font-size="72" text-anchor="middle" fill="#9ca3af">🐱</text>
</svg>
```

---

画像ファイルを準備するスクリプトを作成しますか？それとも、404エラーを無視する設定にしますか？

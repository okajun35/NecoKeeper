# PWAアイコンのセットアップ

NecoKeeperをPWA（Progressive Web App）として動作させるには、アイコン画像が必要です。

## 必要なアイコンサイズ

以下のサイズのPNG画像を `app/static/icons/` ディレクトリに配置してください：

- `icon-72x72.png` (72x72px)
- `icon-96x96.png` (96x96px)
- `icon-128x128.png` (128x128px)
- `icon-144x144.png` (144x144px)
- `icon-152x152.png` (152x152px)
- `icon-192x192.png` (192x192px)
- `icon-384x384.png` (384x384px)
- `icon-512x512.png` (512x512px)

## アイコン作成方法

### オプション1: オンラインツールを使用

1. **PWA Asset Generator** (推奨)
   - https://www.pwabuilder.com/imageGenerator
   - 512x512pxの元画像をアップロード
   - すべてのサイズを自動生成
   - ダウンロードして `app/static/icons/` に配置

2. **Favicon Generator**
   - https://realfavicongenerator.net/
   - 元画像をアップロード
   - PWAアイコンを生成

### オプション2: ImageMagickで一括生成

元画像（512x512px以上推奨）から一括生成：

```bash
# ImageMagickをインストール（Windows）
# https://imagemagick.org/script/download.php

# 一括生成スクリプト
cd app/static/icons

# 各サイズを生成
magick convert source.png -resize 72x72 icon-72x72.png
magick convert source.png -resize 96x96 icon-96x96.png
magick convert source.png -resize 128x128 icon-128x128.png
magick convert source.png -resize 144x144 icon-144x144.png
magick convert source.png -resize 152x152 icon-152x152.png
magick convert source.png -resize 192x192 icon-192x192.png
magick convert source.png -resize 384x384 icon-384x384.png
magick convert source.png -resize 512x512 icon-512x512.png
```

### オプション3: Pythonスクリプトで生成

```python
from PIL import Image
import os

# 元画像のパス
source_image = "source.png"
output_dir = "app/static/icons"

# 必要なサイズ
sizes = [72, 96, 128, 144, 152, 192, 384, 512]

# 元画像を開く
img = Image.open(source_image)

# 各サイズを生成
for size in sizes:
    resized = img.resize((size, size), Image.Resampling.LANCZOS)
    output_path = os.path.join(output_dir, f"icon-{size}x{size}.png")
    resized.save(output_path, "PNG")
    print(f"Created: {output_path}")

print("All icons generated successfully!")
```

## 簡易セットアップ（開発用）

開発環境で動作確認するだけなら、1つのアイコンをすべてのサイズにコピーすることもできます：

```bash
# Windows PowerShell
cd app/static/icons
Copy-Item default-icon.png icon-72x72.png
Copy-Item default-icon.png icon-96x96.png
Copy-Item default-icon.png icon-128x128.png
Copy-Item default-icon.png icon-144x144.png
Copy-Item default-icon.png icon-152x152.png
Copy-Item default-icon.png icon-192x192.png
Copy-Item default-icon.png icon-384x384.png
Copy-Item default-icon.png icon-512x512.png
```

## デフォルトアイコンの作成

アイコンがない場合は、シンプルなプレースホルダーを作成できます：

```python
from PIL import Image, ImageDraw, ImageFont

def create_placeholder_icon(size, output_path):
    """プレースホルダーアイコンを作成"""
    # 背景色（インディゴ）
    img = Image.new('RGB', (size, size), color='#4f46e5')
    draw = ImageDraw.Draw(img)

    # テキスト "NK" を中央に描画
    try:
        font = ImageFont.truetype("arial.ttf", size // 3)
    except:
        font = ImageFont.load_default()

    text = "NK"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    position = ((size - text_width) // 2, (size - text_height) // 2)
    draw.text(position, text, fill='white', font=font)

    img.save(output_path, "PNG")
    print(f"Created placeholder: {output_path}")

# すべてのサイズを生成
sizes = [72, 96, 128, 144, 152, 192, 384, 512]
for size in sizes:
    create_placeholder_icon(size, f"app/static/icons/icon-{size}x{size}.png")
```

## 確認方法

1. 開発サーバーを起動：
   ```bash
   uvicorn app.main:app --reload
   ```

2. ブラウザで確認：
   - http://localhost:8000/public/care-form?animal_id=1
   - DevToolsのConsoleでエラーがないか確認
   - Applicationタブ > Manifestでアイコンが表示されるか確認

3. PWAインストールテスト：
   - Chrome: アドレスバーの右側にインストールアイコンが表示される
   - Edge: 同様にインストールアイコンが表示される

## トラブルシューティング

### アイコンが404エラー

- ファイル名が正確か確認（`icon-144x144.png`）
- ファイルが `app/static/icons/` に配置されているか確認
- サーバーを再起動

### アイコンが表示されない

- ブラウザのキャッシュをクリア（Ctrl+Shift+Delete）
- manifest.jsonのパスが正しいか確認（`/static/icons/icon-*.png`）
- Service Workerをアンレジスター（DevTools > Application > Service Workers > Unregister）

### PWAインストールボタンが表示されない

- HTTPSまたはlocalhostで実行しているか確認
- manifest.jsonが正しく読み込まれているか確認
- すべての必須アイコン（192x192, 512x512）が存在するか確認

## 参考リンク

- [PWA Builder](https://www.pwabuilder.com/)
- [Web.dev - Add a web app manifest](https://web.dev/add-manifest/)
- [MDN - Web app manifests](https://developer.mozilla.org/en-US/docs/Web/Manifest)

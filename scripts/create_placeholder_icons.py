"""
PWA用プレースホルダーアイコン生成スクリプト

開発環境用のシンプルなアイコンを生成します。
本番環境では適切なデザインのアイコンに置き換えてください。
"""

from __future__ import annotations

from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("Error: Pillow is not installed.")
    print("Install it with: pip install Pillow")
    exit(1)


def create_placeholder_icon(size: int, output_path: Path) -> None:
    """
    プレースホルダーアイコンを作成

    Args:
        size: アイコンのサイズ（正方形）
        output_path: 出力ファイルパス
    """
    # 背景色（インディゴ）
    img = Image.new("RGB", (size, size), color="#4f46e5")
    draw = ImageDraw.Draw(img)

    # テキスト "NK" を中央に描画
    text = "NK"
    font_size = size // 3

    try:
        # システムフォントを試す
        font = ImageFont.truetype("arial.ttf", font_size)
    except OSError:
        try:
            # Windowsの別のフォント
            font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", font_size)
        except OSError:
            try:
                # Linuxのフォント
                font = ImageFont.truetype(
                    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size
                )
            except OSError:
                # デフォルトフォント
                print(f"Warning: Using default font for {size}x{size}")
                font = ImageFont.load_default()

    # テキストのバウンディングボックスを取得
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # 中央に配置
    position = ((size - text_width) // 2, (size - text_height) // 2 - bbox[1])
    draw.text(position, text, fill="white", font=font)

    # 保存
    img.save(output_path, "PNG")
    print(f"✓ Created: {output_path}")


def main() -> None:
    """メイン処理"""
    # 出力ディレクトリ
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    output_dir = project_root / "app" / "static" / "icons"

    # ディレクトリが存在しない場合は作成
    output_dir.mkdir(parents=True, exist_ok=True)

    # 必要なサイズ
    sizes = [72, 96, 128, 144, 152, 192, 384, 512]

    print("Creating placeholder PWA icons...")
    print(f"Output directory: {output_dir}")
    print()

    # 各サイズを生成
    for size in sizes:
        output_path = output_dir / f"icon-{size}x{size}.png"
        create_placeholder_icon(size, output_path)

    print()
    print("✓ All icons generated successfully!")
    print()
    print("Note: These are placeholder icons for development.")
    print("For production, replace them with properly designed icons.")
    print("See docs/setup-pwa-icons.md for more information.")


if __name__ == "__main__":
    main()

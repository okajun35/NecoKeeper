#!/usr/bin/env python3
"""
Kiroween Theme Asset Setup Script

このスクリプトは、Kiroween Theme（Necro-Terminal Edition）用の
Halloween画像アセットを準備します。

機能:
- tmp/for_icon/からapp/static/icons/へ画像をコピー
- 各画像を適切なサイズにリサイズ（favicon、logo、placeholder）
- WebP形式での最適化

Requirements: 13.1, 13.2, 13.3, 13.4
"""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image


def setup_directories() -> tuple[Path, Path]:
    """
    ソースとターゲットディレクトリを設定

    Returns:
        tuple[Path, Path]: (source_dir, target_dir)
    """
    # プロジェクトルートを取得
    script_dir = Path(__file__).parent
    project_root = script_dir.parent

    source_dir = project_root / "tmp" / "for_icon"
    target_dir = project_root / "app" / "static" / "icons"

    # ディレクトリの存在確認
    if not source_dir.exists():
        print(f"❌ Error: Source directory not found: {source_dir}")
        sys.exit(1)

    if not target_dir.exists():
        print(f"Creating target directory: {target_dir}")
        target_dir.mkdir(parents=True, exist_ok=True)

    return source_dir, target_dir


def resize_image(
    source_path: Path, target_path: Path, size: tuple[int, int] | None = None
) -> None:
    """
    画像をリサイズして保存

    Args:
        source_path: ソース画像パス
        target_path: ターゲット画像パス
        size: リサイズサイズ (width, height)。Noneの場合は元のサイズを維持
    """
    try:
        with Image.open(source_path) as img:
            # RGBA形式に変換（透過対応）
            if img.mode != "RGBA":
                img = img.convert("RGBA")

            # リサイズ
            if size:
                # アスペクト比を維持してリサイズ
                img.thumbnail(size, Image.Resampling.LANCZOS)

            # WebP形式で保存（品質80、ファイルサイズ最適化）
            img.save(target_path, "WEBP", quality=80, method=6)
            print(f"✅ Saved: {target_path.name} ({size if size else 'original'})")

    except Exception as e:
        print(f"❌ Error processing {source_path.name}: {e}")
        raise


def copy_and_resize_assets(source_dir: Path, target_dir: Path) -> None:
    """
    アセットをコピーしてリサイズ

    Requirements: 13.1, 13.2, 13.3, 13.4

    Args:
        source_dir: ソースディレクトリ
        target_dir: ターゲットディレクトリ
    """
    print("\n🎃 Kiroween Theme Asset Setup")
    print("=" * 50)

    # アセットマッピング: (source_filename, target_filename, size)
    # size: (width, height) or None for original size
    assets = [
        # Favicon（32x32）
        ("halloween_icon.webp", "halloween_icon.webp", (32, 32)),
        # Logo（レスポンシブ、最大幅400px）
        ("hallwin_logo.webp", "halloween_logo.webp", (400, 400)),
        # Placeholder（300x300）
        ("halloween_logo2.webp", "halloween_logo_2.webp", (300, 300)),
    ]

    success_count = 0
    error_count = 0

    for source_name, target_name, size in assets:
        source_path = source_dir / source_name
        target_path = target_dir / target_name

        if not source_path.exists():
            print(f"⚠️  Warning: Source file not found: {source_name}")
            error_count += 1
            continue

        try:
            resize_image(source_path, target_path, size)
            success_count += 1
        except Exception:
            error_count += 1

    # サマリー
    print("\n" + "=" * 50)
    print(f"✅ Success: {success_count} files")
    if error_count > 0:
        print(f"❌ Errors: {error_count} files")
    print("=" * 50)

    if error_count > 0:
        print("\n⚠️  Some files could not be processed.")
        print("Please check the error messages above.")
        sys.exit(1)
    else:
        print("\n🎉 All assets successfully prepared!")
        print("\nNext steps:")
        print("1. Set KIROWEEN_MODE=true in your .env file")
        print("2. Restart the application")
        print("3. Enjoy the Necro-Terminal theme! 👻")


def main() -> None:
    """メイン処理"""
    try:
        source_dir, target_dir = setup_directories()
        copy_and_resize_assets(source_dir, target_dir)
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

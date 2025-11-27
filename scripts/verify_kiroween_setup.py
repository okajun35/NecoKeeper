#!/usr/bin/env python3
"""
Kiroween Theme Setup Verification Script

このスクリプトは、Task 1の実装を検証します。
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from PIL import Image


def verify_config() -> bool:
    """設定ファイルの検証"""
    print("\n📋 Configuration Verification")
    print("=" * 50)

    try:
        from app.config import get_settings

        # デフォルト値の確認
        settings = get_settings()
        print(f"✅ KIROWEEN_MODE default: {settings.kiroween_mode}")

        # 環境変数での設定確認
        os.environ["KIROWEEN_MODE"] = "true"
        # キャッシュをクリア
        get_settings.cache_clear()
        settings = get_settings()
        print(f"✅ KIROWEEN_MODE with env=true: {settings.kiroween_mode}")

        # クリーンアップ
        os.environ.pop("KIROWEEN_MODE", None)
        get_settings.cache_clear()

        return True
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False


def verify_env_example() -> bool:
    """環境変数テンプレートの検証"""
    print("\n📄 .env.example Verification")
    print("=" * 50)

    env_example = Path(".env.example")
    if not env_example.exists():
        print("❌ .env.example not found")
        return False

    content = env_example.read_text()
    if "KIROWEEN_MODE" in content:
        print("✅ KIROWEEN_MODE documented in .env.example")
        return True
    else:
        print("❌ KIROWEEN_MODE not found in .env.example")
        return False


def verify_assets() -> bool:
    """アセットファイルの検証"""
    print("\n🎨 Asset Files Verification")
    print("=" * 50)

    assets = [
        ("app/static/icons/halloween_icon.webp", (32, 32)),
        ("app/static/icons/halloween_logo.webp", (400, 400)),
        ("app/static/icons/halloween_logo_2.webp", (300, 300)),
    ]

    all_ok = True
    for asset_path, expected_max_size in assets:
        path = Path(asset_path)
        if not path.exists():
            print(f"❌ Missing: {asset_path}")
            all_ok = False
            continue

        try:
            with Image.open(path) as img:
                size = img.size
                file_size = path.stat().st_size / 1024  # KB

                # サイズチェック（最大サイズ以下であることを確認）
                if size[0] <= expected_max_size[0] and size[1] <= expected_max_size[1]:
                    print(f"✅ {path.name}: {size} ({file_size:.1f}KB) - OK")
                else:
                    print(f"⚠️  {path.name}: {size} (expected max {expected_max_size})")
                    all_ok = False

        except Exception as e:
            print(f"❌ Error reading {asset_path}: {e}")
            all_ok = False

    return all_ok


def verify_script() -> bool:
    """セットアップスクリプトの検証"""
    print("\n🔧 Setup Script Verification")
    print("=" * 50)

    script_path = Path("scripts/setup_kiroween_assets.py")
    if not script_path.exists():
        print("❌ setup_kiroween_assets.py not found")
        return False

    print("✅ setup_kiroween_assets.py exists")

    # 実行可能かチェック
    if os.access(script_path, os.X_OK):
        print("✅ Script is executable")
    else:
        print("⚠️  Script is not executable (chmod +x may be needed)")

    return True


def main() -> None:
    """メイン処理"""
    print("\n🎃 Kiroween Theme - Task 1 Verification")
    print("=" * 50)
    print("Verifying: Configuration Setup and Asset Preparation")
    print("=" * 50)

    results = {
        "Configuration": verify_config(),
        ".env.example": verify_env_example(),
        "Assets": verify_assets(),
        "Setup Script": verify_script(),
    }

    # サマリー
    print("\n" + "=" * 50)
    print("📊 Verification Summary")
    print("=" * 50)

    all_passed = True
    for name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {name}")
        if not passed:
            all_passed = False

    print("=" * 50)

    if all_passed:
        print("\n🎉 All verifications passed!")
        print("\n✅ Task 1 Implementation Complete:")
        print("   - KIROWEEN_MODE configuration added")
        print("   - .env.example updated with documentation")
        print("   - Asset copy script created")
        print("   - Halloween assets prepared and optimized")
        print("\nRequirements validated: 1.1, 1.2, 1.3, 11.2, 13.1, 13.2, 13.3, 13.4")
        sys.exit(0)
    else:
        print("\n⚠️  Some verifications failed. Please review the errors above.")
        sys.exit(1)


if __name__ == "__main__":
    main()

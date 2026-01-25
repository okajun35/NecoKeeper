#!/usr/bin/env python3
"""
猫データの診断スクリプト

本番環境で500エラーが発生する原因を特定するため、
全ての猫データをバリデーションしてエラーを報告します。

使用方法:
    python scripts/diagnose_animals.py
"""

import sys
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import SessionLocal
from app.models.animal import Animal
from app.schemas.animal import AnimalResponse


def diagnose_animals():
    """全ての猫データを診断"""
    db = SessionLocal()

    try:
        print("=" * 70)
        print("猫データ診断ツール")
        print("=" * 70)

        # 全ての猫を取得
        animals = db.query(Animal).all()
        print(f"\n総猫数: {len(animals)}")

        # ステータス別の集計
        from collections import Counter

        status_counts = Counter(animal.status for animal in animals)
        print("\nステータス別集計:")
        for status, count in sorted(status_counts.items()):
            print(f"  {status}: {count}件")

        # バリデーションエラーをチェック
        print("\n" + "=" * 70)
        print("バリデーションチェック")
        print("=" * 70)

        errors = []
        for animal in animals:
            try:
                # スキーマでバリデーション
                AnimalResponse.model_validate(animal)
            except Exception as e:
                errors.append({"id": animal.id, "name": animal.name, "error": str(e)})
                print(f"\n❌ エラー: 猫 ID {animal.id} ({animal.name})")
                print(f"   Status: {animal.status!r}")
                print(f"   Gender: {animal.gender!r}")
                print(f"   Coat color: {animal.coat_color!r}")
                print(f"   Tail length: {animal.tail_length!r}")
                print(f"   Protected at: {animal.protected_at!r}")
                print(f"   Location type: {animal.location_type!r}")
                print(f"   エラー詳細: {e}")

        if errors:
            print(f"\n\n⚠️  バリデーションエラー: {len(errors)}件")
            print("\n問題のある猫:")
            for error in errors:
                print(f"  - ID {error['id']}: {error['name']}")
        else:
            print("\n\n✅ 全ての猫データは正常です！")

        # 必須フィールドがNULLの猫を探す
        print("\n" + "=" * 70)
        print("NULL フィールドチェック")
        print("=" * 70)

        null_checks = {
            "status": db.query(Animal).filter(Animal.status.is_(None)).all(),
            "gender": db.query(Animal).filter(Animal.gender.is_(None)).all(),
            "coat_color": db.query(Animal).filter(Animal.coat_color.is_(None)).all(),
            "tail_length": db.query(Animal).filter(Animal.tail_length.is_(None)).all(),
            "protected_at": db.query(Animal)
            .filter(Animal.protected_at.is_(None))
            .all(),
            "location_type": db.query(Animal)
            .filter(Animal.location_type.is_(None))
            .all(),
        }

        has_null = False
        for field, animals_with_null in null_checks.items():
            if animals_with_null:
                has_null = True
                print(f"\n⚠️  {field} が NULL: {len(animals_with_null)}件")
                for animal in animals_with_null[:5]:  # 最大5件表示
                    print(f"   - ID {animal.id}: {animal.name}")

        if not has_null:
            print("\n✅ NULL フィールドはありません")

        # 不正なステータス値をチェック
        print("\n" + "=" * 70)
        print("不正なステータス値チェック")
        print("=" * 70)

        from app.utils.enums import AnimalStatus

        valid_statuses = {s.value for s in AnimalStatus}
        invalid_status_animals = [
            animal for animal in animals if animal.status not in valid_statuses
        ]

        if invalid_status_animals:
            print(f"\n⚠️  不正なステータス値: {len(invalid_status_animals)}件")
            for animal in invalid_status_animals:
                print(f"   - ID {animal.id} ({animal.name}): status='{animal.status}'")
                print(f"     有効な値: {', '.join(valid_statuses)}")
        else:
            print("\n✅ 全てのステータス値は正常です")

        print("\n" + "=" * 70)
        print("診断完了")
        print("=" * 70)

    finally:
        db.close()


if __name__ == "__main__":
    diagnose_animals()

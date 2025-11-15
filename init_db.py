"""データベース初期化とテストデータ作成"""

import sys
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy.orm import Session

from app.database import Base, engine
from app.models.animal import Animal
from app.models.volunteer import Volunteer

print("📦 データベーステーブルを作成中...")
Base.metadata.create_all(bind=engine)
print("✅ テーブル作成完了")

print("\n🐱 テストデータを作成中...")
with Session(engine) as db:
    # テスト猫
    animal = db.query(Animal).filter(Animal.id == 1).first()
    if not animal:
        animal = Animal(
            name="テスト猫",
            photo="default.jpg",
            pattern="キジトラ",
            tail_length="長い",
            age="成猫",
            gender="male",
            status="保護中",
        )
        db.add(animal)
        db.flush()  # IDを取得
        print(f"  ✅ テスト猫を作成（ID: {animal.id}）")
    else:
        print(f"  ℹ️  テスト猫は既に存在（ID: {animal.id}, 名前: {animal.name}）")

    # テストボランティア
    volunteer = db.query(Volunteer).filter(Volunteer.id == 1).first()
    if not volunteer:
        volunteer = Volunteer(
            name="テストボランティア",
            contact="test@example.com / 090-1234-5678",
            status="active",
        )
        db.add(volunteer)
        db.flush()  # IDを取得
        print(f"  ✅ テストボランティアを作成（ID: {volunteer.id}）")
    else:
        print(
            f"  ℹ️  テストボランティアは既に存在（ID: {volunteer.id}, 名前: {volunteer.name}）"
        )

    db.commit()

    print("\n" + "=" * 60)
    print("🎉 初期化完了！")
    print("=" * 60)
    print("\n📍 Public フォームにアクセス:")
    print(f"   http://localhost:8000/public/care-form?animal_id={animal.id}")
    print("\n💡 ヒント:")
    print("   - ボランティアで「テストボランティア」を選択")
    print("   - 時点、食欲、元気を選択して保存")
    print()

"""
テストデータ作成スクリプト

Public フォームの動作確認用にテストデータを作成します。
"""

from app.database import SessionLocal, engine
from app.models import Base
from app.models.animal import Animal
from app.models.volunteer import Volunteer


def create_test_data():
    """テストデータを作成"""
    # テーブルを作成
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        # 既存のテストデータを確認
        existing_animal = db.query(Animal).filter(Animal.name == "テスト猫").first()
        if existing_animal:
            print(f"✅ テスト猫は既に存在します（ID: {existing_animal.id}）")
            animal_id = existing_animal.id
        else:
            # テスト用の猫を作成
            animal = Animal(
                name="テスト猫",
                pattern="キジトラ",
                status="保護中",
                gender="オス",
                age_years=2,
                age_months=0,
                description="動作確認用のテスト猫です",
            )
            db.add(animal)
            db.flush()
            animal_id = animal.id
            print(f"✅ テスト猫を作成しました（ID: {animal_id}）")

        # 既存のテストボランティアを確認
        existing_volunteer = (
            db.query(Volunteer).filter(Volunteer.name == "テストボランティア").first()
        )
        if existing_volunteer:
            print(
                f"✅ テストボランティアは既に存在します（ID: {existing_volunteer.id}）"
            )
            volunteer_id = existing_volunteer.id
        else:
            # テスト用のボランティアを作成
            volunteer = Volunteer(
                name="テストボランティア",
                email="test@example.com",
                phone="090-1234-5678",
                status="active",
            )
            db.add(volunteer)
            db.flush()
            volunteer_id = volunteer.id
            print(f"✅ テストボランティアを作成しました（ID: {volunteer_id}）")

        db.commit()

        print("\n" + "=" * 50)
        print("🎉 テストデータの作成が完了しました！")
        print("=" * 50)
        print("\n📍 Public フォームにアクセス:")
        print(f"   http://localhost:8000/public/care-form?animal_id={animal_id}")
        print("\n💡 ボランティアID: {volunteer_id}")
        print("   フォームで「テストボランティア」を選択してください")
        print()

    except Exception as e:
        db.rollback()
        print(f"❌ エラーが発生しました: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    create_test_data()

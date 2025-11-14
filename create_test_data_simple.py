#!/usr/bin/env python3
"""簡易テストデータ作成スクリプト"""

import sys

sys.path.insert(0, ".")

from app.database import SessionLocal, engine
from app.models import Base
from app.models.animal import Animal
from app.models.volunteer import Volunteer

# テーブル作成
Base.metadata.create_all(bind=engine)

db = SessionLocal()

# テスト猫を作成
animal = db.query(Animal).filter(Animal.name == "テスト猫").first()
if not animal:
    animal = Animal(
        name="テスト猫",
        pattern="キジトラ",
        status="保護中",
        gender="オス",
        age_years=2,
        age_months=0,
    )
    db.add(animal)
    db.commit()
    db.refresh(animal)
    print(f"猫を作成: ID={animal.id}")
else:
    print(f"猫は既に存在: ID={animal.id}")

# テストボランティアを作成
volunteer = db.query(Volunteer).filter(Volunteer.name == "テストボランティア").first()
if not volunteer:
    volunteer = Volunteer(
        name="テストボランティア",
        email="test@example.com",
        phone="090-1234-5678",
        status="active",
    )
    db.add(volunteer)
    db.commit()
    db.refresh(volunteer)
    print(f"ボランティアを作成: ID={volunteer.id}")
else:
    print(f"ボランティアは既に存在: ID={volunteer.id}")

print(f"\nアクセスURL: http://localhost:8000/public/care-form?animal_id={animal.id}")

db.close()

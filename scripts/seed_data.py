#!/usr/bin/env python3
"""
開発環境用サンプルデータ作成スクリプト

管理者ユーザー、ボランティア、猫、世話記録のサンプルデータを作成します。

Usage:
    python scripts/seed_data.py

Context7参照:
- /sqlalchemy/alembic - データマイグレーションパターン
- /fastapi/fastapi - 初期化ベストプラクティス
"""

from __future__ import annotations

import sys
from datetime import date, timedelta
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy.orm import Session

from app.auth.password import hash_password
from app.database import SessionLocal
from app.models.animal import Animal
from app.models.care_log import CareLog
from app.models.user import User
from app.models.volunteer import Volunteer


def create_admin_user(db: Session) -> User:
    """管理者ユーザーを作成"""
    # 既存チェック
    existing = db.query(User).filter(User.email == "admin@example.com").first()
    if existing:
        print("✓ 管理者ユーザーは既に存在します")
        return existing

    admin = User(
        email="admin@example.com",
        name="管理者",
        password_hash=hash_password("admin123"),
        role="admin",
        is_active=True,
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    print("✓ 管理者ユーザーを作成しました (admin@example.com / admin123)")
    return admin


def create_volunteers(db: Session) -> list[Volunteer]:
    """ボランティアを作成"""
    volunteers_data = [
        {"name": "田中太郎", "contact": "090-1234-5678 / tanaka@example.com"},
        {"name": "佐藤花子", "contact": "090-2345-6789 / sato@example.com"},
        {"name": "鈴木一郎", "contact": "090-3456-7890 / suzuki@example.com"},
        {"name": "高橋美咲", "contact": "090-4567-8901 / takahashi@example.com"},
        {"name": "伊藤健太", "contact": "090-5678-9012 / ito@example.com"},
    ]

    volunteers: list[Volunteer] = []
    for data in volunteers_data:
        # 既存チェック
        existing = db.query(Volunteer).filter(Volunteer.name == data["name"]).first()
        if existing:
            volunteers.append(existing)
            continue

        volunteer = Volunteer(**data, status="active")
        db.add(volunteer)
        volunteers.append(volunteer)

    db.commit()
    print(f"✓ ボランティア {len(volunteers)} 人を作成しました")
    return volunteers


def create_animals(db: Session) -> list[Animal]:
    """猫を作成"""
    animals_data = [
        {
            "name": "たま",
            "photo": "/static/images/default.svg",
            "pattern": "キジトラ",
            "tail_length": "長い",
            "gender": "female",
            "age": "成猫",
            "status": "保護中",
            "protected_at": date.today() - timedelta(days=30),
            "features": "人懐っこい性格で、よく鳴きます",
            "rescue_source": "〇〇保健所",
            "breed": "雑種",
        },
        {
            "name": "ミケ",
            "photo": "/static/images/default.svg",
            "pattern": "三毛",
            "tail_length": "長い",
            "gender": "female",
            "age": "成猫",
            "status": "譲渡可能",
            "protected_at": date.today() - timedelta(days=60),
            "features": "おとなしい性格で、膝の上が好きです",
            "rescue_source": "△△動物愛護団体",
            "breed": "雑種",
        },
        {
            "name": "クロ",
            "photo": "/static/images/default.svg",
            "pattern": "黒猫",
            "tail_length": "長い",
            "gender": "male",
            "age": "子猫",
            "status": "保護中",
            "protected_at": date.today() - timedelta(days=15),
            "features": "元気いっぱいで遊ぶのが大好きです",
            "rescue_source": "個人保護",
            "breed": "雑種",
        },
        {
            "name": "シロ",
            "photo": "/static/images/default.svg",
            "pattern": "白猫",
            "tail_length": "長い",
            "gender": "female",
            "age": "成猫",
            "status": "治療中",
            "protected_at": date.today() - timedelta(days=45),
            "features": "静かな性格で、高い場所が好きです",
        },
        {
            "name": "トラ",
            "photo": "/static/images/default.svg",
            "pattern": "茶トラ",
            "tail_length": "長い",
            "gender": "male",
            "age": "成猫",
            "status": "譲渡可能",
            "protected_at": date.today() - timedelta(days=90),
            "features": "食いしん坊で、おもちゃで遊ぶのが好きです",
        },
        {
            "name": "ハチ",
            "photo": "/static/images/default.svg",
            "pattern": "サバトラ",
            "tail_length": "長い",
            "gender": "male",
            "age": "老猫",
            "status": "保護中",
            "protected_at": date.today() - timedelta(days=20),
            "features": "落ち着いた性格で、撫でられるのが好きです",
        },
        {
            "name": "モモ",
            "photo": "/static/images/default.svg",
            "pattern": "キジトラ",
            "tail_length": "長い",
            "gender": "female",
            "age": "子猫",
            "status": "譲渡可能",
            "protected_at": date.today() - timedelta(days=75),
            "features": "好奇心旺盛で、人の後をついて歩きます",
        },
        {
            "name": "ソラ",
            "photo": "/static/images/default.svg",
            "pattern": "グレー",
            "tail_length": "長い",
            "gender": "male",
            "age": "成猫",
            "status": "保護中",
            "protected_at": date.today() - timedelta(days=10),
            "features": "シャイな性格ですが、慣れると甘えん坊です",
        },
    ]

    animals: list[Animal] = []
    for data in animals_data:
        # 既存チェック
        existing = db.query(Animal).filter(Animal.name == data["name"]).first()
        if existing:
            animals.append(existing)
            continue

        animal = Animal(**data)
        db.add(animal)
        animals.append(animal)

    db.commit()
    print(f"✓ 猫 {len(animals)} 匹を作成しました")
    return animals


def create_care_logs(
    db: Session, animals: list[Animal], volunteers: list[Volunteer]
) -> None:
    """世話記録を作成"""
    if not animals or not volunteers:
        print("⚠ 猫またはボランティアが存在しないため、世話記録をスキップします")
        return

    # 過去7日間の記録を作成
    today = date.today()
    time_slots = ["morning", "noon", "evening"]

    count = 0
    for days_ago in range(7):
        log_date = today - timedelta(days=days_ago)

        for animal in animals[:5]:  # 最初の5匹のみ
            for time_slot in time_slots:
                # 既存チェック
                existing = (
                    db.query(CareLog)
                    .filter(
                        CareLog.animal_id == animal.id,
                        CareLog.log_date == log_date,
                        CareLog.time_slot == time_slot,
                    )
                    .first()
                )
                if existing:
                    continue

                # ランダムにボランティアを選択
                volunteer = volunteers[count % len(volunteers)]

                care_log = CareLog(
                    animal_id=animal.id,
                    recorder_id=volunteer.id,
                    recorder_name=volunteer.name,
                    log_date=log_date,
                    time_slot=time_slot,
                    appetite=4 if days_ago < 3 else 5,
                    energy=4 if days_ago < 3 else 5,
                    urination=True,
                    cleaning=True,
                    memo=f"{time_slot}の世話記録" if days_ago == 0 else None,
                )
                db.add(care_log)
                count += 1

    db.commit()
    print(f"✓ 世話記録 {count} 件を作成しました")


def main() -> None:
    """メイン処理"""
    print("=" * 60)
    print("🐱 NecoKeeper - サンプルデータ作成スクリプト")
    print("=" * 60)
    print()

    db = SessionLocal()
    try:
        # 1. 管理者ユーザー作成
        print("[1/4] 管理者ユーザーを作成中...")
        admin = create_admin_user(db)

        # 2. ボランティア作成
        print("[2/4] ボランティアを作成中...")
        volunteers = create_volunteers(db)

        # 3. 猫作成
        print("[3/4] 猫を作成中...")
        animals = create_animals(db)

        # 4. 世話記録作成
        print("[4/4] 世話記録を作成中...")
        create_care_logs(db, animals, volunteers)

        print()
        print("=" * 60)
        print("✅ サンプルデータの作成が完了しました！")
        print("=" * 60)
        print()
        print("📝 管理画面ログイン情報:")
        print("   URL: http://localhost:8000/admin/login")
        print(f"   メール: {admin.email}")
        print("   パスワード: admin123")
        print()

    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()

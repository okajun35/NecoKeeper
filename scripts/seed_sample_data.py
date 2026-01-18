"""
サンプルデータ投入スクリプト

開発・テスト用の充実したサンプルデータを投入します。
"""

from __future__ import annotations

import sys
from datetime import date, datetime, timedelta
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy.orm import Session

from app.auth.password import hash_password
from app.database import SessionLocal, init_db
from app.models.animal import Animal
from app.models.care_log import CareLog
from app.models.status_history import StatusHistory
from app.models.user import User
from app.models.volunteer import Volunteer


def clear_all_data(db: Session) -> None:
    """既存データをすべて削除"""
    print("🗑️  既存データを削除中...")
    db.query(CareLog).delete()
    db.query(StatusHistory).delete()
    db.query(Animal).delete()
    db.query(Volunteer).delete()
    db.query(User).delete()
    db.commit()
    print("✅ 既存データを削除しました")


def seed_users(db: Session) -> dict[str, User]:
    """ユーザーデータを投入"""
    print("👤 ユーザーデータを投入中...")

    users_data = [
        {
            "email": "admin@example.com",
            "password": "admin123",
            "name": "管理者",
            "role": "admin",
        },
        {
            "email": "admin2@example.com",
            "password": "admin123",
            "name": "管理者 太郎",
            "role": "admin",
        },
        {
            "email": "vet@example.com",
            "password": "vet123",
            "name": "獣医師 花子",
            "role": "vet",
        },
    ]

    users = {}
    for user_data in users_data:
        password = user_data.pop("password")
        user = User(
            **user_data,
            password_hash=hash_password(password),
        )
        db.add(user)
        if user_data["role"] not in users:
            users[user_data["role"]] = user

    db.commit()
    print(f"✅ {len(users_data)}人のユーザーを作成しました")
    return users


def seed_volunteers(db: Session) -> list[Volunteer]:
    """ボランティアデータを投入"""
    print("🙋 ボランティアデータを投入中...")

    volunteers_data = [
        {"name": "ボランティア A", "contact": "090-1234-5678"},
        {"name": "ボランティア B", "contact": "080-9876-5432"},
        {"name": "ボランティア C", "contact": "070-1111-2222"},
        {"name": "ボランティア D", "contact": "090-3333-4444"},
    ]

    volunteers = []
    for vol_data in volunteers_data:
        volunteer = Volunteer(**vol_data)
        db.add(volunteer)
        volunteers.append(volunteer)

    db.commit()
    print(f"✅ {len(volunteers)}人のボランティアを作成しました")
    return volunteers


def seed_animals(db: Session, admin_user: User) -> list[Animal]:
    """猫データを投入"""
    print("🐱 猫データを投入中...")

    animals_data = [
        {
            "name": "たま",
            "photo": "/static/images/animals/tama.jpg",
            "pattern": "キジトラ",
            "tail_length": "長い",
            "collar": "赤い首輪",
            "age": "成猫",
            "gender": "female",
            "ear_cut": False,
            "features": "人懐っこい性格。おもちゃで遊ぶのが大好き。",
            "rescue_source": "〇〇保健所",
            "breed": "雑種",
            "status": "譲渡可能",
            "protected_at": date.today() - timedelta(days=30),
        },
        {
            "name": "ミケ",
            "photo": "/static/images/animals/mike.jpg",
            "pattern": "三毛",
            "tail_length": "短い",
            "collar": None,
            "age": "成猫",
            "gender": "female",
            "ear_cut": True,
            "features": "少し警戒心が強いが、慣れると甘えん坊。",
            "rescue_source": "△△動物愛護団体",
            "breed": "日本猫",
            "status": "保護中",
            "protected_at": date.today() - timedelta(days=15),
        },
        {
            "name": "クロ",
            "photo": "/static/images/animals/kuro.jpg",
            "pattern": "黒猫",
            "tail_length": "長い",
            "collar": "青い首輪",
            "age": "成猫",
            "gender": "male",
            "ear_cut": False,
            "features": "とても元気で活発。高いところが好き。",
            "rescue_source": "個人保護",
            "breed": "雑種",
            "status": "治療中",
            "protected_at": date.today() - timedelta(days=7),
        },
        {
            "name": "チビ",
            "photo": "/static/images/animals/chibi.jpg",
            "pattern": "茶トラ",
            "tail_length": "長い",
            "collar": None,
            "age": "子猫",
            "gender": "male",
            "ear_cut": False,
            "features": "生後3ヶ月程度。ミルクから離乳食に移行中。",
            "status": "保護中",
            "protected_at": date.today() - timedelta(days=5),
        },
        {
            "name": "シロ",
            "photo": "/static/images/animals/shiro.jpg",
            "pattern": "白猫",
            "tail_length": "短い",
            "collar": None,
            "age": "老猫",
            "gender": "male",
            "ear_cut": True,
            "features": "推定10歳以上。穏やかな性格で静かな環境を好む。",
            "status": "譲渡可能",
            "protected_at": date.today() - timedelta(days=60),
        },
        {
            "name": "ハチ",
            "photo": "/static/images/animals/hachi.jpg",
            "pattern": "サバトラ",
            "tail_length": "長い",
            "collar": "黄色い首輪",
            "age": "成猫",
            "gender": "male",
            "ear_cut": False,
            "features": "とても賢く、名前を呼ぶと来る。",
            "status": "譲渡済み",
            "protected_at": date.today() - timedelta(days=90),
        },
        {
            "name": None,
            "photo": "/static/images/animals/unknown1.jpg",
            "pattern": "キジトラ白",
            "tail_length": "長い",
            "collar": None,
            "age": "成猫",
            "gender": "unknown",
            "ear_cut": False,
            "features": "警戒心が強く、まだ人に慣れていない。",
            "status": "保護中",
            "protected_at": date.today() - timedelta(days=3),
        },
        {
            "name": "モモ",
            "photo": "/static/images/animals/momo.jpg",
            "pattern": "茶白",
            "tail_length": "長い",
            "collar": "ピンクの首輪",
            "age": "子猫",
            "gender": "female",
            "ear_cut": False,
            "features": "生後2ヶ月。兄弟猫と一緒に保護。",
            "status": "保護中",
            "protected_at": date.today() - timedelta(days=10),
        },
        {
            "name": "ソラ",
            "photo": "/static/images/animals/sora.jpg",
            "pattern": "グレー",
            "tail_length": "長い",
            "collar": None,
            "age": "成猫",
            "gender": "male",
            "ear_cut": True,
            "features": "ロシアンブルー風の美しい毛並み。",
            "status": "譲渡可能",
            "protected_at": date.today() - timedelta(days=45),
        },
        {
            "name": "ナナ",
            "photo": "/static/images/animals/nana.jpg",
            "pattern": "サビ猫",
            "tail_length": "短い",
            "collar": None,
            "age": "成猫",
            "gender": "female",
            "ear_cut": False,
            "features": "独特な柄が魅力的。マイペースな性格。",
            "status": "保護中",
            "protected_at": date.today() - timedelta(days=20),
        },
    ]

    animals = []
    for animal_data in animals_data:
        animal = Animal(**animal_data)
        db.add(animal)
        db.flush()  # IDを取得

        # ステータス履歴を作成
        status_history = StatusHistory(
            animal_id=animal.id,
            old_status=None,
            new_status=animal.status,
            reason="初期登録",
            changed_by=admin_user.id,
            changed_at=datetime.now()
            - timedelta(days=(date.today() - animal.protected_at).days),
        )
        db.add(status_history)

        animals.append(animal)

    db.commit()
    print(f"✅ {len(animals)}匹の猫を作成しました")
    return animals


def seed_care_logs(
    db: Session,
    animals: list[Animal],
    volunteers: list[Volunteer],
) -> None:
    """世話記録データを投入"""
    print("📝 世話記録データを投入中...")

    time_slots = ["morning", "noon", "evening"]
    care_logs_count = 0

    # 各猫について過去7日分の記録を作成
    for animal in animals:
        # 譲渡済みの猫は記録を少なくする
        days_back = 3 if animal.status == "譲渡済み" else 7

        for days_ago in range(days_back):
            log_date = date.today() - timedelta(days=days_ago)

            for time_slot in time_slots:
                # ランダムに記録を作成（すべての時点で記録があるわけではない）
                if days_ago > 0 and (days_ago + hash(time_slot)) % 3 == 0:
                    continue

                volunteer = volunteers[care_logs_count % len(volunteers)]

                # 食欲と元気は日によって変動
                appetite = 3 + (days_ago % 3) - 1  # 2〜4
                energy = 3 + ((days_ago + 1) % 3) - 1  # 2〜4

                # 治療中の猫は食欲・元気が低め
                if animal.status == "治療中":
                    appetite = max(1, appetite - 1)
                    energy = max(1, energy - 1)

                care_log = CareLog(
                    animal_id=animal.id,
                    recorder_id=volunteer.id,
                    recorder_name=volunteer.name,
                    log_date=log_date,
                    time_slot=time_slot,
                    appetite=appetite,
                    energy=energy,
                    urination=time_slot in ["morning", "evening"],
                    cleaning=time_slot == "morning",
                    memo=f"{time_slot}の世話記録" if days_ago == 0 else None,
                    ip_address="192.168.1.100",
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                    device_tag=f"tablet-{volunteer.id}",
                    from_paper=False,
                    created_at=datetime.combine(log_date, datetime.min.time())
                    + timedelta(
                        hours=8
                        if time_slot == "morning"
                        else (12 if time_slot == "noon" else 18)
                    ),
                )
                db.add(care_log)
                care_logs_count += 1

    db.commit()
    print(f"✅ {care_logs_count}件の世話記録を作成しました")


def main() -> None:
    """メイン処理"""
    print("=" * 60)
    print("🌱 サンプルデータ投入スクリプト")
    print("=" * 60)

    # データベース初期化
    print("\n📦 データベースを初期化中...")
    init_db()

    # セッション作成
    db = SessionLocal()

    try:
        # 既存データを削除
        clear_all_data(db)

        # データ投入
        users = seed_users(db)
        volunteers = seed_volunteers(db)
        animals = seed_animals(db, users["admin"])
        seed_care_logs(db, animals, volunteers)

        print("\n" + "=" * 60)
        print("✅ サンプルデータの投入が完了しました！")
        print("=" * 60)
        print("\n📊 投入されたデータ:")
        print("  - ユーザー: 3人")
        print(f"  - ボランティア: {len(volunteers)}人")
        print(f"  - 猫: {len(animals)}匹")
        print(f"  - 世話記録: {db.query(CareLog).count()}件")
        print(f"  - ステータス履歴: {db.query(StatusHistory).count()}件")

        print("\n🔑 ログイン情報:")
        print("  - 開発用管理者: admin@example.com / admin123")
        print("  - 管理者: admin2@example.com / admin123")
        print("  - 獣医師: vet@example.com / vet123")

    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()

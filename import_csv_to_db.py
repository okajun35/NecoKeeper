"""
CSVファイルから猫データをDBにインポートするスクリプト

既存のAnimalデータを削除し、CSVから新規登録します。
"""

import csv
from datetime import date, datetime
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.animal import Animal
from app.models.care_log import CareLog

# 直接DBパスを指定
DB_PATH = "data/necokeeper.db"
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def parse_date(date_str: str) -> date | None:
    """日付文字列をパース"""
    if not date_str:
        return None
    # 複数のフォーマットに対応
    for fmt in ["%Y/%m/%d", "%Y-%m-%d", "%Y/%-m/%-d"]:
        try:
            return datetime.strptime(date_str.strip(), fmt).date()
        except ValueError:
            continue
    # 手動パース（2025/7/31 のような形式）
    try:
        parts = date_str.strip().split("/")
        if len(parts) == 3:
            return datetime(int(parts[0]), int(parts[1]), int(parts[2])).date()
    except (ValueError, IndexError):
        # 手動パースに失敗した場合は無効な日付として扱う
        return None
    return None


def gender_to_db(gender_str: str) -> str:
    """性別をDB形式に変換"""
    mapping = {
        "オス": "male",
        "メス": "female",
        "不明": "unknown",
    }
    return mapping.get(gender_str, "unknown")


def age_to_db(age_years: str, age_months: str) -> str:
    """年齢をDB形式に変換"""
    try:
        years = int(age_years) if age_years else 0
        months = int(age_months) if age_months else 0
    except ValueError:
        return "不明"

    if years >= 7:
        return "老猫"
    elif years >= 1 or months >= 6:
        return "成猫"
    else:
        return "子猫"


def main():
    db = SessionLocal()

    try:
        # 1. 既存データを削除（CareLogも連鎖削除される）
        existing_count = db.query(Animal).count()
        print(f"🗑️  既存の猫データを削除します: {existing_count}件")

        # CareLogを先に削除
        care_log_count = db.query(CareLog).count()
        db.query(CareLog).delete()
        print(f"   - CareLog削除: {care_log_count}件")

        # Animalを削除
        db.query(Animal).delete()
        db.commit()
        print(f"   - Animal削除: {existing_count}件")

        # 2. CSVを読み込み
        csv_path = Path("tmp/健康管理 - プロフィール登録.csv")
        animals_to_add = []

        with csv_path.open(encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # 空行をスキップ
                if not row.get("ID") or not row.get("猫の名前"):
                    continue

                name = row["猫の名前"].strip()
                gender = gender_to_db(row.get("性別", ""))
                age = age_to_db(
                    row.get("保護時の年齢", ""), row.get("保護時の月齢", "")
                )
                protected_at = parse_date(
                    row.get("保護日 ", "") or row.get("保護日", "")
                )
                features = row.get("特徴・性格", "").strip() or None
                rescue_from = row.get("レスキュー元 ", "") or row.get(
                    "レスキュー元", ""
                )

                # 特徴にレスキュー元を追加
                if rescue_from and rescue_from.strip():
                    if features:
                        features = f"{features}、レスキュー元: {rescue_from.strip()}"
                    else:
                        features = f"レスキュー元: {rescue_from.strip()}"

                # 柄・パターンを特徴から推測
                pattern = "Mix"
                features_lower = (features or "").lower()
                if "キジトラ" in (features or "") or "キジ" in (features or ""):
                    pattern = "キジトラ"
                elif "黒猫" in (features or "") or "黒" in (features or ""):
                    pattern = "黒猫"
                elif "白猫" in (features or "") or features_lower.startswith("白"):
                    pattern = "白猫"
                elif "茶トラ" in (features or "") or "茶白" in (features or ""):
                    pattern = "茶トラ"
                elif "サビ" in (features or ""):
                    pattern = "サビ"
                elif "パステル" in (features or ""):
                    pattern = "パステルキジ"

                animal = Animal(
                    name=name,
                    pattern=pattern,
                    tail_length="不明",  # CSVにないのでデフォルト
                    age=age,
                    gender=gender,
                    features=features,
                    status="保護中",
                    protected_at=protected_at,
                    ear_cut=False,
                )
                animals_to_add.append(animal)
                print(f"   📝 {name} ({gender}, {age}, {pattern})")

        # 3. DBに追加
        db.add_all(animals_to_add)
        db.commit()

        print(f"\n✅ {len(animals_to_add)}匹の猫を登録しました")

        # 4. 確認
        final_count = db.query(Animal).count()
        print(f"📊 DB内の猫の数: {final_count}匹")

    except Exception as e:
        db.rollback()
        print(f"❌ エラー: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
正規シードデータ投入スクリプト

Alembicでheadまで適用済みのDBに対して、モデル準拠のサンプルデータを投入する。
"""

from __future__ import annotations

import sys
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy.orm import Session

from app.auth.password import hash_password
from app.database import SessionLocal
from app.models.adoption_record import AdoptionRecord
from app.models.animal import Animal
from app.models.animal_image import AnimalImage
from app.models.applicant import Applicant, ApplicantHouseholdMember, ApplicantPet
from app.models.care_log import CareLog
from app.models.medical_action import MedicalAction
from app.models.medical_record import MedicalRecord
from app.models.status_history import StatusHistory
from app.models.user import User
from app.models.volunteer import Volunteer
from app.utils.timezone import get_jst_date, get_jst_now


def get_or_create_user(
    db: Session,
    *,
    email: str,
    name: str,
    role: str,
    password: str,
) -> User:
    """ユーザーを作成（存在すれば既存を返す）"""
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        return existing

    user = User(
        email=email,
        name=name,
        role=role,
        is_active=True,
        password_hash=hash_password(password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_or_create_volunteer(db: Session, *, name: str, contact: str) -> Volunteer:
    """ボランティアを作成（存在すれば既存を返す）"""
    existing = db.query(Volunteer).filter(Volunteer.name == name).first()
    if existing:
        return existing

    volunteer = Volunteer(name=name, contact=contact, status="active")
    db.add(volunteer)
    db.commit()
    db.refresh(volunteer)
    return volunteer


def get_or_create_animal(db: Session, data: dict) -> Animal:
    """猫を作成（存在すれば既存を返す）"""
    existing = (
        db.query(Animal)
        .filter(
            Animal.name == data["name"],
            Animal.pattern == data["pattern"],
            Animal.protected_at == data["protected_at"],
        )
        .first()
    )
    if existing:
        return existing

    animal = Animal(**data)
    db.add(animal)
    db.commit()
    db.refresh(animal)
    return animal


def ensure_initial_status_history(
    db: Session, *, animal: Animal, changed_by: int | None
) -> StatusHistory:
    """初期ステータス履歴を作成"""
    existing = (
        db.query(StatusHistory)
        .filter(
            StatusHistory.animal_id == animal.id,
            StatusHistory.old_status.is_(None),
            StatusHistory.new_status == animal.status,
        )
        .first()
    )
    if existing:
        return existing

    history = StatusHistory(
        animal_id=animal.id,
        old_status=None,
        new_status=animal.status,
        reason="seed",
        changed_by=changed_by,
        changed_at=get_jst_now(),
    )
    db.add(history)
    db.commit()
    db.refresh(history)
    return history


def get_or_create_medical_action(db: Session, data: dict) -> MedicalAction:
    """診療行為マスターを作成"""
    existing = (
        db.query(MedicalAction)
        .filter(
            MedicalAction.name == data["name"],
            MedicalAction.valid_from == data["valid_from"],
        )
        .first()
    )
    if existing:
        return existing

    action = MedicalAction(**data)
    db.add(action)
    db.commit()
    db.refresh(action)
    return action


def upsert_applicant_extended(
    db: Session,
    *,
    data: dict,
    household_members: list[dict],
    pets: list[dict],
) -> Applicant:
    """里親希望者（拡張項目）を作成/更新"""
    existing = db.query(Applicant).filter(Applicant.name == data["name"]).first()
    if existing:
        for key, value in data.items():
            if value is None:
                continue
            current = getattr(existing, key, None)
            if current in (None, ""):
                setattr(existing, key, value)
        db.commit()
        db.refresh(existing)
        applicant = existing
    else:
        applicant = Applicant(**data)
        db.add(applicant)
        db.commit()
        db.refresh(applicant)

    if not applicant.household_members and household_members:
        for member_data in household_members:
            db.add(ApplicantHouseholdMember(applicant_id=applicant.id, **member_data))
        db.commit()

    if not applicant.pets and pets:
        for pet_data in pets:
            db.add(ApplicantPet(applicant_id=applicant.id, **pet_data))
        db.commit()

    return applicant


def seed_users(db: Session) -> dict[str, User]:
    """ユーザー作成"""
    return {
        "admin": get_or_create_user(
            db,
            email="admin@example.com",
            name="管理者",
            role="admin",
            password="Password123",
        ),
        "staff": get_or_create_user(
            db,
            email="staff@example.com",
            name="スタッフ",
            role="staff",
            password="Password123",
        ),
        "vet": get_or_create_user(
            db,
            email="vet@example.com",
            name="獣医師",
            role="vet",
            password="Password123",
        ),
    }


def seed_volunteers(db: Session) -> list[Volunteer]:
    """ボランティア作成"""
    volunteers_data = [
        {"name": "田中太郎", "contact": "090-1234-5678 / tanaka@example.com"},
        {"name": "佐藤花子", "contact": "090-2345-6789 / sato@example.com"},
        {"name": "鈴木一郎", "contact": "090-3456-7890 / suzuki@example.com"},
        {"name": "高橋美咲", "contact": "090-4567-8901 / takahashi@example.com"},
        {"name": "伊藤健太", "contact": "090-5678-9012 / ito@example.com"},
    ]
    return [get_or_create_volunteer(db, **data) for data in volunteers_data]


def seed_animals(db: Session) -> list[Animal]:
    """猫作成"""
    today = get_jst_date()
    animals_data = [
        {
            "name": "たま",
            "photo": None,
            "pattern": "キジトラ",
            "tail_length": "長い",
            "collar": "赤い首輪",
            "age_months": 24,
            "age_is_estimated": False,
            "gender": "female",
            "ear_cut": False,
            "features": "人懐っこい性格。",
            "status": "譲渡可能",
            "protected_at": today - timedelta(days=30),
        },
        {
            "name": "ミケ",
            "photo": None,
            "pattern": "三毛",
            "tail_length": "短い",
            "collar": None,
            "age_months": 36,
            "age_is_estimated": False,
            "gender": "female",
            "ear_cut": True,
            "features": "少し警戒心が強い。",
            "status": "保護中",
            "protected_at": today - timedelta(days=15),
        },
        {
            "name": "クロ",
            "photo": None,
            "pattern": "黒猫",
            "tail_length": "長い",
            "collar": "青い首輪",
            "age_months": 18,
            "age_is_estimated": True,
            "gender": "male",
            "ear_cut": False,
            "features": "元気で活発。",
            "status": "治療中",
            "protected_at": today - timedelta(days=7),
        },
        {
            "name": "チビ",
            "photo": None,
            "pattern": "茶トラ",
            "tail_length": "長い",
            "collar": None,
            "age_months": 4,
            "age_is_estimated": False,
            "gender": "male",
            "ear_cut": False,
            "features": "子猫。",
            "status": "保護中",
            "protected_at": today - timedelta(days=5),
        },
        {
            "name": "シロ",
            "photo": None,
            "pattern": "白猫",
            "tail_length": "短い",
            "collar": None,
            "age_months": 120,
            "age_is_estimated": True,
            "gender": "male",
            "ear_cut": True,
            "features": "穏やかな性格。",
            "status": "譲渡可能",
            "protected_at": today - timedelta(days=60),
        },
        {
            "name": "ハチ",
            "photo": None,
            "pattern": "サバトラ",
            "tail_length": "長い",
            "collar": "黄色い首輪",
            "age_months": 30,
            "age_is_estimated": False,
            "gender": "male",
            "ear_cut": False,
            "features": "賢い性格。",
            "status": "譲渡済み",
            "protected_at": today - timedelta(days=90),
        },
        {
            "name": "モモ",
            "photo": None,
            "pattern": "茶白",
            "tail_length": "長い",
            "collar": "ピンクの首輪",
            "age_months": 3,
            "age_is_estimated": False,
            "gender": "female",
            "ear_cut": False,
            "features": "好奇心旺盛。",
            "status": "保護中",
            "protected_at": today - timedelta(days=10),
        },
        {
            "name": "ソラ",
            "photo": None,
            "pattern": "グレー",
            "tail_length": "長い",
            "collar": None,
            "age_months": 28,
            "age_is_estimated": True,
            "gender": "male",
            "ear_cut": True,
            "features": "ロシアンブルー風。",
            "status": "譲渡可能",
            "protected_at": today - timedelta(days=45),
        },
        {
            "name": "ナナ",
            "photo": None,
            "pattern": "サビ猫",
            "tail_length": "短い",
            "collar": None,
            "age_months": 22,
            "age_is_estimated": False,
            "gender": "female",
            "ear_cut": False,
            "features": "マイペースな性格。",
            "status": "保護中",
            "protected_at": today - timedelta(days=20),
        },
        {
            "name": "ココ",
            "photo": None,
            "pattern": "黒白",
            "tail_length": "短い",
            "collar": None,
            "age_months": None,
            "age_is_estimated": True,
            "gender": "unknown",
            "ear_cut": False,
            "features": "まだ人に慣れていない。",
            "status": "保護中",
            "protected_at": today - timedelta(days=3),
        },
    ]
    return [get_or_create_animal(db, data) for data in animals_data]


def seed_status_history(db: Session, animals: list[Animal], admin_user: User) -> None:
    """初期ステータス履歴作成"""
    for animal in animals:
        ensure_initial_status_history(db, animal=animal, changed_by=admin_user.id)


def seed_medical_actions(db: Session, admin_user: User) -> list[MedicalAction]:
    """診療行為マスター作成"""
    valid_from = date(2025, 1, 1)
    actions_data = [
        {
            "name": "FVRCPワクチン",
            "valid_from": valid_from,
            "valid_to": None,
            "cost_price": Decimal("1200.00"),
            "selling_price": Decimal("2500.00"),
            "procedure_fee": Decimal("1500.00"),
            "currency": "JPY",
            "unit": "dose",
            "last_updated_by": admin_user.id,
        },
        {
            "name": "狂犬病ワクチン",
            "valid_from": valid_from,
            "valid_to": None,
            "cost_price": Decimal("800.00"),
            "selling_price": Decimal("2000.00"),
            "procedure_fee": Decimal("1500.00"),
            "currency": "JPY",
            "unit": "dose",
            "last_updated_by": admin_user.id,
        },
        {
            "name": "駆虫薬（内服）",
            "valid_from": valid_from,
            "valid_to": None,
            "cost_price": Decimal("500.00"),
            "selling_price": Decimal("1500.00"),
            "procedure_fee": Decimal("1000.00"),
            "currency": "JPY",
            "unit": "tablet",
            "last_updated_by": admin_user.id,
        },
        {
            "name": "ノミダニ治療",
            "valid_from": valid_from,
            "valid_to": None,
            "cost_price": Decimal("1000.00"),
            "selling_price": Decimal("2500.00"),
            "procedure_fee": Decimal("1000.00"),
            "currency": "JPY",
            "unit": "application",
            "last_updated_by": admin_user.id,
        },
        {
            "name": "抗生物質（アモキシシリン）",
            "valid_from": valid_from,
            "valid_to": None,
            "cost_price": Decimal("300.00"),
            "selling_price": Decimal("1000.00"),
            "procedure_fee": Decimal("500.00"),
            "currency": "JPY",
            "unit": "ml",
            "last_updated_by": admin_user.id,
        },
        {
            "name": "消炎鎮痛剤",
            "valid_from": valid_from,
            "valid_to": None,
            "cost_price": Decimal("400.00"),
            "selling_price": Decimal("1200.00"),
            "procedure_fee": Decimal("500.00"),
            "currency": "JPY",
            "unit": "tablet",
            "last_updated_by": admin_user.id,
        },
        {
            "name": "血液検査（基本）",
            "valid_from": valid_from,
            "valid_to": None,
            "cost_price": Decimal("2000.00"),
            "selling_price": Decimal("5000.00"),
            "procedure_fee": Decimal("2000.00"),
            "currency": "JPY",
            "unit": "test",
            "last_updated_by": admin_user.id,
        },
        {
            "name": "避妊去勢手術",
            "valid_from": valid_from,
            "valid_to": None,
            "cost_price": Decimal("5000.00"),
            "selling_price": Decimal("12000.00"),
            "procedure_fee": Decimal("8000.00"),
            "currency": "JPY",
            "unit": "procedure",
            "last_updated_by": admin_user.id,
        },
    ]
    return [get_or_create_medical_action(db, data) for data in actions_data]


def seed_medical_records(
    db: Session,
    animals: list[Animal],
    vet_user: User,
    actions: list[MedicalAction],
) -> None:
    """診療記録作成"""
    records_data = []
    base_date = date(2025, 12, 1)
    for i, animal in enumerate(animals[:5]):
        records_data.append(
            {
                "animal_id": animal.id,
                "vet_id": vet_user.id,
                "date": base_date - timedelta(days=i * 5),
                "time_slot": "morning",
                "weight": Decimal("3.5") + Decimal(str(i)) * Decimal("0.2"),
                "temperature": Decimal("38.5"),
                "symptoms": "定期健診",
                "medical_action_id": actions[i % len(actions)].id,
                "dosage": 1,
                "other": None,
                "comment": "特記事項なし",
                "last_updated_by": vet_user.id,
            }
        )

    for i, animal in enumerate(animals[5:10]):
        records_data.append(
            {
                "animal_id": animal.id,
                "vet_id": vet_user.id,
                "date": base_date - timedelta(days=2 + i * 4),
                "time_slot": "afternoon",
                "weight": Decimal("4.0") + Decimal(str(i)) * Decimal("0.2"),
                "temperature": Decimal("38.3"),
                "symptoms": "軽度の経過観察",
                "medical_action_id": actions[(i + 2) % len(actions)].id,
                "dosage": 1,
                "other": None,
                "comment": "様子見",
                "last_updated_by": vet_user.id,
            }
        )

    for data in records_data:
        exists = (
            db.query(MedicalRecord)
            .filter(
                MedicalRecord.animal_id == data["animal_id"],
                MedicalRecord.date == data["date"],
                MedicalRecord.time_slot == data["time_slot"],
            )
            .first()
        )
        if exists:
            continue

        record = MedicalRecord(**data)
        db.add(record)

    db.commit()


def seed_applicants(db: Session) -> list[Applicant]:
    """里親希望者作成"""
    applicants_payload = [
        {
            "data": {
                "name_kana": "ヤマダタロウ",
                "name": "山田太郎",
                "age": 35,
                "phone": "09012345678",
                "contact_type": "line",
                "contact_line_id": "yamada_taro",
                "contact_email": None,
                "contact": "yamada_taro",
                "postal_code": "1600022",
                "address1": "東京都新宿区新宿1-2-3",
                "address2": "サンプルマンション101",
                "occupation": "company_employee",
                "occupation_other": None,
                "desired_cat_alias": "未定",
                "emergency_relation": "parents",
                "emergency_relation_other": None,
                "emergency_name": "山田花子",
                "emergency_phone": "09098765432",
                "family_intent": "all_positive",
                "pet_permission": "allowed",
                "pet_limit_type": "limited",
                "pet_limit_count": 2,
                "housing_type": "apartment",
                "housing_ownership": "rented",
                "relocation_plan": "none",
                "relocation_time_note": None,
                "relocation_cat_plan": None,
                "allergy_status": "none",
                "smoker_in_household": "no",
                "monthly_budget_yen": 15000,
                "alone_time_status": "sometimes",
                "alone_time_weekly_days": 2,
                "alone_time_hours": 6.0,
                "has_existing_cat": "no",
                "has_other_pets": "no",
                "address": "東京都新宿区",
                "family": "夫婦2人",
                "environment": "マンション",
                "conditions": "成猫希望",
            },
            "household_members": [
                {"relation": "wife", "relation_other": None, "age": 33},
            ],
            "pets": [],
        },
        {
            "data": {
                "name_kana": "ササキハナコ",
                "name": "佐々木花子",
                "age": 29,
                "phone": "08011112222",
                "contact_type": "email",
                "contact_line_id": None,
                "contact_email": "sasaki@example.com",
                "contact": "sasaki@example.com",
                "postal_code": "2200012",
                "address1": "神奈川県横浜市西区みなとみらい1-2-3",
                "address2": "サンプルアパート202",
                "occupation": "other",
                "occupation_other": "フリーランス",
                "desired_cat_alias": "ミケ",
                "emergency_relation": "other",
                "emergency_relation_other": "友人",
                "emergency_name": "田中麻美",
                "emergency_phone": "08022223333",
                "family_intent": "single_household",
                "pet_permission": "tolerated",
                "pet_limit_type": "unknown",
                "pet_limit_count": None,
                "housing_type": "apartment",
                "housing_ownership": "rented",
                "relocation_plan": "planned",
                "relocation_time_note": "1年以内",
                "relocation_cat_plan": "転居先でも飼育継続",
                "allergy_status": "exists",
                "smoker_in_household": "yes",
                "monthly_budget_yen": 12000,
                "alone_time_status": "regular",
                "alone_time_weekly_days": 4,
                "alone_time_hours": 8.0,
                "has_existing_cat": "yes",
                "has_other_pets": "yes",
                "address": "神奈川県横浜市",
                "family": "単身",
                "environment": "アパート",
                "conditions": "子猫希望",
            },
            "household_members": [],
            "pets": [
                {
                    "pet_category": "cat",
                    "count": 1,
                    "breed_or_type": "雑種",
                    "age_note": "3歳",
                },
                {
                    "pet_category": "other",
                    "count": 1,
                    "breed_or_type": "小型犬",
                    "age_note": "5歳",
                },
            ],
        },
        {
            "data": {
                "name_kana": "タカハシイチロウ",
                "name": "高橋一郎",
                "age": 42,
                "phone": "09033334444",
                "contact_type": "email",
                "contact_line_id": None,
                "contact_email": "takahashi@example.com",
                "contact": "takahashi@example.com",
                "postal_code": "3300005",
                "address1": "埼玉県さいたま市中央区本町1-2-3",
                "address2": "",
                "occupation": "public_servant",
                "occupation_other": None,
                "desired_cat_alias": "未定",
                "emergency_relation": "siblings",
                "emergency_relation_other": None,
                "emergency_name": "高橋次郎",
                "emergency_phone": "09055556666",
                "family_intent": "all_positive",
                "pet_permission": "allowed",
                "pet_limit_type": "unlimited",
                "pet_limit_count": None,
                "housing_type": "house",
                "housing_ownership": "owned",
                "relocation_plan": "none",
                "relocation_time_note": None,
                "relocation_cat_plan": None,
                "allergy_status": "unknown",
                "smoker_in_household": "no",
                "monthly_budget_yen": 20000,
                "alone_time_status": "none",
                "alone_time_weekly_days": None,
                "alone_time_hours": None,
                "has_existing_cat": "no",
                "has_other_pets": "no",
                "address": "埼玉県さいたま市",
                "family": "家族4人（子2人）",
                "environment": "一戸建て",
                "conditions": "人懐っこい猫希望",
            },
            "household_members": [
                {"relation": "wife", "relation_other": None, "age": 40},
                {"relation": "son", "relation_other": None, "age": 12},
                {"relation": "daughter", "relation_other": None, "age": 9},
            ],
            "pets": [],
        },
    ]
    applicants = []
    for payload in applicants_payload:
        applicants.append(
            upsert_applicant_extended(
                db,
                data=payload["data"],
                household_members=payload["household_members"],
                pets=payload["pets"],
            )
        )
    return applicants


def seed_adoption_records(
    db: Session, animals: list[Animal], applicants: list[Applicant]
) -> None:
    """譲渡記録作成"""
    records = [
        {
            "animal_id": animals[0].id,
            "applicant_id": applicants[0].id,
            "interview_date": date(2025, 12, 5),
            "interview_note": "面談実施済み。",
            "decision": "approved",
            "adoption_date": date(2025, 12, 20),
            "follow_up": "譲渡後フォロー中。",
        },
        {
            "animal_id": animals[5].id,
            "applicant_id": applicants[2].id,
            "interview_date": date(2025, 12, 10),
            "interview_note": "家庭環境良好。",
            "decision": "pending",
            "adoption_date": None,
            "follow_up": None,
        },
    ]

    for data in records:
        exists = (
            db.query(AdoptionRecord)
            .filter(
                AdoptionRecord.animal_id == data["animal_id"],
                AdoptionRecord.applicant_id == data["applicant_id"],
            )
            .first()
        )
        if exists:
            continue

        record = AdoptionRecord(**data)
        db.add(record)

    db.commit()


def seed_care_logs(
    db: Session, animals: list[Animal], volunteers: list[Volunteer]
) -> None:
    """世話記録作成"""
    time_slots = ["morning", "noon", "evening"]
    target_animals = animals[:6]
    today = get_jst_date()
    count = 0

    for days_ago in range(7):
        log_date = today - timedelta(days=days_ago)
        for animal in target_animals:
            for time_slot in time_slots:
                exists = (
                    db.query(CareLog)
                    .filter(
                        CareLog.animal_id == animal.id,
                        CareLog.log_date == log_date,
                        CareLog.time_slot == time_slot,
                    )
                    .first()
                )
                if exists:
                    continue

                volunteer = volunteers[count % len(volunteers)]
                defecation = time_slot in ["morning", "evening"]

                care_log = CareLog(
                    animal_id=animal.id,
                    recorder_id=volunteer.id,
                    recorder_name=volunteer.name,
                    log_date=log_date,
                    time_slot=time_slot,
                    appetite=4,
                    energy=4,
                    urination=time_slot in ["morning", "evening"],
                    defecation=defecation,
                    stool_condition=3 if defecation else None,
                    cleaning=time_slot == "morning",
                    memo="サンプル記録" if days_ago == 0 else None,
                    ip_address="192.168.1.100",
                    user_agent="seed-script",
                    device_tag=f"tablet-{volunteer.id}",
                    from_paper=False,
                )
                db.add(care_log)
                count += 1

    db.commit()


def seed_animal_images(db: Session, animals: list[Animal]) -> None:
    """猫画像作成"""
    targets = animals[:4]
    for animal in targets:
        for idx in range(2):
            image_path = f"/static/images/animals/sample_{animal.id}_{idx + 1}.jpg"
            exists = (
                db.query(AnimalImage)
                .filter(
                    AnimalImage.animal_id == animal.id,
                    AnimalImage.image_path == image_path,
                )
                .first()
            )
            if exists:
                continue

            image = AnimalImage(
                animal_id=animal.id,
                image_path=image_path,
                taken_at=None,
                description="サンプル画像",
                file_size=0,
            )
            db.add(image)

    db.commit()


def main() -> None:
    """メイン処理"""
    db = SessionLocal()
    try:
        users = seed_users(db)
        volunteers = seed_volunteers(db)
        animals = seed_animals(db)
        seed_status_history(db, animals, users["admin"])
        actions = seed_medical_actions(db, users["admin"])
        seed_medical_records(db, animals, users["vet"], actions)
        applicants = seed_applicants(db)
        seed_adoption_records(db, animals, applicants)
        seed_care_logs(db, animals, volunteers)
        seed_animal_images(db, animals)

        print("✅ 正規シードの投入が完了しました")
    except Exception as exc:
        db.rollback()
        raise exc
    finally:
        db.close()


if __name__ == "__main__":
    main()

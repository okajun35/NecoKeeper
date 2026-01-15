"""
pytest共通設定

全テストで共有されるフィクスチャとデータベース設定
"""

from __future__ import annotations

import os
import warnings
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

# テスト用のSECRET_KEYを設定（warningを抑制）
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-testing-only")

# テスト環境でのSECRET_KEY warningを抑制
warnings.filterwarnings("ignore", message="デフォルトのSECRET_KEYが使用されています")

# ruff: noqa: E402
from app.auth.password import hash_password
from app.database import Base, get_db
from app.main import app
from app.models.adoption_record import AdoptionRecord
from app.models.animal import Animal
from app.models.animal_image import AnimalImage
from app.models.applicant import Applicant
from app.models.care_log import CareLog
from app.models.setting import Setting
from app.models.status_history import StatusHistory
from app.models.user import User
from app.models.volunteer import Volunteer

# テスト用のインメモリデータベース（StaticPoolで接続を共有）
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db() -> Generator[Session, None, None]:
    """テスト用のデータベースセッションを提供"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


# 依存性をオーバーライド
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session", autouse=True)
def setup_test_database() -> Generator[None, None, None]:
    """テストセッション開始時にテーブルを作成"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def test_client() -> TestClient:
    """テストクライアントを提供（関数スコープ）"""
    return TestClient(app)


@pytest.fixture(scope="function", autouse=True)
def test_db() -> Generator[Session, None, None]:
    """各テスト関数ごとにデータベースセッションを提供（自動使用）"""
    db = TestingSessionLocal()

    # 既存のデータをクリア（外部キー制約の順序に注意）
    try:
        # 医療記録関連のインポート
        from app.models.medical_action import MedicalAction
        from app.models.medical_record import MedicalRecord

        db.query(AdoptionRecord).delete()
        db.query(Applicant).delete()
        db.query(AnimalImage).delete()
        db.query(CareLog).delete()
        db.query(MedicalRecord).delete()  # 診療記録を追加
        db.query(MedicalAction).delete()  # 診療行為を追加
        db.query(StatusHistory).delete()
        db.query(Animal).delete()
        db.query(Setting).delete()
        db.query(Volunteer).delete()
        db.query(User).delete()
        db.commit()
    except Exception:
        db.rollback()

    # APIテスト用のデータを作成
    # テスト用ユーザーを作成（staff role for comprehensive permissions）
    test_user = User(
        email="test@example.com",
        password_hash=hash_password("TestPassword123"),
        name="Test User",
        role="staff",  # staff role has csv:export and volunteer:write permissions
        is_active=True,
    )
    db.add(test_user)

    # テスト用の猫を作成
    test_animal = Animal(
        name="テスト猫",
        photo="test.jpg",
        pattern="キジトラ",
        tail_length="長い",
        age_months=12,
        gender="female",
        status="保護中",
    )
    db.add(test_animal)

    db.commit()

    yield db

    # テスト後のクリーンアップ
    try:
        # 医療記録関連のインポート
        from app.models.medical_action import MedicalAction
        from app.models.medical_record import MedicalRecord

        db.query(AdoptionRecord).delete()
        db.query(Applicant).delete()
        db.query(AnimalImage).delete()
        db.query(CareLog).delete()
        db.query(MedicalRecord).delete()  # 診療記録を追加
        db.query(MedicalAction).delete()  # 診療行為を追加
        db.query(StatusHistory).delete()
        db.query(Animal).delete()
        db.query(Setting).delete()
        db.query(Volunteer).delete()
        db.query(User).delete()
        db.commit()
    except Exception:
        db.rollback()
    finally:
        db.close()


@pytest.fixture(scope="function")
def auth_token(test_client: TestClient, test_db: Session) -> str:
    """認証トークンを取得（test_dbに依存してユーザーが作成済みであることを保証）"""
    response = test_client.post(
        "/api/v1/auth/token",
        data={
            "username": "test@example.com",
            "password": "TestPassword123",
        },
    )
    if response.status_code != 200:
        raise Exception(
            f"Failed to get auth token: {response.status_code} - {response.text}"
        )
    return response.json()["access_token"]


@pytest.fixture(scope="function")
def auth_headers(auth_token: str) -> dict[str, str]:
    """認証ヘッダーを取得"""
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture(scope="function")
def test_user(test_db: Session) -> User:
    """テスト用ユーザーを取得（staff role）"""
    user = test_db.query(User).filter(User.email == "test@example.com").first()
    if not user:
        raise Exception("Test user not found in database")
    return user


@pytest.fixture(scope="function")
def test_vet_user(test_db: Session) -> User:
    """テスト用獣医師ユーザーを作成（vet role for medical:write）"""
    vet_user = User(
        email="vet@example.com",
        password_hash=hash_password("VetPassword123"),
        name="Test Vet",
        role="vet",
        is_active=True,
    )
    test_db.add(vet_user)
    test_db.commit()
    test_db.refresh(vet_user)
    return vet_user


@pytest.fixture(scope="function")
def vet_auth_token(test_client: TestClient, test_vet_user: User) -> str:
    """獣医師用認証トークンを取得"""
    response = test_client.post(
        "/api/v1/auth/token",
        data={
            "username": "vet@example.com",
            "password": "VetPassword123",
        },
    )
    if response.status_code != 200:
        raise Exception(
            f"Failed to get vet auth token: {response.status_code} - {response.text}"
        )
    return response.json()["access_token"]


@pytest.fixture(scope="function")
def vet_auth_headers(vet_auth_token: str) -> dict[str, str]:
    """獣医師用認証ヘッダーを生成"""
    return {"Authorization": f"Bearer {vet_auth_token}"}


@pytest.fixture(scope="function")
def test_animal(test_db: Session) -> Animal:
    """テスト用の猫を取得"""
    animal = test_db.query(Animal).filter(Animal.name == "テスト猫").first()
    if not animal:
        raise Exception("Test animal not found in database")
    return animal


@pytest.fixture(scope="function")
def test_animals_bulk(test_db: Session) -> list[Animal]:
    """テスト用の複数の猫を作成（15個）"""
    animals: list[Animal] = []
    for i in range(15):
        animal = Animal(
            name=f"猫{i}",
            photo=f"photo{i}.jpg",
            pattern="三毛" if i % 2 == 0 else "キジトラ",
            tail_length="長い" if i % 2 == 0 else "短い",
            age_months=12,
            gender="female" if i % 2 == 0 else "male",
            status="保護中" if i % 3 == 0 else "譲渡可能",
        )
        test_db.add(animal)
        animals.append(animal)

    test_db.commit()

    # 各animalをrefreshしてIDを取得
    for animal in animals:
        test_db.refresh(animal)

    return animals


@pytest.fixture(scope="function")
def test_volunteer(test_db: Session) -> Volunteer:
    """テスト用ボランティアを作成"""
    volunteer = Volunteer(
        name="テストボランティア",
        contact="090-1234-5678",
        affiliation="保護猫団体A",
        status="active",
    )
    test_db.add(volunteer)
    test_db.commit()
    test_db.refresh(volunteer)
    return volunteer


@pytest.fixture(scope="function")
def test_care_logs(test_db: Session, test_animal: Animal) -> list[CareLog]:
    """テスト用のケアログを作成"""
    from datetime import datetime

    care_logs = [
        CareLog(
            animal_id=test_animal.id,
            time_slot="morning",
            recorder_name="テストユーザー",
            appetite=4,
            energy=4,
            urination=True,
            cleaning=True,
            memo="朝の記録",
            created_at=datetime(2024, 11, 15, 9, 0, 0),
        ),
        CareLog(
            animal_id=test_animal.id,
            time_slot="noon",
            recorder_name="テストユーザー",
            appetite=3,
            energy=3,
            urination=False,
            cleaning=True,
            memo="昼の記録",
            created_at=datetime(2024, 11, 15, 12, 0, 0),
        ),
        CareLog(
            animal_id=test_animal.id,
            time_slot="evening",
            recorder_name="テストユーザー",
            appetite=5,
            energy=4,
            urination=True,
            cleaning=True,
            memo="夕方の記録",
            created_at=datetime(2024, 11, 15, 18, 0, 0),
        ),
    ]

    for care_log in care_logs:
        test_db.add(care_log)

    test_db.commit()

    for care_log in care_logs:
        test_db.refresh(care_log)

    return care_logs


@pytest.fixture(scope="function")
def temp_media_dir(tmp_path, monkeypatch):
    """テスト用の一時メディアディレクトリを作成"""
    # 一時ディレクトリを作成
    media_dir = tmp_path / "media"
    media_dir.mkdir()

    # 環境変数をモンキーパッチ
    monkeypatch.setenv("MEDIA_DIR", str(media_dir))

    # app.configのmedia_dirもオーバーライド
    from app.config import get_settings

    settings = get_settings()
    monkeypatch.setattr(settings, "media_dir", str(media_dir))

    yield media_dir

    # クリーンアップは自動的に行われる（tmp_pathが削除される）


@pytest.fixture(scope="function")
def automation_api_key(monkeypatch) -> str:
    """Automation API用のテストキーを設定"""
    from app.config import get_settings

    # 環境変数を設定
    monkeypatch.setenv("ENABLE_AUTOMATION_API", "true")
    monkeypatch.setenv("AUTOMATION_API_KEY", "test-api-key-32-characters-long-xxx")

    # 設定キャッシュをクリア
    get_settings.cache_clear()

    return "test-api-key-32-characters-long-xxx"

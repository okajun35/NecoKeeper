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
from app.models.animal import Animal
from app.models.care_log import CareLog
from app.models.status_history import StatusHistory
from app.models.user import User

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

    # 既存のデータをクリア
    try:
        db.query(CareLog).delete()
        db.query(StatusHistory).delete()
        db.query(Animal).delete()
        db.query(User).delete()
        db.commit()
    except Exception:
        db.rollback()

    # APIテスト用のデータを作成
    # テスト用ユーザーを作成
    test_user = User(
        email="test@example.com",
        password_hash=hash_password("TestPassword123"),
        name="Test User",
        role="staff",
        is_active=True,
    )
    db.add(test_user)

    # テスト用の猫を作成
    test_animal = Animal(
        name="テスト猫",
        photo="test.jpg",
        pattern="キジトラ",
        tail_length="長い",
        age="成猫",
        gender="female",
        status="保護中",
    )
    db.add(test_animal)

    db.commit()

    yield db

    # テスト後のクリーンアップ
    try:
        db.query(CareLog).delete()
        db.query(StatusHistory).delete()
        db.query(Animal).delete()
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
def test_user(test_db: Session) -> User:
    """テスト用ユーザーを取得"""
    user = test_db.query(User).filter(User.email == "test@example.com").first()
    if not user:
        raise Exception("Test user not found in database")
    return user


@pytest.fixture(scope="function")
def test_animal(test_db: Session) -> Animal:
    """テスト用の猫を取得"""
    animal = test_db.query(Animal).filter(Animal.name == "テスト猫").first()
    if not animal:
        raise Exception("Test animal not found in database")
    return animal


@pytest.fixture(scope="function")
def test_animals_bulk(test_db: Session) -> list[Animal]:
    """テスト用の複数の猫を作成"""
    animals: list[Animal] = []
    for i in range(10):
        animal = Animal(
            name=f"猫{i}",
            photo=f"photo{i}.jpg",
            pattern="三毛" if i % 2 == 0 else "キジトラ",
            tail_length="長い" if i % 2 == 0 else "短い",
            age="成猫",
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

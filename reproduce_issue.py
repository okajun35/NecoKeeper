import os

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.auth.password import hash_password
from app.config import get_settings
from app.database import Base, get_db
from app.main import app
from app.models.animal import Animal
from app.models.user import User

# Setup In-Memory DB
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
Base.metadata.create_all(bind=engine)
db = TestingSessionLocal()

# Create user
user = User(
    email="test@example.com",
    password_hash=hash_password("password"),
    name="Test User",
    role="staff",
    is_active=True,
)
db.add(user)

# Create animal
animal = Animal(
    name="Test Cat",
    photo="test.jpg",
    pattern="Pattern",
    tail_length="Long",
    age_months=24,
    gender="female",
    status="Protected",
)
db.add(animal)
db.commit()
db.refresh(user)
db.refresh(animal)

# Get token
client = TestClient(app)
response = client.post(
    "/api/v1/auth/token", data={"username": "test@example.com", "password": "password"}
)
token = response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# Enable Kiroween Mode
os.environ["KIROWEEN_MODE"] = "true"
get_settings.cache_clear()

# Request edit page
response = client.get(f"/admin/animals/{animal.id}/edit", headers=headers)

print(f"Status Code: {response.status_code}")
print(f"Content Type: {response.headers['content-type']}")
content = response.content.decode("utf-8")
print("Content length:", len(content))

if "猫情報編集" in content:
    print("Found '猫情報編集'")
else:
    print("NOT Found '猫情報編集'")
    print("Content snippet:")
    print(content[:500])
    print("...")
    print(content[-500:])

# Cleanup
db.close()
Base.metadata.drop_all(bind=engine)

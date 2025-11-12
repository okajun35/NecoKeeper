---
inclusion: always
---

# Python バックエンド開発ベストプラクティス

このドキュメントは、NecoKeeperプロジェクトにおけるPythonバックエンド開発（FastAPI、SQLAlchemy、Alembic、Pytest）のベストプラクティスを定義します。
すべてのコード作成・修正時にこれらのルールに従ってください。

**Context7参照**:
- `/zhanymkanov/fastapi-best-practices` (Trust Score: 8.8)
- `/fastapi/fastapi` (Trust Score: 9.9)
- `/websites/python_3_15` (Trust Score: 7.5)
- `/pytest-dev/pytest` (Trust Score: 9.5)
- `/sqlalchemy/sqlalchemy` (Code Snippets: 2830)
- `/sqlalchemy/alembic` (Code Snippets: 363)
- `/python/typing` (Trust Score: 8.9)
- `/python/mypy` (Trust Score: 8.9)

---

## 🔧 必須実行項目

### 1. コードフォーマット
**すべてのPythonファイル作成・修正後、必ずRuffでフォーマットを実行すること**

```bash
# Lintチェックと自動修正
ruff check . --fix

# コードフォーマット
ruff format .
```

### 2. テスト実行
**すべてのコード変更後、Pytestを実施してすべてのテストケースがPassするまでテストを修正・実施すること**

```bash
# すべてのテストを実行
python -m pytest

# 詳細出力
python -m pytest -v

# 特定のテストファイルのみ
python -m pytest tests/test_specific.py
```

### 3. 非推奨ライブラリの検証
**warningで非推奨のライブラリが表示された場合、Context7を使用して代替ライブラリを検証すること**

```python
# 非推奨の警告が出た場合の対応手順:
# 1. Context7で最新のライブラリを検索
# 2. Trust Scoreが高い(8.0以上)ライブラリを選択
# 3. 最新バージョンのドキュメントを確認
# 4. 移行パスを確認して実装
```

---

## 📁 プロジェクト構造

```
app/
├── api/           # APIエンドポイント
│   └── v1/        # APIバージョン管理
├── models/        # SQLAlchemyモデル
├── schemas/       # Pydanticスキーマ
├── services/      # ビジネスロジック
├── auth/          # 認証・認可
├── utils/         # ユーティリティ関数
├── config.py      # 設定管理
├── database.py    # データベース接続
└── main.py        # アプリケーションエントリーポイント

tests/             # テストコード
├── conftest.py    # Pytestフィクスチャ
├── api/           # APIテスト
├── models/        # モデルテスト
└── services/      # サービステスト
```

---

## 🐍 Python コーディング規約

### インポート順序
**標準ライブラリ → サードパーティ → ローカルモジュールの順**

```python
# 標準ライブラリ
import os
import sys
from datetime import datetime
from typing import Optional

# サードパーティ
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

# ローカルモジュール
from app.database import get_db
from app.models.user import User
```

### 型ヒント
**すべての関数に型ヒントを付けること**

**Context7参照**: `/python/typing` (Trust Score: 8.9), `/python/mypy` (Trust Score: 8.9)

```python
from __future__ import annotations  # 前方参照を有効化

from collections.abc import Iterator, Callable
from sqlalchemy.orm import Session

# ✅ 推奨: collections.abcを使用
def get_user(db: Session, user_id: int) -> User | None:
    """ユーザーを取得"""
    return db.query(User).filter(User.id == user_id).first()

# ✅ 推奨: X | None 構文（Python 3.10+）
async def create_item(
    item_data: ItemCreate,
    db: Session = Depends(get_db)
) -> Item:
    """アイテムを作成"""
    item = Item(**item_data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

# ✅ 推奨: 明示的な型注釈（空のコレクション）
def process_items() -> list[Item]:
    """アイテムを処理"""
    items: list[Item] = []  # 明示的な型注釈
    for i in range(10):
        items.append(Item(id=i))
    return items

# ✅ 推奨: Callable型ヒント
def register_callback(
    callback: Callable[[str], int]
) -> None:
    """コールバックを登録"""
    pass

# ✅ 推奨: Generator型ヒント
def generate_numbers(n: int) -> Iterator[int]:
    """数値を生成"""
    i = 0
    while i < n:
        yield i
        i += 1

# ❌ 非推奨: typing モジュールの型
# from typing import Optional, List, Dict
# def get_user(db: Session, user_id: int) -> Optional[User]:
#     pass
```

### コンテキストマネージャー
**ファイル操作は必ずwith文を使用**

```python
# Good
with open("file.txt") as f:
    content = f.read()

# Bad
f = open("file.txt")
content = f.read()
f.close()
```

### Docstring
**すべての関数・クラスにDocstringを記述**

```python
def calculate_total(items: list[Item]) -> Decimal:
    """
    アイテムの合計金額を計算

    Args:
        items: アイテムのリスト

    Returns:
        Decimal: 合計金額

    Example:
        >>> items = [Item(price=100), Item(price=200)]
        >>> calculate_total(items)
        Decimal('300.00')
    """
    return sum(item.price for item in items)
```

---

## 🚀 FastAPI ベストプラクティス

### 1. 依存性注入の活用

```python
from fastapi import Depends
from sqlalchemy.orm import Session

# データベースセッション
def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 認証
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    # トークン検証ロジック
    return user

# エンドポイントで使用
@app.get("/items/")
async def read_items(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Item).all()
```

### 2. Pydanticスキーマの分離

```python
# schemas/item.py
from pydantic import BaseModel, Field

class ItemBase(BaseModel):
    """共通フィールド"""
    name: str = Field(..., max_length=100)
    description: str | None = None

class ItemCreate(ItemBase):
    """作成用スキーマ"""
    price: Decimal = Field(..., gt=0)

class ItemUpdate(BaseModel):
    """更新用スキーマ（全フィールド任意）"""
    name: str | None = None
    description: str | None = None
    price: Decimal | None = None

class ItemResponse(ItemBase):
    """レスポンススキーマ"""
    id: int
    price: Decimal
    created_at: datetime

    model_config = {"from_attributes": True}
```

### 3. ビジネスロジックの分離

```python
# services/item_service.py
def create_item(db: Session, item_data: ItemCreate) -> Item:
    """
    アイテムを作成

    ビジネスロジックはサービス層に配置
    """
    item = Item(**item_data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

# api/v1/items.py
@router.post("", response_model=ItemResponse)
async def create_item_endpoint(
    item_data: ItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    エンドポイントはルーティングのみ
    ビジネスロジックはサービス層に委譲
    """
    return create_item(db, item_data)
```

### 4. 適切なHTTPステータスコード

```python
from fastapi import status

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_item(...):
    """作成: 201 Created"""
    pass

@router.get("/{id}")
async def get_item(...):
    """取得: 200 OK"""
    pass

@router.put("/{id}")
async def update_item(...):
    """更新: 200 OK"""
    pass

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(...):
    """削除: 204 No Content"""
    pass
```

### 5. エラーハンドリング

```python
from fastapi import HTTPException, status

def get_item(db: Session, item_id: int) -> Item:
    """アイテムを取得"""
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item {item_id} not found"
        )
    return item
```

---

## 🗄️ SQLAlchemy ベストプラクティス

**Context7参照**: `/sqlalchemy/sqlalchemy` (Code Snippets: 2830)

### 1. モダンなDeclarative Mapping

**推奨: Mapped と mapped_column を使用**

```python
from sqlalchemy import String, Integer, DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import datetime
from typing import Optional

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(255), unique=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now()
    )
    # オプショナルフィールドはOptional型を使用
    description: Mapped[Optional[str]] = mapped_column(String(500))
```

### 2. コネクションとトランザクション管理

**コンテキストマネージャーを使用**

```python
from sqlalchemy import create_engine

engine = create_engine("postgresql://user:pass@localhost/db")

# 推奨: コンテキストマネージャーでトランザクション管理
with engine.begin() as conn:
    conn.execute(table.insert(), parameters)
    result = conn.execute(table.select())
    conn.execute(table.update(), parameters)
```

### 3. パフォーマンス最適化

**特定のカラムのみを選択**

```python
from sqlalchemy import select

# ✅ 推奨: 必要なカラムのみ選択
stmt = select(User.id, User.name)
result = session.execute(stmt)

# ❌ 非推奨: 全カラム取得（不要な場合）
stmt = select(User)
```

**キャッシュを活用した繰り返しクエリ**

```python
def run_my_statement(connection, parameter):
    """SQLコンパイルキャッシュを活用"""
    stmt = select(table)
    stmt = stmt.where(table.c.col == parameter)
    stmt = stmt.order_by(table.c.id)
    return connection.execute(stmt)
```

### 4. リレーションシップのJOIN

**推奨されるJOINパターン**

```python
from sqlalchemy.orm import Session

# ✅ 推奨: リレーションシップを直接指定
q = session.query(User).join(User.addresses).filter(Address.email_address == "ed@foo.com")

# ✅ 推奨: ターゲットを明示的に指定
q = (
    session.query(User)
    .join(Address, User.addresses)
    .filter(Address.email_address == "ed@foo.com")
)
```

### 5. テーブル・カラム命名規則

```python
# lower_case_snake を使用
# テーブル名は単数形
class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now()
    )

# 関連テーブルはモジュールプレフィックス
class PaymentAccount(Base):
    __tablename__ = "payment_account"

class PaymentBill(Base):
    __tablename__ = "payment_bill"
```

### 6. インデックス命名規則

```python
from sqlalchemy import MetaData

POSTGRES_INDEXES_NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=POSTGRES_INDEXES_NAMING_CONVENTION)
```

---

## 🧪 Pytest ベストプラクティス

**Context7参照**: `/pytest-dev/pytest` (Trust Score: 9.5)

### 1. 基本的なパラメータ化テスト

```python
import pytest

@pytest.mark.parametrize(
    "test_input,expected",
    [
        ("3+5", 8),
        ("2+4", 6),
        pytest.param("6*9", 42, marks=pytest.mark.xfail),  # 期待される失敗
    ],
)
def test_eval(test_input, expected):
    assert eval(test_input) == expected
```

### 2. フィクスチャのパラメータ化

```python
import pytest

@pytest.fixture(params=[0, 1], ids=["spam", "ham"])
def data_set(request):
    """パラメータ化されたフィクスチャ"""
    return request.param

def test_data(data_set):
    """data_setは0と1で2回実行される"""
    pass
```

### 3. スコープ付きフィクスチャ

```python
import pytest

@pytest.fixture(scope="module", params=["mod1", "mod2"])
def modarg(request):
    """モジュールスコープのフィクスチャ"""
    param = request.param
    print(f"  SETUP modarg {param}")
    yield param
    print(f"  TEARDOWN modarg {param}")

@pytest.fixture(scope="function", params=[1, 2])
def otherarg(request):
    """関数スコープのフィクスチャ"""
    param = request.param
    print(f"  SETUP otherarg {param}")
    yield param
    print(f"  TEARDOWN otherarg {param}")

def test_example(modarg, otherarg):
    """複数のスコープを持つフィクスチャを使用"""
    print(f"  RUN test with modarg {modarg} and otherarg {otherarg}")
```

### 4. 間接的なパラメータ化

```python
import pytest

@pytest.fixture
def fixt(request):
    """フィクスチャでパラメータを処理"""
    return request.param * 3

@pytest.mark.parametrize("fixt", ["a", "b"], indirect=True)
def test_indirect(fixt):
    """フィクスチャを通じてパラメータを渡す"""
    assert len(fixt) == 3
```

### 5. クラスレベルのパラメータ化

```python
import pytest

@pytest.mark.parametrize("n,expected", [(1, 2), (3, 4)])
class TestClass:
    """クラス全体にパラメータを適用"""

    def test_simple_case(self, n, expected):
        assert n + 1 == expected

    def test_weird_simple_case(self, n, expected):
        assert (n * 1) + 1 == expected
```

### 6. モジュールレベルのパラメータ化

```python
import pytest

# モジュール全体にパラメータを適用
pytestmark = pytest.mark.parametrize("n,expected", [(1, 2), (3, 4)])

class TestClass:
    def test_simple_case(self, n, expected):
        assert n + 1 == expected

    def test_weird_simple_case(self, n, expected):
        assert (n * 1) + 1 == expected
```

### 7. フィクスチャのオーバーライド

```python
# conftest.py
import pytest

@pytest.fixture(params=['one', 'two', 'three'])
def parametrized_username(request):
    return request.param

# test_something.py
@pytest.fixture
def parametrized_username():
    """特定のテストモジュールでフィクスチャをオーバーライド"""
    return 'overridden-username'

def test_username(parametrized_username):
    assert parametrized_username == 'overridden-username'
```

### 8. FastAPI TestClient

```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_main():
    """メインエンドポイントのテスト"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"msg": "Hello World"}

def test_create_item():
    """アイテム作成のテスト"""
    response = client.post(
        "/items/",
        json={"name": "Test Item", "price": 100}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Item"
    assert "id" in data
```

### 9. 非同期テスト

```python
import pytest
from httpx import AsyncClient, ASGITransport

@pytest.mark.anyio
async def test_async_endpoint():
    """非同期エンドポイントのテスト"""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        response = await client.get("/async-endpoint")
        assert response.status_code == 200
```

### 10. データベーステスト用フィクスチャ

```python
# conftest.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

@pytest.fixture(scope="function")
def test_db():
    """テスト用データベースセッション"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def auth_token(test_client):
    """認証トークンを取得"""
    response = test_client.post(
        "/auth/token",
        data={"username": "test@example.com", "password": "password"}
    )
    return response.json()["access_token"]
```

---

## 🔍 Mypy 型チェック設定

**Context7参照**: `/python/mypy` (Trust Score: 8.9)

### 1. mypy.ini設定ファイル

**Strict モードの推奨設定**

```ini
# mypy.ini
[mypy]
python_version = 3.12
warn_return_any = True
warn_unused_configs = True
warn_redundant_casts = True
warn_unused_ignores = True
strict_equality = True
check_untyped_defs = True
disallow_subclassing_any = True
disallow_untyped_decorators = True
disallow_any_generics = True
disallow_untyped_calls = True
disallow_incomplete_defs = True
disallow_untyped_defs = True
no_implicit_reexport = True
extra_checks = True

# プラグイン
plugins = pydantic.mypy, sqlalchemy.ext.mypy.plugin

# 除外パターン
exclude = (?x)(
    ^\.venv/
    | ^venv/
    | ^build/
    | ^dist/
  )

# サードパーティライブラリの型スタブがない場合
[mypy-some_untyped_library.*]
ignore_missing_imports = True
```

### 2. 型チェックの実行

```bash
# すべてのファイルをチェック
mypy .

# 特定のディレクトリをチェック
mypy app/

# Strict モードで実行
mypy --strict app/

# レポート生成
mypy --html-report ./mypy-report app/
```

### 3. 型ヒントのベストプラクティス

**モダンな型ヒント構文**

```python
from __future__ import annotations

from collections.abc import Sequence, Mapping, Callable
from typing import Protocol, TypeVar

# ✅ 推奨: collections.abc を使用
def process_items(items: Sequence[str]) -> list[int]:
    return [len(item) for item in items]

# ✅ 推奨: X | None 構文
def find_user(user_id: int) -> User | None:
    return db.query(User).get(user_id)

# ✅ 推奨: Union型は | で表現
def parse_value(value: str | int | float) -> float:
    return float(value)

# ✅ 推奨: Protocol を使用した構造的サブタイピング
class Closeable(Protocol):
    def close(self) -> None: ...

def close_all(items: Sequence[Closeable]) -> None:
    for item in items:
        item.close()

# ✅ 推奨: TypeVar でジェネリック型を定義
T = TypeVar('T')

def first(items: Sequence[T]) -> T | None:
    return items[0] if items else None
```

**空のコレクションの型注釈**

```python
# ✅ 推奨: 明示的な型注釈
items: list[str] = []
mapping: dict[str, int] = {}

# ❌ 非推奨: 型注釈なし（Mypyが推論できない）
# items = []  # Mypyエラー
```

---

## ⚙️ 設定管理

### Pydantic Settingsの使用

```python
# config.py
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    """アプリケーション設定"""
    app_name: str = "NecoKeeper"
    debug: bool = False
    secret_key: str
    database_url: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

@lru_cache()
def get_settings() -> Settings:
    """設定インスタンスを取得（キャッシュ付き）"""
    return Settings()

# 使用例
settings = get_settings()
```

### テスト時の設定オーバーライド

```python
def get_settings_override():
    return Settings(
        database_url="sqlite:///:memory:",
        secret_key="test-secret-key"
    )

app.dependency_overrides[get_settings] = get_settings_override
```

---

## 📝 Alembic マイグレーションベストプラクティス

**Context7参照**: `/sqlalchemy/alembic` (Code Snippets: 363)

### 1. 命名規則の設定

**alembic.ini設定**

```ini
# alembic.ini
[alembic]
script_location = alembic

# マイグレーションファイル名テンプレート
file_template = %%(year)d%%(month).2d%%(day).2d_%%(hour).2d%%(minute).2d_%%(slug)s

# または日付のみ
# file_template = %%(year)d-%%(month).2d-%%(day).2d_%%(slug)s
```

**MetaData命名規則の統合**

```python
# models.py
from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    metadata = MetaData(naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s"
    })

# env.py
from myapp import mymodel
target_metadata = mymodel.Base.metadata

def run_migrations_online():
    context.configure(
        connection=connection,
        target_metadata=target_metadata
    )
```

### 2. マイグレーション命名のベストプラクティス

```bash
# ✅ 良い例: 説明的で実行可能な名前
alembic revision -m "create_user_table"
alembic revision -m "add_email_index_to_users"
alembic revision -m "add_created_at_to_posts"
alembic revision -m "remove_deprecated_status_column"

# ❌ 悪い例: 曖昧な名前
alembic revision -m "update"
alembic revision -m "fix"
alembic revision -m "changes"
```

### 3. 制約の作成と削除

**命名規則を使用した制約操作**

```python
def upgrade():
    """制約を作成（命名規則が自動適用される）"""
    op.create_unique_constraint(
        op.f('uq_const_x'),  # op.f()で明示的に名前を指定
        'some_table',
        'x'
    )

def downgrade():
    """制約を削除"""
    op.drop_constraint("some_check_const", "t1", type_="check")

    # または命名規則をバイパス
    op.drop_constraint(op.f("some_check_const"), "t1", type_="check")
```

**バッチ操作での命名規則**

```python
def upgrade():
    """バッチ操作で外部キーを削除"""
    naming_convention = {
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    }
    with op.batch_alter_table(
        "bar", naming_convention=naming_convention
    ) as batch_op:
        batch_op.drop_constraint(
            "fk_bar_foo_id_foo", type_="foreignkey"
        )
```

### 4. スキーマ管理

**include_nameフックの設定**

```python
# env.py
def include_name(name, type_, parent_names):
    """スキーマとテーブルの包含を制御"""
    if type_ == "schema":
        return name in [None, "schema_one", "schema_two"]
    elif type_ == "table":
        # schema_qualified_table_nameを直接使用
        return (
            parent_names["schema_qualified_table_name"] in
            target_metadata.tables
        )
    else:
        return True

context.configure(
    target_metadata=target_metadata,
    include_name=include_name,
    include_schemas=True
)
```

### 5. マイグレーションのベストプラクティス

1. **静的マイグレーション**: 動的なデータ操作は避ける
2. **リバート可能**: 必ずdowngrade関数を実装
3. **説明的な名前**: マイグレーションの内容が分かる名前を付ける
4. **命名規則の一貫性**: MetaDataの命名規則をAlembicと統合
5. **バッチ操作**: 大規模テーブルでは適切にバッチ操作を使用

---

## 🔒 セキュリティ

### パスワードハッシュ化

```python
from argon2 import PasswordHasher

ph = PasswordHasher()

# ハッシュ化
hashed = ph.hash("password123")

# 検証
try:
    ph.verify(hashed, "password123")
    print("Valid password")
except:
    print("Invalid password")
```

### JWT認証

```python
from datetime import datetime, timedelta
import jwt

def create_access_token(data: dict) -> str:
    """JWTトークンを生成"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=2)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
```

---

## 📊 パフォーマンス

### N+1問題の回避

```python
# Bad: N+1問題
users = db.query(User).all()
for user in users:
    print(user.posts)  # 各ユーザーごとにクエリ実行

# Good: Eager Loading
from sqlalchemy.orm import joinedload

users = db.query(User).options(joinedload(User.posts)).all()
for user in users:
    print(user.posts)  # 1回のクエリで取得
```

### ページネーション

```python
def get_items(
    db: Session,
    skip: int = 0,
    limit: int = 100
) -> list[Item]:
    """ページネーション付きでアイテムを取得"""
    return db.query(Item).offset(skip).limit(limit).all()
```

---

## 🚨 チェックリスト

コード作成・修正時に以下を確認すること:

### 基本チェック
- [ ] Ruffでフォーマット実行済み (`ruff format .`)
- [ ] Ruffでlintチェック実行済み (`ruff check . --fix`)
- [ ] すべてのテストがPass (`python -m pytest`)
- [ ] Mypyで型チェック実行済み (`mypy .`)
- [ ] 型ヒントを付与（`from __future__ import annotations`使用）
- [ ] Docstringを記述
- [ ] エラーハンドリングを実装
- [ ] 非推奨ライブラリを使用していない
- [ ] セキュリティ上の問題がない
- [ ] パフォーマンスを考慮

### 型ヒントチェック
- [ ] `collections.abc`の型を使用（`typing`モジュールではなく）
- [ ] `X | None`構文を使用（`Optional[X]`ではなく）
- [ ] `X | Y`構文を使用（`Union[X, Y]`ではなく）
- [ ] 空のコレクションに明示的な型注釈を付与
- [ ] `Protocol`を使用した構造的サブタイピング
- [ ] 前方参照に`from __future__ import annotations`を使用

### SQLAlchemyチェック
- [ ] モダンな`Mapped`と`mapped_column`を使用
- [ ] コンテキストマネージャーでトランザクション管理
- [ ] 必要なカラムのみを選択してパフォーマンス最適化
- [ ] 適切なJOINパターンを使用
- [ ] 命名規則に従ったインデックス・制約名

### Pytestチェック
- [ ] 適切なフィクスチャスコープを使用
- [ ] パラメータ化テストで複数ケースをカバー
- [ ] テストIDを明示的に指定（可読性向上）
- [ ] 間接的なパラメータ化で複雑なセットアップを実現
- [ ] フィクスチャのオーバーライドを適切に使用

### Alembicチェック
- [ ] 説明的なマイグレーション名を使用
- [ ] `upgrade()`と`downgrade()`の両方を実装
- [ ] 命名規則をMetaDataと統合
- [ ] `op.f()`で制約名を明示的に指定
- [ ] スキーマ管理で`include_name`フックを使用

---

## 📚 参考リソース

### 公式ドキュメント
- [FastAPI公式ドキュメント](https://fastapi.tiangolo.com/)
- [Pydantic公式ドキュメント](https://docs.pydantic.dev/)
- [SQLAlchemy公式ドキュメント](https://docs.sqlalchemy.org/)
- [Alembic公式ドキュメント](https://alembic.sqlalchemy.org/)
- [Pytest公式ドキュメント](https://docs.pytest.org/)
- [Ruff公式ドキュメント](https://docs.astral.sh/ruff/)

### Context7検証済みリソース
- [FastAPI](https://github.com/fastapi/fastapi) - Trust Score: 9.9
- [FastAPI Best Practices](https://github.com/zhanymkanov/fastapi-best-practices) - Trust Score: 8.8
- [Pytest](https://github.com/pytest-dev/pytest) - Trust Score: 9.5
- [SQLAlchemy](https://github.com/sqlalchemy/sqlalchemy) - Code Snippets: 2830
- [Alembic](https://github.com/sqlalchemy/alembic) - Code Snippets: 363
- [Python Typing](https://github.com/python/typing) - Trust Score: 8.9
- [Mypy](https://github.com/python/mypy) - Trust Score: 8.9

---

**最終更新**: 2025-11-12
**Context7検証済み**: ✅

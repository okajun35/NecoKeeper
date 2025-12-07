---
inclusion: always
---

# Python Backend Development Best Practices

This document defines best practices for Python backend development (FastAPI, SQLAlchemy, Alembic, Pytest) in the NecoKeeper project.
Follow these rules when creating or modifying code.

**Context7 References**:
- `/zhanymkanov/fastapi-best-practices` (Trust Score: 8.8)
- `/fastapi/fastapi` (Trust Score: 9.9)
- `/websites/python_3_15` (Trust Score: 7.5)
- `/pytest-dev/pytest` (Trust Score: 9.5)
- `/sqlalchemy/sqlalchemy` (Code Snippets: 2830)
- `/sqlalchemy/alembic` (Code Snippets: 363)
- `/python/typing` (Trust Score: 8.9)
- `/python/mypy` (Trust Score: 8.9)

---

## 🔧 Required Actions

### 1. Code Formatting
**Always run Ruff formatting after creating or modifying any Python file**

```bash
# Lint check and auto-fix
ruff check . --fix

# Code formatting
ruff format .
```

### 2. Test Execution and Coverage Measurement
**After all code changes, run Pytest and fix/run tests until all test cases pass**

**Coverage Goals**:
- **Service Layer**: 80%+
- **API Layer**: 70%+
- **Overall**: 70%+ (aiming for 80% eventually)

```bash
# Run all tests with coverage
python -m pytest --cov=app --cov-report=html --cov-report=term-missing

# Coverage threshold check (fail if below 70%)
python -m pytest --cov=app --cov-report=term-missing --cov-fail-under=70

# Verbose output
python -m pytest -v --cov=app

# Specific test file only
python -m pytest tests/test_specific.py --cov=app

# View HTML report in browser
# Linux: xdg-open htmlcov/index.html
# macOS: open htmlcov/index.html
# Windows: start htmlcov/index.html
```

**Coverage configuration (pyproject.toml)**:
```toml
[tool.pytest.ini_options]
addopts = [
    "--cov=app",
    "--cov-report=html",
    "--cov-report=term-missing",
    "--cov-report=term:skip-covered",
]

[tool.coverage.run]
source = ["app"]
omit = ["*/tests/*", "*/test_*.py"]
branch = true

[tool.coverage.report]
precision = 2
show_missing = true
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
    "if TYPE_CHECKING:",
    "@(abc\\.)?abstractmethod",
]
```

### 3. Deprecated Library Verification
**When deprecated library warnings appear, use Context7 to verify alternative libraries**

```python
# Steps when deprecation warnings appear:
# 1. Search for latest library in Context7
# 2. Select library with high Trust Score (8.0+)
# 3. Check latest version documentation
# 4. Verify migration path and implement
```

### 4. Test Coverage and DDD/TDD Principles

**From DDD (Domain-Driven Design) and TDD (Test-Driven Development) Perspective**:

#### Test Coverage Priority (t-wada Compliant)

1. **Domain Layer (Highest Priority)**: 90%+
   - Business rule validation
   - Entity invariants
   - Value object validation
   - Domain service logic

2. **Application Layer (High Priority)**: 80%+
   - Use case execution flow
   - Service layer business logic
   - Transaction boundaries

3. **Infrastructure Layer (Medium Priority)**: 70%+
   - Repository persistence logic
   - External service integration

4. **Presentation Layer (Low Priority)**: 60%+
   - API endpoints
   - Request/response transformation

#### Development Continuation Decision at 73% Coverage

**✅ Conditions to Continue Development**:
- Domain layer (models/) coverage is 80%+
- Service layer (services/) main use cases are tested
- Regression tests for existing features are in place
- New features developed test-first

**⚠️ Conditions Requiring Improvement**:
- Service layer coverage below 50% (currently 36% in some files)
- Domain logic tests insufficient
- Edge case tests not implemented

**Current Status (73.48%)**:
- ✅ Domain Layer (models/): High coverage (90%+)
- ⚠️ Service Layer (services/): Needs improvement (36-68%)
- ✅ Auth Layer (auth/): Good (75-95%)
- ❌ Utility Layer (utils/image.py): Untested (0%)

**Recommended Actions**:
1. **Before Phase 5**: Add tests for `app/services/animal_service.py` (36%)
2. **During Phase 5**: Develop new features test-first
3. **After Phase 5**: Add tests for `app/utils/image.py` (0%)
4. **Continuously**: Maintain 70%+ coverage at each Phase completion

**Test-First Development Principles**:
```python
# 1. Red: Write a failing test
def test_create_image_gallery():
    # Given
    animal_id = 1
    image_data = b"fake_image_data"

    # When
    result = image_service.upload_image(animal_id, image_data)

    # Then
    assert result.success is True
    assert result.image_id is not None

# 2. Green: Write minimal code to pass
def upload_image(animal_id: int, image_data: bytes) -> UploadResult:
    # Minimal implementation
    return UploadResult(success=True, image_id=1)

# 3. Refactor: Improve the code
def upload_image(animal_id: int, image_data: bytes) -> UploadResult:
    # Implementation after refactoring
    validated_data = validate_image(image_data)
    saved_path = save_to_storage(validated_data)
    return UploadResult(success=True, image_id=saved_path.id)
```

---

## 📁 Project Structure

```
app/
├── api/           # API endpoints
│   └── v1/        # API versioning
├── models/        # SQLAlchemy models
├── schemas/       # Pydantic schemas
├── services/      # Business logic
├── auth/          # Authentication & authorization
├── utils/         # Utility functions
├── config.py      # Configuration management
├── database.py    # Database connection
└── main.py        # Application entry point

tests/             # Test code
├── conftest.py    # Pytest fixtures
├── api/           # API tests
├── models/        # Model tests
└── services/      # Service tests
```

---

## 🐍 Python Coding Conventions

### Import Order
**Standard library → Third-party → Local modules**

```python
# Standard library
import os
import sys
from datetime import datetime
from typing import Optional

# Third-party
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

# Local modules
from app.database import get_db
from app.models.user import User
```

### Type hints
**Add type hints to all functions**

**Context7 reference**: `/python/typing` (Trust Score: 8.9), `/python/mypy` (Trust Score: 8.9)

```python
from __future__ import annotations  # Enable forward references

from collections.abc import Iterator, Callable
from sqlalchemy.orm import Session

# ✅ Recommended: use collections.abc
def get_user(db: Session, user_id: int) -> User | None:
    """Get a user"""
    return db.query(User).filter(User.id == user_id).first()

# ✅ Recommended: X | None syntax (Python 3.10+)
async def create_item(
    item_data: ItemCreate,
    db: Session = Depends(get_db)
) -> Item:
    """Create an item"""
    item = Item(**item_data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

# ✅ Recommended: explicit type annotations (empty collections)
def process_items() -> list[Item]:
    """Process items"""
    items: list[Item] = []  # Explicit type annotation
    for i in range(10):
        items.append(Item(id=i))
    return items

# ✅ Recommended: Callable type hints
def register_callback(
    callback: Callable[[str], int]
) -> None:
    """Register a callback"""
    pass

# ✅ Recommended: Generator type hints
def generate_numbers(n: int) -> Iterator[int]:
    """Generate numbers"""
    i = 0
    while i < n:
        yield i
        i += 1

# ❌ Not recommended: types from typing module
# from typing import Optional, List, Dict
# def get_user(db: Session, user_id: int) -> Optional[User]:
#     pass
```

### Context managers
**Always use with statement for file operations**

```python
# Good
with open("file.txt") as f:
    content = f.read()

# Bad
f = open("file.txt")
content = f.read()
f.close()
```

### Docstrings
**Write Docstrings for all functions and classes**

```python
def calculate_total(items: list[Item]) -> Decimal:
    """
    Calculate total price of items.

    Args:
        items: List of items

    Returns:
        Decimal: Total price

    Example:
        >>> items = [Item(price=100), Item(price=200)]
        >>> calculate_total(items)
        Decimal('300.00')
    """
    return sum(item.price for item in items)
```

---

## 🚀 FastAPI Best Practices

### 1. Utilizing Dependency Injection

```python
from fastapi import Depends
from sqlalchemy.orm import Session

# Database session
def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Authentication
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    # Token verification logic
    return user

# Usage in endpoint
@app.get("/items/")
async def read_items(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Item).all()
```

### 2. Separation of Pydantic schemas

```python
# schemas/item.py
from pydantic import BaseModel, Field

class ItemBase(BaseModel):
    """Common fields"""
    name: str = Field(..., max_length=100)
    description: str | None = None

class ItemCreate(ItemBase):
    """Schema for creation"""
    price: Decimal = Field(..., gt=0)

class ItemUpdate(BaseModel):
    """Schema for update (all fields optional)"""
    name: str | None = None
    description: str | None = None
    price: Decimal | None = None

class ItemResponse(ItemBase):
    """Response schema"""
    id: int
    price: Decimal
    created_at: datetime

    model_config = {"from_attributes": True}
```

### 3. Separation of business logic

```python
# services/item_service.py
def create_item(db: Session, item_data: ItemCreate) -> Item:
    """
    Create an item.

    Business logic is placed in the service layer.
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
    Endpoint handles routing only.
    Business logic is delegated to the service layer.
    """
    return create_item(db, item_data)
```

### 4. Appropriate HTTP status codes

```python
from fastapi import status

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_item(...):
    """Create: 201 Created"""
    pass

@router.get("/{id}")
async def get_item(...):
    """Retrieve: 200 OK"""
    pass

@router.put("/{id}")
async def update_item(...):
    """Update: 200 OK"""
    pass

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(...):
    """Delete: 204 No Content"""
    pass
```

### 5. Error handling

```python
from fastapi import HTTPException, status

def get_item(db: Session, item_id: int) -> Item:
    """Get an item"""
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item {item_id} not found"
        )
    return item
```

---

## 🗄️ SQLAlchemy Best Practices

**Context7 Reference**: `/sqlalchemy/sqlalchemy` (Code Snippets: 2830)

### 1. Modern Declarative Mapping

**Recommended: use Mapped and mapped_column**

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
    # For optional fields, use Optional type
    description: Mapped[Optional[str]] = mapped_column(String(500))
```

### 2. Connection and transaction management

**Use context managers**

```python
from sqlalchemy import create_engine

engine = create_engine("postgresql://user:pass@localhost/db")

# Recommended: manage transactions with context managers
with engine.begin() as conn:
    conn.execute(table.insert(), parameters)
    result = conn.execute(table.select())
    conn.execute(table.update(), parameters)
```

### 3. Performance optimization

**Select only specific columns**

```python
from sqlalchemy import select

# ✅ Recommended: select only required columns
stmt = select(User.id, User.name)
result = session.execute(stmt)

# ❌ Not recommended: selecting all columns when not needed
stmt = select(User)
```

**Repeated queries with cache utilization**

```python
def run_my_statement(connection, parameter):
    """Use SQL compilation cache"""
    stmt = select(table)
    stmt = stmt.where(table.c.col == parameter)
    stmt = stmt.order_by(table.c.id)
    return connection.execute(stmt)
```

### 4. Relationship JOIN

**Recommended JOIN patterns**

```python
from sqlalchemy.orm import Session

# ✅ Recommended: specify relationship directly
q = session.query(User).join(User.addresses).filter(Address.email_address == "ed@foo.com")

# ✅ Recommended: specify target explicitly
q = (
    session.query(User)
    .join(Address, User.addresses)
    .filter(Address.email_address == "ed@foo.com")
)
```

### 5. Table and column naming conventions

```python
# Use lower_case_snake
# Table names are singular
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

# Related tables use module prefix
class PaymentAccount(Base):
    __tablename__ = "payment_account"

class PaymentBill(Base):
    __tablename__ = "payment_bill"
```

### 6. Index naming conventions

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

## 🧪 Pytest Best Practices

**Context7 Reference**: `/pytest-dev/pytest` (Trust Score: 9.5)

### 1. Basic parameterized tests

```python
import pytest

@pytest.mark.parametrize(
    "test_input,expected",
    [
        ("3+5", 8),
        ("2+4", 6),
        pytest.param("6*9", 42, marks=pytest.mark.xfail),  # Expected failure
    ],
)
def test_eval(test_input, expected):
    assert eval(test_input) == expected
```

### 2. Fixture parameterization

```python
import pytest

@pytest.fixture(params=[0, 1], ids=["spam", "ham"])
def data_set(request):
    """Parameterized fixture"""
    return request.param

def test_data(data_set):
    """data_set runs twice, with 0 and 1"""
    pass
```

### 3. Scoped fixtures

```python
import pytest

@pytest.fixture(scope="module", params=["mod1", "mod2"])
def modarg(request):
    """Module-scoped fixture"""
    param = request.param
    print(f"  SETUP modarg {param}")
    yield param
    print(f"  TEARDOWN modarg {param}")

@pytest.fixture(scope="function", params=[1, 2])
def otherarg(request):
    """Function-scoped fixture"""
    param = request.param
    print(f"  SETUP otherarg {param}")
    yield param
    print(f"  TEARDOWN otherarg {param}")

def test_example(modarg, otherarg):
    """Use fixtures with multiple scopes"""
    print(f"  RUN test with modarg {modarg} and otherarg {otherarg}")
```

### 4. Indirect parameterization

```python
import pytest

@pytest.fixture
def fixt(request):
    """Process parameters in fixture"""
    return request.param * 3

@pytest.mark.parametrize("fixt", ["a", "b"], indirect=True)
def test_indirect(fixt):
    """Pass parameters via fixture"""
    assert len(fixt) == 3
```

### 5. Class-level parameterization

```python
import pytest

@pytest.mark.parametrize("n,expected", [(1, 2), (3, 4)])
class TestClass:
    """Apply parameters to the entire class"""

    def test_simple_case(self, n, expected):
        assert n + 1 == expected

    def test_weird_simple_case(self, n, expected):
        assert (n * 1) + 1 == expected
```

### 6. Module-level parameterization

```python
import pytest

# Apply parameters to the entire module
pytestmark = pytest.mark.parametrize("n,expected", [(1, 2), (3, 4)])

class TestClass:
    def test_simple_case(self, n, expected):
        assert n + 1 == expected

    def test_weird_simple_case(self, n, expected):
        assert (n * 1) + 1 == expected
```

### 7. Overriding fixtures

```python
# conftest.py
import pytest

@pytest.fixture(params=['one', 'two', 'three'])
def parametrized_username(request):
    return request.param

# test_something.py
@pytest.fixture
def parametrized_username():
    """Override fixture in a specific test module"""
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
    """Test main endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"msg": "Hello World"}

def test_create_item():
    """Test item creation"""
    response = client.post(
        "/items/",
        json={"name": "Test Item", "price": 100}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Item"
    assert "id" in data
```

### 9. Asynchronous tests

```python
import pytest
from httpx import AsyncClient, ASGITransport

@pytest.mark.anyio
async def test_async_endpoint():
    """Test asynchronous endpoint"""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        response = await client.get("/async-endpoint")
        assert response.status_code == 200
```

### 10. Fixtures for database tests

```python
# conftest.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

@pytest.fixture(scope="function")
def test_db():
    """Database session for tests"""
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
    """Obtain authentication token"""
    response = test_client.post(
        "/auth/token",
        data={"username": "test@example.com", "password": "password"}
    )
    return response.json()["access_token"]
```

---

## 🔍 Mypy Type Checking Configuration

**Context7 Reference**: `/python/mypy` (Trust Score: 8.9)

### 1. mypy.ini configuration file

**Recommended strict-mode settings**

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

# Plugins
plugins = pydantic.mypy, sqlalchemy.ext.mypy.plugin

# Exclude patterns
exclude = (?x)(
    ^\.venv/
    | ^venv/
    | ^build/
    | ^dist/
  )

# When third-party libraries have no type stubs
[mypy-some_untyped_library.*]
ignore_missing_imports = True
```

### 2. Running type checks

```bash
# Check all files
mypy .

# Check a specific directory
mypy app/

# Run in strict mode
mypy --strict app/

# Generate HTML report
mypy --html-report ./mypy-report app/
```

### 3. Best practices for type hints

**Modern type hint syntax**

```python
from __future__ import annotations

from collections.abc import Sequence, Mapping, Callable
from typing import Protocol, TypeVar

# ✅ Recommended: use collections.abc
def process_items(items: Sequence[str]) -> list[int]:
    return [len(item) for item in items]

# ✅ Recommended: X | None syntax
def find_user(user_id: int) -> User | None:
    return db.query(User).get(user_id)

# ✅ Recommended: express Union types with |
def parse_value(value: str | int | float) -> float:
    return float(value)

# ✅ Recommended: use Protocol for structural subtyping
class Closeable(Protocol):
    def close(self) -> None: ...

def close_all(items: Sequence[Closeable]) -> None:
    for item in items:
        item.close()

# ✅ Recommended: define generics with TypeVar
T = TypeVar('T')

def first(items: Sequence[T]) -> T | None:
    return items[0] if items else None
```

**Type annotations for empty collections**

```python
# ✅ Recommended: explicit type annotations
items: list[str] = []
mapping: dict[str, int] = {}

# ❌ Not recommended: no type annotation (Mypy cannot infer)
# items = []  # Mypy error
```

---

## ⚙️ Configuration Management

### Using Pydantic Settings

```python
# config.py
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    """Application settings"""
    app_name: str = "NecoKeeper"
    debug: bool = False
    secret_key: str
    database_url: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

@lru_cache()
def get_settings() -> Settings:
    """Get settings instance (with cache)"""
    return Settings()

# Usage example
settings = get_settings()
```

### Overriding settings in tests

```python
def get_settings_override():
    return Settings(
        database_url="sqlite:///:memory:",
        secret_key="test-secret-key"
    )

app.dependency_overrides[get_settings] = get_settings_override
```

---

## 📝 Alembic Migration Best Practices

**Context7 Reference**: `/sqlalchemy/alembic` (Code Snippets: 363)

### 1. Naming conventions

**alembic.ini configuration**

```ini
# alembic.ini
[alembic]
script_location = alembic

# Migration file name template
file_template = %%(year)d%%(month).2d%%(day).2d_%%(hour).2d%%(minute).2d_%%(slug)s

# Or date only
# file_template = %%(year)d-%%(month).2d-%%(day).2d_%%(slug)s
```

**Integrating MetaData naming conventions**

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

### 2. Best practices for migration naming

```bash
# ✅ Good examples: descriptive and actionable names
alembic revision -m "create_user_table"
alembic revision -m "add_email_index_to_users"
alembic revision -m "add_created_at_to_posts"
alembic revision -m "remove_deprecated_status_column"

# ❌ Bad examples: ambiguous names
alembic revision -m "update"
alembic revision -m "fix"
alembic revision -m "changes"
```

### 3. Creating and dropping constraints

**Constraint operations with naming conventions**

```python
def upgrade():
    """Create constraint (naming convention applied automatically)"""
    op.create_unique_constraint(
        op.f('uq_const_x'),  # Explicitly specify name with op.f()
        'some_table',
        'x'
    )

def downgrade():
    """Drop constraint"""
    op.drop_constraint("some_check_const", "t1", type_="check")

    # Or bypass naming convention
    op.drop_constraint(op.f("some_check_const"), "t1", type_="check")
```

**Naming conventions with batch operations**

```python
def upgrade():
    """Drop foreign key with batch operation"""
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

### 4. Schema management

**Configuring include_name hook**

```python
# env.py
def include_name(name, type_, parent_names):
    """Control inclusion of schemas and tables"""
    if type_ == "schema":
        return name in [None, "schema_one", "schema_two"]
    elif type_ == "table":
        # Use schema_qualified_table_name directly
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

### 5. Migration best practices

1. **Static migrations**: avoid dynamic data manipulation
2. **Reversible**: always implement a downgrade function
3. **Descriptive names**: use names that describe the migration
4. **Consistent naming**: unify MetaData naming conventions with Alembic
5. **Batch operations**: use batch operations appropriately for large tables

---

## 🔒 Security

### Password Hashing

```python
from argon2 import PasswordHasher

ph = PasswordHasher()

# Hashing
hashed = ph.hash("password123")

# Verification
try:
    ph.verify(hashed, "password123")
    print("Valid password")
except:
    print("Invalid password")
```

### JWT authentication

```python
from datetime import datetime, timedelta
import jwt

def create_access_token(data: dict) -> str:
    """Generate a JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=2)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
```

---

## 📊 Performance

### Avoiding N+1 Problem

```python
# Bad: N+1 query problem
users = db.query(User).all()
for user in users:
    print(user.posts)  # Executes a query per user

# Good: eager loading
from sqlalchemy.orm import joinedload

users = db.query(User).options(joinedload(User.posts)).all()
for user in users:
    print(user.posts)  # Fetched with a single query
```

### Pagination

```python
def get_items(
    db: Session,
    skip: int = 0,
    limit: int = 100
) -> list[Item]:
    """Get items with pagination"""
    return db.query(Item).offset(skip).limit(limit).all()
```

---

## 🚨 Checklist

Verify the following when creating or modifying code:

### 🔴 Mandatory checks after implementation (run before committing)

**After all tasks are implemented, run the following in order before committing:**

1. **Code formatting**
   ```bash
   ruff format .
   ```

2. **Run tests**
   ```bash
   python -m pytest
   ```
    - Confirm all tests pass
    - For new implementations, confirm coverage is 70% or higher

3. **For UI work: verify in Chrome DevTools**
    - Start dev server: `uvicorn app.main:app --reload`
    - Access in browser: `http://localhost:8000`
    - In Chrome DevTools (F12), check:
        - Console: no JavaScript errors
        - Network: API requests work correctly
        - Application: PWA features (Service Worker, Cache) work
        - Lighthouse: performance and accessibility scores
    - Mobile view: use device mode in DevTools
    - Responsive design: adjust viewport width and verify

4. **Git commit**
   ```bash
   git add .
    git commit -m "feat(scope): add feature"
   ```

### Basic checks
- [ ] Run `ruff format .`
- [ ] Run `ruff check . --fix`
- [ ] All tests pass (`python -m pytest`)
- [ ] For UI work: Chrome DevTools verification completed
- [ ] Run Mypy type checks (`mypy .`)
- [ ] Type hints added (`from __future__ import annotations` used)
- [ ] Docstrings written
- [ ] Error handling implemented
- [ ] No deprecated libraries in use
- [ ] No security issues
- [ ] Performance considerations addressed

### Type hint checks
- [ ] Use `collections.abc` types (not `typing` module)
- [ ] Use `X | None` syntax (not `Optional[X]`)
- [ ] Use `X | Y` syntax (not `Union[X, Y]`)
- [ ] Add explicit type annotations for empty collections
- [ ] Use `Protocol` for structural subtyping
- [ ] Use `from __future__ import annotations` for forward references

### SQLAlchemy checks
- [ ] Use modern `Mapped` and `mapped_column`
- [ ] Manage transactions with context managers
- [ ] Select only required columns for performance
- [ ] Use appropriate JOIN patterns
- [ ] Follow naming conventions for indexes and constraints

### Pytest checks
- [ ] Use appropriate fixture scopes
- [ ] Cover multiple cases with parameterized tests
- [ ] Explicitly specify test IDs (for readability)
- [ ] Use indirect parameterization for complex setups
- [ ] Appropriately override fixtures when needed

### Alembic checks
- [ ] Use descriptive migration names
- [ ] Implement both `upgrade()` and `downgrade()`
- [ ] Integrate naming conventions with MetaData
- [ ] Explicitly specify constraint names with `op.f()`
- [ ] Use the `include_name` hook for schema management

---

## 📚 References

### Official Documentation
- [FastAPI official documentation](https://fastapi.tiangolo.com/)
- [Pydantic official documentation](https://docs.pydantic.dev/)
- [SQLAlchemy official documentation](https://docs.sqlalchemy.org/)
- [Alembic official documentation](https://alembic.sqlalchemy.org/)
- [Pytest official documentation](https://docs.pytest.org/)
- [Ruff official documentation](https://docs.astral.sh/ruff/)

### Context7 verified resources
- [FastAPI](https://github.com/fastapi/fastapi) - Trust Score: 9.9
- [FastAPI Best Practices](https://github.com/zhanymkanov/fastapi-best-practices) - Trust Score: 8.8
- [Pytest](https://github.com/pytest-dev/pytest) - Trust Score: 9.5
- [SQLAlchemy](https://github.com/sqlalchemy/sqlalchemy) - Code Snippets: 2830
- [Alembic](https://github.com/sqlalchemy/alembic) - Code Snippets: 363
- [Python Typing](https://github.com/python/typing) - Trust Score: 8.9
- [Mypy](https://github.com/python/mypy) - Trust Score: 8.9

---

**Last updated**: 2025-11-12
**Context7 verified**: ✅

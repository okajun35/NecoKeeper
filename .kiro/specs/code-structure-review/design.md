# コード構造レビューと改善 - 設計ドキュメント

## Overview

NecoKeeperプロジェクトの現在のコード構造をFastAPI/SQLAlchemy/Pytest/Alembic/Mypyのベストプラクティスに沿って改善します。このドキュメントでは、各要件に対する具体的な技術的アプローチと実装計画を定義します。

## Architecture

### 現在の構造分析

```
app/
├── api/v1/          ✅ 良好 - APIバージョン管理
├── auth/            ✅ 良好 - 認証・認可
├── db/              ⚠️  空ディレクトリ - 削除候補
├── middleware/      ⚠️  ほぼ空 - 必要に応じて整理
├── models/          ✅ 良好 - SQLAlchemyモデル
├── schemas/         ✅ 良好 - Pydanticスキーマ
├── services/        ✅ 良好 - ビジネスロジック
├── static/          ✅ 良好 - 静的ファイル
├── tasks/           ⚠️  空ディレクトリ - 削除候補
├── templates/       ✅ 良好 - テンプレート（使用中）
├── utils/           ✅ 良好 - ユーティリティ
├── config.py        ✅ 良好 - 設定管理
├── database.py      🔧 要改善 - 命名規則追加
└── main.py          ✅ 良好 - エントリーポイント

tests/
├── api/             ✅ 良好 - APIテスト
├── auth/            ✅ 良好 - 認証テスト
├── models/          ✅ 良好 - モデルテスト
└── conftest.py      ✅ 良好 - テストフィクスチャ
```

### 改善後の構造

```
app/
├── api/v1/          # APIエンドポイント
├── auth/            # 認証・認可
├── models/          # SQLAlchemyモデル（改善版）
├── schemas/         # Pydanticスキーマ
├── services/        # ビジネスロジック（拡充）
├── static/          # 静的ファイル
├── templates/       # Jinjaテンプレート
├── utils/           # ユーティリティ
├── config.py        # 設定管理
├── database.py      # データベース接続（改善版）
└── main.py          # エントリーポイント

tests/
├── api/             # APIテスト
├── auth/            # 認証テスト
├── models/          # モデルテスト
├── services/        # サービステスト（追加）
└── conftest.py      # テストフィクスチャ（改善版）

# 新規追加
mypy.ini             # Mypy設定ファイル
.mypy_cache/         # Mypyキャッシュ（.gitignore）
```

## Components and Interfaces

### 1. データベースモジュール改善 (app/database.py)

**現在の問題点:**
- 命名規則が未設定
- モデルのインポートが明示的でない
- Base クラスに命名規則が含まれていない

**改善アプローチ:**

```python
from __future__ import annotations

from collections.abc import Generator

from sqlalchemy import MetaData, create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import get_settings

settings = get_settings()

# PostgreSQL互換の命名規則
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

# SQLAlchemyエンジンの作成
engine = create_engine(
    settings.database_url,
    echo=settings.database_echo,
    connect_args={"check_same_thread": False}
    if "sqlite" in settings.database_url
    else {},
)

# セッションファクトリーの作成
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """SQLAlchemy Declarative Base with naming convention"""
    
    metadata = MetaData(naming_convention=NAMING_CONVENTION)


def get_db() -> Generator[Session, None, None]:
    """データベースセッションの依存性注入用ジェネレーター"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### 2. モデル改善パターン

**現在の問題点:**
- 一部のモデルで `server_default` と `onupdate` の使用が不一致
- Optional型ヒントが明示的でない箇所がある

**改善パターン:**

```python
from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ImprovedModel(Base):
    """改善されたモデルパターン"""
    
    __tablename__ = "improved_model"
    
    # 主キー
    id: Mapped[int] = mapped_column(primary_key=True)
    
    # 必須フィールド
    name: Mapped[str] = mapped_column(String(100))
    
    # オプショナルフィールド（明示的にOptional型を使用）
    description: Mapped[Optional[str]] = mapped_column(String(500))
    
    # タイムスタンプ（server_defaultとonupdateを使用）
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        comment="作成日時"
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        comment="更新日時"
    )
```

### 3. Alembic env.py 改善

**現在の問題点:**
- モデルのインポートがコメントアウトされている
- 命名規則の統合が不完全

**改善アプローチ:**

```python
from __future__ import annotations

from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context
from app.config import get_settings
from app.database import Base

# すべてのモデルを明示的にインポート（Base.metadataに登録）
from app.models import (
    AdoptionRecord,
    Animal,
    AnimalImage,
    Applicant,
    AuditLog,
    CareLog,
    MedicalAction,
    MedicalRecord,
    Setting,
    StatusHistory,
    User,
    Volunteer,
)

config = context.config
settings = get_settings()
config.set_main_option("sqlalchemy.url", settings.database_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()
```

### 4. 型ヒント改善パターン

**全ファイルに適用する改善:**

```python
from __future__ import annotations  # すべてのファイルの先頭に追加

from collections.abc import Sequence, Iterator, Callable
from typing import Protocol

# ✅ 推奨パターン
def get_items(db: Session, skip: int = 0, limit: int = 100) -> list[Item]:
    """アイテム一覧を取得"""
    return db.query(Item).offset(skip).limit(limit).all()

def find_user(user_id: int) -> User | None:
    """ユーザーを検索"""
    return db.query(User).get(user_id)

def process_values(values: str | int | float) -> float:
    """値を処理"""
    return float(values)

# 空のコレクションには明示的な型注釈
def collect_items() -> list[Item]:
    items: list[Item] = []
    for i in range(10):
        items.append(Item(id=i))
    return items
```

### 5. Mypy設定ファイル

**新規作成: mypy.ini**

```ini
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
    | ^alembic/versions/
  )

# サードパーティライブラリ
[mypy-pytest.*]
ignore_missing_imports = True

[mypy-argon2.*]
ignore_missing_imports = True
```

## Data Models

### モデル改善の優先順位

**Phase 1: 基盤モデル（高優先度）**
1. `User` - ユーザー管理の基盤
2. `Animal` - 猫管理の基盤
3. `CareLog` - 世話記録

**Phase 2: 関連モデル（中優先度）**
4. `MedicalRecord` - 医療記録
5. `MedicalAction` - 医療処置
6. `StatusHistory` - ステータス履歴
7. `AnimalImage` - 猫の画像

**Phase 3: 拡張モデル（低優先度）**
8. `AdoptionRecord` - 譲渡記録
9. `Applicant` - 里親希望者
10. `Volunteer` - ボランティア
11. `Setting` - 設定
12. `AuditLog` - 監査ログ

### 各モデルの改善ポイント

**共通改善:**
- `from __future__ import annotations` を追加
- `Optional[type]` を明示的に使用
- `server_default=func.now()` を使用
- `onupdate=func.now()` を使用
- 型ヒントを `collections.abc` から使用

## Error Handling

### サービス層のエラーハンドリングパターン

```python
from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

import logging

logger = logging.getLogger(__name__)


def create_animal(
    db: Session,
    animal_data: AnimalCreate,
    user_id: int
) -> Animal:
    """
    猫を作成
    
    Args:
        db: データベースセッション
        animal_data: 猫作成データ
        user_id: 作成ユーザーID
        
    Returns:
        Animal: 作成された猫
        
    Raises:
        HTTPException: データベースエラーまたはバリデーションエラー
    """
    try:
        animal = Animal(**animal_data.model_dump())
        db.add(animal)
        db.commit()
        db.refresh(animal)
        return animal
        
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Integrity error creating animal: {e}")
        
        if "unique constraint" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="この猫は既に登録されています"
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="データの整合性エラーが発生しました"
        )
        
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error creating animal: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="データベースエラーが発生しました"
        )
```

## Testing Strategy

### テストフィクスチャの改善

```python
from __future__ import annotations

import pytest
from collections.abc import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.main import app


@pytest.fixture(scope="session")
def test_engine():
    """テスト用エンジン（セッションスコープ）"""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)


@pytest.fixture(scope="function")
def test_db(test_engine) -> Generator[Session, None, None]:
    """テスト用データベースセッション（関数スコープ）"""
    TestingSessionLocal = sessionmaker(
        bind=test_engine,
        autocommit=False,
        autoflush=False,
    )
    
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.rollback()
        db.close()


@pytest.fixture(scope="function")
def test_client(test_db: Session) -> TestClient:
    """テストクライアント"""
    def override_get_db():
        try:
            yield test_db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)
```

## Implementation Plan

### Phase 1: 基盤整備（優先度: 高）

1. **mypy.ini 作成**
   - Strict mode設定
   - プラグイン設定
   - 除外パターン設定

2. **app/database.py 改善**
   - 命名規則の追加
   - Base クラスの改善
   - 型ヒントの改善

3. **alembic/env.py 改善**
   - モデルの明示的インポート
   - 命名規則の統合
   - 型ヒントの追加

4. **未使用ディレクトリの削除**
   - `app/db/` 削除
   - `app/tasks/` 削除（または将来の使用計画を確認）

### Phase 2: モデル改善（優先度: 高）

5. **基盤モデルの改善**
   - `app/models/user.py`
   - `app/models/animal.py`
   - `app/models/care_log.py`

6. **関連モデルの改善**
   - `app/models/medical_record.py`
   - `app/models/medical_action.py`
   - その他のモデル

### Phase 3: API・サービス層改善（優先度: 中）

7. **サービス層の改善**
   - エラーハンドリングの統一
   - 型ヒントの改善
   - ロギングの追加

8. **APIエンドポイントの改善**
   - 型ヒントの改善
   - ドキュメントの充実

### Phase 4: テスト改善（優先度: 中）

9. **テストフィクスチャの改善**
   - スコープの最適化
   - パラメータ化の活用

10. **テストカバレッジの向上**
    - サービス層のテスト追加
    - エッジケースのテスト追加

### Phase 5: 検証とドキュメント（優先度: 低）

11. **型チェックの実行**
    - `mypy .` の実行
    - エラーの修正

12. **ドキュメントの更新**
    - README.md の更新
    - 開発ガイドの作成

## Design Decisions

### 1. 命名規則の選択

**決定:** PostgreSQL互換の命名規則を採用

**理由:**
- 将来的にPostgreSQLへの移行を考慮
- 一貫性のある制約名
- Alembicとの統合が容易

### 2. 型ヒント構文の選択

**決定:** Python 3.10+ の新しい構文を採用

**理由:**
- `X | None` は `Optional[X]` より読みやすい
- `collections.abc` は `typing` より推奨される
- `from __future__ import annotations` で前方参照を解決

### 3. Mypy Strict Mode の採用

**決定:** Strict mode を有効化

**理由:**
- 型安全性の最大化
- 早期のバグ検出
- IDEサポートの向上

### 4. テストフィクスチャのスコープ

**決定:** 関数スコープを基本とし、必要に応じてモジュール/セッションスコープを使用

**理由:**
- テストの独立性を保証
- データの汚染を防止
- パフォーマンスとのバランス

## Migration Strategy

### データベースマイグレーション

1. **新しいマイグレーションの作成**
   ```bash
   alembic revision --autogenerate -m "add_naming_convention"
   ```

2. **マイグレーションの確認**
   - 生成されたマイグレーションファイルを確認
   - upgrade() と downgrade() の両方を実装

3. **マイグレーションの適用**
   ```bash
   alembic upgrade head
   ```

### コード移行の順序

1. 基盤ファイル（database.py, env.py）
2. モデルファイル（優先度順）
3. サービスファイル
4. APIエンドポイント
5. テストファイル

各ステップで以下を実行：
- Ruff でフォーマット
- Mypy で型チェック
- Pytest でテスト実行

## Risks and Mitigation

### リスク1: 既存のマイグレーションとの互換性

**リスク:** 命名規則の変更が既存のマイグレーションに影響

**対策:**
- 新しいマイグレーションで命名規則を適用
- 既存のテーブルは変更しない
- 段階的な移行

### リスク2: 型チェックエラーの大量発生

**リスク:** Strict mode で多数のエラーが発生

**対策:**
- ファイル単位で段階的に修正
- `# type: ignore` を一時的に使用
- 優先度の高いファイルから修正

### リスク3: テストの失敗

**リスク:** 変更によりテストが失敗

**対策:**
- 各変更後にテストを実行
- テストを先に修正
- CI/CDパイプラインで自動検証

## Success Criteria

### 完了条件

1. ✅ mypy.ini が作成され、`mypy .` がエラーなく実行される
2. ✅ すべてのモデルが改善されたパターンに従っている
3. ✅ alembic/env.py がすべてのモデルをインポートしている
4. ✅ app/database.py に命名規則が設定されている
5. ✅ 未使用ディレクトリが削除されている
6. ✅ すべてのテストがパスする
7. ✅ Ruff でフォーマットエラーがない
8. ✅ ドキュメントが更新されている

### 品質指標

- **型カバレッジ:** 95%以上
- **テストカバレッジ:** 80%以上
- **Mypy エラー:** 0件
- **Ruff エラー:** 0件
- **Pytest 成功率:** 100%

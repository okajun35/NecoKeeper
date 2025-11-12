# コード構造レビューと改善

## Introduction

NecoKeeperプロジェクトの現在のコード構造をFastAPI/SQLAlchemy/Pytest/Alembicのベストプラクティスに照らし合わせてレビューし、必要な改善を実施します。

## Glossary

- **System**: NecoKeeperアプリケーション全体
- **Database Module**: app/database.pyモジュール
- **Model**: SQLAlchemyのORMモデルクラス
- **Schema**: Pydanticのバリデーションスキーマ
- **API Endpoint**: FastAPIのルーターエンドポイント
- **Test Fixture**: Pytestのフィクスチャ関数

## Requirements

### Requirement 1: データベースモジュールの改善

**User Story:** As a developer, I want the database module to follow SQLAlchemy 2.0+ best practices, so that the code is maintainable and performant.

#### Acceptance Criteria

1. WHEN the Database Module is initialized, THE System SHALL use modern SQLAlchemy 2.0+ patterns with `Mapped` and `mapped_column`
2. WHEN the Database Module creates a naming convention, THE System SHALL use the recommended PostgreSQL-compatible naming convention
3. WHEN the Database Module provides a session, THE System SHALL use context managers for transaction management
4. WHERE the database is SQLite, THE System SHALL configure appropriate connection arguments
5. WHEN models are imported, THE System SHALL ensure all models are registered with Base.metadata before table creation

### Requirement 2: モデルの改善

**User Story:** As a developer, I want all models to follow modern SQLAlchemy patterns, so that type safety and IDE support are maximized.

#### Acceptance Criteria

1. WHEN a Model defines timestamp fields, THE System SHALL use `server_default=func.now()` instead of Python datetime functions
2. WHEN a Model defines an update timestamp, THE System SHALL use `onupdate=func.now()` for automatic updates
3. WHEN a Model uses Optional fields, THE System SHALL explicitly use `Optional[type]` type hints
4. WHEN a Model defines relationships, THE System SHALL use modern `Mapped` type hints
5. THE System SHALL NOT use deprecated `Column()` syntax in any model

### Requirement 3: APIエンドポイントの改善

**User Story:** As a developer, I want API endpoints to follow FastAPI best practices, so that the API is consistent and well-documented.

#### Acceptance Criteria

1. WHEN an API router is defined, THE System SHALL use consistent prefix and tags
2. WHEN an API endpoint returns data, THE System SHALL use appropriate response_model
3. WHEN an API endpoint modifies data, THE System SHALL use appropriate HTTP status codes (201 for creation, 204 for deletion)
4. WHEN an API endpoint has dependencies, THE System SHALL use `Annotated` type hints for clarity
5. WHEN business logic is needed, THE System SHALL delegate to service layer functions

### Requirement 4: テスト構造の改善

**User Story:** As a developer, I want tests to follow Pytest best practices, so that tests are maintainable and reliable.

#### Acceptance Criteria

1. WHEN test fixtures are defined, THE System SHALL use appropriate scope (function, module, session)
2. WHEN test database is needed, THE System SHALL use in-memory SQLite with StaticPool
3. WHEN test data is needed, THE System SHALL create minimal required data in fixtures
4. WHEN tests need authentication, THE System SHALL provide reusable auth_token fixture
5. WHEN tests are parametrized, THE System SHALL use `@pytest.mark.parametrize` with clear test IDs

### Requirement 5: Alembicマイグレーションの改善

**User Story:** As a developer, I want Alembic migrations to follow best practices, so that database schema changes are safe and reversible.

#### Acceptance Criteria

1. WHEN alembic.ini is configured, THE System SHALL use descriptive file_template with timestamps
2. WHEN env.py is configured, THE System SHALL import all models to ensure metadata is complete
3. WHEN migrations are created, THE System SHALL use descriptive names (e.g., "create_user_table")
4. WHEN constraints are created, THE System SHALL use `op.f()` for explicit naming
5. WHEN migrations are written, THE System SHALL implement both upgrade() and downgrade() functions

### Requirement 6: プロジェクト構造の整理

**User Story:** As a developer, I want the project structure to follow FastAPI conventions, so that the codebase is easy to navigate.

#### Acceptance Criteria

1. THE System SHALL organize code into clear layers: api, models, schemas, services, auth, utils
2. THE System SHALL NOT have unused directories (e.g., app/db, app/tasks, app/templates if not used)
3. WHEN static files exist, THE System SHALL organize them appropriately
4. WHEN tests exist, THE System SHALL mirror the app structure in tests directory
5. THE System SHALL have clear separation between API layer and business logic layer

### Requirement 7: 型ヒントとドキュメントの改善

**User Story:** As a developer, I want all functions to have proper type hints and docstrings, so that the code is self-documenting.

#### Acceptance Criteria

1. WHEN a function is defined, THE System SHALL include complete type hints for all parameters and return values
2. WHEN a function is defined, THE System SHALL include a docstring with description, Args, Returns, and Example sections
3. WHEN a class is defined, THE System SHALL include a docstring with Attributes section
4. WHEN complex logic exists, THE System SHALL include inline comments explaining the reasoning
5. THE System SHALL use `from __future__ import annotations` for forward references where needed

### Requirement 8: 型ヒントとMypy設定の改善

**User Story:** As a developer, I want comprehensive type hints and Mypy configuration, so that type errors are caught early and IDE support is maximized.

#### Acceptance Criteria

1. WHEN a function is defined, THE System SHALL use complete type hints with `collections.abc` types instead of `typing` module types
2. WHEN optional types are needed, THE System SHALL use `X | None` syntax (Python 3.10+) instead of `Optional[X]`
3. WHEN union types are needed, THE System SHALL use `X | Y` syntax instead of `Union[X, Y]`
4. WHEN forward references are needed, THE System SHALL use `from __future__ import annotations`
5. WHEN generic types are needed, THE System SHALL use modern generic syntax with `Protocol` and `TypeVar`
6. WHEN empty collections are initialized, THE System SHALL provide explicit type annotations
7. THE System SHALL have a mypy.ini configuration file with strict mode enabled
8. THE System SHALL pass `mypy --strict` checks without errors

### Requirement 9: エラーハンドリングの改善

**User Story:** As a developer, I want consistent error handling across the application, so that errors are properly logged and reported.

#### Acceptance Criteria

1. WHEN a database error occurs, THE System SHALL catch SQLAlchemyError and provide meaningful error messages
2. WHEN a validation error occurs, THE System SHALL use Pydantic validation with clear error messages
3. WHEN a resource is not found, THE System SHALL raise HTTPException with 404 status
4. WHEN authorization fails, THE System SHALL raise HTTPException with 403 status
5. WHEN an unexpected error occurs, THE System SHALL log the error and return a generic error message in production

# Implementation Plan

このドキュメントは、NecoKeeperシステムの実装タスクリストです。各タスクは段階的に実装可能で、前のタスクの成果物を活用します。

## 現在の状態

**プロジェクトステータス**: Phase 9 Public API完了、MVP Core バックエンド完成！

**完了済み:**
- ✅ Phase 1: プロジェクト基盤とデータベース（全11タスク）
- ✅ Phase 2: 認証・認可システム（全7タスク）
- ✅ Phase 3: 猫管理機能（全6タスク）
- ✅ Phase 4: 世話記録機能（全5タスク）
- ✅ Phase 4: ボランティア管理（全4タスク）
- ✅ Phase 6: PDF生成機能（全5タスク）
- ✅ Phase 9: Public API（Task 14.2完了）

**実装済み機能:**
- データベース（全12モデル）
- JWT認証・認可システム（RBAC、権限チェック）
- 猫管理機能（CRUD、検索、ステータス管理）
- 世話記録機能（CRUD、CSV出力、前回値コピー）
- ボランティア管理機能（CRUD、活動履歴）
- 画像アップロード・最適化・ギャラリー管理
- PDF生成機能（QRカード、面付けカード、紙記録フォーム）
- **Public API（認証不要の世話記録入力）**
- 統合テスト（232テスト、カバレッジ84.90%）

**次のステップ**: Phase 9 フロントエンド実装（Publicフォーム、PWA機能）またはPhase 5（診療記録機能）

**重要な注意事項:**

1. **Context7 MCP使用**: すべてのコード実装前に、Context7 MCPを使用して最新のライブラリドキュメントを参照すること

2. **コード品質基準（code-structure-review統合）**:
   - すべてのファイルに `from __future__ import annotations` を追加
   - 型ヒントは `collections.abc` を使用（`list[T]`, `dict[K, V]`, `Sequence[T]`, `Iterator[T]`）
   - Optional型は `X | None` 構文を使用（`Optional[X]` ではなく）
   - Union型は `X | Y` 構文を使用（`Union[X, Y]` ではなく）
   - 空のコレクションには明示的な型注釈を付与
   - SQLAlchemyモデルは `server_default=func.now()` と `onupdate=func.now()` を使用
   - エラーハンドリングを統一（HTTPException、ロギング）
   - すべての関数にDocstring（Args, Returns, Raises, Example）を記述

3. **Mypy strict mode**: すべてのコードは `mypy --strict` をパスすること

4. **テスト**: 実装と並行してテストを作成し、品質を担保すること

### Context7 MCP 使用方法
1. **ライブラリID解決**: `mcp_context7_resolve_library_id` でライブラリ名を検索
2. **ドキュメント取得**: `mcp_context7_get_library_docs` で最新ドキュメントを取得（tokens: 5000推奨）
3. **実装根拠**: 取得したドキュメントを一次根拠として設計・実装を行う
4. **バージョン確認**: 非推奨APIが疑われる場合は Context7 で再確認

## クイックスタートガイド

### 開発環境セットアップ（初回のみ）
```bash
# 1. 仮想環境作成
python -m venv .venv

# 2. 仮想環境アクティベート（Windows）
.venv\Scripts\activate

# 3. 依存関係インストール
pip install -r requirements.txt

# 4. 環境変数設定
# .env ファイルを作成し、必要な環境変数を設定
```

### タスク実行の流れ
1. 該当Phaseの「Context7 MCP使用ガイドライン」を確認
2. Context7 MCPで最新ドキュメントを取得
3. タスクを1つずつ実装
4. 実装完了後、チェックボックスをマーク
5. 次のタスクへ進む

## タスク実行の注意事項

- すべてのタスクは必須です（テスト含む）
- 各タスクは独立して実装可能ですが、依存関係に注意してください
- **必須**: Context7 MCPを使用して最新のライブラリドキュメントを参照すること
- 各Phase開始時に、該当するContext7ガイドラインを確認すること
- テストは実装と並行して作成し、品質を担保してください

## 実装優先順位

### 最優先（MVP Core）
1. ✅ Phase 1: プロジェクト基盤とデータベース
2. ✅ Phase 2: 認証・認可システム
3. ✅ Phase 3: 猫管理機能（基本CRUD）
4. ✅ Phase 4: 世話記録機能（基本入力）
5. ✅ Phase 6: PDF生成機能（QRカード）
6. Phase 9: Publicフォーム（基本入力）

### 高優先（MVP Extended）
7. Phase 5: 診療記録機能
8. Phase 7: 里親管理機能
9. Phase 8: 管理画面UI（基本画面）
10. Phase 11: セキュリティとログ

### 中優先（Enhancement）
11. Phase 10: 多言語対応
12. Phase 12: バックアップとデータ管理
13. Phase 15: デプロイとドキュメント

### 低優先（Optional）
14. Phase 13: OCR機能
15. Phase 14: ヘルプとサポート
16. Phase 16: パフォーマンス最適化とテスト
17. Phase 17: 最終調整とリリース

---

## Phase 1: プロジェクト基盤とデータベース ✅ 完了

**Context7 MCP使用ガイドライン**:
- 各タスク実装前に、必ず Context7 MCP を使用して最新ドキュメントを参照すること
- FastAPI実装: `mcp_context7_get_library_docs` で `/fastapi/fastapi` を参照（tokens: 5000）
- SQLAlchemy実装: `mcp_context7_get_library_docs` で `/sqlalchemy/sqlalchemy` を参照（tokens: 5000）
- Pydantic実装: `mcp_context7_get_library_docs` で `/pydantic/pydantic` を参照（tokens: 5000）
- WeasyPrint実装: `mcp_context7_resolve_library_id` で "WeasyPrint" を検索後、ドキュメント取得

**コード品質改善（code-structure-review統合）**:
- すべてのファイルに `from __future__ import annotations` を追加
- 型ヒントは `collections.abc` を使用（`list[T]`, `dict[K, V]`, `Sequence[T]`, `Iterator[T]`）
- Optional型は `X | None` 構文を使用（`Optional[X]` ではなく）
- Union型は `X | Y` 構文を使用（`Union[X, Y]` ではなく）
- 空のコレクションには明示的な型注釈を付与
- SQLAlchemyモデルは `server_default=func.now()` と `onupdate=func.now()` を使用
- データベースモジュールにPostgreSQL互換の命名規則を追加

### 1. プロジェクト構造とセットアップ

プロジェクトの基本構造を作成し、必要な依存関係をセットアップします。

- [x] 1.1 プロジェクトディレクトリ構造を作成
  - `app/`, `data/`, `media/`, `backups/`, `tests/` ディレクトリ
  - `app/models/`, `app/schemas/`, `app/api/`, `app/services/`, `app/auth/`, `app/templates/`, `app/static/` サブディレクトリ
  - _Requirements: 技術的制約1, 技術的制約2_

- [x] 1.2 requirements.txtを作成
  - FastAPI, SQLAlchemy, Pydantic, WeasyPrint, bcrypt, python-multipart, jinja2, qrcode, python-dotenv, alembic
  - テスト用: pytest, pytest-asyncio, httpx, faker
  - _Requirements: 技術的制約1_

- [x] 1.3 設定管理モジュールを実装（app/config.py）
  - 環境変数の読み込み（DATABASE_URL, SECRET_KEY, DEBUG, LOG_LEVEL）
  - Pydantic Settingsを使用した型安全な設定管理
  - _Requirements: Requirement 20.3_

- [x] 1.4 FastAPIアプリケーションのエントリーポイントを作成（app/main.py）
  - FastAPIインスタンス作成
  - CORSミドルウェア設定
  - 静的ファイル・テンプレート設定
  - _Requirements: 技術的制約1_

- [x] 1.5 開発環境のセットアップスクリプトを作成
  - 仮想環境作成、依存関係インストール、データベース初期化の自動化スクリプト
  - README.mdに手動セットアップ手順を記載
  - _Requirements: Requirement 31_

### 2. データベース設計と初期化

SQLiteデータベースとSQLAlchemyモデルを実装します。

- [x] 2.1 データベース接続モジュールを実装（app/database.py）
  - **Context7**: `/sqlalchemy/sqlalchemy` のドキュメントを参照（特にAsyncエンジン、セッション管理）
  - SQLAlchemyエンジン作成（create_engine with SQLite）
  - セッション管理（SessionLocal, get_db dependency）
  - Base クラス定義（DeclarativeBase）
  - データベースファイルパス: `settings.database_url` を使用
  - _Requirements: 技術的制約1_

- [x] 2.2 Animalsモデルを実装（app/models/animal.py）
  - **Context7**: SQLAlchemy 2.0のモデル定義方法を確認（Mapped, mapped_column）
  - 全カラム定義（id, name, photo, pattern, tail_length, collar, age, gender, ear_cut, features, status, protected_at, created_at, updated_at）
  - インデックス設定（status, protected_at, name）
  - デフォルト値設定（status='保護中', protected_at=CURRENT_DATE）
  - 型ヒント使用（Mapped[str], Mapped[Optional[str]]等）
  - _Requirements: Requirement 1.4, Requirement 15.1_

- [x] 2.3 CareLogモデルを実装（app/models/care_log.py）
  - 全カラム定義（id, animal_id, recorder_id, recorder_name, time_slot, appetite, energy, urination, cleaning, memo, ip_address, user_agent, device_tag, from_paper, created_at, last_updated_at, last_updated_by）
  - 外部キー設定（animal_id, last_updated_by）
  - インデックス設定（animal_id, created_at, recorder_id, time_slot）
  - _Requirements: Requirement 3.2, Requirement 3.6, Requirement 23.6_

- [x] 2.4 MedicalRecordモデルを実装（app/models/medical_record.py）
  - 全カラム定義（id, animal_id, vet_id, date, time_slot, weight, temperature, symptoms, medical_action_id, dosage（INTEGER型、回数）, other, comment, created_at, updated_at, last_updated_at, last_updated_by）
  - 外部キー設定（animal_id, vet_id, medical_action_id, last_updated_by）
  - インデックス設定（animal_id, date, vet_id, medical_action_id）
  - _Requirements: Requirement 5.2, Requirement 23.6_

- [x] 2.5 Usersモデルを実装（app/models/user.py）
  - 全カラム定義（id, email, password_hash, name, role, is_active, failed_login_count, locked_until, created_at, updated_at）
  - ユニークインデックス（email）
  - _Requirements: Requirement 21.6, Requirement 22.2_

- [x] 2.6 Volunteersモデルを実装（app/models/volunteer.py）
  - 全カラム定義（id, name, contact, affiliation, status, started_at, created_at, updated_at）
  - インデックス設定（status, name）
  - _Requirements: Requirement 4.1_

- [x] 2.7 Applicants, AdoptionRecord, StatusHistory, AuditLog, Sessions, Settingsモデルを実装
  - 各モデルの全カラム定義と外部キー設定
  - 適切なインデックス設定
  - _Requirements: Requirement 14, Requirement 15.2, Requirement 23.1_

- [x] 2.8 診療行為マスターモデルを実装（MedicalActions）
  - 全カラム定義（id, name, valid_from, valid_to, cost_price, selling_price, procedure_fee, currency, created_at, updated_at, last_updated_at, last_updated_by）
  - 期間別価格管理と通貨単位（JPY/USD）
  - インデックス設定（name, valid_from, valid_to）
  - _Requirements: Requirement 6.1, Requirement 6.2, Requirement 6.3_

- [x] 2.9 AnimalImagesモデルを実装（app/models/animal_image.py）
  - 全カラム定義（id, animal_id, image_path, taken_at, description, file_size, created_at）
  - 外部キー設定（animal_id）
  - _Requirements: Requirement 27.3_

- [x] 2.10 Alembicマイグレーション設定
  - **Context7**: Alembicの初期化と設定方法を確認
  - `alembic init alembic` コマンド実行
  - alembic.ini の設定（sqlalchemy.url）
  - env.py の設定（target_metadata = Base.metadata）
  - 初期マイグレーションスクリプト作成（`alembic revision --autogenerate -m "Initial migration"`）
  - _Requirements: 技術的制約1_

- [x] 2.11 ドメインモデルの単体テストを作成（DDD準拠）
  - ドメインオブジェクトのビジネスルールテスト
  - 値オブジェクトの不変性テスト
  - エンティティの同一性テスト
  - _Requirements: Requirement 28_


## Phase 2: 認証・認可システム（JWT + OAuth2） ✅ 完了

**Context7 MCP使用ガイドライン**:
- JWT実装前: `mcp_context7_get_library_docs` で `/fastapi/fastapi` のOAuth2/JWT関連ドキュメントを参照（tokens: 5000）
- passlib実装前: `mcp_context7_resolve_library_id` で "passlib" を検索し、ドキュメント取得
- python-jose実装前: `mcp_context7_resolve_library_id` で "python-jose" を検索し、ドキュメント取得

**コード品質改善（code-structure-review統合）**:
- すべての認証関連ファイルに型ヒント改善を適用
- エラーハンドリングパターンを統一（HTTPException、ロギング）
- Docstringを充実（Args, Returns, Raises, Example）

### 3. JWT認証機能の実装

JWT + OAuth2 Password Flowによる認証システムを実装します。

- [x] 3.1 パスワードハッシュ化ユーティリティを実装（app/auth/password.py）
  - **Context7**: passlib + bcryptの使用方法を確認
  - passlib.CryptContextを使用したハッシュ化・検証関数
  - パスワードポリシー検証（最小8文字、英数字混在）
  - _Requirements: Requirement 21.7, Requirement 22.1_

- [x] 3.2 JWT管理モジュールを実装（app/auth/jwt.py）
  - **Context7**: python-joseでのJWT生成・検証方法を確認
  - JWTアクセストークン生成関数（有効期限: 2時間）
  - JWTトークン検証関数
  - SECRET_KEY設定（環境変数から取得）
  - _Requirements: Requirement 21.3, Requirement 22.3, Requirement 22.8_

- [x] 3.3 認証依存性を実装（app/auth/dependencies.py）
  - **Context7**: FastAPIのOAuth2PasswordBearerの使用方法を確認
  - OAuth2PasswordBearerスキーム設定
  - get_current_user依存性（トークンからユーザー取得）
  - get_current_active_user依存性（アクティブユーザーのみ）
  - _Requirements: Requirement 21.3_

- [x] 3.4 ログイン試行回数制限を実装
  - 失敗回数のカウント（Usersテーブル）
  - 5回失敗後15分間ロック
  - _Requirements: Requirement 22.2_

- [x] 3.5 権限チェック依存性を実装（app/auth/permissions.py）
  - ロール別権限マトリクス定義
  - require_role依存性関数
  - require_permission依存性関数
  - _Requirements: Requirement 10.1-10.5_

- [x] 3.6 認証APIエンドポイントを実装（app/api/v1/auth.py）
  - **Context7**: FastAPIのOAuth2 Password Flowエンドポイント実装を確認
  - POST /api/v1/auth/token（ログイン、JWTトークン取得）
  - GET /api/v1/auth/me（現在のユーザー情報取得）
  - OAuth2PasswordRequestFormを使用
  - _Requirements: Requirement 21.1-21.4, Requirement 21.8-21.9_

- [x] 3.7 認証機能のテストを作成
  - パスワードハッシュ化のテスト
  - JWT生成・検証のテスト
  - 認証依存性のテスト
  - ログインAPIのテスト
  - 権限チェックのテスト
  - _Requirements: Requirement 22_

## Phase 3: 猫管理機能 ✅ 完了

**Context7 MCP使用ガイドライン**:
- Pydantic実装: `mcp_context7_get_library_docs` で `/pydantic/pydantic` を参照（tokens: 5000）
- SQLAlchemy実装: `mcp_context7_get_library_docs` で `/sqlalchemy/sqlalchemy` を参照（tokens: 5000）
- Pillow実装: `mcp_context7_get_library_docs` で `/python-pillow/Pillow` を参照（tokens: 5000）

**コード品質改善（code-structure-review統合）**:
- すべてのスキーマ、サービス、APIファイルに型ヒント改善を適用
- エラーハンドリングパターンを統一
- ロギングを追加

### 4. 猫マスター管理

猫の個体情報のCRUD機能を実装します。

- [x] 4.1 Pydanticスキーマを実装（app/schemas/animal.py）
  - AnimalCreate, AnimalUpdate, AnimalResponse
  - バリデーションルール（必須項目、形式チェック）
  - _Requirements: Requirement 1.2_

- [x] 4.2 猫管理サービスを実装（app/services/animal_service.py）
  - create_animal（猫登録）
  - get_animal（猫詳細取得）
  - update_animal（猫更新）
  - delete_animal（論理削除）
  - list_animals（一覧取得、ページネーション）
  - search_animals（検索）
  - _Requirements: Requirement 1.1-1.3, Requirement 1.5, Requirement 24.2_

- [x] 4.3 画像アップロード処理を実装（app/utils/image.py）
  - ファイル検証（拡張子、MIMEタイプ、サイズ）
  - 画像最適化（リサイズ、圧縮）
  - ファイル保存処理
  - _Requirements: Requirement 27.9, Requirement 27.10_

- [x] 4.4 猫管理APIエンドポイントを実装（app/api/v1/animals.py）
  - GET /api/v1/animals（一覧取得）
  - POST /api/v1/animals（登録）
  - GET /api/v1/animals/{id}（詳細取得）
  - PUT /api/v1/animals/{id}（更新）
  - DELETE /api/v1/animals/{id}（論理削除）
  - GET /api/v1/animals/search（検索）
  - _Requirements: Requirement 1, Requirement 24_

- [x] 4.5 ステータス管理機能を実装
  - ステータス変更処理
  - StatusHistory記録
  - ステータスフィルタリング
  - _Requirements: Requirement 15.2, Requirement 15.3, Requirement 15.6-15.7_

- [x] 4.6 猫管理のテストを作成（DDD準拠）
  - 猫ドメインオブジェクトの単体テスト（ステータス変更ルール等）
  - 猫管理アプリケーションサービスのテスト（ユースケース）
  - 猫リポジトリの統合テスト（永続化）
  - _Requirements: Requirement 1, Requirement 15_

### 5. 画像ギャラリー機能

**Context7 MCP使用ガイドライン**:
- Pillow実装: `mcp_context7_get_library_docs` で `/python-pillow/Pillow` を参照（tokens: 5000）
- ファイルアップロード: `mcp_context7_get_library_docs` で `/fastapi/fastapi` のFile Upload関連を参照

**コード品質改善**:
- 型ヒント: `from __future__ import annotations`, `X | None`, `collections.abc`
- エラーハンドリング: HTTPException、ロギング
- Docstring: Args, Returns, Raises, Example

猫の複数画像管理機能を実装します。

- [x] 5.1 画像ギャラリーサービスを実装（app/services/image_service.py）
  - upload_image（画像アップロード）
  - list_images（画像一覧取得）
  - delete_image（画像削除）
  - 枚数制限チェック
  - ファイルサイズ制限チェック
  - _Requirements: Requirement 27.2-27.3, Requirement 27.8-27.9_

- [x] 5.2 画像管理APIエンドポイントを実装（app/api/v1/images.py）
  - POST /api/v1/animals/{id}/images（画像アップロード）
  - GET /api/v1/animals/{id}/images（画像一覧取得）
  - DELETE /api/v1/images/{id}（画像削除）
  - _Requirements: Requirement 27.1-27.5_

- [x] 5.3 画像制限設定機能を実装
  - Settingsテーブルでの設定管理
  - デフォルト値（最大20枚、最大5MB）
  - _Requirements: Requirement 27.6-27.7, Requirement 27.10_


## Phase 4: 世話記録機能 ✅ 完了

**Context7 MCP使用ガイドライン**:
- CSV処理: `mcp_context7_resolve_library_id` で "pandas" または標準ライブラリ `csv` の使用を検討
- FastAPI実装: `mcp_context7_get_library_docs` で `/fastapi/fastapi` を参照（tokens: 5000）

**コード品質改善（code-structure-review統合）**:
- すべてのファイルに型ヒント改善を適用
- エラーハンドリングとロギングを統一

### 6. 世話記録管理

日々の世話記録のCRUD機能を実装します。

- [x] 6.1 Pydanticスキーマを実装（app/schemas/care_log.py）
  - CareLogCreate, CareLogUpdate, CareLogResponse
  - バリデーションルール（time_slot: 朝/昼/夕、appetite/energy: 1-5、urination/cleaning: boolean）
  - _Requirements: Requirement 3.2_

- [x] 6.2 世話記録サービスを実装（app/services/care_log_service.py）
  - create_care_log（記録登録）
  - get_care_log（記録詳細取得）
  - list_care_logs（一覧取得、フィルタリング）
  - export_care_logs_csv（CSV出力）
  - _Requirements: Requirement 3.5, Requirement 25.2-25.3_

- [x] 6.3 世話記録APIエンドポイントを実装（app/api/v1/care_logs.py）
  - GET /api/v1/care-logs（一覧取得）
  - POST /api/v1/care-logs（登録）
  - GET /api/v1/care-logs/{id}（詳細取得）
  - PUT /api/v1/care-logs/{id}（更新）
  - GET /api/v1/care-logs/export（CSV出力）
  - _Requirements: Requirement 3, Requirement 25_

- [x] 6.4 前回入力値コピー機能を実装
  - 最新の記録を取得
  - フロントエンドへのデータ提供
  - _Requirements: Requirement 3.7_

- [x] 6.5 世話記録機能の統合テストを作成
  - CRUD操作のテスト
  - CSV出力のテスト
  - _Requirements: Requirement 3, Requirement 25_

### 7. ボランティア管理 ✅ 完了

ボランティア記録者の管理機能を実装します。

- [x] 7.1 Pydanticスキーマを実装（app/schemas/volunteer.py）
  - VolunteerCreate, VolunteerUpdate, VolunteerResponse
  - _Requirements: Requirement 4.1_

- [x] 7.2 ボランティア管理サービスを実装（app/services/volunteer_service.py）
  - create_volunteer（登録）
  - get_volunteer（詳細取得）
  - list_volunteers（一覧取得）
  - update_volunteer（更新）
  - get_activity_history（活動履歴取得）
  - get_active_volunteers（アクティブボランティア一覧取得）
  - _Requirements: Requirement 4.2, Requirement 4.4, Requirement 4.5_

- [x] 7.3 ボランティア管理APIエンドポイントを実装（app/api/v1/volunteers.py）
  - GET /api/v1/volunteers（一覧取得）
  - POST /api/v1/volunteers（登録）
  - GET /api/v1/volunteers/{id}（詳細取得）
  - PUT /api/v1/volunteers/{id}（更新）
  - GET /api/v1/volunteers/{id}/activity（活動履歴取得）
  - _Requirements: Requirement 4_

- [x] 7.4 アクティブボランティア取得機能を実装
  - Publicフォーム用の選択リスト提供
  - _Requirements: Requirement 4.4_
  - Publicフォーム用の選択リスト提供
  - _Requirements: Requirement 4.4_

## Phase 5: 診療記録機能

**Context7 MCP使用ガイドライン**:
- Pydantic実装: `mcp_context7_get_library_docs` で `/pydantic/pydantic` を参照（tokens: 5000）
- SQLAlchemy実装: `mcp_context7_get_library_docs` で `/sqlalchemy/sqlalchemy` を参照（tokens: 5000）
- Decimal型処理: Python標準ライブラリ `decimal` の使用方法を確認

**コード品質改善**:
- 型ヒント: `from __future__ import annotations`, `Decimal`, `X | None`
- エラーハンドリング: IntegrityError、SQLAlchemyError
- Docstring: 完全なドキュメント

### 8. 診療記録管理

獣医診療記録のCRUD機能を実装します。

- [ ] 8.1 Pydanticスキーマを実装（app/schemas/medical_record.py）
  - MedicalRecordCreate, MedicalRecordUpdate, MedicalRecordResponse
  - バリデーションルール（必須項目：診療年月日、体重、症状）
  - _Requirements: Requirement 5.3_

- [ ] 8.2 診療記録サービスを実装（app/services/medical_record_service.py）
  - create_medical_record（記録登録）
  - get_medical_record（記録詳細取得）
  - list_medical_records（一覧取得、時系列表示）
  - update_medical_record（記録更新）
  - _Requirements: Requirement 5.1, Requirement 5.5_

- [ ] 8.3 診療記録APIエンドポイントを実装（app/api/v1/medical_records.py）
  - GET /api/v1/medical-records（一覧取得）
  - POST /api/v1/medical-records（登録）
  - GET /api/v1/medical-records/{id}（詳細取得）
  - PUT /api/v1/medical-records/{id}（更新）
  - _Requirements: Requirement 5_

- [ ] 8.4 診療記録機能の統合テストを作成
  - CRUD操作のテスト
  - バリデーションのテスト
  - _Requirements: Requirement 5_

### 9. 診療マスターデータ管理

処置・薬剤・ワクチンのマスターデータ管理機能を実装します。

- [ ] 9.1 Pydanticスキーマを実装（app/schemas/medical_action.py）
  - MedicalActionCreate, MedicalActionUpdate, MedicalActionResponse
  - 期間別価格と通貨単位のバリデーション
  - _Requirements: Requirement 6.1-6.3_

- [ ] 9.2 診療行為マスターサービスを実装（app/services/medical_action_service.py）
  - create_medical_action（診療行為登録）
  - list_medical_actions（一覧取得）
  - update_medical_action（更新）
  - calculate_billing（料金計算：請求価格×投薬量＋処置料金）
  - _Requirements: Requirement 6.4_

- [ ] 9.3 診療行為マスターAPIエンドポイントを実装（app/api/v1/medical_actions.py）
  - GET/POST /api/v1/medical-actions
  - GET/PUT /api/v1/medical-actions/{id}
  - _Requirements: Requirement 6_

- [ ] 9.4 診療行為選択機能を実装
  - MedicalActionsマスターからの選択リスト提供
  - 自由入力も可能
  - _Requirements: Requirement 5.4_

## Phase 6: PDF生成機能 ✅ 完了

**Context7 MCP使用ガイドライン**:
- WeasyPrint実装前: `mcp_context7_resolve_library_id` で "WeasyPrint" を検索し、`mcp_context7_get_library_docs` でドキュメント取得（tokens: 5000）
- QRコード実装前: `mcp_context7_resolve_library_id` で "python-qrcode" を検索し、ドキュメント取得
- Jinja2テンプレート実装前: `mcp_context7_get_library_docs` で `/pallets/jinja` を参照（tokens: 5000）
- PDF生成のベストプラクティスを Context7 で確認

### 10. QRコードとPDF生成 ✅ 完了

QRカードと紙記録フォームのPDF生成機能を実装します。

- [x] 10.1 QRコード生成ユーティリティを実装（app/utils/qr_code.py）
  - QRコード画像生成
  - バイト列変換
  - 猫用URL生成機能
  - _Requirements: Requirement 2.3_

- [x] 10.2 PDF生成サービスを実装（app/services/pdf_service.py）
  - generate_qr_card（QRカードPDF生成）
  - generate_qr_card_grid（面付けカードPDF生成、最大10枚）
  - generate_paper_form（紙記録フォームPDF生成）
  - generate_medical_detail（診療明細PDF生成 - 未実装マーク付き）
  - generate_report（帳票PDF生成 - 未実装マーク付き）
  - _Requirements: Requirement 2.1-2.2, Requirement 2.5-2.8, Requirement 7.2-7.3, Requirement 9_

- [x] 10.3 PDFテンプレートを作成（app/templates/pdf/）
  - qr_card.html（A6サイズ）
  - qr_card_grid.html（A4、2×5枚）
  - paper_form.html（A4、1ヶ月分）
  - _Requirements: Requirement 2, Requirement 7, Requirement 9_

- [x] 10.4 PDF生成APIエンドポイントを実装（app/api/v1/pdf.py）
  - POST /api/v1/pdf/qr-card
  - POST /api/v1/pdf/qr-card-grid
  - POST /api/v1/pdf/paper-form
  - POST /api/v1/pdf/medical-detail（未実装エンドポイント）
  - POST /api/v1/pdf/report（未実装エンドポイント）
  - 認証・権限チェック付き
  - _Requirements: Requirement 2, Requirement 7, Requirement 9_

- [x] 10.5 PDF生成機能のテストを作成
  - QRカード生成テスト（9テスト）
  - 面付けカード生成テスト（4テスト）
  - 紙記録フォーム生成テスト（4テスト）
  - エラーハンドリングテスト
  - カバレッジ94.81%
  - _Requirements: Requirement 28.3_


### 11. CSV/Excelエクスポート機能

CSV・Excel形式でのデータ出力機能を実装します。

- [ ] 11.1 CSV出力ユーティリティを実装（app/utils/csv_export.py）
  - データフレーム→CSV変換
  - 文字エンコーディング処理（UTF-8 BOM）
  - _Requirements: Requirement 8.1, Requirement 25.3_

- [ ] 11.2 Excel出力ユーティリティを実装（app/utils/excel_export.py）
  - openpyxlを使用したExcel生成
  - スタイル設定（ヘッダー、罫線）
  - _Requirements: Requirement 7.5, Requirement 9.4_

- [ ] 11.3 猫マスターCSVインポート/エクスポート機能を実装
  - CSVフォーマット検証
  - バリデーションエラー処理
  - _Requirements: Requirement 8.2-8.4_

- [ ] 11.4 診療明細・帳票のCSV/Excel出力機能を実装
  - 診療記録のCSV/Excel出力
  - 日報・週報・月次集計のCSV/Excel出力
  - _Requirements: Requirement 7.4-7.5, Requirement 9.3-9.4_

## Phase 7: 里親管理機能

### 12. 里親希望者と譲渡管理

里親探しと譲渡プロセスの管理機能を実装します。

- [ ] 12.1 Pydanticスキーマを実装（app/schemas/adoption.py）
  - ApplicantCreate, ApplicantUpdate, ApplicantResponse
  - AdoptionRecordCreate, AdoptionRecordUpdate, AdoptionRecordResponse
  - _Requirements: Requirement 14.1-14.2_

- [ ] 12.2 里親管理サービスを実装（app/services/adoption_service.py）
  - create_applicant（希望者登録）
  - list_applicants（希望者一覧）
  - create_interview_record（面談記録登録）
  - create_adoption_record（譲渡記録登録）
  - update_animal_status（猫のステータス更新）
  - create_follow_up（譲渡後フォロー登録）
  - _Requirements: Requirement 14.3-14.5_

- [ ] 12.3 里親管理APIエンドポイントを実装（app/api/v1/adoptions.py）
  - GET/POST /api/v1/applicants
  - GET/PUT /api/v1/applicants/{id}
  - POST /api/v1/adoptions
  - PUT /api/v1/adoptions/{id}
  - _Requirements: Requirement 14_

- [ ] 12.4 里親管理機能の統合テストを作成
  - 希望者登録のテスト
  - 譲渡プロセスのテスト
  - ステータス更新のテスト
  - _Requirements: Requirement 14_

## Phase 8: 管理画面UI

**Context7 MCP使用ガイドライン**:
- AdminLTE実装前: `mcp_context7_resolve_library_id` で "AdminLTE" を検索し、ドキュメント取得
- Chart.js実装前: `mcp_context7_get_library_docs` で `/chartjs/Chart.js` を参照（tokens: 5000）
- DataTables実装前: `mcp_context7_resolve_library_id` で "DataTables" を検索し、ドキュメント取得
- Jinja2テンプレート実装前: `mcp_context7_get_library_docs` で `/pallets/jinja` を参照

### 13. AdminLTE管理画面の実装

管理画面のUIを実装します。

- [ ] 13.1 ベーステンプレートを作成（app/templates/admin/base.html）
  - AdminLTEレイアウト
  - サイドバーメニュー
  - ヘッダー（ユーザー名、ログアウト）
  - _Requirements: Requirement 12.1-12.2_

- [ ] 13.2 ダッシュボード画面を実装（app/templates/admin/dashboard.html）
  - 統計情報表示（猫数、譲渡数、診療件数、医療費）
  - 世話記録入力数推移グラフ（Chart.js）
  - 長期保護猫一覧
  - _Requirements: Requirement 12.3, Requirement 16.1-16.4_

- [ ] 13.3 猫台帳一覧画面を実装（app/templates/admin/animals/list.html）
  - DataTables（検索、ソート、ページング）
  - ステータスフィルタ
  - アクションボタン（詳細、編集、QRカード出力）
  - _Requirements: Requirement 12.4, Requirement 15.3, Requirement 15.6-15.7_

- [ ] 13.4 猫詳細画面を実装（app/templates/admin/animals/detail.html）
  - タブ構成（基本情報、世話記録、診療記録、画像ギャラリー、体重グラフ）
  - 基本情報編集フォーム
  - ステータス変更機能
  - _Requirements: Requirement 1.3, Requirement 15.2_

- [ ] 13.5 世話記録一覧画面を実装（app/templates/admin/care_logs/list.html）
  - DataTables
  - CSVエクスポートボタン
  - _Requirements: Requirement 25.1_

- [ ] 13.6 診療記録一覧画面を実装（app/templates/admin/medical_records/list.html）
  - DataTables（時系列表示）
  - PDF/CSV/Excelエクスポートボタン
  - _Requirements: Requirement 5.5, Requirement 7.1_

- [ ] 13.7 里親管理画面を実装（app/templates/admin/adoptions/）
  - 希望者一覧・登録・編集画面
  - 面談記録入力画面
  - 譲渡記録入力画面
  - _Requirements: Requirement 14_

- [ ] 13.8 マスター管理画面を実装（app/templates/admin/masters/）
  - ボランティア一覧・登録・編集画面
  - 処置・薬剤・ワクチンマスター画面
  - _Requirements: Requirement 4, Requirement 6_

- [ ] 13.9 帳票出力画面を実装（app/templates/admin/reports/）
  - 期間指定フォーム
  - 形式選択（PDF/CSV/Excel）
  - 日報・週報・月次集計・個別帳票出力
  - _Requirements: Requirement 9.1-9.8_

- [ ] 13.10 設定画面を実装（app/templates/admin/settings/）
  - 団体情報設定
  - 画像制限設定
  - 言語設定
  - ユーザー管理
  - _Requirements: Requirement 27.6-27.7, Requirement 31.3-31.4_

- [ ] 13.11 ログイン画面を実装（app/templates/admin/login.html）
  - メールアドレス・パスワード入力フォーム
  - エラーメッセージ表示
  - _Requirements: Requirement 21.1-21.2_

- [ ] 13.12 体重推移グラフを実装
  - Chart.jsを使用したグラフ表示
  - 期間変更機能（1ヶ月、3ヶ月、6ヶ月、1年、全期間）
  - 警告マーカー表示（10%以上増減）
  - _Requirements: Requirement 26.1-26.4_

- [ ] 13.13 画像ギャラリータブを実装
  - サムネイル表示
  - 画像アップロードダイアログ
  - 拡大表示機能
  - ソート機能（撮影日順、登録日順）
  - _Requirements: Requirement 27.1-27.5_

- [ ] 13.14 検索機能を実装
  - リアルタイム検索（JavaScript）
  - 詳細検索フォーム（性別、年齢範囲、Status、保護日範囲）
  - _Requirements: Requirement 24.1-24.5_


## Phase 9: Publicフォーム（PWA）

**Context7 MCP使用ガイドライン**:
- Tailwind CSS実装前: `mcp_context7_get_library_docs` で `/tailwindlabs/tailwindcss` を参照（tokens: 5000）
- PWA/Service Worker実装前: `mcp_context7_resolve_library_id` で "Workbox" を検索し、ドキュメント取得
- IndexedDB実装前: `mcp_context7_resolve_library_id` で "IndexedDB" または "Dexie.js" を検索（ラッパーライブラリ推奨）

### 14. Publicフォームの実装

認証不要の世話記録入力フォームを実装します。

- [ ] 14.1 Publicフォームテンプレートを作成（app/templates/public/care_form.html）
  - Tailwind CSSでモバイル最適化
  - 1画面完結型レイアウト
  - 猫の名前・顔写真サムネイル表示
  - 入力欄（時点選択、食欲1-5段階、元気1-5段階、排尿有無、清掃済未、メモ）
  - ボランティア選択リスト
  - 保存ボタン（画面下部固定）
  - _Requirements: Requirement 3.1-3.4, Requirement 13.1-13.5_

- [x] 14.2 Publicフォーム用APIエンドポイントを実装（app/api/v1/public.py）
  - GET /api/v1/public/animals/{animal_id}（猫情報取得）
  - GET /api/v1/public/volunteers（アクティブボランティア一覧）
  - POST /api/v1/public/care-logs（記録保存、IPアドレス・User-Agent自動記録）
  - GET /api/v1/public/care-logs/latest/{animal_id}（前回入力値取得）
  - テスト11個実装（カバレッジ97.62%）
  - _Requirements: Requirement 3.5-3.7_

- [ ] 14.3 前回入力値コピー機能を実装（JavaScript）
  - 最新記録の取得
  - フォームへの自動入力
  - _Requirements: Requirement 3.7_

- [ ] 14.4 PWA設定を実装
  - manifest.json作成（アイコン、名前、テーマカラー）
  - Service Worker実装（app/static/js/sw.js）
  - オフラインキャッシュ戦略
  - _Requirements: Requirement 18.1-18.2_

- [ ] 14.5 オフライン機能を実装
  - IndexedDBへの一時保存
  - オンライン復帰時の自動同期
  - 同期状態表示（同期済み、同期待ち、同期中）
  - _Requirements: Requirement 18.3-18.5_

- [ ] 14.6 ホーム画面追加プロンプトを実装
  - 初回アクセス時のプロンプト表示
  - _Requirements: Requirement 18.2_

- [ ] 14.7 Publicフォームの動作テストを作成
  - フォーム入力・保存のテスト
  - オフライン機能のテスト
  - _Requirements: Requirement 3, Requirement 18_

## Phase 10: 多言語対応

**Context7 MCP使用ガイドライン**:
- i18next実装前: `mcp_context7_get_library_docs` で `/i18next/i18next` を参照（tokens: 5000）
- バックエンド多言語化: Jinja2テンプレートでの実装方法を Context7 で確認

### 15. i18n実装

日本語・英語の多言語対応を実装します。

- [ ] 15.1 対訳ファイルを作成（app/static/i18n/）
  - ja.json（日本語）
  - en.json（英語）
  - カテゴリ別に文言を定義（共通UI、猫台帳、世話記録、診療記録、里親管理、帳票、エラーメッセージ）
  - _Requirements: Requirement 19.2, Requirement 19.6_

- [ ] 15.2 フロントエンド多言語化を実装（JavaScript）
  - i18nextライブラリ統合
  - 言語切り替え機能
  - ローカルストレージへの保存
  - ブラウザ言語設定からの自動選択
  - _Requirements: Requirement 19.3-19.5_

- [ ] 15.3 バックエンド多言語化を実装（Jinja2）
  - テンプレートでの対訳ファイル読み込み
  - 言語切り替えエンドポイント
  - _Requirements: Requirement 19.3_

- [ ] 15.4 PDF帳票の多言語化を実装
  - PDFテンプレートでの言語切り替え
  - _Requirements: Requirement 19.7_

- [ ] 15.5 多言語対応のテストを作成
  - 言語切り替えのテスト
  - 対訳ファイルの整合性チェック
  - _Requirements: Requirement 19_

## Phase 11: セキュリティとログ

### 16. セキュリティ強化

セキュリティ対策を実装します。

- [ ] 16.1 セキュリティヘッダーミドルウェアを実装（app/middleware/security.py）
  - X-Content-Type-Options: nosniff
  - X-Frame-Options: DENY
  - X-XSS-Protection: 1; mode=block
  - Strict-Transport-Security（HTTPS時）
  - _Requirements: Requirement 22.5_

- [ ] 16.2 入力バリデーション強化
  - Pydanticスキーマでの厳密な検証
  - ファイルアップロード検証（拡張子、MIMEタイプ、サイズ）
  - _Requirements: Requirement 22.6_

- [ ] 16.3 監査ログ機能を実装（app/services/audit_service.py）
  - 重要操作の記録（猫Status変更、譲渡決定、ユーザー登録・削除、マスターデータ変更）
  - AuditLogテーブルへの保存
  - _Requirements: Requirement 23.1-23.2_

- [ ] 16.4 監査ログ画面を実装（app/templates/admin/audit_logs/）
  - 一覧表示（時系列）
  - フィルタ機能（日付範囲、操作者、操作種別）
  - CSVエクスポート
  - _Requirements: Requirement 23.3-23.5_

- [ ] 16.5 セキュリティ機能のテストを作成
  - セキュリティヘッダーのテスト
  - 監査ログ記録のテスト
  - _Requirements: Requirement 22, Requirement 23_

### 17. ログとエラーハンドリング

ログ管理とエラーハンドリングを実装します。

- [ ] 17.1 ログ設定を実装（app/logging_config.py）
  - RotatingFileHandler（10MB、5ファイル）
  - ログレベル設定（INFO, WARNING, ERROR, CRITICAL）
  - フォーマット設定
  - _Requirements: Requirement 29.6_

- [ ] 17.2 エラーハンドリングミドルウェアを実装（app/middleware/error_handler.py）
  - 例外キャッチ
  - エラーレスポンス生成（JSON形式）
  - エラーログ記録
  - _Requirements: Requirement 29.1-29.3_

- [ ] 17.3 エラーページを実装（app/templates/errors/）
  - 400, 401, 403, 404, 500エラーページ
  - ユーザーフレンドリーなメッセージ
  - _Requirements: Requirement 29.1_

- [ ] 17.4 データベース接続エラー処理を実装
  - リトライ処理
  - 管理者通知
  - _Requirements: Requirement 29.2_

- [ ] 17.5 ネットワークエラー処理を実装（PWA）
  - オフラインモード切り替え
  - 復旧後の自動同期
  - _Requirements: Requirement 29.4_


## Phase 12: バックアップとデータ管理

**Context7 MCP使用ガイドライン**:
- APScheduler実装前: `mcp_context7_get_library_docs` で `/agronholm/apscheduler` を参照（tokens: 5000）
- FastAPI統合方法を Context7 ドキュメントで確認

### 18. バックアップ機能

自動バックアップ機能を実装します。

- [ ] 18.1 バックアップタスクを実装（app/tasks/backup.py）
  - SQLiteデータベースのバックアップ
  - /mediaディレクトリのバックアップ
  - タイムスタンプ付きファイル名
  - 90日以上前のバックアップ自動削除
  - _Requirements: Requirement 11.1-11.3, Requirement 30.1-30.2_

- [ ] 18.2 スケジューラー設定を実装
  - APSchedulerによる定時実行（毎晩2:00）
  - バックアップ失敗時のエラーログ記録
  - _Requirements: Requirement 11.1, Requirement 11.4_

- [ ] 18.3 データ保持期間管理を実装
  - 譲渡済み猫データの無期限保持
  - 里親希望者の個人情報3年間保持
  - 個人情報削除機能
  - _Requirements: Requirement 30.3-30.5_

- [ ] 18.4 バックアップ機能のテストを作成
  - バックアップ実行のテスト
  - 古いバックアップ削除のテスト
  - _Requirements: Requirement 11, Requirement 30_

### 19. 初期セットアップ

初回セットアップウィザードを実装します。

- [ ] 19.1 セットアップウィザード画面を実装（app/templates/setup/wizard.html）
  - ステップ1: 初期管理者アカウント作成
  - ステップ2: 団体情報登録
  - ステップ3: 基本設定（言語、タイムゾーン、画像制限）
  - _Requirements: Requirement 31.1-31.4_

- [ ] 19.2 セットアップAPIエンドポイントを実装（app/api/v1/setup.py）
  - POST /api/v1/setup/admin（管理者作成）
  - POST /api/v1/setup/organization（団体情報登録）
  - POST /api/v1/setup/settings（基本設定）
  - POST /api/v1/setup/complete（セットアップ完了）
  - _Requirements: Requirement 31.2-31.5_

- [ ] 19.3 サンプルデータ投入機能を実装（app/db/init_data.py）
  - サンプル猫1頭
  - サンプルボランティア1名
  - _Requirements: Requirement 31.6_

- [ ] 19.4 初回起動判定処理を実装
  - Usersテーブルが空の場合、セットアップウィザードにリダイレクト
  - _Requirements: Requirement 31.1_

## Phase 13: OCR機能（オプション）

### 20. OCR処理

紙記録からのデータ移行支援機能を実装します。

- [ ] 20.1 OCRサービスを実装（app/services/ocr_service.py）
  - 画像/PDFアップロード処理
  - Tesseract OCR実行
  - テキスト抽出
  - 編集可能フォームへのデータ提供
  - _Requirements: Requirement 17.5-17.7_

- [ ] 20.2 MCP連携を実装
  - Google Cloud Vision API連携
  - AWS Textract連携
  - OCRサービス選択機能
  - _Requirements: Requirement 17.9_

- [ ] 20.3 Kiro Hook連携を実装
  - 指定フォルダ監視
  - ファイル追加時の自動OCR処理
  - _Requirements: Requirement 17.8_

- [ ] 20.4 OCR APIエンドポイントを実装（app/api/v1/ocr.py）
  - POST /api/v1/ocr/upload（アップロード→OCR処理）
  - GET /api/v1/ocr/status/{job_id}（処理状況取得）
  - _Requirements: Requirement 17.5, Requirement 17.10_

- [ ] 20.5 OCR結果確認画面を実装（app/templates/admin/ocr/）
  - 認識テキスト表示
  - 編集フォーム
  - 保存ボタン
  - _Requirements: Requirement 17.6-17.7_

- [ ] 20.6 進捗通知機能を実装
  - WebSocketまたはポーリングによる進捗表示
  - _Requirements: Requirement 17.10_

- [ ] 20.7 OCR機能のテストを作成
  - OCR処理のテスト
  - MCP連携のテスト
  - _Requirements: Requirement 17_

## Phase 14: ヘルプとサポート

### 21. ヘルプ機能

ユーザー向けヘルプ機能を実装します。

- [ ] 21.1 オンラインヘルプページを作成（app/templates/help/）
  - 各機能の使い方（画像付き）
  - よくある質問（FAQ）
  - _Requirements: Requirement 32.2-32.4_

- [ ] 21.2 ヘルプボタンを配置
  - 管理画面各ページにヘルプボタン
  - コンテキストヘルプ（該当ページのヘルプを表示）
  - _Requirements: Requirement 32.1-32.2_

- [ ] 21.3 問い合わせフォームを実装（app/templates/help/contact.html）
  - 問い合わせ内容入力フォーム
  - メール送信機能
  - _Requirements: Requirement 32.5-32.6_

- [ ] 21.4 プライバシーポリシーページを作成
  - データ収集・利用目的の明示
  - _Requirements: Requirement 30.6_

## Phase 15: デプロイとドキュメント

### 22. デプロイ設定

ホスティングサービスへのデプロイ設定を作成します。

- [ ] 22.1 Renderデプロイ設定を作成（render.yaml）
  - Web service設定
  - 環境変数設定
  - Disk設定（1GB）
  - _Requirements: Requirement 20.1-20.2, Requirement 20.4_

- [ ] 22.2 Railwayデプロイ設定を作成（railway.json）
  - ビルド設定
  - 起動コマンド設定
  - _Requirements: Requirement 20.1-20.2_

- [ ] 22.3 Fly.ioデプロイ設定を作成（fly.toml）
  - ビルド設定
  - Volume設定
  - リージョン設定
  - _Requirements: Requirement 20.1-20.2, Requirement 20.4_

- [ ] 22.4 環境変数テンプレートを作成（.env.example）
  - 必須環境変数の一覧
  - 説明コメント
  - _Requirements: Requirement 20.3_

- [ ] 22.5 デプロイ手順ドキュメントを作成（README.md）
  - 各ホスティングサービスへのデプロイ手順
  - 環境変数設定方法
  - データベース永続化設定
  - _Requirements: Requirement 20.5-20.6_

- [ ] 22.6 ワンクリックデプロイボタンを追加
  - Deploy to Render
  - Deploy to Railway
  - _Requirements: Requirement 20.7_

### 23. ドキュメント整備

開発・運用ドキュメントを整備します。

- [ ] 23.1 API仕様書を作成
  - OpenAPI（Swagger）仕様書
  - FastAPIの自動生成機能を活用
  - _Requirements: 技術的制約1_

- [ ] 23.2 開発環境セットアップガイドを作成
  - 仮想環境作成手順
  - 依存関係インストール手順
  - データベース初期化手順
  - 開発サーバー起動手順
  - _Requirements: Requirement 31_

- [ ] 23.3 運用マニュアルを作成
  - バックアップ・リストア手順
  - ユーザー管理手順
  - トラブルシューティング
  - _Requirements: Requirement 11, Requirement 21_

- [ ] 23.4 コードドキュメントを整備
  - docstring追加
  - 型ヒント追加
  - _Requirements: 技術的制約1_

## Phase 16: パフォーマンス最適化とテスト

**Context7 MCP使用ガイドライン**:
- pytest実装前: `mcp_context7_get_library_docs` で `/pytest-dev/pytest` を参照（tokens: 5000）
- pytest-asyncio実装前: `mcp_context7_resolve_library_id` で "pytest-asyncio" を検索
- Pillow実装前: `mcp_context7_get_library_docs` で `/python-pillow/Pillow` を参照（tokens: 5000）

### 24. パフォーマンス最適化

システムパフォーマンスを最適化します。

- [ ] 24.1 データベースインデックスを最適化
  - 頻繁に検索されるカラムのインデックス確認
  - 複合インデックスの追加
  - _Requirements: Requirement 28.1-28.2_

- [ ] 24.2 クエリ最適化を実施
  - N+1問題の解消（eager loading）
  - 不要なカラムの除外
  - _Requirements: Requirement 28.1_

- [ ] 24.3 画像最適化を実装
  - アップロード時の自動リサイズ
  - 圧縮処理
  - _Requirements: Requirement 27.9_

- [ ] 24.4 キャッシュ戦略を実装
  - アクティブボランティア一覧のキャッシュ
  - 設定値のキャッシュ
  - _Requirements: Requirement 28.1_

- [ ] 24.5 パフォーマンステストを実施
  - レスポンスタイム測定（画面遷移3秒、記録保存2秒、PDF生成10秒）
  - 同時接続テスト（20名）
  - 大量データテスト（猫100頭）
  - _Requirements: Requirement 28.1-28.5_

### 25. 統合テストとE2Eテスト

システム全体のテストを実施します。

- [ ] 25.1 統合テストを作成（DDD準拠）
  - ドメインサービス間の協調テスト
  - アプリケーションサービスの統合テスト
  - インフラストラクチャ層の統合テスト
  - APIエンドポイントのコントラクトテスト
  - _Requirements: Requirement 28_

- [ ] 25.2 フロントエンドテストを作成
  - Jest + jsdomでJavaScript関数のテスト
  - PWA機能（オフライン同期、キャッシュ）のテスト
  - _Requirements: Requirement 18_

- [ ] 25.3 E2Eテストを作成
  - ユーザーフロー（猫登録→記録入力→帳票出力）のテスト
  - Playwrightを使用
  - _Requirements: Requirement 28_

- [ ] 25.4 ブラウザ互換性テストを実施
  - Chrome、Firefox、Safari、Edge（最新版+1つ前）
  - iOS 14+、Android 10+
  - _Requirements: Requirement 28.7-28.8_

- [ ] 25.5 セキュリティテストを実施
  - SQLインジェクションテスト
  - XSSテスト
  - CSRF対策テスト
  - _Requirements: Requirement 22_

## Phase 17: 最終調整とリリース

### 26. 最終調整

リリース前の最終調整を行います。

- [ ] 26.1 エラーメッセージの多言語化を確認
  - 全エラーメッセージが対訳ファイルに含まれているか確認
  - _Requirements: Requirement 19.6_

- [ ] 26.2 UI/UXの最終調整
  - モバイル表示の確認
  - ボタンサイズの確認（最小44×44px）
  - _Requirements: Requirement 13.2_

- [ ] 26.3 デフォルト設定値の確認
  - 画像制限（最大20枚、最大5MB）
  - セッションタイムアウト（2時間）
  - ログイン試行回数制限（5回）
  - _Requirements: Requirement 22, Requirement 27.10_

- [ ] 26.4 ログ出力の確認
  - 本番環境でのログレベル設定
  - 機密情報のマスキング
  - _Requirements: Requirement 29.6_

- [ ] 26.5 HTTPS設定の確認
  - 本番環境でのHTTPS必須化
  - セキュリティヘッダーの確認
  - _Requirements: Requirement 22.5_

- [ ] 26.6 負荷テストを実施
  - 同時接続20名での動作確認
  - システム稼働率95%の確認
  - _Requirements: Requirement 28.4, Requirement 28.6_

### 27. リリース準備

リリースに向けた最終準備を行います。

- [ ] 27.1 本番環境へのデプロイ
  - Render/Railway/Fly.ioへのデプロイ
  - 環境変数設定
  - データベース永続化設定
  - _Requirements: Requirement 20.1-20.5_

- [ ] 27.2 初期データ投入
  - セットアップウィザードの実行
  - 初期管理者アカウント作成
  - サンプルデータ投入
  - _Requirements: Requirement 31_

- [ ] 27.3 バックアップ設定の確認
  - 自動バックアップの動作確認
  - バックアップファイルの保存先確認
  - _Requirements: Requirement 11_

- [ ] 27.4 監視設定
  - エラーログ監視
  - システム稼働監視
  - _Requirements: Requirement 29.2_

- [ ] 27.5 ユーザー向けドキュメントの公開
  - オンラインヘルプの公開
  - FAQ の公開
  - プライバシーポリシーの公開
  - _Requirements: Requirement 32_

- [ ] 27.6 リリースノートの作成
  - 実装機能一覧
  - 既知の制限事項
  - 今後の予定
  - _Requirements: スケジュール制約1_

---

## 実装完了

全てのタスクが完了したら、NecoKeeperシステムのMVPが完成です。

次のステップ:
1. ユーザーフィードバックの収集
2. バグ修正と改善
3. Phase 2機能の検討（通知機能、SNS連携、AI機能等）

---

## 進捗サマリー

### Phase別完了状況
- [x] Phase 1: プロジェクト基盤とデータベース (11/11 完了) ✅
- [x] Phase 2: 認証・認可システム (7/7 完了) ✅
- [x] Phase 3: 猫管理機能 (6/6 完了) ✅
- [x] Phase 4: 世話記録機能 (5/5 完了) ✅
- [ ] Phase 5: 画像ギャラリー機能 (0/3 完了)
- [ ] Phase 6: 診療記録機能 (0/4 完了)
- [ ] Phase 6: 診療マスターデータ管理 (0/4 完了)
- [ ] Phase 7: 診療明細出力 (0/5 完了)
- [ ] Phase 8: CSVインポート・エクスポート (0/4 完了)
- [ ] Phase 9: 帳票出力（日報・週報・月次集計） (0/4 完了)
- [ ] Phase 10: 権限管理とアクセス制御 (0/1 完了)
- [ ] Phase 11: データバックアップ (0/4 完了)
- [ ] Phase 12: 管理画面UI (0/14 完了)
- [ ] Phase 13: Publicフォーム（PWA） (0/7 完了)
- [ ] Phase 14: 里親管理機能 (0/4 完了)
- [ ] Phase 15: 猫のステータス管理と論理削除 (0/1 完了)
- [ ] Phase 16: 活動状況の可視化 (0/1 完了)
- [ ] Phase 17: 紙記録からのデータ移行支援 (0/7 完了)
- [ ] Phase 18: PWA対応とオフライン機能 (0/2 完了)
- [ ] Phase 19: 多言語対応 (0/5 完了)
- [ ] Phase 20: 簡単デプロイとホスティング (0/6 完了)
- [ ] Phase 21: 認証とユーザー管理 (0/2 完了)
- [ ] Phase 22: セキュリティ対策 (0/5 完了)
- [ ] Phase 23: 監査ログ (0/5 完了)
- [ ] Phase 24: 検索機能 (0/2 完了)
- [ ] Phase 25: 世話記録のCSVエクスポート (0/2 完了)
- [ ] Phase 26: 体重推移の可視化 (0/1 完了)
- [ ] Phase 27: 画像ギャラリー (0/3 完了)
- [ ] Phase 28: パフォーマンス最適化 (0/5 完了)
- [ ] Phase 29: 統合テストとE2Eテスト (0/5 完了)
- [ ] Phase 30: 最終調整 (0/6 完了)
- [ ] Phase 31: リリース準備 (0/6 完了)

### 全体進捗
**完了タスク数**: 29 / 140 タスク (20.7%)
**MVP Core完了**: Phase 1, 2, 3, 4 完全完了 ✅
**推定残り時間**: 約105-165時間（1タスク平均1-1.5時間）

### 実装済み機能
- ✅ データベース（全12モデル）
- ✅ JWT認証・認可システム（RBAC）
- ✅ 猫管理機能（CRUD、検索、ステータス管理）
- ✅ 世話記録機能（CRUD、CSV出力、前回値コピー）
- ✅ 画像アップロード・最適化
- ✅ 統合テスト（認証25テスト、猫管理7テスト、世話記録7テスト）

### 実装済みAPI（合計14エンドポイント）
- **認証**: 2エンドポイント
- **猫管理**: 6エンドポイント
- **世話記録**: 6エンドポイント

### 次に実装すべきタスク（MVP Core優先順位）

**重要**: 実装前に必ずcode-structure-reviewの改善を適用すること
- すべてのファイルに `from __future__ import annotations` を追加
- 型ヒントは `collections.abc` と `X | None` 構文を使用
- エラーハンドリングとロギングを統一
- Docstringを完全に記述

**次のタスク:**
1. **Task 5.1**: 画像ギャラリーサービスを実装（app/services/image_service.py）
2. **Task 5.2**: 画像管理APIエンドポイントを実装（app/api/v1/images.py）
3. **Task 5.3**: 画像制限設定機能を実装

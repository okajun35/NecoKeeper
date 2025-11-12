# Design Document

## Overview

NecoKeeperは、保護猫活動のデジタル化を実現するWebアプリケーションです。FastAPI（バックエンド）+ SQLite（データベース）+ AdminLTE/Tailwind CSS（フロントエンド）の構成で、小規模団体（10名前後、猫10〜20頭）での運用を想定しています。

### 設計原則

1. **シンプルさ優先**: POC段階のため、過度に複雑な実装を避ける
2. **モバイルファースト**: ボランティアがスマホで記録入力できることを最優先
3. **オフライン対応**: PWAによるオフライン記録と自動同期
4. **低コスト運用**: 無料ホスティングサービスで運用可能
5. **段階的デジタル化**: 紙との併用を前提とした設計

### 技術スタック

- **バックエンド**: FastAPI 0.104+ (Python 3.9+)
- **データベース**: SQLite 3.35+
- **ORM**: SQLAlchemy 2.0+
- **認証**: JWT + OAuth2 Password Flow（python-jose + passlib/bcrypt）
- **PDF生成**: WeasyPrint 60+
- **管理画面UI**: AdminLTE 3.2+
- **PublicフォームUI**: Tailwind CSS 3.3+
- **PWA**: Workbox 7+
- **多言語**: i18next（JSON対訳ファイル）
- **OCR**: Tesseract（オプション、MCP連携）

## Architecture

### システム構成図

```
┌─────────────────────────────────────────────────────────────┐
│                        Client Layer                          │
├──────────────────────┬──────────────────────────────────────┤
│  Admin UI (AdminLTE) │  Public Form (Tailwind + PWA)        │
│  - 管理画面          │  - QRスキャン→記録入力               │
│  - 認証必須          │  - 認証不要                          │
│  - PC/スマホ対応     │  - スマホ最適化                      │
└──────────────────────┴──────────────────────────────────────┘
                              ↓ HTTPS
┌─────────────────────────────────────────────────────────────┐
│                     Application Layer                        │
│                      FastAPI Server                          │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Auth Module  │  │ API Endpoints│  │ PDF Generator│      │
│  │ - JWT/OAuth2 │  │ - REST API   │  │ - WeasyPrint │      │
│  │ - RBAC       │  │ - CRUD       │  │ - QR Code    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                      Data Layer                              │
│                   SQLite Database                            │
├─────────────────────────────────────────────────────────────┤
│  Animals | CareLog | MedicalRecord | Users | Volunteers     │
│  Applicants | Procedures | Medications | Vaccines           │
│  AuditLog | Sessions | Settings                             │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    Storage Layer                             │
├─────────────────────────────────────────────────────────────┤
│  /data/app.sqlite3  │  /media/photos/  │  /backups/         │
└─────────────────────────────────────────────────────────────┘
```

### ディレクトリ構造

```
necokeeper/
├── app/
│   ├── main.py                 # FastAPIアプリケーションエントリーポイント
│   ├── config.py               # 設定管理（環境変数）
│   ├── database.py             # データベース接続
│   ├── models/                 # SQLAlchemyモデル
│   │   ├── animal.py
│   │   ├── care_log.py
│   │   ├── medical_record.py
│   │   ├── user.py
│   │   ├── volunteer.py
│   │   └── ...
│   ├── schemas/                # Pydanticスキーマ（バリデーション）
│   │   ├── animal.py
│   │   ├── care_log.py
│   │   └── ...
│   ├── api/                    # APIエンドポイント
│   │   ├── v1/
│   │   │   ├── animals.py
│   │   │   ├── care_logs.py
│   │   │   ├── medical_records.py
│   │   │   ├── auth.py
│   │   │   └── ...
│   ├── services/               # ビジネスロジック
│   │   ├── animal_service.py
│   │   ├── care_log_service.py
│   │   ├── pdf_service.py
│   │   ├── ocr_service.py
│   │   └── ...
│   ├── auth/                   # 認証・認可
│   │   ├── jwt.py             # JWT生成・検証
│   │   ├── password.py        # パスワードハッシュ化
│   │   ├── dependencies.py    # 認証依存性
│   │   └── permissions.py     # 権限チェック
│   ├── templates/              # Jinja2テンプレート
│   │   ├── admin/              # 管理画面（AdminLTE）
│   │   ├── public/             # Publicフォーム（Tailwind）
│   │   └── pdf/                # PDF生成用テンプレート
│   ├── static/                 # 静的ファイル
│   │   ├── css/
│   │   ├── js/
│   │   ├── img/
│   │   └── i18n/               # 対訳ファイル（JSON）
│   └── utils/                  # ユーティリティ
│       ├── qr_code.py
│       ├── validators.py
│       └── ...
├── data/
│   └── app.sqlite3             # SQLiteデータベース
├── media/
│   └── photos/                 # 猫の写真
├── backups/                    # バックアップファイル
├── tests/                      # テストコード
├── requirements.txt            # Python依存関係
├── render.yaml                 # Renderデプロイ設定
├── railway.json                # Railwayデプロイ設定
├── fly.toml                    # Fly.ioデプロイ設定
└── README.md                   # デプロイ手順
```


## Data Models

### ER図（主要エンティティ）

```
┌─────────────┐       ┌──────────────┐       ┌─────────────┐
│   Animals   │1    n │   CareLog    │n    1 │ Volunteers  │
│─────────────│───────│──────────────│───────│─────────────│
│ id (PK)     │       │ id (PK)      │       │ id (PK)     │
│ name        │       │ animal_id(FK)│       │ name        │
│ photo       │       │ recorder_id  │       │ contact     │
│ pattern     │       │ weight       │       │ status      │
│ status      │       │ food         │       │ ...         │
│ ...         │       │ created_at   │       └─────────────┘
└─────────────┘       └──────────────┘
      │1
      │
      │n
┌──────────────┐       ┌─────────────┐
│MedicalRecord │n    1 │    Users    │
│──────────────│───────│─────────────│
│ id (PK)      │       │ id (PK)     │
│ animal_id(FK)│       │ email       │
│ vet_id (FK)  │       │ password    │
│ date         │       │ role        │
│ weight       │       │ ...         │
│ symptoms     │       └─────────────┘
│ ...          │
└──────────────┘

┌─────────────┐       ┌──────────────┐
│ Applicants  │1    n │AdoptionRecord│
│─────────────│───────│──────────────│
│ id (PK)     │       │ id (PK)      │
│ name        │       │ animal_id(FK)│
│ contact     │       │ applicant_id │
│ address     │       │ interview_dt │
│ ...         │       │ decision     │
└─────────────┘       └──────────────┘
```

### テーブル定義

#### Animals（猫マスター）

| カラム名 | 型 | NULL | デフォルト | 説明 |
|---------|-----|------|-----------|------|
| id | INTEGER | NO | AUTO | 主キー |
| name | VARCHAR(100) | YES | NULL | 猫の名前 |
| photo | VARCHAR(255) | NO | - | 顔写真パス |
| pattern | VARCHAR(100) | NO | - | 柄・色 |
| tail_length | VARCHAR(50) | NO | - | 尻尾の長さ |
| collar | VARCHAR(100) | YES | NULL | 首輪有無・色 |
| age | VARCHAR(50) | NO | - | 年齢（大きさ） |
| gender | VARCHAR(10) | NO | - | 性別（male/female/unknown） |
| ear_cut | BOOLEAN | NO | FALSE | 耳カット有無 |
| features | TEXT | YES | NULL | 外傷・特徴・性格 |
| status | VARCHAR(20) | NO | '保護中' | ステータス |
| protected_at | DATE | NO | CURRENT_DATE | 保護日 |
| created_at | DATETIME | NO | CURRENT_TIMESTAMP | 作成日時 |
| updated_at | DATETIME | NO | CURRENT_TIMESTAMP | 更新日時 |

**インデックス**: status, protected_at, name

#### CareLog（世話記録）

| カラム名 | 型 | NULL | デフォルト | 説明 |
|---------|-----|------|-----------|------|
| id | INTEGER | NO | AUTO | 主キー |
| animal_id | INTEGER | NO | - | 猫ID（FK） |
| recorder_id | INTEGER | YES | NULL | 記録者ID（FK） |
| recorder_name | VARCHAR(100) | NO | - | 記録者名 |
| time_slot | VARCHAR(10) | NO | - | 時点（morning/noon/evening） |
| appetite | INTEGER | NO | 3 | 食欲（1〜5段階、5が最良） |
| energy | INTEGER | NO | 3 | 元気（1〜5段階、5が最良） |
| urination | BOOLEAN | NO | FALSE | 排尿（有り=TRUE、無し=FALSE） |
| cleaning | BOOLEAN | NO | FALSE | 清掃（済=TRUE、未=FALSE） |
| memo | TEXT | YES | NULL | メモ |
| ip_address | VARCHAR(45) | YES | NULL | IPアドレス |
| user_agent | VARCHAR(255) | YES | NULL | ユーザーエージェント |
| device_tag | VARCHAR(100) | YES | NULL | デバイスタグ |
| from_paper | BOOLEAN | NO | FALSE | 紙記録からの転記 |
| created_at | DATETIME | NO | CURRENT_TIMESTAMP | 記録日時 |
| last_updated_at | DATETIME | NO | CURRENT_TIMESTAMP | 最終更新日時 |
| last_updated_by | INTEGER | YES | NULL | 最終更新者ID（FK） |

**インデックス**: animal_id, created_at, recorder_id, time_slot

#### MedicalRecord（診療記録）

| カラム名 | 型 | NULL | デフォルト | 説明 |
|---------|-----|------|-----------|------|
| id | INTEGER | NO | AUTO | 主キー |
| animal_id | INTEGER | NO | - | 猫ID（FK） |
| vet_id | INTEGER | NO | - | 獣医師ID（FK） |
| date | DATE | NO | - | 診療日 |
| time_slot | VARCHAR(20) | YES | NULL | 時間帯 |
| weight | DECIMAL(5,2) | NO | - | 体重（kg） |
| temperature | DECIMAL(4,1) | YES | NULL | 体温（℃） |
| symptoms | TEXT | NO | - | 症状 |
| medical_action_id | INTEGER | YES | NULL | 診療行為ID（FK） |
| dosage | INTEGER | YES | NULL | 投薬量（回数） |
| other | TEXT | YES | NULL | その他（ロット番号等） |
| comment | TEXT | YES | NULL | コメント |
| created_at | DATETIME | NO | CURRENT_TIMESTAMP | 作成日時 |
| updated_at | DATETIME | NO | CURRENT_TIMESTAMP | 更新日時 |
| last_updated_at | DATETIME | NO | CURRENT_TIMESTAMP | 最終更新日時 |
| last_updated_by | INTEGER | YES | NULL | 最終更新者ID（FK） |

**インデックス**: animal_id, date, vet_id, medical_action_id

#### Users（ユーザー）

| カラム名 | 型 | NULL | デフォルト | 説明 |
|---------|-----|------|-----------|------|
| id | INTEGER | NO | AUTO | 主キー |
| email | VARCHAR(255) | NO | - | メールアドレス（ユニーク） |
| password_hash | VARCHAR(255) | NO | - | パスワードハッシュ（bcrypt） |
| name | VARCHAR(100) | NO | - | 氏名 |
| role | VARCHAR(20) | NO | 'read_only' | ロール |
| is_active | BOOLEAN | NO | TRUE | アクティブ状態 |
| failed_login_count | INTEGER | NO | 0 | ログイン失敗回数 |
| locked_until | DATETIME | YES | NULL | ロック解除日時 |
| created_at | DATETIME | NO | CURRENT_TIMESTAMP | 作成日時 |
| updated_at | DATETIME | NO | CURRENT_TIMESTAMP | 更新日時 |

**インデックス**: email（ユニーク）, role

#### Volunteers（ボランティア）

| カラム名 | 型 | NULL | デフォルト | 説明 |
|---------|-----|------|-----------|------|
| id | INTEGER | NO | AUTO | 主キー |
| name | VARCHAR(100) | NO | - | 氏名 |
| contact | VARCHAR(255) | YES | NULL | 連絡先 |
| affiliation | VARCHAR(100) | YES | NULL | 所属 |
| status | VARCHAR(20) | NO | 'active' | 活動状態 |
| started_at | DATE | NO | CURRENT_DATE | 活動開始日 |
| created_at | DATETIME | NO | CURRENT_TIMESTAMP | 作成日時 |
| updated_at | DATETIME | NO | CURRENT_TIMESTAMP | 更新日時 |

**インデックス**: status, name

#### Applicants（里親希望者）

| カラム名 | 型 | NULL | デフォルト | 説明 |
|---------|-----|------|-----------|------|
| id | INTEGER | NO | AUTO | 主キー |
| name | VARCHAR(100) | NO | - | 氏名 |
| contact | VARCHAR(255) | NO | - | 連絡先 |
| address | TEXT | YES | NULL | 住所 |
| family | TEXT | YES | NULL | 家族構成 |
| environment | TEXT | YES | NULL | 飼育環境 |
| conditions | TEXT | YES | NULL | 希望条件 |
| created_at | DATETIME | NO | CURRENT_TIMESTAMP | 作成日時 |
| updated_at | DATETIME | NO | CURRENT_TIMESTAMP | 更新日時 |

**インデックス**: name, contact

#### AdoptionRecord（譲渡記録）

| カラム名 | 型 | NULL | デフォルト | 説明 |
|---------|-----|------|-----------|------|
| id | INTEGER | NO | AUTO | 主キー |
| animal_id | INTEGER | NO | - | 猫ID（FK） |
| applicant_id | INTEGER | NO | - | 里親希望者ID（FK）※Applicantsテーブルと紐付け |
| interview_date | DATE | YES | NULL | 面談日 |
| interview_note | TEXT | YES | NULL | 面談内容 |
| decision | VARCHAR(20) | YES | NULL | 判定結果（approved/rejected/pending） |
| adoption_date | DATE | YES | NULL | 譲渡日 |
| follow_up | TEXT | YES | NULL | 譲渡後フォロー |
| created_at | DATETIME | NO | CURRENT_TIMESTAMP | 作成日時 |
| updated_at | DATETIME | NO | CURRENT_TIMESTAMP | 更新日時 |

**インデックス**: animal_id, applicant_id, adoption_date

**applicant_idの用途**:
- Applicants（里親希望者）テーブルと紐付けて、誰に譲渡したかを記録
- 面談記録、譲渡決定、譲渡後フォローの履歴管理
- 同一希望者が複数の猫を譲渡された場合の追跡


#### MedicalActions（診療行為マスター）

| カラム名 | 型 | NULL | デフォルト | 説明 |
|---------|-----|------|-----------|------|
| id | INTEGER | NO | AUTO | 主キー |
| name | VARCHAR(100) | NO | - | 診療名称（薬剤、ワクチン、検査等） |
| valid_from | DATE | NO | - | 適用開始日 |
| valid_to | DATE | YES | NULL | 適用終了日 |
| cost_price | DECIMAL(10,2) | NO | 0.00 | 原価（小数点2桁） |
| selling_price | DECIMAL(10,2) | NO | 0.00 | 請求価格（小数点2桁） |
| procedure_fee | DECIMAL(10,2) | NO | 0.00 | 投薬・処置料金（小数点2桁） |
| currency | VARCHAR(3) | NO | 'JPY' | 通貨単位（JPY/USD） |
| created_at | DATETIME | NO | CURRENT_TIMESTAMP | 作成日時 |
| updated_at | DATETIME | NO | CURRENT_TIMESTAMP | 更新日時 |
| last_updated_at | DATETIME | NO | CURRENT_TIMESTAMP | 最終更新日時 |
| last_updated_by | INTEGER | YES | NULL | 最終更新者ID（FK） |

**インデックス**: name, valid_from, valid_to

**料金計算式**:
- 実際の請求価格 = (請求価格 × 投薬量) + 投薬・処置料金

#### AnimalImages（猫画像ギャラリー）

| カラム名 | 型 | NULL | デフォルト | 説明 |
|---------|-----|------|-----------|------|
| id | INTEGER | NO | AUTO | 主キー |
| animal_id | INTEGER | NO | - | 猫ID（FK） |
| image_path | VARCHAR(255) | NO | - | 画像パス |
| taken_at | DATE | YES | NULL | 撮影日 |
| description | TEXT | YES | NULL | 説明 |
| file_size | INTEGER | NO | 0 | ファイルサイズ（bytes） |
| created_at | DATETIME | NO | CURRENT_TIMESTAMP | 作成日時 |

**インデックス**: animal_id, taken_at

#### StatusHistory（ステータス変更履歴）

| カラム名 | 型 | NULL | デフォルト | 説明 |
|---------|-----|------|-----------|------|
| id | INTEGER | NO | AUTO | 主キー |
| animal_id | INTEGER | NO | - | 猫ID（FK） |
| changed_by | INTEGER | NO | - | 変更者ID（FK） |
| old_status | VARCHAR(20) | YES | NULL | 変更前ステータス |
| new_status | VARCHAR(20) | NO | - | 変更後ステータス |
| changed_at | DATETIME | NO | CURRENT_TIMESTAMP | 変更日時 |

**インデックス**: animal_id, changed_at

#### AuditLog（監査ログ）

| カラム名 | 型 | NULL | デフォルト | 説明 |
|---------|-----|------|-----------|------|
| id | INTEGER | NO | AUTO | 主キー |
| user_id | INTEGER | YES | NULL | ユーザーID（FK） |
| action | VARCHAR(50) | NO | - | 操作種別 |
| target_type | VARCHAR(50) | NO | - | 対象エンティティ |
| target_id | INTEGER | YES | NULL | 対象ID |
| old_value | TEXT | YES | NULL | 変更前の値（JSON） |
| new_value | TEXT | YES | NULL | 変更後の値（JSON） |
| ip_address | VARCHAR(45) | YES | NULL | IPアドレス |
| created_at | DATETIME | NO | CURRENT_TIMESTAMP | 操作日時 |

**インデックス**: user_id, action, created_at

#### RefreshTokens（リフレッシュトークン）※オプション

| カラム名 | 型 | NULL | デフォルト | 説明 |
|---------|-----|------|-----------|------|
| id | INTEGER | NO | AUTO | 主キー |
| user_id | INTEGER | NO | - | ユーザーID（FK） |
| token | VARCHAR(255) | NO | - | リフレッシュトークン（ユニーク） |
| expires_at | DATETIME | NO | - | 有効期限 |
| created_at | DATETIME | NO | CURRENT_TIMESTAMP | 作成日時 |
| revoked | BOOLEAN | NO | FALSE | 無効化フラグ |

**インデックス**: user_id, token（ユニーク）, expires_at

**注**: アクセストークンはステートレス（JWTのみ）。リフレッシュトークンは長期間有効なトークンの管理用（オプション機能）。

#### Settings（システム設定）

| カラム名 | 型 | NULL | デフォルト | 説明 |
|---------|-----|------|-----------|------|
| key | VARCHAR(100) | NO | - | 設定キー（主キー） |
| value | TEXT | NO | - | 設定値（JSON） |
| description | TEXT | YES | NULL | 説明 |
| updated_at | DATETIME | NO | CURRENT_TIMESTAMP | 更新日時 |

**設定例**:
- `organization_info`: 団体情報
- `image_limits`: 画像制限（最大枚数、最大サイズ）
- `language`: デフォルト言語
- `timezone`: タイムゾーン

## Components and Interfaces

### API Endpoints

#### 認証API

```
POST   /api/v1/auth/token          # ログイン（JWTトークン取得）
GET    /api/v1/auth/me             # 現在のユーザー情報取得
POST   /api/v1/auth/refresh        # トークンリフレッシュ（オプション）
```

#### 猫管理API

```
GET    /api/v1/animals             # 猫一覧取得
POST   /api/v1/animals             # 猫登録
GET    /api/v1/animals/{id}        # 猫詳細取得
PUT    /api/v1/animals/{id}        # 猫更新
DELETE /api/v1/animals/{id}        # 猫削除（論理削除）
GET    /api/v1/animals/search      # 猫検索
POST   /api/v1/animals/import      # CSV一括登録
GET    /api/v1/animals/export      # CSV一括出力
```

#### 世話記録API

```
GET    /api/v1/care-logs           # 世話記録一覧取得
POST   /api/v1/care-logs           # 世話記録登録
GET    /api/v1/care-logs/{id}      # 世話記録詳細取得
PUT    /api/v1/care-logs/{id}      # 世話記録更新
GET    /api/v1/care-logs/export    # CSV出力
```

#### 診療記録API

```
GET    /api/v1/medical-records     # 診療記録一覧取得
POST   /api/v1/medical-records     # 診療記録登録
GET    /api/v1/medical-records/{id}# 診療記録詳細取得
PUT    /api/v1/medical-records/{id}# 診療記録更新
```

#### PDF生成API

```
POST   /api/v1/pdf/qr-card         # QRカードPDF生成
POST   /api/v1/pdf/paper-form      # 紙記録フォームPDF生成
POST   /api/v1/pdf/medical-detail  # 診療明細PDF生成
POST   /api/v1/pdf/report          # 帳票PDF生成
```

#### ボランティア管理API

```
GET    /api/v1/volunteers          # ボランティア一覧取得
POST   /api/v1/volunteers          # ボランティア登録
GET    /api/v1/volunteers/{id}     # ボランティア詳細取得
PUT    /api/v1/volunteers/{id}     # ボランティア更新
```

#### 里親管理API

```
GET    /api/v1/applicants          # 里親希望者一覧取得
POST   /api/v1/applicants          # 里親希望者登録
GET    /api/v1/applicants/{id}     # 里親希望者詳細取得
PUT    /api/v1/applicants/{id}     # 里親希望者更新
POST   /api/v1/adoptions           # 譲渡記録登録
PUT    /api/v1/adoptions/{id}      # 譲渡記録更新
```

#### マスターデータAPI

```
GET    /api/v1/procedures          # 処置マスター一覧
POST   /api/v1/procedures          # 処置マスター登録
GET    /api/v1/medications         # 薬剤マスター一覧
POST   /api/v1/medications         # 薬剤マスター登録
GET    /api/v1/vaccines            # ワクチンマスター一覧
POST   /api/v1/vaccines            # ワクチンマスター登録
```

#### ダッシュボードAPI

```
GET    /api/v1/dashboard/stats     # 統計情報取得
GET    /api/v1/dashboard/chart     # グラフデータ取得
```

#### 画像管理API

```
POST   /api/v1/animals/{id}/images # 画像アップロード
GET    /api/v1/animals/{id}/images # 画像一覧取得
DELETE /api/v1/images/{id}         # 画像削除
```

#### OCR API

```
POST   /api/v1/ocr/upload          # 画像/PDFアップロード→OCR処理
GET    /api/v1/ocr/status/{job_id} # OCR処理状況取得
```


### フロントエンド構成

#### 管理画面（AdminLTE）

**レイアウト構造**:
```
┌────────────────────────────────────────────────┐
│ Header (ロゴ、ユーザー名、ログアウト)          │
├────────┬───────────────────────────────────────┤
│        │ Dashboard                             │
│ Side   │ ┌─────────┬─────────┬─────────┐     │
│ bar    │ │保護中   │譲渡可能 │今月譲渡 │     │
│        │ │ 15頭    │ 8頭     │ 3頭     │     │
│ - 猫台帳│ └─────────┴─────────┴─────────┘     │
│ - 世話 │ ┌───────────────────────────────┐   │
│ - 診療 │ │ 世話記録入力数推移（7日間）   │   │
│ - 里親 │ │ [グラフ]                      │   │
│ - マスタ│ └───────────────────────────────┘   │
│ - 帳票 │ ┌───────────────────────────────┐   │
│ - 設定 │ │ 長期保護猫一覧                │   │
│        │ │ [テーブル]                    │   │
│        │ └───────────────────────────────┘   │
└────────┴───────────────────────────────────────┘
```

**主要画面**:
1. ダッシュボード: 統計情報、グラフ、アラート
2. 猫台帳一覧: DataTables（検索、ソート、ページング）
3. 猫詳細: タブ（基本情報、世話記録、診療記録、画像ギャラリー、体重グラフ）
4. 世話記録一覧: DataTables、CSVエクスポート
5. 診療記録一覧: DataTables、PDF/CSV/Excel出力
6. 里親管理: 希望者一覧、面談記録、譲渡記録
7. マスター管理: 処置、薬剤、ワクチン、ボランティア
8. 帳票出力: 日報、週報、月次集計、個別帳票
9. 設定: 団体情報、画像制限、言語、ユーザー管理

#### Publicフォーム（Tailwind CSS + PWA）

**レイアウト構造**:
```
┌────────────────────────────────────────┐
│ [猫の顔写真]                           │
│ たま（ID: 001）                        │
├────────────────────────────────────────┤
│ 記録者: [選択リスト ▼]                │
│                                        │
│ 体重: [____] kg                        │
│ 食事量: [____]                         │
│ 水: [____]                             │
│ 排泄: [____]                           │
│ 投薬: [____]                           │
│ メモ: [________________]               │
│                                        │
│ [前回値コピー]                         │
├────────────────────────────────────────┤
│ [保存]                                 │
└────────────────────────────────────────┘
```

**PWA機能**:
- Service Worker: オフライン対応、キャッシュ管理
- manifest.json: ホーム画面追加、アイコン設定
- IndexedDB: オフライン時のデータ一時保存
- Background Sync: オンライン復帰時の自動同期

### 認証・認可フロー

#### JWT認証管理

```python
from jose import jwt, JWTError
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

# OAuth2スキーム設定
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

# JWT設定
SECRET_KEY = "your-secret-key-here"  # 環境変数から取得
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 2

# JWTアクセストークン生成
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)

    to_encode.update({"exp": expire, "sub": str(data["user_id"])})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# トークン検証
def verify_token(token: str):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = int(payload.get("sub"))
        if user_id is None:
            raise credentials_exception
        return user_id
    except JWTError:
        raise credentials_exception

# 認証依存性
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user_id = verify_token(token)
    user = db.query(User).filter(User.id == user_id).first()
    if user is None or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")
    return user

# ログインエンドポイント
@app.post("/api/v1/auth/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={"user_id": user.id, "role": user.role},
        expires_delta=timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    )
    return {"access_token": access_token, "token_type": "bearer"}

# 保護されたエンドポイント
@app.get("/api/v1/users/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user
```

#### 権限チェック

```python
# デコレータによる権限チェック
@require_role(["admin", "vet"])
async def create_medical_record(request: Request):
    # 診療記録作成処理
    pass

# ロール別権限マトリクス
PERMISSIONS = {
    "admin": ["*"],  # 全権限
    "vet": ["medical:*", "report:read"],
    "staff": ["animal:read", "care:read", "medical:read", "report:*"],
    "read_only": ["*:read"],
    "volunteer": []  # Publicフォームのみ
}
```

### PDF生成フロー

#### QRカード生成

```python
# 1. QRコード生成
qr_url = f"https://necokeeper.example.com/public/care/{animal.id}"
qr_img = qrcode.make(qr_url)

# 2. HTMLテンプレートレンダリング
html = render_template("pdf/qr_card.html", animal=animal, qr_img=qr_img)

# 3. WeasyPrintでPDF生成
pdf = HTML(string=html).write_pdf()

# 4. レスポンス返却
return Response(pdf, media_type="application/pdf")
```

#### 面付けカード生成

```python
# A4用紙に2×5枚配置
animals_list = [animals[i:i+10] for i in range(0, len(animals), 10)]
for page_animals in animals_list:
    html += render_template("pdf/qr_card_grid.html", animals=page_animals)
```

### 多言語対応

#### 対訳ファイル構造

```json
// static/i18n/ja.json
{
  "common": {
    "save": "保存",
    "cancel": "キャンセル",
    "delete": "削除"
  },
  "animal": {
    "name": "名前",
    "pattern": "柄・色",
    "status": "ステータス"
  },
  "care_log": {
    "weight": "体重",
    "food": "食事量"
  }
}

// static/i18n/en.json
{
  "common": {
    "save": "Save",
    "cancel": "Cancel",
    "delete": "Delete"
  },
  "animal": {
    "name": "Name",
    "pattern": "Pattern/Color",
    "status": "Status"
  }
}
```

#### 言語切り替え

```javascript
// フロントエンド（i18next）
i18next.init({
  lng: localStorage.getItem('language') || navigator.language.split('-')[0],
  fallbackLng: 'ja',
  resources: {
    ja: { translation: jaTranslation },
    en: { translation: enTranslation }
  }
});

// バックエンド（Jinja2）
{% set lang = request.cookies.get('language', 'ja') %}
{{ t[lang]['common']['save'] }}
```

## Error Handling

### エラー分類

1. **バリデーションエラー** (400 Bad Request)
   - 必須項目未入力
   - 形式不正（メールアドレス、日付等）
   - 範囲外の値

2. **認証エラー** (401 Unauthorized)
   - ログイン失敗
   - セッション期限切れ

3. **認可エラー** (403 Forbidden)
   - 権限不足

4. **リソース未検出** (404 Not Found)
   - 存在しない猫ID
   - 存在しない記録

5. **サーバーエラー** (500 Internal Server Error)
   - データベース接続エラー
   - PDF生成エラー
   - OCR処理エラー

### エラーレスポンス形式

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "入力内容に誤りがあります",
    "details": [
      {
        "field": "weight",
        "message": "体重は0.1〜50.0の範囲で入力してください"
      }
    ]
  }
}
```

### エラーログ

```python
import logging

logger = logging.getLogger(__name__)

# ログレベル
# INFO: 正常な操作
# WARNING: 警告（ログイン失敗等）
# ERROR: エラー（データベースエラー等）
# CRITICAL: 致命的エラー（システム停止等）

logger.error(
    f"Database error: {str(e)}",
    extra={
        "user_id": user.id,
        "endpoint": request.url.path,
        "method": request.method
    }
)
```

## Testing Strategy

### テスト方針

1. **単体テスト**: 各サービス、ユーティリティ関数
2. **統合テスト**: API エンドポイント
3. **E2Eテスト**: 主要ユーザーフロー（オプション）

### テストツール

**バックエンドテスト:**
- **pytest**: テストフレームワーク
- **pytest-asyncio**: 非同期テスト
- **httpx**: APIテスト
- **faker**: テストデータ生成

**フロントエンドテスト:**
- **Jest**: JavaScriptテストフレームワーク
- **Playwright**: E2Eテスト（オプション）
- **jsdom**: DOM環境シミュレーション

### テストカバレッジ目標

- サービス層: 80%以上
- API層: 70%以上
- 全体: 60%以上

### テスト設計方針（t-wada氏のDDD準拠）

**テスト構造:**
- **ドメインロジックテスト**: ビジネスルールの検証（単体テスト）
- **アプリケーションサービステスト**: ユースケースの検証（統合テスト）
- **インフラストラクチャテスト**: 外部依存の検証（統合テスト）

**テスト例**

```python
# tests/domain/test_animal_domain.py
import pytest
from app.domain.animal import Animal, AnimalStatus

def test_animal_can_be_adopted_when_ready():
    """譲渡可能な猫は譲渡できる（ドメインルール）"""
    animal = Animal(name="たま", status=AnimalStatus.READY_FOR_ADOPTION)
    assert animal.can_be_adopted() is True

def test_animal_cannot_be_adopted_when_under_treatment():
    """治療中の猫は譲渡できない（ビジネスルール）"""
    animal = Animal(name="たま", status=AnimalStatus.UNDER_TREATMENT)
    assert animal.can_be_adopted() is False

# tests/application/test_animal_service.py
@pytest.mark.asyncio
async def test_register_new_animal_use_case(db_session):
    """新しい猫を登録するユースケース"""
    service = AnimalService(db_session)
    command = RegisterAnimalCommand(
        name="たま",
        pattern="三毛",
        gender="female"
    )
    animal = await service.register_animal(command)
    assert animal.name == "たま"
    assert animal.status == AnimalStatus.PROTECTED

# tests/infrastructure/test_animal_repository.py
@pytest.mark.asyncio
async def test_animal_repository_persistence(db_session):
    """動物リポジトリの永続化テスト"""
    repo = AnimalRepository(db_session)
    animal = Animal(name="たま", pattern="三毛")
    saved_animal = await repo.save(animal)
    found_animal = await repo.find_by_id(saved_animal.id)
    assert found_animal.name == "たま"
```


## Deployment

### ホスティングサービス選定

| サービス | 永続化ストレージ | 無料枠 | SQLite対応 | 推奨度 |
|---------|----------------|--------|-----------|--------|
| Render | ○ (Disk) | 750時間/月 | ○ | ★★★ |
| Railway | ○ (Volume) | $5クレジット/月 | ○ | ★★★ |
| Fly.io | ○ (Volume) | 3GB/月 | ○ | ★★☆ |

### Render デプロイ設定

```yaml
# render.yaml
services:
  - type: web
    name: necokeeper
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: DATABASE_URL
        value: /data/app.sqlite3
      - key: SECRET_KEY
        generateValue: true
      - key: PYTHON_VERSION
        value: 3.11.0
    disk:
      name: necokeeper-data
      mountPath: /data
      sizeGB: 1
```

### Railway デプロイ設定

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "uvicorn app.main:app --host 0.0.0.0 --port $PORT",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### Fly.io デプロイ設定

```toml
# fly.toml
app = "necokeeper"
primary_region = "nrt"

[build]
  builder = "paketobuildpacks/builder:base"

[env]
  PORT = "8080"

[http_service]
  internal_port = 8080
  force_https = true
  auto_stop_machines = true
  auto_start_machines = true
  min_machines_running = 0

[[mounts]]
  source = "necokeeper_data"
  destination = "/data"
```

### 環境変数

```bash
# .env.example
DATABASE_URL=sqlite:///data/app.sqlite3
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1
DEBUG=False
LOG_LEVEL=INFO

# オプション（OCR機能）
OCR_ENABLED=False
TESSERACT_PATH=/usr/bin/tesseract
GOOGLE_CLOUD_VISION_API_KEY=
AWS_TEXTRACT_ACCESS_KEY=
```

### バックアップ戦略

#### 自動バックアップ

```python
# app/tasks/backup.py
import shutil
from datetime import datetime
from pathlib import Path

async def backup_database():
    """データベースとメディアファイルをバックアップ"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = Path("/backups")
    backup_dir.mkdir(exist_ok=True)

    # SQLiteバックアップ
    db_path = Path("/data/app.sqlite3")
    backup_db = backup_dir / f"app_{timestamp}.sqlite3"
    shutil.copy2(db_path, backup_db)

    # メディアファイルバックアップ
    media_path = Path("/media")
    backup_media = backup_dir / f"media_{timestamp}.tar.gz"
    shutil.make_archive(backup_media.with_suffix(""), "gztar", media_path)

    # 90日以上前のバックアップを削除
    cutoff = datetime.now() - timedelta(days=90)
    for backup_file in backup_dir.glob("*"):
        if backup_file.stat().st_mtime < cutoff.timestamp():
            backup_file.unlink()
```

#### スケジュール設定

```python
# app/main.py
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()
scheduler.add_job(backup_database, "cron", hour=2, minute=0)  # 毎晩2:00
scheduler.start()
```

## Security Considerations

### セキュリティ対策一覧

1. **認証・認可**
   - bcrypt/passlibによるパスワードハッシュ化
   - JWT + OAuth2 Password Flow認証
   - ログイン試行回数制限（5回失敗で15分ロック）
   - アクセストークン有効期限（2時間）
   - Bearer Token認証（Authorization: Bearer {token}）

2. **入力検証**
   - Pydanticによるバリデーション
   - SQLAlchemy ORMによるSQLインジェクション対策
   - ファイルアップロード検証（拡張子、MIMEタイプ、サイズ）

3. **通信セキュリティ**
   - HTTPS必須（本番環境）
   - HSTS（HTTP Strict Transport Security）
   - Cookie Secure フラグ

4. **データ保護**
   - 個人情報の暗号化（オプション）
   - バックアップの定期実行
   - 監査ログの記録

5. **脆弱性対策**
   - 依存ライブラリの定期更新
   - セキュリティヘッダー設定
   - レート制限（API呼び出し）

### セキュリティヘッダー

```python
# app/middleware/security.py
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response
```

## Performance Optimization

### データベース最適化

1. **インデックス設計**
   - 頻繁に検索されるカラムにインデックス作成
   - 複合インデックスの活用

2. **クエリ最適化**
   - N+1問題の回避（eager loading）
   - ページネーション実装
   - 不要なカラムの除外（select specific columns）

3. **接続プール**
   - SQLAlchemyの接続プール設定
   - 最大接続数: 20

### キャッシュ戦略

```python
# app/cache.py
from functools import lru_cache

@lru_cache(maxsize=128)
def get_active_volunteers():
    """アクティブなボランティア一覧をキャッシュ"""
    return db.query(Volunteer).filter(Volunteer.status == "active").all()
```

### 画像最適化

```python
# app/utils/image.py
from PIL import Image

def optimize_image(image_path: Path, max_size: tuple = (1920, 1080)):
    """画像を最適化（リサイズ、圧縮）"""
    img = Image.open(image_path)
    img.thumbnail(max_size, Image.Resampling.LANCZOS)
    img.save(image_path, optimize=True, quality=85)
```

## Monitoring and Logging

### ログ設定

```python
# app/logging_config.py
import logging
from logging.handlers import RotatingFileHandler

def setup_logging():
    logger = logging.getLogger("necokeeper")
    logger.setLevel(logging.INFO)

    # ファイルハンドラー（ローテーション）
    file_handler = RotatingFileHandler(
        "logs/app.log",
        maxBytes=10485760,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(
        logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
    )
    logger.addHandler(file_handler)

    # コンソールハンドラー
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(
        logging.Formatter("%(levelname)s: %(message)s")
    )
    logger.addHandler(console_handler)
```

### メトリクス収集

```python
# app/middleware/metrics.py
from prometheus_client import Counter, Histogram
import time

request_count = Counter("http_requests_total", "Total HTTP requests", ["method", "endpoint", "status"])
request_duration = Histogram("http_request_duration_seconds", "HTTP request duration")

class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        duration = time.time() - start_time

        request_count.labels(
            method=request.method,
            endpoint=request.url.path,
            status=response.status_code
        ).inc()
        request_duration.observe(duration)

        return response
```

## Migration Strategy

### 初期データ投入

```python
# app/db/init_data.py
async def init_database():
    """初期データを投入"""
    # 初期管理者アカウント
    admin_user = User(
        email="admin@example.com",
        password_hash=hash_password("changeme"),
        name="管理者",
        role="admin"
    )
    db.add(admin_user)

    # サンプル猫データ
    sample_animal = Animal(
        name="サンプル猫",
        pattern="キジトラ",
        gender="female",
        age="成猫",
        status="保護中"
    )
    db.add(sample_animal)

    # サンプルボランティア
    sample_volunteer = Volunteer(
        name="サンプルボランティア",
        status="active"
    )
    db.add(sample_volunteer)

    await db.commit()
```

### データマイグレーション

```python
# alembic/versions/001_initial.py
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.create_table(
        "animals",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(100), nullable=True),
        sa.Column("pattern", sa.String(100), nullable=False),
        # ... 他のカラム
        sa.PrimaryKeyConstraint("id")
    )
    op.create_index("ix_animals_status", "animals", ["status"])

def downgrade():
    op.drop_index("ix_animals_status", table_name="animals")
    op.drop_table("animals")
```

## Future Enhancements

### Phase 2 機能候補

1. **通知機能**
   - メール通知（譲渡決定、診療予定リマインダー）
   - プッシュ通知（PWA）

2. **レポート機能強化**
   - カスタムレポート作成
   - グラフの種類追加（円グラフ、棒グラフ）

3. **SNS連携**
   - 譲渡可能猫の自動投稿（Twitter、Instagram）
   - 画像の自動リサイズ・最適化

4. **モバイルアプリ**
   - React Native / Flutter
   - ネイティブカメラ連携

5. **AI機能**
   - 猫の顔認識
   - 健康状態の異常検知

6. **マルチテナント対応**
   - 複数団体の管理
   - 団体間データ共有

## Appendix

### 開発環境セットアップ

```bash
# Python仮想環境作成
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 依存関係インストール
pip install -r requirements.txt

# データベース初期化
alembic upgrade head
python -m app.db.init_data

# 開発サーバー起動
uvicorn app.main:app --reload --port 8000
```

### 主要ライブラリバージョン

```
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
pydantic==2.5.0
python-multipart==0.0.6
jinja2==3.1.2
weasyprint==60.1
qrcode[pil]==7.4.2
bcrypt==4.1.1
itsdangerous==2.1.2
python-dotenv==1.0.0
alembic==1.12.1
pytest==7.4.3
pytest-asyncio==0.21.1
httpx==0.25.1
```

### 参考資料

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [WeasyPrint Documentation](https://doc.courtbouillon.org/weasyprint/)
- [AdminLTE Documentation](https://adminlte.io/docs/)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [PWA Documentation](https://web.dev/progressive-web-apps/)

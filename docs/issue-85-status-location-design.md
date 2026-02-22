# Issue #85: ステータス・ロケーション管理実装設計書

**最終更新**: 2026-01-20  
**関連Issue**: #85, #83

---

## 1. 概要

猫のステータス・所在地を統一的に管理し、ステータス変更履歴を記録・追跡する機能を実装する。
終端ステータス(ADOPTED/DECEASED)からの復帰時に確認フローを要求し、不用意な変更を防ぐ。

---

## 2. データモデル設計

### 2.1 ステータス定義

| コード | 日本語 | 説明 | 終端 |
|--------|--------|------|------|
| QUARANTINE | 保護中 | 保護・隔離中 | ✗ |
| IN_CARE | 在籍中（施設/カフェ/預かり含む） | 施設/猫カフェ/預かり宅での在籍 | ✗ |
| TRIAL | トライアル中 | 里親候補宅でのトライアル期間 | ✗ |
| ADOPTED | 譲渡済み | 里親に譲渡完了（履歴追跡可・編集可） | ✓ |
| DECEASED | 死亡 | 死亡・安楽死対応（履歴追跡可・編集可） | ✓ |

**遷移ルール**:
- 基本: 任意のステータスから任意のステータスへ遷移可（履歴保存）
- 特例: ADOPTED/DECEASED から他へ遷移する際は確認フロー（UI警告表示）

### 2.2 ロケーションタイプ定義

| コード | 日本語 | 説明 |
|--------|--------|------|
| FACILITY | 施設 | 保護施設・猫カフェ・シェルター |
| FOSTER_HOME | 預かり宅 | 預かりボランティア宅 |
| ADOPTER_HOME | 里親候補宅 | トライアル先（TRIALステータスと通常は紐付く） |

### 2.3 データベーススキーマ変更

#### animals テーブル

```sql
-- 既存
ALTER TABLE animals ADD COLUMN location_type TEXT NOT NULL DEFAULT 'FACILITY';

-- 既存列の変更（status は NOT NULL のままで、英コード値に统一）
-- デフォルト値: 'QUARANTINE'
-- 注：マイグレーションで既存値は 'TRIAL' に統一

-- インデックス: location_type で集計時の検索高速化
CREATE INDEX ix_animals_location_type ON animals(location_type);
```

#### status_history テーブル（汎用化）

現行スキーマを拡張し、ステータス・ロケーション変更両方を記録

```sql
CREATE TABLE status_history (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  animal_id INTEGER NOT NULL,
  field TEXT NOT NULL,                   -- 'status' or 'location_type'
  old_value TEXT,                        -- 変更前値（初回登録時は NULL）
  new_value TEXT NOT NULL,               -- 変更後値
  reason TEXT,                           -- 変更理由（任意）
  changed_by INTEGER,                    -- ユーザーID（任意）
  changed_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  
  FOREIGN KEY (animal_id) REFERENCES animals(id) ON DELETE CASCADE,
  FOREIGN KEY (changed_by) REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX ix_status_history_animal_id ON status_history(animal_id);
CREATE INDEX ix_status_history_changed_at ON status_history(changed_at);
CREATE INDEX ix_status_history_field ON status_history(field);
```

**マイグレーション手順**:
1. `location_type` 列を追加（デフォルト 'FACILITY'）
2. 既存データ: 全件 status='TRIAL' に統一
3. `status_history` スキーマ拡張（新列追加・既存列は保持）
   - 移行後は `old_status`/`new_status` は廃止予定（段階的）
4. インデックス追加

---

## 3. API設計

### 3.1 メタエンドポイント

#### GET /api/v1/meta/statuses

ステータス一覧を取得（i18n対応）

**リクエスト**:
```
GET /api/v1/meta/statuses HTTP/1.1
Accept-Language: ja
```

**レスポンス** (200 OK):
```json
[
  {
    "code": "QUARANTINE",
    "label": "保護中",
    "is_terminal": false
  },
  {
    "code": "IN_CARE",
    "label": "在籍中（施設/カフェ/預かり含む）",
    "is_terminal": false
  },
  {
    "code": "TRIAL",
    "label": "トライアル中",
    "is_terminal": false
  },
  {
    "code": "ADOPTED",
    "label": "譲渡済み",
    "is_terminal": true
  },
  {
    "code": "DECEASED",
    "label": "死亡",
    "is_terminal": true
  }
]
```

**支援言語**: ja（日本語）/ en（英語、デフォルトは日本語）

---

#### GET /api/v1/meta/location-types

ロケーション一覧を取得（i18n対応）

**リクエスト**:
```
GET /api/v1/meta/location-types HTTP/1.1
Accept-Language: ja
```

**レスポンス** (200 OK):
```json
[
  {
    "code": "FACILITY",
    "label": "施設（保護施設・猫カフェ・シェルター）"
  },
  {
    "code": "FOSTER_HOME",
    "label": "預かりボランティア宅"
  },
  {
    "code": "ADOPTER_HOME",
    "label": "里親候補宅（トライアル先）"
  }
]
```

---

### 3.2 ステータス変更（既存エンドポイント拡張）

#### PATCH /api/v1/animals/{animal_id}

猫情報を更新（ステータス・ロケーション含む）

**リクエスト** - 通常更新:
```json
{
  "status": "IN_CARE",
  "location_type": "FACILITY"
}
```

**リクエスト** - 終端ステータスから復帰（確認前）:
```json
{
  "status": "IN_CARE"
}
```

**レスポンス** - 409 Conflict (確認が必要):
```json
{
  "status_code": 409,
  "detail": "確認が必要です",
  "requires_confirmation": true,
  "warning_code": "LEAVE_TERMINAL_STATUS",
  "message": "この個体は譲渡済みです。状態を変更しますか？"
}
```

**リクエスト** - 終端ステータスから復帰（確認後）:
```json
{
  "status": "IN_CARE",
  "confirm": true,
  "reason": "誤登録の修正"
}
```

**レスポンス** - 200 OK:
```json
{
  "id": 1,
  "name": "タマ",
  "status": "IN_CARE",
  "location_type": "FACILITY",
  "updated_at": "2026-01-20T12:34:56+09:00"
}
```

**バリデーション**:
- `status`: QUARANTINE, IN_CARE, TRIAL, ADOPTED, DECEASED のいずれか（必須の場合）
- `location_type`: FACILITY, FOSTER_HOME, ADOPTER_HOME のいずれか（必須の場合）
- `confirm`: true の場合のみ確認をバイパス
- `reason`: 任意（最大 500 文字）

---

### 3.3 ステータス履歴取得（新規）

#### GET /api/v1/animals/{animal_id}/status-history

ステータス・ロケーション変更履歴を取得

**リクエスト**:
```
GET /api/v1/animals/1/status-history?page=1&page_size=20 HTTP/1.1
```

**レスポンス** (200 OK):
```json
{
  "items": [
    {
      "id": 5,
      "animal_id": 1,
      "field": "status",
      "old_value": "QUARANTINE",
      "new_value": "IN_CARE",
      "reason": "医学検査完了",
      "changed_by": 1,
      "changed_at": "2026-01-20T10:00:00+09:00"
    },
    {
      "id": 4,
      "animal_id": 1,
      "field": "location_type",
      "old_value": "FACILITY",
      "new_value": "FOSTER_HOME",
      "reason": null,
      "changed_by": 1,
      "changed_at": "2026-01-20T09:30:00+09:00"
    }
  ],
  "total": 10,
  "page": 1,
  "page_size": 20,
  "total_pages": 1
}
```

---

## 4. UI警告フロー

### 4.1 フロー図

```
[ステータス変更フォーム]
        ↓
  [確定ボタン]
        ↓
  APIリクエスト
  { status: "IN_CARE" }
        ↓
  [409 Conflict + requires_confirmation=true?]
  /
  \
  ├─YES─→ [警告モーダル表示]
  |       「この個体は譲渡済みです。状態を変更しますか？」
  |       [キャンセル] [続行]
  |               ↓
  |       再度APIリクエスト
  |       { status: "IN_CARE", confirm: true, reason: "理由（任意）" }
  |               ↓
  |       200 OK → 更新完了
  |
  └─NO──→ 200 OK → 更新完了
```

### 4.2 モーダル文言（日本語案）

**タイトル**: 「ステータス変更確認」

**メッセージ（例）**:
- ADOPTED→他: 「この個体は『譲渡済み』として登録されています。状態を変更しますか？」
- DECEASED→他: 「この個体は『死亡』として登録されています。状態を変更しますか？」

**理由入力**（任意）:
- プレイスホルダー: 「変更理由を記入してください（任意）」
- 最大文字数: 500 文字

**ボタン**:
- キャンセル（灰色）
- 続行（赤色・警告色）

---

## 5. サービス層実装方針

### 5.1 AnimalService

```python
def update_animal(
    db: Session, 
    animal_id: int, 
    animal_data: AnimalUpdate, 
    user_id: int,
    confirm: bool = False  # 新規パラメータ
) -> Animal | tuple[dict, int]:
    """
    猫情報を更新し、必要に応じて確認フロー＆履歴記録
    
    Returns:
      - 通常: Animal
      - 確認要: ({requires_confirmation, warning_code, message}, 409)
    """
    # status/location_type の変更検出
    # 終端から復帰 → confirm なし → 409 + requires_confirmation
    # confirm=true → 更新 + 履歴記録
    pass

def record_status_change(
    db: Session,
    animal_id: int,
    field: str,  # "status" or "location_type"
    old_value: str,
    new_value: str,
    user_id: int,
    reason: str | None = None
) -> StatusHistory:
    """
    ステータス・ロケーション変更を履歴に記録
    """
    pass
```

### 5.2 バリデーション

Enum（FastAPI, Pydantic）を使用してコード値を厳格化

```python
from enum import Enum

class AnimalStatus(str, Enum):
    QUARANTINE = "QUARANTINE"
    IN_CARE = "IN_CARE"
    TRIAL = "TRIAL"
    ADOPTED = "ADOPTED"
    DECEASED = "DECEASED"

class LocationType(str, Enum):
    FACILITY = "FACILITY"
    FOSTER_HOME = "FOSTER_HOME"
    ADOPTER_HOME = "ADOPTER_HOME"
```

---

## 6. テスト戦略

### 6.1 ユニットテスト対象

- ステータス遷移ルール（自由遷移 + 終端確認）
- 履歴記録（status/location_type 変更の記録）
- 確認フロー（409 → confirm=true）
- Enumバリデーション（無効値の拒否）

### 6.2 統合テスト対象

- ステータス変更API（確認なし → 正常）
- ステータス変更API（終端から復帰 → 409 → confirm=true → 正常）
- メタAPI（言語別レスポンス）
- ダッシュボード集計（新コード値での絞り込み）

---

## 7. マイグレーション実行手順

### 7.1 前準備

```bash
# 現在のデータベースバージョンを確認
alembic current

# （オプション）バックアップを取得
cp data/necokeeper.db data/necokeeper.db.backup.20260120
```

### 7.2 マイグレーション作成

```bash
alembic revision --autogenerate -m "Add location_type and unify status values to TRIAL"
```

### 7.3 マイグレーション内容（例）

```python
# versions/add_location_type_and_unify_status.py

def upgrade():
    # 1. location_type 列を追加（デフォルト FACILITY）
    op.add_column('animals', sa.Column('location_type', sa.String(20), 
                                       nullable=False, server_default='FACILITY'))
    
    # 2. 既存 status を全件 'TRIAL' に統一
    op.execute("UPDATE animals SET status = 'TRIAL'")
    
    # 3. status_history スキーマ拡張
    # 新列追加（既存列は保持）
    op.add_column('status_history', sa.Column('field', sa.String(50), nullable=True))
    op.add_column('status_history', sa.Column('old_value', sa.String(20), nullable=True))
    op.add_column('status_history', sa.Column('new_value', sa.String(20), nullable=True))
    
    # 4. インデックス追加
    op.create_index('ix_animals_location_type', 'animals', ['location_type'])

def downgrade():
    # 逆操作
    op.drop_index('ix_animals_location_type', 'animals')
    op.drop_column('status_history', 'new_value')
    op.drop_column('status_history', 'old_value')
    op.drop_column('status_history', 'field')
    op.drop_column('animals', 'location_type')
```

### 7.4 実行

```bash
# テスト環境で実行
alembic upgrade head

# 本番環境での実行（ダウンタイム: 数秒～1分）
```

---

## 8. デプロイ順序

1. **バックエンド実装 + テスト**
   - モデル、スキーマ、サービス層
   - API（メタ + 確認フロー）
   - マイグレーション

2. **マイグレーション実行**
   - テスト環境で確認
   - 本番実行

3. **フロントエンド実装**
   - i18nメタの取得・キャッシュ
   - 警告モーダル
   - ステータス表示の刷新（コード→ラベル変換）

4. **統合テスト & リリース**

---

## 9. 既知の制限事項・今後の検討

- **検索除外**: 検索時に終端ステータスの除外機構は別Issueで検討（現在はフィルタ不要）
- **一括操作**: 複数猫のステータス一括更新は未対応（今後必要なら検討）
- **履歴統計**: 変更頻度の分析は後続機能として検討
- **ロケーション履歴**: 今後、ロケーション変更の頻度・パターン分析が必要ならAPI拡張

---

## 10. 参考資料

- Issue #85: ステータス変更時の処理
- Issue #83: 確定事項コメント
- [docs/automation-api-guide.md](./automation-api-guide.md)
- [docs/service-layer-test-coverage-improvement.md](./service-layer-test-coverage-improvement.md)

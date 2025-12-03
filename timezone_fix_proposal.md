# タイムゾーン問題の修正案

## 問題の詳細

### 現象
- **Log Date**: 2025-12-02（JST基準）
- **Created At**: 12/1/2025, 5:25:28 PM（UTC 17:25 = JST 翌日 02:25）
- **Last Updated**: 12/1/2025, 5:25:28 PM（UTC 17:25 = JST 翌日 02:25）

### 原因
1. SQLiteの`func.now()`と`func.current_date()`はUTCで動作
2. JavaScriptの`toLocaleString()`はブラウザのタイムゾーン（JST）で表示
3. 結果として、UTC 17:25（12/1）がJST 02:25（12/2）となり、log_dateと1日ずれる

---

## 修正案の比較

| 項目 | 案1: DB統一（推奨） | 案2: アプリ変換 | 案3: フロント表示 |
|------|-------------------|----------------|------------------|
| **実装難易度** | 中（マイグレーション必要） | 中（各所に変換処理） | 低（JS修正のみ） |
| **データ整合性** | ◎ 完全に統一 | ○ 変換で対応 | △ 表示のみ |
| **既存データ** | 要変換 | 影響なし | 影響なし |
| **保守性** | ◎ 一箇所で管理 | △ 各所に分散 | △ 表示のみ |
| **推奨度** | ★★★ | ★★☆ | ★☆☆ |

---

## 案1: データベースレベルでJSTに統一（推奨）

### 概要
データベースに保存する時点でJSTに変換し、すべてのタイムスタンプをJSTで統一します。

### 実装内容

#### 1. タイムゾーン設定の追加（.env）
```env
# タイムゾーン設定
TZ=Asia/Tokyo
TIMEZONE=Asia/Tokyo
```

#### 2. データベースモデルの修正
```python
# app/models/care_log.py
from datetime import datetime
import pytz

JST = pytz.timezone('Asia/Tokyo')

def get_jst_now():
    """JST現在時刻を取得"""
    return datetime.now(JST).replace(tzinfo=None)

def get_jst_date():
    """JST現在日付を取得"""
    return datetime.now(JST).date()

class CareLog(Base):
    # タイムスタンプ（JSTで保存）
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=get_jst_now,  # func.now() → get_jst_now
        comment="記録日時（JST）",
    )

    last_updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=get_jst_now,
        onupdate=get_jst_now,  # func.now() → get_jst_now
        comment="最終更新日時（JST）",
    )

    log_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        default=get_jst_date,  # func.current_date() → get_jst_date
        comment="記録日（年月日、JST）",
    )
```

#### 3. Alembicマイグレーション
```python
# alembic/versions/YYYYMMDD_HHMM_convert_timestamps_to_jst.py
"""Convert timestamps to JST

Revision ID: xxxxx
Revises: yyyyy
Create Date: 2025-12-03 10:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime, timedelta

def upgrade():
    # 既存データをUTC→JSTに変換（+9時間）
    op.execute("""
        UPDATE care_logs
        SET created_at = datetime(created_at, '+9 hours'),
            last_updated_at = datetime(last_updated_at, '+9 hours')
    """)

    # 他のテーブルも同様に変換
    op.execute("""
        UPDATE animals
        SET created_at = datetime(created_at, '+9 hours'),
            last_updated_at = datetime(last_updated_at, '+9 hours')
    """)

def downgrade():
    # JST→UTCに戻す（-9時間）
    op.execute("""
        UPDATE care_logs
        SET created_at = datetime(created_at, '-9 hours'),
            last_updated_at = datetime(last_updated_at, '-9 hours')
    """)

    op.execute("""
        UPDATE animals
        SET created_at = datetime(created_at, '-9 hours'),
            last_updated_at = datetime(last_updated_at, '-9 hours')
    """)
```

#### 4. requirements.txtに追加
```txt
pytz==2024.1
```

### メリット
- ✅ データベースレベルで統一、一貫性が高い
- ✅ フロントエンドでの変換不要
- ✅ 将来的な拡張性が高い

### デメリット
- ⚠️ マイグレーションが必要
- ⚠️ 既存データの変換が必要

---

## 案2: アプリケーションレベルでJST変換

### 概要
データベースはUTCのまま、アプリケーション層でJSTに変換します。

### 実装内容

#### 1. ユーティリティ関数の追加
```python
# app/utils/timezone.py
from datetime import datetime
import pytz

JST = pytz.timezone('Asia/Tokyo')
UTC = pytz.utc

def utc_to_jst(dt: datetime) -> datetime:
    """UTC→JST変換"""
    if dt.tzinfo is None:
        dt = UTC.localize(dt)
    return dt.astimezone(JST).replace(tzinfo=None)

def jst_to_utc(dt: datetime) -> datetime:
    """JST→UTC変換"""
    if dt.tzinfo is None:
        dt = JST.localize(dt)
    return dt.astimezone(UTC).replace(tzinfo=None)

def get_jst_now() -> datetime:
    """JST現在時刻"""
    return datetime.now(JST).replace(tzinfo=None)

def get_jst_date():
    """JST現在日付"""
    return datetime.now(JST).date()
```

#### 2. スキーマでの変換
```python
# app/schemas/care_log.py
from app.utils.timezone import utc_to_jst

class CareLogResponse(CareLogBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    last_updated_at: datetime

    @field_validator('created_at', 'last_updated_at', mode='before')
    @classmethod
    def convert_to_jst(cls, v: datetime) -> datetime:
        """UTC→JST変換"""
        if v:
            return utc_to_jst(v)
        return v
```

#### 3. サービス層での変換
```python
# app/services/care_log_service.py
from app.utils.timezone import get_jst_now, get_jst_date

def create_care_log(db: Session, care_log_data: CareLogCreate) -> CareLog:
    # log_dateをJSTで設定
    if not care_log_data.log_date:
        care_log_data.log_date = get_jst_date()

    care_log = CareLog(**care_log_data.model_dump())
    db.add(care_log)
    db.commit()
    db.refresh(care_log)
    return care_log
```

### メリット
- ✅ マイグレーション不要
- ✅ 既存データに影響なし
- ✅ 段階的に実装可能

### デメリット
- ⚠️ 変換処理が各所に必要
- ⚠️ 保守性が低い

---

## 案3: フロントエンドでタイムゾーン表示を統一

### 概要
バックエンドは変更せず、フロントエンドでUTC→JST変換して表示します。

### 実装内容

#### 1. JavaScriptでの変換関数
```javascript
// app/static/js/admin/common.js

/**
 * UTC文字列をJSTに変換してフォーマット
 * @param {string} utcString - UTC日時文字列
 * @returns {string} - JST日時文字列
 */
function formatDateTimeJST(utcString) {
  if (!utcString) return '-';

  // UTC文字列をDateオブジェクトに変換
  const utcDate = new Date(utcString + 'Z'); // 'Z'を追加してUTCとして解釈

  // JSTでフォーマット
  const locale = currentLanguage === 'en' ? 'en-US' : 'ja-JP';
  return utcDate.toLocaleString(locale, {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    timeZone: 'Asia/Tokyo'
  });
}

// グローバルに公開
window.formatDateTimeJST = formatDateTimeJST;
```

#### 2. care_log_detail.jsの修正
```javascript
// app/static/js/admin/care_log_detail.js

// 修正前
${new Date(careLog.created_at).toLocaleString(i18next.language === 'en' ? 'en-US' : 'ja-JP')}

// 修正後
${formatDateTimeJST(careLog.created_at)}
```

### メリット
- ✅ バックエンド変更不要
- ✅ 実装が簡単

### デメリット
- ⚠️ 表示のみの対応
- ⚠️ データの不整合は残る
- ⚠️ すべてのJavaScriptファイルを修正する必要がある

---

## 推奨実装: 案1（データベースレベルでJST統一）

### 理由
1. **データ整合性**: すべてのタイムスタンプがJSTで統一される
2. **保守性**: 一箇所（モデル層）で管理できる
3. **拡張性**: 将来的な機能追加に対応しやすい
4. **パフォーマンス**: 変換処理が最小限

### 実装手順
1. `pytz`をインストール: `pip install pytz`
2. `app/utils/timezone.py`を作成
3. すべてのモデルの`created_at`、`last_updated_at`を修正
4. Alembicマイグレーションを作成
5. マイグレーション実行: `alembic upgrade head`
6. テスト実行: `pytest`

### 影響範囲
- **モデル**: Animal, CareLog, MedicalRecord, User, Volunteer など
- **マイグレーション**: 既存データの変換（+9時間）
- **テスト**: タイムスタンプ関連のテストを修正

---

## 次のステップ

どの案を採用するか決定してください：

1. **案1を採用**: マイグレーションとモデル修正を実装
2. **案2を採用**: ユーティリティ関数とスキーマ修正を実装
3. **案3を採用**: JavaScript修正のみ実装

推奨は**案1**ですが、既存データへの影響を最小限にしたい場合は**案2**も検討できます。

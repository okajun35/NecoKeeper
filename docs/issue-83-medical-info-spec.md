# Issue #83: プロフィールに医療情報を追加する - 仕様書

## 概要

保護猫の個体情報（Animal モデル）に医療・状態情報を追加し、ワクチン接種履歴を管理する新規テーブルを作成する。

**Issue**: [#83 プロフィールに医療情報を入れる](https://github.com/okajun35/NecoKeeper/issues/83)

---

## 設計方針

| 項目 | 繰り返す | 履歴重要 | 保持方法 |
|------|---------|---------|---------|
| ワクチン | ◯ | ◯ | 別テーブル（VaccinationRecord） |
| FIV/FeLV検査結果 | △ | △ | Animal に直書き |
| 避妊・去勢 | ✕ | ✕ | Animal に直書き |

---

## 1. Animal モデル拡張

### 追加フィールド

#### FIV/FeLV 検査結果

| フィールド | 型 | 初期値 | 説明 |
|-----------|-----|--------|------|
| `fiv_positive` | `bool \| None` | `None` | FIV検査結果（True=陽性, False=陰性, None=不明） |
| `felv_positive` | `bool \| None` | `None` | FeLV検査結果（True=陽性, False=陰性, None=不明） |

- **目的**: ダッシュボードで最新状態のみを即参照可能にする
- **検査日**: 今回スコープ外（将来拡張として `fiv_tested_on`, `felv_tested_on` を検討可能）

#### 避妊・去勢

| フィールド | 型 | 初期値 | 説明 |
|-----------|-----|--------|------|
| `is_sterilized` | `bool \| None` | `None` | 避妊・去勢状態（True=済, False=未, None=不明） |
| `sterilized_on` | `date \| None` | `None` | 避妊・去勢実施日（任意） |

- **理由**: 生涯で1回しか行わない処置のため履歴管理不要

### 追加インデックス

- `ix_animals_fiv_positive`
- `ix_animals_felv_positive`
- `ix_animals_is_sterilized`

---

## 2. VaccinationRecord テーブル（新規作成）

ワクチン接種履歴を管理する。

### テーブル構成

| フィールド | 型 | 必須/任意 | 説明 |
|-----------|-----|---------|------|
| `id` | `int` | 必須 | 主キー（自動採番） |
| `animal_id` | `int` | 必須 | 猫ID（外部キー → animals.id） |
| `vaccine_category` | `str` (enum) | 必須 | ワクチン種別 |
| `administered_on` | `date` | 必須 | 接種日（核となるフィールド） |
| `next_due_on` | `date \| None` | 任意 | 次回予定日（ユーザ入力、自動計算なし） |
| `memo` | `text \| None` | 任意 | 備考（ロット番号等） |
| `created_at` | `datetime` | 自動 | 作成日時 |
| `updated_at` | `datetime` | 自動 | 更新日時 |

### vaccine_category（ワクチン種別）

「どの病気のワクチンを打ったか」ではなく「どのワクチンを打ったか」を記録する設計。

| 値 | 内容 | 一般家庭での必要性 |
|----|------|------------------|
| `3core` | FVR+FCV+FPV（3種混合） | ◎ 基本 |
| `4core` | 3種＋FeLV（4種混合） | ○ 条件付き |
| `5core` | 4種＋クラミジア（5種混合） | △ ほぼ不要 |

### 接種状況の判定ロジック

別カラムで `is_vaccinated` を持たず、レコードの有無で判定：

- **接種済**: 該当カテゴリのレコードが1件以上存在
- **未接種**: 0件
- **期限切れ**: 最新レコードの `next_due_on` が過去日
- **近日**: `next_due_on` が30日以内

### インデックス

- `ix_vaccination_records_animal_id`
- `ix_vaccination_records_administered_on`

---

## 3. Enum 定義

`app/utils/enums.py` に追加：

```python
class VaccineCategoryEnum(str, Enum):
    """ワクチン種別"""

    VACCINE_3CORE = "3core"   # FVR+FCV+FPV（3種混合）
    VACCINE_4CORE = "4core"   # 3種＋FeLV（4種混合）
    VACCINE_5CORE = "5core"   # 4種＋クラミジア（5種混合）

    def display_name_ja(self) -> str:
        """日本語表示名"""
        names = {
            VaccineCategoryEnum.VACCINE_3CORE: "3種",
            VaccineCategoryEnum.VACCINE_4CORE: "4種",
            VaccineCategoryEnum.VACCINE_5CORE: "5種",
        }
        return names.get(self, self.value)

    def display_name_en(self) -> str:
        """英語表示名"""
        names = {
            VaccineCategoryEnum.VACCINE_3CORE: "3-in-1",
            VaccineCategoryEnum.VACCINE_4CORE: "4-in-1",
            VaccineCategoryEnum.VACCINE_5CORE: "5-in-1",
        }
        return names.get(self, self.value)
```

### 表示ラベル一覧

| Enum値 | DB値 | 日本語表示 | 英語表示 | 内容 |
|--------|------|-----------|---------|------|
| `VACCINE_3CORE` | `3core` | 3種 | 3-in-1 | FVR+FCV+FPV |
| `VACCINE_4CORE` | `4core` | 4種 | 4-in-1 | 3種＋FeLV |
| `VACCINE_5CORE` | `5core` | 5種 | 5-in-1 | 4種＋クラミジア |

※ FIV/FeLV検査結果・避妊去勢は三値bool運用のため Enum 不要

---

## 4. 廃止項目

- `vaccine_label`（3種/4種/5種/不明）: 混乱防止のため廃止。`vaccine_category` で種別を一本化。

---

## 5. API/Schema 方針

### Animal

- 三値bool（`fiv_positive`, `felv_positive`, `is_sterilized`）+ 日付（任意）の受け渡し
- 表示: 「陽性/陰性/不明」「済/未/不明」

### VaccinationRecord

- `vaccine_category`: enum 文字列で受け渡し
- `administered_on`: 必須
- `next_due_on`: 任意（自動計算なし、ユーザ入力）

---

## 6. Alembic マイグレーション

### animals テーブル

追加カラム:
- `fiv_positive` (Boolean, nullable)
- `felv_positive` (Boolean, nullable)
- `is_sterilized` (Boolean, nullable)
- `sterilized_on` (Date, nullable)

追加インデックス:
- `ix_animals_fiv_positive`
- `ix_animals_felv_positive`
- `ix_animals_is_sterilized`

### vaccination_records テーブル（新規作成）

```sql
CREATE TABLE vaccination_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    animal_id INTEGER NOT NULL REFERENCES animals(id) ON DELETE CASCADE,
    vaccine_category VARCHAR(20) NOT NULL,
    administered_on DATE NOT NULL,
    next_due_on DATE,
    memo TEXT,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL
);

CREATE INDEX ix_vaccination_records_animal_id ON vaccination_records(animal_id);
CREATE INDEX ix_vaccination_records_administered_on ON vaccination_records(administered_on);
```

---

## 7. 確認履歴

- [x] VaccinationRecord テーブル作成: 確定
- [x] vaccine_category の選択肢: 3core, 4core, 5core
- [x] vaccine_label: 廃止
- [x] 検査日（fiv_tested_on, felv_tested_on）: スコープ外
- [x] 避妊・去勢: 今回に含める
- [x] インデックス: 追加する
- [x] memo: text 型

---

## 作成日

2026-01-27

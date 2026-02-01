# Issue #87: ダッシュボード上段カード改善 仕様書

## 概要

管理画面ダッシュボードの統計カードを改善し、より実用的な情報を表示する。

## 現状の問題点

| カード | 現在のロジック | 問題点 |
|--------|---------------|--------|
| 保護中 | `QUARANTINE` のみ | 隔離中だけでなく在籍中全体を表示すべき |
| 譲渡可能 | `TRIAL` のみ | 譲渡可能な猫（IN_CARE + TRIAL）を表示すべき |
| ボランティア | アクティブ人数 | 優先度が低く、他の情報を優先すべき |
| 今日の記録 | 今日のCareLog数 | 問題なし（現状維持） |

## 改善後のカード構成

### 1. 在籍中（resident_count）

- **表示名**: 在籍中
- **ロジック**: `status IN (QUARANTINE, IN_CARE, TRIAL)`
- **遷移先**: `/admin/animals?status=ACTIVE`
- **色**: indigo（既存色維持）
- **アイコン**: 🏠 または既存アイコン

### 2. 譲渡可能（adoptable_count）

- **表示名**: 譲渡可能
- **ロジック**: `status IN (IN_CARE, TRIAL)`
- **遷移先**: `/admin/animals?status=IN_CARE,TRIAL`
- **色**: green（既存色維持）
- **アイコン**: 既存アイコン

### 3. 今日の記録（today_logs_count）

- **表示名**: 今日の記録
- **ロジック**: 今日のCareLog数（現状維持）
- **遷移先**: `/admin/care-logs`
- **色**: blue（既存色維持）
- **アイコン**: 既存アイコン

### 4. FIV陽性（fiv_positive_count）【新規】

- **表示名**: FIV陽性
- **ロジック**: 在籍中 かつ `fiv_positive = True`
  - 在籍中 = `status IN (QUARANTINE, IN_CARE, TRIAL)`
- **遷移先**: `/admin/animals?fiv_positive=true`
- **色**: 他カードと同じ色調（警告色は使用しない）
- **アイコン**: 適切なアイコン

### 5. FeLV陽性（felv_positive_count）【新規】

- **表示名**: FeLV陽性
- **ロジック**: 在籍中 かつ `felv_positive = True`
  - 在籍中 = `status IN (QUARANTINE, IN_CARE, TRIAL)`
- **遷移先**: `/admin/animals?felv_positive=true`
- **色**: 他カードと同じ色調（警告色は使用しない）
- **アイコン**: 適切なアイコン

### 削除するカード

- **ボランティア**: 優先度が低いため削除

## API変更

### エンドポイント

`GET /api/v1/dashboard/stats`

### レスポンススキーマ（変更後）

```python
class DashboardStats(BaseModel):
    resident_count: int           # 在籍中の猫数（旧: protected_count）
    adoptable_count: int          # 譲渡可能な猫数
    today_logs_count: int         # 今日の記録数
    fiv_positive_count: int       # FIV陽性の猫数【新規】
    felv_positive_count: int      # FeLV陽性の猫数【新規】
    total_animals: int            # 総猫数
    treatment_count: int          # 治療中の猫数
    # active_volunteers_count: 削除
```

### カウントロジック

```python
# 在籍中（resident_count）
RESIDENT_STATUSES = [
    AnimalStatus.QUARANTINE.value,
    AnimalStatus.IN_CARE.value,
    AnimalStatus.TRIAL.value,
]
resident_count = db.query(Animal).filter(
    Animal.status.in_(RESIDENT_STATUSES)
).count()

# 譲渡可能（adoptable_count）
ADOPTABLE_STATUSES = [
    AnimalStatus.IN_CARE.value,
    AnimalStatus.TRIAL.value,
]
adoptable_count = db.query(Animal).filter(
    Animal.status.in_(ADOPTABLE_STATUSES)
).count()

# FIV陽性（fiv_positive_count）
fiv_positive_count = db.query(Animal).filter(
    Animal.status.in_(RESIDENT_STATUSES),
    Animal.fiv_positive == True
).count()

# FeLV陽性（felv_positive_count）
felv_positive_count = db.query(Animal).filter(
    Animal.status.in_(RESIDENT_STATUSES),
    Animal.felv_positive == True
).count()
```

## フロントエンド変更

### テンプレート（dashboard.html）

1. 「保護中」カードのラベルを「在籍中」に変更
2. ボランティアカードを削除
3. FIV陽性カードを追加
4. FeLV陽性カードを追加
5. 各カードにクリック遷移リンク（`<a>`タグ）を追加

### JavaScript（dashboard.js）

1. `protected_count` → `resident_count` に変更
2. `active_volunteers_count` 関連のコードを削除
3. `fiv_positive_count` を新しいカードにバインド
4. `felv_positive_count` を新しいカードにバインド
5. 各カードのクリックイベント設定（リンク対応）

## Animals一覧フィルター追加

`/admin/animals` で `fiv_positive=true` / `felv_positive=true` クエリパラメータをサポートする必要がある。

### ロジック

```python
if fiv_positive == "true":
    query = query.filter(Animal.fiv_positive == True)

if felv_positive == "true":
    query = query.filter(Animal.felv_positive == True)
```

## テスト追加

### ダッシュボードAPIテスト

1. `test_resident_count_includes_quarantine_in_care_trial`
   - QUARANTINE, IN_CARE, TRIAL の猫がすべてカウントされることを確認

2. `test_adoptable_count_includes_in_care_and_trial`
   - IN_CARE, TRIAL の猫がカウントされることを確認

3. `test_fiv_positive_count_only_resident_cats`
   - 在籍中かつ FIV 陽性の猫のみカウントされることを確認
   - 譲渡済み/死亡の猫はカウントされないことを確認

4. `test_felv_positive_count_only_resident_cats`
   - 在籍中かつ FeLV 陽性の猫のみカウントされることを確認
   - 譲渡済み/死亡の猫はカウントされないことを確認

## 実装順序

1. [ ] `docs/issue-87-dashboard-cards-spec.md` 作成（本ドキュメント）
2. [ ] `app/api/v1/dashboard.py` - スキーマ・ロジック修正
3. [ ] `app/templates/admin/dashboard.html` - テンプレート修正
4. [ ] `app/static/js/admin/dashboard.js` - JavaScript修正
5. [ ] `app/api/v1/admin_pages.py` - animals一覧フィルター追加
6. [ ] `tests/api/test_dashboard.py` - テスト追加
7. [ ] `make test` で動作確認
8. [ ] `agent-browser` でUI確認

## 関連Issue

- Issue #87: ダッシュボードの上段カードを考える

## 備考

- 「要対応」カード（POC削除候補）は別タスクとして扱う
- 未避妊/去勢カード、ワクチン期限切れカードは現段階では不要
- FIV陽性・FeLV陽性カードは警告色ではなく、他カードと同じ色調を使用

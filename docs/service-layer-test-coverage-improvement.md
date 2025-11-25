# サービス層テストカバレッジ改善ガイド

> 作成日: 2025-11-25
> ステータス: 待機中（UI POC完了後に実施予定）

## 📊 現在のカバレッジ状況

| サービスファイル | カバレッジ | 未テスト行 | テストファイル有無 |
|-----------------|----------|------------|-----------------|
| `user_service.py` | **33.33%** | 43-62 | ❌ なし |
| `medical_record_service.py` | **68.25%** | 多数 | ❌ なし |
| `medical_action_service.py` | **69.57%** | 57-59, 123, 194-196等 | ❌ なし |
| `volunteer_service.py` | **77.27%** | 58-61, 100-102等 | ✅ あり |
| `animal_service.py` | **74.55%** | 59-62, 96-98等 | ✅ あり |

---

## 🔴 最優先: 新規テストファイル作成が必要

### 1. `tests/services/test_user_service.py` (新規)

**対象ファイル**: `app/services/user_service.py`

**未テスト範囲**: `list_users`関数全体（43-62行目）

**必要なテストケース**:

| テストケース名 | 説明 |
|---------------|------|
| `test_list_users_default_pagination` | デフォルトのページネーション動作 |
| `test_list_users_filter_by_role` | ロールフィルター（admin, vet, staff） |
| `test_list_users_filter_by_is_active` | アクティブ状態フィルター |
| `test_list_users_combined_filters` | 複数フィルター組み合わせ |
| `test_list_users_empty_result` | 結果0件の場合 |
| `test_list_users_total_pages_calculation` | 総ページ数計算の検証 |

**推定作業時間**: 1.5-2時間

---

### 2. `tests/services/test_medical_record_service.py` (新規)

**対象ファイル**: `app/services/medical_record_service.py`

**未テスト範囲**:

| 行番号 | 内容 |
|--------|------|
| 67-70 | 例外時のロールバック |
| 120-130 | 404エラー処理 |
| 159-163 | リレーション取得ロジック |
| 204, 207, 210 | 診療行為なし時の分岐 |
| 240-250 | list時のリレーション構築 |
| 324-325, 346-353 | update時のエラー処理 |

**必要なテストケース**:

| テストケース名 | 説明 |
|---------------|------|
| `test_create_medical_record_success` | 正常系：登録成功 |
| `test_create_medical_record_db_error` | 異常系：DB例外時のロールバック |
| `test_get_medical_record_not_found` | 異常系：404エラー |
| `test_get_medical_record_with_relations` | 正常系：猫名、獣医師名含む取得 |
| `test_get_medical_record_no_medical_action` | 正常系：診療行為なしレコード |
| `test_list_medical_records_with_filters` | 正常系：各種フィルター |
| `test_list_medical_records_pagination` | 正常系：ページネーション |
| `test_update_medical_record_success` | 正常系：更新成功 |
| `test_update_medical_record_not_found` | 異常系：404エラー |
| `test_update_medical_record_db_error` | 異常系：DB例外時 |

**推定作業時間**: 3-4時間

---

### 3. `tests/services/test_medical_action_service.py` (新規)

**対象ファイル**: `app/services/medical_action_service.py`

**未テスト範囲**:

| 行番号 | 内容 |
|--------|------|
| 57-59 | 登録時のDB例外 |
| 123 | 名称フィルターのcontains検索 |
| 194-196 | 更新時のDB例外 |
| 226-237 | calculate_billing（投薬量検証、計算ロジック） |
| 266-269 | get_active_medical_actionsのデフォルト日付 |

**必要なテストケース**:

| テストケース名 | 説明 |
|---------------|------|
| `test_create_medical_action_success` | 正常系：登録成功 |
| `test_create_medical_action_db_error` | 異常系：DB例外処理 |
| `test_get_medical_action_not_found` | 異常系：404エラー |
| `test_list_medical_actions_with_valid_on_filter` | 正常系：有効日フィルター |
| `test_list_medical_actions_with_name_filter` | 正常系：名称フィルター |
| `test_update_medical_action_success` | 正常系：更新成功 |
| `test_update_medical_action_db_error` | 異常系：DB例外処理 |
| `test_calculate_billing_success` | 正常系：料金計算 |
| `test_calculate_billing_invalid_dosage` | 異常系：投薬量<1 |
| `test_get_active_medical_actions_default_date` | 正常系：デフォルト日付 |
| `test_get_active_medical_actions_with_expired` | 正常系：有効期限切れ除外 |

**推定作業時間**: 2.5-3時間

---

## 🟡 既存テスト拡充が必要

### 4. `tests/services/test_volunteer_service.py`

**対象ファイル**: `app/services/volunteer_service.py`

**未テスト範囲**: 58-61, 100-102, 161-163, 208-213, 270-274, 310-312行

**追加すべきテストケース**:

| テストケース名 | 説明 |
|---------------|------|
| `test_create_volunteer_db_error` | 異常系：DB例外処理 |
| `test_get_volunteer_not_found` | 異常系：404エラー |
| `test_update_volunteer_db_error` | 異常系：DB例外処理 |
| `test_delete_volunteer_success` | 正常系：削除成功 |
| `test_delete_volunteer_not_found` | 異常系：404エラー |

**推定作業時間**: 1-1.5時間

---

### 5. `tests/services/test_animal_service.py`

**対象ファイル**: `app/services/animal_service.py`

**未テスト範囲**: 59-62, 96-98, 149-152, 180-183, 311-327行

**追加すべきテストケース**:

| テストケース名 | 説明 |
|---------------|------|
| `test_create_animal_db_error` | 異常系：DB例外処理 |
| `test_get_animal_not_found` | 異常系：404エラー |
| `test_update_animal_db_error` | 異常系：DB例外処理 |
| `test_delete_animal_with_cascade` | 正常系：カスケード削除 |
| `test_bulk_update_animals` | 正常系：一括更新 |

**推定作業時間**: 1.5-2時間

---

## 📋 作業サマリ

| 優先度 | 作業項目 | 推定時間 | カバレッジ向上 |
|--------|----------|----------|--------------|
| 🔴 高 | test_user_service.py 新規作成 | 1.5-2h | +66% → 100% |
| 🔴 高 | test_medical_record_service.py 新規作成 | 3-4h | +32% → ~95% |
| 🔴 高 | test_medical_action_service.py 新規作成 | 2.5-3h | +30% → ~95% |
| 🟡 中 | test_volunteer_service.py 拡充 | 1-1.5h | +23% → ~95% |
| 🟡 中 | test_animal_service.py 拡充 | 1.5-2h | +25% → ~95% |

**合計推定時間**: 10-14時間

---

## 🔧 テスト実装時の注意点

### 共通のテストパターン

```python
# conftest.py で共通フィクスチャを活用
@pytest.fixture
def db_session():
    """テスト用データベースセッション"""
    ...

@pytest.fixture
def sample_user(db_session):
    """テスト用ユーザー"""
    ...
```

### 例外テストのパターン

```python
def test_create_xxx_db_error(db_session, mocker):
    """DB例外時のロールバック確認"""
    mocker.patch.object(
        db_session, 'commit',
        side_effect=Exception("DB Error")
    )

    with pytest.raises(HTTPException) as exc_info:
        create_xxx(db_session, data)

    assert exc_info.value.status_code == 500
```

### 404テストのパターン

```python
def test_get_xxx_not_found(db_session):
    """存在しないIDでの404エラー確認"""
    with pytest.raises(HTTPException) as exc_info:
        get_xxx(db_session, non_existent_id=99999)

    assert exc_info.value.status_code == 404
```

---

## 📝 実施チェックリスト

- [ ] test_user_service.py 新規作成
- [ ] test_medical_record_service.py 新規作成
- [ ] test_medical_action_service.py 新規作成
- [ ] test_volunteer_service.py 拡充
- [ ] test_animal_service.py 拡充
- [ ] `make test` で全テスト合格確認
- [ ] カバレッジ80%以上達成確認

---

## 関連ドキュメント

- [コーディング規約](../.kiro/steering/python-backend-best-practices.md)
- [TDDガイドライン](../.kiro/steering/tdd-guidelines.md)

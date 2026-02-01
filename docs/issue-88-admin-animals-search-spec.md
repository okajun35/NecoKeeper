# Issue #88: 管理画面の個体一覧検索機能仕様

## 概要

管理画面 `/admin/animals` の検索・フィルタ機能を改善し、日常業務で使いやすい一覧画面を実装する。

## 基本コンセプト

- **一覧** = 毎日使う基本情報
- **タグ/詳細検索** = 必要な人が使う条件
- **譲渡済み・死亡はデフォルト非表示**

## ステータスフィルタ

### 選択肢（上から順）

| 値 | ラベル | 説明 | デフォルト |
|----|--------|------|-----------|
| `ACTIVE` | 現在活動している猫 | QUARANTINE, IN_CARE, TRIAL のOR検索 | ✅ |
| `QUARANTINE` | 保護中 | 保護直後、隔離中 | |
| `IN_CARE` | 在籍中 | 施設/カフェ/預かり含む | |
| `TRIAL` | トライアル中 | 譲渡前のお試し期間 | |
| --- | (区切り線) | | |
| `ADOPTED` | 譲渡済み | 譲渡完了 | |
| `DECEASED` | 死亡 | | |
| (空文字) | すべて | 全ステータス表示 | |

### ラベル修正

- ❌ `TRIAL` → 「譲渡可能」（誤り）
- ✅ `TRIAL` → 「トライアル中」（正しい）

## 詳細検索フィルタ

| フィルタ名 | フィールド | 選択肢 |
|-----------|-----------|--------|
| 譲渡可 | ステータス条件 | Yes（IN_CARE or TRIAL）/ No / すべて |
| FIV | `fiv_positive` | 陽性 / 陰性 / 不明 / すべて |
| FeLV | `felv_positive` | 陽性 / 陰性 / 不明 / すべて |
| 避妊・去勢 | `is_sterilized` | 済 / 未 / 不明 / すべて |
| 性別 | `gender` | オス / メス / 不明 / すべて |
| 場所 | `location_type` | 施設 / 預かり宅 / 譲渡先 / すべて |

### 譲渡可の判定ロジック

現在のステータスのみで判定:
- **譲渡可** = `status` が `IN_CARE` または `TRIAL`

## 一覧表示項目

### 表示する項目（左から右）

1. **写真**（サムネイル）
2. **名前** / 管理番号
3. **ステータス**（バッジ）
4. **譲渡可**（Yes/No バッジ、IN_CARE/TRIAL の場合のみ Yes）
5. **FIV/FeLV**（陽性/陰性/不明 アイコン）
6. **避妊・去勢**（済/未/不明）
7. **性別**
8. **月齢**（推定の場合は「約」付き）
9. **場所**（`location_type` + `current_location_note`）

### 譲渡済み・死亡の表示

- デフォルト（ACTIVE）では非表示
- ステータスフィルタで直接選択可能（ADOPTED/DECEASED）
- 「すべて」選択時も表示
- **グレーアウト表示**（薄く表示）で視覚的に区別

## API変更

### GET /api/v1/animals

#### 追加クエリパラメータ

| パラメータ | 型 | 説明 |
|-----------|-----|------|
| `status` | string | `ACTIVE` で複数ステータスOR検索 |
| `gender` | string | 性別フィルタ |
| `fiv` | string | `positive` / `negative` / `unknown` |
| `felv` | string | `positive` / `negative` / `unknown` |
| `is_sterilized` | string | `true` / `false` / `unknown` |
| `location_type` | string | `FACILITY` / `FOSTER_HOME` / `ADOPTER_HOME` |
| `is_ready_for_adoption` | string | `true` で IN_CARE or TRIAL のみ |

## 実装計画（TDDアプローチ）

### Step 1: テスト作成（Red）
- `tests/api/test_animals_search.py` に詳細検索のテストケースを追加
- 複数ステータス検索、各フィルタのテスト

### Step 2: API/サービス層実装（Green）
- `app/api/v1/animals.py` にクエリパラメータ追加
- `app/services/animal_service.py` の `list_animals` を拡張

### Step 3: UI実装
- `app/templates/admin/animals/list.html` のフィルタUI更新
- `app/static/js/admin/animals.js` に詳細検索機能追加

### Step 4: 一覧表示更新
- 表示項目の変更
- 譲渡済み・死亡のグレーアウト表示

### Step 5: i18n対応
- `app/static/i18n/ja/animals.json`
- `app/static/i18n/en/animals.json`

### Step 6: リファクタリング（Refactor）
- コード整理
- `make lint` `make format` `make mypy` 確認

## 参考

- [Issue #88](https://github.com/okajun35/NecoKeeper/issues/88)
- [AGENTS.md](../AGENTS.md)

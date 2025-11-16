# Design Document

## Overview

世話記録一覧画面を日次ビュー形式に改修します。現在の縦長リスト形式から、1日の記録を横に並べて表示する形式に変更し、管理者が一目で各猫の日々の世話状況を把握できるようにします。

## Architecture

### システム構成

```
┌─────────────────┐
│  Browser        │
│  (Admin UI)     │
└────────┬────────┘
         │ HTTP/JSON
         ↓
┌─────────────────┐
│  FastAPI        │
│  Backend        │
├─────────────────┤
│ - API Endpoint  │
│ - Data Transform│
│ - Pagination    │
└────────┬────────┘
         │ SQLAlchemy
         ↓
┌─────────────────┐
│  SQLite         │
│  Database       │
└─────────────────┘
```

### データフロー

1. **フロントエンド → バックエンド**
   - フィルタ条件（猫ID、開始日、終了日、ページ番号）
   - 認証トークン

2. **バックエンド → データベース**
   - SQLクエリ（JOIN、GROUP BY、フィルタ）

3. **データベース → バックエンド**
   - 世話記録データ（生データ）

4. **バックエンド → フロントエンド**
   - 日次ビュー形式に変換されたデータ
   - ページネーション情報

5. **フロントエンド → ユーザー**
   - テーブル形式で表示
   - ○/×のクリッカブルリンク

## Components and Interfaces

### 1. バックエンドAPI

#### 新規エンドポイント: `/api/v1/care-logs/daily-view`

**目的**: 日次ビュー形式のデータを返す

**メソッド**: GET

**クエリパラメータ**:
```python
animal_id: int | None = None  # 猫ID（Noneの場合は全猫）
start_date: date | None = None  # 開始日（デフォルト: 7日前）
end_date: date | None = None  # 終了日（デフォルト: 今日）
page: int = 1  # ページ番号
page_size: int = 20  # ページサイズ
```

**レスポンス**:
```json
{
  "items": [
    {
      "date": "2025-11-16",
      "animal_id": 1,
      "animal_name": "たま",
      "morning": {
        "exists": true,
        "log_id": 123,
        "appetite": 4,
        "energy": 5
      },
      "noon": {
        "exists": true,
        "log_id": 124,
        "appetite": 3,
        "energy": 4
      },
      "evening": {
        "exists": false,
        "log_id": null
      }
    }
  ],
  "total": 150,
  "page": 1,
  "page_size": 20,
  "total_pages": 8
}
```

#### サービス層: `care_log_service.py`

**新規関数**: `get_daily_view()`

```python
def get_daily_view(
    db: Session,
    animal_id: int | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    page: int = 1,
    page_size: int = 20,
) -> dict:
    """
    日次ビュー形式のデータを取得

    処理フロー:
    1. 日付範囲を決定（デフォルト: 過去7日間）
    2. 対象猫を決定（指定なしの場合は全猫）
    3. 日付×猫の組み合わせを生成
    4. 各組み合わせに対して朝・昼・夕の記録を取得
    5. ページネーション適用
    6. 日次ビュー形式に変換
    """
    pass
```

### 2. フロントエンド

#### HTML構造

```html
<div class="care-logs-daily-view">
  <!-- フィルタセクション -->
  <div class="filters">
    <select id="animalFilter">
      <option value="">すべての猫</option>
      <!-- 猫リスト -->
    </select>
    <input type="date" id="startDate">
    <input type="date" id="endDate">
    <button id="searchBtn">検索</button>
    <button id="clearBtn">クリア</button>
  </div>

  <!-- テーブル -->
  <table class="daily-view-table">
    <thead>
      <tr>
        <th>日付</th>
        <th>猫</th>
        <th>朝</th>
        <th>昼</th>
        <th>夕</th>
      </tr>
    </thead>
    <tbody id="dailyViewBody">
      <!-- 動的に生成 -->
    </tbody>
  </table>

  <!-- ページネーション -->
  <div class="pagination">
    <button id="prevBtn">前へ</button>
    <span id="pageInfo">1 / 10</span>
    <button id="nextBtn">次へ</button>
  </div>
</div>
```

#### JavaScript: `care_logs_daily_view.js`

**主要関数**:

```javascript
// データ取得
async function loadDailyView(filters = {}) {
  const params = new URLSearchParams({
    animal_id: filters.animalId || '',
    start_date: filters.startDate || '',
    end_date: filters.endDate || '',
    page: filters.page || 1,
    page_size: 20
  });

  const response = await fetch(`/api/v1/care-logs/daily-view?${params}`, {
    headers: {
      'Authorization': `Bearer ${getToken()}`
    }
  });

  const data = await response.json();
  renderDailyView(data);
}

// テーブル描画
function renderDailyView(data) {
  const tbody = document.getElementById('dailyViewBody');
  tbody.innerHTML = '';

  data.items.forEach(item => {
    const row = createDailyRow(item);
    tbody.appendChild(row);
  });

  updatePagination(data);
}

// 行生成
function createDailyRow(item) {
  const row = document.createElement('tr');

  // 日付
  const dateCell = document.createElement('td');
  dateCell.textContent = item.date;
  row.appendChild(dateCell);

  // 猫名
  const nameCell = document.createElement('td');
  nameCell.textContent = item.animal_name;
  row.appendChild(nameCell);

  // 朝・昼・夕
  ['morning', 'noon', 'evening'].forEach(timeSlot => {
    const cell = document.createElement('td');
    const link = createRecordLink(item, timeSlot);
    cell.appendChild(link);
    row.appendChild(cell);
  });

  return row;
}

// 記録リンク生成
function createRecordLink(item, timeSlot) {
  const record = item[timeSlot];
  const link = document.createElement('a');

  if (record.exists) {
    // 記録あり: ○ → 詳細/編集画面
    link.textContent = '○';
    link.href = `/admin/care-logs/${record.log_id}`;
    link.className = 'record-exists';
  } else {
    // 記録なし: × → 新規登録画面
    link.textContent = '×';
    link.href = `/admin/care-logs/new?animal_id=${item.animal_id}&date=${item.date}&time_slot=${timeSlot}`;
    link.className = 'record-missing';
  }

  return link;
}
```

### 3. CSS スタイリング

```css
/* テーブルスタイル */
.daily-view-table {
  width: 100%;
  border-collapse: collapse;
}

.daily-view-table th,
.daily-view-table td {
  padding: 12px;
  text-align: center;
  border: 1px solid #e5e7eb;
}

.daily-view-table th {
  background-color: #f9fafb;
  font-weight: 600;
}

/* 記録リンク */
.record-exists {
  color: #10b981; /* 緑 */
  font-size: 1.5rem;
  text-decoration: none;
  font-weight: bold;
}

.record-exists:hover {
  color: #059669;
}

.record-missing {
  color: #ef4444; /* 赤 */
  font-size: 1.5rem;
  text-decoration: none;
  font-weight: bold;
}

.record-missing:hover {
  color: #dc2626;
}

/* レスポンシブ対応 */
@media (max-width: 768px) {
  .daily-view-table {
    display: none;
  }

  .daily-view-cards {
    display: block;
  }

  .daily-card {
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    padding: 16px;
    margin-bottom: 16px;
  }
}
```

## Data Models

### 既存モデル（変更なし）

- `Animal`: 猫情報
- `CareLog`: 世話記録
- `Volunteer`: ボランティア情報

### 新規スキーマ

#### `DailyViewRecord` (Pydantic)

```python
class TimeSlotRecord(BaseModel):
    """時点ごとの記録"""
    exists: bool
    log_id: int | None = None
    appetite: int | None = None
    energy: int | None = None
    urination: bool | None = None
    cleaning: bool | None = None

class DailyViewRecord(BaseModel):
    """日次ビューの1レコード"""
    date: date
    animal_id: int
    animal_name: str
    morning: TimeSlotRecord
    noon: TimeSlotRecord
    evening: TimeSlotRecord

class DailyViewResponse(BaseModel):
    """日次ビューのレスポンス"""
    items: list[DailyViewRecord]
    total: int
    page: int
    page_size: int
    total_pages: int
```

## Error Handling

### バックエンド

1. **認証エラー**: 401 Unauthorized
   - トークンが無効または期限切れ

2. **バリデーションエラー**: 422 Unprocessable Entity
   - 日付範囲が不正（開始日 > 終了日）
   - ページ番号が不正（< 1）

3. **データベースエラー**: 500 Internal Server Error
   - クエリ実行失敗
   - ログに詳細を記録

### フロントエンド

1. **ネットワークエラー**
   - エラーメッセージ表示
   - リトライボタン提供

2. **データなし**
   - 「記録がありません」メッセージ表示
   - フィルタクリアボタン提供

3. **ローディング状態**
   - スピナー表示
   - テーブルを半透明化

## Testing Strategy

### バックエンドテスト

1. **ユニットテスト**: `test_care_log_service.py`
   - `test_get_daily_view_default_date_range()`: デフォルト日付範囲
   - `test_get_daily_view_with_animal_filter()`: 猫フィルタ
   - `test_get_daily_view_pagination()`: ページネーション
   - `test_get_daily_view_empty_result()`: 結果なし

2. **APIテスト**: `test_care_logs_api.py`
   - `test_daily_view_endpoint_success()`: 正常系
   - `test_daily_view_endpoint_unauthorized()`: 認証エラー
   - `test_daily_view_endpoint_invalid_date_range()`: バリデーションエラー

### フロントエンドテスト

1. **手動テスト**
   - 各ブラウザでの表示確認（Chrome, Firefox, Safari）
   - レスポンシブデザイン確認（デスクトップ、タブレット、モバイル）
   - リンククリック動作確認

2. **統合テスト**
   - フィルタ適用後のデータ更新
   - ページネーション動作
   - CSVエクスポート

## Performance Considerations

### データベースクエリ最適化

1. **インデックス活用**
   - `care_logs.log_date`: 日付範囲検索
   - `care_logs.animal_id`: 猫フィルタ
   - `care_logs.time_slot`: 時点フィルタ

2. **クエリ最適化**
   - JOINを最小限に
   - 必要なカラムのみSELECT
   - ページネーションでLIMIT/OFFSET使用

3. **キャッシュ戦略**
   - 猫リストをフロントエンドでキャッシュ
   - フィルタ条件をセッションストレージに保存

### フロントエンド最適化

1. **レンダリング最適化**
   - 仮想スクロール（大量データの場合）
   - デバウンス処理（フィルタ入力）

2. **ネットワーク最適化**
   - リクエストのキャンセル（新しいリクエスト時）
   - ローディング状態の適切な表示

## Migration Plan

### Phase 1: バックエンド実装
1. 新規エンドポイント作成
2. サービス層関数実装
3. スキーマ定義
4. ユニットテスト作成

### Phase 2: フロントエンド実装
1. HTML構造作成
2. JavaScript実装
3. CSS スタイリング
4. レスポンシブ対応

### Phase 3: 統合とテスト
1. バックエンド・フロントエンド統合
2. 手動テスト実施
3. バグ修正

### Phase 4: デプロイ
1. 既存の世話記録一覧画面を置き換え
2. ユーザーへの通知
3. モニタリング

## Design Decisions

### 1. なぜ新規エンドポイントを作成するのか？

**理由**: 既存の `/api/v1/care-logs` エンドポイントは汎用的なリスト取得用で、日次ビュー形式への変換ロジックをフロントエンドで実装すると複雑になるため。

**メリット**:
- バックエンドでデータ変換を一元管理
- フロントエンドのロジックがシンプルに
- パフォーマンス向上（必要なデータのみ取得）

### 2. なぜ○/×を使うのか？

**理由**: 視覚的に分かりやすく、日本の管理システムで一般的な表現方法。

**代替案**: チェックマーク/空白、色分けのみ

**選択理由**: ○/×は直感的で、クリック可能であることが明確。

### 3. なぜページネーションを20件にするのか？

**理由**: 1ページに表示する情報量とスクロール量のバランス。

**根拠**:
- 10匹の猫 × 7日間 = 70レコード → 4ページ
- 適度なページ数で管理しやすい
- パフォーマンスへの影響が少ない

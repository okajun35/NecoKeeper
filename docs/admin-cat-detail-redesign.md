# 管理画面 猫詳細画面の分離設計

## Issue
詳細画面が編集兼詳細になっており、項目が増えたため以下に改善する：
- 詳細画面 → **閲覧 + ステータス/所在地変更のみ**
- 編集画面 → **基本情報等の詳細編集に遷移**

## 仕様確定（ユーザー確認済み）
1. **詳細画面で残す変更項目**: ステータス + 所在地タイプ + 所在地詳細
2. **理由入力UI**: 任意で追加（必須でない）
3. **確認フロー**: 必須維持（終端ステータス復帰時）
4. **PUT更新**: 現状維持
5. **編集画面**: ステータス/所在地を残す（確認フロー現状維持）

## 画面遷移（現状と変更後）

### 現状
```
一覧 → 詳細（編集フォーム内包）
      └─ 一覧への戻る
```

### 変更後
```
一覧 → 詳細（閲覧専用 + ステータス変更）
      ├─ [変更]ボタン → 編集画面へ遷移
      └─ 一覧への戻る

編集画面（ステータス/所在地も含む）
      ├─ [保存] → 詳細へ戻る（確認フロー未適用）
      └─ [キャンセル] → 詳細へ戻る
```

## 実装範囲

### 1. 詳細テンプレート ([app/templates/admin/animals/detail.html](app/templates/admin/animals/detail.html))

#### 変更内容
- **基本情報フォーム全体を読み取り専用に変換**
  - `<input>`, `<select>`, `<textarea>` を `<div>` + テキスト表示に変更
  - フォーム送信ボタン（保存/キャンセル）を削除

- **ステータス/所在地UI は詳細画面の左カラムに残す**
  - `statusSelect`, `locationTypeSelect`, `currentLocationNote`（読み取り専用）
  - `updateStatusAndLocationBtn` は維持

- **理由入力UI を新規追加**
  - `currentLocationNote` の下に `reasonForStatusChange` という `<textarea>` を追加
  - ラベル: 「変更理由（オプション）」
  - プレースホルダ: 「例: 譲渡予定、治療完了」

- **[変更]ボタン導線を追加**
  - 基本情報エリアのヘッダー または フォーム下部に配置
  - テキスト: 「編集する」（一覧と統一）
  - クリック時: `/admin/animals/{id}/edit` へ遷移
  - UIは最終確認時に配置決定

#### 削除対象
- `basicInfoForm` 内のすべてのフォーム要素をプレビュー化
- フォーム送信ボタン（保存/キャンセル）
- 医療情報セクション（編集画面で編集）
- ワクチン接種記録フォーム（編集画面で編集）

#### 残す要素
- タブ機能
- 左カラムのステータス/所在地変更UI
- QRカード/紙記録生成ボタン
- ギャラリー/世話記録タブ

### 2. 詳細 JavaScript ([app/static/js/admin/animal_detail.js](app/static/js/admin/animal_detail.js))

#### 変更内容
- **`setupBasicInfoForm()` の削除 または 無効化**
  - フォーム送信のバリデーション・送信処理は不要
  - フォーム表示のみに

- **理由入力フィールドの処理**
  - `updateStatusAndLocation()` 内で `reasonForStatusChange` を取得
  - PUT リクエストボディに含める場合のフィールド名: `reason` (またはスキーマに合わせる)

- **`updateStatusAndLocation()` の改良**
  ```javascript
  // 現状では confirm パラメータで再送のみ
  // 変更後: reason フィールドを含める
  {
    status: newStatus,
    location_type: newLocationType,
    current_location_note: currentLocationNote,
    reason: reasonForStatusChange,  // 追加
    confirm: false  // 初回送信
  }
  ```

- **確認フロー再送で理由を保持**
  - 409 Conflict で確認ダイアログ表示後、確認時に再度送信
  - 理由は変更せずに送信

- **[変更]ボタン遷移の実装**
  - `#editBtn` または同名のボタンにリスナ追加
  - クリック時: `window.location.href = ${adminBasePath}/animals/${animalId}/edit`

### 3. 編集テンプレート ([app/templates/admin/animals/edit.html](app/templates/admin/animals/edit.html))

#### 確認事項
- 現状: 基本情報フォーム + ステータス/所在地を含む
- 変更: **スキップ**（現状のまま）
  - 理由: ユーザー指示「編集画面からステータス/所在地編集を外すか残すか → 残していい」

#### 補足
- 編集画面の PUT 更新には確認フロー処理が未実装（現状維持）
- ステータス/所在地を編集画面でも変更可能 → 別導線で詳細から直接変更可能にした分、利便性向上

### 4. 編集 JavaScript ([app/static/js/admin/animal_edit.js](app/static/js/admin/animal_edit.js))

#### 確認事項
- 現状のまま（変更不要）
- 編集画面の確認フロー処理は現状維持（409 Conflict 時にダイアログなし）

## API への影響

### エンドポイント
- `PUT /api/v1/animals/{id}`: 変更なし（既存の確認フロー維持）
  - リクエストボディに `reason` フィールドが追加される可能性あり

### 仕様確認
- 理由フィールドは任意（null 許容）
- ステータス/所在地変更の確認フローは既に実装済み
- 理由はステータス履歴テーブルに記録するか、または履歴メモフィールドに格納するか → スキーマ確認後に決定

## テスト影響範囲

### 確認・更新対象のテスト
- [tests/api/test_animals.py](tests/api/test_animals.py):
  - PUT `/animals/{id}` の理由フィールド対応テスト

- [tests/services/test_animal_service.py](tests/services/test_animal_service.py):
  - ステータス履歴記録に理由を含める場合

- 管理画面 E2E テスト（あれば）:
  - 詳細画面で読み取り専用化確認
  - ステータス変更 UI テスト
  - [変更]ボタン遷移テスト

### 変更不要のテスト
- 編集画面の送信ロジック（`animal_edit.js` 未変更）
- 基本情報更新の API テスト（テンプレート変更であり、API は未変更）

## ファイル修正手順

1. [app/templates/admin/animals/detail.html](app/templates/admin/animals/detail.html)
   - 基本情報フォーム要素の読み取り専用化
   - 理由入力UI 追加
   - [変更]ボタン追加

2. [app/static/js/admin/animal_detail.js](app/static/js/admin/animal_detail.js)
   - `setupBasicInfoForm()` 削除 or 無効化
   - `updateStatusAndLocation()` に理由フィールド統合
   - [変更]ボタン遷移処理追加

3. テスト実行
   - 詳細画面表示確認
   - ステータス変更確認
   - [変更]ボタン遷移確認

## 実装時の注意点

### UI 配置（最終決定は画面確認後）
- [変更]ボタンは「基本情報」タイトル右隣 or フォーム下部
- 理由入力 UI は所在地詳細の下に配置

### i18n
- 「編集する」ボタン文言は既存キー確認（`buttons.edit` など）
- 理由入力ラベル: 「変更理由（オプション）」
- 理由入力プレースホルダ: 「例: 譲渡予定、治療完了」

### アクセシビリティ
- 読み取り専用化した要素は `<span>`, `<div>` で実装
- ラベルとの関連付けを `data-i18n` で保持

---

## 変更前後の機能一覧

| 機能 | 現状（詳細） | 変更後（詳細） | 編集画面 |
|-----|----------|----------|--------|
| 基本情報表示 | 編集フォーム | 読み取り専用 | 編集フォーム |
| ステータス変更 | 詳細内 | 詳細内 | 編集内 |
| 所在地変更 | 詳細内 | 詳細内 | 編集内 |
| 理由入力 | なし | あり（任意） | なし |
| 確認フロー | 詳細内 | 詳細内 | なし |
| 編集導線 | なし | [変更]ボタン | - |
| ギャラリー | タブ | タブ | - |
| 世話記録 | タブ | タブ | - |

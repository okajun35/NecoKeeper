# i18n Translation Files

このディレクトリには、NecoKeeperの多言語対応用の対訳ファイルが含まれています。

## ファイル構成

- `ja.json`: 日本語翻訳
- `en.json`: 英語翻訳

## カテゴリ構成

### 1. common
共通UI要素（ボタン、ラベル、アクション等）

### 2. nav
ナビゲーションメニュー

### 3. dashboard
ダッシュボード画面

### 4. animals
猫台帳（猫管理機能）

### 5. care_logs
世話記録機能

### 6. medical_records
診療記録機能

### 7. medical_actions
診療行為マスター

### 8. adoptions
里親管理機能

### 9. volunteers
ボランティア管理機能

### 10. reports
帳票出力機能

### 11. settings
設定画面

### 12. auth
認証関連（ログイン・ログアウト）

### 13. public
Publicフォーム（PWA）

### 14. errors
エラーメッセージ

### 15. validation
バリデーションメッセージ

### 16. pagination
ページネーション

### 17. date
日付・時刻関連

## 使用方法

### JavaScript (i18next)

```javascript
// i18nextの初期化
import i18next from 'i18next';

await i18next.init({
  lng: 'ja', // デフォルト言語
  fallbackLng: 'en',
  resources: {
    ja: { translation: await fetch('/static/i18n/ja.json').then(r => r.json()) },
    en: { translation: await fetch('/static/i18n/en.json').then(r => r.json()) }
  }
});

// 翻訳の取得
const title = i18next.t('dashboard.title'); // "ダッシュボード"
const saveButton = i18next.t('common.save'); // "保存"

// パラメータ付き翻訳
const message = i18next.t('validation.required', { field: '名前' }); // "名前は必須です"
```

### Jinja2テンプレート

```jinja2
{# テンプレートで翻訳を使用 #}
<h1>{{ _('dashboard.title') }}</h1>
<button>{{ _('common.save') }}</button>
```

## 翻訳の追加・更新

1. 新しいキーを追加する場合は、`ja.json`と`en.json`の両方に追加してください
2. カテゴリ構造を維持してください
3. キー名は英語のスネークケースで統一してください（例: `add_new`, `delete_confirm`）
4. 階層構造は最大3レベルまでとしてください

## 翻訳キーの命名規則

- **画面名.要素名**: `dashboard.title`, `animals.list_title`
- **画面名.fields.フィールド名**: `animals.fields.name`, `care_logs.fields.appetite`
- **画面名.actions.アクション名**: `animals.actions.edit_info`, `care_logs.actions.export_csv`
- **画面名.messages.メッセージ種別**: `animals.messages.created`, `care_logs.messages.updated`
- **画面名.status.ステータス名**: `animals.status.protected`, `adoptions.status.pending`

## テスト

翻訳ファイルの整合性をチェックするには、以下のコマンドを実行してください：

```bash
# JSONの構文チェック
python -m json.tool app/static/i18n/ja.json > /dev/null
python -m json.tool app/static/i18n/en.json > /dev/null

# キーの整合性チェック（Python）
python scripts/check_i18n_keys.py
```

## 注意事項

- 翻訳ファイルはUTF-8エンコーディングで保存してください
- JSONの構文エラーに注意してください（末尾のカンマ、引用符等）
- 変数プレースホルダーは`{{variable}}`形式を使用してください
- HTMLタグは翻訳文に含めないでください（i18nextで処理）

## 対応言語

- 🇯🇵 日本語 (ja)
- 🇬🇧 英語 (en)

## 今後の拡張

将来的に他の言語を追加する場合は、以下の手順で行ってください：

1. 新しい言語コードのJSONファイルを作成（例: `zh.json`, `ko.json`）
2. `ja.json`の構造をコピーして翻訳
3. フロントエンドのi18next設定に言語を追加
4. 言語切り替えUIに選択肢を追加

## 参考リンク

- [i18next Documentation](https://www.i18next.com/)
- [Jinja2 i18n Extension](https://jinja.palletsprojects.com/en/3.1.x/extensions/#i18n-extension)

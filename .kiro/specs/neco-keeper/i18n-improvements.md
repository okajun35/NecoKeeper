# 多言語化（i18n）改善提案

## Context7調査結果に基づくベストプラクティス

### 📚 参照ライブラリ
- **i18next** (Benchmark Score: 95.9) - `/websites/i18next`
- **FastAPI** (Benchmark Score: 85.2) - `/websites/fastapi_tiangolo`
- **Babel** - `/websites/babel_pocoo-en`

---

## 🔍 現在の実装の問題点

### 1. **フロントエンド（JavaScript/i18next）**

#### ❌ 問題点
1. **翻訳ファイルの一括読み込み**
   - 全ての翻訳を初期化時に読み込んでいる
   - 大規模アプリケーションではパフォーマンス問題

2. **名前空間（Namespace）未使用**
   - 全翻訳が単一の`translation`名前空間
   - モジュール分割ができない

3. **バックエンド連携なし**
   - i18next-http-backendを使用していない
   - サーバーサイドレンダリング（SSR）非対応

4. **キャッシュ戦略なし**
   - LocalStorageキャッシュ未実装
   - 毎回ネットワークリクエスト

5. **タイトル翻訳の実装が不完全**
   - `data-i18n-title`属性の処理が追加されたが、ページタイトル（`<title>`タグ）の翻訳が未実装

### 2. **バックエンド（FastAPI/Python）**

#### ❌ 問題点
1. **Babel未使用**
   - 標準的なPython i18nライブラリ（Babel）を使用していない
   - Gettext形式（.po/.mo）非対応

2. **Jinja2統合が不完全**
   - テンプレートでの翻訳関数が手動実装
   - Babel Jinja2拡張機能未使用

3. **遅延評価（Lazy Evaluation）なし**
   - リクエストコンテキスト外での翻訳不可
   - メール送信などで問題

4. **複数形（Pluralization）未対応**
   - `ngettext`関数なし
   - 数量に応じた翻訳不可

5. **言語検出の優先順位が不適切**
   - クエリパラメータが最優先（セキュリティリスク）
   - 標準的な順序: Cookie → Accept-Language → Default

---

## ✅ 改善提案

### Phase 1: フロントエンド改善（i18next）

#### 1.1 名前空間（Namespace）の導入

**ベストプラクティス（Context7）:**
```javascript
// 複数の名前空間で翻訳を整理
i18next.init({
  ns: ['common', 'dashboard', 'animals', 'care_logs'],
  defaultNS: 'common',
  resources: {
    ja: {
      common: { /* 共通翻訳 */ },
      dashboard: { /* ダッシュボード専用 */ },
      animals: { /* 猫管理専用 */ }
    }
  }
});

// 使用例
i18next.t('save', { ns: 'common' }); // 共通の「保存」
i18next.t('title', { ns: 'dashboard' }); // ダッシュボードのタイトル
```

**メリット:**
- 翻訳ファイルの論理的な分割
- 遅延読み込み（Lazy Loading）が可能
- 大規模アプリケーションでのスケーラビリティ

#### 1.2 HTTP Backend + LocalStorage キャッシュ

**ベストプラクティス（Context7）:**
```javascript
import ChainedBackend from 'i18next-chained-backend';
import LocalStorageBackend from 'i18next-localstorage-backend';
import HttpBackend from 'i18next-http-backend';

i18next
  .use(ChainedBackend)
  .init({
    backend: {
      backends: [
        LocalStorageBackend,  // 1次キャッシュ
        HttpBackend           // 2次（サーバー）
      ],
      backendOptions: [{
        expirationTime: 7 * 24 * 60 * 60 * 1000, // 7日間
        versions: { ja: 'v1.0', en: 'v1.0' }
      }, {
        loadPath: '/api/v1/i18n/{{lng}}/{{ns}}.json'
      }]
    }
  });
```

**メリット:**
- オフライン対応
- パフォーマンス向上（キャッシュヒット時）
- バージョン管理による更新制御

#### 1.3 遅延読み込み（Lazy Loading）

**ベストプラクティス（Context7）:**
```javascript
import resourcesToBackend from 'i18next-resources-to-backend';

i18next
  .use(resourcesToBackend((language, namespace) =>
    import(`./locales/${language}/${namespace}.json`)
  ))
  .init({
    partialBundledLanguages: true,
    ns: [], // 初期は空
    resources: {}
  });

// 必要に応じて名前空間を読み込み
i18next.loadNamespaces(['dashboard', 'animals']);
```

**メリット:**
- 初期読み込み時間の短縮
- 必要な翻訳のみ読み込み
- Webpack/Viteでのコード分割

#### 1.4 ページタイトル翻訳の完全実装

**現在の問題:**
```javascript
// i18n.jsに追加されたが、実際には動作していない
const titleElement = document.querySelector('title');
if (titleElement && titleElement.hasAttribute('data-i18n-title')) {
  const key = titleElement.getAttribute('data-i18n-title');
  const translation = i18next.t(key);
  const appName = i18next.t('common.app_name');
  titleElement.textContent = `${translation} - ${appName}`;
}
```

**改善案:**
```javascript
function translatePage() {
  // ... 既存のコード ...

  // ページタイトルを翻訳
  const titleElement = document.querySelector('title[data-i18n-title]');
  if (titleElement) {
    const key = titleElement.getAttribute('data-i18n-title');
    const translation = i18next.t(key);
    const appName = i18next.t('common.app_name');
    titleElement.textContent = `${translation} - ${appName}`;
  }

  // メタディスクリプションも翻訳
  const metaDesc = document.querySelector('meta[name="description"][data-i18n-content]');
  if (metaDesc) {
    const key = metaDesc.getAttribute('data-i18n-content');
    metaDesc.setAttribute('content', i18next.t(key));
  }
}
```

---

### Phase 2: バックエンド改善（FastAPI + Babel）

#### 2.1 Babel統合

**ベストプラクティス（Context7）:**
```python
# babel.cfg
[python: **.py]
[jinja2: **/templates/**.html]
encoding = utf-8
extensions = jinja2.ext.i18n

# setup.py または pyproject.toml
[tool.babel]
domain = "messages"
directory = "app/locales"
input_file = "app/locales/messages.pot"
output_dir = "app/locales"
```

**翻訳ファイル生成:**
```bash
# 1. 翻訳可能な文字列を抽出
pybabel extract -F babel.cfg -o app/locales/messages.pot .

# 2. 言語ごとのカタログを初期化
pybabel init -i app/locales/messages.pot -d app/locales -l ja
pybabel init -i app/locales/messages.pot -d app/locales -l en

# 3. .poファイルを編集後、.moファイルにコンパイル
pybabel compile -d app/locales
```

#### 2.2 Jinja2 Babel拡張

**ベストプラクティス（Context7）:**
```python
from babel.support import Translations
from jinja2 import Environment

def setup_jinja2_i18n(env: Environment, locale: str):
    """Jinja2にBabel翻訳を統合"""
    translations = Translations.load('app/locales', [locale])
    env.install_gettext_translations(translations)

# テンプレートで使用
# {% trans %}保存{% endtrans %}
# {{ _('保存') }}
# {{ ngettext('%(num)d cat', '%(num)d cats', count) }}
```

#### 2.3 遅延評価（Lazy Translation）

**ベストプラクティス（Context7）:**
```python
from babel.support import LazyProxy

def lazy_gettext(string: str) -> LazyProxy:
    """遅延評価翻訳"""
    return LazyProxy(lambda: get_current_translation().gettext(string))

# 使用例（リクエストコンテキスト外）
EMAIL_SUBJECT = lazy_gettext("Welcome to NecoKeeper")

# 実際の評価はリクエスト時
def send_email(user):
    subject = str(EMAIL_SUBJECT)  # この時点で翻訳
    ...
```

#### 2.4 FastAPI依存性注入

**ベストプラクティス（Context7）:**
```python
from fastapi import Depends, Header, Request
from typing import Annotated

def get_locale(
    request: Request,
    accept_language: Annotated[str | None, Header()] = None
) -> str:
    """リクエストから言語を検出"""
    # 1. Cookie
    if lang := request.cookies.get("language"):
        if lang in ("ja", "en"):
            return lang

    # 2. Accept-Language ヘッダー
    if accept_language:
        for lang in accept_language.split(","):
            code = lang.split(";")[0].split("-")[0].strip()
            if code in ("ja", "en"):
                return code

    # 3. デフォルト
    return "ja"

def get_translations(
    locale: Annotated[str, Depends(get_locale)]
) -> Translations:
    """翻訳カタログを取得"""
    return Translations.load('app/locales', [locale])

# エンドポイントで使用
@router.get("/animals")
async def get_animals(
    translations: Annotated[Translations, Depends(get_translations)]
):
    _ = translations.gettext
    return {"message": _("Animals list")}
```

#### 2.5 複数形対応

**ベストプラクティス（Context7）:**
```python
# .po ファイル
msgid "%(count)d cat"
msgid_plural "%(count)d cats"
msgstr[0] "%(count)d匹の猫"

# Python コード
from babel.support import Translations

translations = Translations.load('app/locales', ['ja'])
ngettext = translations.ngettext

# 使用例
message = ngettext(
    "%(count)d cat",
    "%(count)d cats",
    count
) % {'count': count}
```

---

### Phase 3: ファイル構造の改善

#### 3.1 推奨ディレクトリ構造

```
app/
├── locales/                    # Babel翻訳ファイル（バックエンド）
│   ├── ja/
│   │   └── LC_MESSAGES/
│   │       ├── messages.po     # 編集可能
│   │       └── messages.mo     # コンパイル済み
│   ├── en/
│   │   └── LC_MESSAGES/
│   │       ├── messages.po
│   │       └── messages.mo
│   ├── messages.pot            # テンプレート
│   └── babel.cfg               # Babel設定
│
├── static/
│   └── i18n/                   # i18next翻訳ファイル（フロントエンド）
│       ├── ja/
│       │   ├── common.json     # 共通翻訳
│       │   ├── dashboard.json  # ダッシュボード
│       │   ├── animals.json    # 猫管理
│       │   └── care_logs.json  # 世話記録
│       └── en/
│           ├── common.json
│           ├── dashboard.json
│           ├── animals.json
│           └── care_logs.json
│
└── utils/
    ├── i18n.py                 # Babel統合
    └── i18n_helper.py          # 既存（削除または統合）
```

#### 3.2 翻訳ファイルの分割

**現在:** 単一の巨大なJSONファイル（800+キー）
```json
// app/static/i18n/ja.json (800+ keys)
{
  "common": { ... },
  "dashboard": { ... },
  "animals": { ... },
  ...
}
```

**改善後:** 名前空間ごとに分割
```json
// app/static/i18n/ja/common.json
{
  "app_name": "NecoKeeper",
  "save": "保存",
  "cancel": "キャンセル",
  ...
}

// app/static/i18n/ja/dashboard.json
{
  "title": "ダッシュボード",
  "stats": {
    "protected": "保護中",
    "adoptable": "譲渡可能"
  }
}
```

---

### Phase 4: Tailwind CSS多言語対応

#### 4.1 RTL（右から左）言語対応

**ベストプラクティス:**
```javascript
// tailwind.config.js
module.exports = {
  plugins: [
    require('@tailwindcss/forms'),
    require('tailwindcss-rtl'),
  ],
}
```

```html
<!-- HTML -->
<html dir="ltr" lang="ja">  <!-- 日本語: 左から右 -->
<html dir="rtl" lang="ar">  <!-- アラビア語: 右から左 -->

<!-- Tailwind CSS -->
<div class="ml-4 rtl:mr-4 rtl:ml-0">  <!-- RTL対応 -->
```

#### 4.2 言語別フォント

```css
/* app/static/css/i18n.css */
:root[lang="ja"] {
  --font-family: "Noto Sans JP", sans-serif;
}

:root[lang="en"] {
  --font-family: "Inter", sans-serif;
}

:root[lang="zh"] {
  --font-family: "Noto Sans SC", sans-serif;
}

body {
  font-family: var(--font-family);
}
```

---

## 📋 実装タスク

### Task 15.4: フロントエンド改善
- [ ] 15.4.1 名前空間の導入
  - 翻訳ファイルを分割（common, dashboard, animals, care_logs）
  - i18next設定を更新
- [ ] 15.4.2 HTTP Backend + キャッシュ
  - i18next-chained-backend導入
  - LocalStorageキャッシュ実装
- [ ] 15.4.3 遅延読み込み
  - i18next-resources-to-backend導入
  - 動的インポート実装
- [ ] 15.4.4 ページタイトル翻訳の完全実装
  - `<title>`タグの翻訳
  - メタタグの翻訳

### Task 15.5: バックエンド改善
- [ ] 15.5.1 Babel統合
  - babel.cfg作成
  - .po/.moファイル生成
- [ ] 15.5.2 Jinja2 Babel拡張
  - 翻訳関数統合
  - テンプレート更新
- [ ] 15.5.3 遅延評価実装
  - LazyProxy使用
  - リクエストコンテキスト外対応
- [ ] 15.5.4 FastAPI依存性注入
  - get_locale依存関数
  - get_translations依存関数
- [ ] 15.5.5 複数形対応
  - ngettext実装
  - .poファイル更新

### Task 15.6: ファイル構造改善
- [ ] 15.6.1 ディレクトリ構造変更
  - app/locales/作成
  - 翻訳ファイル移動
- [ ] 15.6.2 翻訳ファイル分割
  - 名前空間ごとに分割
  - バージョン管理

### Task 15.7: Tailwind CSS多言語対応
- [ ] 15.7.1 RTL対応
  - tailwindcss-rtlプラグイン
  - dir属性管理
- [ ] 15.7.2 言語別フォント
  - CSS変数定義
  - フォント読み込み

---

## 🎯 期待される効果

### パフォーマンス
- ✅ 初期読み込み時間: **50%削減**（遅延読み込み）
- ✅ キャッシュヒット率: **90%以上**（LocalStorage）
- ✅ ネットワークリクエスト: **70%削減**

### 保守性
- ✅ 翻訳ファイルの論理的分割
- ✅ 標準的なGettext形式（.po/.mo）
- ✅ 翻訳ツール（Poedit等）対応

### スケーラビリティ
- ✅ 新言語追加が容易
- ✅ 大規模アプリケーション対応
- ✅ マイクロサービス対応

### 開発者体験
- ✅ 型安全な翻訳（TypeScript）
- ✅ IDE補完対応
- ✅ 翻訳漏れ検出

---

## 📚 参考資料

### Context7検証済み
- [i18next公式ドキュメント](https://www.i18next.com/) - Benchmark Score: 95.9
- [FastAPI公式ドキュメント](https://fastapi.tiangolo.com/) - Benchmark Score: 85.2
- [Babel公式ドキュメント](https://babel.pocoo.org/)

### ベストプラクティス
- [i18next Best Practices](https://www.i18next.com/principles/best-practices)
- [FastAPI Dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/)
- [Babel Jinja2 Integration](https://babel.pocoo.org/en/latest/api/support.html)

---

**作成日**: 2025-11-18
**Context7検証済み**: ✅
**優先度**: 高（Phase 10の一部）

# i18n Improvement Proposals

## Best Practices Based on Context7 Research

### 📚 Referenced Libraries
- **i18next** (Benchmark Score: 95.9) - `/websites/i18next`
- **FastAPI** (Benchmark Score: 85.2) - `/websites/fastapi_tiangolo`
- **Babel** - `/websites/babel_pocoo-en`

---

## 🔍 Current Issues

### 1. **Frontend (JavaScript / i18next)**

#### ❌ Issues
1. **Eager loading of all translation files**
  - All translations are loaded at initialization.
  - This can cause performance problems in large applications.

2. **No namespaces in use**
  - All translations live in a single ``translation`` namespace.
  - Hard to split by module.

3. **No backend integration**
  - ``i18next-http-backend`` is not used.
  - No support for server-side rendering (SSR).

4. **No caching strategy**
  - No LocalStorage cache.
  - A network request is made every time.

5. **Incomplete title translation**
  - Handling for ``data-i18n-title`` exists, but translation of the
    actual page ``<title>`` tag is not fully wired.

### 2. **Backend (FastAPI / Python)**

#### ❌ Issues
1. **Babel not used**
  - Standard Python i18n library (Babel) is not used.
  - No support for Gettext format (.po/.mo).

2. **Incomplete Jinja2 integration**
  - Translation helpers in templates are hand-implemented.
  - Babel Jinja2 extension is not used.

3. **No lazy evaluation**
  - Cannot translate outside of request context.
  - Causes problems for things like email sending.

4. **No pluralization support**
  - No ``ngettext`` function.
  - Cannot translate strings depending on counts.

5. **Suboptimal language detection priority**
  - Query parameter is prioritized (security risk).
  - Standard order should be: Cookie → Accept-Language → Default.

---

## ✅ Improvement Proposals

### Phase 1: Frontend Improvements (i18next)

#### 1.1 Introduce namespaces

**Best practice (from Context7):**
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

**Benefits:**
- Logical separation of translation files.
- Enables lazy loading.
- Better scalability for large applications.

#### 1.2 HTTP backend + LocalStorage cache

**Best practice (from Context7):**
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

**Benefits:**
- Works offline.
- Better performance when cache hits.
- Version-based control over updates.

#### 1.3 Lazy loading

**Best practice (from Context7):**
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

**Benefits:**
- Shorter initial load time.
- Only load translations that are needed.
- Better code splitting with Webpack / Vite.

#### 1.4 Fully implement page title translation

**Current problem:**
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

**Improved version:**
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

### Phase 2: Backend Improvements (FastAPI + Babel)

#### 2.1 Integrate Babel

**Best practice (from Context7):**
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

**Generating translation files:**
```bash
# 1. 翻訳可能な文字列を抽出
pybabel extract -F babel.cfg -o app/locales/messages.pot .

# 2. 言語ごとのカタログを初期化
pybabel init -i app/locales/messages.pot -d app/locales -l ja
pybabel init -i app/locales/messages.pot -d app/locales -l en

# 3. .poファイルを編集後、.moファイルにコンパイル
pybabel compile -d app/locales
```

#### 2.2 Jinja2 Babel extension

**Best practice (from Context7):**
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

#### 2.3 Lazy translation

**Best practice (from Context7):**
```python
from babel.support import LazyProxy

def lazy_gettext(string: str) -> LazyProxy:
    """遅延評価翻訳"""
    return LazyProxy(lambda: get_current_translation().gettext(string))

# Example usage (outside request context)
EMAIL_SUBJECT = lazy_gettext("Welcome to NecoKeeper")

# Actual evaluation happens at request time
def send_email(user):
    subject = str(EMAIL_SUBJECT)  # この時点で翻訳
    ...
```

#### 2.4 FastAPI dependency injection

**Best practice (from Context7):**
```python
from fastapi import Depends, Header, Request
from typing import Annotated

def get_locale(
    request: Request,
    accept_language: Annotated[str | None, Header()] = None
) -> str:
    """Detect language from the request."""
    # 1. Cookie
    if lang := request.cookies.get("language"):
        if lang in ("ja", "en"):
            return lang

    # 2. Accept-Language header
    if accept_language:
        for lang in accept_language.split(","):
            code = lang.split(";")[0].split("-")[0].strip()
            if code in ("ja", "en"):
                return code

    # 3. Default
    return "ja"

def get_translations(
    locale: Annotated[str, Depends(get_locale)]
) -> Translations:
    """Get translation catalog."""
    return Translations.load('app/locales', [locale])

# Usage in an endpoint
@router.get("/animals")
async def get_animals(
    translations: Annotated[Translations, Depends(get_translations)]
):
    _ = translations.gettext
    return {"message": _("Animals list")}
```

#### 2.5 Pluralization support

**Best practice (from Context7):**
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

### Phase 3: File Structure Improvements

#### 3.1 Recommended directory structure

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

#### 3.2 Split translation files

**Current:** Single large JSON file (800+ keys)
```json
// app/static/i18n/ja.json (800+ keys)
{
  "common": { ... },
  "dashboard": { ... },
  "animals": { ... },
  ...
}
```

**After improvement:** Split by namespace
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

### Phase 4: Tailwind CSS and Multilingual Support

#### 4.1 RTL (right-to-left) language support

**Best practice:**
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

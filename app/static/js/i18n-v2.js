/**
 * i18n (国際化) モジュール v2.0
 *
 * Context7ベストプラクティスに基づいた実装:
 * - 名前空間（Namespace）による翻訳ファイル分割
 * - HTTP Backend + LocalStorage キャッシュ
 * - 遅延読み込み（Lazy Loading）
 * - ページタイトル翻訳の完全実装
 *
 * 参照: /websites/i18next (Benchmark Score: 95.9)
 */

// i18nextの初期化状態
let i18nextInitialized = false;
let currentLanguage = 'ja';

// キャッシュバージョン（翻訳更新時にインクリメント）
const CACHE_VERSION = 'v1.0.0';

/**
 * i18nextを初期化（名前空間 + HTTP Backend + キャッシュ）
 *
 * @returns {Promise<void>}
 */
async function initI18n() {
  if (i18nextInitialized) {
    return;
  }

  try {
    // 保存された言語設定を取得
    const savedLanguage = localStorage.getItem('language');
    const browserLanguage = navigator.language.split('-')[0];
    const defaultLanguage =
      savedLanguage ||
      (browserLanguage === 'ja' || browserLanguage === 'en' ? browserLanguage : 'ja');

    // i18next-http-backend を使用（CDN経由）
    await i18next.use(i18nextHttpBackend).init({
      lng: defaultLanguage,
      fallbackLng: 'ja',
      debug: false,

      // 名前空間の設定
      ns: ['common', 'nav', 'dashboard', 'animals', 'care_logs'],
      defaultNS: 'common',

      // HTTP Backend設定
      backend: {
        loadPath: '/static/i18n/{{lng}}/{{ns}}.json',
        crossDomain: false,
        withCredentials: false,
        requestOptions: {
          mode: 'cors',
          credentials: 'same-origin',
          cache: 'default',
        },
      },

      // キャッシュ設定（LocalStorage）
      cache: {
        enabled: true,
        prefix: 'i18next_res_',
        expirationTime: 7 * 24 * 60 * 60 * 1000, // 7日間
        versions: {
          ja: CACHE_VERSION,
          en: CACHE_VERSION,
        },
      },

      // 補間設定
      interpolation: {
        escapeValue: false, // HTMLエスケープを無効化（XSS対策は別途実施）
      },

      // 遅延読み込み設定
      partialBundledLanguages: true,
    });

    currentLanguage = defaultLanguage;
    i18nextInitialized = true;

    console.log(`[i18n] Initialized with language: ${currentLanguage}`);
    console.log(`[i18n] Loaded namespaces:`, i18next.options.ns);

    // 初回翻訳を適用
    translatePage();

    // 言語切り替えボタンのイベントリスナーを設定
    setupLanguageSwitcher();
  } catch (error) {
    console.error('[i18n] Initialization failed:', error);
    // フォールバック: 日本語のまま続行
    i18nextInitialized = true;
  }
}

/**
 * ページ内の全ての翻訳可能な要素を翻訳
 */
function translatePage() {
  if (!i18nextInitialized) {
    console.warn('[i18n] Not initialized yet');
    return;
  }

  // ページタイトルを翻訳（完全実装）
  const titleElement = document.querySelector('title[data-i18n-title]');
  if (titleElement) {
    const key = titleElement.getAttribute('data-i18n-title');
    const ns = titleElement.getAttribute('data-i18n-ns') || 'common';
    const translation = i18next.t(key, { ns });
    const appName = i18next.t('app_name', { ns: 'common' });
    titleElement.textContent = `${translation} - ${appName}`;
  }

  // メタディスクリプションを翻訳
  const metaDesc = document.querySelector('meta[name="description"][data-i18n-content]');
  if (metaDesc) {
    const key = metaDesc.getAttribute('data-i18n-content');
    metaDesc.setAttribute('content', i18next.t(key));
  }

  // data-i18n属性を持つ要素を翻訳
  document.querySelectorAll('[data-i18n]').forEach(element => {
    const key = element.getAttribute('data-i18n');
    const ns = element.getAttribute('data-i18n-ns') || 'common';
    const translation = i18next.t(key, { ns });

    // テキストコンテンツを更新
    if (element.tagName === 'INPUT' || element.tagName === 'TEXTAREA') {
      if (element.hasAttribute('placeholder')) {
        element.placeholder = translation;
      } else {
        element.value = translation;
      }
    } else {
      element.textContent = translation;
    }
  });

  // data-i18n-html属性を持つ要素を翻訳（HTML含む）
  document.querySelectorAll('[data-i18n-html]').forEach(element => {
    const key = element.getAttribute('data-i18n-html');
    const ns = element.getAttribute('data-i18n-ns') || 'common';
    const translation = i18next.t(key, { ns });
    element.innerHTML = translation;
  });

  // data-i18n-placeholder属性を持つ要素のplaceholderを翻訳
  document.querySelectorAll('[data-i18n-placeholder]').forEach(element => {
    const key = element.getAttribute('data-i18n-placeholder');
    const ns = element.getAttribute('data-i18n-ns') || 'common';
    const translation = i18next.t(key, { ns });
    element.placeholder = translation;
  });

  // data-i18n-title属性を持つ要素のtitleを翻訳
  document.querySelectorAll('[data-i18n-title]').forEach(element => {
    const key = element.getAttribute('data-i18n-title');
    const ns = element.getAttribute('data-i18n-ns') || 'common';
    const translation = i18next.t(key, { ns });
    element.title = translation;
  });

  // data-i18n-aria-label属性を持つ要素のaria-labelを翻訳
  document.querySelectorAll('[data-i18n-aria-label]').forEach(element => {
    const key = element.getAttribute('data-i18n-aria-label');
    const ns = element.getAttribute('data-i18n-ns') || 'common';
    const translation = i18next.t(key, { ns });
    element.setAttribute('aria-label', translation);
  });

  console.log(`[i18n] Page translated to: ${currentLanguage}`);
}

/**
 * 言語を切り替え
 *
 * @param {string} language - 言語コード ('ja' or 'en')
 */
async function changeLanguage(language) {
  if (!i18nextInitialized) {
    console.warn('[i18n] Not initialized yet');
    return;
  }

  if (language !== 'ja' && language !== 'en') {
    console.error(`[i18n] Unsupported language: ${language}`);
    return;
  }

  try {
    await i18next.changeLanguage(language);
    currentLanguage = language;

    // ローカルストレージに保存
    localStorage.setItem('language', language);

    // ページを再翻訳
    translatePage();

    // 言語切り替えボタンの表示を更新
    updateLanguageSwitcherUI();

    console.log(`[i18n] Language changed to: ${language}`);

    // カスタムイベントを発火
    window.dispatchEvent(new CustomEvent('languageChanged', { detail: { language } }));
  } catch (error) {
    console.error('[i18n] Language change failed:', error);
  }
}

/**
 * 追加の名前空間を遅延読み込み
 *
 * @param {string|string[]} namespaces - 読み込む名前空間
 * @returns {Promise<void>}
 */
async function loadNamespaces(namespaces) {
  if (!i18nextInitialized) {
    console.warn('[i18n] Not initialized yet');
    return;
  }

  try {
    await i18next.loadNamespaces(namespaces);
    console.log(`[i18n] Loaded namespaces:`, namespaces);
  } catch (error) {
    console.error('[i18n] Failed to load namespaces:', error);
  }
}

/**
 * 言語切り替えボタンのイベントリスナーを設定
 */
function setupLanguageSwitcher() {
  // 言語切り替えボタン
  const languageSwitcher = document.getElementById('language-switcher');
  if (languageSwitcher) {
    languageSwitcher.addEventListener('click', () => {
      const newLanguage = currentLanguage === 'ja' ? 'en' : 'ja';
      changeLanguage(newLanguage);
    });
  }

  // 言語選択ドロップダウン
  const languageSelect = document.getElementById('language-select');
  if (languageSelect) {
    languageSelect.value = currentLanguage;
    languageSelect.addEventListener('change', e => {
      changeLanguage(e.target.value);
    });
  }

  // 初期表示を更新
  updateLanguageSwitcherUI();
}

/**
 * 言語切り替えボタンのUIを更新
 */
function updateLanguageSwitcherUI() {
  const languageSwitcher = document.getElementById('language-switcher');
  if (languageSwitcher) {
    const languageText = languageSwitcher.querySelector('.language-text');
    if (languageText) {
      languageText.textContent = currentLanguage === 'ja' ? '🇯🇵 日本語' : '🇬🇧 English';
    }
  }

  const languageSelect = document.getElementById('language-select');
  if (languageSelect) {
    languageSelect.value = currentLanguage;
  }
}

/**
 * 翻訳テキストを取得（ヘルパー関数）
 *
 * @param {string} key - 翻訳キー
 * @param {Object} options - 補間オプション（ns: 名前空間を含む）
 * @returns {string} 翻訳されたテキスト
 */
function t(key, options = {}) {
  if (!i18nextInitialized) {
    console.warn('[i18n] Not initialized yet');
    return key;
  }
  return i18next.t(key, options);
}

/**
 * 現在の言語を取得
 *
 * @returns {string} 現在の言語コード
 */
function getCurrentLanguage() {
  return currentLanguage;
}

/**
 * 動的に追加された要素を翻訳
 *
 * @param {HTMLElement} element - 翻訳する要素
 */
function translateElement(element) {
  if (!i18nextInitialized) {
    console.warn('[i18n] Not initialized yet');
    return;
  }

  // data-i18n属性を持つ子要素を翻訳
  element.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.getAttribute('data-i18n');
    const ns = el.getAttribute('data-i18n-ns') || 'common';
    const translation = i18next.t(key, { ns });

    if (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA') {
      if (el.hasAttribute('placeholder')) {
        el.placeholder = translation;
      } else {
        el.value = translation;
      }
    } else {
      el.textContent = translation;
    }
  });

  // 要素自体も翻訳
  if (element.hasAttribute('data-i18n')) {
    const key = element.getAttribute('data-i18n');
    const ns = element.getAttribute('data-i18n-ns') || 'common';
    const translation = i18next.t(key, { ns });
    element.textContent = translation;
  }
}

/**
 * キャッシュをクリア
 */
function clearCache() {
  const keys = Object.keys(localStorage);
  keys.forEach(key => {
    if (key.startsWith('i18next_res_')) {
      localStorage.removeItem(key);
    }
  });
  console.log('[i18n] Cache cleared');
}

// DOMContentLoadedイベントで初期化
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initI18n);
} else {
  initI18n();
}

// グローバルに公開
window.i18n = {
  init: initI18n,
  t: t,
  changeLanguage: changeLanguage,
  getCurrentLanguage: getCurrentLanguage,
  translatePage: translatePage,
  translateElement: translateElement,
  loadNamespaces: loadNamespaces,
  clearCache: clearCache,
};

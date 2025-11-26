/**
 * i18n (国際化) モジュール
 *
 * i18nextを使用した多言語対応機能を提供します。
 *
 * Features:
 * - 日本語・英語の切り替え
 * - ローカルストレージへの言語設定保存
 * - ブラウザ言語設定からの自動選択
 * - 動的な翻訳テキスト更新
 */

// i18nextの初期化状態
let i18nextInitialized = false;
let currentLanguage = 'ja';
const I18N_VERSION = '20241126v2';

/**
 * i18nextを初期化
 *
 * @returns {Promise<void>}
 */
async function initI18n() {
  if (i18nextInitialized) {
    return;
  }

  try {
    // Kiroweenモードかどうかを判定
    const isKiroween = document.body.classList.contains('kiroween-mode');

    // 保存された言語設定を取得、なければブラウザ言語を使用
    const savedLanguage = localStorage.getItem('language');
    const browserLanguage = navigator.language.split('-')[0]; // 'ja-JP' -> 'ja'

    // Kiroweenモードの場合は強制的に英語、それ以外は保存された設定またはブラウザ言語
    const defaultLanguage = isKiroween
      ? 'en'
      : savedLanguage ||
        (browserLanguage === 'ja' || browserLanguage === 'en' ? browserLanguage : 'ja');

    // Kiroweenモードの場合は単一のen_necro.jsonファイルを読み込み
    if (isKiroween) {
      const cacheBuster = `?v=${I18N_VERSION}`;
      const necroRes = await fetch(`/static/i18n/en_necro.json${cacheBuster}`);

      if (necroRes.ok) {
        const necroTranslations = await necroRes.json();

        // i18nextを初期化（Necro翻訳）
        await i18next.init({
          lng: 'en',
          fallbackLng: 'en',
          debug: false,
          resources: {
            en: necroTranslations,
          },
          ns: [
            'common',
            'nav',
            'dashboard',
            'animals',
            'care_logs',
            'medical_records',
            'medical_actions',
            'volunteers',
            'adoptions',
            'reports',
            'settings',
            'care',
            'login',
          ],
          defaultNS: 'common',
          interpolation: {
            escapeValue: false,
          },
        });

        currentLanguage = 'en';
        i18nextInitialized = true;

        console.log('[i18n] Initialized with NECRO-TERMINAL translations');

        // 初回翻訳を適用
        translatePage();

        // i18nextInitializedイベントを発火
        document.dispatchEvent(new Event('i18nextInitialized'));

        return;
      } else {
        console.error('[i18n] Failed to load en_necro.json, falling back to standard translations');
      }
    }

    // 標準モード: 翻訳ファイルを読み込み(名前空間ごと)
    const namespaces = [
      'common',
      'nav',
      'dashboard',
      'animals',
      'care_logs',
      'medical_records',
      'medical_actions',
      'volunteers',
      'adoptions',
      'reports', // Added reports namespace
      'settings', // Added settings namespace
      'care', // Added care namespace for public care form
      'login', // Added login namespace
    ];
    const jaTranslations = {};
    const enTranslations = {};

    // 各名前空間の翻訳ファイルを読み込み
    await Promise.all(
      namespaces.map(async ns => {
        try {
          const cacheBuster = `?v=${I18N_VERSION}`;
          const jaRes = await fetch(`/static/i18n/ja/${ns}.json${cacheBuster}`);
          const enRes = await fetch(`/static/i18n/en/${ns}.json${cacheBuster}`);

          if (jaRes.ok) {
            jaTranslations[ns] = await jaRes.json();
          }
          if (enRes.ok) {
            enTranslations[ns] = await enRes.json();
          }
        } catch (err) {
          console.warn(`[i18n] Failed to load namespace: ${ns}`, err);
        }
      })
    );

    // i18nextを初期化
    await i18next.init({
      lng: defaultLanguage,
      fallbackLng: 'ja',
      debug: false,
      ns: namespaces,
      defaultNS: 'common',
      fallbackNS: 'common',
      resources: {
        ja: jaTranslations,
        en: enTranslations,
      },
      interpolation: {
        escapeValue: false, // HTMLエスケープを無効化（XSS対策は別途実施）
      },
    });

    currentLanguage = defaultLanguage;
    i18nextInitialized = true;

    console.log(`[i18n] Initialized with language: ${currentLanguage}`);
    console.log(`[i18n] Loaded namespaces:`, namespaces);

    // 初回翻訳を適用
    translatePage();

    // i18nextInitializedイベントを発火
    document.dispatchEvent(new Event('i18nextInitialized'));

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

  // data-i18n属性を持つ要素を翻訳
  document.querySelectorAll('[data-i18n]').forEach(element => {
    const key = element.getAttribute('data-i18n');
    const ns = element.getAttribute('data-i18n-ns') || 'common';

    // 名前空間付きで翻訳を取得（ネストされたキーをサポート）
    const translation = i18next.t(key, { ns, defaultValue: key });

    // テキストコンテンツを更新
    if (element.tagName === 'INPUT' || element.tagName === 'TEXTAREA') {
      // input要素の場合はplaceholderを更新
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
    if (element.tagName === 'TITLE') {
      const suffix = element.getAttribute('data-i18n-title-suffix') || '';
      document.title = `${translation}${suffix}`;
    } else {
      element.title = translation;
    }
  });

  // data-i18n-aria-label属性を持つ要素のaria-labelを翻訳
  document.querySelectorAll('[data-i18n-aria-label]').forEach(element => {
    const key = element.getAttribute('data-i18n-aria-label');
    const ns = element.getAttribute('data-i18n-ns') || 'common';
    const translation = i18next.t(key, { ns });
    element.setAttribute('aria-label', translation);
  });

  // data-i18n-alt属性を持つ要素のaltを翻訳
  document.querySelectorAll('[data-i18n-alt]').forEach(element => {
    const key = element.getAttribute('data-i18n-alt');
    const ns = element.getAttribute('data-i18n-ns') || 'common';
    const translation = i18next.t(key, { ns });
    element.alt = translation;
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

  // Kiroweenモードでは言語切り替えを無効化
  const isKiroween = document.body.classList.contains('kiroween-mode');
  if (isKiroween) {
    console.log('[i18n] Language switching disabled in NECRO-TERMINAL mode');
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

    // languageChangedイベントを発火
    document.dispatchEvent(new Event('languageChanged'));

    console.log(`[i18n] Language changed to: ${language}`);

    // カスタムイベントを発火（他のコンポーネントが言語変更を検知できるように）
    window.dispatchEvent(new CustomEvent('languageChanged', { detail: { language } }));
  } catch (error) {
    console.error('[i18n] Language change failed:', error);
  }
}

/**
 * 言語切り替えボタンのイベントリスナーを設定
 */
function setupLanguageSwitcher() {
  const attachHandlers = () => {
    const languageSwitcher = document.getElementById('language-switcher');
    if (languageSwitcher && !languageSwitcher.dataset.listenerAttached) {
      languageSwitcher.dataset.listenerAttached = 'true';
      languageSwitcher.addEventListener('click', () => {
        const newLanguage = currentLanguage === 'ja' ? 'en' : 'ja';
        changeLanguage(newLanguage);
      });
    }

    const languageSelect = document.getElementById('language-select');
    if (languageSelect) {
      languageSelect.value = currentLanguage;
      if (!languageSelect.dataset.listenerAttached) {
        languageSelect.dataset.listenerAttached = 'true';
        languageSelect.addEventListener('change', e => {
          changeLanguage(e.target.value);
        });
      }
    }

    updateLanguageSwitcherUI();
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', attachHandlers, { once: true });
  } else {
    attachHandlers();
  }
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
 * @param {Object} options - 補間オプション
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

// DOMContentLoadedイベントで初期化
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initI18n);
} else {
  // すでにDOMが読み込まれている場合は即座に初期化
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
};

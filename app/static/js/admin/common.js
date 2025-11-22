/**
 * 管理画面共通JavaScript
 * Context7参照: /bigskysoftware/htmx (Trust Score: 90.7)
 */

// API Base URL
const API_BASE = '/api/v1';

/**
 * トーストメッセージを表示
 * @param {string} message - 表示するメッセージ
 * @param {string} type - メッセージタイプ ('success', 'error', 'info', 'warning')
 * @param {number} duration - 表示時間（ミリ秒）
 */
function showToast(message, type = 'info', duration = 3000) {
  const container = document.getElementById('toast-container');
  if (!container) return;

  const toast = document.createElement('div');
  toast.className = `toast-${type} px-6 py-4 rounded-lg shadow-lg transform transition-all duration-300 translate-x-full`;

  // タイプ別のスタイル
  const styles = {
    success: 'bg-green-500 text-white',
    error: 'bg-red-500 text-white',
    warning: 'bg-yellow-500 text-white',
    info: 'bg-blue-500 text-white',
  };

  toast.className += ` ${styles[type] || styles.info}`;

  // アイコン
  const icons = {
    success: '✓',
    error: '✕',
    warning: '⚠',
    info: 'ℹ',
  };

  toast.innerHTML = `
        <div class="flex items-center gap-3">
            <span class="text-xl">${icons[type] || icons.info}</span>
            <span class="font-medium">${message}</span>
        </div>
    `;

  container.appendChild(toast);

  // アニメーション
  setTimeout(() => {
    toast.classList.remove('translate-x-full');
  }, 10);

  // 自動削除
  setTimeout(() => {
    toast.classList.add('translate-x-full');
    setTimeout(() => {
      container.removeChild(toast);
    }, 300);
  }, duration);
}

/**
 * 確認ダイアログを表示
 * @param {string} message - 確認メッセージ
 * @returns {boolean} - ユーザーの選択
 */
function confirmAction(message) {
  return confirm(message);
}

/**
 * 日付を YYYY-MM-DD 形式にフォーマット
 * @param {Date|string} dateInput - 日付オブジェクトまたはISO形式の日付文字列
 * @returns {string} - フォーマットされた日付文字列
 */
function formatDate(dateInput) {
  if (!dateInput) return '-';

  try {
    // 文字列の場合はDateオブジェクトに変換
    const date = typeof dateInput === 'string' ? new Date(dateInput) : dateInput;

    // 無効な日付をチェック
    if (isNaN(date.getTime())) {
      console.error('Invalid date:', dateInput);
      return '-';
    }

    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  } catch (error) {
    console.error('Error formatting date:', error, 'input:', dateInput);
    return '-';
  }
}

/**
 * 日時を YYYY-MM-DD HH:MM 形式にフォーマット
 * 多言語対応: 現在の言語設定に応じてロケールを使用
 * @param {string} dateTimeString - ISO形式の日時文字列
 * @returns {string} - フォーマットされた日時文字列
 */
function formatDateTime(dateTimeString) {
  if (!dateTimeString) return '-';

  try {
    const date = new Date(dateTimeString);

    if (isNaN(date.getTime())) {
      console.error('Invalid date:', dateTimeString);
      return '-';
    }

    // i18nextから現在の言語を取得
    const currentLanguage = window.i18next?.language || 'ja';
    const locale = currentLanguage === 'en' ? 'en-US' : 'ja-JP';

    return date.toLocaleString(locale, {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    });
  } catch (error) {
    console.error('Error formatting datetime:', error, 'input:', dateTimeString);
    return '-';
  }
}

const STATUS_KEY_MAP = {
  保護中: 'protected',
  protected: 'protected',
  治療中: 'treatment',
  treatment: 'treatment',
  譲渡可能: 'adoptable',
  adoptable: 'adoptable',
  譲渡済み: 'adopted',
  adopted: 'adopted',
  死亡: 'deceased',
  deceased: 'deceased',
};

const STATUS_STYLE_MAP = {
  protected: 'px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded-full',
  treatment: 'px-2 py-1 text-xs font-medium bg-yellow-100 text-yellow-800 rounded-full',
  adoptable: 'px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded-full',
  adopted: 'px-2 py-1 text-xs font-medium bg-gray-100 text-gray-800 rounded-full',
  deceased: 'px-2 py-1 text-xs font-medium bg-red-100 text-red-800 rounded-full',
};

function normalizeStatusKey(status) {
  if (!status) {
    return null;
  }
  const trimmed = status.trim();
  if (STATUS_KEY_MAP[trimmed]) {
    return STATUS_KEY_MAP[trimmed];
  }
  const lower = trimmed.toLowerCase();
  return STATUS_KEY_MAP[lower] || null;
}

function translateStatusLabel(statusKey, fallback) {
  const translator = window.i18n?.t
    ? window.i18n.t
    : window.i18next?.t
      ? window.i18next.t.bind(window.i18next)
      : null;

  if (!translator || !statusKey) {
    return fallback;
  }

  return translator(`animals:status.${statusKey}`, { defaultValue: fallback }) || fallback;
}

/**
 * ステータスバッジのHTMLを生成
 * @param {string} status - ステータス
 * @returns {string} - バッジHTML
 */
function getStatusBadge(status) {
  const statusKey = normalizeStatusKey(status);
  const label = translateStatusLabel(statusKey, status || '');
  const classes =
    (statusKey && STATUS_STYLE_MAP[statusKey]) ||
    'px-2 py-1 text-xs font-medium bg-gray-100 text-gray-800 rounded-full';

  return `<span class="${classes}">${label || ''}</span>`;
}

/**
 * 時点の日本語表示を取得
 * @param {string} timeSlot - 時点 ('morning', 'noon', 'evening')
 * @returns {string} - 日本語表示
 */
function getTimeSlotLabel(timeSlot) {
  const labels = {
    morning: '朝',
    noon: '昼',
    evening: '夜',
  };
  return labels[timeSlot] || timeSlot;
}

/**
 * 認証トークンを取得
 * @returns {string|null} - アクセストークン
 */
function getAccessToken() {
  return localStorage.getItem('access_token');
}

/**
 * ログアウト処理
 */
function logout() {
  localStorage.removeItem('access_token');
  localStorage.removeItem('token_type');
  window.location.href = '/admin/login';
}

/**
 * 認証チェック
 */
function checkAuth() {
  const token = getAccessToken();
  if (!token) {
    window.location.href = '/admin/login';
  }
}

/**
 * APIリクエストを送信
 * @param {string} url - リクエストURL
 * @param {object} options - fetchオプション
 * @returns {Promise} - レスポンス（JSONパース済み）
 *
 * Example:
 *   // GET request
 *   const data = await apiRequest('/api/v1/animals');
 *
 *   // POST request
 *   const result = await apiRequest('/api/v1/animals', {
 *     method: 'POST',
 *     body: JSON.stringify({ name: 'たま' })
 *   });
 *
 *   // Custom headers
 *   const data = await apiRequest('/api/v1/animals', {
 *     headers: { 'X-Custom': 'value' }
 *   });
 */
async function apiRequest(url, options = {}) {
  try {
    const token = getAccessToken();

    // デフォルトヘッダーの設定
    const defaultHeaders = {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` }),
    };

    const response = await fetch(url, {
      ...options,
      headers: {
        ...defaultHeaders,
        ...options.headers,
      },
    });

    // 401エラーの場合はログイン画面にリダイレクト
    if (response.status === 401) {
      logout();
      return null;
    }

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.detail || `リクエストに失敗しました (${response.status})`);
    }

    // レスポンスボディが空の場合は null を返す
    const contentType = response.headers.get('content-type');
    if (contentType && contentType.includes('application/json')) {
      return await response.json();
    }

    return null;
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
}

// HTMXイベントハンドラー
document.addEventListener('htmx:afterRequest', event => {
  const xhr = event.detail.xhr;

  // エラーハンドリング
  if (xhr.status >= 400) {
    try {
      const error = JSON.parse(xhr.responseText);
      showToast(error.detail || 'エラーが発生しました', 'error');
    } catch {
      showToast('エラーが発生しました', 'error');
    }
  }
});

// ページ読み込み時に認証チェック
document.addEventListener('DOMContentLoaded', () => {
  // ログインページ以外では認証チェック
  if (!window.location.pathname.includes('/login')) {
    checkAuth();
  }
});

// グローバルエクスポート
window.showToast = showToast;
window.confirmAction = confirmAction;
window.formatDate = formatDate;
window.formatDateTime = formatDateTime;
window.getStatusBadge = getStatusBadge;
window.getTimeSlotLabel = getTimeSlotLabel;
window.apiRequest = apiRequest;
window.getAccessToken = getAccessToken;
window.getToken = getAccessToken; // エイリアス（後方互換性のため）
window.logout = logout;
window.checkAuth = checkAuth;
window.API_BASE = API_BASE;
window.applyDynamicTranslations = applyDynamicTranslations;
window.translate = translate;

/**
 * 動的に生成されたコンテンツに翻訳を適用
 * @param {HTMLElement} container - 翻訳を適用するコンテナ要素
 */
function applyDynamicTranslations(container) {
  if (!window.i18next || !container) {
    return;
  }

  // data-i18n属性を持つすべての要素に翻訳を適用
  container.querySelectorAll('[data-i18n]').forEach(element => {
    const key = element.getAttribute('data-i18n');
    const ns = element.getAttribute('data-i18n-ns') || 'common';

    if (key) {
      const translation = window.i18next.t(key, { ns });
      element.textContent = translation;
    }
  });
}

/**
 * 翻訳関数（i18nextのラッパー）
 * @param {string} key - 翻訳キー
 * @param {object} options - オプション（defaultValue, ns など）
 * @returns {string} - 翻訳されたテキスト
 */
function translate(key, options = {}) {
  if (!window.i18next) {
    return options.defaultValue || key;
  }

  const ns = options.ns || 'common';
  return window.i18next.t(key, { ...options, ns });
}

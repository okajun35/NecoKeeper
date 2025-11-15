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
 * @param {Date} date - 日付オブジェクト
 * @returns {string} - フォーマットされた日付文字列
 */
function formatDate(date) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

/**
 * 日時を YYYY-MM-DD HH:MM 形式にフォーマット
 * @param {string} dateTimeString - ISO形式の日時文字列
 * @returns {string} - フォーマットされた日時文字列
 */
function formatDateTime(dateTimeString) {
  const date = new Date(dateTimeString);
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  const hours = String(date.getHours()).padStart(2, '0');
  const minutes = String(date.getMinutes()).padStart(2, '0');
  return `${year}-${month}-${day} ${hours}:${minutes}`;
}

/**
 * ステータスバッジのHTMLを生成
 * @param {string} status - ステータス
 * @returns {string} - バッジHTML
 */
function getStatusBadge(status) {
  const badges = {
    保護中:
      '<span class="px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded-full">保護中</span>',
    治療中:
      '<span class="px-2 py-1 text-xs font-medium bg-yellow-100 text-yellow-800 rounded-full">治療中</span>',
    譲渡可能:
      '<span class="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded-full">譲渡可能</span>',
    譲渡済み:
      '<span class="px-2 py-1 text-xs font-medium bg-gray-100 text-gray-800 rounded-full">譲渡済み</span>',
  };
  return (
    badges[status] ||
    `<span class="px-2 py-1 text-xs font-medium bg-gray-100 text-gray-800 rounded-full">${status}</span>`
  );
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
 * APIリクエストを送信
 * @param {string} url - リクエストURL
 * @param {object} options - fetchオプション
 * @returns {Promise} - レスポンス
 */
async function apiRequest(url, options = {}) {
  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'リクエストに失敗しました');
    }

    return await response.json();
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

// グローバルエクスポート
window.showToast = showToast;
window.confirmAction = confirmAction;
window.formatDate = formatDate;
window.formatDateTime = formatDateTime;
window.getStatusBadge = getStatusBadge;
window.getTimeSlotLabel = getTimeSlotLabel;
window.apiRequest = apiRequest;
window.API_BASE = API_BASE;

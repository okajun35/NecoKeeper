/**
 * 猫管理 JavaScript
 * Context7参照: /bigskysoftware/htmx (Trust Score: 90.7)
 */

const I18N_NAMESPACE = 'animals';
const COMMON_NAMESPACE = 'common';

let currentPage = 1;
let currentPageSize = 20;
let currentStatus = '';
let currentSearch = '';
let advancedFilters = {
  gender: '',
  ageMin: null,
  ageMax: null,
  rescueDateFrom: '',
  rescueDateTo: '',
  earCut: '',
  collar: '',
};
let lastAnimals = [];
let lastPagination = { total: 0, page: 1, pageSize: currentPageSize };
let hasLoadedAnimals = false;

function translate(key, options = {}) {
  const { ns = I18N_NAMESPACE, defaultValue = '', ...rest } = options;
  const namespacedKey = `${ns}:${key}`;

  if (window.i18n?.t) {
    return window.i18n.t(namespacedKey, { defaultValue, ...rest }) || defaultValue || key;
  }

  if (window.i18next?.t) {
    return window.i18next.t(namespacedKey, { defaultValue, ...rest }) || defaultValue || key;
  }

  return defaultValue || key;
}

function applyDynamicTranslations(element) {
  if (window.i18n?.translateElement && element) {
    window.i18n.translateElement(element);
  }
}

// DBの値を翻訳キーにマッピング
const DB_VALUE_MAPS = {
  gender: {
    male: 'gender.male',
    female: 'gender.female',
    unknown: 'gender.unknown',
    オス: 'gender.male',
    メス: 'gender.female',
    不明: 'gender.unknown',
  },
  age: {
    子猫: 'age.kitten',
    成猫: 'age.adult',
    老猫: 'age.senior',
    kitten: 'age.kitten',
    adult: 'age.adult',
    senior: 'age.senior',
  },
};

function translateDBValue(category, value) {
  if (!value) return '-';
  const map = DB_VALUE_MAPS[category];
  if (map && map[value]) {
    return translate(map[value], { defaultValue: value });
  }
  return value;
}

// 猫一覧を読み込み
async function loadAnimals() {
  try {
    const listContainer = document.getElementById('animals-list');
    if (listContainer) {
      const loadingMessage = translate('loading', {
        ns: COMMON_NAMESPACE,
        defaultValue: '読み込み中...',
      });
      listContainer.innerHTML = `
        <div class="p-8 text-center text-gray-500" data-i18n="loading" data-i18n-ns="common">
          ${loadingMessage}
        </div>`;
      applyDynamicTranslations(listContainer);
    }

    const params = new URLSearchParams({
      page: currentPage,
      page_size: currentPageSize,
    });

    if (currentStatus) {
      params.append('status', currentStatus);
    }

    // 詳細検索フィルター
    if (advancedFilters.gender) {
      params.append('gender', advancedFilters.gender);
    }
    if (advancedFilters.ageMin !== null && advancedFilters.ageMin !== '') {
      params.append('age_min', advancedFilters.ageMin);
    }
    if (advancedFilters.ageMax !== null && advancedFilters.ageMax !== '') {
      params.append('age_max', advancedFilters.ageMax);
    }
    if (advancedFilters.rescueDateFrom) {
      params.append('rescue_date_from', advancedFilters.rescueDateFrom);
    }
    if (advancedFilters.rescueDateTo) {
      params.append('rescue_date_to', advancedFilters.rescueDateTo);
    }
    if (advancedFilters.earCut) {
      params.append('ear_cut', advancedFilters.earCut);
    }
    if (advancedFilters.collar) {
      params.append('collar', advancedFilters.collar);
    }

    const url = currentSearch
      ? `${API_BASE}/animals/search?q=${encodeURIComponent(currentSearch)}&${params}`
      : `${API_BASE}/animals?${params}`;

    const response = await apiRequest(url);

    if (!response) {
      return;
    }

    renderAnimalsList(response.items || []);
    renderPagination(response.total || 0, response.page || 1, response.page_size || 20);
  } catch (error) {
    console.error('Animals load error:', error);
    const errorMessage = translate('list.load_error', {
      defaultValue: '猫一覧の読み込みに失敗しました',
    });
    showToast(errorMessage, 'error');

    const listContainer = document.getElementById('animals-list');
    if (listContainer) {
      listContainer.innerHTML = `
        <div class="p-8 text-center text-red-500" data-i18n="list.load_error" data-i18n-ns="animals">
          ${errorMessage}
        </div>`;
      applyDynamicTranslations(listContainer);
    }
  }
}

// 猫一覧を描画
function renderAnimalsList(animals = []) {
  const container = document.getElementById('animals-list');
  if (!container) {
    return;
  }
  lastAnimals = animals;

  if (animals.length === 0) {
    const emptyMessage = translate('list.empty', {
      defaultValue: '猫が見つかりませんでした',
    });
    container.innerHTML = `
      <div class="p-8 text-center text-gray-500" data-i18n="list.empty" data-i18n-ns="animals">
        ${emptyMessage}
      </div>`;
    applyDynamicTranslations(container);
    hasLoadedAnimals = true;
    return;
  }

  container.innerHTML = animals
    .map(animal => {
      const photoUrl =
        animal.photo && animal.photo.trim() !== '' ? animal.photo : '/static/images/default.svg';
      const displayName =
        animal.name && animal.name.trim() !== ''
          ? animal.name
          : translate('fallbacks.no_name', { defaultValue: '名前なし' });

      return `
        <div class="p-6 hover:bg-gray-50 transition-colors">
            <div class="flex items-center gap-6">
                <!-- 写真 -->
                <img src="${photoUrl}"
                     alt="${displayName}"
                     onerror="this.onerror=null; this.src='/static/images/default.svg';"
                     class="w-20 h-20 rounded-lg object-cover border-2 border-gray-200">

                <!-- 基本情報 -->
                <div class="flex-1 min-w-0">
                    <div class="flex items-center gap-3 mb-2">
                        <h3 class="text-lg font-semibold text-gray-900">${displayName}</h3>
                        ${getStatusBadge(animal.status)}
                    </div>
                    <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm text-gray-600">
                        <div>
                            <span class="text-gray-500"><span data-i18n="fields.pattern" data-i18n-ns="animals">柄</span>:</span>
                            <span class="ml-1">${animal.pattern || '-'}</span>
                        </div>
                        <div>
                            <span class="text-gray-500"><span data-i18n="fields.gender" data-i18n-ns="animals">性別</span>:</span>
                            <span class="ml-1">${translateDBValue('gender', animal.gender)}</span>
                        </div>
                        <div>
                            <span class="text-gray-500"><span data-i18n="fields.age" data-i18n-ns="animals">年齢</span>:</span>
                            <span class="ml-1">${translateDBValue('age', animal.age)}</span>
                        </div>
                        <div>
                            <span class="text-gray-500"><span data-i18n="fields.protected_at" data-i18n-ns="animals">保護日</span>:</span>
                            <span class="ml-1">${animal.rescue_date ? formatDate(new Date(animal.rescue_date)) : '-'}</span>
                        </div>
                    </div>
                </div>

                <!-- アクション -->
                <div class="flex gap-2">
                    <a href="/admin/animals/${animal.id}"
                       class="px-4 py-2 text-sm bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
                       data-i18n="actions.view_details" data-i18n-ns="animals">
                        詳細
                    </a>
                    <a href="/admin/animals/${animal.id}/edit"
                       class="px-4 py-2 text-sm bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
                       data-i18n="actions.edit_info" data-i18n-ns="animals">
                        編集
                    </a>
                    <button onclick="showQRCode(${animal.id})"
                            class="px-4 py-2 text-sm bg-green-100 text-green-700 rounded-lg hover:bg-green-200 transition-colors"
                            data-i18n="actions.qr_code" data-i18n-ns="animals">
                        QR
                    </button>
                </div>
            </div>
        </div>
    `;
    })
    .join('');

  applyDynamicTranslations(container);
  hasLoadedAnimals = true;
}

// ページネーションを描画
function renderPagination(total, page, pageSize) {
  const totalPages = Math.ceil(total / pageSize);
  const container = document.getElementById('pagination');
  if (!container) {
    return;
  }
  lastPagination = { total, page, pageSize };

  if (totalPages <= 1) {
    container.innerHTML = '';
    return;
  }

  const pages = [];
  const maxVisible = 5;
  let startPage = Math.max(1, page - Math.floor(maxVisible / 2));
  let endPage = Math.min(totalPages, startPage + maxVisible - 1);

  if (endPage - startPage < maxVisible - 1) {
    startPage = Math.max(1, endPage - maxVisible + 1);
  }

  for (let i = startPage; i <= endPage; i++) {
    pages.push(i);
  }

  container.innerHTML = `
        <div class="flex items-center justify-between">
            <div class="text-sm text-gray-600">
                ${translate('pagination.summary', {
                  defaultValue: `全 ${total} 件中 ${(page - 1) * pageSize + 1} - ${Math.min(
                    page * pageSize,
                    total
                  )} 件を表示`,
                  total,
                  from: (page - 1) * pageSize + 1,
                  to: Math.min(page * pageSize, total),
                })}
            </div>
            <div class="flex gap-2">
                <button onclick="changePage(${page - 1})"
                        ${page === 1 ? 'disabled' : ''}
                        class="px-3 py-2 text-sm border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed">
                    ${translate('pagination.previous', {
                      ns: COMMON_NAMESPACE,
                      defaultValue: '前へ',
                    })}
                </button>
                ${pages
                  .map(
                    p => `
                    <button onclick="changePage(${p})"
                            class="px-3 py-2 text-sm border rounded-lg ${p === page ? 'bg-indigo-600 text-white border-indigo-600' : 'border-gray-300 hover:bg-gray-50'}">
                        ${p}
                    </button>
                `
                  )
                  .join('')}
                <button onclick="changePage(${page + 1})"
                        ${page === totalPages ? 'disabled' : ''}
                    class="px-3 py-2 text-sm border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed">
                  ${translate('pagination.next', {
                    ns: COMMON_NAMESPACE,
                    defaultValue: '次へ',
                  })}
                </button>
            </div>
        </div>
    `;
}

// ページ変更
function changePage(page) {
  currentPage = page;
  loadAnimals();
}

// QRコードを表示
function showQRCode(animalId) {
  const qrUrl = `${API_BASE}/animals/${animalId}/qr`;
  const publicUrl = `/public/care?animal_id=${animalId}`;
  const modalTitle = translate('modals.qr_code.title', {
    defaultValue: 'QRコード',
  });
  const modalDescription = translate('modals.qr_code.description', {
    defaultValue: 'このQRコードをスキャンすると、世話記録入力画面が開きます',
  });
  const linkText = translate('modals.qr_code.link_text', {
    defaultValue: '世話記録入力画面を開く',
  });

  // モーダルを作成
  const modal = document.createElement('div');
  modal.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';
  modal.innerHTML = `
    <div class="bg-white rounded-lg p-6 max-w-md w-full mx-4">
      <div class="flex justify-between items-center mb-4">
        <h3 class="text-lg font-semibold">${modalTitle}</h3>
        <button onclick="this.closest('.fixed').remove()"
                class="text-gray-500 hover:text-gray-700">
          ✕
        </button>
      </div>
      <div class="flex justify-center">
        <img src="${qrUrl}" alt="QRコード" class="w-64 h-64">
      </div>
      <div class="mt-4 text-center">
        <a href="${publicUrl}" target="_blank" class="text-indigo-600 hover:text-indigo-800 underline flex items-center justify-center gap-1">
          ${linkText}
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path>
          </svg>
        </a>
      </div>
      <p class="mt-4 text-sm text-gray-600 text-center">
        ${modalDescription}
      </p>
    </div>
  `;

  document.body.appendChild(modal);

  // 背景クリックで閉じる
  modal.addEventListener('click', e => {
    if (e.target === modal) {
      modal.remove();
    }
  });
}

// イベントリスナー
document.addEventListener('DOMContentLoaded', () => {
  // i18nextの初期化を待ってから読み込み
  if (window.i18next && window.i18next.isInitialized) {
    loadAnimals();
  } else {
    // i18nextの初期化を待つ
    const checkI18next = setInterval(() => {
      if (window.i18next && window.i18next.isInitialized) {
        clearInterval(checkI18next);
        loadAnimals();
      }
    }, 100);

    // タイムアウト（5秒）
    setTimeout(() => {
      clearInterval(checkI18next);
      if (!hasLoadedAnimals) {
        loadAnimals();
      }
    }, 5000);
  }

  // 検索
  const searchInput = document.getElementById('search');
  let searchTimeout;
  searchInput.addEventListener('input', e => {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
      currentSearch = e.target.value;
      currentPage = 1;
      loadAnimals();
    }, 500);
  });

  // ステータスフィルター
  document.getElementById('status-filter').addEventListener('change', e => {
    currentStatus = e.target.value;
    currentPage = 1;
    loadAnimals();
  });

  // 表示件数
  document.getElementById('page-size').addEventListener('change', e => {
    currentPageSize = parseInt(e.target.value);
    currentPage = 1;
    loadAnimals();
  });
});

window.addEventListener('languageChanged', () => {
  if (!hasLoadedAnimals) {
    return;
  }
  renderAnimalsList(lastAnimals);
  renderPagination(lastPagination.total, lastPagination.page, lastPagination.pageSize);
});

// グローバルエクスポート
window.changePage = changePage;
window.showQRCode = showQRCode;

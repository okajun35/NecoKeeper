/**
 * 猫管理 JavaScript
 * Context7参照: /bigskysoftware/htmx (Trust Score: 90.7)
 */

const I18N_NAMESPACE = 'animals';
const COMMON_NAMESPACE = 'common';

const isKiroweenMode = document.body && document.body.classList.contains('kiroween-mode');
const DEFAULT_IMAGE_PLACEHOLDER = isKiroweenMode
  ? '/static/icons/halloween_logo_2.webp'
  : '/static/images/default.svg';
const adminBasePath = window.ADMIN_BASE_PATH || window.__ADMIN_BASE_PATH__ || '/admin';

let currentPage = 1;
let currentPageSize = 20;
let currentStatus = 'ACTIVE'; // デフォルトは「現在活動している猫」
let currentSearch = '';
let advancedFilters = {
  gender: '',
  fiv: '',
  felv: '',
  isSterilized: '',
  locationType: '',
  isReadyForAdoption: '',
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
};

function translateDBValue(category, value) {
  if (!value) return '-';
  const map = DB_VALUE_MAPS[category];
  if (map && map[value]) {
    return translate(map[value], { defaultValue: value });
  }
  return value;
}

function formatAgeMonths(ageMonths, isEstimated) {
  if (ageMonths === null || ageMonths === undefined || ageMonths === '') {
    return translate('age_unknown', { defaultValue: '-' });
  }
  const formatKey = isEstimated ? 'age_months_estimated' : 'age_months';
  return translate(formatKey, { value: ageMonths, defaultValue: `${ageMonths}` });
}

// FIV/FeLV検査結果をフォーマット
function formatTestResult(value, testName) {
  if (value === true) {
    return `<span class="text-red-600 font-medium">${translate('test_result.positive', { defaultValue: '陽性' })}</span>`;
  } else if (value === false) {
    return `<span class="text-green-600">${translate('test_result.negative', { defaultValue: '陰性' })}</span>`;
  }
  return translate('test_result.unknown', { defaultValue: '不明' });
}

// 避妊・去勢状態をフォーマット
function formatSterilized(value) {
  if (value === true) {
    return translate('sterilized.done', { defaultValue: '済' });
  } else if (value === false) {
    return translate('sterilized.not_done', { defaultValue: '未' });
  }
  return translate('sterilized.unknown', { defaultValue: '不明' });
}

// 場所をフォーマット
function formatLocation(locationType, locationNote) {
  const typeLabels = {
    FACILITY: translate('location_type.FACILITY', { defaultValue: '施設' }),
    FOSTER_HOME: translate('location_type.FOSTER_HOME', { defaultValue: '預かり宅' }),
    ADOPTER_HOME: translate('location_type.ADOPTER_HOME', { defaultValue: '譲渡先' }),
  };
  const typeLabel = typeLabels[locationType] || locationType || '-';

  if (locationNote && locationNote.trim()) {
    return `${typeLabel} (${locationNote})`;
  }
  return typeLabel;
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
    if (advancedFilters.fiv) {
      params.append('fiv', advancedFilters.fiv);
    }
    if (advancedFilters.felv) {
      params.append('felv', advancedFilters.felv);
    }
    if (advancedFilters.isSterilized) {
      params.append('is_sterilized', advancedFilters.isSterilized);
    }
    if (advancedFilters.locationType) {
      params.append('location_type', advancedFilters.locationType);
    }
    if (advancedFilters.isReadyForAdoption) {
      params.append('is_ready_for_adoption', advancedFilters.isReadyForAdoption);
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

  container.innerHTML = '';

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

  animals.forEach(animal => {
    const card = cloneTemplate('tmpl-animal-card');
    assertRequiredSelectors(
      card,
      [
        '.js-photo',
        '.js-name',
        '.js-id',
        '.js-status-badge',
        '.js-ready-badge',
        '.js-gender',
        '.js-age',
        '.js-fiv',
        '.js-felv',
        '.js-sterilized',
        '.js-location',
        '.js-view-btn',
        '.js-edit-btn',
        '.js-qr-btn',
      ],
      'animals.tmpl-animal-card'
    );

    // Fallback display name
    const displayName =
      animal.name && animal.name.trim() !== ''
        ? animal.name
        : translate('fallbacks.no_name', { defaultValue: '名前なし' });

    // Photo
    let photoUrl = DEFAULT_IMAGE_PLACEHOLDER;
    if (animal.photo && animal.photo.trim() !== '') {
      photoUrl = animal.photo.startsWith('/') ? animal.photo : `/media/${animal.photo}`;
    }
    const photoEl = requireSelector(card, '.js-photo', 'animals.tmpl-animal-card');
    photoEl.src = photoUrl;
    photoEl.alt = displayName;
    photoEl.onerror = () => {
      photoEl.onerror = null;
      photoEl.src = DEFAULT_IMAGE_PLACEHOLDER;
    };

    // Basic Info
    requireSelector(card, '.js-name', 'animals.tmpl-animal-card').textContent = displayName;
    requireSelector(card, '.js-id', 'animals.tmpl-animal-card').textContent = `#${animal.id}`;

    // Inactive State Styles
    const isInactive = animal.status === 'ADOPTED' || animal.status === 'DECEASED';
    if (isInactive) {
      card.classList.add('opacity-50', 'bg-gray-50');
    }

    // Status Badge
    const statusBadgeEl = requireSelector(card, '.js-status-badge', 'animals.tmpl-animal-card');
    statusBadgeEl.innerHTML = getStatusBadge(animal.status);

    // Ready for Adoption Badge
    const isReadyForAdoption = animal.status === 'IN_CARE' || animal.status === 'TRIAL';
    const readyBadgeEl = requireSelector(card, '.js-ready-badge', 'animals.tmpl-animal-card');
    if (readyBadgeEl && isReadyForAdoption) {
      readyBadgeEl.classList.remove('hidden');
    }

    // Details Grid
    requireSelector(card, '.js-gender', 'animals.tmpl-animal-card').textContent = translateDBValue(
      'gender',
      animal.gender
    );
    requireSelector(card, '.js-age', 'animals.tmpl-animal-card').textContent = formatAgeMonths(
      animal.age_months,
      animal.age_is_estimated
    );
    requireSelector(card, '.js-fiv', 'animals.tmpl-animal-card').innerHTML = formatTestResult(
      animal.fiv_positive,
      'FIV'
    );
    requireSelector(card, '.js-felv', 'animals.tmpl-animal-card').innerHTML = formatTestResult(
      animal.felv_positive,
      'FeLV'
    );
    requireSelector(card, '.js-sterilized', 'animals.tmpl-animal-card').textContent =
      formatSterilized(animal.is_sterilized);
    requireSelector(card, '.js-location', 'animals.tmpl-animal-card').textContent = formatLocation(
      animal.location_type,
      animal.current_location_note
    );

    // Actions
    const viewBtn = requireSelector(card, '.js-view-btn', 'animals.tmpl-animal-card');
    if (viewBtn) viewBtn.href = `${adminBasePath}/animals/${animal.id}`;

    const editBtn = requireSelector(card, '.js-edit-btn', 'animals.tmpl-animal-card');
    if (editBtn) editBtn.href = `${adminBasePath}/animals/${animal.id}/edit`;

    const qrBtn = requireSelector(card, '.js-qr-btn', 'animals.tmpl-animal-card');
    if (qrBtn) {
      qrBtn.addEventListener('click', () => showQRCode(animal.id));
    }

    container.appendChild(card);
  });

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
  container.innerHTML = '';

  if (totalPages <= 1) {
    return;
  }

  // Wrapper for logic structure (keeping it simple for now, can be template-ized more if needed)
  const wrapper = document.createElement('div');
  wrapper.className = 'flex items-center justify-between';

  // Summary Text
  const summaryDiv = document.createElement('div');
  summaryDiv.className = 'text-sm text-gray-600';
  summaryDiv.textContent = translate('pagination.summary', {
    defaultValue: `全 ${total} 件中 ${(page - 1) * pageSize + 1} - ${Math.min(page * pageSize, total)} 件を表示`,
    total,
    from: (page - 1) * pageSize + 1,
    to: Math.min(page * pageSize, total),
  });
  wrapper.appendChild(summaryDiv);

  // Buttons Container
  const buttonsDiv = document.createElement('div');
  buttonsDiv.className = 'flex gap-2';

  const maxVisible = 5;
  let startPage = Math.max(1, page - Math.floor(maxVisible / 2));
  let endPage = Math.min(totalPages, startPage + maxVisible - 1);

  if (endPage - startPage < maxVisible - 1) {
    startPage = Math.max(1, endPage - maxVisible + 1);
  }

  // Helper to create Nav Button (Prev/Next) - keeping as createElement for simplicity as usually distinctive
  const createNavBtn = (text, targetPage, disabled) => {
    const btn = document.createElement('button');
    btn.className =
      'px-3 py-2 text-sm border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed';
    btn.textContent = text;
    btn.disabled = disabled;
    if (!disabled) {
      btn.addEventListener('click', () => changePage(targetPage));
    }
    return btn;
  };

  // Prev Button
  buttonsDiv.appendChild(
    createNavBtn(
      translate('pagination.previous', { ns: COMMON_NAMESPACE, defaultValue: '前へ' }),
      page - 1,
      page === 1
    )
  );

  // Number Buttons (Using Template)
  for (let i = startPage; i <= endPage; i++) {
    const btn = cloneTemplate('tmpl-pagination-item');
    btn.textContent = i;

    if (i === page) {
      btn.classList.add('bg-brand-primary', 'text-white', 'border-brand-primary');
      // Inline styles for theme compatibility if CSS classes miss
      btn.style.backgroundColor = 'var(--color-brand-primary)';
      btn.style.borderColor = 'var(--color-brand-primary)';
      btn.style.color = '#ffffff';
    } else {
      btn.classList.add('border-border', 'hover:bg-bg-base');
      btn.style.borderColor = 'var(--color-border)';
      btn.addEventListener('click', () => changePage(i));
    }
    buttonsDiv.appendChild(btn);
  }

  // Next Button
  buttonsDiv.appendChild(
    createNavBtn(
      translate('pagination.next', { ns: COMMON_NAMESPACE, defaultValue: '次へ' }),
      page + 1,
      page === totalPages
    )
  );

  wrapper.appendChild(buttonsDiv);
  container.appendChild(wrapper);
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

  const isKiroween = document.body.classList.contains('kiroween-mode');

  // モーダルスタイル
  const modalContentClass = isKiroween
    ? 'p-6 max-w-md w-full mx-4'
    : 'bg-white rounded-lg p-6 max-w-md w-full mx-4';

  const modalContentStyle = isKiroween
    ? 'background-color: #000000 !important; border: 2px solid #33ff00 !important; color: #33ff00 !important;'
    : '';

  const closeButtonClass = isKiroween
    ? 'text-[#33ff00] hover:text-black hover:bg-[#33ff00] border border-[#33ff00] px-3 py-1 transition-colors duration-200 font-bold'
    : 'text-gray-500 hover:text-gray-700';

  const closeButtonText = isKiroween ? '[ CLOSE ]' : '✕';

  const linkClass = isKiroween
    ? 'text-[#33ff00] hover:text-[#66ff33] underline flex flex-nowrap items-center justify-center gap-2 whitespace-nowrap'
    : 'text-brand-primary hover:opacity-80 underline flex items-center justify-center gap-1 whitespace-nowrap';

  const descriptionClass = isKiroween
    ? 'mt-4 text-sm text-[#1a8000] text-center'
    : 'mt-4 text-sm text-gray-600 text-center';

  // モーダルを作成
  const modal = document.createElement('div');
  modal.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';

  if (isKiroween) {
    modal.style.zIndex = '10000';
  }

  modal.innerHTML = `
    <div class="${modalContentClass}" style="${modalContentStyle}">
      <div class="flex justify-between items-center mb-4">
        <h3 class="text-lg font-semibold">${modalTitle}</h3>
        <button onclick="this.closest('.fixed').remove()"
                class="${closeButtonClass}">
          ${closeButtonText}
        </button>
      </div>
      <div class="flex justify-center bg-white p-2 rounded">
        <img src="${qrUrl}" alt="QRコード" class="w-64 h-64">
      </div>
      <div class="mt-4 text-center">
        <a href="${publicUrl}" target="_blank" class="${linkClass}" ${!isKiroween ? 'style="color: var(--color-brand-primary);"' : ''}>
          ${linkText}
          <svg class="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path>
          </svg>
        </a>
      </div>
      <p class="${descriptionClass}">
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

// URLパラメータからフィルターを初期化
function initFiltersFromURL() {
  const urlParams = new URLSearchParams(window.location.search);

  // ステータスフィルター
  if (urlParams.has('status')) {
    currentStatus = urlParams.get('status');
    const statusFilter = document.getElementById('status-filter');
    if (statusFilter) {
      statusFilter.value = currentStatus;
    }
  }

  // FIV陽性フィルター（ダッシュボードからのリンク用）
  if (urlParams.get('fiv_positive') === 'true') {
    advancedFilters.fiv = 'positive';

    // 詳細検索フォームを表示
    const advancedSearchForm = document.getElementById('advanced-search-form');
    const advancedSearchIcon = document.getElementById('advanced-search-icon');
    if (advancedSearchForm) {
      advancedSearchForm.classList.remove('hidden');
    }
    if (advancedSearchIcon) {
      advancedSearchIcon.classList.add('rotate-180');
    }

    // FIVフィルターの値を設定
    const fivFilter = document.getElementById('fiv-filter');
    if (fivFilter) {
      fivFilter.value = 'positive';
    }
  }

  // FeLV陽性フィルター（ダッシュボードからのリンク用）
  if (urlParams.get('felv_positive') === 'true') {
    advancedFilters.felv = 'positive';

    // 詳細検索フォームを表示
    const advancedSearchForm = document.getElementById('advanced-search-form');
    const advancedSearchIcon = document.getElementById('advanced-search-icon');
    if (advancedSearchForm) {
      advancedSearchForm.classList.remove('hidden');
    }
    if (advancedSearchIcon) {
      advancedSearchIcon.classList.add('rotate-180');
    }

    // FeLVフィルターの値を設定
    const felvFilter = document.getElementById('felv-filter');
    if (felvFilter) {
      felvFilter.value = 'positive';
    }
  }

  // 検索キーワード
  if (urlParams.has('q')) {
    currentSearch = urlParams.get('q');
    const searchInput = document.getElementById('search');
    if (searchInput) {
      searchInput.value = currentSearch;
    }
  }
}

// イベントリスナー
document.addEventListener('DOMContentLoaded', () => {
  // URLパラメータからフィルターを初期化
  initFiltersFromURL();

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

  // 詳細検索トグル
  const toggleAdvancedSearch = document.getElementById('toggle-advanced-search');
  const advancedSearchForm = document.getElementById('advanced-search-form');
  const advancedSearchIcon = document.getElementById('advanced-search-icon');

  if (toggleAdvancedSearch && advancedSearchForm) {
    toggleAdvancedSearch.addEventListener('click', () => {
      advancedSearchForm.classList.toggle('hidden');
      if (advancedSearchIcon) {
        advancedSearchIcon.classList.toggle('rotate-180');
      }
    });
  }

  // 詳細検索フィルター - 譲渡可
  const readyForAdoptionFilter = document.getElementById('ready-for-adoption-filter');
  if (readyForAdoptionFilter) {
    readyForAdoptionFilter.addEventListener('change', e => {
      advancedFilters.isReadyForAdoption = e.target.value;
      currentPage = 1;
      loadAnimals();
    });
  }

  // 詳細検索フィルター - 性別
  const genderFilter = document.getElementById('gender-filter');
  if (genderFilter) {
    genderFilter.addEventListener('change', e => {
      advancedFilters.gender = e.target.value;
      currentPage = 1;
      loadAnimals();
    });
  }

  // 詳細検索フィルター - FIV
  const fivFilter = document.getElementById('fiv-filter');
  if (fivFilter) {
    fivFilter.addEventListener('change', e => {
      advancedFilters.fiv = e.target.value;
      currentPage = 1;
      loadAnimals();
    });
  }

  // 詳細検索フィルター - FeLV
  const felvFilter = document.getElementById('felv-filter');
  if (felvFilter) {
    felvFilter.addEventListener('change', e => {
      advancedFilters.felv = e.target.value;
      currentPage = 1;
      loadAnimals();
    });
  }

  // 詳細検索フィルター - 避妊・去勢
  const sterilizedFilter = document.getElementById('sterilized-filter');
  if (sterilizedFilter) {
    sterilizedFilter.addEventListener('change', e => {
      advancedFilters.isSterilized = e.target.value;
      currentPage = 1;
      loadAnimals();
    });
  }

  // 詳細検索フィルター - 場所
  const locationTypeFilter = document.getElementById('location-type-filter');
  if (locationTypeFilter) {
    locationTypeFilter.addEventListener('change', e => {
      advancedFilters.locationType = e.target.value;
      currentPage = 1;
      loadAnimals();
    });
  }

  // 詳細検索クリア
  const clearAdvancedSearch = document.getElementById('clear-advanced-search');
  if (clearAdvancedSearch) {
    clearAdvancedSearch.addEventListener('click', () => {
      // フィルタ値をリセット
      advancedFilters = {
        gender: '',
        fiv: '',
        felv: '',
        isSterilized: '',
        locationType: '',
        isReadyForAdoption: '',
      };

      // UI要素をリセット
      if (readyForAdoptionFilter) readyForAdoptionFilter.value = '';
      if (genderFilter) genderFilter.value = '';
      if (fivFilter) fivFilter.value = '';
      if (felvFilter) felvFilter.value = '';
      if (sterilizedFilter) sterilizedFilter.value = '';
      if (locationTypeFilter) locationTypeFilter.value = '';

      // ステータスフィルターもACTIVE（デフォルト）に戻す
      const statusFilter = document.getElementById('status-filter');
      if (statusFilter) statusFilter.value = 'ACTIVE';
      currentStatus = 'ACTIVE';

      currentPage = 1;
      loadAnimals();
    });
  }
});

window.addEventListener('languageChanged', () => {
  if (!hasLoadedAnimals) {
    return;
  }
  renderAnimalsList(lastAnimals);
  renderPagination(lastPagination.total, lastPagination.page, lastPagination.pageSize);
});

// ステータスバッジを取得
function getStatusBadge(status) {
  // ステータスラベルを取得
  const statusLabel = translate(`status.${status}`, {
    defaultValue: status,
  });

  // ステータスに応じたバッジスタイルを選択
  let badgeClass = 'px-3 py-1 rounded-full text-sm font-medium';
  const statusColorMap = {
    QUARANTINE: 'bg-red-100 text-red-800', // 保護中 - 赤
    IN_CARE: 'bg-orange-100 text-orange-800', // 治療中 - オレンジ
    TRIAL: 'bg-blue-100 text-blue-800', // 譲渡可能 - 青
    ADOPTED: 'bg-green-100 text-green-800', // 譲渡済み - 緑
    DECEASED: 'bg-gray-100 text-gray-800', // 死亡 - グレー
  };

  badgeClass += ' ' + (statusColorMap[status] || 'bg-gray-100 text-gray-800');

  return `<span class="${badgeClass}">${statusLabel}</span>`;
}

// グローバルエクスポート
window.changePage = changePage;
window.showQRCode = showQRCode;
window.getStatusBadge = getStatusBadge;

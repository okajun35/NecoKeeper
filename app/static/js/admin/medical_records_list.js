/**
 * 診療記録一覧ページのJavaScript
 */

// グローバル変数
let currentPage = 1;
const pageSize = 20;
let filters = {
  animal_id: null,
  vet_id: null,
  start_date: null,
  end_date: null,
};
// Force English role labels when Kiroween terminal theme is active.
const isKiroweenMode = document.body && document.body.classList.contains('kiroween-mode');
const fallbackText = (english, japanese) => (isKiroweenMode ? english : japanese);
const roleLabelFallbacks = {
  管理者: 'Administrator',
  獣医師: 'Veterinarian',
  スタッフ: 'Staff',
  閲覧専用: 'Read Only',
  admin: 'Administrator',
  staff: 'Staff',
  vet: 'Veterinarian',
  'read-only': 'Read Only',
  read_only: 'Read Only',
};

const getRoleLabel = role => {
  if (!role) {
    return '';
  }

  if (!isKiroweenMode) {
    return role;
  }

  if (roleLabelFallbacks[role]) {
    return roleLabelFallbacks[role];
  }

  const normalized = typeof role === 'string' ? role.toLowerCase().replace(/\s+/g, '_') : role;
  return roleLabelFallbacks[normalized] || role;
};

const formatVetDisplayName = name => {
  if (!name) {
    return '';
  }

  if (!isKiroweenMode) {
    return name;
  }

  return roleLabelFallbacks[name] || name;
};

// ページ読み込み時の初期化
document.addEventListener('DOMContentLoaded', () => {
  // i18nが初期化されるまで待機
  const waitForI18n = setInterval(() => {
    if (window.i18n && window.i18n.getCurrentLanguage) {
      clearInterval(waitForI18n);

      // i18nが初期化されたら翻訳を適用
      translateButtonTexts();
      loadAnimals();
      loadVets();
      loadMedicalRecords();
      setupEventListeners();

      // 言語変更イベントをリッスン
      window.addEventListener('languageChanged', () => {
        translateButtonTexts();
        // ページネーション情報の再表示（データは保持）
        const info = document.getElementById('paginationInfo');
        if (info && info.textContent) {
          // 既存のページネーション情報を保持
          const itemsText =
            window.i18n && window.i18n.t ? window.i18n.t('items', { ns: 'common' }) : '件';
          // テキストの最後の「件」を新しい翻訳に置き換え
          const text = info.innerHTML.replace(/件$/, itemsText);
          info.innerHTML = text;
        }
      });
    }
  }, 100);

  // タイムアウト（5秒）
  setTimeout(() => {
    clearInterval(waitForI18n);
    if (!window.i18n || !window.i18n.getCurrentLanguage) {
      console.warn('[medical_records_list] i18n initialization timeout');
      loadAnimals();
      loadVets();
      loadMedicalRecords();
      setupEventListeners();
    }
  }, 5000);
});

// ボタンのテキストを翻訳
function translateButtonTexts() {
  if (!window.i18n || !window.i18n.t) {
    console.warn('[medical_records_list] i18n not available');
    return;
  }

  const searchBtn = document.getElementById('searchBtn');
  const clearBtn = document.getElementById('clearBtn');
  const prevBtn = document.getElementById('prevPageBtn');
  const nextBtn = document.getElementById('nextPageBtn');

  if (searchBtn) {
    searchBtn.textContent = window.i18n.t('search', { ns: 'common' });
  }
  if (clearBtn) {
    clearBtn.textContent = window.i18n.t('clear', { ns: 'common' });
  }
  if (prevBtn) {
    prevBtn.textContent = window.i18n.t('pagination.previous', { ns: 'common' });
  }
  if (nextBtn) {
    nextBtn.textContent = window.i18n.t('pagination.next', { ns: 'common' });
  }

  updateSelectDefaults();
}

function updateSelectDefaults() {
  const allLabel =
    window.i18n && window.i18n.t ? window.i18n.t('common.all', { ns: 'common' }) : 'すべて';
  setDefaultOptionText('filterAnimal', 'All Cats', allLabel);
  setDefaultOptionText('filterVet', 'All Vets', allLabel);
}

function setDefaultOptionText(selectId, kiroweenLabel, defaultLabel) {
  const select = document.getElementById(selectId);
  if (!select) return;
  const option = select.querySelector('option[value=""]');
  if (!option) return;
  if (!option.dataset.originalI18nKey && option.getAttribute('data-i18n')) {
    option.dataset.originalI18nKey = option.getAttribute('data-i18n');
  }
  if (!option.dataset.originalI18nNs && option.getAttribute('data-i18n-ns')) {
    option.dataset.originalI18nNs = option.getAttribute('data-i18n-ns');
  }

  if (isKiroweenMode) {
    option.textContent = kiroweenLabel;
    if (option.dataset.originalI18nKey) {
      option.removeAttribute('data-i18n');
    }
    if (option.dataset.originalI18nNs) {
      option.removeAttribute('data-i18n-ns');
    }
  } else {
    option.textContent = defaultLabel;
    if (option.dataset.originalI18nKey) {
      option.setAttribute('data-i18n', option.dataset.originalI18nKey);
    }
    if (option.dataset.originalI18nNs) {
      option.setAttribute('data-i18n-ns', option.dataset.originalI18nNs);
    }
  }
}

// イベントリスナーの設定
function setupEventListeners() {
  document.getElementById('searchBtn').addEventListener('click', handleSearch);
  document.getElementById('clearBtn').addEventListener('click', handleClear);
  document
    .getElementById('prevPageBtn')
    .addEventListener('click', () => changePage(currentPage - 1));
  document
    .getElementById('nextPageBtn')
    .addEventListener('click', () => changePage(currentPage + 1));
}

// 猫一覧を読み込み（全ステータス含む）
async function loadAnimals() {
  try {
    const response = await fetch('/api/v1/animals?page=1&page_size=100', {
      headers: {
        Authorization: `Bearer ${getToken()}`,
      },
    });

    if (!response.ok) {
      const errorMsg =
        window.i18n && window.i18n.t
          ? window.i18n.t('load_error', { ns: 'medical_records' })
          : '猫一覧の取得に失敗しました';
      throw new Error(errorMsg);
    }

    const data = await response.json();
    const select = document.getElementById('filterAnimal');

    // 全ステータスの猫を表示（譲渡済み含む）
    data.items.forEach(animal => {
      const option = document.createElement('option');
      option.value = animal.id;
      option.textContent = `${animal.name} (${animal.status})`;
      select.appendChild(option);
    });
  } catch (error) {
    console.error('Error loading animals:', error);
  }
}

// 獣医師一覧を読み込み
async function loadVets() {
  try {
    // 全ユーザーを取得（獣医師ロールが設定されていない可能性があるため）
    const response = await fetch('/api/v1/users?page=1&page_size=100', {
      headers: {
        Authorization: `Bearer ${getToken()}`,
      },
    });

    if (!response.ok) throw new Error('ユーザー一覧の取得に失敗しました');

    const data = await response.json();
    const select = document.getElementById('filterVet');

    // ユーザーをドロップダウンに追加
    data.items.forEach(user => {
      const option = document.createElement('option');
      option.value = user.id;
      const roleLabel = getRoleLabel(user.role) || user.role || '';
      option.textContent = `${user.name} (${roleLabel})`;
      select.appendChild(option);
    });

    // フィルターを有効化
    select.disabled = false;
    select.title = '';
  } catch (error) {
    console.error('Error loading vets:', error);
    // エラーが発生してもフィルターは有効化
    const select = document.getElementById('filterVet');
    select.disabled = false;
    select.title = '';
  }
}

// 診療記録一覧を読み込み
async function loadMedicalRecords() {
  showLoading();
  hideError();

  try {
    const params = new URLSearchParams({
      page: currentPage,
      page_size: pageSize,
    });

    if (filters.animal_id) params.append('animal_id', filters.animal_id);
    if (filters.vet_id) params.append('vet_id', filters.vet_id);
    if (filters.start_date) params.append('start_date', filters.start_date);
    if (filters.end_date) params.append('end_date', filters.end_date);

    const response = await fetch(`/api/v1/medical-records?${params}`, {
      headers: {
        Authorization: `Bearer ${getToken()}`,
      },
    });

    if (!response.ok) {
      throw new Error('load_error');
    }

    const data = await response.json();
    renderMedicalRecords(data);
    updatePagination(data);
  } catch (error) {
    console.error('Error loading medical records:', error);
    showError(error.message);
  } finally {
    hideLoading();
  }
}

// 診療記録を表示
function renderMedicalRecords(data) {
  const mobileList = document.getElementById('mobileList');
  const desktopTableBody = document.getElementById('desktopTableBody');

  mobileList.innerHTML = '';
  desktopTableBody.innerHTML = '';

  if (data.items.length === 0) {
    const noDataText =
      window.i18n && window.i18n.t
        ? window.i18n.t('no_data', { ns: 'common' })
        : 'データがありません';
    const emptyMessage = `<div class="p-8 text-center text-gray-500">${noDataText}</div>`;
    mobileList.innerHTML = emptyMessage;
    desktopTableBody.innerHTML = `<tr><td colspan="9" class="px-6 py-8 text-center text-gray-500">${noDataText}</td></tr>`;
    return;
  }

  data.items.forEach(record => {
    // モバイル表示
    mobileList.appendChild(createMobileCard(record));

    // デスクトップ表示
    desktopTableBody.appendChild(createDesktopRow(record));
  });
}

// モバイルカードを作成
function createMobileCard(record) {
  const card = document.createElement('div');
  card.className = 'p-4 hover:bg-gray-50';

  // 翻訳テキストを取得
  const weightLabel =
    window.i18n && window.i18n.t ? window.i18n.t('weight', { ns: 'medical_records' }) : '体重';
  const tempLabel =
    window.i18n && window.i18n.t ? window.i18n.t('temperature', { ns: 'medical_records' }) : '体温';
  const viewText =
    window.i18n && window.i18n.t ? window.i18n.t('view', { ns: 'medical_records' }) : '詳細';
  const medicalActionLabel = fallbackText('Medical Action', '診療行為');
  const billingLabel = fallbackText('Billing Amount', '請求価格');
  const vetDisplayName =
    formatVetDisplayName(record.vet_name) || (record.vet_id ? `ID: ${record.vet_id}` : '-');

  // 診療行為と投薬情報
  let medicalActionInfo = '';
  if (record.medical_action_name) {
    medicalActionInfo = `<div class="text-sm text-gray-600 mb-2">
      <span class="text-gray-500">${medicalActionLabel}:</span> ${record.medical_action_name}
      ${record.dosage ? ` (${record.dosage}${record.dosage_unit || ''})` : ''}
    </div>`;
  }

  // 請求価格情報
  let billingInfo = '';
  if (record.billing_amount) {
    billingInfo = `<div class="text-sm text-gray-600 mb-2">
      <span class="text-gray-500">${billingLabel}:</span> <span class="font-medium">¥${Number(record.billing_amount).toLocaleString()}</span>
    </div>`;
  }

  card.innerHTML = `
        <div class="flex justify-between items-start mb-2">
            <div>
                <p class="font-medium text-gray-900">${record.date}</p>
                <p class="text-sm text-gray-600">${record.animal_name || 'ID: ' + record.animal_id}</p>
            </div>
          <span class="px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded">${vetDisplayName}</span>
        </div>
        <div class="grid grid-cols-2 gap-2 text-sm mb-3">
            <div><span class="text-gray-500">${weightLabel}:</span> ${record.weight ? record.weight + 'kg' : '-'}</div>
            <div><span class="text-gray-500">${tempLabel}:</span> ${record.temperature ? record.temperature + '℃' : '-'}</div>
        </div>
        ${medicalActionInfo}
        ${billingInfo}
        <p class="text-sm text-gray-600 mb-3">${record.symptoms}</p>
        <div class="flex gap-2">
            <a href="/admin/medical-records/${record.id}" class="flex-1 px-3 py-2 text-sm text-center bg-indigo-600 text-white rounded hover:bg-indigo-700">
                ${viewText}
            </a>
        </div>
    `;
  return card;
}

// デスクトップ行を作成
function createDesktopRow(record) {
  const row = document.createElement('tr');
  row.className = 'hover:bg-gray-50';

  // 翻訳テキストを取得
  const viewText =
    window.i18n && window.i18n.t ? window.i18n.t('view', { ns: 'medical_records' }) : '詳細';
  const vetDisplayName =
    formatVetDisplayName(record.vet_name) || (record.vet_id ? `ID: ${record.vet_id}` : '-');

  // 診療行為と投薬情報
  let medicalActionText = '-';
  if (record.medical_action_name) {
    medicalActionText = record.medical_action_name;
    if (record.dosage) {
      medicalActionText += ` (${record.dosage}${record.dosage_unit || ''})`;
    }
  }

  // 請求価格
  const billingText = record.billing_amount
    ? `¥${Number(record.billing_amount).toLocaleString()}`
    : '-';

  row.innerHTML = `
        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${record.date}</td>
        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${record.animal_name || 'ID: ' + record.animal_id}</td>
        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${vetDisplayName}</td>
        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${record.weight ? record.weight + 'kg' : '-'}</td>
        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${record.temperature ? record.temperature + '℃' : '-'}</td>
        <td class="px-6 py-4 text-sm text-gray-600 max-w-xs truncate">${record.symptoms}</td>
        <td class="px-6 py-4 text-sm text-gray-600 max-w-xs truncate">${medicalActionText}</td>
        <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium text-gray-900">${billingText}</td>
        <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
            <a href="/admin/medical-records/${record.id}" class="text-indigo-600 hover:text-indigo-900">${viewText}</a>
        </td>
    `;
  return row;
}

// ページネーション更新
function updatePagination(data) {
  const info = document.getElementById('paginationInfo');
  const prevBtn = document.getElementById('prevPageBtn');
  const nextBtn = document.getElementById('nextPageBtn');

  const start = (data.page - 1) * data.page_size + 1;
  const end = Math.min(data.page * data.page_size, data.total);
  const itemsText = window.i18n && window.i18n.t ? window.i18n.t('items', { ns: 'common' }) : '件';

  info.innerHTML = `<span class="font-medium">${start}</span> - <span class="font-medium">${end}</span> / <span class="font-medium">${data.total}</span> ${itemsText}`;

  prevBtn.disabled = data.page <= 1;
  nextBtn.disabled = data.page >= data.total_pages;

  // ボタンのテキストを翻訳
  if (window.i18n && window.i18n.t) {
    prevBtn.textContent = window.i18n.t('pagination.previous', { ns: 'common' });
    nextBtn.textContent = window.i18n.t('pagination.next', { ns: 'common' });
  }
}

// 検索処理
function handleSearch() {
  filters.animal_id = document.getElementById('filterAnimal').value || null;
  filters.vet_id = document.getElementById('filterVet').value || null;
  filters.start_date = document.getElementById('filterStartDate').value || null;
  filters.end_date = document.getElementById('filterEndDate').value || null;

  currentPage = 1;
  loadMedicalRecords();
}

// クリア処理
function handleClear() {
  document.getElementById('filterAnimal').value = '';
  document.getElementById('filterVet').value = '';
  document.getElementById('filterStartDate').value = '';
  document.getElementById('filterEndDate').value = '';

  filters = {
    animal_id: null,
    vet_id: null,
    start_date: null,
    end_date: null,
  };

  currentPage = 1;
  loadMedicalRecords();
}

// ページ変更
function changePage(page) {
  currentPage = page;
  loadMedicalRecords();
}

// ローディング表示
function showLoading() {
  document.getElementById('loadingIndicator').classList.remove('hidden');
  document.getElementById('medicalRecordsContainer').classList.add('hidden');
}

function hideLoading() {
  document.getElementById('loadingIndicator').classList.add('hidden');
  document.getElementById('medicalRecordsContainer').classList.remove('hidden');
}

// エラー表示
function showError(message) {
  const errorDiv = document.getElementById('errorMessage');
  let translatedMessage = message;

  if (window.i18n && window.i18n.t) {
    // メッセージが翻訳キーの場合は翻訳
    if (message === 'load_error') {
      translatedMessage = window.i18n.t('load_error', { ns: 'medical_records' });
    }
  }

  errorDiv.querySelector('p').textContent = translatedMessage;
  errorDiv.classList.remove('hidden');
}

function hideError() {
  document.getElementById('errorMessage').classList.add('hidden');
}

// 注: getToken等はcommon.jsで定義済み

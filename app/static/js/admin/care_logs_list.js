/**
 * 世話記録一覧（日次ビュー）
 *
 * 1日×1匹を1行で表示する形式で世話記録を管理します。
 */

const adminBasePath = window.ADMIN_BASE_PATH || window.__ADMIN_BASE_PATH__ || '/admin';

// グローバル変数
let currentPage = 1;
let currentFilters = {};
let currentAnimalStatus = 'DAILY'; // デフォルトは日常記録（保護中・在籍中）
let animals = [];
const isKiroweenMode = document.body && document.body.classList.contains('kiroween-mode');
const fallbackText = (english, japanese) => (isKiroweenMode ? english : japanese);

// 初期化
document.addEventListener('DOMContentLoaded', () => {
  initializeFilters();
  loadAnimals();
  loadDailyView();
  setupEventListeners();
  setupTabListeners();

  // 言語切り替えで「すべての猫」を現在の言語に再設定
  window.addEventListener('languageChanged', () => {
    updateAllCatsOption();
  });
});

/**
 * フィルタの初期化
 */
function initializeFilters() {
  // デフォルト日付範囲: 過去7日間
  const today = new Date();
  const sevenDaysAgo = new Date(today);
  sevenDaysAgo.setDate(today.getDate() - 6);

  document.getElementById('filterStartDate').valueAsDate = sevenDaysAgo;
  document.getElementById('filterEndDate').valueAsDate = today;
}

/**
 * イベントリスナーの設定
 */
function setupEventListeners() {
  // 検索ボタン
  document.getElementById('searchBtn').addEventListener('click', () => {
    currentPage = 1;
    applyFilters();
  });

  // クリアボタン
  document.getElementById('clearBtn').addEventListener('click', () => {
    clearFilters();
  });

  // CSVエクスポートボタン
  document.getElementById('exportCsvBtn').addEventListener('click', () => {
    exportCsv();
  });

  // ページネーション
  document.getElementById('prevPageBtn').addEventListener('click', () => {
    if (currentPage > 1) {
      currentPage--;
      loadDailyView();
    }
  });

  document.getElementById('nextPageBtn').addEventListener('click', () => {
    currentPage++;
    loadDailyView();
  });
}

/**
 * タブリスナーの設定
 */
function setupTabListeners() {
  const tabButtons = document.querySelectorAll('.tab-btn');
  tabButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      const newStatus = btn.dataset.status;
      if (newStatus !== currentAnimalStatus) {
        currentAnimalStatus = newStatus;
        currentPage = 1;
        updateTabStyles();
        loadDailyView();
        loadAnimals(); // タブ切り替え時に猫リストも更新
      }
    });
  });
}

/**
 * タブスタイルを更新
 */
function updateTabStyles() {
  const tabButtons = document.querySelectorAll('.tab-btn');
  tabButtons.forEach(btn => {
    const isActive = btn.dataset.status === currentAnimalStatus;
    if (isActive) {
      btn.classList.remove(
        'border-transparent',
        'text-gray-500',
        'hover:text-gray-700',
        'hover:border-gray-300'
      );
      btn.classList.add('border-brand-primary', 'text-brand-primary');
    } else {
      btn.classList.remove('border-brand-primary', 'text-brand-primary');
      btn.classList.add(
        'border-transparent',
        'text-gray-500',
        'hover:text-gray-700',
        'hover:border-gray-300'
      );
    }
  });
}

/**
 * 猫リストを取得
 */
async function loadAnimals() {
  try {
    // 現在のタブに応じたステータスフィルターを設定
    let statusParam = '';
    if (currentAnimalStatus === 'DAILY') {
      statusParam = 'DAILY'; // QUARANTINE + IN_CARE（トライアル中は除く）
    } else if (currentAnimalStatus === 'TRIAL') {
      statusParam = 'TRIAL';
    } else if (currentAnimalStatus === 'ARCHIVE') {
      statusParam = 'ARCHIVE'; // ADOPTED + DECEASED
    }

    const url = statusParam
      ? `/api/v1/animals?page=1&page_size=100&status=${statusParam}`
      : '/api/v1/animals?page=1&page_size=100';

    const response = await fetch(url, {
      headers: {
        Authorization: `Bearer ${getToken()}`,
      },
    });

    if (!response.ok) {
      throw new Error(fallbackText('Failed to load cat list.', '猫一覧の取得に失敗しました'));
    }

    const data = await response.json();
    animals = data.items;

    // ドロップダウンに追加
    const select = document.getElementById('filterAnimal');
    select.innerHTML = '';
    select.appendChild(createAllCatsOption());

    animals.forEach(animal => {
      const option = document.createElement('option');
      option.value = animal.id;
      option.textContent = animal.name || `猫 ${animal.id}`;
      select.appendChild(option);
    });
  } catch (error) {
    console.error('猫一覧の読み込みエラー:', error);
  }
}

function createAllCatsOption() {
  const option = document.createElement('option');
  option.value = '';
  option.setAttribute('data-i18n', 'filter.all_cats');
  option.setAttribute('data-i18n-ns', 'care_logs');
  option.textContent = getAllCatsLabel();
  return option;
}

function getAllCatsLabel() {
  const translated =
    (window.i18n && window.i18n.t
      ? window.i18n.t('filter.all_cats', {
          ns: 'care_logs',
          defaultValue: null,
        })
      : null) || null;

  return translated || fallbackText('All Cats', 'すべての猫');
}

function updateAllCatsOption() {
  const select = document.getElementById('filterAnimal');
  if (!select) return;
  const first = select.querySelector('option[value=""]');
  if (first) {
    first.textContent = getAllCatsLabel();
  }
}

/**
 * 日次ビューデータを取得
 */
async function loadDailyView() {
  showLoading();
  hideError();

  try {
    const params = new URLSearchParams({
      page: currentPage,
      page_size: 20,
      animal_status: currentAnimalStatus,
    });

    // フィルタ条件を追加
    if (currentFilters.animalId) {
      params.append('animal_id', currentFilters.animalId);
    }
    if (currentFilters.startDate) {
      params.append('start_date', currentFilters.startDate);
    }
    if (currentFilters.endDate) {
      params.append('end_date', currentFilters.endDate);
    }

    const response = await fetch(`/api/v1/care-logs/daily-view?${params}`, {
      headers: {
        Authorization: `Bearer ${getToken()}`,
      },
    });

    if (!response.ok) {
      throw new Error(fallbackText('Failed to load care logs.', '世話記録の取得に失敗しました'));
    }

    const data = await response.json();
    renderDailyView(data);
    updatePagination(data);
  } catch (error) {
    console.error('世話記録の読み込みエラー:', error);
    showError(fallbackText('Failed to load care logs.', '世話記録の取得に失敗しました'));
  } finally {
    hideLoading();
  }
}

/**
 * 日次ビューを描画
 */
function renderDailyView(data) {
  const tbody = document.getElementById('desktopTableBody');
  const mobileList = document.getElementById('mobileList');

  tbody.innerHTML = '';
  mobileList.innerHTML = '';

  if (data.items.length === 0) {
    const emptyMessage = fallbackText('No records found.', '記録がありません');
    tbody.innerHTML = `
      <tr>
        <td colspan="5" class="px-6 py-8 text-center text-gray-500">${emptyMessage}</td>
      </tr>`;
    mobileList.innerHTML = `<div class="p-8 text-center text-gray-500">${emptyMessage}</div>`;
    return;
  }

  data.items.forEach(item => {
    // デスクトップ: テーブル行
    const row = createDailyRow(item);
    tbody.appendChild(row);

    // モバイル: カード
    const card = createDailyCard(item);
    mobileList.appendChild(card);
  });
}

function translateDynamicElement(element) {
  if (!element) return;
  if (window.i18n && typeof window.i18n.translateElement === 'function') {
    window.i18n.translateElement(element);
    return;
  }
  if (window.applyDynamicTranslations) {
    window.applyDynamicTranslations(element);
  }
}

/**
 * テーブル行を作成
 */
function createDailyRow(item) {
  const row = cloneTemplate('tmpl-daily-row');
  assertRequiredSelectors(
    row,
    ['.js-date', '.js-name', '.js-morning', '.js-noon', '.js-evening'],
    'care_logs_list.tmpl-daily-row'
  );

  // 日付
  requireSelector(row, '.js-date', 'care_logs_list.tmpl-daily-row').textContent = item.date;

  // 猫名
  requireSelector(row, '.js-name', 'care_logs_list.tmpl-daily-row').textContent = item.animal_name;

  // 朝・昼・夕
  const timeSlots = {
    morning: '.js-morning',
    noon: '.js-noon',
    evening: '.js-evening',
  };

  Object.entries(timeSlots).forEach(([slot, selector]) => {
    const cell = requireSelector(row, selector, 'care_logs_list.tmpl-daily-row');
    const link = createRecordLink(item, slot);
    cell.appendChild(link);
  });

  translateDynamicElement(row);
  return row;
}

/**
 * モバイルカードを作成
 */
function createDailyCard(item) {
  const card = cloneTemplate('tmpl-daily-card-mobile');
  assertRequiredSelectors(
    card,
    ['.js-name', '.js-date', '.js-morning', '.js-noon', '.js-evening'],
    'care_logs_list.tmpl-daily-card-mobile'
  );

  requireSelector(card, '.js-name', 'care_logs_list.tmpl-daily-card-mobile').textContent =
    item.animal_name;
  requireSelector(card, '.js-date', 'care_logs_list.tmpl-daily-card-mobile').textContent =
    item.date;

  const timeSlots = {
    morning: '.js-morning',
    noon: '.js-noon',
    evening: '.js-evening',
  };

  // リンクを追加
  Object.entries(timeSlots).forEach(([slot, selector]) => {
    const container = requireSelector(card, selector, 'care_logs_list.tmpl-daily-card-mobile');
    const link = createRecordLink(item, slot);
    container.appendChild(link);
  });

  translateDynamicElement(card);
  return card;
}

/**
 * 記録リンクを作成
 */
function createRecordLink(item, timeSlot) {
  const record = item[timeSlot];
  const link = cloneTemplate('tmpl-record-link');

  if (record.exists) {
    // 記録あり: ○ → 詳細/編集画面
    link.textContent = record.has_image ? '○📷' : '○';
    link.href = `${adminBasePath}/care-logs/${record.log_id}`;
    link.classList.add('text-green-600');
    const appetiteLabel = fallbackText('Appetite', '食欲');
    const energyLabel = fallbackText('Energy', '元気');
    const photoSuffix = record.has_image ? fallbackText(', Photo attached', '、写真あり') : '';
    link.title = `${appetiteLabel}: ${formatAppetiteLabel(record.appetite)}, ${energyLabel}: ${record.energy}${photoSuffix}`;
  } else {
    // 記録なし: × → 新規登録画面
    link.textContent = '×';
    link.href = `${adminBasePath}/care-logs/new?animal_id=${item.animal_id}&date=${item.date}&time_slot=${timeSlot}`;
    link.classList.add('text-red-600');
    link.title = fallbackText('Add record', '記録を追加');
  }

  return link;
}

/**
 * ページネーション情報を更新
 */
function updatePagination(data) {
  const { total, page, page_size, total_pages } = data;

  // 表示範囲
  const start = total === 0 ? 0 : (page - 1) * page_size + 1;
  const end = Math.min(page * page_size, total);

  document.getElementById('paginationInfo').innerHTML = `
        <span class="font-medium">${start}</span> -
        <span class="font-medium">${end}</span> /
        <span class="font-medium">${total}</span> ${fallbackText('items', '件')}
    `;

  // ボタンの有効/無効
  document.getElementById('prevPageBtn').disabled = page <= 1;
  document.getElementById('nextPageBtn').disabled = page >= total_pages;
}

/**
 * フィルタを適用
 */
function applyFilters() {
  const animalId = document.getElementById('filterAnimal').value;
  const startDate = document.getElementById('filterStartDate').value;
  const endDate = document.getElementById('filterEndDate').value;

  currentFilters = {
    animalId: animalId || null,
    startDate: startDate || null,
    endDate: endDate || null,
  };

  loadDailyView();
}

/**
 * フィルタをクリア
 */
function clearFilters() {
  document.getElementById('filterAnimal').value = '';
  initializeFilters();
  currentFilters = {};
  currentPage = 1;
  loadDailyView();
}

/**
 * CSVエクスポート
 */
async function exportCsv() {
  try {
    const params = new URLSearchParams();

    // フィルタ条件を追加
    if (currentFilters.animalId) {
      params.append('animal_id', currentFilters.animalId);
    }
    if (currentFilters.startDate) {
      params.append('start_date', currentFilters.startDate);
    }
    if (currentFilters.endDate) {
      params.append('end_date', currentFilters.endDate);
    }

    const response = await fetch(`/api/v1/care-logs/export?${params}`, {
      headers: {
        Authorization: `Bearer ${getToken()}`,
      },
    });

    if (!response.ok) {
      throw new Error(fallbackText('Failed to export CSV.', 'CSVエクスポートに失敗しました'));
    }

    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `care_logs_${new Date().toISOString().split('T')[0]}.csv`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  } catch (error) {
    console.error('CSVエクスポートエラー:', error);
    showError(fallbackText('Failed to export CSV.', 'CSVエクスポートに失敗しました'));
  }
}

/**
 * ローディング表示
 */
function showLoading() {
  document.getElementById('loadingIndicator').classList.remove('hidden');
  document.getElementById('careLogsContainer').style.opacity = '0.5';
}

/**
 * ローディング非表示
 */
function hideLoading() {
  document.getElementById('loadingIndicator').classList.add('hidden');
  document.getElementById('careLogsContainer').style.opacity = '1';
}

/**
 * エラー表示
 */
function showError(message) {
  const errorDiv = document.getElementById('errorMessage');
  errorDiv.querySelector('p').textContent = message;
  errorDiv.classList.remove('hidden');
}

/**
 * エラー非表示
 */
function hideError() {
  document.getElementById('errorMessage').classList.add('hidden');
}

/**
 * 注: getToken等はcommon.jsで定義済み
 */

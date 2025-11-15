/**
 * 世話記録一覧の動的機能
 *
 * APIからデータを取得し、フィルター、ページネーション、CSVエクスポートを実装
 */

// 状態管理
const state = {
  currentPage: 1,
  pageSize: 20,
  totalPages: 0,
  totalItems: 0,
  filters: {
    animalId: '',
    startDate: '',
    endDate: '',
    timeSlot: '',
  },
  animals: [],
};

// 時点の日本語マッピング
const TIME_SLOT_MAP = {
  morning: '朝',
  noon: '昼',
  evening: '夕',
};

// 時点のバッジカラー
const TIME_SLOT_COLORS = {
  morning: 'bg-blue-100 text-blue-800',
  noon: 'bg-yellow-100 text-yellow-800',
  evening: 'bg-purple-100 text-purple-800',
};

/**
 * 初期化
 */
document.addEventListener('DOMContentLoaded', () => {
  initializeEventListeners();
  loadAnimals();
  loadCareLogs();
});

/**
 * イベントリスナーの初期化
 */
function initializeEventListeners() {
  // 検索ボタン
  document.getElementById('searchBtn').addEventListener('click', () => {
    state.currentPage = 1;
    loadCareLogs();
  });

  // クリアボタン
  document.getElementById('clearBtn').addEventListener('click', () => {
    clearFilters();
    state.currentPage = 1;
    loadCareLogs();
  });

  // CSVエクスポートボタン
  document.getElementById('exportCsvBtn').addEventListener('click', exportToCsv);

  // ページネーションボタン
  document.getElementById('prevPageBtn').addEventListener('click', () => {
    if (state.currentPage > 1) {
      state.currentPage--;
      loadCareLogs();
    }
  });

  document.getElementById('nextPageBtn').addEventListener('click', () => {
    if (state.currentPage < state.totalPages) {
      state.currentPage++;
      loadCareLogs();
    }
  });
}

/**
 * 猫一覧を読み込み
 */
async function loadAnimals() {
  try {
    const response = await fetch('/api/v1/animals?page=1&page_size=100');
    if (!response.ok) throw new Error('猫一覧の取得に失敗しました');

    const data = await response.json();
    state.animals = data.items;

    // セレクトボックスに追加
    const select = document.getElementById('filterAnimal');
    data.items.forEach(animal => {
      const option = document.createElement('option');
      option.value = animal.id;
      option.textContent = animal.name || `猫 ${animal.id}`;
      select.appendChild(option);
    });
  } catch (error) {
    console.error('猫一覧の読み込みエラー:', error);
  }
}

/**
 * 世話記録を読み込み
 */
async function loadCareLogs() {
  showLoading();
  hideError();

  try {
    // フィルターを取得
    state.filters.animalId = document.getElementById('filterAnimal').value;
    state.filters.startDate = document.getElementById('filterStartDate').value;
    state.filters.endDate = document.getElementById('filterEndDate').value;
    state.filters.timeSlot = document.getElementById('filterTimeSlot').value;

    // クエリパラメータを構築
    const params = new URLSearchParams({
      page: state.currentPage,
      page_size: state.pageSize,
    });

    if (state.filters.animalId) params.append('animal_id', state.filters.animalId);
    if (state.filters.startDate) params.append('start_date', state.filters.startDate);
    if (state.filters.endDate) params.append('end_date', state.filters.endDate);
    if (state.filters.timeSlot) params.append('time_slot', state.filters.timeSlot);

    // APIリクエスト
    const response = await fetch(`/api/v1/care-logs?${params}`);
    if (!response.ok) throw new Error('世話記録の取得に失敗しました');

    const data = await response.json();

    // 状態を更新
    state.totalPages = data.total_pages;
    state.totalItems = data.total;

    // データを表示
    renderCareLogs(data.items);
    updatePagination();

    hideLoading();
  } catch (error) {
    console.error('世話記録の読み込みエラー:', error);
    showError(error.message);
    hideLoading();
  }
}

/**
 * 世話記録を表示
 */
function renderCareLogs(careLogs) {
  renderMobileList(careLogs);
  renderDesktopTable(careLogs);
}

/**
 * モバイルリストを表示
 */
function renderMobileList(careLogs) {
  const container = document.getElementById('mobileList');
  container.innerHTML = '';

  if (careLogs.length === 0) {
    container.innerHTML = '<div class="p-4 text-center text-gray-500">記録がありません</div>';
    return;
  }

  careLogs.forEach(log => {
    const animalName = getAnimalName(log.animal_id);
    const timeSlotLabel = TIME_SLOT_MAP[log.time_slot] || log.time_slot;
    const timeSlotColor = TIME_SLOT_COLORS[log.time_slot] || 'bg-gray-100 text-gray-800';
    const createdAt = formatDateTime(log.created_at);

    const card = document.createElement('div');
    card.className = 'p-4 hover:bg-gray-50';
    card.innerHTML = `
            <div class="flex items-start justify-between mb-2">
                <div>
                    <h3 class="font-medium text-gray-900">${animalName}</h3>
                    <p class="text-sm text-gray-500">${createdAt}</p>
                </div>
                <span class="px-2 py-1 text-xs ${timeSlotColor} rounded">${timeSlotLabel}</span>
            </div>
            <div class="space-y-1 text-sm">
                <p class="text-gray-600">記録者: ${log.recorder_name}</p>
                <div class="flex gap-3">
                    <span class="text-gray-600">食欲: <span class="font-medium">${log.appetite}</span></span>
                    <span class="text-gray-600">元気: <span class="font-medium">${log.energy}</span></span>
                </div>
                <div class="flex gap-3">
                    <span class="text-gray-600">排尿: ${log.urination ? '○' : '×'}</span>
                    <span class="text-gray-600">清掃: ${log.cleaning ? '済' : '未'}</span>
                </div>
                ${log.memo ? `<p class="text-gray-600 mt-2">メモ: ${log.memo}</p>` : ''}
            </div>
        `;
    container.appendChild(card);
  });
}

/**
 * デスクトップテーブルを表示
 */
function renderDesktopTable(careLogs) {
  const tbody = document.getElementById('desktopTableBody');
  tbody.innerHTML = '';

  if (careLogs.length === 0) {
    tbody.innerHTML =
      '<tr><td colspan="9" class="px-6 py-4 text-center text-gray-500">記録がありません</td></tr>';
    return;
  }

  careLogs.forEach(log => {
    const animalName = getAnimalName(log.animal_id);
    const timeSlotLabel = TIME_SLOT_MAP[log.time_slot] || log.time_slot;
    const timeSlotColor = TIME_SLOT_COLORS[log.time_slot] || 'bg-gray-100 text-gray-800';
    const createdAt = formatDateTime(log.created_at);

    const row = document.createElement('tr');
    row.className = 'hover:bg-gray-50';
    row.innerHTML = `
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${createdAt}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">${animalName}</td>
            <td class="px-6 py-4 whitespace-nowrap">
                <span class="px-2 py-1 text-xs ${timeSlotColor} rounded">${timeSlotLabel}</span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600">${log.recorder_name}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${log.appetite}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${log.energy}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${log.urination ? '○' : '×'}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${log.cleaning ? '済' : '未'}</td>
            <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <button class="text-indigo-600 hover:text-indigo-900 mr-3" onclick="viewDetail(${log.id})">詳細</button>
            </td>
        `;
    tbody.appendChild(row);
  });
}

/**
 * ページネーションを更新
 */
function updatePagination() {
  const start = state.totalItems === 0 ? 0 : (state.currentPage - 1) * state.pageSize + 1;
  const end = Math.min(state.currentPage * state.pageSize, state.totalItems);

  document.getElementById('paginationInfo').innerHTML = `
        <span class="font-medium">${start}</span> -
        <span class="font-medium">${end}</span> /
        <span class="font-medium">${state.totalItems}</span> 件
    `;

  // ボタンの有効/無効を設定
  document.getElementById('prevPageBtn').disabled = state.currentPage === 1;
  document.getElementById('nextPageBtn').disabled = state.currentPage >= state.totalPages;
}

/**
 * CSVエクスポート
 */
async function exportToCsv() {
  try {
    // フィルターを適用したURLを構築
    const params = new URLSearchParams();
    if (state.filters.animalId) params.append('animal_id', state.filters.animalId);
    if (state.filters.startDate) params.append('start_date', state.filters.startDate);
    if (state.filters.endDate) params.append('end_date', state.filters.endDate);

    // CSVダウンロード
    const url = `/api/v1/care-logs/export?${params}`;
    window.location.href = url;
  } catch (error) {
    console.error('CSVエクスポートエラー:', error);
    showError('CSVエクスポートに失敗しました');
  }
}

/**
 * フィルターをクリア
 */
function clearFilters() {
  document.getElementById('filterAnimal').value = '';
  document.getElementById('filterStartDate').value = '';
  document.getElementById('filterEndDate').value = '';
  document.getElementById('filterTimeSlot').value = '';
}

/**
 * 猫名を取得
 */
function getAnimalName(animalId) {
  const animal = state.animals.find(a => a.id === animalId);
  return animal ? animal.name || `猫 ${animalId}` : `猫 ${animalId}`;
}

/**
 * 日時をフォーマット
 */
function formatDateTime(dateTimeStr) {
  const date = new Date(dateTimeStr);
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  const hours = String(date.getHours()).padStart(2, '0');
  const minutes = String(date.getMinutes()).padStart(2, '0');
  return `${year}-${month}-${day} ${hours}:${minutes}`;
}

/**
 * ローディング表示
 */
function showLoading() {
  document.getElementById('loadingIndicator').classList.remove('hidden');
  document.getElementById('careLogsContainer').classList.add('hidden');
}

/**
 * ローディング非表示
 */
function hideLoading() {
  document.getElementById('loadingIndicator').classList.add('hidden');
  document.getElementById('careLogsContainer').classList.remove('hidden');
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
 * 詳細表示（将来実装）
 */
function viewDetail(logId) {
  alert(`詳細表示機能は今後実装予定です（記録ID: ${logId}）`);
}

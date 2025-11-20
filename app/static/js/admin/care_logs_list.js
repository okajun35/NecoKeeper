/**
 * 世話記録一覧（日次ビュー）
 *
 * 1日×1匹を1行で表示する形式で世話記録を管理します。
 */

// グローバル変数
let currentPage = 1;
let currentFilters = {};
let animals = [];

// 初期化
document.addEventListener('DOMContentLoaded', () => {
  initializeFilters();
  loadAnimals();
  loadDailyView();
  setupEventListeners();
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
 * 猫リストを取得
 */
async function loadAnimals() {
  try {
    const response = await fetch('/api/v1/animals?page=1&page_size=100', {
      headers: {
        Authorization: `Bearer ${getToken()}`,
      },
    });

    if (!response.ok) {
      throw new Error('猫一覧の取得に失敗しました');
    }

    const data = await response.json();
    animals = data.items;

    // ドロップダウンに追加
    const select = document.getElementById('filterAnimal');
    select.innerHTML = '<option value="">すべての猫</option>';

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
      throw new Error('世話記録の取得に失敗しました');
    }

    const data = await response.json();
    renderDailyView(data);
    updatePagination(data);
  } catch (error) {
    console.error('世話記録の読み込みエラー:', error);
    showError('世話記録の取得に失敗しました');
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
    tbody.innerHTML =
      '<tr><td colspan="5" class="px-6 py-8 text-center text-gray-500">記録がありません</td></tr>';
    mobileList.innerHTML = '<div class="p-8 text-center text-gray-500">記録がありません</div>';
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

/**
 * テーブル行を作成
 */
function createDailyRow(item) {
  const row = document.createElement('tr');
  row.className = 'hover:bg-gray-50';

  // 日付
  const dateCell = document.createElement('td');
  dateCell.className = 'px-6 py-4 whitespace-nowrap text-sm text-gray-900';
  dateCell.textContent = item.date;
  row.appendChild(dateCell);

  // 猫名
  const nameCell = document.createElement('td');
  nameCell.className = 'px-6 py-4 whitespace-nowrap text-sm text-gray-900';
  nameCell.textContent = item.animal_name;
  row.appendChild(nameCell);

  // 朝・昼・夕
  ['morning', 'noon', 'evening'].forEach(timeSlot => {
    const cell = document.createElement('td');
    cell.className = 'px-6 py-4 whitespace-nowrap text-center';

    const link = createRecordLink(item, timeSlot);
    cell.appendChild(link);

    row.appendChild(cell);
  });

  return row;
}

/**
 * モバイルカードを作成
 */
function createDailyCard(item) {
  const card = document.createElement('div');
  card.className = 'p-4';

  card.innerHTML = `
        <div class="flex justify-between items-start mb-3">
            <div>
                <div class="text-sm font-medium text-gray-900">${item.animal_name}</div>
                <div class="text-xs text-gray-500">${item.date}</div>
            </div>
        </div>
        <div class="grid grid-cols-3 gap-4">
            <div class="text-center">
                <div class="text-xs text-gray-500 mb-1">朝</div>
                <div id="morning-${item.date}-${item.animal_id}"></div>
            </div>
            <div class="text-center">
                <div class="text-xs text-gray-500 mb-1">昼</div>
                <div id="noon-${item.date}-${item.animal_id}"></div>
            </div>
            <div class="text-center">
                <div class="text-xs text-gray-500 mb-1">夕</div>
                <div id="evening-${item.date}-${item.animal_id}"></div>
            </div>
        </div>
    `;

  // リンクを追加
  ['morning', 'noon', 'evening'].forEach(timeSlot => {
    const container = card.querySelector(`#${timeSlot}-${item.date}-${item.animal_id}`);
    const link = createRecordLink(item, timeSlot);
    container.appendChild(link);
  });

  return card;
}

/**
 * 記録リンクを作成
 */
function createRecordLink(item, timeSlot) {
  const record = item[timeSlot];
  const link = document.createElement('a');
  link.className = 'text-2xl font-bold hover:opacity-70 transition-opacity';

  if (record.exists) {
    // 記録あり: ○ → 詳細/編集画面
    link.textContent = '○';
    link.href = `/admin/care-logs/${record.log_id}`;
    link.className += ' text-green-600';
    link.title = `食欲: ${record.appetite}, 元気: ${record.energy}`;
  } else {
    // 記録なし: × → 新規登録画面
    link.textContent = '×';
    link.href = `/admin/care-logs/new?animal_id=${item.animal_id}&date=${item.date}&time_slot=${timeSlot}`;
    link.className += ' text-red-600';
    link.title = '記録を追加';
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
        <span class="font-medium">${total}</span> 件
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
      throw new Error('CSVエクスポートに失敗しました');
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
    showError('CSVエクスポートに失敗しました');
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

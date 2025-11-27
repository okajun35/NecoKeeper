/**
 * 診療行為マスター管理
 * Medical Actions Master Management
 */

// 状態管理
let currentPage = 1;
const pageSize = 20;
let totalPages = 0;

/**
 * 初期化
 * @description ページロード時にイベントリスナーを設定し、データを読み込む
 */
document.addEventListener('i18nextInitialized', () => {
  loadMedicalActions();

  // イベントリスナー
  document.getElementById('btnNewAction').addEventListener('click', () => openModal());
  document.getElementById('btnSearch').addEventListener('click', () => {
    currentPage = 1;
    loadMedicalActions();
  });
  document.getElementById('btnClear').addEventListener('click', clearFilters);
  document.getElementById('btnPrev').addEventListener('click', () => changePage(-1));
  document.getElementById('btnNext').addEventListener('click', () => changePage(1));
  document.getElementById('btnCancel').addEventListener('click', closeModal);
  document.getElementById('actionForm').addEventListener('submit', handleSubmit);

  // 言語切り替え時に動的コンテンツを再レンダリング
  document.addEventListener('languageChanged', loadMedicalActions);
});

/**
 * 診療行為一覧を読み込み
 * @description APIから診療行為一覧を取得してテーブルに表示
 */
async function loadMedicalActions() {
  const loading = document.getElementById('loading');
  const error = document.getElementById('error');
  const mobileList = document.getElementById('mobileList');
  const desktopList = document.getElementById('desktopList');

  loading.classList.remove('hidden');
  error.classList.add('hidden');
  mobileList.innerHTML = '';
  desktopList.innerHTML = '';

  try {
    const params = new URLSearchParams({
      page: currentPage,
      page_size: pageSize,
    });

    const searchName = document.getElementById('searchName').value;
    if (searchName) params.append('name_filter', searchName);

    const validOn = document.getElementById('filterValidOn').value;
    if (validOn) params.append('valid_on', validOn);

    const data = await apiRequest(`/api/v1/medical-actions?${params}`);

    if (!data) {
      // apiRequest は 401 エラー時に null を返す（自動でログアウト）
      return;
    }

    totalPages = data.total_pages;

    // データが0件でもエラーではない
    renderMobileList(data.items);
    renderDesktopList(data.items);
    updatePagination(data);
  } catch (err) {
    console.error('Error loading medical actions:', err);
    error.textContent = err.message || translate('messages.load_error', { ns: 'medical_actions' });
    error.classList.remove('hidden');
  } finally {
    loading.classList.add('hidden');
  }
}

/**
 * モバイルリスト描画
 * @param {Array} items - 診療行為データの配列
 */
function renderMobileList(items) {
  const container = document.getElementById('mobileList');

  items.forEach(item => {
    const card = document.createElement('div');
    card.className = 'p-4 hover:bg-gray-50';
    card.innerHTML = `
            <div class="flex items-start justify-between mb-2">
                <div>
                    <h3 class="font-medium text-gray-900">${item.name}</h3>
                    <p class="text-sm text-gray-500">${formatDateRange(item.valid_from, item.valid_to)}</p>
                </div>
                <span class="px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded">${item.currency}</span>
            </div>
            <div class="space-y-1 text-sm text-gray-600">
                <p>${translate('table.cost_price', { ns: 'medical_actions' })}: ${formatPrice(item.cost_price, item.currency)}</p>
                <p>${translate('table.selling_price', { ns: 'medical_actions' })}: ${formatPrice(item.selling_price, item.currency)}</p>
                <p>${translate('table.procedure_fee', { ns: 'medical_actions' })}: ${formatPrice(item.procedure_fee, item.currency)}</p>
            </div>
            <div class="mt-3 flex gap-2">
                <button onclick="editAction(${item.id})" class="flex-1 px-3 py-1.5 text-sm bg-indigo-600 text-white rounded hover:bg-indigo-700">
                    ${translate('buttons.edit', { ns: 'medical_actions' })}
                </button>
            </div>
        `;
    container.appendChild(card);
  });
}

/**
 * デスクトップリスト描画
 * @param {Array} items - 診療行為データの配列
 */
function renderDesktopList(items) {
  const tbody = document.getElementById('desktopList');

  items.forEach(item => {
    const row = document.createElement('tr');
    row.className = 'hover:bg-gray-50';
    row.innerHTML = `
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">${item.name}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600">${formatDateRange(item.valid_from, item.valid_to)}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600 text-right">${formatPrice(item.cost_price, item.currency)}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600 text-right">${formatPrice(item.selling_price, item.currency)}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600 text-right">${formatPrice(item.procedure_fee, item.currency)}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600 text-center">${item.currency}</td>
            <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <button onclick="editAction(${item.id})" class="text-indigo-600 hover:text-indigo-900">${translate('buttons.edit', { ns: 'medical_actions' })}</button>
            </td>
        `;
    tbody.appendChild(row);
  });
}

/**
 * ページネーション更新
 * @param {Object} data - APIレスポンスデータ
 */
function updatePagination(data) {
  const info = document.getElementById('paginationInfo');
  const btnPrev = document.getElementById('btnPrev');
  const btnNext = document.getElementById('btnNext');

  const start = (data.page - 1) * data.page_size + 1;
  const end = Math.min(data.page * data.page_size, data.total);
  info.textContent = translate('pagination.info', {
    ns: 'medical_actions',
    start: start,
    end: end,
    total: data.total,
  });

  btnPrev.disabled = data.page === 1;
  btnNext.disabled = data.page >= data.total_pages;
}

/**
 * ページ変更
 * @param {number} delta - ページ変更量（+1 or -1）
 */
function changePage(delta) {
  currentPage += delta;
  loadMedicalActions();
}

/**
 * フィルタークリア
 */
function clearFilters() {
  document.getElementById('searchName').value = '';
  document.getElementById('filterValidOn').value = '';
  document.getElementById('filterCurrency').value = '';
  currentPage = 1;
  loadMedicalActions();
}

/**
 * モーダルを開く
 * @param {number|null} actionId - 編集する診療行為ID（新規登録の場合はnull）
 */
function openModal(actionId = null) {
  const modal = document.getElementById('modalForm');
  const title = document.getElementById('modalTitle');
  const form = document.getElementById('actionForm');

  form.reset();
  document.getElementById('actionId').value = actionId || '';

  if (actionId) {
    title.setAttribute('data-i18n', 'modal.title_edit');
    title.textContent = translate('modal.title_edit', { ns: 'medical_actions' });
    loadActionData(actionId);
  } else {
    title.setAttribute('data-i18n', 'modal.title_new');
    title.textContent = translate('modal.title_new', { ns: 'medical_actions' });
  }

  modal.classList.remove('hidden');
  modal.classList.add('flex');
}

/**
 * モーダルを閉じる
 */
function closeModal() {
  const modal = document.getElementById('modalForm');
  modal.classList.add('hidden');
  modal.classList.remove('flex');
}

/**
 * 診療行為データを読み込み
 * @param {number} actionId - 診療行為ID
 */
async function loadActionData(actionId) {
  try {
    const data = await apiRequest(`/api/v1/medical-actions/${actionId}`);

    if (!data) {
      // apiRequest は 401 エラー時に null を返す（自動でログアウト）
      return;
    }

    document.getElementById('name').value = data.name;
    document.getElementById('validFrom').value = data.valid_from;
    document.getElementById('validTo').value = data.valid_to || '';
    document.getElementById('costPrice').value = data.cost_price;
    document.getElementById('sellingPrice').value = data.selling_price;
    document.getElementById('procedureFee').value = data.procedure_fee;
    document.getElementById('currency').value = data.currency;
    document.getElementById('unit').value = data.unit || '';
  } catch (err) {
    alert(err.message || translate('messages.load_error', { ns: 'medical_actions' }));
    closeModal();
  }
}

/**
 * フォーム送信
 * @param {Event} e - フォーム送信イベント
 */
async function handleSubmit(e) {
  e.preventDefault();

  const actionId = document.getElementById('actionId').value;
  const data = {
    name: document.getElementById('name').value,
    valid_from: document.getElementById('validFrom').value,
    valid_to: document.getElementById('validTo').value || null,
    cost_price: parseFloat(document.getElementById('costPrice').value) || 0,
    selling_price: parseFloat(document.getElementById('sellingPrice').value) || 0,
    procedure_fee: parseFloat(document.getElementById('procedureFee').value) || 0,
    currency: document.getElementById('currency').value,
    unit: document.getElementById('unit').value || null,
  };

  try {
    const url = actionId ? `/api/v1/medical-actions/${actionId}` : '/api/v1/medical-actions';
    const method = actionId ? 'PUT' : 'POST';

    const result = await apiRequest(url, {
      method,
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!result) {
      // apiRequest は 401 エラー時に null を返す（自動でログアウト）
      return;
    }

    closeModal();
    loadMedicalActions();
  } catch (err) {
    alert(err.message || translate('messages.save_error', { ns: 'medical_actions' }));
  }
}

/**
 * 編集
 * @param {number} actionId - 診療行為ID
 */
function editAction(actionId) {
  openModal(actionId);
}

/**
 * ユーティリティ関数: 日付範囲のフォーマット
 * @param {string} from - 開始日
 * @param {string|null} to - 終了日
 * @returns {string} フォーマット済み日付範囲
 */
function formatDateRange(from, to) {
  if (!to) return `${from} 〜`;
  return `${from} 〜 ${to}`;
}

/**
 * ユーティリティ関数: 価格のフォーマット
 * @param {number} price - 価格
 * @param {string} currency - 通貨コード
 * @returns {string} フォーマット済み価格
 */
function formatPrice(price, currency) {
  const symbol = currency === 'JPY' ? '¥' : '$';
  return `${symbol}${parseFloat(price).toLocaleString()}`;
}

/**
 * 猫管理 JavaScript
 * Context7参照: /bigskysoftware/htmx (Trust Score: 90.7)
 */

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

// 猫一覧を読み込み
async function loadAnimals() {
  try {
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

    renderAnimalsList(response.items || []);
    renderPagination(response.total || 0, response.page || 1, response.page_size || 20);
  } catch (error) {
    console.error('Animals load error:', error);
    showToast('猫一覧の読み込みに失敗しました', 'error');
    document.getElementById('animals-list').innerHTML =
      '<div class="p-8 text-center text-red-500">読み込みに失敗しました</div>';
  }
}

// 猫一覧を描画
function renderAnimalsList(animals) {
  const container = document.getElementById('animals-list');

  if (animals.length === 0) {
    container.innerHTML =
      '<div class="p-8 text-center text-gray-500">猫が見つかりませんでした</div>';
    return;
  }

  container.innerHTML = animals
    .map(animal => {
      const photoUrl =
        animal.photo && animal.photo.trim() !== '' ? animal.photo : '/static/images/default.svg';

      return `
        <div class="p-6 hover:bg-gray-50 transition-colors">
            <div class="flex items-center gap-6">
                <!-- 写真 -->
                <img src="${photoUrl}"
                     alt="${animal.name}"
                     onerror="this.onerror=null; this.src='/static/images/default.svg';"
                     class="w-20 h-20 rounded-lg object-cover border-2 border-gray-200">

                <!-- 基本情報 -->
                <div class="flex-1 min-w-0">
                    <div class="flex items-center gap-3 mb-2">
                        <h3 class="text-lg font-semibold text-gray-900">${animal.name || '名前なし'}</h3>
                        ${getStatusBadge(animal.status)}
                    </div>
                    <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm text-gray-600">
                        <div>
                            <span class="text-gray-500">柄:</span>
                            <span class="ml-1">${animal.pattern || '-'}</span>
                        </div>
                        <div>
                            <span class="text-gray-500">性別:</span>
                            <span class="ml-1">${animal.gender || '-'}</span>
                        </div>
                        <div>
                            <span class="text-gray-500">年齢:</span>
                            <span class="ml-1">${animal.age || '-'}</span>
                        </div>
                        <div>
                            <span class="text-gray-500">保護日:</span>
                            <span class="ml-1">${animal.rescue_date ? formatDate(new Date(animal.rescue_date)) : '-'}</span>
                        </div>
                    </div>
                </div>

                <!-- アクション -->
                <div class="flex gap-2">
                    <a href="/admin/animals/${animal.id}"
                       class="px-4 py-2 text-sm bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors">
                        詳細
                    </a>
                    <a href="/admin/animals/${animal.id}/edit"
                       class="px-4 py-2 text-sm bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors">
                        編集
                    </a>
                    <button onclick="showQRCode(${animal.id})"
                            class="px-4 py-2 text-sm bg-green-100 text-green-700 rounded-lg hover:bg-green-200 transition-colors">
                        QR
                    </button>
                </div>
            </div>
        </div>
    `;
    })
    .join('');
}

// ページネーションを描画
function renderPagination(total, page, pageSize) {
  const totalPages = Math.ceil(total / pageSize);
  const container = document.getElementById('pagination');

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
                全 ${total} 件中 ${(page - 1) * pageSize + 1} - ${Math.min(page * pageSize, total)} 件を表示
            </div>
            <div class="flex gap-2">
                <button onclick="changePage(${page - 1})"
                        ${page === 1 ? 'disabled' : ''}
                        class="px-3 py-2 text-sm border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed">
                    前へ
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
                    次へ
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

  // モーダルを作成
  const modal = document.createElement('div');
  modal.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';
  modal.innerHTML = `
    <div class="bg-white rounded-lg p-6 max-w-md w-full mx-4">
      <div class="flex justify-between items-center mb-4">
        <h3 class="text-lg font-semibold">QRコード</h3>
        <button onclick="this.closest('.fixed').remove()"
                class="text-gray-500 hover:text-gray-700">
          ✕
        </button>
      </div>
      <div class="flex justify-center">
        <img src="${qrUrl}" alt="QRコード" class="w-64 h-64">
      </div>
      <p class="mt-4 text-sm text-gray-600 text-center">
        このQRコードをスキャンすると、世話記録入力画面が開きます
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
  // 初期読み込み
  loadAnimals();

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

// グローバルエクスポート
window.changePage = changePage;
window.showQRCode = showQRCode;

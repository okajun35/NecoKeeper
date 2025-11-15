/**
 * 猫管理 JavaScript
 * Context7参照: /bigskysoftware/htmx (Trust Score: 90.7)
 */

let currentPage = 1;
let currentPageSize = 20;
let currentStatus = '';
let currentSearch = '';

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
    .map(
      animal => `
        <div class="p-6 hover:bg-gray-50 transition-colors">
            <div class="flex items-center gap-6">
                <!-- 写真 -->
                <img src="${animal.photo || '/static/images/default.svg'}"
                     alt="${animal.name}"
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
                    <button onclick="generateQRCard(${animal.id})"
                            class="px-4 py-2 text-sm bg-green-100 text-green-700 rounded-lg hover:bg-green-200 transition-colors">
                        QR
                    </button>
                </div>
            </div>
        </div>
    `
    )
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

// QRカード生成
async function generateQRCard(animalId) {
  try {
    const response = await fetch(`${API_BASE}/pdf/qr-card`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        animal_id: animalId,
      }),
    });

    if (!response.ok) {
      throw new Error('QRカードの生成に失敗しました');
    }

    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `qr_card_${animalId}.pdf`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);

    showToast('QRカードをダウンロードしました', 'success');
  } catch (error) {
    console.error('QR card generation error:', error);
    showToast('QRカードの生成に失敗しました', 'error');
  }
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
window.generateQRCard = generateQRCard;

/**
 * ボランティア管理ページのJavaScript
 */

let currentPage = 1;
const pageSize = 20;

// ページ読み込み時の初期化
document.addEventListener('i18nextInitialized', () => {
  loadVolunteers();

  // 検索・フィルターのイベントリスナー
  document.getElementById('btnSearch')?.addEventListener('click', () => {
    currentPage = 1;
    loadVolunteers();
  });

  document.getElementById('btnClear')?.addEventListener('click', clearFilters);
  document.getElementById('btnPrev')?.addEventListener('click', () => changePage(-1));
  document.getElementById('btnNext')?.addEventListener('click', () => changePage(1));

  // 新規登録ボタン
  document
    .querySelector('[data-i18n="add_new"]')
    ?.closest('button')
    ?.addEventListener('click', () => {
      window.location.href = '/admin/volunteers/new';
    });

  // 言語切り替え時に再読み込み
  document.addEventListener('languageChanged', loadVolunteers);
});

// ボランティア一覧を読み込み
async function loadVolunteers() {
  const loading = document.getElementById('loading');
  const error = document.getElementById('error');
  const mobileList = document.getElementById('mobileList');
  const desktopList = document.getElementById('desktopList');

  if (loading) loading.classList.remove('hidden');
  if (error) error.classList.add('hidden');
  if (mobileList) mobileList.innerHTML = '';
  if (desktopList) desktopList.innerHTML = '';

  try {
    const params = new URLSearchParams({
      page: currentPage,
      page_size: pageSize,
    });

    const searchName = document.getElementById('searchName')?.value;
    if (searchName) params.append('search', searchName);

    const filterStatus = document.getElementById('filterStatus')?.value;
    if (filterStatus) params.append('status', filterStatus);

    const filterAffiliation = document.getElementById('filterAffiliation')?.value;
    if (filterAffiliation) params.append('affiliation', filterAffiliation);

    const response = await fetch(`/api/v1/volunteers?${params}`, {
      headers: {
        Authorization: `Bearer ${getToken()}`,
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || translate('messages.load_error', { ns: 'volunteers' }));
    }

    const data = await response.json();

    // データを描画
    if (mobileList) renderMobileList(data.items || data);
    if (desktopList) renderDesktopList(data.items || data);
    if (data.total !== undefined) updatePagination(data);
  } catch (err) {
    console.error('Error loading volunteers:', err);
    if (error) {
      error.querySelector('p').textContent = err.message;
      error.classList.remove('hidden');
    }
  } finally {
    if (loading) loading.classList.add('hidden');
  }
}

// モバイルリスト描画
function renderMobileList(items) {
  const container = document.getElementById('mobileList');
  if (!container) return;

  items.forEach(item => {
    const card = document.createElement('div');
    card.className = 'p-4 hover:bg-gray-50';
    card.innerHTML = `
      <div class="flex items-start justify-between mb-2">
        <div>
          <h3 class="font-medium text-gray-900">${item.name}</h3>
          <p class="text-sm text-gray-500">${item.contact || ''}</p>
        </div>
        <span class="px-2 py-1 text-xs ${item.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'} rounded">
          ${translate(item.status === 'active' ? 'status_active' : 'status_inactive', { ns: 'volunteers' })}
        </span>
      </div>
      <div class="space-y-1 text-sm text-gray-600">
        <p>${translate('affiliation', { ns: 'volunteers' })}: ${item.affiliation || '-'}</p>
        <p>${translate('start_date', { ns: 'volunteers' })}: ${window.formatDate ? window.formatDate(item.started_at) : item.started_at || '-'}</p>
      </div>
      <div class="mt-3 flex gap-2">
        <button onclick="viewDetails(${item.id})" class="flex-1 px-3 py-1.5 text-sm bg-indigo-600 text-white rounded hover:bg-indigo-700">
          ${translate('details', { ns: 'common' })}
        </button>
        <button onclick="editVolunteer(${item.id})" class="flex-1 px-3 py-1.5 text-sm bg-gray-200 text-gray-700 rounded hover:bg-gray-300">
          ${translate('edit', { ns: 'common' })}
        </button>
      </div>
    `;
    container.appendChild(card);
  });
}

// デスクトップリスト描画
function renderDesktopList(items) {
  const tbody = document.getElementById('desktopList');
  if (!tbody) return;

  items.forEach(item => {
    const row = document.createElement('tr');
    row.className = 'hover:bg-gray-50';
    row.innerHTML = `
      <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">${item.name}</td>
      <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600">${item.contact || '-'}</td>
      <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600">${item.affiliation || '-'}</td>
      <td class="px-6 py-4 whitespace-nowrap text-sm">
        <span class="px-2 py-1 text-xs ${item.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'} rounded">
          ${translate(item.status === 'active' ? 'status_active' : 'status_inactive', { ns: 'volunteers' })}
        </span>
      </td>
      <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600">${window.formatDate ? window.formatDate(item.started_at) : item.started_at || '-'}</td>
      <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
        <button onclick="viewDetails(${item.id})" class="text-indigo-600 hover:text-indigo-900 mr-3">
          ${translate('details', { ns: 'common' })}
        </button>
        <button onclick="editVolunteer(${item.id})" class="text-indigo-600 hover:text-indigo-900">
          ${translate('edit', { ns: 'common' })}
        </button>
      </td>
    `;
    tbody.appendChild(row);
  });
}

// ページネーション更新
function updatePagination(data) {
  const info = document.getElementById('paginationInfo');
  const btnPrev = document.getElementById('btnPrev');
  const btnNext = document.getElementById('btnNext');

  if (info) {
    const start = (data.page - 1) * data.page_size + 1;
    const end = Math.min(data.page * data.page_size, data.total);
    info.innerHTML = `<span class="font-medium">${start}</span> - <span class="font-medium">${end}</span> / <span class="font-medium">${data.total}</span> ${translate('items', { ns: 'common' })}`;
  }

  if (btnPrev) btnPrev.disabled = data.page === 1;
  if (btnNext) btnNext.disabled = data.page >= data.total_pages;
}

// ページ変更
function changePage(delta) {
  currentPage += delta;
  loadVolunteers();
}

// フィルタークリア
function clearFilters() {
  const searchName = document.getElementById('searchName');
  const filterStatus = document.getElementById('filterStatus');
  const filterAffiliation = document.getElementById('filterAffiliation');

  if (searchName) searchName.value = '';
  if (filterStatus) filterStatus.value = '';
  if (filterAffiliation) filterAffiliation.value = '';

  currentPage = 1;
  loadVolunteers();
}

// 詳細表示
function viewDetails(volunteerId) {
  window.location.href = `/admin/volunteers/${volunteerId}`;
}

// 編集
function editVolunteer(volunteerId) {
  window.location.href = `/admin/volunteers/${volunteerId}/edit`;
}

/**
 * ボランティア管理ページのJavaScript
 */

const adminBasePath = window.ADMIN_BASE_PATH || window.__ADMIN_BASE_PATH__ || '/admin';
let currentPage = 1;
const pageSize = 20;
let pageInitialized = false;

function initializePage() {
  if (pageInitialized) return;
  pageInitialized = true;

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
      window.location.href = `${adminBasePath}/volunteers/new`;
    });

  // 言語切り替え時に再読み込み
  document.addEventListener('languageChanged', loadVolunteers);
}

// ページ読み込み時の初期化
document.addEventListener('i18nextInitialized', initializePage, { once: true });
if (window.i18n && typeof window.i18n.getCurrentLanguage === 'function') {
  initializePage();
}

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

// モバイルリスト描画
function renderMobileList(items) {
  const container = document.getElementById('mobileList');
  if (!container) return;

  items.forEach(item => {
    const card = cloneTemplate('tmpl-mobile-card');
    assertRequiredSelectors(
      card,
      [
        '.js-name',
        '.js-contact',
        '.js-status',
        '.js-affiliation',
        '.js-start-date',
        '.js-view-btn',
        '.js-edit-btn',
      ],
      'volunteers.tmpl-mobile-card'
    );

    // 基本情報
    requireSelector(card, '.js-name', 'volunteers.tmpl-mobile-card').textContent = item.name;
    requireSelector(card, '.js-contact', 'volunteers.tmpl-mobile-card').textContent =
      item.contact || '';

    // ステータス
    const statusSpan = requireSelector(card, '.js-status', 'volunteers.tmpl-mobile-card');
    if (item.status === 'active') {
      statusSpan.classList.add('bg-green-100', 'text-green-800');
      statusSpan.textContent = translate('status_active', { ns: 'volunteers' });
    } else {
      statusSpan.classList.add('bg-gray-100', 'text-gray-800');
      statusSpan.textContent = translate('status_inactive', { ns: 'volunteers' });
    }

    // 詳細情報
    requireSelector(card, '.js-affiliation', 'volunteers.tmpl-mobile-card').textContent =
      item.affiliation || '-';

    const startDate = window.formatDate
      ? window.formatDate(item.started_at)
      : item.started_at || '-';
    requireSelector(card, '.js-start-date', 'volunteers.tmpl-mobile-card').textContent = startDate;

    // ボタン
    const viewBtn = requireSelector(card, '.js-view-btn', 'volunteers.tmpl-mobile-card');
    viewBtn.onclick = () => viewDetails(item.id);

    const editBtn = requireSelector(card, '.js-edit-btn', 'volunteers.tmpl-mobile-card');
    editBtn.onclick = () => editVolunteer(item.id);

    translateDynamicElement(card);
    container.appendChild(card);
  });
}

// デスクトップリスト描画
function renderDesktopList(items) {
  const tbody = document.getElementById('desktopList');
  if (!tbody) return;

  items.forEach(item => {
    const row = cloneTemplate('tmpl-desktop-row');
    assertRequiredSelectors(
      row,
      [
        '.js-name',
        '.js-contact',
        '.js-affiliation',
        '.js-status',
        '.js-start-date',
        '.js-view-btn',
        '.js-edit-btn',
      ],
      'volunteers.tmpl-desktop-row'
    );

    requireSelector(row, '.js-name', 'volunteers.tmpl-desktop-row').textContent = item.name;
    requireSelector(row, '.js-contact', 'volunteers.tmpl-desktop-row').textContent =
      item.contact || '-';
    requireSelector(row, '.js-affiliation', 'volunteers.tmpl-desktop-row').textContent =
      item.affiliation || '-';

    // ステータス
    const statusSpan = requireSelector(row, '.js-status', 'volunteers.tmpl-desktop-row');
    if (item.status === 'active') {
      statusSpan.classList.add('bg-green-100', 'text-green-800');
      statusSpan.textContent = translate('status_active', { ns: 'volunteers' });
    } else {
      statusSpan.classList.add('bg-gray-100', 'text-gray-800');
      statusSpan.textContent = translate('status_inactive', { ns: 'volunteers' });
    }

    const startDate = window.formatDate
      ? window.formatDate(item.started_at)
      : item.started_at || '-';
    requireSelector(row, '.js-start-date', 'volunteers.tmpl-desktop-row').textContent = startDate;

    // ボタン
    const viewBtn = requireSelector(row, '.js-view-btn', 'volunteers.tmpl-desktop-row');
    viewBtn.onclick = () => viewDetails(item.id);

    const editBtn = requireSelector(row, '.js-edit-btn', 'volunteers.tmpl-desktop-row');
    editBtn.onclick = () => editVolunteer(item.id);

    translateDynamicElement(row);
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
  window.location.href = `${adminBasePath}/volunteers/${volunteerId}`;
}

// 編集
function editVolunteer(volunteerId) {
  window.location.href = `${adminBasePath}/volunteers/${volunteerId}/edit`;
}

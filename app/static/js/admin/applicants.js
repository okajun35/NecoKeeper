/**
 * 里親希望者管理画面のJavaScript
 */

const adminBasePath = window.ADMIN_BASE_PATH || window.__ADMIN_BASE_PATH__ || '/admin';
let currentPage = 0;
const pageSize = 20;
let allApplicants = [];
let filteredApplicants = [];

// i18next翻訳ヘルパー
function t(key, options = {}) {
  if (typeof i18next !== 'undefined' && i18next.isInitialized) {
    return i18next.t(key, options);
  }
  // フォールバック: キーの最後の部分を返す
  const parts = key.split('.');
  return parts[parts.length - 1];
}

// 初期化
document.addEventListener('DOMContentLoaded', () => {
  // i18nextの初期化を待つ
  const checkI18n = setInterval(() => {
    if (typeof i18next !== 'undefined' && i18next.isInitialized) {
      clearInterval(checkI18n);
      loadApplicants();
      setupEventListeners();
    }
  }, 50);
});

// イベントリスナー設定
function setupEventListeners() {
  document.getElementById('searchBtn').addEventListener('click', () => filterApplicants());
  document.getElementById('clearBtn').addEventListener('click', () => clearSearch());
  document.getElementById('prevBtn').addEventListener('click', () => changePage(-1));
  document.getElementById('nextBtn').addEventListener('click', () => changePage(1));
}

// 里親希望者一覧を読み込み
async function loadApplicants() {
  showLoading(true);
  hideError();

  try {
    const token = localStorage.getItem('access_token');
    const response = await fetch('/api/v1/adoptions/applicants-extended?limit=1000', {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      throw new Error('データの取得に失敗しました');
    }

    const data = await response.json();

    // レスポンスが配列であることを確認
    if (!Array.isArray(data)) {
      console.error('Invalid response format:', data);
      throw new Error('データ形式が不正です');
    }

    allApplicants = data;
    filteredApplicants = [...allApplicants];
    currentPage = 0;
    renderApplicants();
  } catch (error) {
    console.error('Error loading applicants:', error);
    showError(error.message);
    // エラー時は空の配列を設定
    allApplicants = [];
    filteredApplicants = [];
    renderApplicants();
  } finally {
    showLoading(false);
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

// 里親希望者を表示
function renderApplicants() {
  const start = currentPage * pageSize;
  const end = start + pageSize;
  const pageApplicants = filteredApplicants.slice(start, end);

  const mobileList = document.getElementById('mobileList');
  const desktopList = document.getElementById('desktopList');

  if (mobileList) mobileList.innerHTML = '';
  if (desktopList) desktopList.innerHTML = '';

  pageApplicants.forEach(applicant => {
    // モバイル表示
    if (mobileList) {
      const card = cloneTemplate('tmpl-mobile-card');
      assertRequiredSelectors(
        card,
        [
          '.js-name',
          '.js-contact',
          '.js-address-container',
          '.js-address',
          '.js-household',
          '.js-registration-date',
          '.js-edit-btn',
          '.js-records-btn',
        ],
        'applicants.tmpl-mobile-card'
      );

      requireSelector(card, '.js-name', 'applicants.tmpl-mobile-card').textContent = applicant.name;
      requireSelector(card, '.js-contact', 'applicants.tmpl-mobile-card').textContent =
        formatContact(applicant);

      const address = formatAddress(applicant);
      if (address) {
        requireSelector(
          card,
          '.js-address-container',
          'applicants.tmpl-mobile-card'
        ).classList.remove('hidden');
        requireSelector(card, '.js-address', 'applicants.tmpl-mobile-card').textContent = address;
      }

      requireSelector(card, '.js-household', 'applicants.tmpl-mobile-card').textContent =
        formatHousehold(applicant);
      requireSelector(card, '.js-registration-date', 'applicants.tmpl-mobile-card').textContent =
        formatDate(applicant.created_at);

      const editBtn = requireSelector(card, '.js-edit-btn', 'applicants.tmpl-mobile-card');
      editBtn.href = `${adminBasePath}/adoptions/applicants/${applicant.id}/edit`;

      const recordsBtn = requireSelector(card, '.js-records-btn', 'applicants.tmpl-mobile-card');
      recordsBtn.onclick = () => viewAdoptionRecords(applicant.id);

      translateDynamicElement(card);
      mobileList.appendChild(card);
    }

    // デスクトップ表示
    if (desktopList) {
      const row = cloneTemplate('tmpl-desktop-row');
      assertRequiredSelectors(
        row,
        [
          '.js-name',
          '.js-contact',
          '.js-address',
          '.js-household',
          '.js-registration-date',
          '.js-edit-btn',
          '.js-records-btn',
        ],
        'applicants.tmpl-desktop-row'
      );

      requireSelector(row, '.js-name', 'applicants.tmpl-desktop-row').textContent = applicant.name;
      requireSelector(row, '.js-contact', 'applicants.tmpl-desktop-row').textContent =
        formatContact(applicant);
      requireSelector(row, '.js-address', 'applicants.tmpl-desktop-row').textContent =
        formatAddress(applicant) || '-';
      requireSelector(row, '.js-household', 'applicants.tmpl-desktop-row').textContent =
        formatHousehold(applicant);
      requireSelector(row, '.js-registration-date', 'applicants.tmpl-desktop-row').textContent =
        formatDate(applicant.created_at);

      const editBtn = requireSelector(row, '.js-edit-btn', 'applicants.tmpl-desktop-row');
      editBtn.href = `${adminBasePath}/adoptions/applicants/${applicant.id}/edit`;

      const recordsBtn = requireSelector(row, '.js-records-btn', 'applicants.tmpl-desktop-row');
      recordsBtn.onclick = () => viewAdoptionRecords(applicant.id);

      translateDynamicElement(row);
      desktopList.appendChild(row);
    }
  });

  // ページネーション情報
  updatePagination();
}

// ページネーション更新
function updatePagination() {
  const total = filteredApplicants.length;
  const start = total === 0 ? 0 : currentPage * pageSize + 1;
  const end = total === 0 ? 0 : Math.min((currentPage + 1) * pageSize, total);
  const itemsText = window.i18n && window.i18n.t ? window.i18n.t('items', { ns: 'common' }) : '件';

  document.getElementById('paginationInfo').textContent =
    `${start} - ${end} / ${total} ${itemsText}`;

  document.getElementById('prevBtn').disabled = currentPage === 0;
  document.getElementById('nextBtn').disabled = end >= total;
}

// ページ変更
function changePage(delta) {
  currentPage += delta;
  renderApplicants();
}

// フィルター
function filterApplicants() {
  const searchText = document.getElementById('searchInput').value.toLowerCase();

  filteredApplicants = allApplicants.filter(applicant => {
    const name = applicant.name?.toLowerCase() ?? '';
    const contact = formatContact(applicant).toLowerCase();
    const phone = applicant.phone?.toLowerCase?.() ?? '';
    const email = applicant.contact_email?.toLowerCase?.() ?? '';
    const lineId = applicant.contact_line_id?.toLowerCase?.() ?? '';
    return (
      name.includes(searchText) ||
      contact.includes(searchText) ||
      phone.includes(searchText) ||
      email.includes(searchText) ||
      lineId.includes(searchText)
    );
  });

  currentPage = 0;
  renderApplicants();
}

// 検索クリア
function clearSearch() {
  document.getElementById('searchInput').value = '';
  filteredApplicants = [...allApplicants];
  currentPage = 0;
  renderApplicants();
}

// 譲渡記録を表示
function viewAdoptionRecords(applicantId) {
  window.location.href = `${adminBasePath}/adoptions/records?applicant_id=${applicantId}`;
}

function formatContact(applicant) {
  if (applicant.contact_type === 'line' && applicant.contact_line_id) {
    return `LINE: ${applicant.contact_line_id}`;
  }
  if (applicant.contact_email) {
    return `メール: ${applicant.contact_email}`;
  }
  if (applicant.phone) {
    return `電話: ${applicant.phone}`;
  }
  return '-';
}

function formatAddress(applicant) {
  const parts = [applicant.address1, applicant.address2].filter(Boolean);
  return parts.join(' ');
}

function formatHousehold(applicant) {
  const count = applicant.household_members?.length ?? 0;
  return `${count}人`;
}

// 注: formatDate等はcommon.jsで定義済み

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

function showLoading(show) {
  document.getElementById('loading').classList.toggle('hidden', !show);
  document.getElementById('applicantsList').classList.toggle('hidden', show);
}

function showError(message) {
  const errorDiv = document.getElementById('error');
  errorDiv.textContent = message;
  errorDiv.classList.remove('hidden');
}

function hideError() {
  document.getElementById('error').classList.add('hidden');
}

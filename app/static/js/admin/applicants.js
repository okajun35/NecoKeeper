/**
 * 里親希望者管理画面のJavaScript
 */

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

// 里親希望者を表示
function renderApplicants() {
  const start = currentPage * pageSize;
  const end = start + pageSize;
  const pageApplicants = filteredApplicants.slice(start, end);

  // モバイル表示
  const mobileList = document.getElementById('mobileList');
  mobileList.innerHTML = pageApplicants
    .map(
      applicant => `
        <div class="p-4 hover:bg-gray-50">
            <div class="flex items-start justify-between mb-2">
                <div>
                  <h3 class="font-medium text-gray-900">${escapeHtml(applicant.name)}</h3>
                  <p class="text-sm text-gray-500">${escapeHtml(formatContact(applicant))}</p>
                </div>
            </div>
            <div class="space-y-1 text-sm text-gray-600">
                ${formatAddress(applicant) ? `<p>住所: ${escapeHtml(formatAddress(applicant))}</p>` : ''}
                <p>家族構成: ${formatHousehold(applicant)}</p>
                <p>${t('applicants.labels.registration_date', { ns: 'adoptions' })}: ${formatDate(applicant.created_at)}</p>
            </div>
            <div class="mt-3 flex gap-2">
                <a href="/admin/adoptions/applicants/${applicant.id}/edit" class="flex-1 px-3 py-1.5 text-sm bg-indigo-600 text-white rounded hover:bg-indigo-700 text-center">
                    ${t('buttons.edit', { ns: 'common' })}
                </a>
                <button onclick="viewAdoptionRecords(${applicant.id})" class="flex-1 px-3 py-1.5 text-sm bg-gray-200 text-gray-700 rounded hover:bg-gray-300">
                    ${t('buttons.adoption_records', { ns: 'common' })}
                </button>
            </div>
        </div>
    `
    )
    .join('');

  // デスクトップ表示
  const desktopList = document.getElementById('desktopList');
  desktopList.innerHTML = pageApplicants
    .map(
      applicant => `
        <tr class="hover:bg-gray-50">
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">${escapeHtml(applicant.name)}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600">${escapeHtml(formatContact(applicant))}</td>
            <td class="px-6 py-4 text-sm text-gray-600">${formatAddress(applicant) ? escapeHtml(formatAddress(applicant)) : '-'}</td>
            <td class="px-6 py-4 text-sm text-gray-600">${formatHousehold(applicant)}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600">${formatDate(applicant.created_at)}</td>
            <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <a href="/admin/adoptions/applicants/${applicant.id}/edit" class="text-indigo-600 hover:text-indigo-900 mr-3">${t('buttons.edit', { ns: 'common' })}</a>
                <button onclick="viewAdoptionRecords(${applicant.id})" class="text-gray-600 hover:text-gray-900">${t('buttons.adoption_records', { ns: 'common' })}</button>
            </td>
        </tr>
    `
    )
    .join('');

  // ページネーション情報
  updatePagination();
}

// ページネーション更新
function updatePagination() {
  const start = currentPage * pageSize + 1;
  const end = Math.min((currentPage + 1) * pageSize, filteredApplicants.length);
  const total = filteredApplicants.length;

  document.getElementById('paginationInfo').textContent = `${start} - ${end} / ${total} 件`;

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
  window.location.href = `/admin/adoptions/records?applicant_id=${applicantId}`;
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

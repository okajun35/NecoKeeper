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
  document.getElementById('newApplicantBtn').addEventListener('click', () => openModal());
  document.getElementById('searchBtn').addEventListener('click', () => filterApplicants());
  document.getElementById('clearBtn').addEventListener('click', () => clearSearch());
  document.getElementById('closeModal').addEventListener('click', () => closeModal());
  document.getElementById('cancelBtn').addEventListener('click', () => closeModal());
  document.getElementById('applicantForm').addEventListener('submit', e => saveApplicant(e));
  document.getElementById('prevBtn').addEventListener('click', () => changePage(-1));
  document.getElementById('nextBtn').addEventListener('click', () => changePage(1));
}

// 里親希望者一覧を読み込み
async function loadApplicants() {
  showLoading(true);
  hideError();

  try {
    const token = localStorage.getItem('access_token');
    const response = await fetch('/api/v1/adoptions/applicants?limit=1000', {
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
                    <p class="text-sm text-gray-500">${escapeHtml(applicant.contact)}</p>
                </div>
            </div>
            <div class="space-y-1 text-sm text-gray-600">
                ${applicant.address ? `<p>${t('applicants.labels.address', { ns: 'adoptions' })}: ${escapeHtml(applicant.address)}</p>` : ''}
                ${applicant.family ? `<p>${t('applicants.labels.family', { ns: 'adoptions' })}: ${escapeHtml(applicant.family)}</p>` : ''}
                <p>${t('applicants.labels.registration_date', { ns: 'adoptions' })}: ${formatDate(applicant.created_at)}</p>
            </div>
            <div class="mt-3 flex gap-2">
                <button onclick="editApplicant(${applicant.id})" class="flex-1 px-3 py-1.5 text-sm bg-indigo-600 text-white rounded hover:bg-indigo-700">
                    ${t('buttons.edit', { ns: 'common' })}
                </button>
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
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600">${escapeHtml(applicant.contact)}</td>
            <td class="px-6 py-4 text-sm text-gray-600">${applicant.address ? escapeHtml(applicant.address) : '-'}</td>
            <td class="px-6 py-4 text-sm text-gray-600">${applicant.family ? escapeHtml(applicant.family) : '-'}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600">${formatDate(applicant.created_at)}</td>
            <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <button onclick="editApplicant(${applicant.id})" class="text-indigo-600 hover:text-indigo-900 mr-3">${t('buttons.edit', { ns: 'common' })}</button>
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
    return (
      applicant.name.toLowerCase().includes(searchText) ||
      applicant.contact.toLowerCase().includes(searchText)
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

// モーダルを開く
function openModal(applicant = null) {
  const modal = document.getElementById('applicantModal');
  const form = document.getElementById('applicantForm');
  const title = document.getElementById('modalTitle');

  form.reset();

  if (applicant) {
    // 編集モード
    title.textContent = t('applicants.modal.title_edit', { ns: 'adoptions' });
    title.setAttribute('data-i18n', 'applicants.modal.title_edit');
    document.getElementById('applicantId').value = applicant.id;
    document.getElementById('name').value = applicant.name;
    document.getElementById('contact').value = applicant.contact;
    document.getElementById('address').value = applicant.address || '';
    document.getElementById('family').value = applicant.family || '';
    document.getElementById('environment').value = applicant.environment || '';
    document.getElementById('conditions').value = applicant.conditions || '';
  } else {
    // 新規登録モード
    title.textContent = t('applicants.modal.title_new', { ns: 'adoptions' });
    title.setAttribute('data-i18n', 'applicants.modal.title_new');
    document.getElementById('applicantId').value = '';
  }

  modal.classList.remove('hidden');
}

// モーダルを閉じる
function closeModal() {
  document.getElementById('applicantModal').classList.add('hidden');
}

// 里親希望者を保存
async function saveApplicant(e) {
  e.preventDefault();

  const applicantId = document.getElementById('applicantId').value;
  const data = {
    name: document.getElementById('name').value,
    contact: document.getElementById('contact').value,
    address: document.getElementById('address').value || null,
    family: document.getElementById('family').value || null,
    environment: document.getElementById('environment').value || null,
    conditions: document.getElementById('conditions').value || null,
  };

  try {
    const token = localStorage.getItem('access_token');
    const url = applicantId
      ? `/api/v1/adoptions/applicants/${applicantId}`
      : '/api/v1/adoptions/applicants';
    const method = applicantId ? 'PUT' : 'POST';

    const response = await fetch(url, {
      method: method,
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      throw new Error('保存に失敗しました');
    }

    closeModal();
    await loadApplicants();
    alert(applicantId ? '更新しました' : '登録しました');
  } catch (error) {
    alert(error.message);
  }
}

// 編集
async function editApplicant(id) {
  const applicant = allApplicants.find(a => a.id === id);
  if (applicant) {
    openModal(applicant);
  }
}

// 譲渡記録を表示
function viewAdoptionRecords(applicantId) {
  window.location.href = `/admin/adoptions/records?applicant_id=${applicantId}`;
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

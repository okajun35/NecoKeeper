/**
 * 譲渡記録管理画面のJavaScript
 */

let allRecords = [];
let filteredRecords = [];
let animals = [];
let applicants = [];

// 初期化
document.addEventListener('DOMContentLoaded', () => {
  loadData();
  setupEventListeners();
});

// イベントリスナー設定
function setupEventListeners() {
  document.getElementById('newRecordBtn').addEventListener('click', () => openInterviewModal());
  document.getElementById('filterBtn').addEventListener('click', () => filterRecords());
  document.getElementById('clearFilterBtn').addEventListener('click', () => clearFilter());
  document
    .getElementById('closeInterviewModal')
    .addEventListener('click', () => closeInterviewModal());
  document
    .getElementById('cancelInterviewBtn')
    .addEventListener('click', () => closeInterviewModal());
  document.getElementById('interviewForm').addEventListener('submit', e => saveInterview(e));
  document
    .getElementById('closeAdoptionModal')
    .addEventListener('click', () => closeAdoptionModal());
  document
    .getElementById('cancelAdoptionBtn')
    .addEventListener('click', () => closeAdoptionModal());
  document.getElementById('adoptionForm').addEventListener('submit', e => completeAdoption(e));
}

// データを読み込み
async function loadData() {
  showLoading(true);
  hideError();

  try {
    const token = localStorage.getItem('access_token');

    // 並列で全データを取得
    const [recordsRes, animalsRes, applicantsRes] = await Promise.all([
      fetch('/api/v1/adoptions/records?limit=1000', {
        headers: { Authorization: `Bearer ${token}` },
      }),
      fetch('/api/v1/animals?limit=1000', {
        headers: { Authorization: `Bearer ${token}` },
      }),
      fetch('/api/v1/adoptions/applicants?limit=1000', {
        headers: { Authorization: `Bearer ${token}` },
      }),
    ]);

    if (!recordsRes.ok || !animalsRes.ok || !applicantsRes.ok) {
      throw new Error('データの取得に失敗しました');
    }

    const recordsData = await recordsRes.json();
    const animalsData = await animalsRes.json();
    const applicantsData = await applicantsRes.json();

    // APIレスポンスが配列かオブジェクト（{items: [...]}）かを確認
    allRecords = Array.isArray(recordsData) ? recordsData : recordsData.items || [];
    animals = Array.isArray(animalsData) ? animalsData : animalsData.items || [];
    applicants = Array.isArray(applicantsData) ? applicantsData : applicantsData.items || [];

    filteredRecords = [...allRecords];
    populateFilters();
    renderRecords();
  } catch (error) {
    showError(error.message);
  } finally {
    showLoading(false);
  }
}

// フィルター選択肢を設定
function populateFilters() {
  // 猫フィルター
  const animalFilter = document.getElementById('animalFilter');
  animalFilter.innerHTML =
    '<option value="">すべて</option>' +
    animals.map(a => `<option value="${a.id}">${escapeHtml(a.name)}</option>`).join('');

  // 里親希望者フィルター
  const applicantFilter = document.getElementById('applicantFilter');
  applicantFilter.innerHTML =
    '<option value="">すべて</option>' +
    applicants.map(a => `<option value="${a.id}">${escapeHtml(a.name)}</option>`).join('');

  // モーダル用の選択肢も設定（譲渡可能な猫のみ）
  document.getElementById('animalId').innerHTML =
    '<option value="">選択してください</option>' +
    animals
      .filter(a => a.status === '譲渡可能')
      .map(a => `<option value="${a.id}">${escapeHtml(a.name)}</option>`)
      .join('');

  document.getElementById('applicantId').innerHTML =
    '<option value="">選択してください</option>' +
    applicants.map(a => `<option value="${a.id}">${escapeHtml(a.name)}</option>`).join('');
}

// 譲渡記録を表示
function renderRecords() {
  // モバイル表示
  const mobileList = document.getElementById('mobileList');
  mobileList.innerHTML = filteredRecords
    .map(record => {
      const animal = animals.find(a => a.id === record.animal_id);
      const applicant = applicants.find(a => a.id === record.applicant_id);
      const decisionBadge = getDecisionBadge(record.decision);

      return `
            <div class="p-4 hover:bg-gray-50">
                <div class="flex items-start justify-between mb-2">
                    <div>
                        <h3 class="font-medium text-gray-900">${animal ? escapeHtml(animal.name) : '不明'}</h3>
                        <p class="text-sm text-gray-500">${applicant ? escapeHtml(applicant.name) : '不明'}</p>
                    </div>
                    ${decisionBadge}
                </div>
                <div class="space-y-1 text-sm text-gray-600">
                    ${record.interview_date ? `<p>面談日: ${formatDate(record.interview_date)}</p>` : ''}
                    ${record.adoption_date ? `<p>譲渡日: ${formatDate(record.adoption_date)}</p>` : ''}
                </div>
                <div class="mt-3 flex gap-2">
                    <button onclick="editRecord(${record.id})" class="flex-1 px-3 py-1.5 text-sm bg-indigo-600 text-white rounded hover:bg-indigo-700">
                        編集
                    </button>
                    ${
                      !record.adoption_date && record.decision === 'approved'
                        ? `
                        <button onclick="openAdoptionModal(${record.animal_id}, ${record.applicant_id})" class="flex-1 px-3 py-1.5 text-sm bg-green-600 text-white rounded hover:bg-green-700">
                            譲渡完了
                        </button>
                    `
                        : ''
                    }
                </div>
            </div>
        `;
    })
    .join('');

  // デスクトップ表示
  const desktopList = document.getElementById('desktopList');
  desktopList.innerHTML = filteredRecords
    .map(record => {
      const animal = animals.find(a => a.id === record.animal_id);
      const applicant = applicants.find(a => a.id === record.applicant_id);
      const decisionBadge = getDecisionBadge(record.decision);

      return `
            <tr class="hover:bg-gray-50">
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">${animal ? escapeHtml(animal.name) : '不明'}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600">${applicant ? escapeHtml(applicant.name) : '不明'}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600">${record.interview_date ? formatDate(record.interview_date) : '-'}</td>
                <td class="px-6 py-4 whitespace-nowrap">${decisionBadge}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600">${record.adoption_date ? formatDate(record.adoption_date) : '-'}</td>
                <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <button onclick="editRecord(${record.id})" class="text-indigo-600 hover:text-indigo-900 mr-3">編集</button>
                    ${
                      !record.adoption_date && record.decision === 'approved'
                        ? `
                        <button onclick="openAdoptionModal(${record.animal_id}, ${record.applicant_id})" class="text-green-600 hover:text-green-900">譲渡完了</button>
                    `
                        : ''
                    }
                </td>
            </tr>
        `;
    })
    .join('');
}

// 判定結果バッジ
function getDecisionBadge(decision) {
  const badges = {
    pending: '<span class="px-2 py-1 text-xs bg-yellow-100 text-yellow-800 rounded">審査中</span>',
    approved: '<span class="px-2 py-1 text-xs bg-green-100 text-green-800 rounded">承認済み</span>',
    rejected: '<span class="px-2 py-1 text-xs bg-red-100 text-red-800 rounded">不承認</span>',
  };
  return (
    badges[decision] || '<span class="px-2 py-1 text-xs bg-gray-100 text-gray-800 rounded">-</span>'
  );
}

// フィルター
function filterRecords() {
  const animalId = document.getElementById('animalFilter').value;
  const applicantId = document.getElementById('applicantFilter').value;
  const decision = document.getElementById('decisionFilter').value;

  filteredRecords = allRecords.filter(record => {
    if (animalId && record.animal_id !== parseInt(animalId)) return false;
    if (applicantId && record.applicant_id !== parseInt(applicantId)) return false;
    if (decision && record.decision !== decision) return false;
    return true;
  });

  renderRecords();
}

// フィルタークリア
function clearFilter() {
  document.getElementById('animalFilter').value = '';
  document.getElementById('applicantFilter').value = '';
  document.getElementById('decisionFilter').value = '';
  filteredRecords = [...allRecords];
  renderRecords();
}

// 面談記録モーダルを開く
function openInterviewModal(record = null) {
  const modal = document.getElementById('interviewModal');
  const form = document.getElementById('interviewForm');
  const title = document.getElementById('interviewModalTitle');

  form.reset();

  if (record) {
    title.textContent = '面談記録編集';
    document.getElementById('recordId').value = record.id;
    document.getElementById('animalId').value = record.animal_id;
    document.getElementById('applicantId').value = record.applicant_id;
    document.getElementById('interviewDate').value = record.interview_date || '';
    document.getElementById('interviewNote').value = record.interview_note || '';
    document.getElementById('decision').value = record.decision || 'pending';
  } else {
    title.textContent = '面談記録登録';
    document.getElementById('recordId').value = '';
    document.getElementById('decision').value = 'pending';
  }

  modal.classList.remove('hidden');
}

// 面談記録モーダルを閉じる
function closeInterviewModal() {
  document.getElementById('interviewModal').classList.add('hidden');
}

// 面談記録を保存
async function saveInterview(e) {
  e.preventDefault();

  const recordId = document.getElementById('recordId').value;
  const data = {
    animal_id: parseInt(document.getElementById('animalId').value),
    applicant_id: parseInt(document.getElementById('applicantId').value),
    interview_date: document.getElementById('interviewDate').value || null,
    interview_note: document.getElementById('interviewNote').value || null,
    decision: document.getElementById('decision').value || 'pending',
  };

  try {
    const token = localStorage.getItem('access_token');
    const url = recordId ? `/api/v1/adoptions/records/${recordId}` : '/api/v1/adoptions/records';
    const method = recordId ? 'PUT' : 'POST';

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

    closeInterviewModal();
    await loadData();
    alert(recordId ? '更新しました' : '登録しました');
  } catch (error) {
    alert(error.message);
  }
}

// 編集
async function editRecord(id) {
  const record = allRecords.find(r => r.id === id);
  if (record) {
    openInterviewModal(record);
  }
}

// 譲渡完了モーダルを開く
function openAdoptionModal(animalId, applicantId) {
  const modal = document.getElementById('adoptionModal');
  document.getElementById('adoptAnimalId').value = animalId;
  document.getElementById('adoptApplicantId').value = applicantId;
  document.getElementById('adoptionDate').value = new Date().toISOString().split('T')[0];
  modal.classList.remove('hidden');
}

// 譲渡完了モーダルを閉じる
function closeAdoptionModal() {
  document.getElementById('adoptionModal').classList.add('hidden');
}

// 譲渡完了
async function completeAdoption(e) {
  e.preventDefault();

  const animalId = document.getElementById('adoptAnimalId').value;
  const applicantId = document.getElementById('adoptApplicantId').value;
  const adoptionDate = document.getElementById('adoptionDate').value;

  try {
    const token = localStorage.getItem('access_token');
    const response = await fetch('/api/v1/adoptions/records/adopt', {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        animal_id: parseInt(animalId),
        applicant_id: parseInt(applicantId),
        adoption_date: adoptionDate,
      }),
    });

    if (!response.ok) {
      throw new Error('譲渡完了処理に失敗しました');
    }

    closeAdoptionModal();
    await loadData();
    alert('譲渡完了しました。猫のステータスが「譲渡済み」に更新されました。');
  } catch (error) {
    alert(error.message);
  }
}

// ユーティリティ関数
function formatDate(dateString) {
  if (!dateString) return '-';
  const date = new Date(dateString);
  if (isNaN(date.getTime())) return '-';
  return date.toLocaleDateString('ja-JP');
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

function showLoading(show) {
  document.getElementById('loading').classList.toggle('hidden', !show);
  document.getElementById('recordsList').classList.toggle('hidden', show);
}

function showError(message) {
  const errorDiv = document.getElementById('error');
  errorDiv.textContent = message;
  errorDiv.classList.remove('hidden');
}

function hideError() {
  document.getElementById('error').classList.add('hidden');
}

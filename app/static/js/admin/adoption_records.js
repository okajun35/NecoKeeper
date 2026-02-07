/**
 * 譲渡記録管理画面のJavaScript
 */

let allRecords = [];
let filteredRecords = [];
let animals = [];
let adoptableAnimals = [];
let applicants = [];

// Helper function for safe i18next translation
function t(key, options = {}) {
  if (typeof i18next !== 'undefined' && i18next.isInitialized) {
    return i18next.t(key, options);
  }
  // Fallback: return last part of key
  const parts = key.split('.');
  return parts[parts.length - 1];
}

function isAdoptableAnimal(animal) {
  if (!animal) return false;
  // ダッシュボードの adoptable_count と同じ定義（IN_CARE / TRIAL）
  const normalizedStatus = String(animal.status || '')
    .trim()
    .toUpperCase();
  return normalizedStatus === 'IN_CARE' || normalizedStatus === 'TRIAL';
}

function ensureAnimalOptionExists(selectElement, animalId) {
  if (!selectElement || !animalId) return;

  const optionValue = String(animalId);
  if (selectElement.querySelector(`option[value="${optionValue}"]`)) return;

  const animal = animals.find(a => a.id === animalId);
  if (!animal) return;

  const option = document.createElement('option');
  option.value = optionValue;
  option.textContent = animal.name;
  selectElement.appendChild(option);
}

// 初期化
document.addEventListener('DOMContentLoaded', () => {
  // Wait for i18next to initialize before loading data
  const checkI18n = setInterval(() => {
    if (typeof i18next !== 'undefined' && i18next.isInitialized) {
      clearInterval(checkI18n);
      loadData();
      setupEventListeners();
    }
  }, 50);
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
    // 並列で全データを取得
    const [recordsData, animalsData, adoptableAnimalsData, applicantsData] = await Promise.all([
      apiRequest('/api/v1/adoptions/records?limit=1000'),
      apiRequest('/api/v1/animals?limit=1000'),
      apiRequest('/api/v1/animals?limit=1000&is_ready_for_adoption=true'),
      apiRequest('/api/v1/adoptions/applicants-extended?limit=1000'),
    ]);

    // APIレスポンスが配列かオブジェクト（{items: [...]}）かを確認
    allRecords = Array.isArray(recordsData) ? recordsData : recordsData.items || [];
    animals = Array.isArray(animalsData) ? animalsData : animalsData.items || [];
    adoptableAnimals = Array.isArray(adoptableAnimalsData)
      ? adoptableAnimalsData
      : adoptableAnimalsData.items || [];
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
  const selectableAnimals =
    adoptableAnimals.length > 0 ? adoptableAnimals : animals.filter(isAdoptableAnimal);

  // 猫フィルター
  const animalFilter = document.getElementById('animalFilter');
  animalFilter.innerHTML =
    `<option value="">${t('common:filters.all', { ns: 'common' })}</option>` +
    selectableAnimals.map(a => `<option value="${a.id}">${escapeHtml(a.name)}</option>`).join('');

  // 里親希望者フィルター
  const applicantFilter = document.getElementById('applicantFilter');
  applicantFilter.innerHTML =
    `<option value="">${t('common:filters.all', { ns: 'common' })}</option>` +
    applicants.map(a => `<option value="${a.id}">${escapeHtml(a.name)}</option>`).join('');

  // モーダル用の選択肢（基本は譲渡可能な猫のみ）
  document.getElementById('animalId').innerHTML =
    `<option value="">${t('common:messages.please_select', { ns: 'common' })}</option>` +
    selectableAnimals.map(a => `<option value="${a.id}">${escapeHtml(a.name)}</option>`).join('');

  document.getElementById('applicantId').innerHTML =
    `<option value="">${t('common:messages.please_select', { ns: 'common' })}</option>` +
    applicants.map(a => `<option value="${a.id}">${escapeHtml(a.name)}</option>`).join('');
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

// 譲渡記録を表示
function renderRecords() {
  // モバイル表示
  const mobileList = document.getElementById('mobileList');
  const desktopList = document.getElementById('desktopList');

  if (mobileList) mobileList.innerHTML = '';
  if (desktopList) desktopList.innerHTML = '';

  filteredRecords.forEach(record => {
    const animal = animals.find(a => a.id === record.animal_id);
    const applicant = applicants.find(a => a.id === record.applicant_id);
    const decisionBadgeHtml = getDecisionBadge(record.decision); // Returns HTML string

    // モバイル表示
    if (mobileList) {
      const card = cloneTemplate('tmpl-mobile-card');
      assertRequiredSelectors(
        card,
        [
          '.js-animal-name',
          '.js-applicant-name',
          '.js-decision',
          '.js-interview-date-container',
          '.js-interview-date',
          '.js-adoption-date-container',
          '.js-adoption-date',
          '.js-edit-btn',
          '.js-complete-btn',
        ],
        'adoption_records.tmpl-mobile-card'
      );

      requireSelector(card, '.js-animal-name', 'adoption_records.tmpl-mobile-card').textContent =
        animal ? animal.name : t('adoptions:records.labels.animal', { ns: 'adoptions' });
      requireSelector(card, '.js-applicant-name', 'adoption_records.tmpl-mobile-card').textContent =
        applicant ? applicant.name : t('adoptions:records.labels.applicant', { ns: 'adoptions' });
      requireSelector(card, '.js-decision', 'adoption_records.tmpl-mobile-card').innerHTML =
        decisionBadgeHtml;

      if (record.interview_date) {
        requireSelector(
          card,
          '.js-interview-date-container',
          'adoption_records.tmpl-mobile-card'
        ).classList.remove('hidden');
        requireSelector(
          card,
          '.js-interview-date',
          'adoption_records.tmpl-mobile-card'
        ).textContent = formatDate(record.interview_date);
      }

      if (record.adoption_date) {
        requireSelector(
          card,
          '.js-adoption-date-container',
          'adoption_records.tmpl-mobile-card'
        ).classList.remove('hidden');
        requireSelector(
          card,
          '.js-adoption-date',
          'adoption_records.tmpl-mobile-card'
        ).textContent = formatDate(record.adoption_date);
      }

      const editBtn = requireSelector(card, '.js-edit-btn', 'adoption_records.tmpl-mobile-card');
      editBtn.onclick = () => editRecord(record.id);

      if (!record.adoption_date && record.decision === 'approved') {
        const completeBtn = requireSelector(
          card,
          '.js-complete-btn',
          'adoption_records.tmpl-mobile-card'
        );
        completeBtn.classList.remove('hidden');
        completeBtn.onclick = () => openAdoptionModal(record.animal_id, record.applicant_id);
      }

      translateDynamicElement(card);
      mobileList.appendChild(card);
    }

    // デスクトップ表示
    if (desktopList) {
      const row = cloneTemplate('tmpl-desktop-row');
      assertRequiredSelectors(
        row,
        [
          '.js-animal-name',
          '.js-applicant-name',
          '.js-interview-date',
          '.js-decision',
          '.js-adoption-date',
          '.js-edit-btn',
          '.js-complete-btn',
        ],
        'adoption_records.tmpl-desktop-row'
      );

      requireSelector(row, '.js-animal-name', 'adoption_records.tmpl-desktop-row').textContent =
        animal ? animal.name : '-';
      requireSelector(row, '.js-applicant-name', 'adoption_records.tmpl-desktop-row').textContent =
        applicant ? applicant.name : '-';
      requireSelector(row, '.js-interview-date', 'adoption_records.tmpl-desktop-row').textContent =
        record.interview_date ? formatDate(record.interview_date) : '-';
      requireSelector(row, '.js-decision', 'adoption_records.tmpl-desktop-row').innerHTML =
        decisionBadgeHtml;
      requireSelector(row, '.js-adoption-date', 'adoption_records.tmpl-desktop-row').textContent =
        record.adoption_date ? formatDate(record.adoption_date) : '-';

      const editBtn = requireSelector(row, '.js-edit-btn', 'adoption_records.tmpl-desktop-row');
      editBtn.onclick = () => editRecord(record.id);

      if (!record.adoption_date && record.decision === 'approved') {
        const completeBtn = requireSelector(
          row,
          '.js-complete-btn',
          'adoption_records.tmpl-desktop-row'
        );
        completeBtn.classList.remove('hidden');
        completeBtn.onclick = () => openAdoptionModal(record.animal_id, record.applicant_id);
      }

      translateDynamicElement(row);
      desktopList.appendChild(row);
    }
  });
}

// 判定結果バッジ
function getDecisionBadge(decision) {
  const badges = {
    pending: `<span class="px-2 py-1 text-xs bg-yellow-100 text-yellow-800 rounded">${t('adoptions:records.decision.pending', { ns: 'adoptions' })}</span>`,
    approved: `<span class="px-2 py-1 text-xs bg-green-100 text-green-800 rounded">${t('adoptions:records.decision.approved', { ns: 'adoptions' })}</span>`,
    rejected: `<span class="px-2 py-1 text-xs bg-red-100 text-red-800 rounded">${t('adoptions:records.decision.rejected', { ns: 'adoptions' })}</span>`,
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
  const animalSelect = document.getElementById('animalId');

  form.reset();

  if (record) {
    title.textContent = t('adoptions:records.modal.title_edit', { ns: 'adoptions' });
    document.getElementById('recordId').value = record.id;
    // 既存記録編集時は、現在譲渡可能でなくても対象猫を選択できるようにする
    ensureAnimalOptionExists(animalSelect, record.animal_id);
    animalSelect.value = String(record.animal_id);
    document.getElementById('applicantId').value = record.applicant_id;
    document.getElementById('interviewDate').value = record.interview_date || '';
    document.getElementById('interviewNote').value = record.interview_note || '';
    document.getElementById('decision').value = record.decision || 'pending';
  } else {
    title.textContent = t('adoptions:records.modal.title_new', { ns: 'adoptions' });
    document.getElementById('recordId').value = '';
    animalSelect.value = '';
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
      throw new Error(
        t('adoptions:records.messages.error', {
          ns: 'adoptions',
          defaultValue: '保存に失敗しました',
        })
      );
    }

    closeInterviewModal();
    await loadData();
    alert(
      recordId
        ? t('adoptions:records.messages.updated', { ns: 'adoptions' })
        : t('adoptions:records.messages.registered', { ns: 'adoptions' })
    );
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
      throw new Error(
        t('adoptions:records.messages.error', {
          ns: 'adoptions',
          defaultValue: '譲渡完了処理に失敗しました',
        })
      );
    }

    closeAdoptionModal();
    await loadData();
    alert(t('adoptions:records.messages.adoption_completed', { ns: 'adoptions' }));
  } catch (error) {
    alert(error.message);
  }
}

// 注: formatDateはcommon.jsで定義済み

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

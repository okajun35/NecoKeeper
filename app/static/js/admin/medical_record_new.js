/**
 * 診療記録登録ページのJavaScript
 */

const isKiroweenMode = document.body && document.body.classList.contains('kiroween-mode');
const adminBasePath = window.ADMIN_BASE_PATH || window.__ADMIN_BASE_PATH__ || '/admin';

// ページ読み込み時の初期化
document.addEventListener('DOMContentLoaded', () => {
  applyKiroweenPlaceholders();
  loadAnimals();
  loadVets();
  loadMedicalActions();
  setupFormValidation();

  window.addEventListener('languageChanged', () => {
    applyKiroweenPlaceholders();
  });
});

function applyKiroweenPlaceholders() {
  const placeholderConfigs = [
    { id: 'animalId', english: 'Select a Cat' },
    { id: 'vetId', english: 'Select a Veterinarian' },
    { id: 'timeSlot', english: 'Select a Time Slot' },
    { id: 'medicalActionId', english: 'Select a Medical Action' },
  ];

  placeholderConfigs.forEach(config => setSelectPlaceholder(config));
}

function setSelectPlaceholder({ id, english }) {
  const select = document.getElementById(id);
  if (!select) return;

  const option = select.querySelector('option[value=""]');
  if (!option) return;

  if (!option.dataset.originalText) {
    option.dataset.originalText = option.textContent;
  }
  if (!option.dataset.originalI18nKey && option.getAttribute('data-i18n')) {
    option.dataset.originalI18nKey = option.getAttribute('data-i18n');
  }
  if (!option.dataset.originalI18nNs && option.getAttribute('data-i18n-ns')) {
    option.dataset.originalI18nNs = option.getAttribute('data-i18n-ns');
  }

  if (isKiroweenMode) {
    option.textContent = english;
    if (option.dataset.originalI18nKey) {
      option.removeAttribute('data-i18n');
    }
    if (option.dataset.originalI18nNs) {
      option.removeAttribute('data-i18n-ns');
    }
  } else {
    option.textContent = option.dataset.originalText || option.textContent;
    if (option.dataset.originalI18nKey) {
      option.setAttribute('data-i18n', option.dataset.originalI18nKey);
    }
    if (option.dataset.originalI18nNs) {
      option.setAttribute('data-i18n-ns', option.dataset.originalI18nNs);
    }
  }
}

// 猫一覧を読み込み（譲渡済みを除く）
async function loadAnimals() {
  try {
    const response = await fetch('/api/v1/animals?page=1&page_size=100', {
      headers: {
        Authorization: `Bearer ${getToken()}`,
      },
    });

    if (!response.ok) throw new Error(i18n.t('medical_records.messages.load_error'));

    const data = await response.json();
    const select = document.getElementById('animalId');

    // 譲渡済みの猫を除外
    const availableAnimals = data.items.filter(animal => animal.status !== '譲渡済み');

    availableAnimals.forEach(animal => {
      const option = document.createElement('option');
      option.value = animal.id;
      option.textContent = `${animal.name} (${animal.status})`;
      select.appendChild(option);
    });

    if (availableAnimals.length === 0) {
      const option = document.createElement('option');
      option.value = '';
      option.textContent = i18n.t('common.no_data');
      option.disabled = true;
      select.appendChild(option);
    }

    // 猫選択時のイベントリスナー
    select.addEventListener('change', handleAnimalChange);
  } catch (error) {
    console.error('Error loading animals:', error);
    showError(i18n.t('medical_records.messages.load_error'));
  }
}

// 猫選択時の処理
function handleAnimalChange(e) {
  const selectedOption = e.target.options[e.target.selectedIndex];
  const animalStatus = selectedOption.textContent.match(/\((.+)\)/)?.[1];

  if (animalStatus === '譲渡済み') {
    showError(i18n.t('medical_records.validation.animal_required'));
    e.target.value = '';
  }
}

// 獣医師一覧を読み込み
async function loadVets() {
  try {
    // TODO: ユーザー一覧APIが実装されたら修正
    // 現時点では手動入力またはスキップ
    console.log('Veterinarian list loading skipped (API not implemented)');

    // 仮のデータとして管理者を追加
    const select = document.getElementById('vetId');
    const option = document.createElement('option');
    option.value = '1';
    option.textContent = 'Administrator (Temporary)';
    select.appendChild(option);
  } catch (error) {
    console.error('Error loading vets:', error);
  }
}

// 診療行為一覧を読み込み
let medicalActionsData = [];

async function loadMedicalActions() {
  try {
    const response = await fetch(
      '/api/v1/medical-actions/active/list?target_date=' + new Date().toISOString().split('T')[0],
      {
        headers: {
          Authorization: `Bearer ${getToken()}`,
        },
      }
    );

    if (!response.ok) throw new Error(i18n.t('medical_records.messages.load_error'));

    const data = await response.json();
    medicalActionsData = data;
    const select = document.getElementById('medicalActionId');

    data.forEach(action => {
      const option = document.createElement('option');
      option.value = action.id;
      option.textContent = `${action.name} (${action.selling_price} ${action.currency})`;
      select.appendChild(option);
    });

    if (data.length === 0) {
      const option = document.createElement('option');
      option.value = '';
      option.textContent = i18n.t('common.no_data');
      option.disabled = true;
      select.appendChild(option);
    }

    // 診療行為選択時のイベントリスナー
    select.addEventListener('change', handleMedicalActionChange);
  } catch (error) {
    console.error('Error loading medical actions:', error);
    showError(i18n.t('medical_records.messages.load_error'));
  }
}

// 診療行為選択時の処理
function handleMedicalActionChange(e) {
  const actionId = parseInt(e.target.value);
  const dosageLabel = document.querySelector('label[for="dosage"]');

  if (actionId && dosageLabel) {
    const action = medicalActionsData.find(a => a.id === actionId);
    if (action && action.unit) {
      // 投薬単位を表示
      const dosageText = i18n.t('medical_records.labels.dosage');
      dosageLabel.innerHTML = `${dosageText} <span class="text-sm text-gray-500">(${action.unit})</span>`;
    } else {
      dosageLabel.textContent = i18n.t('medical_records.labels.dosage');
    }
  } else if (dosageLabel) {
    dosageLabel.textContent = i18n.t('medical_records.labels.dosage');
  }
}

// フォームバリデーション設定
function setupFormValidation() {
  const form = document.getElementById('medicalRecordForm');
  if (!form) return;

  form.addEventListener('submit', handleSubmit);
}

// フォーム送信処理
async function handleSubmit(e) {
  e.preventDefault();

  // 体重の値を取得（空文字列の場合はnull）
  const weightValue = document.getElementById('weight').value.trim();
  const weight = weightValue !== '' ? parseFloat(weightValue) : null;

  const formData = {
    animal_id: parseInt(document.getElementById('animalId').value),
    vet_id: parseInt(document.getElementById('vetId').value),
    date: document.getElementById('date').value,
    time_slot: document.getElementById('timeSlot').value || null,
    weight: weight,
    temperature: document.getElementById('temperature').value
      ? parseFloat(document.getElementById('temperature').value)
      : null,
    symptoms: document.getElementById('symptoms').value,
    comment: document.getElementById('comment').value || null,
    medical_action_id: document.getElementById('medicalActionId').value
      ? parseInt(document.getElementById('medicalActionId').value)
      : null,
    dosage: document.getElementById('dosage').value
      ? parseInt(document.getElementById('dosage').value)
      : null,
    other: document.getElementById('other').value || null,
  };

  try {
    const response = await fetch('/api/v1/medical-records', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${getToken()}`,
      },
      body: JSON.stringify(formData),
    });

    if (!response.ok) {
      const errorData = await response.json();
      // エラーメッセージを適切に抽出
      let errorMessage = i18n.t('medical_records.messages.save_error');

      if (errorData.detail) {
        if (typeof errorData.detail === 'string') {
          errorMessage = errorData.detail;
        } else if (Array.isArray(errorData.detail)) {
          // FastAPIのバリデーションエラーの場合
          errorMessage = errorData.detail.map(err => err.msg).join('\n');
        } else if (typeof errorData.detail === 'object') {
          errorMessage = JSON.stringify(errorData.detail);
        }
      }

      throw new Error(errorMessage);
    }

    // 成功したら一覧画面に遷移
    window.location.href = `${adminBasePath}/medical-records`;
  } catch (error) {
    console.error('Error submitting form:', error);
    showError(error.message || i18n.t('medical_records.messages.save_error'));
  }
}

// エラー表示
function showError(message) {
  alert(message);
}

// 注: getToken等はcommon.jsで定義済み

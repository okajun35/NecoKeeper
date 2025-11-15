/**
 * 診療記録登録ページのJavaScript
 */

// ページ読み込み時の初期化
document.addEventListener('DOMContentLoaded', () => {
  loadAnimals();
  loadVets();
  loadMedicalActions();
  setupFormValidation();
});

// 猫一覧を読み込み（譲渡済みを除く）
async function loadAnimals() {
  try {
    const response = await fetch('/api/v1/animals?page=1&page_size=100', {
      headers: {
        Authorization: `Bearer ${getToken()}`,
      },
    });

    if (!response.ok) throw new Error('猫一覧の取得に失敗しました');

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
      option.textContent = '診療可能な猫がいません';
      option.disabled = true;
      select.appendChild(option);
    }

    // 猫選択時のイベントリスナー
    select.addEventListener('change', handleAnimalChange);
  } catch (error) {
    console.error('Error loading animals:', error);
    showError('猫一覧の読み込みに失敗しました');
  }
}

// 猫選択時の処理
function handleAnimalChange(e) {
  const selectedOption = e.target.options[e.target.selectedIndex];
  const animalStatus = selectedOption.textContent.match(/\((.+)\)/)?.[1];

  if (animalStatus === '譲渡済み') {
    showError('譲渡済みの猫は診療記録を登録できません');
    e.target.value = '';
  }
}

// 獣医師一覧を読み込み
async function loadVets() {
  try {
    // TODO: ユーザー一覧APIが実装されたら修正
    // 現時点では手動入力またはスキップ
    console.log('獣医師一覧の読み込みはスキップされました（API未実装）');

    // 仮のデータとして管理者を追加
    const select = document.getElementById('vetId');
    const option = document.createElement('option');
    option.value = '1';
    option.textContent = '管理者（仮）';
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

    if (!response.ok) throw new Error('診療行為一覧の取得に失敗しました');

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
      option.textContent = '有効な診療行為がありません';
      option.disabled = true;
      select.appendChild(option);
    }

    // 診療行為選択時のイベントリスナー
    select.addEventListener('change', handleMedicalActionChange);
  } catch (error) {
    console.error('Error loading medical actions:', error);
    showError('診療行為一覧の読み込みに失敗しました');
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
      dosageLabel.innerHTML = `投薬回数 <span class="text-sm text-gray-500">(${action.unit})</span>`;
    } else {
      dosageLabel.textContent = '投薬回数';
    }
  } else if (dosageLabel) {
    dosageLabel.textContent = '投薬回数';
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

  const formData = {
    animal_id: parseInt(document.getElementById('animalId').value),
    vet_id: parseInt(document.getElementById('vetId').value),
    date: document.getElementById('date').value,
    time_slot: document.getElementById('timeSlot').value || null,
    weight: document.getElementById('weight').value
      ? parseFloat(document.getElementById('weight').value)
      : 0.0, // 体重を任意項目に（デフォルト0.0）
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
      const error = await response.json();
      throw new Error(error.detail || '登録に失敗しました');
    }

    // 成功したら一覧画面に遷移
    window.location.href = '/admin/medical-records';
  } catch (error) {
    console.error('Error submitting form:', error);
    showError(error.message);
  }
}

// エラー表示
function showError(message) {
  alert(message);
}

// トークン取得
function getToken() {
  return localStorage.getItem('access_token');
}

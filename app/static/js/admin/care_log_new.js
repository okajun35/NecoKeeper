/**
 * 世話記録新規登録 JavaScript
 * Context7参照: /bigskysoftware/htmx (Trust Score: 90.7)
 */

const API_BASE = '/api/v1';

// ページ読み込み時の処理
document.addEventListener('DOMContentLoaded', async () => {
  // 猫一覧を読み込み
  await loadAnimals();

  // フォーム送信イベント
  document.getElementById('care-log-form').addEventListener('submit', handleFormSubmit);

  // 本日の日付をデフォルト値に設定
  const today = new Date().toISOString().split('T')[0];
  document.getElementById('log_date').value = today;

  // URLパラメータから初期値を設定
  const params = new URLSearchParams(window.location.search);
  if (params.has('animal_id')) {
    document.getElementById('animal_id').value = params.get('animal_id');
  }
  if (params.has('date')) {
    document.getElementById('log_date').value = params.get('date');
  }
  if (params.has('time_slot')) {
    document.getElementById('time_slot').value = params.get('time_slot');
  }
});

/**
 * 猫一覧を読み込み
 */
async function loadAnimals() {
  try {
    const response = await apiRequest(`${API_BASE}/animals?page=1&page_size=1000`);
    const animals = response.items || [];

    const select = document.getElementById('animal_id');
    animals.forEach(animal => {
      const option = document.createElement('option');
      option.value = animal.id;
      option.textContent = animal.name;
      select.appendChild(option);
    });
  } catch (error) {
    console.error('Failed to load animals:', error);
    showAlert('猫一覧の読み込みに失敗しました', 'error');
  }
}

/**
 * フォーム送信処理
 */
async function handleFormSubmit(e) {
  e.preventDefault();

  try {
    const formData = {
      animal_id: parseInt(document.getElementById('animal_id').value),
      log_date: document.getElementById('log_date').value,
      time_slot: document.getElementById('time_slot').value,
      appetite: parseInt(document.getElementById('appetite').value),
      energy: parseInt(document.getElementById('energy').value),
      urination: document.getElementById('urination').checked,
      cleaning: document.getElementById('cleaning').checked,
      memo: document.getElementById('memo').value || null,
    };

    // バリデーション
    if (
      !formData.animal_id ||
      !formData.log_date ||
      !formData.time_slot ||
      !formData.appetite ||
      !formData.energy
    ) {
      showAlert('必須項目を入力してください', 'error');
      return;
    }

    // API呼び出し
    const response = await apiRequest(`${API_BASE}/care-logs`, {
      method: 'POST',
      body: JSON.stringify(formData),
    });

    showAlert('世話記録を登録しました', 'success');

    // 一覧ページにリダイレクト
    setTimeout(() => {
      window.location.href = '/admin/care-logs';
    }, 1500);
  } catch (error) {
    console.error('Failed to create care log:', error);
    showAlert('世話記録の登録に失敗しました', 'error');
  }
}

/**
 * API呼び出し
 */
async function apiRequest(url, options = {}) {
  const token = localStorage.getItem('access_token');

  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
      ...options.headers,
    },
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'API request failed');
  }

  return await response.json();
}

/**
 * アラート表示
 */
function showAlert(message, type = 'info') {
  const container = document.getElementById('alertContainer');

  const alert = document.createElement('div');
  alert.className = `px-4 py-3 rounded-lg text-white ${
    type === 'success' ? 'bg-green-500' : type === 'error' ? 'bg-red-500' : 'bg-blue-500'
  }`;
  alert.textContent = message;

  container.appendChild(alert);

  // 3秒後に削除
  setTimeout(() => {
    alert.remove();
  }, 3000);
}

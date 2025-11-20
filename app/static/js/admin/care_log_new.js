/**
 * 世話記録新規登録 JavaScript
 * Context7参照: /bigskysoftware/htmx (Trust Score: 90.7)
 */

// API_BASEはcommon.jsで定義されています

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
    const response = await apiRequest(`${API_BASE}/animals?page=1&page_size=100`);
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
    showToast(translate('messages.load_animals_failed', { ns: 'care_logs' }), 'error');
  }
}

/**
 * フォーム送信処理
 */
async function handleFormSubmit(e) {
  e.preventDefault();

  try {
    // ログインユーザー情報を取得（JWTトークンからメールアドレスを取得）
    const token = getToken();
    let recorderName = '管理者'; // デフォルト値
    if (token) {
      try {
        const payload = JSON.parse(atob(token.split('.')[1]));
        // JWTペイロードにemailやnameがあれば使用、なければデフォルト
        recorderName = payload.email || payload.name || '管理者';
      } catch (error) {
        console.warn('Failed to decode token, using default recorder name');
      }
    }

    const formData = {
      animal_id: parseInt(document.getElementById('animal_id').value),
      recorder_name: recorderName,
      log_date: document.getElementById('log_date').value,
      time_slot: document.getElementById('time_slot').value,
      appetite: parseInt(document.getElementById('appetite').value),
      energy: parseInt(document.getElementById('energy').value),
      urination: document.getElementById('urination').checked,
      cleaning: document.getElementById('cleaning').checked,
      memo: document.getElementById('memo').value || null,
    };

    // バリデーション（HTML5のrequired属性が優先されるため、ここでは追加チェックのみ）
    if (
      !formData.animal_id ||
      !formData.log_date ||
      !formData.time_slot ||
      !formData.appetite ||
      !formData.energy
    ) {
      showToast(translate('messages.required_fields', { ns: 'care_logs' }), 'error');
      return;
    }

    // API呼び出し
    const response = await apiRequest(`${API_BASE}/care-logs`, {
      method: 'POST',
      body: JSON.stringify(formData),
    });

    showToast(translate('messages.created', { ns: 'care_logs' }), 'success');

    // 一覧ページにリダイレクト
    setTimeout(() => {
      window.location.href = '/admin/care-logs';
    }, 1500);
  } catch (error) {
    console.error('Failed to create care log:', error);
    showToast(translate('messages.create_failed', { ns: 'care_logs' }), 'error');
  }
}

// ========================================
// 注: apiRequest, showAlert, showToast などは
// common.jsで定義されているグローバル関数を使用
// ========================================

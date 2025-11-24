/**
 * 世話記録編集 JavaScript
 */

// API_BASEはcommon.jsで定義されています

// ページ読み込み時の処理
document.addEventListener('DOMContentLoaded', async () => {
  const container = document.querySelector('[data-care-log-id]');
  if (!container) {
    console.error('Care log ID container not found');
    return;
  }
  const careLogId = container.dataset.careLogId;

  // 戻る・キャンセルボタンのリンク先を詳細ページに変更
  const backLinks = document.querySelectorAll('a[href="/admin/care-logs"]');
  backLinks.forEach(link => {
    link.href = `/admin/care-logs/${careLogId}`;
  });

  // 猫一覧を読み込み
  await loadAnimals();

  // 既存データを読み込み
  await loadCareLog(careLogId);

  // フォーム送信イベント
  document
    .getElementById('care-log-form')
    .addEventListener('submit', e => handleFormSubmit(e, careLogId));
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
 * 世話記録データを読み込み
 */
async function loadCareLog(id) {
  try {
    const data = await apiRequest(`${API_BASE}/care-logs/${id}`);

    document.getElementById('animal_id').value = data.animal_id;
    document.getElementById('log_date').value = data.log_date;
    document.getElementById('time_slot').value = data.time_slot;
    document.getElementById('appetite').value = data.appetite;
    document.getElementById('energy').value = data.energy;
    document.getElementById('urination').checked = data.urination;
    document.getElementById('cleaning').checked = data.cleaning;
    document.getElementById('memo').value = data.memo || '';
  } catch (error) {
    console.error('Failed to load care log:', error);
    showToast(translate('messages.load_failed', { ns: 'care_logs' }), 'error');
  }
}

/**
 * フォーム送信処理
 */
async function handleFormSubmit(e, id) {
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
      showToast(translate('messages.required_fields', { ns: 'care_logs' }), 'error');
      return;
    }

    // API呼び出し
    await apiRequest(`${API_BASE}/care-logs/${id}`, {
      method: 'PUT',
      body: JSON.stringify(formData),
    });

    // 成功メッセージをセッションストレージに保存して遷移
    sessionStorage.setItem('careLogUpdateSuccess', 'true');
    window.location.href = `/admin/care-logs/${id}`;
  } catch (error) {
    console.error('Failed to update care log:', error);
    showToast(translate('messages.update_failed', { ns: 'care_logs' }), 'error');
  }
}

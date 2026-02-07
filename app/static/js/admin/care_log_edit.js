/**
 * 世話記録編集 JavaScript
 */

// API_BASEはcommon.jsで定義されています
const adminBasePath = window.ADMIN_BASE_PATH || window.__ADMIN_BASE_PATH__ || '/admin';

// ページ読み込み時の処理
document.addEventListener('DOMContentLoaded', async () => {
  const container = document.querySelector('[data-care-log-id]');
  if (!container) {
    console.error('Care log ID container not found');
    return;
  }
  const careLogId = container.dataset.careLogId;

  // 戻る・キャンセルボタンのリンク先を詳細ページに変更
  const backLinks = document.querySelectorAll(`a[href="${adminBasePath}/care-logs"]`);
  backLinks.forEach(link => {
    link.href = `${adminBasePath}/care-logs/${careLogId}`;
  });

  // 猫一覧を読み込み
  await loadAnimals();

  // 排便・便状態 UI
  setupDefecationAndStoolConditionUI();

  // 便状態ヘルプモーダル
  setupStoolConditionHelpModal();

  // 既存データを読み込み
  await loadCareLog(careLogId);

  // フォーム送信イベント
  document
    .getElementById('care-log-form')
    .addEventListener('submit', e => handleFormSubmit(e, careLogId));
});

function setupStoolConditionHelpModal() {
  const modal = document.getElementById('stoolConditionHelpModal');
  const openBtn = document.getElementById('stoolConditionHelpOpen');
  const closeBtn = document.getElementById('stoolConditionHelpClose');
  const backdrop = document.getElementById('stoolConditionHelpBackdrop');

  if (!modal || !openBtn || !closeBtn || !backdrop) return;

  const open = () => modal.classList.remove('hidden');
  const close = () => modal.classList.add('hidden');

  openBtn.addEventListener('click', open);
  closeBtn.addEventListener('click', close);
  backdrop.addEventListener('click', close);

  document.addEventListener('keydown', e => {
    if (e.key === 'Escape' && !modal.classList.contains('hidden')) {
      close();
    }
  });
}

function setSelectedButton(buttons, selectedButton) {
  buttons.forEach(btn => {
    if (btn === selectedButton) {
      btn.classList.add('selected', 'border-brand-primary', 'bg-brand-primary-light', 'text-brand-primary-dark');
      btn.classList.remove('border-gray-300');
    } else {
      btn.classList.remove('selected', 'border-brand-primary', 'bg-brand-primary-light', 'text-brand-primary-dark');
      btn.classList.add('border-gray-300');
    }
  });
}

function clearSelectedButtons(buttons) {
  buttons.forEach(btn => {
    btn.classList.remove('selected', 'border-brand-primary', 'bg-brand-primary-light', 'text-brand-primary-dark');
    btn.classList.add('border-gray-300');
  });
}

function updateStoolConditionVisibility() {
  const defecationInput = document.getElementById('defecation');
  const section = document.getElementById('stoolConditionSection');
  const stoolInput = document.getElementById('stoolCondition');
  if (!defecationInput || !section || !stoolInput) return;

  const isYes = defecationInput.value === 'true';
  section.classList.toggle('hidden', !isYes);

  if (!isYes) {
    stoolInput.value = '';
    clearSelectedButtons(document.querySelectorAll('.stool-condition-btn'));
  }
}

function setupDefecationAndStoolConditionUI() {
  const defecationInput = document.getElementById('defecation');
  const stoolInput = document.getElementById('stoolCondition');
  if (!defecationInput || !stoolInput) return;

  const defecationButtons = Array.from(document.querySelectorAll('.defecation-btn'));
  defecationButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      defecationInput.value = btn.dataset.value;
      setSelectedButton(defecationButtons, btn);
      updateStoolConditionVisibility();
    });
  });

  const stoolButtons = Array.from(document.querySelectorAll('.stool-condition-btn'));
  stoolButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      stoolInput.value = btn.dataset.value;
      setSelectedButton(stoolButtons, btn);
    });
  });

  updateStoolConditionVisibility();
}

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

    // 排便/便状態
    const defecationInput = document.getElementById('defecation');
    const stoolInput = document.getElementById('stoolCondition');
    if (defecationInput) {
      defecationInput.value = typeof data.defecation === 'boolean' ? String(data.defecation) : '';
      const defBtn = document.querySelector(
        `.defecation-btn[data-value="${defecationInput.value}"]`
      );
      if (defBtn)
        setSelectedButton(Array.from(document.querySelectorAll('.defecation-btn')), defBtn);
    }

    if (stoolInput) {
      stoolInput.value = data.stool_condition ? String(data.stool_condition) : '';
      const stoolBtn = stoolInput.value
        ? document.querySelector(`.stool-condition-btn[data-value="${stoolInput.value}"]`)
        : null;
      if (stoolBtn)
        setSelectedButton(Array.from(document.querySelectorAll('.stool-condition-btn')), stoolBtn);
    }

    updateStoolConditionVisibility();
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
      appetite: parseFloat(document.getElementById('appetite').value),
      energy: parseInt(document.getElementById('energy').value),
      urination: document.getElementById('urination').checked,
      cleaning: document.getElementById('cleaning').checked,
      memo: document.getElementById('memo').value || null,
    };

    const defecationRaw = document.getElementById('defecation')?.value;
    const stoolConditionRaw = document.getElementById('stoolCondition')?.value;

    // バリデーション
    if (
      !formData.animal_id ||
      !formData.log_date ||
      !formData.time_slot ||
      Number.isNaN(formData.appetite) ||
      !formData.energy ||
      (defecationRaw !== 'true' && defecationRaw !== 'false')
    ) {
      showToast(translate('messages.required_fields', { ns: 'care_logs' }), 'error');
      return;
    }

    formData.defecation = defecationRaw === 'true';

    // 条件付き必須: defecation=true の場合は stool_condition 必須
    if (formData.defecation) {
      if (!stoolConditionRaw || stoolConditionRaw.trim() === '') {
        showToast(translate('messages.required_fields', { ns: 'care_logs' }), 'error');
        return;
      }
      formData.stool_condition = parseInt(stoolConditionRaw);
    } else {
      formData.stool_condition = null;
    }

    // API呼び出し
    await apiRequest(`${API_BASE}/care-logs/${id}`, {
      method: 'PUT',
      body: JSON.stringify(formData),
    });

    // 成功メッセージをセッションストレージに保存して遷移
    sessionStorage.setItem('careLogUpdateSuccess', 'true');
    window.location.href = `${adminBasePath}/care-logs/${id}`;
  } catch (error) {
    console.error('Failed to update care log:', error);
    showToast(translate('messages.update_failed', { ns: 'care_logs' }), 'error');
  }
}

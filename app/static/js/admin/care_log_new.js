/**
 * 世話記録新規登録 JavaScript
 * Context7参照: /bigskysoftware/htmx (Trust Score: 90.7)
 */

// API_BASEはcommon.jsで定義されています
const adminBasePath = window.ADMIN_BASE_PATH || window.__ADMIN_BASE_PATH__ || '/admin';

// ページ読み込み時の処理
document.addEventListener('DOMContentLoaded', async () => {
  // 猫一覧を読み込み
  await loadAnimals();

  // 排便・便状態 UI
  setupDefecationAndStoolConditionUI();

  // 便状態ヘルプモーダル
  setupStoolConditionHelpModal();

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
      appetite: parseFloat(document.getElementById('appetite').value),
      energy: parseInt(document.getElementById('energy').value),
      urination: document.getElementById('urination').checked,
      cleaning: document.getElementById('cleaning').checked,
      memo: document.getElementById('memo').value || null,
    };

    const defecationRaw = document.getElementById('defecation')?.value;
    const stoolConditionRaw = document.getElementById('stoolCondition')?.value;

    // バリデーション（HTML5のrequired属性が優先されるため、ここでは追加チェックのみ）
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
    const response = await apiRequest(`${API_BASE}/care-logs`, {
      method: 'POST',
      body: JSON.stringify(formData),
    });

    showToast(translate('messages.created', { ns: 'care_logs' }), 'success');

    // 一覧ページにリダイレクト
    setTimeout(() => {
      window.location.href = `${adminBasePath}/care-logs`;
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

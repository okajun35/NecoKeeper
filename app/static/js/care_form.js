/**
 * 世話記録入力フォームのJavaScript
 *
 * 猫の世話記録を入力するフォームの動作を制御します。
 * オフライン対応、前回値コピー、バリデーションなどの機能を提供します。
 */

// URLからanimal_idを取得
const urlParams = new URLSearchParams(window.location.search);
const animalId = urlParams.get('animal_id');
const logId = urlParams.get('log_id');
const isEditMode = Boolean(logId);
const presetTimeSlot = urlParams.get('time_slot');

const isKiroweenMode = document.body && document.body.classList.contains('kiroween-mode');
const DEFAULT_IMAGE_PLACEHOLDER = isKiroweenMode
  ? '/static/icons/halloween_logo_2.webp'
  : '/static/images/default.svg';
const OFFLINE_SAVE_FALLBACK = isKiroweenMode
  ? 'Saved offline. It will auto-sync once you are back online.'
  : '記録を一時保存しました（オンライン時に自動同期されます）';
const fallbackText = (english, japanese) => (isKiroweenMode ? english : japanese);

if (!animalId) {
  showError(fallbackText('Animal ID is missing.', '猫のIDが指定されていません'));
}

// 記録日に今日の日付を設定
document.getElementById('logDate').value = getTodayString();

const CARE_NAMESPACE = 'care';
const PAGE_TITLE_SUFFIX = ' - NecoKeeper';
const REQUIRED_FIELD_CONFIG = [
  { id: 'logDate', key: 'log_date' },
  { id: 'timeSlot', key: 'time_slot' },
  { id: 'appetite', key: 'appetite' },
  { id: 'energy', key: 'energy' },
  { id: 'vomiting', key: 'vomiting' },
  { id: 'urination', key: 'urination' },
  { id: 'defecation', key: 'defecation' },
  { id: 'cleaning', key: 'cleaning' },
  { id: 'volunteer', key: 'recorder' },
];
const CARE_IMAGE_ALLOWED_MIME_TYPES = ['image/jpeg', 'image/png', 'image/webp'];
const CARE_IMAGE_HEIC_MIME_TYPES = ['image/heic', 'image/heif'];

function renderCareTemplate(template, options = {}) {
  if (typeof template !== 'string') return template;
  if (!template.includes('{{')) return template;
  return template.replace(/{{(\w+)}}/g, (_, k) => options[k] ?? '');
}

function translateCare(key, fallback = '', options = {}) {
  const namespacedKey = `${CARE_NAMESPACE}:${key}`;
  const shouldForceFallback = isKiroweenMode && typeof fallback === 'string' && fallback.length > 0;

  if (!shouldForceFallback && window.i18n && typeof window.i18n.t === 'function') {
    const translation = window.i18n.t(namespacedKey, options);
    if (translation && translation !== namespacedKey) {
      return translation;
    }
  }

  if (typeof fallback === 'string') {
    return renderCareTemplate(fallback, options) || key;
  }

  return fallback || key;
}

function updatePageTitle() {
  const titleKey = isEditMode ? 'title_edit' : 'title';
  const fallbackTitle = isEditMode ? '世話記録を編集' : '世話記録入力';
  const localizedTitle = translateCare(titleKey, isKiroweenMode ? 'Care Log Edit' : fallbackTitle);
  document.title = `${localizedTitle}${PAGE_TITLE_SUFFIX}`;
}

function disableImmutableFields() {
  // 動物はUI上で選択不可のままなので何もしない
  const timeSlotButtons = document.querySelectorAll('.time-slot-btn');
  const timeSlotInput = document.getElementById('timeSlot');

  timeSlotButtons.forEach(btn => {
    btn.disabled = true;
    btn.classList.add('opacity-60', 'cursor-not-allowed');
  });

  if (timeSlotInput) {
    timeSlotInput.setAttribute('readonly', 'readonly');
  }
}

function showToast(message, subMessage = '') {
  const toast = document.getElementById('successToast');
  const text = document.getElementById('successToastText');
  const subText = document.getElementById('successToastSubText');
  if (!toast || !text) return;

  text.textContent = message;
  if (subText) {
    subText.textContent = subMessage;
    subText.classList.toggle('hidden', !subMessage);
  }

  toast.classList.remove('hidden');
  toast.dataset.visible = 'true';

  clearTimeout(showToast.timeoutId);
  showToast.timeoutId = setTimeout(() => {
    hideToast();
  }, 2500);
}

function hideToast() {
  const toast = document.getElementById('successToast');
  if (!toast) return;
  toast.classList.add('hidden');
  toast.dataset.visible = 'false';
}

function getFieldContainer(fieldId) {
  return document.querySelector(`[data-field="${fieldId}"]`);
}

function ensureFieldErrorElement(container) {
  if (!container) return null;
  let errorEl = container.querySelector('.field-error-message');
  if (!errorEl) {
    errorEl = document.createElement('p');
    errorEl.className = 'field-error-message mt-2 text-sm text-red-600 hidden';
    errorEl.setAttribute('role', 'alert');
    container.appendChild(errorEl);
  }
  return errorEl;
}

function setFieldErrorState(fieldId, hasError, message = '') {
  const container = getFieldContainer(fieldId);
  const targetInput = document.getElementById(fieldId);

  const errorClasses = ['ring-2', 'ring-red-300', 'ring-offset-2'];
  if (container) {
    errorClasses.forEach(cls => {
      if (hasError) {
        container.classList.add(cls);
      } else {
        container.classList.remove(cls);
      }
    });

    const errorEl = ensureFieldErrorElement(container);
    if (errorEl) {
      errorEl.textContent = hasError ? message : '';
      errorEl.classList.toggle('hidden', !hasError);
    }
  }

  if (targetInput) {
    if (hasError) {
      targetInput.setAttribute('aria-invalid', 'true');
    } else {
      targetInput.removeAttribute('aria-invalid');
    }
  }
}

function clearAllFieldErrors() {
  REQUIRED_FIELD_CONFIG.forEach(field => setFieldErrorState(field.id, false));
  setFieldErrorState('stoolCondition', false);
}

function updateStoolConditionVisibility() {
  const defecationInput = document.getElementById('defecation');
  const section = document.getElementById('stoolConditionSection');
  const stoolInput = document.getElementById('stoolCondition');

  if (!defecationInput || !section || !stoolInput) return;

  const isDefecationYes = defecationInput.value === 'true';
  section.classList.toggle('hidden', !isDefecationYes);

  if (!isDefecationYes) {
    // defecation=false の場合は stool_condition を必ずクリア
    stoolInput.value = '';
    document.querySelectorAll('.stool-condition-btn.selected').forEach(btn => {
      btn.classList.remove('selected', 'border-brand-primary', 'bg-brand-primary', 'text-white');
      btn.classList.add('border-gray-300', 'bg-bg-base', 'text-text-main');
      btn.style.backgroundColor = 'var(--color-bg-base)';
      btn.style.borderColor = 'var(--color-border)';
      btn.style.color = 'var(--color-text-main)';
    });
    setFieldErrorState('stoolCondition', false);
  }
}

function setupStoolConditionHelpModal() {
  const modal = document.getElementById('stoolConditionHelpModal');
  const openBtn = document.getElementById('stoolConditionHelpOpen');
  const closeBtn = document.getElementById('stoolConditionHelpClose');
  const backdrop = document.getElementById('stoolConditionHelpBackdrop');

  if (!modal || !openBtn || !closeBtn || !backdrop) return;

  const open = () => {
    modal.classList.remove('hidden');
  };

  const close = () => {
    modal.classList.add('hidden');
  };

  openBtn.addEventListener('click', open);
  closeBtn.addEventListener('click', close);
  backdrop.addEventListener('click', close);

  document.addEventListener('keydown', e => {
    if (e.key === 'Escape' && !modal.classList.contains('hidden')) {
      close();
    }
  });
}

function focusField(fieldId) {
  const container = getFieldContainer(fieldId);
  if (!container) return;

  const focusTarget = container.querySelector(
    'input:not([type="hidden"]):not([disabled]), select:not([disabled]), textarea:not([disabled]), button:not([disabled])'
  );

  if (focusTarget) {
    focusTarget.focus();
    if (typeof focusTarget.scrollIntoView === 'function') {
      focusTarget.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
  } else if (typeof container.scrollIntoView === 'function') {
    container.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }
}

function validateForm() {
  const missingFields = [];

  REQUIRED_FIELD_CONFIG.forEach(field => {
    const element = document.getElementById(field.id);
    if (!element) return;

    const rawValue = typeof element.value === 'string' ? element.value.trim() : element.value;
    const isMissing = rawValue === '' || rawValue === null || typeof rawValue === 'undefined';

    if (isMissing) {
      const fieldLabel = translateCare(field.key, field.key);
      const fieldMessage = translateCare(
        'validation_required',
        fallbackText('{{field}} is required.', '{{field}}は必須です'),
        {
          field: fieldLabel,
        }
      );
      missingFields.push({ id: field.id, label: fieldLabel, message: fieldMessage });
      setFieldErrorState(field.id, true, fieldMessage);
    } else {
      setFieldErrorState(field.id, false);
    }
  });

  if (missingFields.length > 0) {
    const summaryMessageParts = [
      translateCare(
        'save_validation_error',
        fallbackText(
          'Some fields are missing or invalid. Please review the highlighted sections.',
          '未入力または不正な項目があります。赤枠の欄を確認してください。'
        )
      ),
      translateCare(
        'validation_missing_fields',
        fallbackText(
          'Missing required fields: {{fields}}',
          '以下の必須項目が未入力です: {{fields}}'
        ),
        {
          fields: missingFields.map(field => field.label).join(', '),
        }
      ),
    ];

    return {
      isValid: false,
      message: summaryMessageParts.join(' '),
      firstInvalidFieldId: missingFields[0].id,
    };
  }

  // 条件付き必須: defecation=true の場合は stool_condition 必須
  const defecationValue = document.getElementById('defecation')?.value;
  const stoolConditionValue = document.getElementById('stoolCondition')?.value;
  if (defecationValue === 'true' && (!stoolConditionValue || stoolConditionValue.trim() === '')) {
    const fieldLabel = translateCare(
      'stool_condition',
      isKiroweenMode ? 'Stool condition' : '便の状態'
    );
    const fieldMessage = translateCare(
      'validation_required',
      fallbackText('{{field}} is required.', '{{field}}は必須です'),
      {
        field: fieldLabel,
      }
    );
    setFieldErrorState('stoolCondition', true, fieldMessage);
    return {
      isValid: false,
      message: translateCare(
        'save_validation_error',
        fallbackText(
          'Some fields are missing or invalid. Please review the highlighted sections.',
          '未入力または不正な項目があります。赤枠の欄を確認してください。'
        )
      ),
      firstInvalidFieldId: 'stoolCondition',
    };
  }

  // defecation=false の場合は stool_condition は送らない（UI側でクリア済みだが念のため）
  if (defecationValue === 'false' && stoolConditionValue && stoolConditionValue.trim() !== '') {
    const message = translateCare(
      'validation_invalid_combo',
      fallbackText(
        'Stool condition must be empty when defecation is No.',
        '排便が「なし」の場合、便の状態は選択できません。'
      )
    );
    setFieldErrorState('stoolCondition', true, message);
    return { isValid: false, message, firstInvalidFieldId: 'stoolCondition' };
  }

  return { isValid: true, message: '' };
}

function getCareImageInput() {
  return document.getElementById('careImage');
}

function getSelectedCareImage() {
  const input = getCareImageInput();
  if (!input || !input.files || input.files.length === 0) {
    return null;
  }
  return input.files[0];
}

function getCareImageReceiveMaxSizeBytes() {
  const form = document.getElementById('careForm');
  const maxSizeMb = Number(form?.dataset?.imageReceiveMaxSizeMb || '10');
  if (Number.isNaN(maxSizeMb) || maxSizeMb <= 0) {
    return 10 * 1024 * 1024;
  }
  return maxSizeMb * 1024 * 1024;
}

function clearCareImageSelection() {
  const input = getCareImageInput();
  const previewContainer = document.getElementById('careImagePreviewContainer');
  const preview = document.getElementById('careImagePreview');
  const selectedFileName = document.getElementById('careImageSelectedFileName');

  if (input) {
    input.value = '';
  }
  if (preview) {
    preview.src = '';
  }
  if (previewContainer) {
    previewContainer.classList.add('hidden');
  }
  if (selectedFileName) {
    selectedFileName.textContent = '';
    selectedFileName.classList.add('hidden');
  }
}

function updateCareImagePreview() {
  const image = getSelectedCareImage();
  const previewContainer = document.getElementById('careImagePreviewContainer');
  const preview = document.getElementById('careImagePreview');
  const selectedFileName = document.getElementById('careImageSelectedFileName');

  if (!previewContainer || !preview) {
    return;
  }

  if (!image) {
    preview.src = '';
    previewContainer.classList.add('hidden');
    if (selectedFileName) {
      selectedFileName.textContent = '';
      selectedFileName.classList.add('hidden');
    }
    return;
  }

  if (selectedFileName) {
    selectedFileName.textContent = image.name;
    selectedFileName.classList.remove('hidden');
  }

  const objectUrl = URL.createObjectURL(image);
  preview.onload = () => URL.revokeObjectURL(objectUrl);
  preview.src = objectUrl;
  previewContainer.classList.remove('hidden');
}

function validateCareImage(imageFile) {
  if (!imageFile) {
    return { isValid: true };
  }

  const fileType = (imageFile.type || '').toLowerCase();
  if (CARE_IMAGE_HEIC_MIME_TYPES.includes(fileType)) {
    return {
      isValid: false,
      message: fallbackText(
        'HEIC is not supported. Please re-submit as JPEG.',
        'HEICは非対応です。JPEGで再投稿してください。'
      ),
    };
  }

  if (!CARE_IMAGE_ALLOWED_MIME_TYPES.includes(fileType)) {
    return {
      isValid: false,
      message: fallbackText(
        'Only JPEG/PNG/WebP images are supported.',
        '画像は JPEG / PNG / WebP のみ対応しています。'
      ),
    };
  }

  const maxSizeBytes = getCareImageReceiveMaxSizeBytes();
  if (imageFile.size > maxSizeBytes) {
    const maxSizeMb = (maxSizeBytes / (1024 * 1024)).toFixed(1);
    return {
      isValid: false,
      message: fallbackText(
        `Image file is too large (max ${maxSizeMb}MB).`,
        `画像サイズが大きすぎます（最大 ${maxSizeMb}MB）。`
      ),
    };
  }

  return { isValid: true };
}

function buildMultipartPayload(formData) {
  const payload = new FormData();
  Object.entries(formData).forEach(([key, value]) => {
    if (value === null || typeof value === 'undefined') {
      return;
    }
    payload.append(key, String(value));
  });
  return payload;
}

function setSubmitButtonState(isLoading) {
  const submitBtn = document.getElementById('submitBtn');
  if (!submitBtn) return;

  submitBtn.disabled = isLoading;
  submitBtn.textContent = isLoading
    ? translateCare('saving', fallbackText('Saving...', '保存中...'))
    : translateCare('save', fallbackText('Save', '保存'));
}

/**
 * 猫情報を取得して表示
 */
async function loadAnimalInfo() {
  try {
    const response = await fetch(`${API_BASE}/animals/${animalId}`);
    if (!response.ok)
      throw new Error(
        fallbackText('Failed to load cat information.', '猫情報の取得に失敗しました')
      );

    const animal = await response.json();
    document.getElementById('animalName').textContent =
      animal.name || fallbackText('No name set', '名前未設定');

    // 画像のフォールバック処理（photoパスに/media/プレフィックスを追加）
    const photoElement = document.getElementById('animalPhoto');
    let photoUrl = DEFAULT_IMAGE_PLACEHOLDER;
    if (animal.photo && animal.photo.trim() !== '') {
      photoUrl = animal.photo.startsWith('/') ? animal.photo : `/media/${animal.photo}`;
    }
    photoElement.src = photoUrl;
    photoElement.onerror = function () {
      this.onerror = null; // 無限ループ防止
      this.src = DEFAULT_IMAGE_PLACEHOLDER;
    };
  } catch (error) {
    showError(error.message);
  }
}

async function loadCareLogForEdit() {
  if (!isEditMode || !logId) return;
  try {
    const response = await fetch(`${API_BASE}/care-logs/animal/${animalId}/${logId}`);
    if (!response.ok) {
      throw new Error(
        translateCare(
          'error_api_failed',
          fallbackText('Failed to load the record.', '記録の取得に失敗しました')
        )
      );
    }

    const log = await response.json();

    // 記録日
    const logDateInput = document.getElementById('logDate');
    if (logDateInput && log.log_date) {
      logDateInput.value = log.log_date;
    }

    // 時点（選択固定）
    if (log.time_slot) {
      const timeSlotBtn = document.querySelector(`.time-slot-btn[data-value="${log.time_slot}"]`);
      if (timeSlotBtn) timeSlotBtn.click();
    }

    // 食欲/元気
    if (log.appetite !== null && log.appetite !== undefined) {
      const btn = document.querySelector(`.appetite-btn[data-value="${log.appetite}"]`);
      if (btn) btn.click();
    }
    if (log.energy) {
      const btn = document.querySelector(`.energy-btn[data-value="${log.energy}"]`);
      if (btn) btn.click();
    }

    // 嘔吐/排尿/排便/便状態
    if (typeof log.vomiting === 'boolean') {
      const btn = document.querySelector(`.vomiting-btn[data-value="${log.vomiting}"]`);
      if (btn) btn.click();
    }
    if (typeof log.urination === 'boolean') {
      const btn = document.querySelector(`.urination-btn[data-value="${log.urination}"]`);
      if (btn) btn.click();
    }
    if (typeof log.defecation === 'boolean') {
      const btn = document.querySelector(`.defecation-btn[data-value="${log.defecation}"]`);
      if (btn) btn.click();
    }
    if (log.defecation === true && log.stool_condition) {
      const btn = document.querySelector(
        `.stool-condition-btn[data-value="${log.stool_condition}"]`
      );
      if (btn) btn.click();
    }

    // 清掃
    if (typeof log.cleaning === 'boolean') {
      const btn = document.querySelector(`.cleaning-btn[data-value="${log.cleaning}"]`);
      if (btn) btn.click();
    }

    // メモ
    const memoEl = document.getElementById('memo');
    if (memoEl) {
      memoEl.value = log.memo || '';
    }

    // 記録者
    const volunteerSelect = document.getElementById('volunteer');
    if (volunteerSelect && log.recorder_id) {
      volunteerSelect.value = String(log.recorder_id);
    }

    // UI 固定
    disableImmutableFields();
    const copyBtn = document.getElementById('copyLastBtn');
    if (copyBtn) {
      copyBtn.disabled = true;
      copyBtn.classList.add('opacity-60', 'cursor-not-allowed');
    }
  } catch (error) {
    showError(
      error?.message || fallbackText('Failed to load the record.', '記録の取得に失敗しました')
    );
  }
}

/**
 * ボランティア一覧を取得してセレクトボックスに設定
 */
async function loadVolunteers() {
  try {
    const response = await fetch(`${API_BASE}/volunteers`);
    if (!response.ok)
      throw new Error(
        fallbackText('Failed to load volunteer list.', 'ボランティア一覧の取得に失敗しました')
      );

    const volunteers = await response.json();
    const select = document.getElementById('volunteer');

    volunteers.forEach(volunteer => {
      const option = document.createElement('option');
      option.value = volunteer.id;
      option.textContent = volunteer.name;
      select.appendChild(option);
    });
  } catch (error) {
    showError(error.message);
  }
}

/**
 * ボタングループの選択処理を設定
 * @param {string} className - ボタンのクラス名
 * @param {string} inputId - 対応するhidden inputのID
 */
function setupButtonGroup(className, inputId) {
  const buttons = document.querySelectorAll(`.${className}`);
  const input = document.getElementById(inputId);

  buttons.forEach(button => {
    button.addEventListener('click', () => {
      // 他のボタンの選択を解除
      buttons.forEach(btn => {
        btn.classList.remove('selected', 'border-brand-primary', 'bg-brand-primary', 'text-white');
        btn.classList.add('border-gray-300', 'bg-bg-base', 'text-text-main');

        // Inline styles override classes, so we must update them too
        btn.style.backgroundColor = 'var(--color-bg-base)';
        btn.style.borderColor = 'var(--color-border)';
        btn.style.color = 'var(--color-text-main)';
      });

      // クリックされたボタンを選択状態に
      button.classList.add('selected', 'border-brand-primary', 'bg-brand-primary', 'text-white');
      button.classList.remove('border-gray-300', 'bg-bg-base', 'text-text-main');

      // Update inline styles for selection
      button.style.backgroundColor = 'var(--color-brand-primary)';
      button.style.borderColor = 'var(--color-brand-primary)';
      button.style.color = '#ffffff';

      // hidden inputに値を設定
      input.value = button.dataset.value;

      setFieldErrorState(inputId, false);
    });
  });
}

/**
 * 前回値をコピー
 */
async function copyLastValues() {
  try {
    const response = await fetch(`${API_BASE}/care-logs/latest/${animalId}`);
    if (!response.ok) {
      if (response.status === 404) {
        showSuccess(
          translateCare(
            'copy_no_data',
            fallbackText(
              'No previous records found (first entry).',
              '前回の記録がありません（初回記録です）'
            )
          )
        );
        return;
      }
      throw new Error(
        translateCare(
          'copy_failure',
          fallbackText('Failed to load previous values.', '前回値の取得に失敗しました')
        )
      );
    }

    const lastLog = await response.json();

    if (!lastLog) {
      showSuccess(
        translateCare(
          'copy_no_data',
          fallbackText(
            'No previous records found (first entry).',
            '前回の記録がありません（初回記録です）'
          )
        )
      );
      return;
    }

    // 各フィールドに値を設定
    // 記録日は今日の日付を維持（コピーしない）

    if (lastLog.time_slot) {
      const timeSlotBtn = document.querySelector(
        `.time-slot-btn[data-value="${lastLog.time_slot}"]`
      );
      if (timeSlotBtn) timeSlotBtn.click();
    }

    if (lastLog.appetite !== null && lastLog.appetite !== undefined) {
      const appetiteBtn = document.querySelector(`.appetite-btn[data-value="${lastLog.appetite}"]`);
      if (appetiteBtn) appetiteBtn.click();
    }

    if (lastLog.energy) {
      const energyBtn = document.querySelector(`.energy-btn[data-value="${lastLog.energy}"]`);
      if (energyBtn) energyBtn.click();
    }

    if (typeof lastLog.vomiting === 'boolean') {
      const vomitingBtn = document.querySelector(`.vomiting-btn[data-value="${lastLog.vomiting}"]`);
      if (vomitingBtn) vomitingBtn.click();
    }

    if (typeof lastLog.urination === 'boolean') {
      const urinationBtn = document.querySelector(
        `.urination-btn[data-value="${lastLog.urination}"]`
      );
      if (urinationBtn) urinationBtn.click();
    }

    if (typeof lastLog.defecation === 'boolean') {
      const defecationBtn = document.querySelector(
        `.defecation-btn[data-value="${lastLog.defecation}"]`
      );
      if (defecationBtn) defecationBtn.click();
    }

    if (lastLog.defecation === true && lastLog.stool_condition) {
      const stoolBtn = document.querySelector(
        `.stool-condition-btn[data-value="${lastLog.stool_condition}"]`
      );
      if (stoolBtn) stoolBtn.click();
    }

    if (typeof lastLog.cleaning === 'boolean') {
      const cleaningBtn = document.querySelector(`.cleaning-btn[data-value="${lastLog.cleaning}"]`);
      if (cleaningBtn) cleaningBtn.click();
    }

    // メモはコピーしない（毎回異なる可能性が高いため）

    showSuccess(
      translateCare(
        'copy_success',
        fallbackText('Copied previous values.', '前回値をコピーしました')
      )
    );
  } catch (error) {
    const message =
      error?.message ||
      translateCare(
        'copy_failure',
        fallbackText('Failed to load previous values.', '前回値の取得に失敗しました')
      );
    showError(message);
  }
}

/**
 * フォームをリセット
 */
function resetForm() {
  document.getElementById('careForm').reset();
  // 記録日を今日の日付に戻す
  document.getElementById('logDate').value = getTodayString();
  // ボタンの選択状態をクリア
  document.querySelectorAll('.selected').forEach(btn => {
    btn.classList.remove('selected', 'border-brand-primary', 'bg-brand-primary', 'text-white');
    btn.classList.add('border-gray-300', 'bg-bg-base', 'text-text-main');
    btn.style.backgroundColor = 'var(--color-bg-base)';
    btn.style.borderColor = 'var(--color-border)';
    btn.style.color = 'var(--color-text-main)';
  });
  // hidden inputをクリア
  [
    'timeSlot',
    'appetite',
    'energy',
    'vomiting',
    'urination',
    'defecation',
    'stoolCondition',
    'cleaning',
  ].forEach(id => {
    document.getElementById(id).value = '';
  });

  updateStoolConditionVisibility();
  clearCareImageSelection();

  clearAllFieldErrors();
  hideToast();
}

/**
 * フォーム送信処理（オフライン対応）
 */
async function handleSubmit(e) {
  e.preventDefault();

  hideError();
  hideSuccess();

  const validationResult = validateForm();
  if (!validationResult.isValid) {
    showError(validationResult.message);
    if (validationResult.firstInvalidFieldId) {
      focusField(validationResult.firstInvalidFieldId);
    }
    return;
  }

  setSubmitButtonState(true);

  try {
    // ボランティア情報を取得
    const volunteerSelect = document.getElementById('volunteer');
    const selectedOption = volunteerSelect.options[volunteerSelect.selectedIndex];
    const recorderName = selectedOption.textContent;

    const formData = {
      animal_id: parseInt(animalId),
      log_date: document.getElementById('logDate').value,
      time_slot: document.getElementById('timeSlot').value,
      appetite: parseFloat(document.getElementById('appetite').value),
      energy: parseInt(document.getElementById('energy').value),
      vomiting:
        document.getElementById('vomiting').value === 'true'
          ? true
          : document.getElementById('vomiting').value === 'false'
            ? false
            : null,
      urination:
        document.getElementById('urination').value === 'true'
          ? true
          : document.getElementById('urination').value === 'false'
            ? false
            : null,
      defecation:
        document.getElementById('defecation').value === 'true'
          ? true
          : document.getElementById('defecation').value === 'false'
            ? false
            : null,
      stool_condition: document.getElementById('stoolCondition').value
        ? parseInt(document.getElementById('stoolCondition').value)
        : null,
      cleaning:
        document.getElementById('cleaning').value === 'true'
          ? true
          : document.getElementById('cleaning').value === 'false'
            ? false
            : null,
      memo: document.getElementById('memo').value || null,
      recorder_id: parseInt(document.getElementById('volunteer').value),
      recorder_name: recorderName,
    };

    const selectedImage = getSelectedCareImage();
    const imageValidation = validateCareImage(selectedImage);
    if (!imageValidation.isValid) {
      showError(imageValidation.message);
      return;
    }

    const requestBody = (() => {
      if (!isEditMode) {
        // 作成時は全てのフィールドを送信
        return formData;
      }
      // 更新時は変更可能なフィールドのみ送信（不変フィールドは除外）
      const { animal_id, log_date, time_slot, recorder_id, recorder_name, ...mutableFields } =
        formData;
      return mutableFields;
    })();

    if (isEditMode) {
      if (selectedImage) {
        throw new Error(
          fallbackText(
            'Image upload is available only when creating a new record.',
            '画像アップロードは新規登録時のみ対応しています。'
          )
        );
      }

      const response = await fetch(`${API_BASE}/care-logs/animal/${animalId}/${logId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestBody),
      });

      if (!response.ok) {
        throw new Error(
          translateCare(
            'error_api_failed',
            fallbackText(
              'Update failed. Please try again.',
              '更新に失敗しました。時間をおいて再度お試しください。'
            )
          )
        );
      }

      showToast(
        translateCare('save_success_online', fallbackText('Record updated.', '記録を更新しました'))
      );

      setTimeout(() => {
        window.location.href = `/public/care-logs?animal_id=${animalId}&highlight_id=${logId}`;
      }, 1200);
    } else {
      if (selectedImage) {
        if (!navigator.onLine) {
          throw new Error(
            fallbackText(
              'Photo upload is not available offline.',
              'オフライン時は写真を送信できません。通信可能な環境で再送してください。'
            )
          );
        }

        const multipart = buildMultipartPayload(formData);
        multipart.append('image', selectedImage);

        const response = await fetch(`${API_BASE}/care-logs`, {
          method: 'POST',
          body: multipart,
        });
        if (!response.ok) {
          const defaultMessage = translateCare(
            'error_api_failed',
            fallbackText(
              'Submission failed. Please try again later.',
              '送信に失敗しました。時間をおいて再度お試しください。'
            )
          );
          let serverMessage = defaultMessage;
          try {
            const errorPayload = await response.json();
            if (typeof errorPayload?.detail === 'string' && errorPayload.detail.trim() !== '') {
              serverMessage = errorPayload.detail;
            }
          } catch {
            // ignore JSON parse errors and keep default message
          }
          throw new Error(serverMessage);
        }

        showToast(
          translateCare('save_success_online', fallbackText('Record saved.', '記録を保存しました')),
          fallbackText(
            'Uploaded photo is reviewed by admins and not shown on this screen.',
            '画像は管理者確認用で、この画面には再表示されません。'
          )
        );
      } else {
        // オフラインマネージャーを使用して保存
        const result = await window.offlineManager.saveCareLog(formData);

        const successMessage = result.online
          ? translateCare(
              'save_success_online',
              fallbackText('Record saved.', '記録を保存しました')
            )
          : translateCare('save_success_offline', OFFLINE_SAVE_FALLBACK);
        showToast(successMessage);
      }

      // フォームをリセット
      setTimeout(() => {
        resetForm();
      }, 2000);
    }
  } catch (error) {
    const fallbackMessage = translateCare(
      'error_api_failed',
      fallbackText(
        'Submission failed. Please try again later.',
        '送信に失敗しました。時間をおいて再度お試しください。'
      )
    );
    showError(error?.message || fallbackMessage);
  } finally {
    setSubmitButtonState(false);
  }
}

// 初期化処理
document.addEventListener('DOMContentLoaded', async () => {
  // i18nを初期化
  if (typeof initI18n === 'function') {
    await initI18n();
  }

  updatePageTitle();
  document.addEventListener('languageChanged', updatePageTitle);

  // 各ボタングループを初期化
  setupButtonGroup('time-slot-btn', 'timeSlot');
  setupButtonGroup('appetite-btn', 'appetite');
  setupButtonGroup('energy-btn', 'energy');
  setupButtonGroup('vomiting-btn', 'vomiting');
  setupButtonGroup('urination-btn', 'urination');
  setupButtonGroup('defecation-btn', 'defecation');
  setupButtonGroup('stool-condition-btn', 'stoolCondition');
  setupButtonGroup('cleaning-btn', 'cleaning');

  // defecation の選択に応じて stool_condition を表示/非表示
  document.querySelectorAll('.defecation-btn').forEach(btn => {
    btn.addEventListener('click', updateStoolConditionVisibility);
  });

  updateStoolConditionVisibility();
  setupStoolConditionHelpModal();

  // 前回値コピーボタン
  document.getElementById('copyLastBtn').addEventListener('click', copyLastValues);

  // フォーム送信
  document.getElementById('careForm').addEventListener('submit', handleSubmit);

  // 記録一覧ボタンのリンクを設定
  document.getElementById('viewLogsBtn').href = `/public/care-logs?animal_id=${animalId}`;

  // データ読み込み
  loadAnimalInfo();
  await loadVolunteers();
  await loadCareLogForEdit();

  const careImageInput = getCareImageInput();
  if (careImageInput) {
    careImageInput.addEventListener('change', updateCareImagePreview);
  }

  const clearCareImageBtn = document.getElementById('careImageClearBtn');
  if (clearCareImageBtn) {
    clearCareImageBtn.addEventListener('click', clearCareImageSelection);
  }

  if (isEditMode && careImageInput) {
    careImageInput.disabled = true;
  }

  // time_slot プリセット（新規作成時のみ）
  if (!isEditMode && presetTimeSlot) {
    const allowed = ['morning', 'noon', 'evening'];
    if (allowed.includes(presetTimeSlot)) {
      const btn = document.querySelector(`.time-slot-btn[data-value="${presetTimeSlot}"]`);
      if (btn) btn.click();
    }
  }

  const logDateInput = document.getElementById('logDate');
  if (logDateInput) {
    logDateInput.addEventListener('input', () => {
      if (logDateInput.value) {
        setFieldErrorState('logDate', false);
      }
    });
  }

  const volunteerSelect = document.getElementById('volunteer');
  if (volunteerSelect) {
    volunteerSelect.addEventListener('change', () => {
      if (volunteerSelect.value) {
        setFieldErrorState('volunteer', false);
      }
    });
  }
});

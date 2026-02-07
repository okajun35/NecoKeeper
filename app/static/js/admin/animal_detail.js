/**
 * 猫詳細ページのJavaScript
 */

const isKiroweenMode = document.body && document.body.classList.contains('kiroween-mode');
const DEFAULT_IMAGE_PLACEHOLDER = isKiroweenMode
  ? '/static/icons/halloween_logo_2.webp'
  : '/static/images/default.svg';
const adminBasePath = window.ADMIN_BASE_PATH || window.__ADMIN_BASE_PATH__ || '/admin';

function parseOptionalInt(value) {
  if (value === '' || value === null || value === undefined) {
    return null;
  }
  const parsed = Number.parseInt(value, 10);
  return Number.isNaN(parsed) ? null : parsed;
}

function parseOptionalBool(value) {
  if (value === '' || value === null || value === undefined) {
    return null;
  }
  if (value === 'true') return true;
  if (value === 'false') return false;
  return null;
}

// ページ読み込み時の初期化
document.addEventListener('DOMContentLoaded', () => {
  setupTabs();
  setupStatusAndLocationUpdate();
  setupQRCardGeneration();
  setupPaperFormGeneration();
});

// タブ切り替え機能
function setupTabs() {
  const tabButtons = document.querySelectorAll('.tab-button');
  const tabContents = document.querySelectorAll('.tab-content');

  tabButtons.forEach(button => {
    button.addEventListener('click', () => {
      const tabId = button.id.replace('tab-', '');

      // すべてのタブを非アクティブ化
      tabButtons.forEach(btn => {
        btn.classList.remove('active', 'border-brand-primary', 'text-brand-primary');
        btn.classList.add('border-transparent', 'text-gray-500');
      });

      // すべてのコンテンツを非表示
      tabContents.forEach(content => {
        content.classList.add('hidden');
      });

      // 選択されたタブをアクティブ化
      button.classList.add('active', 'border-brand-primary', 'text-brand-primary');
      button.classList.remove('border-transparent', 'text-gray-500');

      // 選択されたコンテンツを表示
      const content = document.getElementById(`content-${tabId}`);
      content.classList.remove('hidden');

      // タブごとのデータ読み込み
      loadTabContent(tabId);
    });
  });
}

// タブコンテンツの読み込み
function loadTabContent(tabId) {
  switch (tabId) {
    case 'care':
      loadCareRecords();
      break;
    case 'medical':
      loadMedicalRecords();
      break;
    case 'gallery':
      loadGallery();
      break;
    case 'weight':
      loadWeightChart();
      break;
  }
}

// 基本情報フォームのセットアップ
function setupBasicInfoForm() {
  const form = document.getElementById('basicInfoForm');
  const cancelBtn = document.getElementById('cancelBtn');
  const microchipInput = document.getElementById('microchip_number');
  const microchipError = document.getElementById('microchip_error');
  const isSterilizedSelect = document.getElementById('isSterilized');
  const sterilizedOnWrapper = document.getElementById('sterilizedOnWrapper');

  // 避妊・去勢選択時の日付フィールド表示制御
  if (isSterilizedSelect && sterilizedOnWrapper) {
    isSterilizedSelect.addEventListener('change', function () {
      if (this.value === 'true') {
        sterilizedOnWrapper.style.display = '';
      } else {
        sterilizedOnWrapper.style.display = 'none';
        document.getElementById('sterilizedOn').value = '';
      }
    });
  }

  // マイクロチップ番号のリアルタイムバリデーション
  if (microchipInput) {
    microchipInput.addEventListener('input', function (e) {
      const value = e.target.value.trim();

      if (value === '') {
        microchipError.classList.add('hidden');
        microchipInput.classList.remove('border-red-500');
        return;
      }

      const is15Digit = /^\d{15}$/.test(value);
      const is10AlphaNum = /^[0-9A-Za-z]{10}$/.test(value);

      if (!is15Digit && !is10AlphaNum) {
        microchipError.classList.remove('hidden');
        microchipError.textContent = '15桁の半角数字、または10桁の英数字を入力してください';
        microchipInput.classList.add('border-red-500');
      } else {
        microchipError.classList.add('hidden');
        microchipInput.classList.remove('border-red-500');
      }
    });
  }

  form.addEventListener('submit', async e => {
    e.preventDefault();
    await updateBasicInfo();
  });

  cancelBtn.addEventListener('click', () => {
    window.location.href = `${adminBasePath}/animals`;
  });
}

let currentVaccinationRecordId = null;

// 基本情報の更新
async function updateBasicInfo() {
  try {
    const microchipValue = document.getElementById('microchip_number').value.trim();

    const formData = {
      name: document.getElementById('name').value,
      coat_color: document.getElementById('coat_color').value,
      coat_color_note: document.getElementById('coat_color_note').value || null,
      tail_length: document.getElementById('tailLength').value,
      collar: document.getElementById('collar').value,
      age_months: parseOptionalInt(document.getElementById('age_months').value),
      age_is_estimated: document.getElementById('age_is_estimated').checked,
      gender: document.getElementById('gender').value,
      ear_cut: document.getElementById('earCut').checked,
      rescue_source: document.getElementById('rescue_source').value || null,
      breed: document.getElementById('breed').value || null,
      features: document.getElementById('features').value || null,
      microchip_number: microchipValue || null,
      // 医療情報（Issue #83）
      fiv_positive: parseOptionalBool(document.getElementById('fivPositive').value),
      felv_positive: parseOptionalBool(document.getElementById('felvPositive').value),
      is_sterilized: parseOptionalBool(document.getElementById('isSterilized').value),
      sterilized_on: document.getElementById('sterilizedOn').value || null,
    };

    const response = await fetch(`/api/v1/animals/${animalId}`, {
      method: 'PUT',
      headers: {
        Authorization: `Bearer ${getToken()}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(formData),
    });

    if (!response.ok) {
      const errorData = await response.json();
      if (response.status === 409) {
        // マイクロチップ番号の重複エラー
        const errorMessage = isKiroweenMode
          ? 'MICROCHIP NUMBER ALREADY EXISTS'
          : errorData.detail || 'このマイクロチップ番号は既に登録されています';
        throw new Error(errorMessage);
      }
      const errorMessage = isKiroweenMode
        ? 'FAILED TO UPDATE BASIC INFO'
        : translate('errors.basic_info_update_failed', { ns: 'animals' });
      throw new Error(errorMessage);
    }

    await saveVaccinationRecord();

    const successMessage = isKiroweenMode
      ? 'BASIC INFO UPDATED'
      : translate('messages.basic_info_updated', { ns: 'animals' });
    showToast(successMessage, 'success');
  } catch (error) {
    console.error('Error updating basic info:', error);
    const fallbackMessage = isKiroweenMode
      ? 'FAILED TO UPDATE BASIC INFO'
      : translate('errors.basic_info_update_failed', { ns: 'animals' });
    showToast(error.message || fallbackMessage, 'error');
  }
}

// ワクチン接種記録のセットアップ
async function setupVaccinationRecords() {
  await loadVaccinationRecordIntoForm();
}

// ワクチン接種記録の取得とフォーム反映（最新1件）
async function loadVaccinationRecordIntoForm() {
  currentVaccinationRecordId = null;
  try {
    const response = await fetch(`/api/v1/vaccinations/animal/${animalId}`, {
      headers: {
        Authorization: `Bearer ${getToken()}`,
      },
    });

    if (!response.ok) {
      throw new Error('Failed to fetch vaccination records');
    }

    const records = await response.json();
    if (!records || records.length === 0) {
      setVaccinationFormValues();
      return;
    }

    // 最新（降順で返る前提）
    const record = records[0];
    currentVaccinationRecordId = record.id;
    setVaccinationFormValues({
      vaccine_category: record.vaccine_category,
      administered_on: record.administered_on,
      next_due_on: record.next_due_on,
      memo: record.memo,
    });
  } catch (error) {
    console.error('Error loading vaccination record:', error);
    showToast(translate('medical_record.load_error', { ns: 'animals' }), 'error');
  }
}

function setVaccinationFormValues(values = {}) {
  const { vaccine_category = '3core', administered_on = '', next_due_on = '', memo = '' } = values;

  const categoryEl = document.getElementById('vaccineCategory');
  const dateEl = document.getElementById('vaccinationDate');
  const nextDueEl = document.getElementById('nextDueOn');
  const memoEl = document.getElementById('vaccineMemo');

  if (categoryEl) categoryEl.value = vaccine_category;
  if (dateEl) dateEl.value = administered_on || '';
  if (nextDueEl) nextDueEl.value = next_due_on || '';
  if (memoEl) memoEl.value = memo || '';
}

// ワクチン接種記録の保存（新規 or 更新）
async function saveVaccinationRecord() {
  const vaccineCategory = document.getElementById('vaccineCategory')?.value;
  const vaccinationDate = document.getElementById('vaccinationDate')?.value;
  const nextDueOn = document.getElementById('nextDueOn')?.value || null;
  const vaccineMemo = document.getElementById('vaccineMemo')?.value || null;

  // 接種日未入力なら保存処理をスキップ
  if (!vaccinationDate) {
    return null;
  }

  const payload = {
    animal_id: animalId,
    vaccine_category: vaccineCategory,
    administered_on: vaccinationDate,
    next_due_on: nextDueOn,
    memo: vaccineMemo,
  };

  const isUpdate = Boolean(currentVaccinationRecordId);
  const url = isUpdate
    ? `/api/v1/vaccinations/${currentVaccinationRecordId}`
    : '/api/v1/vaccinations';
  const method = isUpdate ? 'PUT' : 'POST';

  try {
    const response = await fetch(url, {
      method,
      headers: {
        Authorization: `Bearer ${getToken()}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      const message = errorData.detail || translate('medical_record.load_error', { ns: 'animals' });
      throw new Error(message);
    }

    const saved = await response.json();
    currentVaccinationRecordId = saved.id;
    setVaccinationFormValues({
      vaccine_category: saved.vaccine_category,
      administered_on: saved.administered_on,
      next_due_on: saved.next_due_on,
      memo: saved.memo,
    });
    return saved;
  } catch (error) {
    console.error('Error saving vaccination record:', error);
    showToast(error.message, 'error');
    throw error;
  }
}

// ステータス更新のセットアップ
function setupStatusAndLocationUpdate() {
  const updateBtn = document.getElementById('updateStatusAndLocationBtn');

  if (updateBtn) {
    updateBtn.addEventListener('click', async () => {
      await updateStatusAndLocation();
    });
  }
}

// QRカード生成のセットアップ
function setupQRCardGeneration() {
  const generateBtn = document.getElementById('generateQRCardBtn');

  if (generateBtn) {
    generateBtn.addEventListener('click', async () => {
      await generateQRCard();
    });
  }
}

// QRカードPDFを生成してダウンロード
async function generateQRCard() {
  const generateBtn = document.getElementById('generateQRCardBtn');
  const originalText = generateBtn.innerHTML;
  const isKiroween = document.body.classList.contains('kiroween-mode');
  const loadingText = isKiroween ? 'GENERATING...' : '生成中...';

  try {
    // ボタンをローディング状態に
    generateBtn.disabled = true;
    generateBtn.innerHTML = `
      <svg class="animate-spin h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
      <span>${loadingText}</span>
    `;

    // API呼び出し
    const currentLocale =
      window.i18n?.getCurrentLanguage?.() || localStorage.getItem('language') || 'ja';
    const response = await fetch('/api/v1/pdf/qr-card', {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${getToken()}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        animal_id: animalId,
        locale: currentLocale,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      const errorMessage =
        error.detail ||
        (isKiroween
          ? 'FAILED TO GENERATE QR CARD'
          : translate('errors.qr_generation_failed', { ns: 'animals' }));
      throw new Error(errorMessage);
    }

    // PDFをダウンロード
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;

    // Content-Dispositionヘッダーからファイル名を取得
    const contentDisposition = response.headers.get('Content-Disposition');
    let filename = `qr_card_${animalId}.pdf`;
    if (contentDisposition) {
      const filenameMatch = contentDisposition.match(/filename="?([^"]+)"?/);
      if (filenameMatch && filenameMatch[1]) {
        filename = filenameMatch[1];
      }
    }

    a.download = filename;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);

    const successMessage = isKiroween
      ? 'QR CARD GENERATED'
      : translate('messages.qr_generated', { ns: 'animals' });
    showToast(successMessage, 'success');
  } catch (error) {
    console.error('Error generating QR card:', error);
    const fallbackMessage = isKiroween
      ? 'FAILED TO GENERATE QR CARD'
      : translate('errors.qr_generation_failed', { ns: 'animals' });
    showToast(error.message || fallbackMessage, 'error');
  } finally {
    // ボタンを元に戻す
    generateBtn.disabled = false;
    generateBtn.innerHTML = originalText;
  }
}

// 紙記録フォーム生成のセットアップ
function setupPaperFormGeneration() {
  const generateBtn = document.getElementById('generatePaperFormBtn');
  const modal = document.getElementById('paperFormModal');
  const confirmBtn = document.getElementById('confirmPaperFormBtn');
  const cancelBtn = document.getElementById('cancelPaperFormBtn');
  const yearSelect = document.getElementById('paperFormYear');
  const monthSelect = document.getElementById('paperFormMonth');

  if (!generateBtn) return;

  // 年のオプションを生成（現在年の前後2年）
  const currentYear = new Date().getFullYear();
  const isKiroween = document.body.classList.contains('kiroween-mode');

  for (let year = currentYear - 2; year <= currentYear + 2; year++) {
    const option = document.createElement('option');
    option.value = year;
    option.textContent = isKiroween ? `${year}` : `${year}年`;
    if (year === currentYear) {
      option.selected = true;
    }
    yearSelect.appendChild(option);
  }

  // 現在の月を選択
  const currentMonth = new Date().getMonth() + 1;
  monthSelect.value = currentMonth;

  // モーダルを開く
  generateBtn.addEventListener('click', () => {
    modal.classList.remove('hidden');
  });

  // モーダルを閉じる
  const closeModal = () => {
    modal.classList.add('hidden');
  };

  cancelBtn.addEventListener('click', closeModal);

  // モーダル外クリックで閉じる
  modal.addEventListener('click', e => {
    if (e.target === modal) {
      closeModal();
    }
  });

  // 出力ボタン
  confirmBtn.addEventListener('click', async () => {
    const year = parseInt(yearSelect.value);
    const month = parseInt(monthSelect.value);
    closeModal();
    await generatePaperForm(year, month);
  });
}

// 紙記録フォームPDFを生成してダウンロード
async function generatePaperForm(year, month) {
  const generateBtn = document.getElementById('generatePaperFormBtn');
  const originalText = generateBtn.innerHTML;
  const isKiroween = document.body.classList.contains('kiroween-mode');
  const loadingText = isKiroween ? 'GENERATING...' : '生成中...';

  try {
    // ボタンをローディング状態に
    generateBtn.disabled = true;
    generateBtn.innerHTML = `
      <svg class="animate-spin h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
      <span>${loadingText}</span>
    `;

    // API呼び出し
    const response = await fetch('/api/v1/pdf/paper-form', {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${getToken()}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        animal_id: animalId,
        year: year,
        month: month,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      const errorMessage =
        error.detail ||
        (isKiroween
          ? 'FAILED TO GENERATE PAPER FORM'
          : translate('errors.paper_form_generation_failed', { ns: 'animals' }));
      throw new Error(errorMessage);
    }

    // PDFをダウンロード
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `paper_form_${animalId}_${year}${month.toString().padStart(2, '0')}.pdf`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);

    const monthText = month.toString().padStart(2, '0');
    const message = isKiroween
      ? `PAPER FORM GENERATED FOR ${year}-${monthText}`
      : translate('messages.paper_form_generated', { ns: 'animals', year, month: monthText });
    showToast(message, 'success');
  } catch (error) {
    console.error('Error generating paper form:', error);
    const fallbackMessage = isKiroween
      ? 'FAILED TO GENERATE PAPER FORM'
      : translate('errors.paper_form_generation_failed', { ns: 'animals' });
    showToast(error.message || fallbackMessage, 'error');
  } finally {
    // ボタンを元に戻す
    generateBtn.disabled = false;
    generateBtn.innerHTML = originalText;
  }
}

// ステータスの更新（理由フィールド対応）
async function updateStatusAndLocation(confirm = false) {
  try {
    const newStatus = document.getElementById('statusSelect').value;
    const newLocationType = document.getElementById('locationTypeSelect').value;
    const currentLocationNote = document.getElementById('currentLocationNote').value.trim();
    const reasonForStatusChange =
      document.getElementById('reasonForStatusChange')?.value.trim() || null;

    const requestBody = {
      status: newStatus,
      location_type: newLocationType,
    };

    // current_location_noteが空でなければ追加
    if (currentLocationNote) {
      requestBody.current_location_note = currentLocationNote;
    }

    // 理由が入力されていれば追加
    if (reasonForStatusChange) {
      requestBody.reason = reasonForStatusChange;
    }

    if (confirm) {
      requestBody.confirm = true;
    }

    const response = await fetch(`/api/v1/animals/${animalId}`, {
      method: 'PUT',
      headers: {
        Authorization: `Bearer ${getToken()}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestBody),
    });

    // 409 Conflict: 確認が必要
    if (response.status === 409) {
      const data = await response.json();
      // FastAPIはdetailオブジェクトをdetailフィールドにラップする
      const confirmData = data.detail || data;
      if (confirmData.requires_confirmation) {
        const confirmMessage =
          confirmData.message || '終端ステータスから変更しようとしています。本当に変更しますか？';
        if (window.confirm(confirmMessage)) {
          // 確認後、再度リクエスト（理由は保持）
          await updateStatusAndLocation(true);
        }
      }
      return; // 409の場合はここで終了
    }

    if (!response.ok) {
      const errorMessage = isKiroweenMode
        ? 'FAILED TO UPDATE'
        : 'ステータス・所在地の更新に失敗しました';
      throw new Error(errorMessage);
    }

    // 更新成功後、理由フィールドをリセット
    const reasonField = document.getElementById('reasonForStatusChange');
    if (reasonField) {
      reasonField.value = '';
    }

    const successMessage = isKiroweenMode ? 'UPDATED' : 'ステータス・所在地を更新しました';
    showToast(successMessage, 'success');
  } catch (error) {
    console.error('Error updating status and location:', error);
    const fallbackMessage = isKiroweenMode
      ? 'FAILED TO UPDATE'
      : 'ステータス・所在地の更新に失敗しました';
    showToast(error.message || fallbackMessage, 'error');
  }
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

// 世話記録の読み込み
async function loadCareRecords() {
  const content = requireElementById('content-care', 'animal_detail.care');

  try {
    const response = await fetch(`/api/v1/care-logs?animal_id=${animalId}&page=1&page_size=10`, {
      headers: {
        Authorization: `Bearer ${getToken()}`,
      },
    });

    if (!response.ok) {
      throw new Error('世話記録の取得に失敗しました');
    }

    const data = await response.json();
    content.innerHTML = ''; // コンテンツをクリア

    if (data.items.length === 0) {
      content.innerHTML = `<div class="text-center py-8 text-gray-500">${translate('care_log.empty', { ns: 'animals' })}</div>`;
      return;
    }

    // 世話記録の表示
    const listContainer = document.createElement('div');
    listContainer.className = 'space-y-4';

    data.items.forEach(record => {
      const card = cloneTemplate('tmpl-care-record');
      assertRequiredSelectors(
        card,
        [
          '.js-date-time',
          '.js-recorder',
          '.js-appetite',
          '.js-energy',
          '.js-urination',
          '.js-cleaning',
          '.js-memo',
        ],
        'animal_detail.tmpl-care-record'
      );

      // 日時
      const timeSlot = record.time_slot
        ? translate(`care_logs:time_slots.${record.time_slot}`, { defaultValue: record.time_slot })
        : translate('care_log.unset', { ns: 'animals' });
      requireSelector(card, '.js-date-time', 'animal_detail.tmpl-care-record').textContent =
        `${record.created_at.split('T')[0]} - ${timeSlot}`;

      // 記録者
      requireSelector(card, '.js-recorder', 'animal_detail.tmpl-care-record').textContent =
        record.recorder_name || translate('care_log.unknown', { ns: 'animals' });

      // 各種状態
      requireSelector(card, '.js-appetite', 'animal_detail.tmpl-care-record').textContent =
        formatAppetiteLabel(record.appetite);
      requireSelector(card, '.js-energy', 'animal_detail.tmpl-care-record').textContent =
        record.energy;
      requireSelector(card, '.js-urination', 'animal_detail.tmpl-care-record').textContent =
        record.urination
          ? translate('care_log.yes', { ns: 'animals' })
          : translate('care_log.no', { ns: 'animals' });
      requireSelector(card, '.js-cleaning', 'animal_detail.tmpl-care-record').textContent =
        record.cleaning
          ? translate('care_log.done', { ns: 'animals' })
          : translate('care_log.not_done', { ns: 'animals' });

      // メモ
      if (record.memo) {
        const memoEl = requireSelector(card, '.js-memo', 'animal_detail.tmpl-care-record');
        memoEl.textContent = record.memo;
        memoEl.classList.remove('hidden');
      }

      translateDynamicElement(card);
      listContainer.appendChild(card);
    });

    content.appendChild(listContainer);
  } catch (error) {
    console.error('Error loading care records:', error);
    content.innerHTML = `<div class="text-center py-8 text-red-500">${translate('care_log.load_error', { ns: 'animals' })}</div>`;
  }
}

// 診療記録の読み込み
async function loadMedicalRecords() {
  const content = requireElementById('content-medical', 'animal_detail.medical');

  try {
    const response = await fetch(
      `/api/v1/medical-records?animal_id=${animalId}&page=1&page_size=10`,
      {
        headers: {
          Authorization: `Bearer ${getToken()}`,
        },
      }
    );

    if (!response.ok) {
      throw new Error('診療記録の取得に失敗しました');
    }

    const data = await response.json();
    content.innerHTML = '';

    if (data.items.length === 0) {
      content.innerHTML = `<div class="text-center py-8 text-gray-500">${translate('medical_record.empty', { ns: 'animals' })}</div>`;
      return;
    }

    // 診療記録の表示
    const listContainer = document.createElement('div');
    listContainer.className = 'space-y-4';

    data.items.forEach(record => {
      const card = cloneTemplate('tmpl-medical-record');
      assertRequiredSelectors(
        card,
        [
          '.js-date',
          '.js-vet',
          '.js-weight',
          '.js-temperature',
          '.js-symptoms',
          '.js-action-row',
          '.js-action',
          '.js-dosage',
        ],
        'animal_detail.tmpl-medical-record'
      );

      requireSelector(card, '.js-date', 'animal_detail.tmpl-medical-record').textContent =
        record.date;
      requireSelector(card, '.js-vet', 'animal_detail.tmpl-medical-record').textContent =
        record.vet_name || translate('medical_record.unknown', { ns: 'animals' });
      requireSelector(card, '.js-weight', 'animal_detail.tmpl-medical-record').textContent =
        record.weight;
      requireSelector(card, '.js-temperature', 'animal_detail.tmpl-medical-record').textContent =
        record.temperature ? record.temperature + '℃' : '-';
      requireSelector(card, '.js-symptoms', 'animal_detail.tmpl-medical-record').textContent =
        record.symptoms;

      if (record.medical_action_name) {
        const actionRow = requireSelector(
          card,
          '.js-action-row',
          'animal_detail.tmpl-medical-record'
        );
        actionRow.classList.remove('hidden');
        requireSelector(card, '.js-action', 'animal_detail.tmpl-medical-record').textContent =
          record.medical_action_name;
        if (record.dosage) {
          requireSelector(card, '.js-dosage', 'animal_detail.tmpl-medical-record').textContent =
            `(${record.dosage}${record.dosage_unit || ''})`;
        }
      }

      translateDynamicElement(card);
      listContainer.appendChild(card);
    });

    content.appendChild(listContainer);
  } catch (error) {
    console.error('Error loading medical records:', error);
    content.innerHTML = `<div class="text-center py-8 text-red-500">${translate('medical_record.load_error', { ns: 'animals' })}</div>`;
  }
}

// 画像ギャラリーの読み込み
async function loadGallery() {
  const content = requireElementById('content-gallery', 'animal_detail.gallery');

  try {
    const response = await fetch(
      `/api/v1/animals/${animalId}/images?sort_by=created_at&ascending=false`,
      {
        headers: {
          Authorization: `Bearer ${getToken()}`,
        },
      }
    );

    if (!response.ok) {
      throw new Error(translate('gallery.fetch_error', { ns: 'animals' }));
    }

    const images = await response.json();
    content.innerHTML = '';

    if (images.length === 0) {
      content.innerHTML = `
        <div class="text-center py-8">
          <p class="text-gray-500 mb-4">${translate('gallery.empty', { ns: 'animals' })}</p>
          <button onclick="openUploadDialog()" class="px-4 py-2 bg-brand-primary text-white rounded-lg hover:opacity-90">
            ${translate('gallery.upload', { ns: 'animals' })}
          </button>
        </div>
      `;
      return;
    }

    // ヘッダー（件数と追加ボタン）
    const headerHtml = `
      <div class="mb-4 flex justify-between items-center">
        <p class="text-sm text-gray-600">${translate('gallery.count', { ns: 'animals', count: images.length })}</p>
        <button onclick="openUploadDialog()" class="px-4 py-2 bg-brand-primary text-white rounded-lg hover:opacity-90">
          ${translate('gallery.add', { ns: 'animals' })}
        </button>
      </div>
    `;
    const headerDiv = document.createElement('div');
    headerDiv.innerHTML = headerHtml;
    content.appendChild(headerDiv);

    const listContainer = document.createElement('div');
    listContainer.className = 'grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4';
    const locale = window.i18next?.language === 'en' ? 'en-US' : 'ja-JP';

    images.forEach(image => {
      const card = cloneTemplate('tmpl-gallery-item');
      assertRequiredSelectors(
        card,
        ['.js-image', '.js-overlay-caption', '.js-caption', '.js-taken-at', '.js-delete-btn'],
        'animal_detail.tmpl-gallery-item'
      );

      const imageSrc = image.image_path.startsWith('/')
        ? image.image_path
        : `/media/${image.image_path}`;

      const rawDescription = (image.description || '').trim();
      const displayDescription =
        rawDescription === 'プロフィール画像'
          ? translate('gallery.profile_image', {
              ns: 'animals',
              defaultValue: rawDescription || 'プロフィール画像',
            })
          : rawDescription;

      const imgEl = requireSelector(card, '.js-image', 'animal_detail.tmpl-gallery-item');
      imgEl.src = imageSrc;
      imgEl.alt = displayDescription || translate('gallery.cat_image', { ns: 'animals' });
      imgEl.onerror = () => {
        imgEl.onerror = null;
        imgEl.src = DEFAULT_IMAGE_PLACEHOLDER;
      };
      imgEl.style.cursor = 'pointer';
      imgEl.onclick = () =>
        openImageModal(
          imageSrc,
          displayDescription || translate('gallery.cat_image', { ns: 'animals' })
        );

      const overlayCaption = requireSelector(
        card,
        '.js-overlay-caption',
        'animal_detail.tmpl-gallery-item'
      );
      overlayCaption.textContent = displayDescription;

      const captionEl = requireSelector(card, '.js-caption', 'animal_detail.tmpl-gallery-item');
      if (displayDescription) {
        captionEl.textContent = displayDescription;
        captionEl.classList.remove('hidden');
      }

      const takenAtEl = requireSelector(card, '.js-taken-at', 'animal_detail.tmpl-gallery-item');
      if (image.taken_at) {
        takenAtEl.textContent = new Date(image.taken_at).toLocaleDateString(locale);
        takenAtEl.classList.remove('hidden');
      }

      const deleteBtn = requireSelector(card, '.js-delete-btn', 'animal_detail.tmpl-gallery-item');
      deleteBtn.addEventListener('click', event => {
        event.stopPropagation();
        deleteImage(image.id);
      });

      translateDynamicElement(card);
      listContainer.appendChild(card);
    });

    content.appendChild(listContainer);
  } catch (error) {
    console.error('Error loading gallery:', error);
    content.innerHTML = `<div class="text-center py-8 text-red-500">${translate('gallery.fetch_error', { ns: 'animals' })}</div>`;
  }
}

// 画像アップロードダイアログを開く
function openUploadDialog() {
  const input = document.createElement('input');
  input.type = 'file';
  input.accept = 'image/*';
  input.onchange = async e => {
    const file = e.target.files[0];
    if (file) {
      await uploadImage(file);
    }
  };
  input.click();
}

// 画像をアップロード
async function uploadImage(file) {
  try {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`/api/v1/animals/${animalId}/images`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${getToken()}`,
      },
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.detail || translate('gallery.upload_failed', { ns: 'animals' }));
    }

    showToast(translate('gallery.upload_success', { ns: 'animals' }), 'success');
    loadGallery();
  } catch (error) {
    console.error('Error uploading image:', error);
    showToast(error.message, 'error');
  }
}

// 画像を削除
async function deleteImage(imageId) {
  const confirmMessage = translate('gallery.delete_confirm', { ns: 'animals' });
  if (!confirmAction(confirmMessage)) {
    return;
  }

  try {
    const response = await fetch(`/api/v1/images/${imageId}`, {
      method: 'DELETE',
      headers: {
        Authorization: `Bearer ${getToken()}`,
      },
    });

    if (!response.ok) {
      throw new Error(translate('gallery.delete_failed', { ns: 'animals' }));
    }

    showToast(translate('gallery.delete_success', { ns: 'animals' }), 'success');
    loadGallery();
  } catch (error) {
    console.error('Error deleting image:', error);
    showToast(error.message, 'error');
  }
}

// 画像モーダルを開く
function openImageModal(imagePath, description) {
  const modal = document.createElement('div');
  modal.className =
    'fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4';
  modal.onclick = e => {
    if (e.target === modal) modal.remove();
  };

  modal.innerHTML = `
    <div class="max-w-4xl max-h-full relative">
      <button onclick="this.closest('.fixed').remove()" class="absolute top-2 right-2 p-2 bg-white rounded-full hover:bg-gray-100 z-10">
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
        </svg>
      </button>
      <img src="${imagePath}"
           alt="${description}"
          onerror="this.onerror=null; this.src='${DEFAULT_IMAGE_PLACEHOLDER}';"
           class="max-w-full max-h-screen object-contain rounded-lg">
      ${description ? `<p class="text-white text-center mt-2">${description}</p>` : ''}
    </div>
  `;

  document.body.appendChild(modal);
}

// 体重推移グラフの読み込み
async function loadWeightChart() {
  const content = document.getElementById('content-weight');

  try {
    // 診療記録から体重データを取得
    const response = await fetch(
      `/api/v1/medical-records?animal_id=${animalId}&page=1&page_size=100`,
      {
        headers: {
          Authorization: `Bearer ${getToken()}`,
        },
      }
    );

    if (!response.ok) {
      throw new Error(translate('weight_chart.fetch_error', { ns: 'animals' }));
    }

    const data = await response.json();

    // 体重データを抽出
    const weightData = data.items
      .filter(record => record.weight)
      .map(record => ({
        date: record.date,
        weight: parseFloat(record.weight),
      }))
      .sort((a, b) => new Date(a.date) - new Date(b.date));

    if (weightData.length === 0) {
      content.innerHTML = `<div class="text-center py-8 text-gray-500">${translate('weight_chart.empty', { ns: 'animals' })}</div>`;
      return;
    }

    // グラフを描画
    renderWeightChart(content, weightData);
  } catch (error) {
    console.error('Error loading weight chart:', error);
    content.innerHTML = `<div class="text-center py-8 text-red-500">${translate('weight_chart.error', { ns: 'animals' })}</div>`;
  }
}

// 体重推移グラフを描画
function renderWeightChart(container, weightData) {
  // グラフとテーブルの両方を表示
  let html = `
    <div class="space-y-6">
      <!-- グラフ -->
      <div class="bg-white p-4 rounded-lg border border-gray-200">
        <h3 class="text-lg font-medium text-gray-900 mb-4">${translate('weight_chart.graph_title', { ns: 'animals' })}</h3>
        <canvas id="weightChart" class="w-full" style="max-height: 400px;"></canvas>
      </div>

      <!-- テーブル -->
      <div class="bg-white p-4 rounded-lg border border-gray-200">
        <h3 class="text-lg font-medium text-gray-900 mb-4">${translate('weight_chart.data_title', { ns: 'animals' })}</h3>
        <div class="overflow-x-auto">
          <table class="w-full">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-4 py-2 text-left text-sm font-medium text-gray-700">${translate('weight_chart.date', { ns: 'animals' })}</th>
                <th class="px-4 py-2 text-right text-sm font-medium text-gray-700">${translate('weight_chart.weight_kg', { ns: 'animals' })}</th>
                <th class="px-4 py-2 text-right text-sm font-medium text-gray-700">${translate('weight_chart.change', { ns: 'animals' })}</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-200">
  `;

  weightData.forEach((data, index) => {
    let change = '';
    let changeClass = '';

    if (index > 0) {
      const diff = data.weight - weightData[index - 1].weight;
      const percent = (diff / weightData[index - 1].weight) * 100;

      if (diff > 0) {
        change = `+${diff.toFixed(2)}kg (${percent.toFixed(1)}%)`;
        changeClass = 'text-green-600';
      } else if (diff < 0) {
        change = `${diff.toFixed(2)}kg (${percent.toFixed(1)}%)`;
        changeClass = 'text-red-600';
      } else {
        change = translate('weight_chart.no_change', { ns: 'animals' });
        changeClass = 'text-gray-500';
      }

      // 10%以上の変化は警告
      if (Math.abs(percent) >= 10) {
        changeClass = 'text-red-600 font-bold';
        change += ' ⚠️';
      }
    }

    html += `
      <tr>
        <td class="px-4 py-2 text-sm text-gray-900">${data.date}</td>
        <td class="px-4 py-2 text-sm text-gray-900 text-right">${data.weight.toFixed(2)}</td>
        <td class="px-4 py-2 text-sm ${changeClass} text-right">${change}</td>
      </tr>
    `;
  });

  html += `
            </tbody>
          </table>
        </div>
        <div class="mt-4 text-sm text-gray-600">
          <p>${translate('weight_chart.warning_message', { ns: 'animals' })}</p>
        </div>
      </div>
    </div>
  `;

  container.innerHTML = html;

  // DOMが更新された後にChart.jsでグラフを描画
  setTimeout(() => {
    drawWeightChart(weightData);
  }, 100);
}

// Chart.jsで体重グラフを描画
function drawWeightChart(weightData) {
  const canvas = document.getElementById('weightChart');
  if (!canvas) return;

  const ctx = canvas.getContext('2d');

  // 既存のチャートがあれば破棄
  if (window.weightChartInstance) {
    window.weightChartInstance.destroy();
  }

  // データの準備
  const labels = weightData.map(d => d.date);
  const weights = weightData.map(d => d.weight);

  // 最小値と最大値を計算（グラフの範囲を適切に設定）
  const minWeight = Math.min(...weights);
  const maxWeight = Math.max(...weights);
  const range = maxWeight - minWeight;
  const yMin = Math.max(0, minWeight - range * 0.2);
  const yMax = maxWeight + range * 0.2;

  // Chart.jsの設定
  window.weightChartInstance = new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [
        {
          label: translate('weight_chart.tooltip_weight', { ns: 'animals' }) + ' (kg)',
          data: weights,
          borderColor: 'rgb(79, 70, 229)',
          backgroundColor: 'rgba(79, 70, 229, 0.1)',
          borderWidth: 2,
          pointRadius: 4,
          pointHoverRadius: 6,
          tension: 0.1,
          fill: true,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      aspectRatio: 2,
      plugins: {
        legend: {
          display: true,
          position: 'top',
        },
        tooltip: {
          callbacks: {
            label: function (context) {
              return `${translate('weight_chart.tooltip_weight', { ns: 'animals' })}: ${context.parsed.y.toFixed(2)}kg`;
            },
          },
        },
      },
      scales: {
        y: {
          beginAtZero: false,
          min: yMin,
          max: yMax,
          ticks: {
            callback: function (value) {
              return value.toFixed(1) + 'kg';
            },
          },
          title: {
            display: true,
            text: translate('weight_chart.axis_weight', { ns: 'animals' }),
          },
        },
        x: {
          title: {
            display: true,
            text: translate('weight_chart.axis_date', { ns: 'animals' }),
          },
        },
      },
    },
  });
}

// 注: getToken, formatDate, apiRequest, showToast等はcommon.jsで定義済み
// showAlertの代わりにshowToastを使用してください

// プロフィール画像変更機能
document.addEventListener('DOMContentLoaded', () => {
  setupProfileImageChange();
});

function setupProfileImageChange() {
  const modal = document.getElementById('profileImageModal');
  const changeBtn = document.getElementById('changeProfileImageBtn');
  const closeBtn = document.getElementById('closeModalBtn');
  const cancelBtn = document.getElementById('cancelUploadBtn');
  const fileInput = document.getElementById('modal-file-input');
  const preview = document.getElementById('modal-preview');
  const previewContainer = document.getElementById('modal-preview-container');
  const uploadBtn = document.getElementById('uploadBtn');
  const fileNameText = document.getElementById('modal-file-name');

  if (!modal || !changeBtn || !fileInput || !preview || !uploadBtn) {
    return;
  }

  const applyPlaceholderText = () => {
    if (!fileNameText) {
      return;
    }

    fileNameText.setAttribute('data-i18n', 'file_input.empty');
    fileNameText.setAttribute('data-i18n-ns', 'common');

    if (window.i18n && typeof window.i18n.translateElement === 'function') {
      window.i18n.translateElement(fileNameText);
    } else if (typeof translate === 'function') {
      fileNameText.textContent = translate('file_input.empty', { ns: 'common' });
    } else {
      fileNameText.textContent = 'No file selected';
    }

    fileNameText.classList.add('text-gray-500');
  };

  const showSelectedFileName = fileName => {
    if (!fileNameText) {
      return;
    }

    fileNameText.removeAttribute('data-i18n');
    fileNameText.removeAttribute('data-i18n-ns');
    fileNameText.textContent = fileName;
    fileNameText.classList.remove('text-gray-500');
  };

  applyPlaceholderText();

  // モーダルを開く
  changeBtn.addEventListener('click', () => {
    modal.classList.remove('hidden');
    loadGalleryImages();
  });

  // モーダルを閉じる
  const closeModal = () => {
    modal.classList.add('hidden');
    fileInput.value = '';
    previewContainer.classList.add('hidden');
    uploadBtn.disabled = true;
    applyPlaceholderText();
  };

  closeBtn.addEventListener('click', closeModal);
  cancelBtn.addEventListener('click', closeModal);

  // モーダル外クリックで閉じる
  modal.addEventListener('click', e => {
    if (e.target === modal) {
      closeModal();
    }
  });

  // タブ切り替え
  const tabButtons = document.querySelectorAll('.modal-tab');
  const tabContents = document.querySelectorAll('.modal-content');

  tabButtons.forEach(button => {
    button.addEventListener('click', () => {
      const tabId = button.id.replace('tab-', '');

      // タブの切り替え
      tabButtons.forEach(btn => {
        btn.classList.remove('active', 'border-brand-primary', 'text-brand-primary');
        btn.classList.add('border-transparent', 'text-gray-500');
      });
      button.classList.add('active', 'border-brand-primary', 'text-brand-primary');
      button.classList.remove('border-transparent', 'text-gray-500');

      // コンテンツの切り替え
      tabContents.forEach(content => {
        content.classList.add('hidden');
      });
      document.getElementById(`content-${tabId}`).classList.remove('hidden');

      // ギャラリータブの場合は画像を読み込む
      if (tabId === 'gallery') {
        loadGalleryImages();
      }
    });
  });

  // ファイル選択時のプレビュー
  fileInput.addEventListener('change', e => {
    const file = e.target.files[0];
    if (!file) {
      previewContainer.classList.add('hidden');
      uploadBtn.disabled = true;
      applyPlaceholderText();
      return;
    }

    // ファイルサイズチェック（5MB）
    if (file.size > 5 * 1024 * 1024) {
      showToast(translate('errors.file_size_limit', { ns: 'animals' }), 'error');
      fileInput.value = '';
      previewContainer.classList.add('hidden');
      uploadBtn.disabled = true;
      applyPlaceholderText();
      return;
    }

    showSelectedFileName(file.name);

    // プレビュー表示
    const reader = new FileReader();
    reader.onload = e => {
      preview.src = e.target.result;
      previewContainer.classList.remove('hidden');
      uploadBtn.disabled = false;
    };
    reader.readAsDataURL(file);
  });

  window.addEventListener('languageChanged', () => {
    if (fileInput.files.length === 0) {
      applyPlaceholderText();
    }
  });

  // アップロードボタン
  uploadBtn.addEventListener('click', async () => {
    const file = fileInput.files[0];
    if (!file) return;

    uploadBtn.disabled = true;
    const originalUploadText = uploadBtn.textContent;
    uploadBtn.textContent = translate('status_text.uploading', { ns: 'animals' });

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch(`${API_BASE}/animals/${animalId}/profile-image`, {
        method: 'PUT',
        headers: {
          Authorization: `Bearer ${getToken()}`,
        },
        body: formData,
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || translate('errors.upload_failed', { ns: 'animals' }));
      }

      const result = await response.json();

      // プロフィール画像を更新
      document.getElementById('animalPhoto').src = result.image_path;

      showToast(translate('messages.profile_image_updated', { ns: 'animals' }), 'success');
      closeModal();
    } catch (error) {
      console.error('Error uploading image:', error);
      showToast(error.message, 'error');
    } finally {
      uploadBtn.disabled = false;
      uploadBtn.textContent = originalUploadText;
    }
  });
}

// ギャラリー画像を読み込む
async function loadGalleryImages() {
  const grid = document.getElementById('gallery-grid');
  const empty = document.getElementById('gallery-empty');
  const selectLabel =
    typeof translate === 'function'
      ? translate('select', { ns: 'common', defaultValue: 'Select' })
      : 'Select';

  try {
    const response = await fetch(
      `${API_BASE}/animals/${animalId}/images?sort_by=created_at&ascending=false`,
      {
        headers: {
          Authorization: `Bearer ${getToken()}`,
        },
      }
    );

    if (!response.ok) {
      throw new Error(translate('gallery.load_error', { ns: 'animals' }));
    }

    const images = await response.json();

    if (images.length === 0) {
      grid.classList.add('hidden');
      empty.classList.remove('hidden');
      return;
    }

    grid.classList.remove('hidden');
    empty.classList.add('hidden');

    // 画像グリッドを生成
    grid.innerHTML = images
      .map(
        image => `
        <div class="relative group cursor-pointer" onclick="selectGalleryImage(${image.id}, '/media/${image.image_path}')">
          <img src="/media/${image.image_path}"
               alt="${image.description || ''}"
               class="w-full h-32 object-cover rounded-lg border-2 border-gray-300 hover:border-brand-primary transition-colors">
          <div class="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-30 transition-opacity rounded-lg flex items-center justify-center">
            <span class="text-white opacity-0 group-hover:opacity-100 font-medium">${selectLabel}</span>
          </div>
        </div>
      `
      )
      .join('');
  } catch (error) {
    console.error('Error loading gallery images:', error);
    showToast(error.message, 'error');
  }
}

// ギャラリーから画像を選択
async function selectGalleryImage(imageId, imagePath) {
  try {
    const response = await fetch(
      `${API_BASE}/animals/${animalId}/profile-image/from-gallery/${imageId}`,
      {
        method: 'PUT',
        headers: {
          Authorization: `Bearer ${getToken()}`,
          'Content-Type': 'application/json',
        },
      }
    );

    if (!response.ok) {
      const error = await response.json();
      throw new Error(
        error.detail || translate('errors.profile_image_set_failed', { ns: 'animals' })
      );
    }

    const result = await response.json();

    // プロフィール画像を更新
    document.getElementById('animalPhoto').src = result.image_path;

    showToast(translate('messages.profile_image_updated', { ns: 'animals' }), 'success');

    // モーダルを閉じる
    document.getElementById('profileImageModal').classList.add('hidden');
  } catch (error) {
    console.error('Error selecting gallery image:', error);
    showToast(error.message, 'error');
  }
}

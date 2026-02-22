/**
 * 診療記録詳細ページのJavaScript
 */

const adminBasePath = window.ADMIN_BASE_PATH || window.__ADMIN_BASE_PATH__ || '/admin';

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

// ページ読み込み時の初期化
document.addEventListener('DOMContentLoaded', () => {
  // i18nが初期化されるまで待機
  const waitForI18n = setInterval(() => {
    if (window.i18n && window.i18n.getCurrentLanguage) {
      clearInterval(waitForI18n);

      const recordId = getRecordIdFromUrl();
      if (recordId) {
        loadMedicalRecord(recordId);
      } else {
        showError(window.i18n.t('load_error', { ns: 'medical_records' }));
      }

      // 言語変更イベントをリッスン
      window.addEventListener('languageChanged', () => {
        // 動的に生成されたコンテンツを再レンダリング
        const recordId = getRecordIdFromUrl();
        if (recordId) {
          loadMedicalRecord(recordId);
        }
      });
    }
  }, 100);

  // タイムアウト（5秒）
  setTimeout(() => {
    clearInterval(waitForI18n);
    if (!window.i18n || !window.i18n.getCurrentLanguage) {
      console.warn('[medical_records_detail] i18n initialization timeout');
      const recordId = getRecordIdFromUrl();
      if (recordId) {
        loadMedicalRecord(recordId);
      } else {
        showError('診療記録IDが指定されていません');
      }
    }
  }, 5000);
});

// URLから診療記録IDを取得
function getRecordIdFromUrl() {
  const pathParts = window.location.pathname.split('/');
  return pathParts[pathParts.length - 1];
}

// 診療記録を読み込み
async function loadMedicalRecord(recordId) {
  showLoading();
  hideError();

  try {
    const response = await fetch(`/api/v1/medical-records/${recordId}`, {
      headers: {
        Authorization: `Bearer ${getToken()}`,
      },
    });

    if (!response.ok) {
      if (response.status === 404) {
        const noDataMsg =
          window.i18n && window.i18n.t
            ? window.i18n.t('no_data', { ns: 'common' })
            : 'データがありません';
        throw new Error(noDataMsg);
      }
      const errorMsg =
        window.i18n && window.i18n.t
          ? window.i18n.t('load_error', { ns: 'medical_records' })
          : '読み込みに失敗しました';
      throw new Error(errorMsg);
    }

    const record = await response.json();
    renderMedicalRecord(record);
  } catch (error) {
    console.error('Error loading medical record:', error);
    showError(error.message);
  } finally {
    hideLoading();
  }
}

// 診療記録を表示
function renderMedicalRecord(record) {
  const t = key =>
    window.i18n && window.i18n.t ? window.i18n.t(key, { ns: 'medical_records' }) : key;
  const notAvailable = t('dynamic.not_available');

  const container = requireElementById('recordDetail', 'medical_records_detail.page');
  container.innerHTML = '';
  const content = cloneTemplate('tmpl-medical-record-detail');
  assertRequiredSelectors(
    content,
    [
      '.js-date',
      '.js-time-slot',
      '.js-animal',
      '.js-vet',
      '.js-weight',
      '.js-temperature',
      '.js-symptoms',
      '.js-medical-action-section',
      '.js-medical-action',
      '.js-dosage',
      '.js-billing',
      '.js-other-section',
      '.js-other',
      '.js-comment-section',
      '.js-comment',
      '.js-created-at',
      '.js-updated-at',
    ],
    'medical_records_detail.tmpl-medical-record-detail'
  );

  // 基本情報
  requireSelector(
    content,
    '.js-date',
    'medical_records_detail.tmpl-medical-record-detail'
  ).textContent = record.date;
  requireSelector(
    content,
    '.js-time-slot',
    'medical_records_detail.tmpl-medical-record-detail'
  ).textContent = record.time_slot || notAvailable;

  // 猫名を表示（リンク付き）
  const animalText = record.animal_name || `${t('dynamic.cat_id')}: ${record.animal_id}`;
  if (record.animal_name) {
    const animalLink = document.createElement('a');
    animalLink.href = `${adminBasePath}/animals/${record.animal_id}`;
    animalLink.className = 'text-brand-primary hover:text-brand-primary-dark';
    animalLink.textContent = animalText;
    requireSelector(
      content,
      '.js-animal',
      'medical_records_detail.tmpl-medical-record-detail'
    ).appendChild(animalLink);
  } else {
    requireSelector(
      content,
      '.js-animal',
      'medical_records_detail.tmpl-medical-record-detail'
    ).textContent = animalText;
  }

  // 獣医師名を表示
  requireSelector(
    content,
    '.js-vet',
    'medical_records_detail.tmpl-medical-record-detail'
  ).textContent = record.vet_name || `${t('dynamic.vet_id')}: ${record.vet_id}`;

  // 測定値
  requireSelector(
    content,
    '.js-weight',
    'medical_records_detail.tmpl-medical-record-detail'
  ).textContent = record.weight ? `${record.weight}${t('dynamic.kg')}` : notAvailable;
  requireSelector(
    content,
    '.js-temperature',
    'medical_records_detail.tmpl-medical-record-detail'
  ).textContent = record.temperature
    ? `${record.temperature}${t('dynamic.celsius')}`
    : notAvailable;

  // 症状
  requireSelector(
    content,
    '.js-symptoms',
    'medical_records_detail.tmpl-medical-record-detail'
  ).textContent = record.symptoms;

  // 診療行為
  if (record.medical_action_name) {
    const section = requireSelector(
      content,
      '.js-medical-action-section',
      'medical_records_detail.tmpl-medical-record-detail'
    );
    section.classList.remove('hidden');
    requireSelector(
      content,
      '.js-medical-action',
      'medical_records_detail.tmpl-medical-record-detail'
    ).textContent = record.medical_action_name;

    const dosageText = record.dosage ? `${record.dosage}${record.dosage_unit || ''}` : notAvailable;
    requireSelector(
      content,
      '.js-dosage',
      'medical_records_detail.tmpl-medical-record-detail'
    ).textContent = dosageText;

    // 請求価格
    const billingText = record.billing_amount
      ? `${t('dynamic.yen')}${Number(record.billing_amount).toLocaleString()}`
      : notAvailable;
    requireSelector(
      content,
      '.js-billing',
      'medical_records_detail.tmpl-medical-record-detail'
    ).textContent = billingText;
  }

  // その他
  if (record.other) {
    const section = requireSelector(
      content,
      '.js-other-section',
      'medical_records_detail.tmpl-medical-record-detail'
    );
    section.classList.remove('hidden');
    requireSelector(
      content,
      '.js-other',
      'medical_records_detail.tmpl-medical-record-detail'
    ).textContent = record.other;
  }

  // コメント
  if (record.comment) {
    const section = requireSelector(
      content,
      '.js-comment-section',
      'medical_records_detail.tmpl-medical-record-detail'
    );
    section.classList.remove('hidden');
    requireSelector(
      content,
      '.js-comment',
      'medical_records_detail.tmpl-medical-record-detail'
    ).textContent = record.comment;
  }

  // タイムスタンプ
  requireSelector(
    content,
    '.js-created-at',
    'medical_records_detail.tmpl-medical-record-detail'
  ).textContent = formatDateTime(record.created_at);
  requireSelector(
    content,
    '.js-updated-at',
    'medical_records_detail.tmpl-medical-record-detail'
  ).textContent = formatDateTime(record.last_updated_at);

  translateDynamicElement(content);
  container.appendChild(content);
  container.classList.remove('hidden');

  // 修正ボタンを表示設定（ボタン自体はheader_actionsにあるのでここではURLのみ更新）
  const editBtn = document.getElementById('editBtn');
  if (editBtn) {
    editBtn.classList.remove('hidden');
    // 既存のリスナーを削除するために新しく作り直すか、単にクリック時リダイレクトにする
    editBtn.onclick = () => {
      window.location.href = `${adminBasePath}/medical-records/${record.id}/edit`;
    };
  }
}

// 注: formatDateTime, getToken等はcommon.jsで定義済み
// (common.jsのformatDateTimeが自動的に言語を検出)

// ローディング表示
function showLoading() {
  document.getElementById('loadingIndicator').classList.remove('hidden');
  document.getElementById('recordDetail').classList.add('hidden');
}

function hideLoading() {
  document.getElementById('loadingIndicator').classList.add('hidden');
}

// エラー表示
function showError(message) {
  const errorDiv = document.getElementById('errorMessage');
  const translatedMessage =
    message.includes('medical_records') || message.includes('common') ? message : message;
  errorDiv.querySelector('p').textContent = translatedMessage;
  errorDiv.classList.remove('hidden');
  document.getElementById('recordDetail').classList.add('hidden');
}

function hideError() {
  document.getElementById('errorMessage').classList.add('hidden');
}

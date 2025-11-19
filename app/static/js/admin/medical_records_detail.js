/**
 * 診療記録詳細ページのJavaScript
 */

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

  // 基本情報
  document.getElementById('recordDate').textContent = record.date;
  document.getElementById('recordTimeSlot').textContent = record.time_slot || notAvailable;

  // 猫名を表示（リンク付き）
  const animalText = record.animal_name || `${t('dynamic.cat_id')}: ${record.animal_id}`;
  const animalLink = record.animal_name
    ? `<a href="/admin/animals/${record.animal_id}" class="text-indigo-600 hover:text-indigo-900">${animalText}</a>`
    : animalText;
  document.getElementById('recordAnimal').innerHTML = animalLink;

  // 獣医師名を表示
  document.getElementById('recordVet').textContent =
    record.vet_name || `${t('dynamic.vet_id')}: ${record.vet_id}`;

  // 測定値
  document.getElementById('recordWeight').textContent = record.weight
    ? `${record.weight}${t('dynamic.kg')}`
    : notAvailable;
  document.getElementById('recordTemperature').textContent = record.temperature
    ? `${record.temperature}${t('dynamic.celsius')}`
    : notAvailable;

  // 症状
  document.getElementById('recordSymptoms').textContent = record.symptoms;

  // 診療行為
  if (record.medical_action_name) {
    document.getElementById('medicalActionSection').classList.remove('hidden');
    document.getElementById('recordMedicalAction').textContent = record.medical_action_name;

    const dosageText = record.dosage ? `${record.dosage}${record.dosage_unit || ''}` : notAvailable;
    document.getElementById('recordDosage').textContent = dosageText;

    // 請求価格
    const billingText = record.billing_amount
      ? `${t('dynamic.yen')}${Number(record.billing_amount).toLocaleString()}`
      : notAvailable;
    document.getElementById('recordBilling').textContent = billingText;
  }

  // その他
  if (record.other) {
    document.getElementById('otherSection').classList.remove('hidden');
    document.getElementById('recordOther').textContent = record.other;
  }

  // コメント
  if (record.comment) {
    document.getElementById('commentSection').classList.remove('hidden');
    document.getElementById('recordComment').textContent = record.comment;
  }

  // タイムスタンプ
  document.getElementById('recordCreatedAt').textContent = formatDateTime(record.created_at);
  document.getElementById('recordUpdatedAt').textContent = formatDateTime(record.last_updated_at);

  // 詳細を表示
  document.getElementById('recordDetail').classList.remove('hidden');

  // 修正ボタンを表示して、クリックイベントを設定
  const editBtn = document.getElementById('editBtn');
  if (editBtn) {
    editBtn.classList.remove('hidden');
    editBtn.addEventListener('click', () => {
      window.location.href = `/admin/medical-records/${record.id}/edit`;
    });
  }
}

// 日時フォーマット
function formatDateTime(dateTimeStr) {
  const date = new Date(dateTimeStr);
  const currentLanguage = window.i18n ? window.i18n.getCurrentLanguage() : 'ja';
  const locale = currentLanguage === 'en' ? 'en-US' : 'ja-JP';

  return date.toLocaleString(locale, {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  });
}

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

// トークン取得
function getToken() {
  return localStorage.getItem('access_token');
}

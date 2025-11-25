/**
 * 診療記録修正ページのJavaScript
 */

let recordId = null;
let medicalActionsData = [];
const isKiroweenMode = document.body && document.body.classList.contains('kiroween-mode');

// ページ読み込み時の初期化
document.addEventListener('DOMContentLoaded', () => {
  applyKiroweenHints();
  // i18nが初期化されるまで待機
  const waitForI18n = setInterval(() => {
    if (window.i18n && window.i18n.getCurrentLanguage) {
      clearInterval(waitForI18n);

      recordId = getRecordIdFromUrl();
      if (recordId) {
        loadMedicalRecord(recordId);
        loadMedicalActions();
      } else {
        const errorMsg = window.i18n.t('load_error', { ns: 'medical_records' });
        showError(errorMsg);
      }

      // 言語変更イベントをリッスン（ページの再読み込みは不要）
      window.addEventListener('languageChanged', () => {
        // 言語切り替え時は、ページの再読み込みは不要
        // テンプレートの data-i18n 属性が自動的に翻訳される
        applyKiroweenHints();
      });
    }
  }, 100);

  // タイムアウト（5秒）
  setTimeout(() => {
    clearInterval(waitForI18n);
    if (!window.i18n || !window.i18n.getCurrentLanguage) {
      console.warn('[medical_record_edit] i18n initialization timeout');
      recordId = getRecordIdFromUrl();
      if (recordId) {
        loadMedicalRecord(recordId);
        loadMedicalActions();
      } else {
        showError('診療記録IDが指定されていません');
      }
    }
  }, 5000);
});

function applyKiroweenHints() {
  const hint = document.getElementById('temperatureRangeHint');
  if (!hint) {
    return;
  }

  if (!hint.dataset.originalText) {
    hint.dataset.originalText = hint.textContent;
  }
  if (!hint.dataset.originalI18nKey && hint.getAttribute('data-i18n')) {
    hint.dataset.originalI18nKey = hint.getAttribute('data-i18n');
  }
  if (!hint.dataset.originalI18nNs && hint.getAttribute('data-i18n-ns')) {
    hint.dataset.originalI18nNs = hint.getAttribute('data-i18n-ns');
  }

  if (isKiroweenMode) {
    hint.textContent = 'Normal range: 35.0 - 42.0℃';
    if (hint.dataset.originalI18nKey) {
      hint.removeAttribute('data-i18n');
    }
    if (hint.dataset.originalI18nNs) {
      hint.removeAttribute('data-i18n-ns');
    }
  } else {
    hint.textContent = hint.dataset.originalText || hint.textContent;
    if (hint.dataset.originalI18nKey) {
      hint.setAttribute('data-i18n', hint.dataset.originalI18nKey);
    }
    if (hint.dataset.originalI18nNs) {
      hint.setAttribute('data-i18n-ns', hint.dataset.originalI18nNs);
    }
  }
}

// URLから診療記録IDを取得
function getRecordIdFromUrl() {
  const pathParts = window.location.pathname.split('/');
  return pathParts[pathParts.length - 2]; // /admin/medical-records/{id}/edit
}

// 診療記録を読み込み
async function loadMedicalRecord(id) {
  showLoading();
  hideError();

  try {
    const response = await fetch(`/api/v1/medical-records/${id}`, {
      headers: {
        Authorization: `Bearer ${getToken()}`,
      },
    });

    if (!response.ok) {
      if (response.status === 404) {
        const notFoundMsg =
          window.i18n && window.i18n.t
            ? window.i18n.t('no_data', { ns: 'common' })
            : '診療記録が見つかりません';
        throw new Error(notFoundMsg);
      }
      const errorMsg =
        window.i18n && window.i18n.t
          ? window.i18n.t('load_error', { ns: 'medical_records' })
          : '診療記録の取得に失敗しました';
      throw new Error(errorMsg);
    }

    const record = await response.json();
    populateForm(record);
  } catch (error) {
    console.error('Error loading medical record:', error);
    // エラーメッセージを翻訳
    let displayMessage = error.message;
    if (window.i18n && window.i18n.t) {
      if (error.message.includes('見つかりません') || error.message.includes('not found')) {
        displayMessage = window.i18n.t('no_data', { ns: 'common' });
      } else {
        displayMessage = window.i18n.t('load_error', { ns: 'medical_records' });
      }
    }
    showError(displayMessage);
  } finally {
    hideLoading();
  }
}

// フォームにデータを設定
function populateForm(record) {
  document.getElementById('date').value = record.date;
  document.getElementById('timeSlot').value = record.time_slot || '';
  document.getElementById('weight').value = record.weight || '';
  document.getElementById('temperature').value = record.temperature || '';
  document.getElementById('symptoms').value = record.symptoms;
  document.getElementById('comment').value = record.comment || '';
  document.getElementById('medicalActionId').value = record.medical_action_id || '';
  document.getElementById('dosage').value = record.dosage || '';
  document.getElementById('other').value = record.other || '';

  // フォームを表示
  document.getElementById('editForm').classList.remove('hidden');

  // フォーム送信イベントを設定
  const form = document.getElementById('medicalRecordForm');
  form.addEventListener('submit', handleSubmit);
}

// 診療行為一覧を読み込み
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

    // 既存のオプションをクリア（「選択してください」以外）
    while (select.options.length > 1) {
      select.remove(1);
    }

    data.forEach(action => {
      const option = document.createElement('option');
      option.value = action.id;
      option.textContent = `${action.name} (${action.selling_price} ${action.currency})`;
      select.appendChild(option);
    });

    // 診療行為選択時のイベントリスナー
    select.addEventListener('change', handleMedicalActionChange);
  } catch (error) {
    console.error('Error loading medical actions:', error);
  }
}

// 診療行為選択時の処理
function handleMedicalActionChange(e) {
  const actionId = parseInt(e.target.value);
  const dosageLabel = document.querySelector('label[for="dosage"]');

  if (actionId && dosageLabel) {
    const action = medicalActionsData.find(a => a.id === actionId);
    if (action && action.unit) {
      dosageLabel.innerHTML = `投薬回数 <span class="text-sm text-gray-500">(${action.unit})</span>`;
    } else {
      dosageLabel.textContent = '投薬回数';
    }
  } else if (dosageLabel) {
    dosageLabel.textContent = '投薬回数';
  }
}

// フォーム送信処理
async function handleSubmit(e) {
  e.preventDefault();

  const formData = {
    date: document.getElementById('date').value || null,
    time_slot: document.getElementById('timeSlot').value || null,
    weight: document.getElementById('weight').value
      ? parseFloat(document.getElementById('weight').value)
      : null,
    temperature: document.getElementById('temperature').value
      ? parseFloat(document.getElementById('temperature').value)
      : null,
    symptoms: document.getElementById('symptoms').value || null,
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
    const response = await fetch(`/api/v1/medical-records/${recordId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${getToken()}`,
      },
      body: JSON.stringify(formData),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || '更新に失敗しました');
    }

    // 成功したら詳細画面に遷移
    window.location.href = `/admin/medical-records/${recordId}`;
  } catch (error) {
    console.error('Error submitting form:', error);
    showError(error.message);
  }
}

// ローディング表示
function showLoading() {
  document.getElementById('loadingIndicator').classList.remove('hidden');
  document.getElementById('editForm').classList.add('hidden');
}

function hideLoading() {
  document.getElementById('loadingIndicator').classList.add('hidden');
}

// エラー表示
function showError(message) {
  const errorDiv = document.getElementById('errorMessage');
  let displayMessage = message;

  // メッセージが翻訳キーの場合は翻訳
  if (window.i18n && window.i18n.t) {
    // メッセージが翻訳キーかどうかを判定
    if (message === 'load_error' || message.includes('読み込みに失敗')) {
      displayMessage = window.i18n.t('load_error', { ns: 'medical_records' });
    } else if (message === 'no_data' || message.includes('データがありません')) {
      displayMessage = window.i18n.t('no_data', { ns: 'common' });
    }
  }

  errorDiv.querySelector('p').textContent = displayMessage;
  errorDiv.classList.remove('hidden');
  document.getElementById('editForm').classList.add('hidden');
}

function hideError() {
  document.getElementById('errorMessage').classList.add('hidden');
}

// 注: getToken等はcommon.jsで定義済み

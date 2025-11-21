/**
 * 帳票出力画面のJavaScript
 *
 * 期間指定、形式選択、帳票生成・ダウンロード機能を提供します。
 */

// 現在選択されている帳票種別
let currentReportType = null;

// 猫一覧データ
let animalsData = [];

/**
 * ページ読み込み時の初期化
 */
document.addEventListener('DOMContentLoaded', function () {
  // 猫一覧を取得
  loadAnimals();

  // フォーム送信イベント
  document.getElementById('generate-form').addEventListener('submit', handleFormSubmit);

  // デフォルトの日付を設定（今月）
  setDateRange('this_month');
});

/**
 * 猫一覧を取得
 */
async function loadAnimals() {
  try {
    const data = await apiRequest('/api/v1/animals?limit=1000');
    if (!data) return; // 401エラーでログアウト済み

    animalsData = data.items || [];

    // セレクトボックスに追加
    const select = document.getElementById('animal-id');
    select.innerHTML = '<option value="">猫を選択してください</option>';

    animalsData.forEach(animal => {
      const option = document.createElement('option');
      option.value = animal.id;
      option.textContent = `${animal.name || '名前なし'} (ID: ${animal.id})`;
      select.appendChild(option);
    });
  } catch (error) {
    console.error('猫一覧の取得エラー:', error);
    showError('猫一覧の取得に失敗しました');
  }
}

/**
 * 帳票種別を選択
 */
function selectReportType(type) {
  currentReportType = type;

  // フォームを表示
  document.getElementById('report-form').classList.remove('hidden');

  // 帳票種別を設定
  document.getElementById('report-type').value = type;

  // タイトルを更新
  const titles = {
    daily: '日報生成',
    weekly: '週報生成',
    monthly: '月次集計生成',
    individual: '個別帳票生成',
  };
  document.getElementById('form-title').textContent = titles[type] || '帳票生成';

  // 個別帳票の場合は猫選択を表示
  const animalSelectGroup = document.getElementById('animal-select-group');
  if (type === 'individual') {
    animalSelectGroup.classList.remove('hidden');
    document.getElementById('animal-id').required = true;
  } else {
    animalSelectGroup.classList.add('hidden');
    document.getElementById('animal-id').required = false;
  }

  // フォームまでスクロール
  document.getElementById('report-form').scrollIntoView({ behavior: 'smooth' });
}

/**
 * 日付範囲を設定
 */
function setDateRange(preset) {
  const today = new Date();
  let startDate, endDate;

  switch (preset) {
    case 'today':
      startDate = endDate = today;
      break;

    case 'this_week':
      // 今週の月曜日から日曜日
      const dayOfWeek = today.getDay();
      const monday = new Date(today);
      monday.setDate(today.getDate() - (dayOfWeek === 0 ? 6 : dayOfWeek - 1));
      startDate = monday;
      endDate = today;
      break;

    case 'this_month':
      // 今月の1日から今日まで
      startDate = new Date(today.getFullYear(), today.getMonth(), 1);
      endDate = today;
      break;

    case 'last_month':
      // 先月の1日から末日まで
      startDate = new Date(today.getFullYear(), today.getMonth() - 1, 1);
      endDate = new Date(today.getFullYear(), today.getMonth(), 0);
      break;

    case 'last_3_months':
      // 3ヶ月前の1日から今日まで
      startDate = new Date(today.getFullYear(), today.getMonth() - 3, 1);
      endDate = today;
      break;

    case 'last_6_months':
      // 6ヶ月前の1日から今日まで
      startDate = new Date(today.getFullYear(), today.getMonth() - 6, 1);
      endDate = today;
      break;

    case 'this_year':
      // 今年の1月1日から今日まで
      startDate = new Date(today.getFullYear(), 0, 1);
      endDate = today;
      break;

    default:
      return;
  }

  // 日付フィールドに設定
  document.getElementById('start-date').valueAsDate = startDate;
  document.getElementById('end-date').valueAsDate = endDate;
}

/**
 * フォームをキャンセル
 */
function cancelForm() {
  document.getElementById('report-form').classList.add('hidden');
  document.getElementById('generate-form').reset();
  currentReportType = null;
}

/**
 * フォーム送信処理
 */
async function handleFormSubmit(event) {
  event.preventDefault();

  const formData = new FormData(event.target);
  const reportType = formData.get('report_type');
  const startDate = formData.get('start_date');
  const endDate = formData.get('end_date');
  const format = formData.get('format');
  const animalId = formData.get('animal_id');

  // バリデーション
  if (!reportType || !startDate || !endDate || !format) {
    showError('必須項目を入力してください');
    return;
  }

  if (reportType === 'individual' && !animalId) {
    showError('猫を選択してください');
    return;
  }

  if (new Date(startDate) > new Date(endDate)) {
    showError('開始日は終了日より前の日付を指定してください');
    return;
  }

  // ローディング表示
  showLoading();

  try {
    // 帳票を生成・ダウンロード
    await generateReport(reportType, startDate, endDate, format, animalId);

    showSuccess('帳票を生成しました');

    // フォームをリセット
    setTimeout(() => {
      cancelForm();
    }, 2000);
  } catch (error) {
    console.error('帳票生成エラー:', error);
    showError(error.message || '帳票の生成に失敗しました');
  } finally {
    hideLoading();
  }
}

/**
 * 帳票を生成・ダウンロード
 */
async function generateReport(reportType, startDate, endDate, format, animalId) {
  const token = getAccessToken();

  if (!token) {
    throw new Error('認証トークンが見つかりません。再ログインしてください。');
  }

  // フォーマット別の処理
  if (format === 'pdf') {
    await generatePDFReport(reportType, startDate, endDate, animalId, token);
  } else if (format === 'csv') {
    await generateCSVReport(reportType, startDate, endDate, animalId, token);
  } else if (format === 'excel') {
    await generateExcelReport(reportType, startDate, endDate, animalId, token);
  }
}

/**
 * PDF帳票を生成
 */
async function generatePDFReport(reportType, startDate, endDate, animalId, token) {
  const response = await fetch('/api/v1/pdf/report', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({
      report_type: reportType,
      start_date: startDate,
      end_date: endDate,
      animal_id: animalId ? parseInt(animalId) : null,
    }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'PDF生成に失敗しました');
  }

  // PDFをダウンロード
  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `report_${reportType}_${startDate}_${endDate}.pdf`;
  document.body.appendChild(a);
  a.click();
  window.URL.revokeObjectURL(url);
  document.body.removeChild(a);
}

/**
 * CSV帳票を生成
 */
async function generateCSVReport(reportType, startDate, endDate, animalId, token) {
  const response = await fetch('/api/v1/reports/export', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({
      report_type: reportType,
      start_date: startDate,
      end_date: endDate,
      animal_id: animalId ? parseInt(animalId) : null,
      format: 'csv',
    }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'CSV生成に失敗しました');
  }

  // CSVをダウンロード
  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `report_${reportType}_${startDate}_${endDate}.csv`;
  document.body.appendChild(a);
  a.click();
  window.URL.revokeObjectURL(url);
  document.body.removeChild(a);
}

/**
 * Excel帳票を生成
 */
async function generateExcelReport(reportType, startDate, endDate, animalId, token) {
  const response = await fetch('/api/v1/reports/export', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({
      report_type: reportType,
      start_date: startDate,
      end_date: endDate,
      animal_id: animalId ? parseInt(animalId) : null,
      format: 'excel',
    }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Excel生成に失敗しました');
  }

  // Excelをダウンロード
  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `report_${reportType}_${startDate}_${endDate}.xlsx`;
  document.body.appendChild(a);
  a.click();
  window.URL.revokeObjectURL(url);
  document.body.removeChild(a);
}

/**
 * エラーメッセージを表示
 */
function showError(message) {
  const errorDiv = document.getElementById('error-message');
  const errorText = document.getElementById('error-text');
  errorText.textContent = message;
  errorDiv.classList.remove('hidden');

  // 3秒後に非表示
  setTimeout(() => {
    errorDiv.classList.add('hidden');
  }, 3000);

  // エラーメッセージまでスクロール
  errorDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

/**
 * 成功メッセージを表示
 */
function showSuccess(message) {
  const successDiv = document.getElementById('success-message');
  const successText = document.getElementById('success-text');
  successText.textContent = message;
  successDiv.classList.remove('hidden');

  // 3秒後に非表示
  setTimeout(() => {
    successDiv.classList.add('hidden');
  }, 3000);
}

/**
 * ローディングを表示
 */
function showLoading() {
  document.getElementById('loading-indicator').classList.remove('hidden');
}

/**
 * ローディングを非表示
 */
function hideLoading() {
  document.getElementById('loading-indicator').classList.add('hidden');
}

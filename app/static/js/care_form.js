/**
 * 世話記録入力フォームのJavaScript
 *
 * 猫の世話記録を入力するフォームの動作を制御します。
 * オフライン対応、前回値コピー、バリデーションなどの機能を提供します。
 */

// URLからanimal_idを取得
const urlParams = new URLSearchParams(window.location.search);
const animalId = urlParams.get('animal_id');

if (!animalId) {
  showError('猫のIDが指定されていません');
}

// 記録日に今日の日付を設定
document.getElementById('logDate').value = getTodayString();

/**
 * 猫情報を取得して表示
 */
async function loadAnimalInfo() {
  try {
    const response = await fetch(`${API_BASE}/animals/${animalId}`);
    if (!response.ok) throw new Error('猫情報の取得に失敗しました');

    const animal = await response.json();
    document.getElementById('animalName').textContent = animal.name || '名前未設定';

    // 画像のフォールバック処理
    const photoElement = document.getElementById('animalPhoto');
    const photoUrl =
      animal.photo && animal.photo.trim() !== '' ? animal.photo : '/static/images/default.svg';
    photoElement.src = photoUrl;
    photoElement.onerror = function () {
      this.onerror = null; // 無限ループ防止
      this.src = '/static/images/default.svg';
    };
  } catch (error) {
    showError(error.message);
  }
}

/**
 * ボランティア一覧を取得してセレクトボックスに設定
 */
async function loadVolunteers() {
  try {
    const response = await fetch(`${API_BASE}/volunteers`);
    if (!response.ok) throw new Error('ボランティア一覧の取得に失敗しました');

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
        btn.classList.remove('selected', 'border-indigo-600', 'bg-indigo-100', 'text-indigo-700');
        btn.classList.add('border-gray-300');
      });

      // クリックされたボタンを選択状態に
      button.classList.add('selected', 'border-indigo-600', 'bg-indigo-100', 'text-indigo-700');
      button.classList.remove('border-gray-300');

      // hidden inputに値を設定
      input.value = button.dataset.value;
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
        showSuccess('前回の記録がありません（初回記録です）');
        return;
      }
      throw new Error('前回値の取得に失敗しました');
    }

    const lastLog = await response.json();

    // 各フィールドに値を設定
    // 記録日は今日の日付を維持（コピーしない）

    if (lastLog.time_slot) {
      const timeSlotBtn = document.querySelector(
        `.time-slot-btn[data-value="${lastLog.time_slot}"]`
      );
      if (timeSlotBtn) timeSlotBtn.click();
    }

    if (lastLog.appetite) {
      const appetiteBtn = document.querySelector(`.appetite-btn[data-value="${lastLog.appetite}"]`);
      if (appetiteBtn) appetiteBtn.click();
    }

    if (lastLog.energy) {
      const energyBtn = document.querySelector(`.energy-btn[data-value="${lastLog.energy}"]`);
      if (energyBtn) energyBtn.click();
    }

    if (lastLog.urination !== null) {
      const urinationBtn = document.querySelector(
        `.urination-btn[data-value="${lastLog.urination}"]`
      );
      if (urinationBtn) urinationBtn.click();
    }

    if (lastLog.cleaning !== null) {
      const cleaningBtn = document.querySelector(`.cleaning-btn[data-value="${lastLog.cleaning}"]`);
      if (cleaningBtn) cleaningBtn.click();
    }

    // メモはコピーしない（毎回異なる可能性が高いため）

    showSuccess('前回値をコピーしました');
  } catch (error) {
    showError(error.message);
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
    btn.classList.remove('selected', 'border-indigo-600', 'bg-indigo-100', 'text-indigo-700');
    btn.classList.add('border-gray-300');
  });
  // hidden inputをクリア
  ['timeSlot', 'appetite', 'energy', 'urination', 'cleaning'].forEach(id => {
    document.getElementById(id).value = '';
  });
}

/**
 * フォーム送信処理（オフライン対応）
 */
async function handleSubmit(e) {
  e.preventDefault();

  const submitBtn = document.getElementById('submitBtn');
  submitBtn.disabled = true;
  submitBtn.textContent = '保存中...';

  try {
    // ボランティア情報を取得
    const volunteerSelect = document.getElementById('volunteer');
    const selectedOption = volunteerSelect.options[volunteerSelect.selectedIndex];
    const recorderName = selectedOption.textContent;

    const formData = {
      animal_id: parseInt(animalId),
      log_date: document.getElementById('logDate').value,
      time_slot: document.getElementById('timeSlot').value,
      appetite: parseInt(document.getElementById('appetite').value),
      energy: parseInt(document.getElementById('energy').value),
      urination:
        document.getElementById('urination').value === 'true'
          ? true
          : document.getElementById('urination').value === 'false'
            ? false
            : null,
      cleaning:
        document.getElementById('cleaning').value === 'true'
          ? true
          : document.getElementById('cleaning').value === 'false'
            ? false
            : null,
      notes: document.getElementById('notes').value || null,
      recorder_id: parseInt(document.getElementById('volunteer').value),
      recorder_name: recorderName,
    };

    // オフラインマネージャーを使用して保存
    const result = await window.offlineManager.saveCareLog(formData);

    if (result.online) {
      showSuccess('記録を保存しました');
    } else {
      showSuccess('記録を一時保存しました（オンライン時に自動同期されます）');
    }

    // フォームをリセット
    setTimeout(() => {
      resetForm();
      hideSuccess();
    }, 2000);
  } catch (error) {
    showError(error.message);
  } finally {
    submitBtn.disabled = false;
    submitBtn.textContent = '保存';
  }
}

// 初期化処理
document.addEventListener('DOMContentLoaded', () => {
  // 各ボタングループを初期化
  setupButtonGroup('time-slot-btn', 'timeSlot');
  setupButtonGroup('appetite-btn', 'appetite');
  setupButtonGroup('energy-btn', 'energy');
  setupButtonGroup('urination-btn', 'urination');
  setupButtonGroup('cleaning-btn', 'cleaning');

  // 前回値コピーボタン
  document.getElementById('copyLastBtn').addEventListener('click', copyLastValues);

  // フォーム送信
  document.getElementById('careForm').addEventListener('submit', handleSubmit);

  // 記録一覧ボタンのリンクを設定
  document.getElementById('viewLogsBtn').href = `/public/care-logs?animal_id=${animalId}`;

  // データ読み込み
  loadAnimalInfo();
  loadVolunteers();
});

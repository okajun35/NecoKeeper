/**
 * 個別猫の記録一覧ページのJavaScript
 *
 * 猫の記録一覧を表示し、記録詳細をモーダルで表示します。
 */

// URLからanimal_idを取得
const urlParams = new URLSearchParams(window.location.search);
const animalId = urlParams.get('animal_id');

if (!animalId) {
  showError('猫のIDが指定されていません');
}

/**
 * 記録一覧を取得
 */
async function loadCareLogList() {
  try {
    const response = await fetch(`${API_BASE}/care-logs/animal/${animalId}`);
    if (!response.ok) throw new Error('記録一覧の取得に失敗しました');

    const data = await response.json();

    // 猫情報を表示
    document.getElementById('animalName').textContent = data.animal_name || '名前未設定';
    document.getElementById('animalPhoto').src = data.animal_photo || '/static/images/default.svg';

    // 今日の記録状況を表示
    updateTodayStatus(data.today_status);

    // 直近7日間の記録を表示
    displayRecentLogs(data.recent_logs);

    // 記録入力ボタンのリンクを設定
    document.getElementById('addRecordBtn').href = `/public/care?animal_id=${animalId}`;
  } catch (error) {
    showError(error.message);
  }
}

/**
 * 今日の記録状況を更新
 */
function updateTodayStatus(todayStatus) {
  const timeSlots = [
    { key: 'morning', iconId: 'morningIcon', statusId: 'morningStatus' },
    { key: 'noon', iconId: 'noonIcon', statusId: 'noonStatus' },
    { key: 'evening', iconId: 'eveningIcon', statusId: 'eveningStatus' },
  ];

  timeSlots.forEach(slot => {
    const icon = document.getElementById(slot.iconId);
    const statusDiv = document.getElementById(slot.statusId);

    if (todayStatus[slot.key]) {
      icon.textContent = '○';
      icon.classList.add('text-green-600');
      statusDiv.classList.add('border-green-500', 'bg-green-50');
    } else {
      icon.textContent = '×';
      icon.classList.add('text-gray-400');
      statusDiv.classList.add('border-gray-300');
    }
  });
}

/**
 * 直近7日間の記録を表示
 */
function displayRecentLogs(logs) {
  const container = document.getElementById('recentLogs');
  const noLogsDiv = document.getElementById('noLogs');

  if (logs.length === 0) {
    container.classList.add('hidden');
    noLogsDiv.classList.remove('hidden');
    return;
  }

  container.innerHTML = '';
  logs.forEach(log => {
    const logDiv = document.createElement('div');
    logDiv.className =
      'flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors cursor-pointer';
    logDiv.onclick = () => showLogDetail(log.id);

    const timeSlotEmoji = {
      morning: '🌅',
      noon: '☀️',
      evening: '🌙',
    };

    logDiv.innerHTML = `
            <div class="flex items-center gap-3">
                <div class="text-2xl">${timeSlotEmoji[log.time_slot] || '📝'}</div>
                <div>
                    <div class="font-medium text-gray-800">${formatDate(log.log_date)}</div>
                    <div class="text-sm text-gray-500">${getTimeSlotLabel(log.time_slot)} - ${log.recorder_name}</div>
                </div>
            </div>
            <div class="text-green-600 font-bold">○</div>
        `;

    container.appendChild(logDiv);
  });
}

/**
 * 記録詳細を表示（モーダル）
 */
async function showLogDetail(logId) {
  try {
    const response = await fetch(`${API_BASE}/care-logs/animal/${animalId}/${logId}`);
    if (!response.ok) throw new Error('記録詳細の取得に失敗しました');

    const log = await response.json();

    // モーダルを表示
    const modal = document.createElement('div');
    modal.className =
      'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50';
    modal.onclick = e => {
      if (e.target === modal) modal.remove();
    };

    modal.innerHTML = `
            <div class="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
                <div class="flex justify-between items-center mb-4">
                    <h3 class="text-xl font-bold text-gray-800">記録詳細</h3>
                    <button onclick="this.closest('.fixed').remove()" class="text-gray-500 hover:text-gray-700">
                        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                        </svg>
                    </button>
                </div>
                <div class="space-y-3">
                    <div class="flex justify-between py-2 border-b">
                        <span class="text-gray-600">日付</span>
                        <span class="font-medium">${formatDate(log.log_date)}</span>
                    </div>
                    <div class="flex justify-between py-2 border-b">
                        <span class="text-gray-600">時点</span>
                        <span class="font-medium">${getTimeSlotLabel(log.time_slot)}</span>
                    </div>
                    <div class="flex justify-between py-2 border-b">
                        <span class="text-gray-600">記録者</span>
                        <span class="font-medium">${log.recorder_name}</span>
                    </div>
                    <div class="flex justify-between py-2 border-b">
                        <span class="text-gray-600">食欲</span>
                        <span class="font-medium">${log.appetite} / 5</span>
                    </div>
                    <div class="flex justify-between py-2 border-b">
                        <span class="text-gray-600">元気</span>
                        <span class="font-medium">${log.energy} / 5</span>
                    </div>
                    <div class="flex justify-between py-2 border-b">
                        <span class="text-gray-600">排尿</span>
                        <span class="font-medium">${log.urination ? 'あり' : 'なし'}</span>
                    </div>
                    <div class="flex justify-between py-2 border-b">
                        <span class="text-gray-600">清掃</span>
                        <span class="font-medium">${log.cleaning ? '済' : '未'}</span>
                    </div>
                    ${
                      log.memo
                        ? `
                    <div class="py-2">
                        <div class="text-gray-600 mb-1">メモ</div>
                        <div class="text-sm text-gray-800 bg-gray-50 p-3 rounded">${log.memo}</div>
                    </div>
                    `
                        : ''
                    }
                </div>
                <button onclick="this.closest('.fixed').remove()" class="mt-6 w-full py-3 bg-gray-100 text-gray-700 rounded-lg font-medium hover:bg-gray-200 transition-colors">
                    閉じる
                </button>
            </div>
        `;

    document.body.appendChild(modal);
  } catch (error) {
    showError(error.message);
  }
}

/**
 * 日付フォーマット
 */
function formatDate(dateString) {
  const date = new Date(dateString);
  const month = date.getMonth() + 1;
  const day = date.getDate();
  const weekdays = ['日', '月', '火', '水', '木', '金', '土'];
  const weekday = weekdays[date.getDay()];
  return `${month}月${day}日（${weekday}）`;
}

/**
 * 時点ラベル
 */
function getTimeSlotLabel(timeSlot) {
  const labels = {
    morning: '朝',
    noon: '昼',
    evening: '夜',
  };
  return labels[timeSlot] || timeSlot;
}

// 初期化
loadCareLogList();

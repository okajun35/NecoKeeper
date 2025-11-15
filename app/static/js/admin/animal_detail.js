/**
 * 猫詳細ページのJavaScript
 */

document.addEventListener('DOMContentLoaded', async () => {
  const animalId = getAnimalIdFromUrl();

  if (!animalId) {
    showError('猫IDが指定されていません');
    return;
  }

  await loadAnimalDetail(animalId);
  await loadCareLogs(animalId);
});

/**
 * URLから猫IDを取得
 */
function getAnimalIdFromUrl() {
  const pathParts = window.location.pathname.split('/');
  return pathParts[pathParts.length - 1];
}

/**
 * 猫の詳細情報を読み込み
 */
async function loadAnimalDetail(animalId) {
  try {
    const animal = await apiRequest(`${API_BASE}/animals/${animalId}`);
    displayAnimalDetail(animal);
  } catch (error) {
    console.error('Error loading animal detail:', error);
    showError('猫情報の読み込みに失敗しました');
  }
}

/**
 * 猫の詳細情報を表示
 */
function displayAnimalDetail(animal) {
  const container = document.getElementById('animal-detail');

  const statusColors = {
    保護中: 'bg-yellow-100 text-yellow-800',
    治療中: 'bg-red-100 text-red-800',
    譲渡可能: 'bg-green-100 text-green-800',
    譲渡済み: 'bg-gray-100 text-gray-800',
  };

  const genderLabels = {
    male: 'オス',
    female: 'メス',
    unknown: '不明',
  };

  container.innerHTML = `
    <div class="flex flex-col md:flex-row gap-6">
      <!-- 画像 -->
      <div class="md:w-1/3">
        <img src="${animal.photo || '/static/images/default.svg'}"
             alt="${animal.name}"
             class="w-full h-64 object-cover rounded-lg">

        <!-- QRコード表示ボタン -->
        <button onclick="showQRCode(${animal.id})"
                class="mt-4 w-full px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700">
          QRコード表示
        </button>
      </div>

      <!-- 詳細情報 -->
      <div class="md:w-2/3 space-y-4">
        <div class="flex items-center gap-3">
          <h3 class="text-2xl font-bold text-gray-900">${animal.name}</h3>
          <span class="px-3 py-1 rounded-full text-sm font-medium ${statusColors[animal.status] || 'bg-gray-100 text-gray-800'}">
            ${animal.status}
          </span>
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div>
            <p class="text-sm text-gray-500">柄</p>
            <p class="text-base font-medium text-gray-900">${animal.pattern}</p>
          </div>
          <div>
            <p class="text-sm text-gray-500">性別</p>
            <p class="text-base font-medium text-gray-900">${genderLabels[animal.gender] || animal.gender}</p>
          </div>
          <div>
            <p class="text-sm text-gray-500">年齢</p>
            <p class="text-base font-medium text-gray-900">${animal.age}</p>
          </div>
          <div>
            <p class="text-sm text-gray-500">保護日</p>
            <p class="text-base font-medium text-gray-900">${animal.protected_at ? formatDate(animal.protected_at) : '-'}</p>
          </div>
          <div>
            <p class="text-sm text-gray-500">尻尾の長さ</p>
            <p class="text-base font-medium text-gray-900">${animal.tail_length || '-'}</p>
          </div>
          <div>
            <p class="text-sm text-gray-500">首輪</p>
            <p class="text-base font-medium text-gray-900">${animal.collar || '-'}</p>
          </div>
          <div>
            <p class="text-sm text-gray-500">耳カット</p>
            <p class="text-base font-medium text-gray-900">${animal.ear_cut ? 'あり' : 'なし'}</p>
          </div>
        </div>

        ${
          animal.features
            ? `
          <div>
            <p class="text-sm text-gray-500">特徴・性格</p>
            <p class="text-base text-gray-900 whitespace-pre-wrap">${animal.features}</p>
          </div>
        `
            : ''
        }

        <div class="grid grid-cols-2 gap-4 text-sm text-gray-500">
          <div>
            <p>登録日: ${formatDate(animal.created_at)}</p>
          </div>
          <div>
            <p>更新日: ${formatDate(animal.updated_at)}</p>
          </div>
        </div>
      </div>
    </div>
  `;
}

/**
 * 世話記録を読み込み
 */
async function loadCareLogs(animalId) {
  try {
    // 過去30日分の記録を取得
    const data = await apiRequest(`${API_BASE}/care-logs?animal_id=${animalId}&page_size=100`);
    displayCareLogs(data.items || [], animalId);
  } catch (error) {
    console.error('Error loading care logs:', error);
    document.getElementById('care-logs-list').innerHTML = `
      <p class="text-gray-500">世話記録の読み込みに失敗しました</p>
    `;
  }
}

/**
 * 世話記録を日付ごとにグループ化
 */
function groupCareLogsByDate(careLogs) {
  const grouped = {};

  careLogs.forEach(log => {
    if (!grouped[log.log_date]) {
      grouped[log.log_date] = {
        morning: null,
        noon: null,
        evening: null,
      };
    }
    grouped[log.log_date][log.time_slot] = log;
  });

  return grouped;
}

/**
 * 世話記録を表示
 */
function displayCareLogs(careLogs, animalId) {
  const container = document.getElementById('care-logs-list');

  if (careLogs.length === 0) {
    container.innerHTML = '<p class="text-gray-500">世話記録がありません</p>';
    return;
  }

  // 日付ごとにグループ化
  const groupedLogs = groupCareLogsByDate(careLogs);

  // 日付でソート（新しい順）
  const sortedDates = Object.keys(groupedLogs).sort((a, b) => new Date(b) - new Date(a));

  // 最新10日分のみ表示
  const displayDates = sortedDates.slice(0, 10);

  const timeSlotLabels = {
    morning: '朝',
    noon: '昼',
    evening: '夜',
  };

  container.innerHTML = `
    <div class="overflow-x-auto">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              日付
            </th>
            <th class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
              朝
            </th>
            <th class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
              昼
            </th>
            <th class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
              夜
            </th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          ${displayDates
            .map(date => {
              const logs = groupedLogs[date];
              return `
              <tr class="hover:bg-gray-50">
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  ${formatDate(date)}
                </td>
                ${['morning', 'noon', 'evening']
                  .map(timeSlot => {
                    const log = logs[timeSlot];
                    if (log) {
                      return `
                      <td class="px-6 py-4 whitespace-nowrap text-center">
                        <a href="#" onclick="showCareLogDetail(${log.id}); return false;"
                           class="inline-flex items-center justify-center w-8 h-8 rounded-full bg-green-100 text-green-600 hover:bg-green-200 transition-colors"
                           title="記録済み - クリックして詳細を表示">
                          ○
                        </a>
                      </td>
                    `;
                    } else {
                      return `
                      <td class="px-6 py-4 whitespace-nowrap text-center">
                        <a href="/admin/care-logs/new?animal_id=${animalId}&date=${date}&time_slot=${timeSlot}"
                           class="inline-flex items-center justify-center w-8 h-8 rounded-full bg-red-100 text-red-600 hover:bg-red-200 transition-colors"
                           title="未記録 - クリックして登録">
                          ×
                        </a>
                      </td>
                    `;
                    }
                  })
                  .join('')}
              </tr>
            `;
            })
            .join('')}
        </tbody>
      </table>
    </div>
  `;
}

/**
 * 世話記録の詳細を表示
 */
async function showCareLogDetail(logId) {
  try {
    const log = await apiRequest(`${API_BASE}/care-logs/${logId}`);

    const timeSlotLabels = {
      morning: '🌅 朝',
      noon: '☀️ 昼',
      evening: '🌙 夜',
    };

    // モーダルを作成
    const modal = document.createElement('div');
    modal.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';
    modal.innerHTML = `
      <div class="bg-white rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-semibold">世話記録詳細</h3>
          <button onclick="this.closest('.fixed').remove()"
                  class="text-gray-500 hover:text-gray-700">
            ✕
          </button>
        </div>

        <div class="space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <p class="text-sm text-gray-500">日付</p>
              <p class="text-base font-medium text-gray-900">${formatDate(log.log_date)}</p>
            </div>
            <div>
              <p class="text-sm text-gray-500">時間帯</p>
              <p class="text-base font-medium text-gray-900">${timeSlotLabels[log.time_slot] || log.time_slot}</p>
            </div>
            <div>
              <p class="text-sm text-gray-500">記録者</p>
              <p class="text-base font-medium text-gray-900">${log.recorder_name || '不明'}</p>
            </div>
            <div>
              <p class="text-sm text-gray-500">記録日時</p>
              <p class="text-base font-medium text-gray-900">${formatDateTime(log.created_at)}</p>
            </div>
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div>
              <p class="text-sm text-gray-500">食欲</p>
              <p class="text-base font-medium text-gray-900">${log.appetite}/5</p>
            </div>
            <div>
              <p class="text-sm text-gray-500">元気</p>
              <p class="text-base font-medium text-gray-900">${log.energy}/5</p>
            </div>
            <div>
              <p class="text-sm text-gray-500">排尿</p>
              <p class="text-base font-medium text-gray-900">${log.urination ? 'あり' : 'なし'}</p>
            </div>
            <div>
              <p class="text-sm text-gray-500">掃除</p>
              <p class="text-base font-medium text-gray-900">${log.cleaning ? '済' : '未'}</p>
            </div>
          </div>

          ${
            log.memo
              ? `
            <div>
              <p class="text-sm text-gray-500">メモ</p>
              <p class="text-base text-gray-900 whitespace-pre-wrap">${log.memo}</p>
            </div>
          `
              : ''
          }

          <div class="flex justify-end gap-2 pt-4 border-t">
            <button onclick="this.closest('.fixed').remove()"
                    class="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300">
              閉じる
            </button>
            <a href="/admin/care-logs/${logId}/edit"
               class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
              編集
            </a>
          </div>
        </div>
      </div>
    `;

    document.body.appendChild(modal);

    // 背景クリックで閉じる
    modal.addEventListener('click', e => {
      if (e.target === modal) {
        modal.remove();
      }
    });
  } catch (error) {
    console.error('Error loading care log detail:', error);
    showToast('世話記録の読み込みに失敗しました', 'error');
  }
}

/**
 * 日時をフォーマット
 */
function formatDateTime(dateTimeString) {
  const date = new Date(dateTimeString);
  return date.toLocaleString('ja-JP', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  });
}

/**
 * QRコードを表示
 */
function showQRCode(animalId) {
  const qrUrl = `${API_BASE}/animals/${animalId}/qr`;

  // モーダルを作成
  const modal = document.createElement('div');
  modal.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';
  modal.innerHTML = `
    <div class="bg-white rounded-lg p-6 max-w-md w-full mx-4">
      <div class="flex justify-between items-center mb-4">
        <h3 class="text-lg font-semibold">QRコード</h3>
        <button onclick="this.closest('.fixed').remove()"
                class="text-gray-500 hover:text-gray-700">
          ✕
        </button>
      </div>
      <div class="flex justify-center">
        <img src="${qrUrl}" alt="QRコード" class="w-64 h-64">
      </div>
      <p class="mt-4 text-sm text-gray-600 text-center">
        このQRコードをスキャンすると、世話記録入力画面が開きます
      </p>
    </div>
  `;

  document.body.appendChild(modal);

  // 背景クリックで閉じる
  modal.addEventListener('click', e => {
    if (e.target === modal) {
      modal.remove();
    }
  });
}

/**
 * 日付をフォーマット
 */
function formatDate(dateString) {
  const date = new Date(dateString);
  return date.toLocaleDateString('ja-JP', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  });
}

/**
 * エラーメッセージを表示
 */
function showError(message) {
  const container = document.getElementById('animal-detail');
  container.innerHTML = `
    <div class="bg-red-50 border border-red-200 rounded-lg p-4">
      <p class="text-red-800">${message}</p>
      <a href="/admin/animals" class="text-red-600 hover:text-red-800 underline mt-2 inline-block">
        一覧に戻る
      </a>
    </div>
  `;
}

// グローバルエクスポート
window.showCareLogDetail = showCareLogDetail;

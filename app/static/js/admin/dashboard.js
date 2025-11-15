/**
 * ダッシュボード JavaScript
 * Context7参照: /bigskysoftware/htmx (Trust Score: 90.7)
 */

// ダッシュボードデータを読み込み
async function loadDashboardData() {
  try {
    // 統計情報を取得
    await Promise.all([loadStatistics(), loadRecentLogs(), loadNeedsCare()]);
  } catch (error) {
    console.error('Dashboard load error:', error);
    showToast('データの読み込みに失敗しました', 'error');
  }
}

// 統計情報を読み込み
async function loadStatistics() {
  try {
    // 猫の統計
    const animalsResponse = await apiRequest(`${API_BASE}/animals?page=1&page_size=1000`);
    const animals = animalsResponse.items || [];

    const protectedCount = animals.filter(a => a.status === '保護中').length;
    const adoptableCount = animals.filter(a => a.status === '譲渡可能').length;

    document.getElementById('stat-protected').textContent = protectedCount;
    document.getElementById('stat-adoptable').textContent = adoptableCount;

    // 今日の記録数
    const today = formatDate(new Date());
    const logsResponse = await apiRequest(
      `${API_BASE}/care-logs?start_date=${today}&end_date=${today}&page_size=1000`
    );
    const todayLogs = logsResponse.items || [];
    document.getElementById('stat-today-logs').textContent = todayLogs.length;

    // ボランティア数
    const volunteersResponse = await apiRequest(
      `${API_BASE}/volunteers?status=active&page_size=1000`
    );
    const volunteers = volunteersResponse.items || [];
    document.getElementById('stat-volunteers').textContent = volunteers.length;
  } catch (error) {
    console.error('Statistics load error:', error);
  }
}

// 最近の世話記録を読み込み
async function loadRecentLogs() {
  try {
    const response = await apiRequest(`${API_BASE}/care-logs?page=1&page_size=5`);
    const logs = response.items || [];

    const container = document.getElementById('recent-logs');

    if (logs.length === 0) {
      container.innerHTML = '<div class="text-center text-gray-500 py-8">記録がありません</div>';
      return;
    }

    container.innerHTML = logs
      .map(
        log => `
            <div class="flex items-center gap-4 p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                <div class="flex-1">
                    <div class="flex items-center gap-2 mb-1">
                        <span class="font-medium text-gray-900">${log.animal_name || '不明'}</span>
                        <span class="text-sm text-gray-500">${getTimeSlotLabel(log.time_slot)}</span>
                    </div>
                    <div class="text-sm text-gray-600">
                        ${log.recorder_name || '不明'} • ${formatDate(new Date(log.log_date))}
                    </div>
                </div>
                <div class="flex gap-2">
                    <span class="px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded">食欲: ${log.appetite}</span>
                    <span class="px-2 py-1 text-xs bg-green-100 text-green-800 rounded">元気: ${log.energy}</span>
                </div>
            </div>
        `
      )
      .join('');
  } catch (error) {
    console.error('Recent logs load error:', error);
    document.getElementById('recent-logs').innerHTML =
      '<div class="text-center text-red-500 py-8">読み込みに失敗しました</div>';
  }
}

// 記録が必要な猫を読み込み
async function loadNeedsCare() {
  try {
    const response = await apiRequest(`${API_BASE}/public/care-logs/status/today`);
    const animals = response.animals || [];

    // 記録が不足している猫をフィルター
    const needsCare = animals.filter(
      animal => !animal.morning_recorded || !animal.noon_recorded || !animal.evening_recorded
    );

    const container = document.getElementById('needs-care');

    if (needsCare.length === 0) {
      container.innerHTML =
        '<div class="text-center text-green-600 py-8">✓ すべての猫の記録が完了しています</div>';
      return;
    }

    container.innerHTML = needsCare
      .map(animal => {
        const missing = [];
        if (!animal.morning_recorded) missing.push('朝');
        if (!animal.noon_recorded) missing.push('昼');
        if (!animal.evening_recorded) missing.push('夜');

        return `
                <div class="flex items-center gap-4 p-4 bg-yellow-50 rounded-lg border border-yellow-200">
                    <img src="${animal.animal_photo || '/static/images/default.svg'}"
                         alt="${animal.animal_name}"
                         class="w-12 h-12 rounded-full object-cover">
                    <div class="flex-1">
                        <div class="font-medium text-gray-900">${animal.animal_name}</div>
                        <div class="text-sm text-gray-600">未記録: ${missing.join(', ')}</div>
                    </div>
                    <a href="/public/care?animal_id=${animal.animal_id}"
                       target="_blank"
                       class="px-3 py-1 text-sm bg-indigo-600 text-white rounded hover:bg-indigo-700 transition-colors">
                        記録する
                    </a>
                </div>
            `;
      })
      .join('');
  } catch (error) {
    console.error('Needs care load error:', error);
    document.getElementById('needs-care').innerHTML =
      '<div class="text-center text-red-500 py-8">読み込みに失敗しました</div>';
  }
}

// ページ読み込み時に実行
document.addEventListener('DOMContentLoaded', () => {
  loadDashboardData();

  // 5分ごとに自動更新
  setInterval(loadDashboardData, 5 * 60 * 1000);
});

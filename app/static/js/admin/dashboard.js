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
    // ダッシュボード統計APIを使用
    const stats = await apiRequest(`${API_BASE}/dashboard/stats`);

    document.getElementById('stat-resident').textContent = stats.resident_count || 0;
    document.getElementById('stat-adoptable').textContent = stats.adoptable_count || 0;
    document.getElementById('stat-today-logs').textContent = stats.today_logs_count || 0;
    document.getElementById('stat-fiv').textContent = stats.fiv_positive_count || 0;
    document.getElementById('stat-felv').textContent = stats.felv_positive_count || 0;
  } catch (error) {
    console.error('Statistics load error:', error);
    // エラー時はデフォルト値を表示
    document.getElementById('stat-resident').textContent = '0';
    document.getElementById('stat-adoptable').textContent = '0';
    document.getElementById('stat-today-logs').textContent = '0';
    document.getElementById('stat-fiv').textContent = '0';
    document.getElementById('stat-felv').textContent = '0';
  }
}

// 最近の世話記録を読み込み
async function loadRecentLogs() {
  try {
    const response = await apiRequest(`${API_BASE}/care-logs?page=1&page_size=5`);
    const logs = response.items || [];

    const container = document.getElementById('recent-logs');

    if (logs.length === 0) {
      const t = key => (typeof i18next !== 'undefined' ? i18next.t(key, { ns: 'dashboard' }) : key);
      container.innerHTML = `<div class="text-center text-gray-500 py-8">${t('no_logs')}</div>`;
      return;
    }

    const t = key => (typeof i18next !== 'undefined' ? i18next.t(key, { ns: 'dashboard' }) : key);

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
                    <span class="px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded">${t('dynamic.appetite')}: ${formatAppetiteLabel(log.appetite)}</span>
                    <span class="px-2 py-1 text-xs bg-green-100 text-green-800 rounded">${t('dynamic.energy')}: ${log.energy}</span>
                </div>
            </div>
        `
      )
      .join('');
  } catch (error) {
    console.error('Recent logs load error:', error);
    const t = key => (typeof i18next !== 'undefined' ? i18next.t(key, { ns: 'dashboard' }) : key);
    document.getElementById('recent-logs').innerHTML =
      `<div class="text-center text-red-500 py-8">${t('no_logs')}</div>`;
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

    const t = key => (typeof i18next !== 'undefined' ? i18next.t(key, { ns: 'dashboard' }) : key);

    if (needsCare.length === 0) {
      container.innerHTML = `<div class="text-center text-green-600 py-8">${t('dynamic.all_recorded')}</div>`;
      return;
    }

    container.innerHTML = needsCare
      .map(animal => {
        const missing = [];
        if (!animal.morning_recorded) missing.push(t('dynamic.morning'));
        if (!animal.noon_recorded) missing.push(t('dynamic.noon'));
        if (!animal.evening_recorded) missing.push(t('dynamic.evening'));

        // Check for Kiroween mode
        const isKiroween = document.body.classList.contains('kiroween-mode');
        const defaultImage = isKiroween
          ? '/static/icons/halloween_logo_2.webp'
          : '/static/images/default.svg';

        const photoUrl =
          animal.animal_photo && animal.animal_photo.trim() !== ''
            ? animal.animal_photo
            : defaultImage;

        return `
                <div class="flex items-center gap-4 p-4 bg-yellow-50 rounded-lg border border-yellow-200">
                    <img src="${photoUrl}"
                         alt="${animal.animal_name}"
                         onerror="this.onerror=null; this.src='${defaultImage}';"
                         class="w-12 h-12 rounded-full object-cover">
                    <div class="flex-1">
                        <div class="font-medium text-gray-900">${animal.animal_name}</div>
                        <div class="text-sm text-gray-600">${t('dynamic.not_recorded')}: ${missing.join(', ')}</div>
                    </div>
                    <a href="/public/care?animal_id=${animal.animal_id}"
                       target="_blank"
                       class="px-3 py-1 text-sm bg-indigo-600 text-white rounded hover:bg-indigo-700 transition-colors">
                        ${t('dynamic.record')}
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
  // 言語変更イベントをリッスン（i18n初期化前に設定）
  window.addEventListener('languageChanged', () => {
    console.log('[dashboard] Language changed, reloading data');
    loadDashboardData();
  });

  // i18nが初期化されるまで待機
  const waitForI18n = setInterval(() => {
    if (window.i18n && window.i18n.getCurrentLanguage) {
      clearInterval(waitForI18n);
      loadDashboardData();

      // 5分ごとに自動更新
      setInterval(loadDashboardData, 5 * 60 * 1000);
    }
  }, 100);

  // タイムアウト（5秒）
  setTimeout(() => {
    clearInterval(waitForI18n);
    if (!window.i18n || !window.i18n.getCurrentLanguage) {
      console.warn('[dashboard] i18n initialization timeout');
      loadDashboardData();
    }
  }, 5000);
});

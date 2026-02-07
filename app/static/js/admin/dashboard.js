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

    assertRequiredIds(
      ['stat-resident', 'stat-adoptable', 'stat-today-logs', 'stat-fiv', 'stat-felv'],
      'dashboard.stats'
    );
    requireElementById('stat-resident', 'dashboard.stats').textContent = stats.resident_count || 0;
    requireElementById('stat-adoptable', 'dashboard.stats').textContent =
      stats.adoptable_count || 0;
    requireElementById('stat-today-logs', 'dashboard.stats').textContent =
      stats.today_logs_count || 0;
    requireElementById('stat-fiv', 'dashboard.stats').textContent = stats.fiv_positive_count || 0;
    requireElementById('stat-felv', 'dashboard.stats').textContent = stats.felv_positive_count || 0;
  } catch (error) {
    console.error('Statistics load error:', error);
    // エラー時はデフォルト値を表示
    const resident = document.getElementById('stat-resident');
    const adoptable = document.getElementById('stat-adoptable');
    const todayLogs = document.getElementById('stat-today-logs');
    const fiv = document.getElementById('stat-fiv');
    const felv = document.getElementById('stat-felv');
    if (resident) resident.textContent = '0';
    if (adoptable) adoptable.textContent = '0';
    if (todayLogs) todayLogs.textContent = '0';
    if (fiv) fiv.textContent = '0';
    if (felv) felv.textContent = '0';
  }
}

// 最近の世話記録を読み込み
async function loadRecentLogs() {
  try {
    const response = await apiRequest(`${API_BASE}/care-logs?page=1&page_size=5`);
    const logs = response.items || [];

    const container = document.getElementById('recent-logs');
    if (!container) return; // Guard

    if (logs.length === 0) {
      const t = key => (typeof i18next !== 'undefined' ? i18next.t(key, { ns: 'dashboard' }) : key);
      container.innerHTML = `<div class="text-center text-gray-500 py-8">${t('no_logs')}</div>`;
      return;
    }

    const t = key => (typeof i18next !== 'undefined' ? i18next.t(key, { ns: 'dashboard' }) : key);

    container.innerHTML = '';
    logs.forEach(log => {
      const el = cloneTemplate('tmpl-recent-log');
      assertRequiredSelectors(
        el,
        ['.js-animal-name', '.js-time-slot', '.js-details', '.js-appetite', '.js-energy'],
        'dashboard.tmpl-recent-log'
      );
      requireSelector(el, '.js-animal-name', 'dashboard.tmpl-recent-log').textContent =
        log.animal_name || '不明';
      requireSelector(el, '.js-time-slot', 'dashboard.tmpl-recent-log').textContent =
        getTimeSlotLabel(log.time_slot);
      requireSelector(el, '.js-details', 'dashboard.tmpl-recent-log').textContent =
        `${log.recorder_name || '不明'} • ${formatDate(new Date(log.log_date))}`;

      requireSelector(el, '.js-appetite', 'dashboard.tmpl-recent-log').textContent =
        `${t('dynamic.appetite')}: ${formatAppetiteLabel(log.appetite)}`;
      requireSelector(el, '.js-energy', 'dashboard.tmpl-recent-log').textContent =
        `${t('dynamic.energy')}: ${log.energy}`;

      container.appendChild(el);
    });
  } catch (error) {
    console.error('Recent logs load error:', error);
    const t = key => (typeof i18next !== 'undefined' ? i18next.t(key, { ns: 'dashboard' }) : key);
    const container = document.getElementById('recent-logs');
    if (container) {
      container.innerHTML = `<div class="text-center text-red-500 py-8">${t('no_logs')}</div>`;
    }
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
    if (!container) return; // Guard

    const t = key => (typeof i18next !== 'undefined' ? i18next.t(key, { ns: 'dashboard' }) : key);

    if (needsCare.length === 0) {
      container.innerHTML = `<div class="text-center text-green-600 py-8">${t('dynamic.all_recorded')}</div>`;
      return;
    }

    container.innerHTML = '';
    needsCare.forEach(animal => {
      const el = cloneTemplate('tmpl-needs-care');
      assertRequiredSelectors(
        el,
        ['.js-animal-photo', '.js-animal-name', '.js-missing-items', '.js-record-link'],
        'dashboard.tmpl-needs-care'
      );

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

      const img = requireSelector(el, '.js-animal-photo', 'dashboard.tmpl-needs-care');
      img.src = photoUrl;
      img.alt = animal.animal_name;
      img.onerror = function () {
        this.onerror = null;
        this.src = defaultImage;
      };

      requireSelector(el, '.js-animal-name', 'dashboard.tmpl-needs-care').textContent =
        animal.animal_name;
      requireSelector(el, '.js-missing-items', 'dashboard.tmpl-needs-care').textContent =
        `${t('dynamic.not_recorded')}: ${missing.join(', ')}`;

      const link = requireSelector(el, '.js-record-link', 'dashboard.tmpl-needs-care');
      link.href = `/public/care?animal_id=${animal.animal_id}`;
      link.textContent = t('dynamic.record');

      container.appendChild(el);
    });
  } catch (error) {
    console.error('Needs care load error:', error);
    const container = document.getElementById('needs-care');
    if (container) {
      container.innerHTML =
        '<div class="text-center text-red-500 py-8">読み込みに失敗しました</div>';
    }
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

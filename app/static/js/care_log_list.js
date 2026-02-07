/**
 * 個別猫の記録一覧ページのJavaScript
 *
 * 猫の記録一覧を表示し、記録詳細をモーダルで表示します。
 */

const urlParams = new URLSearchParams(window.location.search);
const animalId = urlParams.get('animal_id');
const highlightId = urlParams.get('highlight_id');

const CARE_LOGS_NAMESPACE = 'care_logs';
const isKiroweenMode = document.body && document.body.classList.contains('kiroween-mode');

const TIME_SLOT_EMOJI = isKiroweenMode
  ? {
      morning: '🦇',
      noon: '🎃',
      evening: '👻',
    }
  : {
      morning: '🌅',
      noon: '☀️',
      evening: '🌙',
    };

let careLogData = null;

const DEFAULT_IMAGE_PLACEHOLDER = isKiroweenMode
  ? '/static/icons/halloween_logo_2.webp'
  : '/static/images/default.svg';
const fallbackText = (english, japanese) => (isKiroweenMode ? english : japanese);

function translateCareLogs(key, fallback = '', options = {}) {
  const namespacedKey = `${CARE_LOGS_NAMESPACE}:${key}`;
  if (window.i18n && typeof window.i18n.t === 'function') {
    const translation = window.i18n.t(namespacedKey, options);
    if (translation && translation !== namespacedKey) {
      return translation;
    }
  }

  if (typeof fallback === 'string' && fallback.includes('{{') && options) {
    return fallback.replace(/{{(\w+)}}/g, (_, token) => {
      const value = options[token];
      return value === undefined || value === null ? '' : value;
    });
  }

  return fallback || key;
}

function getActiveLanguage() {
  if (window.i18n && typeof window.i18n.getCurrentLanguage === 'function') {
    return window.i18n.getCurrentLanguage();
  }
  return 'ja';
}

function getUnnamedAnimalLabel() {
  return translateCareLogs('public.unnamed_animal', fallbackText('No name set', '名前未設定'));
}

function setAnimalCaption(name) {
  const captionEl = document.getElementById('animalHeaderCaption');
  if (!captionEl) return;
  const fallback = name
    ? fallbackText(`${name}'s log list`, `${name}の記録一覧`)
    : fallbackText('Care log list', '記録一覧');
  captionEl.textContent = translateCareLogs('public.header_caption', fallback, { name });
}

function updateAnimalInfo(data) {
  const name = data.animal_name || getUnnamedAnimalLabel();
  const nameEl = document.getElementById('animalName');
  if (nameEl) {
    nameEl.textContent = name;
  }
  setAnimalCaption(name);

  const photoElement = document.getElementById('animalPhoto');
  if (photoElement) {
    // photoパスに/media/プレフィックスを追加（既に/で始まる場合は追加しない）
    let photoUrl = DEFAULT_IMAGE_PLACEHOLDER;
    if (data.animal_photo && data.animal_photo.trim() !== '') {
      photoUrl = data.animal_photo.startsWith('/')
        ? data.animal_photo
        : `/media/${data.animal_photo}`;
    }
    photoElement.src = photoUrl;
    photoElement.onerror = function handleImageError() {
      photoElement.onerror = null;
      photoElement.src = DEFAULT_IMAGE_PLACEHOLDER;
    };
  }

  const addRecordBtn = document.getElementById('addRecordBtn');
  if (addRecordBtn && animalId) {
    addRecordBtn.href = `/public/care?animal_id=${animalId}`;
  }
}

function updateTodayStatus(todayStatus = {}) {
  const timeSlots = [
    { key: 'morning', iconId: 'morningIcon', statusId: 'morningStatus' },
    { key: 'noon', iconId: 'noonIcon', statusId: 'noonStatus' },
    { key: 'evening', iconId: 'eveningIcon', statusId: 'eveningStatus' },
  ];

  timeSlots.forEach(slot => {
    const iconEl = document.getElementById(slot.iconId);
    const statusEl = document.getElementById(slot.statusId);

    if (iconEl) {
      iconEl.classList.remove(
        'text-green-600',
        'text-gray-400',
        'text-brand-secondary',
        'text-text-muted'
      );
      // Reset inline
      iconEl.style.color = '';
    }
    if (statusEl) {
      statusEl.classList.remove(
        'border-green-500',
        'bg-green-50',
        'border-gray-300',
        'border-brand-secondary',
        'bg-brand-secondary',
        'border-border'
      );
      // Reset inline
      statusEl.style.borderColor = '';
      statusEl.style.backgroundColor = '';
    }

    const isCompleted = Boolean(todayStatus[slot.key]);
    if (iconEl) {
      iconEl.textContent = isCompleted ? '○' : '×';
      if (isCompleted) {
        iconEl.classList.add('text-brand-secondary');
        iconEl.style.color = 'var(--color-brand-secondary)';
      } else {
        iconEl.classList.add('text-text-muted');
        iconEl.style.color = 'var(--color-text-muted)';
      }
    }

    if (statusEl) {
      if (isCompleted) {
        statusEl.classList.add('border-brand-secondary');
        statusEl.style.borderColor = 'var(--color-brand-secondary)';
        statusEl.style.backgroundColor = 'rgba(129, 178, 154, 0.1)'; // brand-secondary with opacity
      } else {
        statusEl.classList.add('border-border');
        statusEl.style.borderColor = 'var(--color-border)';
      }
    }
  });
}

function setupTodayStatusClickTargets() {
  const slots = [
    { statusId: 'morningStatus', slot: 'morning' },
    { statusId: 'noonStatus', slot: 'noon' },
    { statusId: 'eveningStatus', slot: 'evening' },
  ];

  slots.forEach(({ statusId, slot }) => {
    const el = document.getElementById(statusId);
    if (!el || !animalId) return;

    el.classList.add('cursor-pointer');
    el.addEventListener('click', () => {
      window.location.href = `/public/care?animal_id=${animalId}&time_slot=${slot}`;
    });
  });
}

function getTimeSlotLabel(timeSlot) {
  const fallbackMap = {
    morning: fallbackText('Morning', '朝'),
    noon: fallbackText('Noon', '昼'),
    evening: fallbackText('Evening', '夜'),
  };
  const fallback = fallbackMap[timeSlot] || timeSlot || '';
  return translateCareLogs(`public.time_slots.${timeSlot}`, fallback);
}

function formatScoreValue(value) {
  if (value === null || value === undefined) {
    return '-';
  }
  return `${value} / 5`;
}

function getAppetiteLevelKey(value) {
  const normalized = Math.round(Number(value) * 100) / 100;
  const map = {
    1: '5',
    0.75: '4',
    0.5: '3',
    0.25: '2',
    0: '1',
  };
  return map[normalized] || null;
}

function formatAppetiteValue(value) {
  if (value === null || value === undefined) {
    return '-';
  }

  const key = getAppetiteLevelKey(value);
  if (!key) {
    return `${value}`;
  }

  const fallbackMap = {
    5: fallbackText('Finished', '完食'),
    4: fallbackText('Left 1/4', '1/4残し'),
    3: fallbackText('Left half', '半分残し'),
    2: fallbackText('Left 3/4', '3/4残し'),
    1: fallbackText('Not eating', '食べない'),
  };
  return translateCareLogs(`appetite_levels.${key}`, fallbackMap[key] || `${value}`);
}

function getDateFormatterOptions(lang) {
  if (lang === 'en') {
    return { month: 'short', day: 'numeric', weekday: 'short' };
  }
  return { month: 'numeric', day: 'numeric', weekday: 'short' };
}

function formatDate(dateString) {
  const date = new Date(dateString);
  if (Number.isNaN(date.getTime())) {
    return dateString;
  }
  const lang = getActiveLanguage();
  const formatter = new Intl.DateTimeFormat(
    lang === 'en' ? 'en-US' : 'ja-JP',
    getDateFormatterOptions(lang)
  );
  return formatter.format(date);
}

const SLOT_ORDER = ['morning', 'noon', 'evening'];
const DAILY_WINDOW_DAYS = 7;

function getLocalDateAtMidnight(date = new Date()) {
  const localDate = new Date(date);
  localDate.setHours(0, 0, 0, 0);
  return localDate;
}

function formatDateToISO(dateObj) {
  const year = dateObj.getFullYear();
  const month = String(dateObj.getMonth() + 1).padStart(2, '0');
  const day = String(dateObj.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

function buildDailySummary(logs = []) {
  const baseDate = getLocalDateAtMidnight();
  const summary = [];

  for (let offset = 0; offset < DAILY_WINDOW_DAYS; offset += 1) {
    const dateObj = new Date(baseDate);
    dateObj.setDate(baseDate.getDate() - offset);
    const isoDate = formatDateToISO(dateObj);
    const logsForDay = logs.filter(log => log?.log_date === isoDate);

    const slots = {};
    SLOT_ORDER.forEach(slotKey => {
      const slotLog = logsForDay.find(log => log?.time_slot === slotKey) || null;
      slots[slotKey] = {
        hasRecord: Boolean(slotLog),
        logId: slotLog?.id || null,
        recorder: slotLog?.recorder_name || '',
        entry: slotLog,
      };
    });

    summary.push({
      isoDate,
      dateObj,
      isToday: offset === 0,
      isYesterday: offset === 1,
      slots,
      hasAnyRecord: logsForDay.length > 0,
    });
  }

  return summary;
}

function getRelativeDayBadge(daySummary) {
  if (daySummary.isToday) {
    return translateCareLogs('public.today_badge', fallbackText('Today', '今日'));
  }
  if (daySummary.isYesterday) {
    return translateCareLogs('public.yesterday_badge', fallbackText('Yesterday', '昨日'));
  }
  return '';
}

const FALLBACK_TEMPLATE_DAILY_CARD = `
    <div class="border border-gray-200 rounded-xl p-4 shadow-sm bg-white">
        <div class="flex items-center justify-between gap-2 mb-3">
            <div class="flex items-center gap-2">
                    <div class="text-base font-semibold text-gray-800 js-date"></div>
                    <span class="hidden inline-flex items-center rounded-full bg-brand-primary-light px-2 py-0.5 text-xs font-medium text-brand-primary-dark js-badge"></span>
            </div>
        </div>
        <div class="grid grid-cols-3 gap-2 js-slots"></div>
    </div>
`;

const FALLBACK_TEMPLATE_SLOT_CHIP = `
    <button type="button" class="flex flex-col items-center rounded-xl border px-3 py-2 text-center transition-colors w-full js-chip-container hover:opacity-90">
        <div class="text-2xl js-emoji"></div>
        <div class="mt-1 text-xs font-medium js-label"></div>
        <div class="mt-1 text-sm font-semibold js-status"></div>
        <div class="text-xs mt-1 truncate w-full opacity-80 js-recorder hidden"></div>
    </button>
`;

function cloneTemplate(templateId, fallbackHtml) {
  const template = document.getElementById(templateId);
  if (!template) {
    // Fallback for safety if template is missing (regression safety)
    if (fallbackHtml) {
      const tempDiv = document.createElement('div');
      tempDiv.innerHTML = fallbackHtml.trim();
      return tempDiv.firstElementChild;
    }
    console.error(`Template ${templateId} not found`);
    return document.createElement('div');
  }
  return template.content.cloneNode(true).firstElementChild;
}

function createSlotStatusElement(slotKey, slotInfo = {}, variant = 'card') {
  const hasRecord = Boolean(slotInfo?.hasRecord);
  const slotLabel = getTimeSlotLabel(slotKey);

  // For Table variant, we still build simple DOM because it's just a small button/icon
  if (variant === 'table') {
    const element = document.createElement(hasRecord && slotInfo?.logId ? 'button' : 'div');
    element.className = `mx-auto inline-flex h-9 w-9 items-center justify-center rounded-full border text-sm font-semibold ${
      hasRecord
        ? 'border-brand-secondary text-brand-secondary'
        : 'border-border bg-bg-surface text-text-muted'
    }`;

    if (hasRecord) {
      element.style.borderColor = 'var(--color-brand-secondary)';
      element.style.color = 'var(--color-brand-secondary)';
      element.style.backgroundColor = 'rgba(129, 178, 154, 0.1)';
    } else {
      element.style.borderColor = 'var(--color-border)';
      element.style.backgroundColor = 'var(--color-bg-surface)';
      element.style.color = 'var(--color-text-muted)';
    }

    element.textContent = hasRecord ? '○' : '-';
    if (hasRecord && slotInfo?.logId) {
      element.addEventListener('click', () => showLogDetail(slotInfo.logId));
    }
    return element;
  }

  // Card Variant uses Template
  const element = cloneTemplate('tmpl-slot-chip', FALLBACK_TEMPLATE_SLOT_CHIP);

  // Interactive Container
  const container = element; // The root is the button

  // Apply Styles based on status
  if (hasRecord) {
    container.classList.add('border-brand-secondary', 'text-brand-secondary');
    container.classList.remove('border-border', 'bg-bg-base', 'text-text-muted');
    container.style.borderColor = 'var(--color-brand-secondary)';
    container.style.color = 'var(--color-brand-secondary)';
    container.style.backgroundColor = 'rgba(129, 178, 154, 0.1)';

    if (slotInfo?.logId) {
      container.addEventListener('click', () => showLogDetail(slotInfo.logId));
    }
  } else {
    container.classList.add('border-border', 'bg-bg-base', 'text-text-muted');
    container.classList.remove('border-brand-secondary', 'text-brand-secondary');
    container.style.borderColor = 'var(--color-border)';
    container.style.backgroundColor = 'var(--color-bg-base)';
    container.style.color = 'var(--color-text-muted)';
    // No click action for missing
    container.style.cursor = 'default';
    container.type = 'div'; // effectively
  }

  const ariaLabel = translateCareLogs(
    hasRecord ? 'public.slot_chip.recorded' : 'public.slot_chip.missing',
    hasRecord
      ? `${slotLabel}: ${fallbackText('Recorded', '記録あり')}`
      : `${slotLabel}: ${fallbackText('Missing', '未記録')}`,
    { slot: slotLabel }
  );
  container.setAttribute('aria-label', ariaLabel);

  // Populate Data
  const emojiEl = element.querySelector('.js-emoji');
  if (emojiEl) emojiEl.textContent = TIME_SLOT_EMOJI[slotKey] || '📝';

  const labelEl = element.querySelector('.js-label');
  if (labelEl) labelEl.textContent = slotLabel;

  const statusEl = element.querySelector('.js-status');
  if (statusEl) {
    statusEl.textContent = translateCareLogs(
      hasRecord ? 'public.slot_status.recorded' : 'public.slot_status.missing',
      hasRecord ? fallbackText('Recorded', '記録あり') : fallbackText('Missing', '未記録')
    );
  }

  const recorderEl = element.querySelector('.js-recorder');
  if (recorderEl && slotInfo?.recorder) {
    recorderEl.textContent = slotInfo.recorder;
    recorderEl.classList.remove('hidden');
  }

  return element;
}

function renderDailyCards(summary = []) {
  const container = document.getElementById('dailyStatusCards');
  if (!container) return;

  container.innerHTML = '';

  summary.forEach(day => {
    const card = cloneTemplate('tmpl-daily-card', FALLBACK_TEMPLATE_DAILY_CARD);

    // Date
    const dateEl = card.querySelector('.js-date');
    if (dateEl) dateEl.textContent = formatDate(day.isoDate);

    // Badge
    const badgeText = getRelativeDayBadge(day);
    const badgeEl = card.querySelector('.js-badge');
    if (badgeEl && badgeText) {
      badgeEl.textContent = badgeText;
      badgeEl.classList.remove('hidden');
    }

    // Slots
    const slotsWrapper = card.querySelector('.js-slots');
    if (slotsWrapper) {
      SLOT_ORDER.forEach(slotKey => {
        const slotEl = createSlotStatusElement(slotKey, day.slots[slotKey], 'card');
        slotsWrapper.appendChild(slotEl);
      });
    }

    container.appendChild(card);
  });
}

function renderDailyTable(summary = []) {
  const tbody = document.getElementById('dailyStatusTableBody');
  if (!tbody) return;

  tbody.innerHTML = '';
  summary.forEach(day => {
    const row = document.createElement('tr');

    const dateCell = document.createElement('td');
    dateCell.className = 'px-4 py-3 text-sm font-medium text-gray-800 whitespace-nowrap';
    dateCell.textContent = formatDate(day.isoDate);
    const badgeText = getRelativeDayBadge(day);

    if (badgeText) {
      const badge = document.createElement('span');
      badge.className =
        'ml-2 inline-flex items-center rounded-full bg-brand-primary-light px-2 py-0.5 text-xs font-medium text-brand-primary-dark';
      badge.textContent = badgeText;
      dateCell.appendChild(badge);
    }

    row.appendChild(dateCell);

    SLOT_ORDER.forEach(slotKey => {
      const cell = document.createElement('td');
      cell.className = 'px-4 py-3 text-center';
      const statusEl = createSlotStatusElement(slotKey, day.slots[slotKey], 'table');
      cell.appendChild(statusEl);
      row.appendChild(cell);
    });

    tbody.appendChild(row);
  });
}

function renderDailyOverview(summary = []) {
  if (!summary || !summary.length) {
    renderDailyCards(buildDailySummary([]));
    renderDailyTable(buildDailySummary([]));
    return;
  }
  renderDailyCards(summary);
  renderDailyTable(summary);
}

const FALLBACK_TEMPLATE_LOG_ITEM = `
    <div class="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-brand-primary/5 transition-colors cursor-pointer bg-white mb-2 js-log-container">
        <div class="flex items-center gap-3">
            <div class="text-2xl js-emoji"></div>
            <div>
                <div class="font-medium text-gray-800 js-date"></div>
                <div class="text-sm text-gray-500 js-meta"></div>
            </div>
        </div>
        <div class="font-bold text-brand-secondary js-check">○</div>
    </div>
`;

function displayRecentLogs(logs = []) {
  const container = document.getElementById('recentLogs');
  const noLogsDiv = document.getElementById('noLogs');

  if (!container || !noLogsDiv) {
    return;
  }

  if (!logs.length) {
    container.classList.add('hidden');
    noLogsDiv.classList.remove('hidden');
    return;
  }

  container.classList.remove('hidden');
  noLogsDiv.classList.add('hidden');
  container.innerHTML = '';

  logs.forEach(logItem => {
    const log = logItem || {};
    const logDiv = cloneTemplate('tmpl-log-item', FALLBACK_TEMPLATE_LOG_ITEM);

    // Highlight Effect
    if (highlightId && log.id === Number(highlightId)) {
      logDiv.classList.add('border-brand-primary', 'bg-brand-primary-light');
      setTimeout(() => {
        logDiv.classList.remove('border-brand-primary', 'bg-brand-primary-light');
      }, 3200);
    }

    // Click Handler through class
    if (log && log.id) {
      // Note: In template, the root has js-log-container class usually
      logDiv.addEventListener('click', () => showLogDetail(log.id));
    }

    // Emoji
    const emojiEl = logDiv.querySelector('.js-emoji');
    if (emojiEl) emojiEl.textContent = TIME_SLOT_EMOJI[log.time_slot] || '📝';

    // Date
    const dateEl = logDiv.querySelector('.js-date');
    if (dateEl) dateEl.textContent = log.log_date ? formatDate(log.log_date) : '';

    // Meta (Time Slot + Recorder)
    const metaEl = logDiv.querySelector('.js-meta');
    if (metaEl) {
      const timeSlotLabel = getTimeSlotLabel(log.time_slot);
      metaEl.textContent = log.recorder_name
        ? `${timeSlotLabel} - ${log.recorder_name}`
        : timeSlotLabel;
    }

    // Check Mark
    const checkEl = logDiv.querySelector('.js-check');
    if (checkEl) {
      checkEl.style.color = 'var(--color-brand-secondary)';
    }

    container.appendChild(logDiv);
  });
}

function createDetailRow(label, value) {
  const row = document.createElement('div');
  row.className = 'flex justify-between py-2 border-b';
  const labelEl = document.createElement('span');
  labelEl.className = 'text-gray-600';
  labelEl.textContent = label;
  const valueEl = document.createElement('span');
  valueEl.className = 'font-medium';
  valueEl.textContent = value;
  row.appendChild(labelEl);
  row.appendChild(valueEl);
  return row;
}

function renderLogDetailModal(log) {
  const modal = document.createElement('div');
  modal.className =
    'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50';
  modal.addEventListener('click', event => {
    if (event.target === modal) {
      modal.remove();
    }
  });

  const content = document.createElement('div');
  content.className = 'bg-white rounded-lg shadow-xl max-w-md w-full p-6';

  const header = document.createElement('div');
  header.className = 'flex justify-between items-center mb-4';

  const titleEl = document.createElement('h3');
  titleEl.className = 'text-xl font-bold text-gray-800';
  titleEl.textContent = translateCareLogs('public.modal_title', '記録詳細');

  const closeIconButton = document.createElement('button');
  closeIconButton.type = 'button';
  closeIconButton.className = 'text-gray-500 hover:text-gray-700';
  closeIconButton.setAttribute('aria-label', translateCareLogs('public.modal_close', '閉じる'));
  closeIconButton.innerHTML = `
    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
    </svg>
  `;
  closeIconButton.addEventListener('click', () => modal.remove());

  header.appendChild(titleEl);
  header.appendChild(closeIconButton);

  const detailsContainer = document.createElement('div');
  detailsContainer.className = 'space-y-3';

  const detailRows = [
    {
      label: translateCareLogs('fields.log_date', '記録日'),
      value: formatDate(log.log_date),
    },
    {
      label: translateCareLogs('fields.time_slot', '時点'),
      value: getTimeSlotLabel(log.time_slot),
    },
    {
      label: translateCareLogs('fields.recorder', '記録者'),
      value: log.recorder_name || '',
    },
    {
      label: translateCareLogs('fields.appetite', '食欲'),
      value: formatAppetiteValue(log.appetite),
    },
    {
      label: translateCareLogs('fields.energy', '元気'),
      value: formatScoreValue(log.energy),
    },
    {
      label: translateCareLogs('fields.urination', '排尿'),
      value: log.urination
        ? translateCareLogs('urination_status.yes', 'あり')
        : translateCareLogs('urination_status.no', 'なし'),
    },
    {
      label: translateCareLogs('fields.cleaning', '清掃'),
      value: log.cleaning
        ? translateCareLogs('cleaning_status.done', '済')
        : translateCareLogs('cleaning_status.not_done', '未'),
    },
  ];

  detailRows.forEach(row => {
    detailsContainer.appendChild(createDetailRow(row.label, row.value));
  });

  if (log.memo) {
    const memoWrapper = document.createElement('div');
    memoWrapper.className = 'py-2';

    const memoLabel = document.createElement('div');
    memoLabel.className = 'text-gray-600 mb-1';
    memoLabel.textContent = translateCareLogs('fields.memo', 'メモ');

    const memoContent = document.createElement('div');
    memoContent.className = 'text-sm text-gray-800 bg-gray-50 p-3 rounded';
    memoContent.textContent = log.memo;

    memoWrapper.appendChild(memoLabel);
    memoWrapper.appendChild(memoContent);
    detailsContainer.appendChild(memoWrapper);
  }

  const footerButton = document.createElement('button');
  footerButton.type = 'button';
  footerButton.className =
    'mt-6 w-full py-3 bg-gray-100 text-gray-700 rounded-lg font-medium hover:bg-gray-200 transition-colors';
  footerButton.textContent = translateCareLogs('public.modal_close', '閉じる');
  footerButton.addEventListener('click', () => modal.remove());

  const editButton = document.createElement('a');
  editButton.className =
    'mt-3 w-full inline-flex justify-center py-3 bg-brand-primary text-white rounded-lg font-medium hover:opacity-90 transition-colors';
  editButton.textContent = translateCareLogs('public.modal_edit', 'この記録を編集');
  if (animalId && log?.id) {
    editButton.href = `/public/care?animal_id=${animalId}&log_id=${log.id}`;
  } else {
    editButton.classList.add('opacity-50', 'pointer-events-none');
  }

  content.appendChild(header);
  content.appendChild(detailsContainer);
  content.appendChild(editButton);
  content.appendChild(footerButton);
  modal.appendChild(content);

  document.body.appendChild(modal);
}

async function showLogDetail(logId) {
  try {
    const response = await fetch(`${API_BASE}/care-logs/animal/${animalId}/${logId}`);
    if (!response.ok) {
      throw new Error(
        translateCareLogs('public.errors.load_detail_failed', '記録詳細の取得に失敗しました')
      );
    }

    const log = await response.json();
    renderLogDetailModal(log);
  } catch (error) {
    console.error('[care_log_list] Failed to load detail', error);
    const fallbackMessage = translateCareLogs(
      'public.errors.load_detail_failed',
      '記録詳細の取得に失敗しました'
    );
    showError(error?.message || fallbackMessage);
  }
}

async function loadCareLogList() {
  try {
    const response = await fetch(`${API_BASE}/care-logs/animal/${animalId}`);
    if (!response.ok) {
      throw new Error(
        translateCareLogs('public.errors.load_list_failed', '記録一覧の取得に失敗しました')
      );
    }

    const data = await response.json();
    const dailySummary = buildDailySummary(data.recent_logs || []);
    careLogData = { ...data, dailySummary };
    updateAnimalInfo(careLogData);
    updateTodayStatus(careLogData.today_status || {});
    setupTodayStatusClickTargets();
    renderDailyOverview(careLogData.dailySummary);
    displayRecentLogs(careLogData.recent_logs || []);
  } catch (error) {
    console.error('[care_log_list] Failed to load list', error);
    const fallbackMessage = translateCareLogs(
      'public.errors.load_list_failed',
      '記録一覧の取得に失敗しました'
    );
    showError(error?.message || fallbackMessage);
  }
}

function handleLanguageChange() {
  if (!careLogData) {
    return;
  }
  updateAnimalInfo(careLogData);
  renderDailyOverview(careLogData.dailySummary);
  displayRecentLogs(careLogData.recent_logs || []);
}

document.addEventListener('languageChanged', handleLanguageChange);

async function initializeCareLogList() {
  if (typeof initI18n === 'function') {
    await initI18n();
  }

  if (!animalId) {
    showError(translateCareLogs('public.errors.missing_animal_id', '猫のIDが指定されていません'));
    return;
  }

  await loadCareLogList();
}

initializeCareLogList().catch(error => {
  console.error('[care_log_list] Initialization failed', error);
  const fallbackMessage = translateCareLogs(
    'public.errors.load_list_failed',
    '記録一覧の取得に失敗しました'
  );
  showError(fallbackMessage);
});

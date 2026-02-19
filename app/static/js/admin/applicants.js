/**
 * 里親希望者/相談 一覧画面
 */

const adminBasePath = window.ADMIN_BASE_PATH || window.__ADMIN_BASE_PATH__ || '/admin';
let currentPage = 0;
const pageSize = 20;
let allEntries = [];
let filteredEntries = [];

function t(key, options = {}) {
  if (typeof i18next !== 'undefined' && i18next.isInitialized) {
    return i18next.t(key, options);
  }
  const parts = key.split('.');
  return parts[parts.length - 1];
}

document.addEventListener('DOMContentLoaded', () => {
  const checkI18n = setInterval(() => {
    if (typeof i18next !== 'undefined' && i18next.isInitialized) {
      clearInterval(checkI18n);
      loadEntries();
      setupEventListeners();
    }
  }, 50);
});

function setupEventListeners() {
  document.getElementById('searchBtn').addEventListener('click', () => filterEntries());
  document.getElementById('clearBtn').addEventListener('click', () => clearSearch());
  document.getElementById('prevBtn').addEventListener('click', () => changePage(-1));
  document.getElementById('nextBtn').addEventListener('click', () => changePage(1));
  document.getElementById('requestTypeFilter').addEventListener('change', () => loadEntries());
}

async function fetchJson(url) {
  const token = localStorage.getItem('access_token');
  const headers = {};
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(url, {
    headers,
    credentials: 'same-origin',
  });
  if (!response.ok) {
    throw new Error(
      t('adoptions:applicants.messages.load_failed', {
        ns: 'adoptions',
        defaultValue: 'データの取得に失敗しました',
      })
    );
  }
  return response.json();
}

async function loadEntries() {
  showLoading(true);
  hideError();

  try {
    const requestType = getSelectedRequestType();
    const entries = await fetchJson(
      `/api/v1/adoptions/intake-entries?limit=1000&request_type=${encodeURIComponent(requestType)}`
    );

    allEntries = [...entries].sort((a, b) => new Date(b.created_at) - new Date(a.created_at));

    filterEntries();
  } catch (error) {
    console.error('Error loading adoption entries:', error);
    showError(error.message);
    allEntries = [];
    filteredEntries = [];
    renderEntries();
  } finally {
    showLoading(false);
  }
}

function renderEntries() {
  const start = currentPage * pageSize;
  const end = start + pageSize;
  const pageEntries = filteredEntries.slice(start, end);

  const mobileList = document.getElementById('mobileList');
  const desktopList = document.getElementById('desktopList');

  if (mobileList) mobileList.innerHTML = '';
  if (desktopList) desktopList.innerHTML = '';

  pageEntries.forEach(entry => {
    if (mobileList) {
      const card = cloneTemplate('tmpl-mobile-card');
      assertRequiredSelectors(
        card,
        [
          '.js-request-type',
          '.js-name',
          '.js-phone',
          '.js-contact',
          '.js-registration-date',
          '.js-status',
          '.js-detail-btn',
          '.js-edit-btn',
          '.js-apply-btn',
        ],
        'applicants.tmpl-mobile-card'
      );

      requireSelector(card, '.js-request-type', 'applicants.tmpl-mobile-card').textContent =
        formatRequestType(entry);
      requireSelector(card, '.js-name', 'applicants.tmpl-mobile-card').textContent = entry.name;
      requireSelector(card, '.js-phone', 'applicants.tmpl-mobile-card').textContent =
        entry.phone || '-';
      requireSelector(card, '.js-contact', 'applicants.tmpl-mobile-card').textContent =
        formatContact(entry);
      requireSelector(card, '.js-registration-date', 'applicants.tmpl-mobile-card').textContent =
        formatDate(entry.created_at);
      requireSelector(card, '.js-status', 'applicants.tmpl-mobile-card').textContent =
        formatStatus(entry);

      const detailBtn = requireSelector(card, '.js-detail-btn', 'applicants.tmpl-mobile-card');
      detailBtn.href = getDetailUrl(entry);

      const editBtn = requireSelector(card, '.js-edit-btn', 'applicants.tmpl-mobile-card');
      editBtn.href = getEditUrl(entry);

      const applyBtn = requireSelector(card, '.js-apply-btn', 'applicants.tmpl-mobile-card');
      if (entry.request_type === 'consultation' && entry.status !== 'converted') {
        applyBtn.classList.remove('hidden');
        applyBtn.href = `${adminBasePath}/adoptions/applicants/new?consultation_id=${entry.id}`;
      }

      translateDynamicElement(card);
      mobileList.appendChild(card);
    }

    if (desktopList) {
      const row = cloneTemplate('tmpl-desktop-row');
      assertRequiredSelectors(
        row,
        [
          '.js-request-type',
          '.js-name',
          '.js-phone',
          '.js-contact',
          '.js-registration-date',
          '.js-status',
          '.js-detail-btn',
          '.js-edit-btn',
          '.js-apply-btn',
        ],
        'applicants.tmpl-desktop-row'
      );

      requireSelector(row, '.js-request-type', 'applicants.tmpl-desktop-row').textContent =
        formatRequestType(entry);
      requireSelector(row, '.js-name', 'applicants.tmpl-desktop-row').textContent = entry.name;
      requireSelector(row, '.js-phone', 'applicants.tmpl-desktop-row').textContent =
        entry.phone || '-';
      requireSelector(row, '.js-contact', 'applicants.tmpl-desktop-row').textContent =
        formatContact(entry);
      requireSelector(row, '.js-registration-date', 'applicants.tmpl-desktop-row').textContent =
        formatDate(entry.created_at);
      requireSelector(row, '.js-status', 'applicants.tmpl-desktop-row').textContent =
        formatStatus(entry);

      const detailBtn = requireSelector(row, '.js-detail-btn', 'applicants.tmpl-desktop-row');
      detailBtn.href = getDetailUrl(entry);

      const editBtn = requireSelector(row, '.js-edit-btn', 'applicants.tmpl-desktop-row');
      editBtn.href = getEditUrl(entry);

      const applyBtn = requireSelector(row, '.js-apply-btn', 'applicants.tmpl-desktop-row');
      if (entry.request_type === 'consultation' && entry.status !== 'converted') {
        applyBtn.classList.remove('hidden');
        applyBtn.href = `${adminBasePath}/adoptions/applicants/new?consultation_id=${entry.id}`;
      }

      translateDynamicElement(row);
      desktopList.appendChild(row);
    }
  });

  updatePagination();
}

function translateDynamicElement(element) {
  if (!element) return;
  if (window.i18n && typeof window.i18n.translateElement === 'function') {
    window.i18n.translateElement(element);
    return;
  }
  if (window.applyDynamicTranslations) {
    window.applyDynamicTranslations(element);
  }
}

function formatRequestType(entry) {
  if (entry.request_type === 'both') {
    return t('adoptions:applicants.request_types.both', {
      ns: 'adoptions',
      defaultValue: '相談/譲渡申込',
    });
  }
  return entry.request_type === 'consultation'
    ? t('adoptions:applicants.request_types.consultation', {
        ns: 'adoptions',
        defaultValue: '相談',
      })
    : t('adoptions:applicants.request_types.application', {
        ns: 'adoptions',
        defaultValue: '譲渡申込',
      });
}

function formatStatus(entry) {
  const notApplicable = t('adoptions:applicants.statuses.not_applicable', {
    ns: 'adoptions',
    defaultValue: '-',
  });
  if (entry.request_type === 'application') return notApplicable;
  if (entry.request_type === 'both') {
    const consultationStatus = formatConsultationStatus(entry.status);
    return consultationStatus === notApplicable
      ? t('adoptions:applicants.statuses.applied_with_consultation', {
          ns: 'adoptions',
          defaultValue: '申込済（相談あり）',
        })
      : t('adoptions:applicants.statuses.applied_with_consultation_status', {
          ns: 'adoptions',
          status: consultationStatus,
          defaultValue: '申込済（相談: {{status}}）',
        });
  }
  return formatConsultationStatus(entry.status);
}

function formatConsultationStatus(status) {
  if (status === 'open') {
    return t('adoptions:applicants.consultation_status.open', {
      ns: 'adoptions',
      defaultValue: '受付中',
    });
  }
  if (status === 'converted') {
    return t('adoptions:applicants.consultation_status.converted', {
      ns: 'adoptions',
      defaultValue: '申込化済み',
    });
  }
  if (status === 'closed') {
    return t('adoptions:applicants.consultation_status.closed', {
      ns: 'adoptions',
      defaultValue: '対応終了',
    });
  }
  return (
    status ||
    t('adoptions:applicants.statuses.not_applicable', { ns: 'adoptions', defaultValue: '-' })
  );
}

function getDetailUrl(entry) {
  const applicationId = getApplicationId(entry);
  const consultationId = getConsultationId(entry);

  if (entry.request_type === 'both') {
    if (applicationId) {
      return `${adminBasePath}/adoptions/applicants/${applicationId}`;
    }
    if (consultationId) {
      return `${adminBasePath}/adoptions/consultations/${consultationId}`;
    }
  }
  if (entry.request_type === 'consultation') {
    return `${adminBasePath}/adoptions/consultations/${consultationId || entry.id}`;
  }
  return `${adminBasePath}/adoptions/applicants/${applicationId || entry.id}`;
}

function getEditUrl(entry) {
  const applicationId = getApplicationId(entry);
  const consultationId = getConsultationId(entry);

  if (entry.request_type === 'both') {
    if (applicationId) {
      return `${adminBasePath}/adoptions/applicants/${applicationId}/edit`;
    }
    if (consultationId) {
      return `${adminBasePath}/adoptions/consultations/${consultationId}/edit`;
    }
  }
  if (entry.request_type === 'consultation') {
    return `${adminBasePath}/adoptions/consultations/${consultationId || entry.id}/edit`;
  }
  return `${adminBasePath}/adoptions/applicants/${applicationId || entry.id}/edit`;
}

function formatContact(entry) {
  if (entry.contact_type === 'line' && entry.contact_line_id) {
    return `${t('adoptions:applicants.contact.line', { ns: 'adoptions', defaultValue: 'LINE' })}: ${entry.contact_line_id}`;
  }
  if (entry.contact_type === 'email' && entry.contact_email) {
    return `${t('adoptions:applicants.contact.email', { ns: 'adoptions', defaultValue: 'メール' })}: ${entry.contact_email}`;
  }
  if (entry.phone) {
    return `${t('adoptions:applicants.contact.phone', { ns: 'adoptions', defaultValue: '電話' })}: ${entry.phone}`;
  }
  return t('adoptions:applicants.statuses.not_applicable', { ns: 'adoptions', defaultValue: '-' });
}

function filterEntries() {
  const searchText = document.getElementById('searchInput').value.toLowerCase();
  filteredEntries = allEntries.filter(entry => {
    if (!searchText) {
      return true;
    }

    const values = [
      entry.name,
      entry.name_kana,
      entry.phone,
      entry.contact_line_id,
      entry.contact_email,
      entry.consultation_note,
      formatContact(entry),
    ]
      .filter(Boolean)
      .map(value => value.toLowerCase());

    return values.some(value => value.includes(searchText));
  });
  currentPage = 0;
  renderEntries();
}

function clearSearch() {
  document.getElementById('searchInput').value = '';
  document.getElementById('requestTypeFilter').value = 'all';
  loadEntries();
}

function getSelectedRequestType() {
  const requestTypeFilter = document.getElementById('requestTypeFilter');
  if (!requestTypeFilter) return 'all';
  return requestTypeFilter.value || 'all';
}

function getApplicationId(entry) {
  return entry.application_id || (entry.request_type === 'application' ? entry.id : null);
}

function getConsultationId(entry) {
  return entry.consultation_id || (entry.request_type === 'consultation' ? entry.id : null);
}

function updatePagination() {
  const total = filteredEntries.length;
  const start = total === 0 ? 0 : currentPage * pageSize + 1;
  const end = total === 0 ? 0 : Math.min((currentPage + 1) * pageSize, total);
  const itemsText = window.i18n && window.i18n.t ? window.i18n.t('items', { ns: 'common' }) : '件';

  document.getElementById('paginationInfo').textContent =
    `${start} - ${end} / ${total} ${itemsText}`;

  document.getElementById('prevBtn').disabled = currentPage === 0;
  document.getElementById('nextBtn').disabled = end >= total;
}

function changePage(delta) {
  currentPage += delta;
  renderEntries();
}

function showLoading(show) {
  document.getElementById('loading').classList.toggle('hidden', !show);
  document.getElementById('applicantsList').classList.toggle('hidden', show);
}

function showError(message) {
  const errorDiv = document.getElementById('error');
  errorDiv.textContent = message;
  errorDiv.classList.remove('hidden');
}

function hideError() {
  document.getElementById('error').classList.add('hidden');
}

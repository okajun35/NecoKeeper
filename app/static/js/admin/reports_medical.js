/**
 * 診療記録帳票ページのJavaScript (多言語対応版)
 */

function t(key, options = {}) {
  if (typeof i18next !== 'undefined' && i18next.isInitialized) {
    return i18next.t(key, options);
  }
  return key.split('.').pop();
}

document.addEventListener('DOMContentLoaded', function () {
  const init = () => {
    loadAnimals();

    const scopeEl = document.getElementById('scope');
    if (scopeEl) {
      scopeEl.addEventListener('change', updateScopeUI);
    }
    updateScopeUI();

    document.getElementById('generate-form').addEventListener('submit', handleFormSubmit);
    setDateRange('this_month');
  };

  if (typeof i18next !== 'undefined' && i18next.isInitialized) {
    init();
  } else {
    document.addEventListener('i18nextInitialized', init, { once: true });
  }
});

function updateScopeUI() {
  const scope = document.getElementById('scope')?.value || 'all';
  const animalSelectGroup = document.getElementById('animal-select-group');
  const animalSelect = document.getElementById('animal-id');

  if (!animalSelectGroup || !animalSelect) return;

  if (scope === 'single') {
    animalSelectGroup.classList.remove('hidden');
    animalSelect.required = true;
  } else {
    animalSelectGroup.classList.add('hidden');
    animalSelect.required = false;
    animalSelect.value = '';
  }
}

async function loadAnimals() {
  try {
    const data = await apiRequest('/api/v1/animals?limit=1000');
    if (!data) return;

    const animals = data.items || [];

    const select = document.getElementById('animal-id');
    if (!select) return;

    select.innerHTML = `<option value="">${t('reports:form.animal_select_label', { ns: 'reports' })}</option>`;

    animals.forEach(animal => {
      const option = cloneTemplate('tmpl-animal-option');
      option.value = animal.id;
      option.textContent = `${animal.name || t('reports:animals.no_name', { ns: 'reports' })} (ID: ${animal.id})`;
      select.appendChild(option);
    });
  } catch (error) {
    console.error('猫一覧の取得エラー:', error);
    showError(t('reports:messages.error_fetch_animals', { ns: 'reports' }));
  }
}

function setDateRange(preset) {
  const today = new Date();
  let startDate, endDate;

  switch (preset) {
    case 'today':
      startDate = endDate = today;
      break;

    case 'this_week': {
      const dayOfWeek = today.getDay();
      const monday = new Date(today);
      monday.setDate(today.getDate() - (dayOfWeek === 0 ? 6 : dayOfWeek - 1));
      startDate = monday;
      endDate = today;
      break;
    }

    case 'this_month':
      startDate = new Date(today.getFullYear(), today.getMonth(), 1);
      endDate = today;
      break;

    case 'last_month':
      startDate = new Date(today.getFullYear(), today.getMonth() - 1, 1);
      endDate = new Date(today.getFullYear(), today.getMonth(), 0);
      break;

    case 'last_3_months':
      startDate = new Date(today.getFullYear(), today.getMonth() - 3, 1);
      endDate = today;
      break;

    case 'last_6_months':
      startDate = new Date(today.getFullYear(), today.getMonth() - 6, 1);
      endDate = today;
      break;

    case 'this_year':
      startDate = new Date(today.getFullYear(), 0, 1);
      endDate = today;
      break;

    default:
      return;
  }

  document.getElementById('start-date').valueAsDate = startDate;
  document.getElementById('end-date').valueAsDate = endDate;
}

async function handleFormSubmit(event) {
  event.preventDefault();

  const formData = new FormData(event.target);
  const reportType = formData.get('report_type');
  const startDate = formData.get('start_date');
  const endDate = formData.get('end_date');
  const format = formData.get('format');
  const scope = formData.get('scope') || 'all';
  const animalId = formData.get('animal_id');

  if (!reportType || !startDate || !endDate || !format) {
    showError(t('reports:messages.error_required', { ns: 'reports' }));
    return;
  }

  if (scope === 'single' && !animalId) {
    showError(t('reports:messages.error_select_animal', { ns: 'reports' }));
    return;
  }

  if (new Date(startDate) > new Date(endDate)) {
    showError(t('reports:messages.error_date_order', { ns: 'reports' }));
    return;
  }

  showLoading();

  try {
    await generateReport(
      reportType,
      startDate,
      endDate,
      format,
      scope === 'single' ? animalId : null
    );
    showSuccess(t('reports:messages.success_generated', { ns: 'reports' }));
  } catch (error) {
    console.error('帳票生成エラー:', error);
    showError(error.message || t('reports:messages.error_general', { ns: 'reports' }));
  } finally {
    hideLoading();
  }
}

async function generateReport(reportType, startDate, endDate, format, animalId) {
  if (format === 'pdf') {
    await generatePDFReport(reportType, startDate, endDate, animalId);
  } else if (format === 'csv') {
    await generateCSVReport(reportType, startDate, endDate, animalId);
  } else if (format === 'excel') {
    await generateExcelReport(reportType, startDate, endDate, animalId);
  }
}

async function generatePDFReport(reportType, startDate, endDate, animalId) {
  const response = await fetch('/api/v1/pdf/report', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    credentials: 'same-origin',
    body: JSON.stringify({
      report_type: reportType,
      start_date: startDate,
      end_date: endDate,
      animal_id: animalId ? parseInt(animalId) : null,
      locale: i18next.language || 'ja',
    }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || t('reports:messages.error_pdf', { ns: 'reports' }));
  }

  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `medical_report_${startDate}_${endDate}.pdf`;
  document.body.appendChild(a);
  a.click();
  window.URL.revokeObjectURL(url);
  document.body.removeChild(a);
}

async function generateCSVReport(reportType, startDate, endDate, animalId) {
  const response = await fetch('/api/v1/reports/export', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    credentials: 'same-origin',
    body: JSON.stringify({
      report_type: reportType,
      start_date: startDate,
      end_date: endDate,
      animal_id: animalId ? parseInt(animalId) : null,
      format: 'csv',
      locale: i18next.language || 'ja',
    }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || t('reports:messages.error_csv', { ns: 'reports' }));
  }

  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `medical_report_${startDate}_${endDate}.csv`;
  document.body.appendChild(a);
  a.click();
  window.URL.revokeObjectURL(url);
  document.body.removeChild(a);
}

async function generateExcelReport(reportType, startDate, endDate, animalId) {
  const response = await fetch('/api/v1/reports/export', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    credentials: 'same-origin',
    body: JSON.stringify({
      report_type: reportType,
      start_date: startDate,
      end_date: endDate,
      animal_id: animalId ? parseInt(animalId) : null,
      format: 'excel',
      locale: i18next.language || 'ja',
    }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || t('reports:messages.error_excel', { ns: 'reports' }));
  }

  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `medical_report_${startDate}_${endDate}.xlsx`;
  document.body.appendChild(a);
  a.click();
  window.URL.revokeObjectURL(url);
  document.body.removeChild(a);
}

function showError(message) {
  const errorDiv = document.getElementById('error-message');
  const errorText = document.getElementById('error-text');
  if (!errorDiv || !errorText) return;

  errorText.textContent = message;
  errorDiv.classList.remove('hidden');

  setTimeout(() => {
    errorDiv.classList.add('hidden');
  }, 3000);

  errorDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function showSuccess(message) {
  const successDiv = document.getElementById('success-message');
  const successText = document.getElementById('success-text');
  if (!successDiv || !successText) return;

  successText.textContent = message;
  successDiv.classList.remove('hidden');

  setTimeout(() => {
    successDiv.classList.add('hidden');
  }, 3000);
}

function showLoading() {
  document.getElementById('loading-indicator')?.classList.remove('hidden');
}

function hideLoading() {
  document.getElementById('loading-indicator')?.classList.add('hidden');
}

window.setDateRange = setDateRange;

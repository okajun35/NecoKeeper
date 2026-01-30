/**
 * 猫編集ページのJavaScript
 */

const adminBasePath = window.ADMIN_BASE_PATH || window.__ADMIN_BASE_PATH__ || '/admin';

document.addEventListener('DOMContentLoaded', async () => {
  const animalId = getAnimalIdFromUrl();

  if (!animalId) {
    showError(translate('messages.id_missing', { ns: 'animals' }));
    return;
  }

  await loadAnimalData(animalId);
  setupFormSubmit(animalId);
});

document.addEventListener('i18nextInitialized', () => {
  if (cachedAnimal) {
    renderReadonlyInfo(cachedAnimal);
  }
});

function parseOptionalInt(value) {
  if (value === '' || value === null || value === undefined) {
    return null;
  }
  const parsed = Number.parseInt(value, 10);
  return Number.isNaN(parsed) ? null : parsed;
}

function parseBooleanSelect(value) {
  if (value === '' || value === null || value === undefined) {
    return null;
  }
  if (value === 'true') return true;
  if (value === 'false') return false;
  return null;
}

/**
 * URLから猫IDを取得
 */
function getAnimalIdFromUrl() {
  const pathParts = window.location.pathname.split('/');
  return pathParts[pathParts.length - 2]; // /admin/animals/{id}/edit
}

/**
 * 猫のデータを読み込み
 */
async function loadAnimalData(animalId) {
  try {
    const animal = await apiRequest(`${API_BASE}/animals/${animalId}`);
    const loadErrorMessage = translate('messages.load_error', { ns: 'animals' });
    if (!animal) {
      showError(loadErrorMessage);
      return;
    }
    fillForm(animal);
  } catch (error) {
    console.error('Error loading animal data:', error);
    const loadErrorMessage = translate('messages.load_error', { ns: 'animals' });
    showError(error?.message || loadErrorMessage);
  }
}

let cachedAnimal = null;

function getTranslator() {
  if (window.i18n?.t) {
    return window.i18n.t;
  }
  if (window.i18next?.t) {
    return window.i18next.t.bind(window.i18next);
  }
  return null;
}

function renderReadonlyInfo(animal) {
  cachedAnimal = animal;
  const t = getTranslator();
  const statusKey = animal.status ? `status.${animal.status}` : null;
  const locationKey = animal.location_type ? `location_type.${animal.location_type}` : null;

  document.getElementById('protected_at_display').textContent = animal.protected_at
    ? animal.protected_at.split('T')[0]
    : '-';
  document.getElementById('status_display').textContent =
    (t && statusKey
      ? t(statusKey, { ns: 'animals', defaultValue: animal.status })
      : animal.status) || '-';
  document.getElementById('location_display').textContent =
    (t && locationKey
      ? t(locationKey, { ns: 'animals', defaultValue: animal.location_type })
      : animal.location_type) || '-';
  document.getElementById('current_location_note_display').textContent =
    animal.current_location_note || '-';
}

/**
 * フォームにデータを入力
 */
function fillForm(animal) {
  // 詳細情報セクション（読み取り専用）の表示
  renderReadonlyInfo(animal);

  const requiredIds = [
    'name',
    'coat_color',
    'gender',
    'tail_length',
    'microchip_number',
    'rescue_source',
    'breed',
    'status',
    'protected_at',
    'location_type',
    'current_location_note',
    'features',
    'fiv_positive',
    'felv_positive',
    'is_sterilized',
    'sterilized_on',
  ];
  requiredIds.forEach(id => {
    if (!document.getElementById(id)) {
      console.warn(`fillForm: Expected element with id '${id}' not found.`);
    }
  });

  // 編集フォーム
  const nameElem = document.getElementById('name');
  if (nameElem) nameElem.value = animal.name || '';

  const coatColorElem = document.getElementById('coat_color');
  if (coatColorElem) coatColorElem.value = animal.coat_color || '';

  const coatColorNoteElem = document.getElementById('coat_color_note');
  if (coatColorNoteElem) coatColorNoteElem.value = animal.coat_color_note || '';

  const genderElem = document.getElementById('gender');
  if (genderElem) genderElem.value = animal.gender || '';

  const ageMonthsElem = document.getElementById('age_months');
  if (ageMonthsElem) {
    ageMonthsElem.value =
      animal.age_months === null || animal.age_months === undefined ? '' : animal.age_months;
  }
  const ageEstimatedElem = document.getElementById('age_is_estimated');
  if (ageEstimatedElem) {
    ageEstimatedElem.checked = animal.age_is_estimated || false;
  }
  const microchipElem = document.getElementById('microchip_number');
  if (microchipElem) {
    microchipElem.value = animal.microchip_number || '';
  }

  const tailLengthElem = document.getElementById('tail_length');
  if (tailLengthElem) tailLengthElem.value = animal.tail_length || '';

  const collarElem = document.getElementById('collar');
  if (collarElem) collarElem.value = animal.collar || '';

  const earCutElem = document.getElementById('ear_cut');
  if (earCutElem) earCutElem.checked = animal.ear_cut || false;

  const rescueSourceElem = document.getElementById('rescue_source');
  if (rescueSourceElem) rescueSourceElem.value = animal.rescue_source || '';

  const breedElem = document.getElementById('breed');
  if (breedElem) breedElem.value = animal.breed || '';

  const statusElem = document.getElementById('status');
  if (statusElem) statusElem.value = animal.status || '';

  const protectedAtElem = document.getElementById('protected_at');
  if (protectedAtElem) {
    protectedAtElem.value = animal.protected_at ? animal.protected_at.split('T')[0] : '';
  }

  const locationTypeElem = document.getElementById('location_type');
  if (locationTypeElem) {
    locationTypeElem.value = animal.location_type || '';
  }

  const currentLocationNoteElem = document.getElementById('current_location_note');
  if (currentLocationNoteElem) {
    currentLocationNoteElem.value = animal.current_location_note || '';
  }

  const featuresElem = document.getElementById('features');
  if (featuresElem) featuresElem.value = animal.features || '';

  const fivPositiveElem = document.getElementById('fiv_positive');
  if (fivPositiveElem) {
    fivPositiveElem.value =
      animal.fiv_positive === null ? '' : animal.fiv_positive ? 'true' : 'false';
  }

  const felvPositiveElem = document.getElementById('felv_positive');
  if (felvPositiveElem) {
    felvPositiveElem.value =
      animal.felv_positive === null ? '' : animal.felv_positive ? 'true' : 'false';
  }

  const isSterilizedElem = document.getElementById('is_sterilized');
  if (isSterilizedElem) {
    isSterilizedElem.value =
      animal.is_sterilized === null ? '' : animal.is_sterilized ? 'true' : 'false';
  }

  const sterilizedOnElem = document.getElementById('sterilized_on');
  if (sterilizedOnElem) {
    sterilizedOnElem.value = animal.sterilized_on ? animal.sterilized_on.split('T')[0] : '';
  }
}

/**
 * フォーム送信を設定
 */
function setupFormSubmit(animalId) {
  const form = document.getElementById('edit-form');

  form.addEventListener('submit', async e => {
    e.preventDefault();

    const submitButton = form.querySelector('button[type="submit"]');
    const originalText = submitButton.textContent;
    submitButton.disabled = true;
    submitButton.textContent = translate('buttons.saving', { ns: 'common' });

    try {
      const formData = {
        name: document.getElementById('name').value,
        coat_color: document.getElementById('coat_color').value,
        coat_color_note: document.getElementById('coat_color_note').value || null,
        gender: document.getElementById('gender').value,
        age_months: parseOptionalInt(document.getElementById('age_months').value),
        age_is_estimated: document.getElementById('age_is_estimated').checked,
        microchip_number: document.getElementById('microchip_number').value || null,
        tail_length: document.getElementById('tail_length').value,
        collar: document.getElementById('collar').value || null,
        ear_cut: document.getElementById('ear_cut').checked,
        rescue_source: document.getElementById('rescue_source').value || null,
        breed: document.getElementById('breed').value || null,
        status: document.getElementById('status').value,
        protected_at: document.getElementById('protected_at').value || null,
        location_type: document.getElementById('location_type').value || 'FACILITY',
        current_location_note: document.getElementById('current_location_note').value || null,
        features: document.getElementById('features').value || null,
        fiv_positive: parseBooleanSelect(document.getElementById('fiv_positive').value),
        felv_positive: parseBooleanSelect(document.getElementById('felv_positive').value),
        is_sterilized: parseBooleanSelect(document.getElementById('is_sterilized').value),
        sterilized_on: document.getElementById('sterilized_on').value || null,
      };

      await apiRequest(`${API_BASE}/animals/${animalId}`, {
        method: 'PUT',
        body: JSON.stringify(formData),
      });

      // 成功メッセージを表示
      showSuccess(translate('messages.updated', { ns: 'animals' }));

      // 詳細ページにリダイレクト
      setTimeout(() => {
        window.location.href = `${adminBasePath}/animals/${animalId}`;
      }, 1000);
    } catch (error) {
      console.error('Error updating animal:', error);
      showError(error.message);
      submitButton.disabled = false;
      submitButton.textContent = originalText;
    }
  });
}

/**
 * 成功メッセージを表示
 */
function showSuccess(message) {
  const alert = document.createElement('div');
  alert.className =
    'fixed top-4 right-4 bg-green-50 border border-green-200 rounded-lg p-4 shadow-lg z-50';
  alert.innerHTML = `
    <div class="flex items-center gap-2">
      <span class="text-green-800">${message}</span>
      <button onclick="this.parentElement.parentElement.remove()"
              class="text-green-600 hover:text-green-800">✕</button>
    </div>
  `;
  document.body.appendChild(alert);

  setTimeout(() => alert.remove(), 3000);
}

/**
 * エラーメッセージを表示
 */
function showError(message) {
  const alert = document.createElement('div');
  alert.className =
    'fixed top-4 right-4 bg-red-50 border border-red-200 rounded-lg p-4 shadow-lg z-50';
  alert.innerHTML = `
    <div class="flex items-center gap-2">
      <span class="text-red-800">${message}</span>
      <button onclick="this.parentElement.parentElement.remove()"
              class="text-red-600 hover:text-red-800">✕</button>
    </div>
  `;
  document.body.appendChild(alert);

  setTimeout(() => alert.remove(), 5000);
}

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

function parseOptionalInt(value) {
  if (value === '' || value === null || value === undefined) {
    return null;
  }
  const parsed = Number.parseInt(value, 10);
  return Number.isNaN(parsed) ? null : parsed;
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
    fillForm(animal);
  } catch (error) {
    console.error('Error loading animal data:', error);
    showError(translate('messages.load_error', { ns: 'animals' }));
  }
}

/**
 * フォームにデータを入力
 */
function fillForm(animal) {
  document.getElementById('name').value = animal.name || '';
  document.getElementById('pattern').value = animal.pattern || '';
  document.getElementById('coat_color').value = animal.coat_color || '';
  document.getElementById('coat_color_note').value = animal.coat_color_note || '';
  document.getElementById('gender').value = animal.gender || '';
  document.getElementById('age_months').value =
    animal.age_months === null || animal.age_months === undefined ? '' : animal.age_months;
  document.getElementById('age_is_estimated').checked = animal.age_is_estimated || false;
  document.getElementById('tail_length').value = animal.tail_length || '';
  document.getElementById('collar').value = animal.collar || '';
  document.getElementById('ear_cut').checked = animal.ear_cut || false;
  document.getElementById('rescue_source').value = animal.rescue_source || '';
  document.getElementById('breed').value = animal.breed || '';
  document.getElementById('status').value = animal.status || '';
  document.getElementById('protected_at').value = animal.protected_at
    ? animal.protected_at.split('T')[0]
    : '';
  document.getElementById('features').value = animal.features || '';
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
        pattern: document.getElementById('pattern').value,
        coat_color: document.getElementById('coat_color').value || null,
        coat_color_note: document.getElementById('coat_color_note').value || null,
        gender: document.getElementById('gender').value,
        age_months: parseOptionalInt(document.getElementById('age_months').value),
        age_is_estimated: document.getElementById('age_is_estimated').checked,
        tail_length: document.getElementById('tail_length').value,
        collar: document.getElementById('collar').value || null,
        ear_cut: document.getElementById('ear_cut').checked,
        rescue_source: document.getElementById('rescue_source').value || null,
        breed: document.getElementById('breed').value || null,
        status: document.getElementById('status').value,
        protected_at: document.getElementById('protected_at').value || null,
        features: document.getElementById('features').value || null,
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

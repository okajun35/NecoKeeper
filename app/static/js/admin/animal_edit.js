/**
 * 猫編集ページのJavaScript
 */

document.addEventListener('DOMContentLoaded', async () => {
  const animalId = getAnimalIdFromUrl();

  if (!animalId) {
    showError('猫IDが指定されていません');
    return;
  }

  await loadAnimalData(animalId);
  setupFormSubmit(animalId);
});

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
    showError('猫情報の読み込みに失敗しました');
  }
}

/**
 * フォームにデータを入力
 */
function fillForm(animal) {
  document.getElementById('name').value = animal.name || '';
  document.getElementById('pattern').value = animal.pattern || '';
  document.getElementById('gender').value = animal.gender || '';
  document.getElementById('age').value = animal.age || '';
  document.getElementById('tail_length').value = animal.tail_length || '';
  document.getElementById('collar').value = animal.collar || '';
  document.getElementById('ear_cut').checked = animal.ear_cut || false;
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
    submitButton.textContent = '保存中...';

    try {
      const formData = {
        name: document.getElementById('name').value,
        pattern: document.getElementById('pattern').value,
        gender: document.getElementById('gender').value,
        age: document.getElementById('age').value,
        tail_length: document.getElementById('tail_length').value,
        collar: document.getElementById('collar').value || null,
        ear_cut: document.getElementById('ear_cut').checked,
        status: document.getElementById('status').value,
        protected_at: document.getElementById('protected_at').value || null,
        features: document.getElementById('features').value || null,
      };

      await apiRequest(`${API_BASE}/animals/${animalId}`, {
        method: 'PUT',
        body: JSON.stringify(formData),
      });

      // 成功メッセージを表示
      showSuccess('猫情報を更新しました');

      // 詳細ページにリダイレクト
      setTimeout(() => {
        window.location.href = `/admin/animals/${animalId}`;
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

/**
 * 猫新規登録ページのJavaScript
 */

const adminBasePath = window.ADMIN_BASE_PATH || window.__ADMIN_BASE_PATH__ || '/admin';

document.addEventListener('DOMContentLoaded', () => {
  setupDefaultValues();
  setupImagePreview();
  setupFormSubmit();
});

/**
 * デフォルト値を設定
 */
function setupDefaultValues() {
  // 保護日のデフォルト値を今日に設定
  const today = new Date().toISOString().split('T')[0];
  document.getElementById('protected_at').value = today;
}

/**
 * 画像プレビューを設定
 */
function setupImagePreview() {
  const fileInput = document.getElementById('profile-image');
  const preview = document.getElementById('profile-preview');
  const fileNameText = document.getElementById('profile-image-filename');

  if (!fileInput || !preview) {
    return;
  }

  const applyPlaceholderText = () => {
    if (!fileNameText) {
      return;
    }

    fileNameText.setAttribute('data-i18n', 'file_input.empty');
    fileNameText.setAttribute('data-i18n-ns', 'common');

    if (window.i18n && typeof window.i18n.translateElement === 'function') {
      window.i18n.translateElement(fileNameText);
    } else {
      fileNameText.textContent = '選択されていません';
    }

    fileNameText.classList.add('text-gray-500');
  };

  const showSelectedFileName = fileName => {
    if (!fileNameText) {
      return;
    }

    fileNameText.removeAttribute('data-i18n');
    fileNameText.removeAttribute('data-i18n-ns');
    fileNameText.textContent = fileName;
    fileNameText.classList.remove('text-gray-500');
  };

  applyPlaceholderText();

  fileInput.addEventListener('change', e => {
    const file = e.target.files[0];
    if (!file) {
      applyPlaceholderText();
      return;
    }

    // ファイルサイズチェック（5MB）
    if (file.size > 5 * 1024 * 1024) {
      showError('ファイルサイズは5MB以下にしてください');
      fileInput.value = '';
      applyPlaceholderText();
      return;
    }

    showSelectedFileName(file.name);

    // プレビュー表示
    const reader = new FileReader();
    reader.onload = e => {
      preview.src = e.target.result;
    };
    reader.readAsDataURL(file);
  });

  window.addEventListener('languageChanged', () => {
    if (fileInput.files.length === 0) {
      applyPlaceholderText();
    }
  });
}

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
 * フォーム送信を設定
 */
function setupFormSubmit() {
  const form = document.getElementById('new-form');

  form.addEventListener('submit', async e => {
    e.preventDefault();

    const submitButton = form.querySelector('button[type="submit"]');
    const originalText = submitButton.textContent;
    submitButton.disabled = true;
    submitButton.textContent = '登録中...';

    try {
      // バリデーション
      const protectedAt = document.getElementById('protected_at').value;
      if (!protectedAt) {
        showError('保護日を入力してください');
        submitButton.disabled = false;
        submitButton.textContent = originalText;
        return;
      }

      // 1. 猫の基本情報を登録
      const formData = {
        name: document.getElementById('name').value,
        coat_color: document.getElementById('coat_color').value,
        coat_color_note: document.getElementById('coat_color_note').value || null,
        gender: document.getElementById('gender').value,
        age_months: parseOptionalInt(document.getElementById('age_months').value),
        age_is_estimated: document.getElementById('age_is_estimated').checked,
        microchip_number: document.getElementById('microchip_number').value || null,
        tail_length: document.getElementById('tail_length').value,
        collar: document.getElementById('collar').value || undefined,
        ear_cut: document.getElementById('ear_cut').checked,
        rescue_source: document.getElementById('rescue_source').value || undefined,
        breed: document.getElementById('breed').value || undefined,
        status: document.getElementById('status').value,
        protected_at: protectedAt,
        location_type: document.getElementById('location_type').value || 'FACILITY',
        current_location_note: document.getElementById('current_location_note').value || null,
        features: document.getElementById('features').value || undefined,
        fiv_positive: parseBooleanSelect(document.getElementById('fiv_positive').value),
        felv_positive: parseBooleanSelect(document.getElementById('felv_positive').value),
        is_sterilized: parseBooleanSelect(document.getElementById('is_sterilized').value),
        sterilized_on: document.getElementById('sterilized_on').value || null,
      };

      const animal = await apiRequest(`${API_BASE}/animals`, {
        method: 'POST',
        body: JSON.stringify(formData),
      });

      // 2. プロフィール画像がある場合はアップロード
      const fileInput = document.getElementById('profile-image');
      if (fileInput.files.length > 0) {
        await uploadProfileImage(animal.id, fileInput.files[0]);
      }

      // 成功メッセージを表示
      showSuccess('猫を登録しました');

      // 詳細ページにリダイレクト
      setTimeout(() => {
        window.location.href = `${adminBasePath}/animals/${animal.id}`;
      }, 1000);
    } catch (error) {
      console.error('Error creating animal:', error);
      // エラーメッセージを適切に表示
      let errorMessage = '猫の登録に失敗しました';
      if (error.message) {
        errorMessage = error.message;
      } else if (typeof error === 'string') {
        errorMessage = error;
      }
      showError(errorMessage);
      submitButton.disabled = false;
      submitButton.textContent = originalText;
    }
  });
}

/**
 * プロフィール画像をアップロード
 */
async function uploadProfileImage(animalId, file) {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_BASE}/animals/${animalId}/profile-image`, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${getAccessToken()}`,
    },
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'プロフィール画像のアップロードに失敗しました');
  }

  return response.json();
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

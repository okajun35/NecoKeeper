/**
 * 猫新規登録ページのJavaScript
 */

document.addEventListener('DOMContentLoaded', () => {
  setupImagePreview();
  setupFormSubmit();
});

/**
 * 画像プレビューを設定
 */
function setupImagePreview() {
  const fileInput = document.getElementById('profile-image');
  const preview = document.getElementById('profile-preview');

  fileInput.addEventListener('change', e => {
    const file = e.target.files[0];
    if (file) {
      // ファイルサイズチェック（5MB）
      if (file.size > 5 * 1024 * 1024) {
        showError('ファイルサイズは5MB以下にしてください');
        fileInput.value = '';
        return;
      }

      // プレビュー表示
      const reader = new FileReader();
      reader.onload = e => {
        preview.src = e.target.result;
      };
      reader.readAsDataURL(file);
    }
  });
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
      // 1. 猫の基本情報を登録
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
        window.location.href = `/admin/animals/${animal.id}`;
      }, 1000);
    } catch (error) {
      console.error('Error creating animal:', error);
      showError(error.message);
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
      Authorization: `Bearer ${localStorage.getItem('token')}`,
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

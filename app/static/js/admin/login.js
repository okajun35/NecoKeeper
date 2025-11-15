/**
 * ログイン画面 JavaScript
 * Context7参照: /fastapi/fastapi (Trust Score: 9.9)
 */

const API_BASE = '/api/v1';

// エラー表示
function showError(message) {
  const errorDiv = document.getElementById('errorMessage');
  const errorText = document.getElementById('errorText');
  errorText.textContent = message;
  errorDiv.classList.remove('hidden');
}

// エラー非表示
function hideError() {
  const errorDiv = document.getElementById('errorMessage');
  errorDiv.classList.add('hidden');
}

// ログイン処理
async function login(email, password) {
  try {
    // OAuth2 Password Flow形式でリクエスト
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);

    const response = await fetch(`${API_BASE}/auth/token`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'ログインに失敗しました');
    }

    const data = await response.json();

    // トークンをlocalStorageに保存
    localStorage.setItem('access_token', data.access_token);
    localStorage.setItem('token_type', data.token_type);

    // ダッシュボードにリダイレクト
    window.location.href = '/admin';
  } catch (error) {
    console.error('Login error:', error);
    throw error;
  }
}

// フォーム送信イベント
document.getElementById('loginForm').addEventListener('submit', async e => {
  e.preventDefault();
  hideError();

  const email = document.getElementById('email').value;
  const password = document.getElementById('password').value;
  const loginButton = document.getElementById('loginButton');

  // ボタンを無効化
  loginButton.disabled = true;
  loginButton.textContent = 'ログイン中...';

  try {
    await login(email, password);
  } catch (error) {
    showError(error.message);

    // ボタンを有効化
    loginButton.disabled = false;
    loginButton.textContent = 'ログイン';
  }
});

// Enterキーでログイン
document.getElementById('password').addEventListener('keypress', e => {
  if (e.key === 'Enter') {
    document.getElementById('loginForm').dispatchEvent(new Event('submit'));
  }
});

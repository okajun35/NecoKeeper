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
      // detailが配列の場合（バリデーションエラー）は最初のエラーメッセージを使用
      let errorMessage = 'ログインに失敗しました';
      if (error.detail) {
        if (Array.isArray(error.detail)) {
          errorMessage = error.detail.map(e => e.msg).join(', ');
        } else if (typeof error.detail === 'string') {
          errorMessage = error.detail;
        }
      }
      throw new Error(errorMessage);
    }

    const data = await response.json();

    // 注意: トークンはサーバー側でHTTPOnly Cookieとして設定されます
    // JavaScriptからは直接アクセスできません（XSS対策）
    // ログイン成功後、自動的にCookieが送信されるようになります

    // ダッシュボードにリダイレクト
    window.location.href = '/admin';
  } catch (error) {
    console.error('Login error:', error);
    throw error;
  }
}

// フォーム送信イベント
const loginForm = document.getElementById('loginForm');
if (loginForm) {
  loginForm.addEventListener('submit', async e => {
    e.preventDefault();
    hideError();

    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const loginButton = document.getElementById('loginButton');

    // ボタンを無効化
    loginButton.disabled = true;
    // i18nが利用可能な場合は翻訳を使用
    if (window.i18n && window.i18n.t) {
      loginButton.textContent = window.i18n.t('login_button_loading', { ns: 'login' });
    } else {
      loginButton.textContent = 'ログイン中...';
    }

    try {
      await login(email, password);
    } catch (error) {
      showError(error.message);

      // ボタンを有効化
      loginButton.disabled = false;
      // i18nが利用可能な場合は翻訳を使用
      if (window.i18n && window.i18n.t) {
        loginButton.textContent = window.i18n.t('login_button', { ns: 'login' });
      } else {
        loginButton.textContent = 'ログイン';
      }
    }
  });
}

// Enterキーでログイン
const passwordField = document.getElementById('password');
if (passwordField) {
  passwordField.addEventListener('keypress', e => {
    if (e.key === 'Enter') {
      document.getElementById('loginForm').dispatchEvent(new Event('submit'));
    }
  });
}

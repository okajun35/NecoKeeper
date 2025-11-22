# 認証・認可仕様

## 概要

NecoKeeperの認証・認可システムは、JWT（JSON Web Token）ベースのステートレス認証を採用しています。

### 設計原則

1. **ステートレス**: JWTトークンによるステートレス認証
2. **セキュリティ**: パスワードハッシュ化（Argon2）、トークン有効期限
3. **RBAC**: ロールベースアクセス制御
4. **監査**: ログイン履歴、操作ログの記録

## 認証フロー

### ログインフロー

```
┌─────────┐                ┌─────────┐                ┌─────────┐
│ Client  │                │ Backend │                │Database │
└────┬────┘                └────┬────┘                └────┬────┘
     │                          │                          │
     │ POST /api/v1/auth/token  │                          │
     │ {email, password}        │                          │
     ├─────────────────────────>│                          │
     │                          │                          │
     │                          │ SELECT * FROM users      │
     │                          │ WHERE email = ?          │
     │                          ├─────────────────────────>│
     │                          │                          │
     │                          │<─────────────────────────┤
     │                          │ User record              │
     │                          │                          │
     │                          │ verify_password()        │
     │                          │                          │
     │                          │ create_access_token()    │
     │                          │                          │
     │<─────────────────────────┤                          │
     │ {access_token, token_type}                          │
     │                          │                          │
     │ Store token in           │                          │
     │ localStorage             │                          │
     │                          │                          │
```

### 認証済みリクエストフロー

```
┌─────────┐                ┌─────────┐                ┌─────────┐
│ Client  │                │ Backend │                │Database │
└────┬────┘                └────┬────┘                └────┬────┘
     │                          │                          │
     │ GET /api/v1/animals      │                          │
     │ Authorization: Bearer {token}                       │
     ├─────────────────────────>│                          │
     │                          │                          │
     │                          │ verify_token()           │
     │                          │ decode JWT               │
     │                          │                          │
     │                          │ SELECT * FROM users      │
     │                          │ WHERE id = ?             │
     │                          ├─────────────────────────>│
     │                          │                          │
     │                          │<─────────────────────────┤
     │                          │ User record              │
     │                          │                          │
     │                          │ check_permissions()      │
     │                          │                          │
     │                          │ Execute business logic   │
     │                          │                          │
     │<─────────────────────────┤                          │
     │ Response data            │                          │
     │                          │                          │
```

## バックエンド実装

### JWT設定（app/config.py）

```python
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    """アプリケーション設定"""

    # JWT設定
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_hours: int = 2

    # セキュリティ設定
    password_min_length: int = 8
    max_login_attempts: int = 5
    lockout_duration_minutes: int = 30

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

@lru_cache()
def get_settings() -> Settings:
    """設定インスタンスを取得（キャッシュ付き）"""
    return Settings()
```


### JWT生成・検証（app/auth/jwt.py）

```python
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from jose import JWTError, jwt

from app.config import get_settings

settings = get_settings()


def create_access_token(
    data: dict[str, Any],
    expires_delta: timedelta | None = None,
) -> str:
    """
    JWTアクセストークンを生成

    Args:
        data: トークンに含めるデータ（user_id, role等）
        expires_delta: 有効期限（省略時は設定値を使用）

    Returns:
        str: JWTトークン

    Example:
        >>> token = create_access_token(
        ...     data={"user_id": 1, "role": "admin"},
        ...     expires_delta=timedelta(hours=2)
        ... )
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            hours=settings.access_token_expire_hours
        )

    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "sub": str(data["user_id"])
    })

    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.algorithm
    )

    return encoded_jwt


def decode_access_token(token: str) -> dict[str, Any]:
    """
    JWTトークンをデコード

    Args:
        token: JWTトークン

    Returns:
        dict: デコードされたペイロード

    Raises:
        JWTError: トークンが無効な場合

    Example:
        >>> payload = decode_access_token(token)
        >>> user_id = int(payload["sub"])
    """
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )
        return payload
    except JWTError as e:
        raise JWTError(f"Invalid token: {str(e)}") from e


def get_token_user_id(token: str) -> int:
    """
    トークンからユーザーIDを取得

    Args:
        token: JWTトークン

    Returns:
        int: ユーザーID

    Raises:
        JWTError: トークンが無効な場合
        ValueError: user_idが不正な場合
    """
    payload = decode_access_token(token)
    user_id_str = payload.get("sub")

    if user_id_str is None:
        raise ValueError("Token does not contain user_id")

    try:
        return int(user_id_str)
    except ValueError as e:
        raise ValueError(f"Invalid user_id in token: {user_id_str}") from e
```

### パスワードハッシュ化（app/auth/password.py）

```python
from __future__ import annotations

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

ph = PasswordHasher()


def hash_password(password: str) -> str:
    """
    パスワードをハッシュ化

    Args:
        password: 平文パスワード

    Returns:
        str: ハッシュ化されたパスワード

    Example:
        >>> hashed = hash_password("SecurePassword123")
    """
    return ph.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    パスワードを検証

    Args:
        plain_password: 平文パスワード
        hashed_password: ハッシュ化されたパスワード

    Returns:
        bool: パスワードが一致する場合True

    Example:
        >>> is_valid = verify_password("SecurePassword123", hashed)
    """
    try:
        ph.verify(hashed_password, plain_password)
        return True
    except VerifyMismatchError:
        return False


def needs_rehash(hashed_password: str) -> bool:
    """
    パスワードの再ハッシュ化が必要か判定

    Args:
        hashed_password: ハッシュ化されたパスワード

    Returns:
        bool: 再ハッシュ化が必要な場合True
    """
    return ph.check_needs_rehash(hashed_password)


def validate_password_policy(password: str) -> tuple[bool, str | None]:
    """
    パスワードポリシーを検証

    Args:
        password: 検証するパスワード

    Returns:
        tuple[bool, str | None]: (検証結果, エラーメッセージ)

    Example:
        >>> is_valid, error = validate_password_policy("weak")
        >>> if not is_valid:
        ...     print(error)
    """
    if len(password) < 8:
        return False, "パスワードは8文字以上である必要があります"

    if not any(c.isalpha() for c in password):
        return False, "パスワードには英字を含める必要があります"

    if not any(c.isdigit() for c in password):
        return False, "パスワードには数字を含める必要があります"

    return True, None
```

### 認証依存性（app/auth/dependencies.py）

```python
from __future__ import annotations

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.auth.jwt import get_token_user_id
from app.database import get_db
from app.models.user import User

# OAuth2スキーム設定
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    現在のユーザーを取得

    Args:
        token: JWTトークン
        db: データベースセッション

    Returns:
        User: 現在のユーザー

    Raises:
        HTTPException: トークンが無効、またはユーザーが存在しない場合

    Example:
        >>> @app.get("/api/v1/users/me")
        >>> async def read_users_me(
        ...     current_user: User = Depends(get_current_user)
        ... ):
        ...     return current_user
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        user_id = get_token_user_id(token)
    except Exception:
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()

    if user is None:
        raise credentials_exception

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    現在のアクティブユーザーを取得

    Args:
        current_user: 現在のユーザー

    Returns:
        User: アクティブなユーザー

    Raises:
        HTTPException: ユーザーが非アクティブの場合

    Example:
        >>> @app.get("/api/v1/animals")
        >>> async def list_animals(
        ...     current_user: User = Depends(get_current_active_user)
        ... ):
        ...     return animals
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )

    return current_user
```

### 権限チェック（app/auth/permissions.py）

```python
from __future__ import annotations

from collections.abc import Callable

from fastapi import Depends, HTTPException, status

from app.auth.dependencies import get_current_active_user
from app.models.user import User

# ロール別権限マトリクス
PERMISSIONS = {
    "admin": ["*"],  # 全権限
    "vet": [
        "animal:read",
        "animal:write",
        "medical:read",
        "medical:write",
        "medical:delete",
        "report:read",
    ],
    "staff": [
        "animal:read",
        "animal:write",
        "care:read",
        "care:write",
        "medical:read",
        "volunteer:read",
        "volunteer:write",
        "csv:export",
        "pdf:generate",
        "report:read",
        "report:write",
    ],
    "read_only": [
        "animal:read",
        "care:read",
        "medical:read",
        "volunteer:read",
        "report:read",
    ],
}


def has_permission(user: User, permission: str) -> bool:
    """
    ユーザーが指定された権限を持っているか判定

    Args:
        user: ユーザー
        permission: 権限文字列（例: "animal:write"）

    Returns:
        bool: 権限がある場合True

    Example:
        >>> if has_permission(user, "animal:write"):
        ...     # 猫情報を更新
        ...     pass
    """
    user_permissions = PERMISSIONS.get(user.role, [])

    # 管理者は全権限
    if "*" in user_permissions:
        return True

    # 完全一致
    if permission in user_permissions:
        return True

    # ワイルドカード一致（例: "animal:*"）
    resource, action = permission.split(":")
    wildcard = f"{resource}:*"
    if wildcard in user_permissions:
        return True

    return False


def require_permission(permission: str) -> Callable:
    """
    権限チェックデコレータ

    Args:
        permission: 必要な権限

    Returns:
        Callable: 依存性関数

    Example:
        >>> @app.post("/api/v1/animals")
        >>> async def create_animal(
        ...     current_user: User = Depends(require_permission("animal:write"))
        ... ):
        ...     # 猫を登録
        ...     pass
    """
    async def permission_checker(
        current_user: User = Depends(get_current_active_user),
    ) -> User:
        if not has_permission(current_user, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: {permission}"
            )
        return current_user

    return permission_checker


def require_role(roles: list[str]) -> Callable:
    """
    ロールチェックデコレータ

    Args:
        roles: 許可されたロールのリスト

    Returns:
        Callable: 依存性関数

    Example:
        >>> @app.post("/api/v1/medical-records")
        >>> async def create_medical_record(
        ...     current_user: User = Depends(require_role(["admin", "vet"]))
        ... ):
        ...     # 診療記録を登録
        ...     pass
    """
    async def role_checker(
        current_user: User = Depends(get_current_active_user),
    ) -> User:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role {current_user.role} is not allowed"
            )
        return current_user

    return role_checker
```


### 認証API（app/api/v1/auth.py）

```python
from __future__ import annotations

from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_active_user
from app.auth.jwt import create_access_token
from app.auth.password import verify_password
from app.config import get_settings
from app.database import get_db
from app.models.user import User
from app.schemas.auth import Token, UserResponse

router = APIRouter(prefix="/auth", tags=["認証"])
settings = get_settings()


@router.post("/token", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
) -> Token:
    """
    ログイン（JWTトークン取得）

    Args:
        form_data: ログインフォームデータ（username=email, password）
        db: データベースセッション

    Returns:
        Token: アクセストークンとトークンタイプ

    Raises:
        HTTPException: 認証失敗の場合

    Example:
        POST /api/v1/auth/token
        Content-Type: application/x-www-form-urlencoded

        username=admin@example.com&password=SecurePassword123

        Response:
        {
          "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
          "token_type": "bearer"
        }
    """
    # ユーザー検索
    user = db.query(User).filter(User.email == form_data.username).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # アカウントロックチェック
    if user.is_locked():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Account is locked until {user.locked_until}",
        )

    # パスワード検証
    if not verify_password(form_data.password, user.password_hash):
        # ログイン失敗回数を増やす
        user.increment_failed_login()
        db.commit()

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # ログイン成功
    user.reset_failed_login()
    db.commit()

    # JWTトークン生成
    access_token = create_access_token(
        data={"user_id": user.id, "role": user.role},
        expires_delta=timedelta(hours=settings.access_token_expire_hours)
    )

    return Token(access_token=access_token, token_type="bearer")


@router.get("/me", response_model=UserResponse)
async def read_users_me(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """
    現在のユーザー情報を取得

    Args:
        current_user: 現在のユーザー

    Returns:
        User: ユーザー情報

    Example:
        GET /api/v1/auth/me
        Authorization: Bearer {token}

        Response:
        {
          "id": 1,
          "email": "admin@example.com",
          "name": "管理者",
          "role": "admin",
          "is_active": true
        }
    """
    return current_user
```

## フロントエンド実装

### トークン管理（app/static/js/admin/common.js）

```javascript
/**
 * 認証トークンを取得
 *
 * @returns {string|null} アクセストークン
 *
 * @example
 * const token = getAccessToken();
 * if (!token) {
 *   window.location.href = '/admin/login';
 * }
 */
function getAccessToken() {
  return localStorage.getItem('access_token');
}

/**
 * 認証トークンを保存
 *
 * @param {string} token - アクセストークン
 * @param {string} tokenType - トークンタイプ（通常は "bearer"）
 *
 * @example
 * saveAccessToken(response.access_token, response.token_type);
 */
function saveAccessToken(token, tokenType = 'bearer') {
  localStorage.setItem('access_token', token);
  localStorage.setItem('token_type', tokenType);
}

/**
 * 認証トークンを削除
 *
 * @example
 * clearAccessToken();
 * window.location.href = '/admin/login';
 */
function clearAccessToken() {
  localStorage.removeItem('access_token');
  localStorage.removeItem('token_type');
}

/**
 * ログアウト処理
 *
 * @example
 * document.getElementById('logoutBtn').addEventListener('click', logout);
 */
function logout() {
  clearAccessToken();
  window.location.href = '/admin/login';
}

/**
 * 認証チェック
 *
 * @example
 * // ページ読み込み時に認証チェック
 * document.addEventListener('DOMContentLoaded', () => {
 *   if (!window.location.pathname.includes('/login')) {
 *     checkAuth();
 *   }
 * });
 */
function checkAuth() {
  const token = getAccessToken();
  if (!token) {
    window.location.href = '/admin/login';
  }
}

/**
 * APIリクエストを送信（認証ヘッダー付き）
 *
 * @param {string} url - リクエストURL
 * @param {object} options - fetchオプション
 * @returns {Promise<any>} レスポンスデータ
 *
 * @example
 * const animals = await apiRequest('/api/v1/animals', {
 *   method: 'GET',
 * });
 *
 * @example
 * const newAnimal = await apiRequest('/api/v1/animals', {
 *   method: 'POST',
 *   body: JSON.stringify(animalData),
 * });
 */
async function apiRequest(url, options = {}) {
  try {
    const token = getAccessToken();

    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...(token && { Authorization: `Bearer ${token}` }),
        ...options.headers,
      },
    });

    // 401エラーの場合はログイン画面にリダイレクト
    if (response.status === 401) {
      logout();
      return;
    }

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'リクエストに失敗しました');
    }

    return await response.json();
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
}
```

### ログインページ（app/static/js/admin/login.js）

```javascript
/**
 * ログインフォーム送信処理
 *
 * @example
 * document.getElementById('loginForm').addEventListener('submit', handleLogin);
 */
async function handleLogin(event) {
  event.preventDefault();

  const email = document.getElementById('email').value;
  const password = document.getElementById('password').value;
  const submitButton = event.target.querySelector('button[type="submit"]');

  // ボタンを無効化
  submitButton.disabled = true;
  submitButton.textContent = 'ログイン中...';

  try {
    // ログインAPIを呼び出し
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);

    const response = await fetch('/api/v1/auth/token', {
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

    // トークンを保存
    saveAccessToken(data.access_token, data.token_type);

    // ダッシュボードにリダイレクト
    window.location.href = '/admin';
  } catch (error) {
    console.error('Login error:', error);
    showError(error.message);
  } finally {
    // ボタンを有効化
    submitButton.disabled = false;
    submitButton.textContent = 'ログイン';
  }
}

/**
 * エラーメッセージを表示
 *
 * @param {string} message - エラーメッセージ
 */
function showError(message) {
  const errorDiv = document.getElementById('errorMessage');
  errorDiv.textContent = message;
  errorDiv.classList.remove('hidden');

  // 5秒後に非表示
  setTimeout(() => {
    errorDiv.classList.add('hidden');
  }, 5000);
}
```

### 認証済みページの初期化

```javascript
/**
 * ページ読み込み時の初期化
 *
 * @example
 * document.addEventListener('DOMContentLoaded', initPage);
 */
document.addEventListener('DOMContentLoaded', () => {
  // ログインページ以外では認証チェック
  if (!window.location.pathname.includes('/login')) {
    checkAuth();

    // ユーザー情報を取得して表示
    loadCurrentUser();
  }
});

/**
 * 現在のユーザー情報を取得して表示
 *
 * @example
 * await loadCurrentUser();
 */
async function loadCurrentUser() {
  try {
    const user = await apiRequest('/api/v1/auth/me');

    // ユーザー名を表示
    const userNameElement = document.getElementById('userName');
    if (userNameElement) {
      userNameElement.textContent = user.name;
    }

    // メールアドレスを表示
    const userEmailElement = document.getElementById('userEmail');
    if (userEmailElement) {
      userEmailElement.textContent = user.email;
    }

    // ロールに応じてメニューを表示/非表示
    updateMenuByRole(user.role);
  } catch (error) {
    console.error('Failed to load user:', error);
    // エラーの場合はログイン画面にリダイレクト
    logout();
  }
}

/**
 * ロールに応じてメニューを更新
 *
 * @param {string} role - ユーザーロール
 */
function updateMenuByRole(role) {
  // 管理者のみ表示するメニュー
  const adminOnlyMenus = document.querySelectorAll('[data-role="admin"]');
  adminOnlyMenus.forEach(menu => {
    menu.style.display = role === 'admin' ? 'block' : 'none';
  });

  // 獣医師のみ表示するメニュー
  const vetOnlyMenus = document.querySelectorAll('[data-role="vet"]');
  vetOnlyMenus.forEach(menu => {
    menu.style.display = ['admin', 'vet'].includes(role) ? 'block' : 'none';
  });
}
```


## ロール・権限マトリクス

### ロール定義

| ロール | 説明 | 対象ユーザー |
|-------|------|------------|
| admin | 管理者（全権限） | システム管理者 |
| vet | 獣医師 | 診療記録の作成・編集権限 |
| staff | スタッフ | 日常業務の権限 |
| read_only | 閲覧のみ | 閲覧専用ユーザー |

### 権限マトリクス

| 機能 | 権限 | admin | vet | staff | read_only |
|-----|------|-------|-----|-------|-----------|
| **猫管理** |
| 猫一覧表示 | animal:read | ✓ | ✓ | ✓ | ✓ |
| 猫登録・編集 | animal:write | ✓ | ✓ | ✓ | × |
| 猫削除 | animal:delete | ✓ | × | × | × |
| **世話記録** |
| 世話記録表示 | care:read | ✓ | ✓ | ✓ | ✓ |
| 世話記録登録・編集 | care:write | ✓ | ✓ | ✓ | × |
| **診療記録** |
| 診療記録表示 | medical:read | ✓ | ✓ | ✓ | ✓ |
| 診療記録登録・編集 | medical:write | ✓ | ✓ | × | × |
| 診療記録削除 | medical:delete | ✓ | ✓ | × | × |
| **ボランティア** |
| ボランティア表示 | volunteer:read | ✓ | ✓ | ✓ | ✓ |
| ボランティア登録・編集 | volunteer:write | ✓ | × | ✓ | × |
| **帳票・エクスポート** |
| 帳票閲覧 | report:read | ✓ | ✓ | ✓ | ✓ |
| 帳票作成 | report:write | ✓ | × | ✓ | × |
| CSV出力 | csv:export | ✓ | × | ✓ | × |
| PDF生成 | pdf:generate | ✓ | × | ✓ | × |

## セキュリティ考慮事項

### パスワードポリシー

1. **最小文字数**: 8文字以上
2. **文字種**: 英字と数字を含む
3. **ハッシュアルゴリズム**: Argon2（推奨）またはbcrypt
4. **ソルト**: 自動生成（Argon2/bcryptが自動処理）

### アカウントロック

1. **ログイン失敗回数**: 5回まで
2. **ロック期間**: 30分
3. **ロック解除**: 時間経過または管理者による手動解除

### トークンセキュリティ

1. **有効期限**: 2時間（設定可能）
2. **署名アルゴリズム**: HS256（HMAC-SHA256）
3. **シークレットキー**: 環境変数で管理（最低32文字）
4. **トークン保存**: localStorage（XSS対策が必要）

### HTTPS必須

本番環境では必ずHTTPSを使用してください。

```nginx
# Nginx設定例
server {
    listen 443 ssl http2;
    server_name necokeeper.example.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    # セキュリティヘッダー
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## エラーハンドリング

### 認証エラー

| エラー | HTTPステータス | メッセージ | 対応 |
|-------|--------------|-----------|------|
| トークンなし | 401 | Could not validate credentials | ログイン画面にリダイレクト |
| トークン無効 | 401 | Could not validate credentials | ログイン画面にリダイレクト |
| トークン期限切れ | 401 | Token has expired | ログイン画面にリダイレクト |
| ユーザー非アクティブ | 403 | Inactive user | エラーメッセージ表示 |
| アカウントロック | 403 | Account is locked until {time} | エラーメッセージ表示 |

### 認可エラー

| エラー | HTTPステータス | メッセージ | 対応 |
|-------|--------------|-----------|------|
| 権限不足 | 403 | Permission denied: {permission} | エラーメッセージ表示 |
| ロール不一致 | 403 | Role {role} is not allowed | エラーメッセージ表示 |

### フロントエンドエラーハンドリング

```javascript
/**
 * APIエラーをハンドリング
 *
 * @param {Error} error - エラーオブジェクト
 * @param {Response} response - レスポンスオブジェクト
 */
function handleApiError(error, response) {
  if (response.status === 401) {
    // 認証エラー: ログイン画面にリダイレクト
    showToast('セッションが期限切れです。再度ログインしてください。', 'error');
    setTimeout(() => {
      logout();
    }, 2000);
  } else if (response.status === 403) {
    // 認可エラー: エラーメッセージ表示
    showToast('この操作を実行する権限がありません。', 'error');
  } else {
    // その他のエラー
    showToast(error.message || 'エラーが発生しました。', 'error');
  }
}
```

## テスト仕様

### 認証テスト（tests/auth/test_auth_api.py）

```python
class TestLoginEndpoint:
    """ログインエンドポイントのテスト"""

    def test_login_success(self, test_client, test_user):
        """正常系: ログイン成功"""
        # When: 正しい認証情報でログイン
        response = test_client.post(
            "/api/v1/auth/token",
            data={
                "username": "test@example.com",
                "password": "TestPassword123",
            },
        )

        # Then: 200 OKとトークンが返される
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, test_client, test_user):
        """異常系: パスワード誤り"""
        # When: 誤ったパスワードでログイン
        response = test_client.post(
            "/api/v1/auth/token",
            data={
                "username": "test@example.com",
                "password": "WrongPassword",
            },
        )

        # Then: 401 Unauthorizedが返される
        assert response.status_code == 401

    def test_login_nonexistent_user(self, test_client):
        """異常系: 存在しないユーザー"""
        # When: 存在しないユーザーでログイン
        response = test_client.post(
            "/api/v1/auth/token",
            data={
                "username": "nonexistent@example.com",
                "password": "Password123",
            },
        )

        # Then: 401 Unauthorizedが返される
        assert response.status_code == 401


class TestCurrentUserEndpoint:
    """現在のユーザー情報取得のテスト"""

    def test_get_current_user_with_valid_token(
        self,
        test_client,
        auth_token,
    ):
        """正常系: 有効なトークンでユーザー情報取得"""
        # When: 有効なトークンでユーザー情報を取得
        response = test_client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        # Then: 200 OKとユーザー情報が返される
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "test@example.com"

    def test_get_current_user_without_token(self, test_client):
        """異常系: トークンなし"""
        # When: トークンなしでユーザー情報を取得
        response = test_client.get("/api/v1/auth/me")

        # Then: 401 Unauthorizedが返される
        assert response.status_code == 401
```

### 権限テスト（tests/auth/test_permissions.py）

```python
class TestPermissionsMatrix:
    """権限マトリクスのテスト"""

    def test_admin_has_all_permissions(self, admin_user):
        """管理者は全権限を持つ"""
        assert has_permission(admin_user, "animal:write")
        assert has_permission(admin_user, "medical:delete")
        assert has_permission(admin_user, "csv:export")

    def test_vet_has_medical_permissions(self, vet_user):
        """獣医師は診療記録の権限を持つ"""
        assert has_permission(vet_user, "medical:write")
        assert has_permission(vet_user, "medical:delete")

    def test_vet_cannot_export_csv(self, vet_user):
        """獣医師はCSV出力権限を持たない"""
        assert not has_permission(vet_user, "csv:export")

    def test_staff_has_csv_permissions(self, staff_user):
        """スタッフはCSV出力権限を持つ"""
        assert has_permission(staff_user, "csv:export")

    def test_read_only_can_only_read(self, read_only_user):
        """閲覧専用ユーザーは読み取り権限のみ"""
        assert has_permission(read_only_user, "animal:read")
        assert not has_permission(read_only_user, "animal:write")
```

## 監査ログ

### ログイン履歴

```python
# ログイン成功時
logger.info(
    f"User logged in: {user.email}",
    extra={
        "user_id": user.id,
        "ip_address": request.client.host,
        "user_agent": request.headers.get("user-agent"),
    }
)

# ログイン失敗時
logger.warning(
    f"Failed login attempt: {email}",
    extra={
        "email": email,
        "ip_address": request.client.host,
        "user_agent": request.headers.get("user-agent"),
    }
)
```

### 操作ログ

```python
# 重要な操作（作成・更新・削除）をログに記録
logger.info(
    f"Animal created: {animal.id}",
    extra={
        "user_id": current_user.id,
        "action": "create",
        "target_type": "animal",
        "target_id": animal.id,
    }
)
```

## サーバーサイド認証の実装（2025-11-23追加）

### 問題の背景

**問題**: 管理画面が一瞬表示されてからログイン画面にリダイレクトされる

**原因**: 認証チェックがJavaScriptのみで行われていた

```
❌ 旧実装（セキュリティリスク）
ブラウザ → サーバー（認証チェックなし）→ HTML返却
         ↓
      JavaScript実行 → JWTチェック → リダイレクト
```

**問題点**:
- サーバーが認証チェックせずにHTMLを返していた
- JavaScriptを無効にすると管理画面が見える
- HTMLソースに機密情報が含まれる可能性

### 解決策

**サーバーサイドでJWT認証を実装**

```
✅ 新実装（セキュア）
ブラウザ → サーバー（JWTで認証チェック）→ 401エラー → リダイレクト
                                    ↓
                                 認証OK → HTML返却
```

### 実装内容

#### 1. オプショナル認証依存関数（app/auth/dependencies.py）

```python
async def get_current_user_optional(
    request: Request, db: Session = Depends(get_db)
) -> User | None:
    """
    オプショナル認証（未認証でもエラーにしない）

    ログインページなど、認証済みユーザーをリダイレクトしたい場合に使用。
    未認証の場合はNoneを返し、エラーを発生させない。

    Context7参照: /fastapi/fastapi - Dependencies with try-except
    """
    try:
        # Authorizationヘッダーからトークンを取得
        authorization = request.headers.get("authorization")
        if not authorization:
            return None

        # "Bearer "プレフィックスを削除
        scheme, _, token = authorization.partition(" ")
        if scheme.lower() != "bearer":
            return None

        # トークンをデコード
        payload = decode_access_token(token)
        user_id = payload.get("sub")

        if user_id is None:
            return None

        # ユーザーIDを整数に変換
        try:
            user_id = int(user_id)
        except ValueError:
            return None

        # データベースからユーザーを取得
        user = db.query(User).filter(User.id == user_id).first()
        return user

    except (InvalidTokenError, HTTPException):
        return None
```

#### 2. 管理画面ルーティングの修正（app/api/v1/admin_pages.py）

```python
from app.auth.dependencies import get_current_user, get_current_user_optional

# ログインページ: オプショナル認証
@router.get("/login", response_class=HTMLResponse)
async def login_page(
    request: Request,
    current_user: User | None = Depends(get_current_user_optional)
) -> Response:
    """
    ログインページ
    既にログイン済みの場合はダッシュボードにリダイレクト
    """
    if current_user:
        return RedirectResponse(url="/admin", status_code=302)

    return templates.TemplateResponse("admin/login.html", {"request": request})


# ダッシュボード: 認証必須
@router.get("", response_class=HTMLResponse)
async def dashboard_page(
    request: Request,
    current_user: User = Depends(get_current_user)  # 認証必須
) -> Response:
    """
    ダッシュボード（認証必須）
    未認証の場合は自動的に401エラー
    """
    return templates.TemplateResponse(
        "admin/dashboard.html",
        {"request": request, "user": current_user}
    )


# その他の全管理画面エンドポイント: 認証必須
@router.get("/animals", response_class=HTMLResponse)
async def animals_list_page(
    request: Request,
    current_user: User = Depends(get_current_user)
) -> Response:
    """猫一覧ページ（認証必須）"""
    return templates.TemplateResponse("admin/animals/list.html", {"request": request})
```

#### 3. カスタム例外ハンドラー（app/main.py）

```python
from starlette.exceptions import HTTPException as StarletteHTTPException

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse | RedirectResponse:
    """
    HTTPException用のカスタムハンドラー

    管理画面の401エラーはログインページにリダイレクト。
    APIエンドポイントはJSONエラーを返す。

    Context7参照: /fastapi/fastapi - Custom Exception Handlers
    """
    # 管理画面の401エラーはログインページにリダイレクト
    # ログインページ自体への401はリダイレクトしない（無限ループ防止）
    if (
        exc.status_code == 401
        and request.url.path.startswith("/admin")
        and not request.url.path.startswith("/admin/login")
    ):
        return RedirectResponse(url="/admin/login", status_code=302)

    # APIエンドポイントはJSONエラーを返す
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers=exc.headers if hasattr(exc, "headers") else None,
    )
```

### セキュリティ改善

✅ **サーバーサイドで認証チェック**: JWTトークンをサーバーで検証
✅ **管理画面HTMLが認証なしで取得不可**: 401エラーを返す
✅ **JavaScriptを無効にしても管理画面が見えない**: サーバーで防御
✅ **401エラー時の適切なリダイレクト**: ログインページに誘導

### JWTが適切な理由

#### ❌ 誤解: 「JWTは問題がある」

今回の問題は**JWTの問題ではなく、実装の問題**でした。

#### ✅ 正解: 「JWTは適切だが、サーバーサイドで検証が必要」

**JWTの利点**:
1. **ステートレス認証**: サーバーにセッション情報を保存不要
2. **水平スケーリング**: 複数サーバーで認証情報を共有可能
3. **マイクロサービス対応**: APIとWebアプリで同じトークンを使用
4. **モバイルアプリ対応**: Cookie不要（REST APIの標準）

**重要**: JWTを使う場合も、**サーバーサイドで必ず検証**すること

### テスト結果

- **全525テストPass** ✅
- **カバレッジ**: 73.48% → **83.02%** (+9.54%)
- **認証依存関数**: 76.12%
- **管理画面ページ**: 86.96%

### 参考資料

- **Context7参照**: `/fastapi/fastapi` - Security Dependencies, RedirectResponse, Custom Exception Handlers
- **実装日**: 2025-11-23
- **コミット**: `fix(auth): サーバーサイド認証を実装してセキュリティ問題を修正`

---

## 今後の拡張

### Phase 2以降の機能

1. **リフレッシュトークン**: 長期間有効なトークンの管理
2. **2要素認証（2FA）**: TOTPによる追加認証
3. **OAuth2連携**: Google/GitHub等の外部認証
4. **パスワードリセット**: メール経由のパスワードリセット
5. **セッション管理**: アクティブセッションの一覧・無効化
6. **監査ログUI**: 管理画面での監査ログ閲覧
7. **IP制限**: 特定IPアドレスからのアクセス制限
8. **レート制限**: APIリクエストのレート制限

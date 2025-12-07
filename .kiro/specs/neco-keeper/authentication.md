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
# Example Nginx configuration

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
* Handle API errors.

* @param {Error} error - Error object.
* @param {Response} response - Response object.
    // 認証エラー: ログイン画面にリダイレクト
    showToast('セッションが期限切れです。再度ログインしてください。', 'error');
    // Authentication error: redirect to login page
    showToast('Your session has expired. Please log in again.', 'error');
    // 認可エラー: エラーメッセージ表示
    showToast('この操作を実行する権限がありません。', 'error');
    // Authorization error: show error message
    showToast('You do not have permission to perform this action.', 'error');
    // その他のエラー
    showToast(error.message || 'エラーが発生しました。', 'error');
    // Other errors
    showToast(error.message || 'An error has occurred.', 'error');
## Test Specification

### Authentication Tests (`tests/auth/test_auth_api.py`)
class TestLoginEndpoint:
    """Tests for the login endpoint."""
    def test_login_success(self, test_client, test_user):
        """Success case: login succeeds."""
    # Then: 200 OK and a token are returned
    # Then: 200 OK and a token are returned
    def test_login_wrong_password(self, test_client, test_user):
        """Error case: wrong password."""
    # Then: 401 Unauthorized is returned
    # Then: 401 Unauthorized is returned
    def test_login_nonexistent_user(self, test_client):
        """Error case: non-existent user."""
    # Then: 401 Unauthorized is returned
    # Then: 401 Unauthorized is returned
class TestCurrentUserEndpoint:
    """Tests for retrieving current user information."""
    """Success case: get user info with valid token."""
    # Then: 200 OK and user info are returned
    # Then: 200 OK and user info are returned
    def test_get_current_user_without_token(self, test_client):
        """Error case: no token."""
    # Then: 401 Unauthorized is returned
    # Then: 401 Unauthorized is returned
### Permission Tests (`tests/auth/test_permissions.py`)
class TestPermissionsMatrix:
    """Tests for the permission matrix."""
    def test_admin_has_all_permissions(self, admin_user):
        """Admin has all permissions."""
    def test_vet_has_medical_permissions(self, vet_user):
        """Vet has permissions for medical records."""
    def test_vet_cannot_export_csv(self, vet_user):
        """Vet does not have CSV export permission."""
    def test_staff_has_csv_permissions(self, staff_user):
        """Staff has CSV export permission."""
    def test_read_only_can_only_read(self, read_only_user):
        """Read-only users only have read permissions."""
## Audit Logs

### Login History

# On successful login

# On failed login

### Operation Logs

# Log important operations (create/update/delete)

## Server-side Authentication Implementation (added 2025-11-23)

### Background

**Problem**: The admin page briefly appeared before redirecting to the login screen.

**Cause**: Authentication checks were performed only in JavaScript.

❌ Previous implementation (security risk)
Browser → Server (no auth check) → HTML returned
         ↓
      JavaScript runs → JWT check → redirect

**Issues**:
- Server returned HTML without performing authentication checks.
- If JavaScript was disabled, the admin screen could be seen.
- Confidential information might be included in the HTML source.

### Solution

**Implement JWT authentication on the server side.**

✅ New implementation (secure)
Browser → Server (auth check with JWT) → 401 error → redirect
                                    ↓
                                 Auth OK → HTML returned

### Implementation Details

#### 1. Optional authentication dependency function (`app/auth/dependencies.py`)

    """Optional authentication (does not error if unauthenticated).

    Use this for pages like the login page where you want
    to redirect already authenticated users. If the user is
    unauthenticated, this returns None without raising an error.

    Context7 reference: /fastapi/fastapi - Dependencies with try-except
    """

        # Get token from Authorization header

        # Remove "Bearer " prefix

        # Decode token

        # Convert user ID to int

        # Retrieve user from the database

#### 2. Admin page routing changes (`app/api/v1/admin_pages.py`)

# Login page: optional authentication

    """Login page.

    If already authenticated, redirect to dashboard.
    """

# Dashboard: authentication required

    """Dashboard (authentication required).

    If unauthenticated, a 401 error is automatically raised.
    """

# All other admin endpoints: authentication required

    """Cat list page (authentication required)."""

#### 3. Custom exception handler (`app/main.py`)

    """Custom handler for ``HTTPException``.

    For admin pages, 401 errors are redirected to the login page.
    API endpoints return JSON errors.

    Context7 reference: /fastapi/fastapi - Custom Exception Handlers
    """

    # For admin pages, redirect 401 errors to the login page
    # Do not redirect 401 for the login page itself (avoid loop)

    # For API endpoints, return JSON errors

### Security Improvements

✅ **Server-side authentication checks**: JWT tokens are verified on the server.
✅ **Admin HTML cannot be fetched without auth**: 401 errors are returned.
✅ **Admin screen not visible even if JS is disabled**: Protected on the server.
✅ **Proper redirect on 401**: Users are redirected to the login page.

### Why JWT is Appropriate

#### ❌ Misconception: "JWT itself is the problem"

In this case, the issue was **not JWT itself, but the implementation**.

#### ✅ Correct understanding: "JWT is appropriate, but must be verified server-side"

**Advantages of JWT**:
1. **Stateless authentication**: No need to store session info on the server.
2. **Horizontal scaling**: Authentication can be shared across multiple servers.
3. **Microservice-friendly**: Same token can be used across APIs and web apps.
4. **Mobile-friendly**: No need for cookies (standard for REST APIs).

**Important**: Even when using JWT, **always validate tokens on the server side**.

### Test Results

- **All 525 tests passing** ✅
- **Coverage**: 73.48% → **83.02%** (+9.54%)
- **Authentication dependencies**: 76.12%
- **Admin pages**: 86.96%

### References

- **Context7 reference**: `/fastapi/fastapi` - Security Dependencies, RedirectResponse, Custom Exception Handlers
- **Implementation date**: 2025-11-23
- **Commit**: `fix(auth): implement server-side auth to fix security issue`

---

## Future Enhancements

### Features for Phase 2 and beyond

1. **Refresh tokens**: Manage long-lived tokens.
2. **Two-factor authentication (2FA)**: Additional verification via TOTP.
3. **OAuth2 integration**: External providers such as Google/GitHub.
4. **Password reset**: Password reset via email.
5. **Session management**: List and revoke active sessions.
6. **Audit log UI**: View audit logs in the admin panel.
7. **IP restrictions**: Restrict access from specific IP addresses.
8. **Rate limiting**: Apply rate limits to API requests.
# Authentication & Authorization Specification

## Overview

The NecoKeeper authentication and authorization system uses stateless authentication based on JWT (JSON Web Token).

### Design Principles

1. **Stateless**: Stateless authentication via JWT tokens
2. **Security**: Password hashing (Argon2) and token expiration
3. **RBAC**: Role-based access control
4. **Auditability**: Recording login history and operation logs

## Authentication Flow

### Login Flow

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

### Authenticated Request Flow

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

## Backend Implementation

### JWT Settings (`app/config.py`)

```python
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    """Application settings."""

    # JWT settings
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_hours: int = 2

    # Security settings
    password_min_length: int = 8
    max_login_attempts: int = 5
    lockout_duration_minutes: int = 30

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

@lru_cache()
def get_settings() -> Settings:
    """Get the settings instance (cached)."""
    return Settings()
```


### JWT Generation and Verification (`app/auth/jwt.py`)

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
    """Generate a JWT access token.

    Args:
        data: Data to include in the token (user_id, role, etc.).
        expires_delta: Expiration delta (if omitted, uses settings).

    Returns:
        str: Encoded JWT token.

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
    """Decode a JWT token.

    Args:
        token: JWT token.

    Returns:
        dict: Decoded payload.

    Raises:
        JWTError: If the token is invalid.

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
    """Extract the user ID from a token.

    Args:
        token: JWT token.

    Returns:
        int: User ID.

    Raises:
        JWTError: If the token is invalid.
        ValueError: If the user_id is invalid.
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

### Password Hashing (`app/auth/password.py`)

```python
from __future__ import annotations

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

ph = PasswordHasher()


def hash_password(password: str) -> str:
    """Hash a password.

    Args:
        password: Plain text password.

    Returns:
        str: Hashed password.

    Example:
        >>> hashed = hash_password("SecurePassword123")
    """
    return ph.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password.

    Args:
        plain_password: Plain text password.
        hashed_password: Hashed password.

    Returns:
        bool: True if the password is valid.

    Example:
        >>> is_valid = verify_password("SecurePassword123", hashed)
    """
    try:
        ph.verify(hashed_password, plain_password)
        return True
    except VerifyMismatchError:
        return False


def needs_rehash(hashed_password: str) -> bool:
    """Determine whether the password needs to be rehashed.

    Args:
        hashed_password: Hashed password.

    Returns:
        bool: True if rehash is required.
    """
    return ph.check_needs_rehash(hashed_password)


def validate_password_policy(password: str) -> tuple[bool, str | None]:
    """Validate the password policy.

    Args:
        password: Password to validate.

    Returns:
        tuple[bool, str | None]: (validation result, error message).

    Example:
        >>> is_valid, error = validate_password_policy("weak")
        >>> if not is_valid:
        ...     print(error)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."

    if not any(c.isalpha() for c in password):
        return False, "Password must contain at least one letter."

    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one digit."

    return True, None
```

### Authentication Dependencies (`app/auth/dependencies.py`)

```python
from __future__ import annotations

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.auth.jwt import get_token_user_id
from app.database import get_db
from app.models.user import User

# OAuth2 scheme definition
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Retrieve the current user.

    Args:
        token: JWT token.
        db: Database session.

    Returns:
        User: Current user.

    Raises:
        HTTPException: If the token is invalid or the user does not exist.

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
    """Retrieve the current active user.

    Args:
        current_user: Current user.

    Returns:
        User: Active user.

    Raises:
        HTTPException: If the user is inactive.

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

### Permission Checks (`app/auth/permissions.py`)

```python
from __future__ import annotations

from collections.abc import Callable

from fastapi import Depends, HTTPException, status

from app.auth.dependencies import get_current_active_user
from app.models.user import User

# Permission matrix per role
PERMISSIONS = {
    "admin": ["*"],  # all permissions
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
    """Check whether a user has the specified permission.

    Args:
        user: User instance.
        permission: Permission string (e.g., "animal:write").

    Returns:
        bool: True if the user has the permission.

    Example:
        >>> if has_permission(user, "animal:write"):
        ...     # update animal information
        ...     pass
    """
    user_permissions = PERMISSIONS.get(user.role, [])

    # Admin has all permissions
    if "*" in user_permissions:
        return True

    # Exact match
    if permission in user_permissions:
        return True

    # Wildcard match (e.g., "animal:*")
    resource, action = permission.split(":")
    wildcard = f"{resource}:*"
    if wildcard in user_permissions:
        return True

    return False


def require_permission(permission: str) -> Callable:
    """Dependency factory for permission checking.

    Args:
        permission: Required permission.

    Returns:
        Callable: Dependency function.

    Example:
        >>> @app.post("/api/v1/animals")
        >>> async def create_animal(
        ...     current_user: User = Depends(require_permission("animal:write"))
        ... ):
        ...     # create animal
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
    """Dependency factory for role checking.

    Args:
        roles: List of allowed roles.

    Returns:
        Callable: Dependency function.

    Example:
        >>> @app.post("/api/v1/medical-records")
        >>> async def create_medical_record(
        ...     current_user: User = Depends(require_role(["admin", "vet"]))
        ... ):
        ...     # create medical record
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


### Authentication API (`app/api/v1/auth.py`)

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

router = APIRouter(prefix="/auth", tags=["Authentication"])
settings = get_settings()


@router.post("/token", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
) -> Token:
    """Login and obtain a JWT token.

    Args:
        form_data: Login form data (username=email, password).
        db: Database session.

    Returns:
        Token: Access token and token type.

    Raises:
        HTTPException: If authentication fails.

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
    # Look up user
    user = db.query(User).filter(User.email == form_data.username).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check account lock status
    if user.is_locked():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Account is locked until {user.locked_until}",
        )

    # Verify password
    if not verify_password(form_data.password, user.password_hash):
        # Increment failed login count
        user.increment_failed_login()
        db.commit()

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Login success
    user.reset_failed_login()
    db.commit()

    # Generate JWT token
    access_token = create_access_token(
        data={"user_id": user.id, "role": user.role},
        expires_delta=timedelta(hours=settings.access_token_expire_hours)
    )

    return Token(access_token=access_token, token_type="bearer")


@router.get("/me", response_model=UserResponse)
async def read_users_me(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """Get the current user information.

    Args:
        current_user: Current user.

    Returns:
        User: User information.

    Example:
        GET /api/v1/auth/me
        Authorization: Bearer {token}

        Response:
        {
          "id": 1,
          "email": "admin@example.com",
          "name": "Admin",
          "role": "admin",
          "is_active": true
        }
    """
    return current_user
```

## Frontend Implementation

### Token Management (`app/static/js/admin/common.js`)

```javascript
/**
 * Get the authentication token.
 *
 * @returns {string|null} Access token.
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
 * Save the authentication token.
 *
 * @param {string} token - Access token.
 * @param {string} tokenType - Token type (usually "bearer").
 *
 * @example
 * saveAccessToken(response.access_token, response.token_type);
 */
function saveAccessToken(token, tokenType = 'bearer') {
  localStorage.setItem('access_token', token);
  localStorage.setItem('token_type', tokenType);
}

/**
 * Clear the authentication token.
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
 * Logout handler.
 *
 * @example
 * document.getElementById('logoutBtn').addEventListener('click', logout);
 */
function logout() {
  clearAccessToken();
  window.location.href = '/admin/login';
}

/**
 * Authentication check.
 *
 * @example
 * // Check authentication on page load
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
 * Send an API request (with auth header).
 *
 * @param {string} url - Request URL.
 * @param {object} options - fetch options.
 * @returns {Promise<any>} Response data.
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

    // On 401, redirect to login page
    if (response.status === 401) {
      logout();
      return;
    }

    if (!response.ok) {
      const error = await response.json();
    throw new Error(error.detail || 'Request failed');
    }

    return await response.json();
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
}
```

### Login Page (`app/static/js/admin/login.js`)

```javascript
/**
 * Handle login form submission.
 *
 * @example
 * document.getElementById('loginForm').addEventListener('submit', handleLogin);
 */
async function handleLogin(event) {
  event.preventDefault();

  const email = document.getElementById('email').value;
  const password = document.getElementById('password').value;
  const submitButton = event.target.querySelector('button[type="submit"]');

    // Disable button
    submitButton.disabled = true;
    submitButton.textContent = 'Logging in...';

  try {
    // Call login API
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
    throw new Error(error.detail || 'Login failed');
    }

    const data = await response.json();

    // Save token
    saveAccessToken(data.access_token, data.token_type);

    // Redirect to dashboard
    window.location.href = '/admin';
  } catch (error) {
    console.error('Login error:', error);
    showError(error.message);
  } finally {
    // Re-enable button
    submitButton.disabled = false;
    submitButton.textContent = 'Login';
  }
}

/**
 * Show error message.
 *
 * @param {string} message - Error message.
 */
function showError(message) {
  const errorDiv = document.getElementById('errorMessage');
  errorDiv.textContent = message;
  errorDiv.classList.remove('hidden');

    // Hide after 5 seconds
  setTimeout(() => {
    errorDiv.classList.add('hidden');
  }, 5000);
}
```

### Initialization for Authenticated Pages

```javascript
/**
 * Initialize page on load.
 *
 * @example
 * document.addEventListener('DOMContentLoaded', initPage);
 */
document.addEventListener('DOMContentLoaded', () => {
    // Check auth on all pages except login
  if (!window.location.pathname.includes('/login')) {
    checkAuth();

    // ユーザー情報を取得して表示
    loadCurrentUser();
  }
});

/**
 * Load and display current user.
 *
 * @example
 * await loadCurrentUser();
 */
async function loadCurrentUser() {
  try {
    const user = await apiRequest('/api/v1/auth/me');

    // Display user name
    const userNameElement = document.getElementById('userName');
    if (userNameElement) {
      userNameElement.textContent = user.name;
    }

    // Display email address
    const userEmailElement = document.getElementById('userEmail');
    if (userEmailElement) {
      userEmailElement.textContent = user.email;
    }

    // Show/hide menu items by role
    updateMenuByRole(user.role);
  } catch (error) {
    console.error('Failed to load user:', error);
    // On error, redirect to login page
    logout();
  }
}

/**
 * Update menu based on role.
 *
 * @param {string} role - User role.
 */
function updateMenuByRole(role) {
    // Menus visible only to admin
  const adminOnlyMenus = document.querySelectorAll('[data-role="admin"]');
  adminOnlyMenus.forEach(menu => {
    menu.style.display = role === 'admin' ? 'block' : 'none';
  });

    // Menus visible only to vets
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

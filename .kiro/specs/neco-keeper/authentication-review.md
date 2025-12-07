# Authentication Implementation Review (2025-11-23)

## 📋 Review Summary

The current authentication implementation was reviewed and validated
against FastAPI best practices.

**Context7 reference**: `/fastapi/fastapi` - Cookie Parameters, Security Dependencies, RedirectResponse

---

## 🔍 Current Implementation

### 1. Optional authentication dependency (`app/auth/dependencies.py`)

```python
async def get_current_user_optional(
    request: Request, db: Annotated[Session, Depends(get_db)]
) -> User | None:
    """Optional authentication (does not raise on unauthenticated users).

    Tries to obtain a token from Cookie or Authorization header and
    authenticate the user. Intended for pages like the login page
    where authenticated users should be redirected. If the user is
    unauthenticated, returns ``None`` without raising an error.
    """
    try:
        token = None

        # 1. Get token from Cookie (for HTML pages)
        cookie_token = request.cookies.get("access_token")
        if cookie_token:
            # Remove "Bearer " prefix
            if cookie_token.startswith("Bearer "):
                token = cookie_token[7:]
            else:
                token = cookie_token

        # 2. Get token from Authorization header (for API, backward compatible)
        if not token:
            authorization = request.headers.get("authorization")
            if authorization:
                scheme, _, header_token = authorization.partition(" ")
                if scheme.lower() == "bearer":
                    token = header_token

        if not token:
            return None

        # Decode token
        payload = decode_access_token(token)
        user_id = payload.get("sub")

        if user_id is None:
            return None

        # Convert user ID to int
        try:
            user_id = int(user_id)
        except ValueError:
            return None

        # Retrieve user from database
        user = db.query(User).filter(User.id == user_id).first()
        return user

    except (InvalidTokenError, HTTPException):
        return None
```

### 2. Hybrid Cookie/Header authentication dependency (`app/auth/dependencies.py`)

```python
async def get_current_user_from_cookie_or_header(
    request: Request, db: Annotated[Session, Depends(get_db)]
) -> User:
    """Get authentication information from Cookie or Authorization header.

    Authentication dependency that supports both HTML pages (Cookie)
    and APIs (Authorization header). Returns 401 if authentication
    fails.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="認証情報を検証できませんでした",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        token = None

        # 1. Get token from Cookie (for HTML pages)
        cookie_token = request.cookies.get("access_token")
        if cookie_token:
            if cookie_token.startswith("Bearer "):
                token = cookie_token[7:]
            else:
                token = cookie_token

        # 2. Get token from Authorization header (for API, backward compatible)
        if not token:
            authorization = request.headers.get("authorization")
            if authorization:
                scheme, _, header_token = authorization.partition(" ")
                if scheme.lower() == "bearer":
                    token = header_token

        if not token:
            raise credentials_exception

        # Decode token
        payload = decode_access_token(token)
        user_id = payload.get("sub")

        if user_id is None:
            raise credentials_exception

        # Convert user ID to int
        try:
            user_id = int(user_id)
        except ValueError as e:
            raise credentials_exception from e

        # Retrieve user from database
        user = db.query(User).filter(User.id == user_id).first()

        if user is None:
            raise credentials_exception

        return user

    except InvalidTokenError as e:
        raise credentials_exception from e


async def get_current_active_user(
    current_user: Annotated[
        User, Depends(get_current_user_from_cookie_or_header)
    ],
) -> User:
    """Get the current active user.

    Ensures that the user is active.
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="非アクティブなユーザーです"
        )

    # Check account lock status
    if current_user.is_locked():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Account is locked. Please try again after some time."
            ),
        )

    return current_user
```

### 3. Admin page routing (`app/api/v1/admin_pages.py`)

```python
from app.auth.dependencies import get_current_user_optional

# Login page: optional authentication
@router.get("/login", response_class=HTMLResponse)
async def login_page(
    request: Request,
    current_user: User | None = Depends(get_current_user_optional)
) -> Response:
    """Login page.

    If already logged in, redirect to dashboard.
    """
    if current_user:
        return RedirectResponse(url="/admin", status_code=302)

    return templates.TemplateResponse("admin/login.html", {"request": request})


# Dashboard: optional authentication + manual redirect
@router.get("", response_class=HTMLResponse)
async def dashboard_page(
    request: Request,
    current_user: User | None = Depends(get_current_user_optional)
) -> Response:
    """Dashboard (authentication required).

    If unauthenticated, redirect to the login page.
    """
    if not current_user:
        return RedirectResponse(url="/admin/login", status_code=302)

    return templates.TemplateResponse(
        "admin/dashboard.html",
        {"request": request, "user": current_user}
    )


# All other admin endpoints: optional authentication + manual redirect
@router.get("/animals", response_class=HTMLResponse)
async def animals_list_page(
    request: Request,
    current_user: User | None = Depends(get_current_user_optional)
) -> Response:
    """Cat list page (authentication required)."""
    if not current_user:
        return RedirectResponse(url="/admin/login", status_code=302)

    return templates.TemplateResponse(
        "admin/animals/list.html",
        {"request": request, "user": current_user}
    )
```

---

## ✅ Comparison with FastAPI Best Practices

### 1. Retrieving authentication info from Cookies

**Context7 reference**: `/fastapi/fastapi` - Cookie Parameters

✅ **Implementation is appropriate**
- Uses ``request.cookies.get("access_token")``
- Standard way of reading cookies in FastAPI
- Optional retrieval (returns ``None`` when not present)

**FastAPI recommended pattern**:
```python
# ✅ Current implementation
cookie_token = request.cookies.get("access_token")

# ✅ Alternative (Pydantic model)
from fastapi import Cookie
from pydantic import BaseModel

class AuthCookies(BaseModel):
    access_token: str | None = None

@router.get("/")
async def endpoint(cookies: Annotated[AuthCookies, Cookie()]):
    token = cookies.access_token
```

### 2. Optional dependency pattern

**Context7 reference**: `/fastapi/fastapi` - Dependencies with try-except

✅ **Implementation is appropriate**
- Uses ``try-except`` to catch exceptions and return ``None``
- Matches FastAPI's recommended pattern
- Allows unauthenticated access without raising errors

**FastAPI recommended pattern**:
```python
# ✅ Current implementation
async def get_current_user_optional(...) -> User | None:
    try:
        # 認証処理
        return user
    except (InvalidTokenError, HTTPException):
        return None
```

### 3. Use of ``RedirectResponse``

**Context7 reference**: `/fastapi/fastapi` - RedirectResponse

✅ **Implementation is appropriate**
- Uses ``RedirectResponse(url="/admin/login", status_code=302)``
- Uses 302 Found (temporary redirect)
- Standard redirect approach in FastAPI

**FastAPI recommended pattern**:
```python
# ✅ Current implementation
return RedirectResponse(url="/admin/login", status_code=302)

# ✅ Alternative (using response_class)
@router.get("/redirect", response_class=RedirectResponse)
async def redirect():
    return "/admin/login"
```

### 4. Hybrid authentication (Cookie + Header)

**Context7 reference**: `/fastapi/fastapi` - Cookie Parameters, Security Dependencies

✅ **Implementation is appropriate**
- HTML pages: read from Cookie
- APIs: read from Authorization header
- Flexible implementation supporting both

**FastAPI recommended pattern**:
```python
# ✅ Current implementation
# 1. Read from Cookie
cookie_token = request.cookies.get("access_token")

# 2. Read from Header
authorization = request.headers.get("authorization")
```

---

## ⚠️ Suggested Improvements

### Issue 1: Redundant authentication checks

**Current implementation**:
```python
# ❌ Same pattern repeated in all admin endpoints
@router.get("/admin")
async def dashboard_page(
    request: Request,
    current_user: User | None = Depends(get_current_user_optional)
) -> Response:
    if not current_user:
        return RedirectResponse(url="/admin/login", status_code=302)
    # ...

@router.get("/admin/animals")
async def animals_list_page(
    request: Request,
    current_user: User | None = Depends(get_current_user_optional)
) -> Response:
    if not current_user:
        return RedirectResponse(url="/admin/login", status_code=302)
    # ...
```

**Problems**:
- Violates the DRY principle (Don't Repeat Yourself)
- Same code is repeated in all endpoints
- Harder to maintain

**Recommended improvement 1: Custom exception handler**

```python
# app/main.py
from starlette.exceptions import HTTPException as StarletteHTTPException

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse | RedirectResponse:
    """Custom handler for ``HTTPException``.

    For admin pages, 401 errors are redirected to the login page.
    API endpoints return JSON errors.
    """
    # For admin pages, redirect 401 errors to the login page
    if (
        exc.status_code == 401
        and request.url.path.startswith("/admin")
        and not request.url.path.startswith("/admin/login")
    ):
        return RedirectResponse(url="/admin/login", status_code=302)

    # For API endpoints, return JSON errors
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers=exc.headers if hasattr(exc, "headers") else None,
    )


# app/api/v1/admin_pages.py
# ✅ After improvement: auth check is handled by dependency
@router.get("/admin")
async def dashboard_page(
    request: Request,
    current_user: User = Depends(get_current_active_user)  # raises 401
) -> Response:
    # No manual auth check required (handled by dependency)
    return templates.TemplateResponse(
        "admin/dashboard.html",
        {"request": request, "user": current_user}
    )
```

**Recommended improvement 2: Router-level dependency**

```python
# app/api/v1/admin_pages.py
from fastapi import APIRouter, Depends

# Apply authentication to the whole router
router = APIRouter(
    prefix="/admin",
    tags=["admin-pages"],
    dependencies=[Depends(get_current_active_user)]  # applied to all endpoints
)

# ✅ After improvement: no per-endpoint auth checks needed
@router.get("")
async def dashboard_page(
    request: Request,
    current_user: User = Depends(get_current_active_user)
) -> Response:
    return templates.TemplateResponse(
        "admin/dashboard.html",
        {"request": request, "user": current_user}
    )

# ログインページのみ例外（認証不要）
@router.get("/login", dependencies=[])  # 依存関数をオーバーライド
async def login_page(
    request: Request,
    current_user: User | None = Depends(get_current_user_optional)
) -> Response:
    if current_user:
        return RedirectResponse(url="/admin", status_code=302)
    return templates.TemplateResponse("admin/login.html", {"request": request})
```

### 問題点2: Cookieの設定が不完全

**現在の実装**:
- ログイン時にJavaScriptでCookieを設定
- サーバーサイドでCookieを設定していない

**推奨される改善**:

```python
# app/api/v1/auth.py
from fastapi.responses import JSONResponse

@router.post("/token", response_model=Token)
async def login(
    response: Response,  # Responseオブジェクトを注入
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
) -> Token:
    """
    ログイン（JWTトークン取得）

    Context7参照: /fastapi/fastapi - Set Cookies using Response Parameter
    """
    # ... 認証処理 ...

    # JWTトークン生成
    access_token = create_access_token(
        data={"user_id": user.id, "role": user.role},
        expires_delta=timedelta(hours=settings.access_token_expire_hours)
    )

    # ✅ サーバーサイドでCookieを設定
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,  # JavaScriptからアクセス不可（XSS対策）
        secure=True,    # HTTPS必須（本番環境）
        samesite="lax", # CSRF対策
        max_age=settings.access_token_expire_hours * 3600
    )

    return Token(access_token=access_token, token_type="bearer")
```

**セキュリティ上の利点**:
- `httponly=True`: XSS攻撃からトークンを保護
- `secure=True`: HTTPS経由でのみ送信
- `samesite="lax"`: CSRF攻撃を防止

---

## 📊 実装の妥当性評価

### ✅ 妥当な点

1. **Cookieベースの認証**
   - HTMLページで標準的な方法
   - JavaScriptなしでも動作
   - FastAPIの推奨パターンに準拠

2. **ハイブリッド認証**
   - Cookie（HTML）とHeader（API）の両方に対応
   - 柔軟な実装

3. **オプショナル依存関数**
   - `try-except`で例外を捕捉
   - FastAPIの推奨パターン

4. **RedirectResponse**
   - 標準的なリダイレクト方法
   - 適切なステータスコード（302）

5. **サーバーサイド認証**
   - JWTをサーバーで検証
   - セキュリティベストプラクティス

### ⚠️ 改善が必要な点

1. **冗長な認証チェック**
   - 全エンドポイントで`if not current_user`を繰り返し
   - カスタム例外ハンドラーまたはルーターレベルの依存関数を推奨

2. **Cookieの設定が不完全**
   - サーバーサイドでCookieを設定していない
   - `httponly`, `secure`, `samesite`フラグが未設定

3. **ドキュメントの不足**
   - Cookieベースの認証についての説明が不足
   - セキュリティ設定の説明が不足

---

## 🎯 推奨される改善手順

### Phase 1: カスタム例外ハンドラーの実装

1. `app/main.py`にカスタム例外ハンドラーを追加
2. 401エラーを自動的にリダイレクト
3. 管理画面エンドポイントで`get_current_active_user`を使用
4. 手動の`if not current_user`チェックを削除

### Phase 2: Cookieの設定改善

1. ログインエンドポイントでサーバーサイドでCookieを設定
2. `httponly`, `secure`, `samesite`フラグを設定
3. JavaScriptでのCookie設定を削除（オプション）

### Phase 3: ドキュメントの更新

1. `authentication.md`にCookieベースの認証を追加
2. セキュリティ設定の説明を追加
3. ベストプラクティスを追加

---

## 📚 参考資料

### Context7検証済み

- **Cookie Parameters**: `/fastapi/fastapi` - Cookie Parameters
- **Security Dependencies**: `/fastapi/fastapi` - Security Dependencies
- **RedirectResponse**: `/fastapi/fastapi` - RedirectResponse
- **Set Cookies**: `/fastapi/fastapi` - Set Cookies using Response Parameter
- **Custom Exception Handlers**: `/fastapi/fastapi` - Custom Exception Handlers

### FastAPIベストプラクティス

1. **Cookieベースの認証**
   - `request.cookies.get()`を使用
   - `httponly`, `secure`, `samesite`フラグを設定

2. **オプショナル依存関数**
   - `try-except`で例外を捕捉
   - Noneを返してエラーを発生させない

3. **カスタム例外ハンドラー**
   - 401エラーを自動的にリダイレクト
   - DRY原則に準拠

4. **ルーターレベルの依存関数**
   - 全エンドポイントに認証を適用
   - 個別のエンドポイントで認証チェック不要

---

## 📝 結論

**現在の実装は基本的に妥当ですが、以下の改善を推奨します**:

1. ✅ **Cookieベースの認証**: FastAPIの推奨パターンに準拠
2. ✅ **ハイブリッド認証**: Cookie（HTML）とHeader（API）の両方に対応
3. ✅ **サーバーサイド認証**: JWTをサーバーで検証
4. ⚠️ **冗長な認証チェック**: カスタム例外ハンドラーまたはルーターレベルの依存関数を推奨
5. ⚠️ **Cookieの設定が不完全**: `httponly`, `secure`, `samesite`フラグを設定

**優先度**:
- **高**: Cookieの設定改善（セキュリティ）
- **中**: カスタム例外ハンドラーの実装（保守性）
- **低**: ドキュメントの更新（可読性）

---

**作成日**: 2025-11-23
**Context7検証済み**: ✅
**レビュー担当**: Kiro AI Assistant

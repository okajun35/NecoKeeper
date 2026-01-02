"""
認証依存性モジュール

FastAPIのOAuth2PasswordBearerを使用した認証依存性を提供します。

Context7参照: /fastapi/fastapi
- OAuth2PasswordBearerスキーム
- get_current_user依存性（トークンからユーザー取得）
- get_current_user_optional依存性（オプショナル認証）
- get_current_active_user依存性（アクティブユーザーのみ）
"""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from sqlalchemy.orm import Session

from app.auth.jwt import decode_access_token
from app.database import get_db
from app.models.user import User

# OAuth2スキーム設定
# tokenUrl: トークン取得エンドポイントのパス
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    """
    現在のユーザーを取得

    JWTトークンを検証し、対応するユーザーをデータベースから取得します。

    Args:
        token: JWTアクセストークン（OAuth2PasswordBearerから自動取得）
        db: データベースセッション

    Returns:
        User: 認証されたユーザー

    Raises:
        HTTPException: トークンが無効、またはユーザーが見つからない場合
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="認証情報を検証できませんでした",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # トークンをデコード
        payload = decode_access_token(token)
        user_id = payload.get("sub")

        if user_id is None:
            raise credentials_exception

        # ユーザーIDを整数に変換
        try:
            user_id = int(user_id)
        except ValueError as e:
            raise credentials_exception from e

    except InvalidTokenError as e:
        raise credentials_exception from e

    # データベースからユーザーを取得
    user = db.query(User).filter(User.id == user_id).first()

    if user is None:
        raise credentials_exception

    return user


def get_current_user_optional(
    request: Request, db: Annotated[Session, Depends(get_db)]
) -> User | None:
    """
    オプショナル認証（未認証でもエラーにしない）

    CookieまたはAuthorizationヘッダーからトークンを取得し、認証を試みます。
    ログインページなど、認証済みユーザーをリダイレクトしたい場合に使用。
    未認証の場合はNoneを返し、エラーを発生させない。

    Context7参照: /fastapi/fastapi - Dependencies with try-except

    Args:
        request: FastAPIリクエストオブジェクト
        db: データベースセッション

    Returns:
        User | None: 認証済みユーザー、または未認証の場合はNone

    Example:
        @router.get("/login")
        async def login_page(
            request: Request,
            current_user: User | None = Depends(get_current_user_optional)
        ):
            if current_user:
                return RedirectResponse(url="/admin")
            return templates.TemplateResponse(
                "login.html", {"request": request}
            )
    """
    try:
        token = None

        # 1. Cookieからトークンを取得（HTMLページ用）
        cookie_token = request.cookies.get("access_token")
        if cookie_token:
            # "Bearer "プレフィックスを削除
            if cookie_token.startswith("Bearer "):
                token = cookie_token[7:]
            else:
                token = cookie_token

        # 2. Authorizationヘッダーからトークンを取得（API用、後方互換性）
        if not token:
            authorization = request.headers.get("authorization")
            if authorization:
                # "Bearer "プレフィックスを削除
                scheme, _, header_token = authorization.partition(" ")
                if scheme.lower() == "bearer":
                    token = header_token

        if not token:
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


def get_current_user_from_cookie_or_header(
    request: Request, db: Annotated[Session, Depends(get_db)]
) -> User:
    """
    CookieまたはAuthorizationヘッダーから認証情報を取得

    HTMLページ（Cookie）とAPI（Header）の両方に対応した認証依存関数。
    認証に失敗した場合は401エラーを返します。

    Args:
        request: FastAPIリクエストオブジェクト
        db: データベースセッション

    Returns:
        User: 認証されたユーザー

    Raises:
        HTTPException: 認証に失敗した場合
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="認証情報を検証できませんでした",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        token = None

        # 1. Cookieからトークンを取得（HTMLページ用）
        cookie_token = request.cookies.get("access_token")
        if cookie_token:
            if cookie_token.startswith("Bearer "):
                token = cookie_token[7:]
            else:
                token = cookie_token

        # 2. Authorizationヘッダーからトークンを取得（API用、後方互換性）
        if not token:
            authorization = request.headers.get("authorization")
            if authorization:
                scheme, _, header_token = authorization.partition(" ")
                if scheme.lower() == "bearer":
                    token = header_token

        if not token:
            raise credentials_exception

        # トークンをデコード
        payload = decode_access_token(token)
        user_id = payload.get("sub")

        if user_id is None:
            raise credentials_exception

        # ユーザーIDを整数に変換
        try:
            user_id = int(user_id)
        except ValueError as e:
            raise credentials_exception from e

        # データベースからユーザーを取得
        user = db.query(User).filter(User.id == user_id).first()

        if user is None:
            raise credentials_exception

        return user

    except InvalidTokenError as e:
        raise credentials_exception from e


def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user_from_cookie_or_header)],
) -> User:
    """
    現在のアクティブユーザーを取得

    ユーザーがアクティブ状態であることを確認します。

    Args:
        current_user: 認証されたユーザー

    Returns:
        User: アクティブなユーザー

    Raises:
        HTTPException: ユーザーが非アクティブまたはロックされている場合
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="非アクティブなユーザーです"
        )

    # アカウントロックチェック
    if current_user.is_locked():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="アカウントがロックされています。しばらくしてから再度お試しください",
        )

    return current_user

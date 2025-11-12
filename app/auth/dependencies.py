"""
認証依存性モジュール

FastAPIのOAuth2PasswordBearerを使用した認証依存性を提供します。

Context7参照: /fastapi/fastapi
- OAuth2PasswordBearerスキーム
- get_current_user依存性（トークンからユーザー取得）
- get_current_active_user依存性（アクティブユーザーのみ）
"""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from sqlalchemy.orm import Session

from app.auth.jwt import decode_access_token
from app.database import get_db
from app.models.user import User

# OAuth2スキーム設定
# tokenUrl: トークン取得エンドポイントのパス
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")


async def get_current_user(
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


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
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

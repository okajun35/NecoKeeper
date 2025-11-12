"""
認証APIエンドポイント

JWT + OAuth2 Password Flowによる認証エンドポイントを提供します。

Context7参照: /fastapi/fastapi
- POST /api/v1/auth/token（ログイン、JWTトークン取得）
- GET /api/v1/auth/me（現在のユーザー情報取得）
"""

from datetime import datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_active_user
from app.auth.jwt import create_access_token
from app.auth.password import verify_password
from app.database import get_db
from app.models.user import User
from app.schemas.auth import Token, UserResponse

router = APIRouter(prefix="/auth", tags=["認証"])


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[Session, Depends(get_db)],
):
    """
    ログインしてJWTアクセストークンを取得

    OAuth2 Password Flowに準拠したログインエンドポイント。
    ユーザー名（メールアドレス）とパスワードを検証し、
    JWTアクセストークンを返します。

    Args:
        form_data: OAuth2PasswordRequestForm（username, password）
        db: データベースセッション

    Returns:
        Token: アクセストークンとトークンタイプ

    Raises:
        HTTPException: 認証失敗時（401）
    """
    # ユーザーを検索（メールアドレスで）
    user = db.query(User).filter(User.email == form_data.username).first()

    # ユーザーが存在しない、またはパスワードが一致しない場合
    if not user or not verify_password(form_data.password, user.password_hash):
        # ログイン失敗回数をカウント
        if user:
            user.failed_login_count += 1

            # 5回失敗したらアカウントをロック（15分間）
            if user.failed_login_count >= 5:
                user.locked_until = datetime.now() + timedelta(minutes=15)

            db.commit()

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="メールアドレスまたはパスワードが正しくありません",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # アカウントがロックされているかチェック
    if user.is_locked():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="アカウントがロックされています。しばらくしてから再度お試しください",
        )

    # アクティブでないユーザーはログインできない
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="このアカウントは無効化されています",
        )

    # ログイン成功：失敗回数をリセット
    user.reset_failed_login()
    db.commit()

    # JWTアクセストークンを生成
    access_token = create_access_token(data={"user_id": user.id, "role": user.role})

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """
    現在のユーザー情報を取得

    認証されたユーザーの情報を返します。

    Args:
        current_user: 認証されたユーザー（依存性から自動取得）

    Returns:
        UserResponse: ユーザー情報
    """
    return current_user

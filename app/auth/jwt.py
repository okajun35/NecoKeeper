"""
JWT管理モジュール

PyJWTを使用したJWTトークンの生成と検証を提供します。

Context7参照: /jpadilla/pyjwt
- HS256アルゴリズムを使用したJWT生成・検証
- アクセストークンの有効期限管理（2時間）
"""

from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from jwt.exceptions import InvalidTokenError

from app.config import get_settings

# 設定を取得
settings = get_settings()

# JWT設定
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 2


def create_access_token(
    data: dict[str, Any], expires_delta: timedelta | None = None
) -> str:
    """
    JWTアクセストークンを生成

    Args:
        data: トークンに含めるデータ（user_id, roleなど）
        expires_delta: 有効期限（指定しない場合は2時間）

    Returns:
        str: JWTトークン文字列

    Example:
        >>> token = create_access_token({"user_id": 1, "role": "admin"})
        >>> # 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'
    """
    to_encode = data.copy()

    # 有効期限を設定
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)

    # 標準クレームを追加
    to_encode.update(
        {
            "exp": expire,  # 有効期限
            "iat": datetime.now(UTC),  # 発行時刻
            "sub": str(data.get("user_id")),  # サブジェクト（ユーザーID）
        }
    )

    # トークンを生成
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=ALGORITHM)

    return encoded_jwt


def decode_access_token(token: str) -> dict[str, Any]:
    """
    JWTアクセストークンを検証・デコード

    Args:
        token: JWTトークン文字列

    Returns:
        dict[str, Any]: デコードされたペイロード

    Raises:
        InvalidTokenError: トークンが無効な場合

    Example:
        >>> token = create_access_token({"user_id": 1})
        >>> payload = decode_access_token(token)
        >>> payload["user_id"]
        1
    """
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[ALGORITHM],
            options={
                "verify_signature": True,
                "verify_exp": True,
                "require": ["exp", "iat", "sub"],
            },
        )
        return payload
    except InvalidTokenError as e:
        raise InvalidTokenError(f"トークンの検証に失敗しました: {e!s}") from e


def get_token_user_id(token: str) -> int | None:
    """
    トークンからユーザーIDを取得

    Args:
        token: JWTトークン文字列

    Returns:
        Optional[int]: ユーザーID（取得できない場合はNone）

    Example:
        >>> token = create_access_token({"user_id": 1})
        >>> get_token_user_id(token)
        1
    """
    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        if user_id is None:
            return None
        return int(user_id)
    except (InvalidTokenError, ValueError):
        return None


def get_unverified_header(token: str) -> dict[str, Any]:
    """
    トークンのヘッダーを検証なしで取得

    デバッグやトークン形式の確認に使用します。

    Args:
        token: JWTトークン文字列

    Returns:
        dict[str, Any]: トークンヘッダー

    Example:
        >>> token = create_access_token({"user_id": 1})
        >>> header = get_unverified_header(token)
        >>> header["alg"]
        'HS256'
    """
    return jwt.get_unverified_header(token)


def get_unverified_claims(token: str) -> dict[str, Any]:
    """
    トークンのクレームを検証なしで取得

    デバッグやトークン内容の確認に使用します。
    本番環境では必ず decode_access_token() を使用してください。

    Args:
        token: JWTトークン文字列

    Returns:
        dict[str, Any]: トークンクレーム

    Warning:
        この関数は署名検証を行いません。
        本番環境では decode_access_token() を使用してください。

    Example:
        >>> token = create_access_token({"user_id": 1})
        >>> claims = get_unverified_claims(token)
        >>> claims["user_id"]
        1
    """
    return jwt.decode(token, options={"verify_signature": False})

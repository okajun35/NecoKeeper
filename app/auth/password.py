"""
パスワードハッシュ化ユーティリティ

argon2-cffiを使用したパスワードのハッシュ化と検証を提供します。
パスワードポリシーの検証機能も含まれています。

Context7参照: /hynek/argon2-cffi
- Argon2idアルゴリズムを使用（Password Hashing Competition優勝）
- bcryptより安全で高速
- パスワードポリシー検証（最小8文字、英数字混在）
"""

import re

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerifyMismatchError

# パスワードハッシュ化インスタンス
# Argon2idアルゴリズムを使用（デフォルトパラメータ）
ph = PasswordHasher()


def hash_password(password: str) -> str:
    """
    パスワードをArgon2idでハッシュ化

    Args:
        password: 平文パスワード

    Returns:
        str: Argon2idハッシュ化されたパスワード

    Example:
        >>> hash_password("mypassword123")
        '$argon2id$v=19$m=65536,t=3,p=4$...'
    """
    hashed: str = ph.hash(password)
    return hashed


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    パスワードを検証

    Args:
        plain_password: 平文パスワード
        hashed_password: ハッシュ化されたパスワード

    Returns:
        bool: パスワードが一致する場合True

    Example:
        >>> hash = hash_password("mypassword123")
        >>> verify_password("mypassword123", hash)
        True
        >>> verify_password("wrongpassword", hash)
        False
    """
    try:
        ph.verify(hashed_password, plain_password)
        return True
    except (VerifyMismatchError, InvalidHashError):
        return False


def validate_password_policy(password: str) -> tuple[bool, str | None]:
    """
    パスワードポリシーを検証

    ポリシー:
    - 最小8文字
    - 英字を含む
    - 数字を含む

    Args:
        password: 検証するパスワード

    Returns:
        tuple[bool, Optional[str]]: (検証結果, エラーメッセージ)

    Example:
        >>> validate_password_policy("short")
        (False, 'パスワードは最小8文字必要です')
        >>> validate_password_policy("onlyletters")
        (False, 'パスワードには英字と数字の両方を含める必要があります')
        >>> validate_password_policy("ValidPass123")
        (True, None)
    """
    # 最小文字数チェック
    if len(password) < 8:
        return False, "パスワードは最小8文字必要です"

    # 英字を含むかチェック
    if not re.search(r"[a-zA-Z]", password):
        return False, "パスワードには英字と数字の両方を含める必要があります"

    # 数字を含むかチェック
    if not re.search(r"\d", password):
        return False, "パスワードには英字と数字の両方を含める必要があります"

    return True, None


def needs_rehash(hashed_password: str) -> bool:
    """
    ハッシュが再ハッシュ化を必要とするかチェック

    パラメータが更新された場合にTrueを返します。

    Args:
        hashed_password: チェックするハッシュ

    Returns:
        bool: 再ハッシュ化が必要な場合True
    """
    try:
        needs_rehash: bool = ph.check_needs_rehash(hashed_password)
        return needs_rehash
    except InvalidHashError:
        # 無効なハッシュの場合は再ハッシュが必要
        return True

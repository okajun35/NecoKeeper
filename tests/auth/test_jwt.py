"""
JWT管理のテスト
"""

from datetime import timedelta

import pytest
from jwt.exceptions import InvalidTokenError

from app.auth.jwt import (
    create_access_token,
    decode_access_token,
    get_token_user_id,
    get_unverified_claims,
    get_unverified_header,
)


class TestJWTCreation:
    """JWTトークン生成のテストクラス"""

    def test_create_access_token(self):
        """アクセストークンを生成できる"""
        data = {"user_id": 1, "role": "admin"}
        token = create_access_token(data)

        # トークンが生成されること
        assert token is not None
        assert len(token) > 0

        # JWT形式であること（3つのパートがドットで区切られている）
        parts = token.split(".")
        assert len(parts) == 3

    def test_create_access_token_with_custom_expiration(self):
        """カスタム有効期限でトークンを生成できる"""
        data = {"user_id": 1, "role": "admin"}
        expires_delta = timedelta(minutes=30)
        token = create_access_token(data, expires_delta=expires_delta)

        assert token is not None
        assert len(token) > 0

    def test_decode_access_token(self):
        """トークンをデコードできる"""
        data = {"user_id": 1, "role": "admin"}
        token = create_access_token(data)

        payload = decode_access_token(token)

        # 元のデータが含まれていること
        assert payload["user_id"] == 1
        assert payload["role"] == "admin"

        # 標準クレームが含まれていること
        assert "sub" in payload
        assert "exp" in payload
        assert "iat" in payload

        # subにuser_idが設定されていること
        assert payload["sub"] == "1"

    def test_decode_invalid_token(self):
        """無効なトークンのデコードでエラーが発生する"""
        invalid_token = "invalid.token.here"

        with pytest.raises(InvalidTokenError):
            decode_access_token(invalid_token)

    def test_get_token_user_id(self):
        """トークンからユーザーIDを取得できる"""
        data = {"user_id": 42, "role": "staff"}
        token = create_access_token(data)

        user_id = get_token_user_id(token)

        assert user_id == 42

    def test_get_token_user_id_invalid_token(self):
        """無効なトークンからはNoneが返される"""
        invalid_token = "invalid.token.here"

        user_id = get_token_user_id(invalid_token)

        assert user_id is None


class TestJWTInspection:
    """JWT検査機能のテストクラス"""

    def test_get_unverified_header(self):
        """検証なしでヘッダーを取得できる"""
        data = {"user_id": 1}
        token = create_access_token(data)

        header = get_unverified_header(token)

        # ヘッダーにアルゴリズムが含まれていること
        assert "alg" in header
        assert header["alg"] == "HS256"

        # ヘッダーにタイプが含まれていること
        assert "typ" in header
        assert header["typ"] == "JWT"

    def test_get_unverified_claims(self):
        """検証なしでクレームを取得できる"""
        data = {"user_id": 1, "role": "admin"}
        token = create_access_token(data)

        claims = get_unverified_claims(token)

        # クレームにデータが含まれていること
        assert claims["user_id"] == 1
        assert claims["role"] == "admin"
        assert "sub" in claims
        assert "exp" in claims

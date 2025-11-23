"""
認証依存関数のテスト

オプショナル認証とセキュリティ境界のテスト。
Context7参照: /pytest-dev/pytest (Trust Score: 9.5)
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.user import User


class TestGetCurrentUserOptional:
    """get_current_user_optional のテスト"""

    @pytest.mark.asyncio
    async def test_returns_user_when_authenticated(
        self, test_client: TestClient, auth_token: str, test_db: Session
    ):
        """
        正常系: 認証済みの場合はユーザーを返す

        Given: 有効な認証トークン
        When: get_current_user_optional を呼び出す
        Then: ユーザーオブジェクトが返される
        """
        # Given
        from unittest.mock import Mock

        from fastapi import Request

        from app.auth.dependencies import get_current_user_optional

        request = Mock(spec=Request)
        request.cookies = Mock()
        request.cookies.get = Mock(return_value=None)
        request.headers = Mock()
        request.headers.get = Mock(return_value=f"Bearer {auth_token}")

        # When
        result = await get_current_user_optional(request, test_db)

        # Then
        assert result is not None
        assert isinstance(result, User)
        assert result.email == "test@example.com"

    @pytest.mark.asyncio
    async def test_returns_none_when_unauthenticated(
        self, test_client: TestClient, test_db: Session
    ):
        """
        正常系: 未認証の場合はNoneを返す

        Given: 認証トークンなし
        When: get_current_user_optional を呼び出す
        Then: Noneが返される（エラーにならない）
        """
        # Given
        from unittest.mock import Mock

        from fastapi import Request

        from app.auth.dependencies import get_current_user_optional

        request = Mock(spec=Request)
        request.cookies = Mock()
        request.cookies.get = Mock(return_value=None)
        request.headers = Mock()
        request.headers.get = Mock(return_value=None)

        # When
        result = await get_current_user_optional(request, test_db)

        # Then
        assert result is None

    @pytest.mark.asyncio
    async def test_returns_none_when_invalid_token(
        self, test_client: TestClient, test_db: Session
    ):
        """
        異常系: 無効なトークンの場合はNoneを返す

        Given: 無効な認証トークン
        When: get_current_user_optional を呼び出す
        Then: Noneが返される（エラーにならない）
        """
        # Given
        from unittest.mock import Mock

        from fastapi import Request

        from app.auth.dependencies import get_current_user_optional

        request = Mock(spec=Request)
        request.cookies = Mock()
        request.cookies.get = Mock(return_value=None)
        request.headers = Mock()
        request.headers.get = Mock(return_value="Bearer invalid-token")

        # When
        result = await get_current_user_optional(request, test_db)

        # Then
        assert result is None

    @pytest.mark.asyncio
    async def test_returns_none_when_expired_token(
        self, test_client: TestClient, test_db: Session
    ):
        """
        境界値テスト: 期限切れトークンの場合はNoneを返す

        Given: 期限切れの認証トークン
        When: get_current_user_optional を呼び出す
        Then: Noneが返される
        """
        # Given
        from datetime import timedelta
        from unittest.mock import Mock

        from fastapi import Request

        from app.auth.dependencies import get_current_user_optional
        from app.auth.jwt import create_access_token

        # 期限切れトークンを生成（過去の日時でトークン作成）
        expired_token = create_access_token(
            data={"sub": "test@example.com"}, expires_delta=timedelta(minutes=-30)
        )

        request = Mock(spec=Request)
        request.cookies = Mock()
        request.cookies.get = Mock(return_value=None)
        request.headers = Mock()
        request.headers.get = Mock(return_value=f"Bearer {expired_token}")

        # When
        result = await get_current_user_optional(request, test_db)

        # Then
        assert result is None

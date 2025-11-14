"""
権限チェックのテスト

ロールベースのアクセス制御（RBAC）のテスト。
セキュリティに直結する重要なビジネスルールをテストします。

t-wada視点: ドメインロジック（ビジネスルール）の最優先テスト
"""

from __future__ import annotations

import pytest
from fastapi import HTTPException

from app.auth.permissions import (
    PERMISSIONS,
    has_permission,
    require_permission,
    require_role,
)
from app.models.user import User


class TestPermissionsMatrix:
    """権限マトリクスのテスト（ビジネスルール検証）"""

    def test_admin_has_all_permissions(self):
        """管理者は全権限を持つ"""
        # Given
        admin = User(
            email="admin@example.com",
            password_hash="hash",
            name="Admin",
            role="admin",
        )

        # When/Then
        assert has_permission(admin, "animal:read")
        assert has_permission(admin, "animal:write")
        assert has_permission(admin, "medical:delete")
        assert has_permission(admin, "any:permission")  # 任意の権限

    def test_vet_has_medical_permissions(self):
        """獣医は診療記録の読み書き権限を持つ"""
        # Given
        vet = User(
            email="vet@example.com",
            password_hash="hash",
            name="Vet",
            role="vet",
        )

        # When/Then
        assert has_permission(vet, "medical:read")
        assert has_permission(vet, "medical:write")
        assert has_permission(vet, "medical:delete")

    def test_vet_cannot_import_csv(self):
        """獣医はCSVインポート権限を持たない"""
        # Given
        vet = User(
            email="vet@example.com",
            password_hash="hash",
            name="Vet",
            role="vet",
        )

        # When/Then
        assert not has_permission(vet, "csv:import")

    def test_staff_has_csv_permissions(self):
        """スタッフはCSVインポート/エクスポート権限を持つ"""
        # Given
        staff = User(
            email="staff@example.com",
            password_hash="hash",
            name="Staff",
            role="staff",
        )

        # When/Then
        assert has_permission(staff, "csv:import")
        assert has_permission(staff, "csv:export")

    def test_staff_cannot_delete_medical_records(self):
        """スタッフは診療記録の削除権限を持たない"""
        # Given
        staff = User(
            email="staff@example.com",
            password_hash="hash",
            name="Staff",
            role="staff",
        )

        # When/Then
        assert not has_permission(staff, "medical:delete")

    def test_read_only_can_only_read(self):
        """読み取り専用ユーザーは読み取り権限のみ"""
        # Given
        read_only = User(
            email="readonly@example.com",
            password_hash="hash",
            name="ReadOnly",
            role="read_only",
        )

        # When/Then
        assert has_permission(read_only, "animal:read")
        assert has_permission(read_only, "care:read")
        assert has_permission(read_only, "medical:read")
        assert not has_permission(read_only, "animal:write")
        assert not has_permission(read_only, "care:write")
        assert not has_permission(read_only, "medical:write")

    def test_unknown_role_has_no_permissions(self):
        """未知のロールは権限を持たない"""
        # Given
        unknown = User(
            email="unknown@example.com",
            password_hash="hash",
            name="Unknown",
            role="unknown_role",
        )

        # When/Then
        assert not has_permission(unknown, "animal:read")
        assert not has_permission(unknown, "animal:write")

    def test_all_roles_have_volunteer_read_permission(self):
        """すべてのロールがボランティア読み取り権限を持つ"""
        # Given
        roles = ["admin", "vet", "staff", "read_only"]

        # When/Then
        for role in roles:
            user = User(
                email=f"{role}@example.com",
                password_hash="hash",
                name=role.capitalize(),
                role=role,
            )
            assert has_permission(
                user, "volunteer:read"
            ), f"{role} should have volunteer:read"

    def test_staff_has_volunteer_write_permission(self):
        """スタッフはボランティア書き込み権限を持つ"""
        # Given
        staff = User(
            email="staff@example.com",
            password_hash="hash",
            name="Staff",
            role="staff",
        )

        # When/Then
        assert has_permission(staff, "volunteer:write")

    def test_vet_cannot_write_volunteers(self):
        """獣医はボランティア書き込み権限を持たない"""
        # Given
        vet = User(
            email="vet@example.com",
            password_hash="hash",
            name="Vet",
            role="vet",
        )

        # When/Then
        assert not has_permission(vet, "volunteer:write")


class TestRequireRole:
    """ロール要求のテスト（認可ロジック）"""

    @pytest.mark.asyncio
    async def test_require_role_allows_correct_role(self):
        """正しいロールのユーザーは許可される"""
        # Given
        admin = User(
            email="admin@example.com",
            password_hash="hash",
            name="Admin",
            role="admin",
            is_active=True,
        )
        checker = require_role(["admin", "staff"])

        # When
        result = await checker(admin)

        # Then
        assert result == admin

    @pytest.mark.asyncio
    async def test_require_role_denies_incorrect_role(self):
        """間違ったロールのユーザーは拒否される"""
        # Given
        read_only = User(
            email="readonly@example.com",
            password_hash="hash",
            name="ReadOnly",
            role="read_only",
            is_active=True,
        )
        checker = require_role(["admin", "staff"])

        # When/Then
        with pytest.raises(HTTPException) as exc_info:
            await checker(read_only)

        assert exc_info.value.status_code == 403
        assert "admin, staff" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_require_role_allows_any_of_multiple_roles(self):
        """複数のロールのいずれかを持つユーザーは許可される"""
        # Given
        staff = User(
            email="staff@example.com",
            password_hash="hash",
            name="Staff",
            role="staff",
            is_active=True,
        )
        checker = require_role(["admin", "staff", "vet"])

        # When
        result = await checker(staff)

        # Then
        assert result == staff


class TestRequirePermission:
    """権限要求のテスト（認可ロジック）"""

    @pytest.mark.asyncio
    async def test_require_permission_allows_user_with_permission(self):
        """権限を持つユーザーは許可される"""
        # Given
        staff = User(
            email="staff@example.com",
            password_hash="hash",
            name="Staff",
            role="staff",
            is_active=True,
        )
        checker = require_permission("animal:write")

        # When
        result = await checker(staff)

        # Then
        assert result == staff

    @pytest.mark.asyncio
    async def test_require_permission_denies_user_without_permission(self):
        """権限を持たないユーザーは拒否される"""
        # Given
        read_only = User(
            email="readonly@example.com",
            password_hash="hash",
            name="ReadOnly",
            role="read_only",
            is_active=True,
        )
        checker = require_permission("animal:write")

        # When/Then
        with pytest.raises(HTTPException) as exc_info:
            await checker(read_only)

        assert exc_info.value.status_code == 403
        assert "animal:write" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_require_permission_allows_admin_any_permission(self):
        """管理者は任意の権限を持つ"""
        # Given
        admin = User(
            email="admin@example.com",
            password_hash="hash",
            name="Admin",
            role="admin",
            is_active=True,
        )
        checker = require_permission("any:permission")

        # When
        result = await checker(admin)

        # Then
        assert result == admin

    @pytest.mark.asyncio
    async def test_require_permission_medical_delete_vet_only(self):
        """診療記録削除は獣医のみ可能"""
        # Given
        vet = User(
            email="vet@example.com",
            password_hash="hash",
            name="Vet",
            role="vet",
            is_active=True,
        )
        staff = User(
            email="staff@example.com",
            password_hash="hash",
            name="Staff",
            role="staff",
            is_active=True,
        )
        checker = require_permission("medical:delete")

        # When/Then: 獣医は許可される
        result = await checker(vet)
        assert result == vet

        # When/Then: スタッフは拒否される
        with pytest.raises(HTTPException) as exc_info:
            await checker(staff)
        assert exc_info.value.status_code == 403


class TestPermissionsMatrixCompleteness:
    """権限マトリクスの完全性テスト（設定ミス検出）"""

    def test_all_roles_defined(self):
        """すべての想定ロールが定義されている"""
        # Given
        expected_roles = ["admin", "vet", "staff", "read_only"]

        # When/Then
        for role in expected_roles:
            assert role in PERMISSIONS, f"Role '{role}' is not defined in PERMISSIONS"

    def test_admin_has_wildcard_permission(self):
        """管理者はワイルドカード権限を持つ"""
        # Given/When/Then
        assert "*" in PERMISSIONS["admin"]

    def test_no_role_has_empty_permissions(self):
        """どのロールも空の権限リストを持たない"""
        # Given/When/Then
        for role, permissions in PERMISSIONS.items():
            assert len(permissions) > 0, f"Role '{role}' has empty permissions"

    def test_read_only_has_only_read_permissions(self):
        """読み取り専用ロールは読み取り権限のみ"""
        # Given
        read_only_permissions = PERMISSIONS["read_only"]

        # When/Then
        for permission in read_only_permissions:
            assert (
                ":read" in permission
            ), f"read_only has non-read permission: {permission}"

    def test_staff_has_pdf_generate_permission(self):
        """スタッフはPDF生成権限を持つ"""
        # Given/When/Then
        assert "pdf:generate" in PERMISSIONS["staff"]

    def test_vet_has_report_read_permission(self):
        """獣医は帳票読み取り権限を持つ"""
        # Given/When/Then
        assert "report:read" in PERMISSIONS["vet"]

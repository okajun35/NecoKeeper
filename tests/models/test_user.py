"""
Userモデルの単体テスト

ユーザー認証とセキュリティ関連のビジネスルールをテストします。
"""

from datetime import datetime, timedelta

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.user import User


class TestUserModel:
    """Userモデルのテストクラス"""

    def test_create_user_with_required_fields(self, test_db: Session):
        """必須フィールドでユーザーを作成できることを確認"""
        user = User(
            email="admin@example.com",
            password_hash="hashed_password_123",
            name="管理者",
        )

        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)

        assert user.id is not None
        assert user.email == "admin@example.com"
        assert user.password_hash == "hashed_password_123"
        assert user.name == "管理者"

    def test_user_default_values(self, test_db: Session):
        """デフォルト値が正しく設定されることを確認"""
        user = User(
            email="staff@example.com",
            password_hash="hashed_password_456",
            name="スタッフ",
        )

        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)

        # デフォルト値の確認
        assert user.role == "read_only"
        assert user.is_active is True
        assert user.failed_login_count == 0
        assert user.locked_until is None
        assert user.created_at is not None
        assert user.updated_at is not None

    def test_user_with_role(self, test_db: Session):
        """ロールを指定してユーザーを作成できることを確認"""
        roles = ["admin", "staff", "vet", "read_only"]

        for role in roles:
            user = User(
                email=f"{role}@example.com",
                password_hash="hashed_password",
                name=f"{role}ユーザー",
                role=role,
            )

            test_db.add(user)
            test_db.commit()
            test_db.refresh(user)

            assert user.role == role

    def test_user_is_locked_when_not_locked(self, test_db: Session):
        """ロックされていないユーザーのis_locked()がFalseを返すことを確認"""
        user = User(
            email="user1@example.com",
            password_hash="hashed_password",
            name="ユーザー1",
        )

        test_db.add(user)
        test_db.commit()

        assert user.is_locked() is False

    def test_user_is_locked_when_locked(self, test_db: Session):
        """ロックされているユーザーのis_locked()がTrueを返すことを確認"""
        user = User(
            email="user2@example.com",
            password_hash="hashed_password",
            name="ユーザー2",
            locked_until=datetime.now() + timedelta(minutes=15),
        )

        test_db.add(user)
        test_db.commit()

        assert user.is_locked() is True

    def test_user_is_locked_when_lock_expired(self, test_db: Session):
        """ロック期限が切れたユーザーのis_locked()がFalseを返すことを確認"""
        user = User(
            email="user3@example.com",
            password_hash="hashed_password",
            name="ユーザー3",
            locked_until=datetime.now() - timedelta(minutes=1),
        )

        test_db.add(user)
        test_db.commit()

        assert user.is_locked() is False

    def test_user_reset_failed_login(self, test_db: Session):
        """reset_failed_login()がログイン失敗回数をリセットすることを確認"""
        user = User(
            email="user4@example.com",
            password_hash="hashed_password",
            name="ユーザー4",
            failed_login_count=5,
            locked_until=datetime.now() + timedelta(minutes=15),
        )

        test_db.add(user)
        test_db.commit()

        # リセット前の確認
        assert user.failed_login_count == 5
        assert user.locked_until is not None

        # リセット
        user.reset_failed_login()
        test_db.commit()
        test_db.refresh(user)

        # リセット後の確認
        assert user.failed_login_count == 0
        assert user.locked_until is None

    def test_user_failed_login_increment(self, test_db: Session):
        """ログイン失敗回数をインクリメントできることを確認"""
        user = User(
            email="user5@example.com",
            password_hash="hashed_password",
            name="ユーザー5",
        )

        test_db.add(user)
        test_db.commit()

        # 失敗回数をインクリメント
        for i in range(1, 6):
            user.failed_login_count += 1
            test_db.commit()
            test_db.refresh(user)
            assert user.failed_login_count == i

    def test_user_str_representation(self, test_db: Session):
        """文字列表現が正しいことを確認"""
        user = User(
            email="admin@example.com",
            password_hash="hashed_password",
            name="管理者",
            role="admin",
        )

        test_db.add(user)
        test_db.commit()

        assert str(user) == "管理者（admin）"

    def test_user_repr(self, test_db: Session):
        """repr表現が正しいことを確認"""
        user = User(
            email="staff@example.com",
            password_hash="hashed_password",
            name="スタッフ",
            role="staff",
        )

        test_db.add(user)
        test_db.commit()

        repr_str = repr(user)
        assert "User" in repr_str
        assert "id=" in repr_str
        assert "email='staff@example.com'" in repr_str
        assert "name='スタッフ'" in repr_str
        assert "role='staff'" in repr_str

    def test_user_email_uniqueness(self, test_db: Session):
        """メールアドレスがユニークであることを確認"""
        user1 = User(
            email="duplicate@example.com",
            password_hash="hashed_password_1",
            name="ユーザー1",
        )

        test_db.add(user1)
        test_db.commit()

        # 同じメールアドレスで2人目を作成しようとする
        user2 = User(
            email="duplicate@example.com",
            password_hash="hashed_password_2",
            name="ユーザー2",
        )

        test_db.add(user2)

        # ユニーク制約違反でエラーが発生することを確認
        with pytest.raises(IntegrityError):
            test_db.commit()

    def test_user_is_active_flag(self, test_db: Session):
        """is_activeフラグが正しく機能することを確認"""
        user = User(
            email="inactive@example.com",
            password_hash="hashed_password",
            name="無効ユーザー",
            is_active=False,
        )

        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)

        assert user.is_active is False

        # アクティブに変更
        user.is_active = True
        test_db.commit()
        test_db.refresh(user)

        assert user.is_active is True

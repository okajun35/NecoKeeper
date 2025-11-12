"""
ユーザー（User）モデル

システムユーザー（管理者、スタッフ、獣医師）を管理するORMモデルです。
"""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.database import Base


class User(Base):
    """
    ユーザーモデル

    システムにログインする管理者、スタッフ、獣医師を管理します。
    認証情報とロール（権限）を保持します。

    Attributes:
        id: 主キー（自動採番）
        email: メールアドレス（ユニーク、ログインID）
        password_hash: パスワードハッシュ（bcrypt）
        name: 氏名
        role: ロール（admin/staff/vet/read_only）
        is_active: アクティブ状態（True=有効、False=無効）
        failed_login_count: ログイン失敗回数
        locked_until: ロック解除日時（5回失敗後15分間ロック）
        created_at: 作成日時（自動設定）
        updated_at: 更新日時（自動更新）
    """

    __tablename__ = "users"

    # 主キー
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, comment="主キー"
    )

    # 認証情報
    email: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True, comment="メールアドレス（ログインID）"
    )

    password_hash: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="パスワードハッシュ（bcrypt）"
    )

    # ユーザー情報
    name: Mapped[str] = mapped_column(String(100), nullable=False, comment="氏名")

    role: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="read_only",
        server_default="read_only",
        comment="ロール（admin/staff/vet/read_only）",
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="1",
        comment="アクティブ状態（True=有効、False=無効）",
    )

    # セキュリティ
    failed_login_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
        comment="ログイン失敗回数",
    )

    locked_until: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True, comment="ロック解除日時（5回失敗後15分間ロック）"
    )

    # タイムスタンプ
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.now,
        server_default=func.current_timestamp(),
        comment="作成日時",
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.now,
        onupdate=datetime.now,
        server_default=func.current_timestamp(),
        server_onupdate=func.current_timestamp(),
        comment="更新日時",
    )

    # インデックス定義
    __table_args__ = (
        Index("ix_users_email", "email", unique=True),
        Index("ix_users_role", "role"),
    )

    def __repr__(self) -> str:
        """文字列表現"""
        return (
            f"<User(id={self.id}, email={self.email!r}, "
            f"name={self.name!r}, role={self.role!r})>"
        )

    def __str__(self) -> str:
        """人間が読みやすい文字列表現"""
        return f"{self.name}（{self.role}）"

    def is_locked(self) -> bool:
        """
        アカウントがロックされているかチェック

        Returns:
            bool: ロックされている場合True
        """
        if self.locked_until is None:
            return False
        return datetime.now() < self.locked_until

    def reset_failed_login(self) -> None:
        """ログイン失敗回数をリセット"""
        self.failed_login_count = 0
        self.locked_until = None

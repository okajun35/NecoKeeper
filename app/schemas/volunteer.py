"""
ボランティア（Volunteer）関連のPydanticスキーマ

ボランティア記録者のリクエスト・レスポンススキーマを定義します。
"""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class VolunteerBase(BaseModel):
    """ボランティアの基本情報スキーマ"""

    name: str = Field(..., max_length=100, description="氏名")
    contact: str | None = Field(
        None, max_length=255, description="連絡先（電話番号、メールアドレス等）"
    )
    affiliation: str | None = Field(
        None, max_length=100, description="所属（団体名等）"
    )
    status: str = Field(
        "active", max_length=20, description="活動状態（active/inactive）"
    )
    started_at: date = Field(default_factory=date.today, description="活動開始日")

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        """
        活動状態の検証

        Args:
            v: 検証する活動状態

        Returns:
            str: 検証済みの活動状態

        Raises:
            ValueError: 許可されていない活動状態の場合

        Example:
            >>> VolunteerBase(name="田中太郎", status="active")
            VolunteerBase(name='田中太郎', ...)
        """
        allowed: list[str] = ["active", "inactive"]
        if v not in allowed:
            raise ValueError(
                f"活動状態は {', '.join(allowed)} のいずれかである必要があります"
            )
        return v


class VolunteerCreate(VolunteerBase):
    """
    ボランティア登録リクエストスキーマ

    新規ボランティアを登録する際のリクエストボディ。

    Example:
        >>> volunteer_data = VolunteerCreate(
        ...     name="田中太郎", contact="090-1234-5678", affiliation="保護猫団体A"
        ... )
    """

    pass


class VolunteerUpdate(BaseModel):
    """
    ボランティア更新リクエストスキーマ（全フィールド任意）

    既存ボランティア情報を更新する際のリクエストボディ。
    すべてのフィールドが任意で、指定されたフィールドのみ更新されます。

    Example:
        >>> update_data = VolunteerUpdate(status="inactive")
    """

    name: str | None = Field(None, max_length=100)
    contact: str | None = Field(None, max_length=255)
    affiliation: str | None = Field(None, max_length=100)
    status: str | None = Field(None, max_length=20)
    started_at: date | None = None

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str | None) -> str | None:
        """
        活動状態の検証

        Args:
            v: 検証する活動状態（Noneの場合はスキップ）

        Returns:
            str | None: 検証済みの活動状態

        Raises:
            ValueError: 許可されていない活動状態の場合
        """
        if v is not None:
            allowed: list[str] = ["active", "inactive"]
            if v not in allowed:
                raise ValueError(
                    f"活動状態は {', '.join(allowed)} のいずれかである必要があります"
                )
        return v


class VolunteerResponse(VolunteerBase):
    """
    ボランティアレスポンススキーマ

    ボランティア情報のAPIレスポンス。

    Attributes:
        id: ボランティアID
        name: 氏名
        contact: 連絡先
        affiliation: 所属
        status: 活動状態
        started_at: 活動開始日
        created_at: 作成日時
        updated_at: 更新日時

    Example:
        >>> response = VolunteerResponse(
        ...     id=1,
        ...     name="田中太郎",
        ...     contact="090-1234-5678",
        ...     affiliation="保護猫団体A",
        ...     status="active",
        ...     started_at=date(2024, 1, 1),
        ...     created_at=datetime(2024, 1, 1, 10, 0, 0),
        ...     updated_at=datetime(2024, 1, 1, 10, 0, 0),
        ... )
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class VolunteerListResponse(BaseModel):
    """
    ボランティア一覧レスポンススキーマ

    ページネーション情報を含むボランティア一覧のAPIレスポンス。

    Attributes:
        items: ボランティアのリスト
        total: 総件数
        page: 現在のページ番号
        page_size: 1ページあたりの件数
        total_pages: 総ページ数

    Example:
        >>> response = VolunteerListResponse(
        ...     items=[volunteer1, volunteer2],
        ...     total=2,
        ...     page=1,
        ...     page_size=10,
        ...     total_pages=1,
        ... )
    """

    items: list[VolunteerResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

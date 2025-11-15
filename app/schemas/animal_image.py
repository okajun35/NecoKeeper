"""
猫画像ギャラリースキーマ

猫の複数画像管理のためのPydanticスキーマです。
"""

from datetime import date, datetime

from pydantic import BaseModel, Field


class AnimalImageBase(BaseModel):
    """画像ギャラリーの基本スキーマ"""

    taken_at: date | None = Field(None, description="撮影日")
    description: str | None = Field(None, max_length=500, description="説明")


class AnimalImageCreate(AnimalImageBase):
    """画像ギャラリー作成スキーマ"""

    pass


class AnimalImageUpdate(BaseModel):
    """画像ギャラリー更新スキーマ"""

    taken_at: date | None = Field(None, description="撮影日")
    description: str | None = Field(None, max_length=500, description="説明")


class AnimalImageResponse(AnimalImageBase):
    """画像ギャラリーレスポンススキーマ"""

    id: int = Field(..., description="画像ID")
    animal_id: int = Field(..., description="猫ID")
    image_path: str = Field(..., description="画像ファイルパス")
    file_size: int = Field(..., description="ファイルサイズ（bytes）")
    created_at: datetime = Field(..., description="作成日時")

    model_config = {"from_attributes": True}

    def get_file_size_mb(self) -> float:
        """
        ファイルサイズをMB単位で取得

        Returns:
            float: ファイルサイズ（MB）
        """
        return self.file_size / (1024 * 1024)


class ImageLimitsResponse(BaseModel):
    """画像制限設定レスポンススキーマ"""

    max_images_per_animal: int = Field(..., description="1猫あたりの最大画像枚数")
    max_image_size_mb: float = Field(
        ..., description="1画像あたりの最大ファイルサイズ（MB）"
    )
    current_count: int = Field(..., description="現在の画像枚数")
    remaining_count: int = Field(..., description="残り登録可能枚数")

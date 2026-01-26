"""
VaccineCategoryEnum のテスト

Issue #83: プロフィールに医療情報を追加
TDD: テスト先行で実装
"""

import pytest

from app.utils.enums import VaccineCategoryEnum


class TestVaccineCategoryEnum:
    """VaccineCategoryEnum のテストクラス"""

    def test_enum_values(self) -> None:
        """Enum値が正しく定義されていること"""
        assert VaccineCategoryEnum.VACCINE_3CORE.value == "3core"
        assert VaccineCategoryEnum.VACCINE_4CORE.value == "4core"
        assert VaccineCategoryEnum.VACCINE_5CORE.value == "5core"

    def test_enum_count(self) -> None:
        """Enumの要素数が3つであること"""
        assert len(VaccineCategoryEnum) == 3

    def test_display_name_ja(self) -> None:
        """日本語表示名が正しいこと"""
        assert VaccineCategoryEnum.VACCINE_3CORE.display_name_ja() == "3種"
        assert VaccineCategoryEnum.VACCINE_4CORE.display_name_ja() == "4種"
        assert VaccineCategoryEnum.VACCINE_5CORE.display_name_ja() == "5種"

    def test_display_name_en(self) -> None:
        """英語表示名が正しいこと"""
        assert VaccineCategoryEnum.VACCINE_3CORE.display_name_en() == "3-in-1"
        assert VaccineCategoryEnum.VACCINE_4CORE.display_name_en() == "4-in-1"
        assert VaccineCategoryEnum.VACCINE_5CORE.display_name_en() == "5-in-1"

    def test_string_conversion(self) -> None:
        """文字列として比較できること（str継承）"""
        # str(Enum) は "EnumName.MEMBER" を返すが、value比較は可能
        assert VaccineCategoryEnum.VACCINE_3CORE.value == "3core"
        assert VaccineCategoryEnum.VACCINE_3CORE == "3core"

    def test_from_value(self) -> None:
        """文字列からEnumに変換できること"""
        assert VaccineCategoryEnum("3core") == VaccineCategoryEnum.VACCINE_3CORE
        assert VaccineCategoryEnum("4core") == VaccineCategoryEnum.VACCINE_4CORE
        assert VaccineCategoryEnum("5core") == VaccineCategoryEnum.VACCINE_5CORE

    def test_invalid_value_raises_error(self) -> None:
        """無効な値でValueErrorが発生すること"""
        with pytest.raises(ValueError):
            VaccineCategoryEnum("invalid")

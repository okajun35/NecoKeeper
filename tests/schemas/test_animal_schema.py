"""
Animalスキーマの単体テスト

Pydanticスキーマのバリデーションをテストします。
"""

import pytest
from pydantic import ValidationError

from app.schemas.animal import AnimalCreate, AnimalUpdate


class TestAnimalSchemaValidation:
    """Animalスキーマのバリデーションテスト"""

    def test_microchip_number_validation_valid_15_digits(self):
        """15桁の半角数字が有効であることを確認"""
        data = {
            "name": "テスト",
            "pattern": "キジトラ",
            "tail_length": "長い",
            "age_months": 12,
            "gender": "male",
            "microchip_number": "392123456789012",
        }
        schema = AnimalCreate(**data)
        assert schema.microchip_number == "392123456789012"

    def test_microchip_number_validation_valid_10_alphanumeric(self):
        """10桁の英数字が有効であることを確認（旧規格）"""
        data = {
            "name": "テスト",
            "pattern": "キジトラ",
            "tail_length": "長い",
            "age_months": 12,
            "gender": "male",
            "microchip_number": "ABC1234567",
        }
        schema = AnimalCreate(**data)
        assert schema.microchip_number == "ABC1234567"

    def test_microchip_number_validation_none(self):
        """None（未入力）が有効であることを確認"""
        data = {
            "name": "テスト",
            "pattern": "キジトラ",
            "tail_length": "長い",
            "age_months": 12,
            "gender": "male",
            "microchip_number": None,
        }
        schema = AnimalCreate(**data)
        assert schema.microchip_number is None

    def test_microchip_number_validation_empty_string_to_none(self):
        """空文字列がNoneに変換されることを確認"""
        data = {
            "name": "テスト",
            "pattern": "キジトラ",
            "tail_length": "長い",
            "age_months": 12,
            "gender": "male",
            "microchip_number": "",
        }
        schema = AnimalCreate(**data)
        assert schema.microchip_number is None

    def test_microchip_number_validation_whitespace_to_none(self):
        """空白文字のみの文字列がNoneに変換されることを確認"""
        data = {
            "name": "テスト",
            "pattern": "キジトラ",
            "tail_length": "長い",
            "age_months": 12,
            "gender": "male",
            "microchip_number": "   ",
        }
        schema = AnimalCreate(**data)
        assert schema.microchip_number is None

    def test_microchip_number_validation_invalid_length(self):
        """無効な桁数でエラーになることを確認"""
        data = {
            "name": "テスト",
            "pattern": "キジトラ",
            "tail_length": "長い",
            "age_months": 12,
            "gender": "male",
            "microchip_number": "12345",
        }
        with pytest.raises(ValidationError) as exc_info:
            AnimalCreate(**data)
        assert "15桁の半角数字、または10桁の英数字" in str(exc_info.value)

    def test_microchip_number_validation_invalid_characters(self):
        """無効な文字でエラーになることを確認"""
        data = {
            "name": "テスト",
            "pattern": "キジトラ",
            "tail_length": "長い",
            "age_months": 12,
            "gender": "male",
            "microchip_number": "392-1234-5678-9012",  # ハイフン入り
        }
        with pytest.raises(ValidationError) as exc_info:
            AnimalCreate(**data)
        assert "15桁の半角数字、または10桁の英数字" in str(exc_info.value)

    def test_microchip_number_validation_14_digits_invalid(self):
        """14桁の数字が無効であることを確認"""
        data = {
            "name": "テスト",
            "pattern": "キジトラ",
            "tail_length": "長い",
            "age_months": 12,
            "gender": "male",
            "microchip_number": "39212345678901",  # 14桁
        }
        with pytest.raises(ValidationError) as exc_info:
            AnimalCreate(**data)
        assert "15桁の半角数字、または10桁の英数字" in str(exc_info.value)

    def test_microchip_number_validation_16_digits_invalid(self):
        """16桁の数字が無効であることを確認"""
        data = {
            "name": "テスト",
            "pattern": "キジトラ",
            "tail_length": "長い",
            "age_months": 12,
            "gender": "male",
            "microchip_number": "3921234567890123",  # 16桁
        }
        with pytest.raises(ValidationError) as exc_info:
            AnimalCreate(**data)
        assert "15桁の半角数字、または10桁の英数字" in str(exc_info.value)


class TestAnimalUpdateSchemaValidation:
    """AnimalUpdateスキーマのバリデーションテスト"""

    def test_microchip_number_update_valid_15_digits(self):
        """15桁の半角数字での更新が有効であることを確認"""
        data = {"microchip_number": "392123456789012"}
        schema = AnimalUpdate(**data)
        assert schema.microchip_number == "392123456789012"

    def test_microchip_number_update_valid_10_alphanumeric(self):
        """10桁の英数字での更新が有効であることを確認"""
        data = {"microchip_number": "ABC1234567"}
        schema = AnimalUpdate(**data)
        assert schema.microchip_number == "ABC1234567"

    def test_microchip_number_update_none(self):
        """Noneでの更新が有効であることを確認"""
        data = {"microchip_number": None}
        schema = AnimalUpdate(**data)
        assert schema.microchip_number is None

    def test_microchip_number_update_empty_string_to_none(self):
        """空文字列がNoneに変換されることを確認（更新時）"""
        data = {"microchip_number": ""}
        schema = AnimalUpdate(**data)
        assert schema.microchip_number is None

    def test_microchip_number_update_invalid(self):
        """無効な形式でエラーになることを確認（更新時）"""
        data = {"microchip_number": "invalid"}
        with pytest.raises(ValidationError) as exc_info:
            AnimalUpdate(**data)
        assert "15桁の半角数字、または10桁の英数字" in str(exc_info.value)

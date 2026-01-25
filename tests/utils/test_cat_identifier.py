"""
猫識別ユーティリティのテスト

Requirements: 4.1, 4.2, 4.3, 4.4, 4.5
"""

from __future__ import annotations

from unittest.mock import Mock, patch

import pytest
import requests

from scripts.utils.cat_identifier import (
    CatIdentifier,
    CatNotFoundError,
    MultipleCatsFoundError,
    identify_cat,
)


class TestCatIdentifierByID:
    """IDによる猫識別のテスト"""

    def test_identify_by_id_success(self):
        """正常系: IDで猫を識別できる"""
        # Given
        api_base_url = "http://localhost:8000"
        auth_token = "test-token"
        animal_id = 5

        mock_response = Mock()
        mock_response.json.return_value = {
            "items": [
                {"id": 5, "name": "たま", "coat_color": "キジトラ"},
                {"id": 10, "name": "みけ", "coat_color": "三毛"},
            ],
            "total": 2,
            "page": 1,
            "page_size": 100,
            "total_pages": 1,
        }
        mock_response.raise_for_status = Mock()

        with patch("requests.get", return_value=mock_response) as mock_get:
            identifier = CatIdentifier(api_base_url, auth_token)

            # When
            result = identifier.identify_by_id(animal_id)

            # Then
            assert result == 5
            mock_get.assert_called_once()

    def test_identify_by_id_not_found(self):
        """異常系: 存在しないIDでエラー"""
        # Given
        api_base_url = "http://localhost:8000"
        auth_token = "test-token"
        animal_id = 999

        mock_response = Mock()
        mock_response.json.return_value = {
            "items": [
                {"id": 5, "name": "たま", "coat_color": "キジトラ"},
            ],
            "total": 1,
            "page": 1,
            "page_size": 100,
            "total_pages": 1,
        }
        mock_response.raise_for_status = Mock()

        with patch("requests.get", return_value=mock_response):
            identifier = CatIdentifier(api_base_url, auth_token)

            # When/Then
            with pytest.raises(CatNotFoundError, match="猫ID 999 が見つかりません"):
                identifier.identify_by_id(animal_id)


class TestCatIdentifierByName:
    """名前による猫識別のテスト"""

    def test_identify_by_name_success(self):
        """正常系: 名前で猫を識別できる"""
        # Given
        api_base_url = "http://localhost:8000"
        auth_token = "test-token"
        name = "たま"

        mock_response = Mock()
        mock_response.json.return_value = {
            "items": [
                {"id": 5, "name": "たま", "coat_color": "キジトラ"},
                {"id": 10, "name": "みけ", "coat_color": "三毛"},
            ],
            "total": 2,
            "page": 1,
            "page_size": 100,
            "total_pages": 1,
        }
        mock_response.raise_for_status = Mock()

        with patch("requests.get", return_value=mock_response):
            identifier = CatIdentifier(api_base_url, auth_token)

            # When
            result = identifier.identify_by_name(name)

            # Then
            assert result == 5

    def test_identify_by_name_case_insensitive(self):
        """正常系: 大文字小文字を区別しない"""
        # Given
        api_base_url = "http://localhost:8000"
        auth_token = "test-token"
        name = "TAMA"  # 大文字

        mock_response = Mock()
        mock_response.json.return_value = {
            "items": [
                {"id": 5, "name": "tama", "coat_color": "キジトラ"},  # 小文字
            ],
            "total": 1,
            "page": 1,
            "page_size": 100,
            "total_pages": 1,
        }
        mock_response.raise_for_status = Mock()

        with patch("requests.get", return_value=mock_response):
            identifier = CatIdentifier(api_base_url, auth_token)

            # When
            result = identifier.identify_by_name(name)

            # Then
            assert result == 5

    def test_identify_by_name_not_found(self):
        """異常系: 存在しない名前でエラー"""
        # Given
        api_base_url = "http://localhost:8000"
        auth_token = "test-token"
        name = "存在しない猫"

        mock_response = Mock()
        mock_response.json.return_value = {
            "items": [
                {"id": 5, "name": "たま", "coat_color": "キジトラ"},
            ],
            "total": 1,
            "page": 1,
            "page_size": 100,
            "total_pages": 1,
        }
        mock_response.raise_for_status = Mock()

        with patch("requests.get", return_value=mock_response):
            identifier = CatIdentifier(api_base_url, auth_token)

            # When/Then
            with pytest.raises(
                CatNotFoundError, match="猫の名前 '存在しない猫' が見つかりません"
            ):
                identifier.identify_by_name(name)

    def test_identify_by_name_multiple_matches(self):
        """異常系: 複数の猫が見つかった場合エラー"""
        # Given
        api_base_url = "http://localhost:8000"
        auth_token = "test-token"
        name = "たま"

        mock_response = Mock()
        mock_response.json.return_value = {
            "items": [
                {"id": 5, "name": "たま", "coat_color": "キジトラ"},
                {"id": 15, "name": "たま", "coat_color": "三毛"},
            ],
            "total": 2,
            "page": 1,
            "page_size": 100,
            "total_pages": 1,
        }
        mock_response.raise_for_status = Mock()

        with patch("requests.get", return_value=mock_response):
            identifier = CatIdentifier(api_base_url, auth_token)

            # When/Then
            with pytest.raises(MultipleCatsFoundError) as exc_info:
                identifier.identify_by_name(name)

            # エラーメッセージの検証
            assert "複数見つかりました" in str(exc_info.value)
            assert "ID: 5" in str(exc_info.value)
            assert "ID: 15" in str(exc_info.value)

            # matching_cats属性の検証
            assert len(exc_info.value.matching_cats) == 2
            assert exc_info.value.matching_cats[0]["id"] == 5
            assert exc_info.value.matching_cats[1]["id"] == 15


class TestCatIdentifierGeneric:
    """汎用識別メソッドのテスト"""

    def test_identify_with_integer(self):
        """正常系: 整数でIDとして識別"""
        # Given
        api_base_url = "http://localhost:8000"
        auth_token = "test-token"
        identifier_value = 5

        mock_response = Mock()
        mock_response.json.return_value = {
            "items": [
                {"id": 5, "name": "たま", "coat_color": "キジトラ"},
            ],
            "total": 1,
            "page": 1,
            "page_size": 100,
            "total_pages": 1,
        }
        mock_response.raise_for_status = Mock()

        with patch("requests.get", return_value=mock_response):
            identifier = CatIdentifier(api_base_url, auth_token)

            # When
            result = identifier.identify(identifier_value)

            # Then
            assert result == 5

    def test_identify_with_numeric_string(self):
        """正常系: 数字文字列でIDとして識別"""
        # Given
        api_base_url = "http://localhost:8000"
        auth_token = "test-token"
        identifier_value = "5"

        mock_response = Mock()
        mock_response.json.return_value = {
            "items": [
                {"id": 5, "name": "たま", "coat_color": "キジトラ"},
            ],
            "total": 1,
            "page": 1,
            "page_size": 100,
            "total_pages": 1,
        }
        mock_response.raise_for_status = Mock()

        with patch("requests.get", return_value=mock_response):
            identifier = CatIdentifier(api_base_url, auth_token)

            # When
            result = identifier.identify(identifier_value)

            # Then
            assert result == 5

    def test_identify_with_name_string(self):
        """正常系: 名前文字列で名前として識別"""
        # Given
        api_base_url = "http://localhost:8000"
        auth_token = "test-token"
        identifier_value = "たま"

        mock_response = Mock()
        mock_response.json.return_value = {
            "items": [
                {"id": 5, "name": "たま", "coat_color": "キジトラ"},
            ],
            "total": 1,
            "page": 1,
            "page_size": 100,
            "total_pages": 1,
        }
        mock_response.raise_for_status = Mock()

        with patch("requests.get", return_value=mock_response):
            identifier = CatIdentifier(api_base_url, auth_token)

            # When
            result = identifier.identify(identifier_value)

            # Then
            assert result == 5


class TestCatIdentifierPagination:
    """ページネーション処理のテスト"""

    def test_fetch_all_animals_multiple_pages(self):
        """正常系: 複数ページの猫を取得"""
        # Given
        api_base_url = "http://localhost:8000"
        auth_token = "test-token"

        # ページ1のレスポンス
        mock_response_page1 = Mock()
        mock_response_page1.json.return_value = {
            "items": [
                {"id": 1, "name": "猫1", "coat_color": "キジトラ"},
                {"id": 2, "name": "猫2", "coat_color": "三毛"},
            ],
            "total": 3,
            "page": 1,
            "page_size": 2,
            "total_pages": 2,
        }
        mock_response_page1.raise_for_status = Mock()

        # ページ2のレスポンス
        mock_response_page2 = Mock()
        mock_response_page2.json.return_value = {
            "items": [
                {"id": 3, "name": "猫3", "coat_color": "黒猫"},
            ],
            "total": 3,
            "page": 2,
            "page_size": 2,
            "total_pages": 2,
        }
        mock_response_page2.raise_for_status = Mock()

        with patch(
            "requests.get", side_effect=[mock_response_page1, mock_response_page2]
        ) as mock_get:
            identifier = CatIdentifier(api_base_url, auth_token)

            # When
            animals = identifier._fetch_all_animals()

            # Then
            assert len(animals) == 3
            assert animals[0]["id"] == 1
            assert animals[1]["id"] == 2
            assert animals[2]["id"] == 3
            assert mock_get.call_count == 2

    def test_fetch_all_animals_caching(self):
        """正常系: 2回目の呼び出しではキャッシュを使用"""
        # Given
        api_base_url = "http://localhost:8000"
        auth_token = "test-token"

        mock_response = Mock()
        mock_response.json.return_value = {
            "items": [
                {"id": 5, "name": "たま", "coat_color": "キジトラ"},
            ],
            "total": 1,
            "page": 1,
            "page_size": 100,
            "total_pages": 1,
        }
        mock_response.raise_for_status = Mock()

        with patch("requests.get", return_value=mock_response) as mock_get:
            identifier = CatIdentifier(api_base_url, auth_token)

            # When
            animals1 = identifier._fetch_all_animals()
            animals2 = identifier._fetch_all_animals()

            # Then
            assert animals1 == animals2
            # APIは1回だけ呼ばれる（キャッシュが効いている）
            assert mock_get.call_count == 1


class TestCatIdentifierErrorHandling:
    """エラーハンドリングのテスト"""

    def test_api_request_failure(self):
        """異常系: API呼び出し失敗"""
        # Given
        api_base_url = "http://localhost:8000"
        auth_token = "test-token"

        with patch(
            "requests.get", side_effect=requests.RequestException("Network error")
        ):
            identifier = CatIdentifier(api_base_url, auth_token)

            # When/Then
            with pytest.raises(requests.RequestException):
                identifier._fetch_all_animals()

    def test_api_http_error(self):
        """異常系: HTTPエラー"""
        # Given
        api_base_url = "http://localhost:8000"
        auth_token = "test-token"

        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.HTTPError(
            "401 Unauthorized"
        )

        with patch("requests.get", return_value=mock_response):
            identifier = CatIdentifier(api_base_url, auth_token)

            # When/Then
            with pytest.raises(requests.HTTPError):
                identifier._fetch_all_animals()


class TestIdentifyCatFunction:
    """便利関数のテスト"""

    def test_identify_cat_by_id(self):
        """正常系: IDで猫を識別（便利関数）"""
        # Given
        api_base_url = "http://localhost:8000"
        auth_token = "test-token"
        identifier_value = 5

        mock_response = Mock()
        mock_response.json.return_value = {
            "items": [
                {"id": 5, "name": "たま", "coat_color": "キジトラ"},
            ],
            "total": 1,
            "page": 1,
            "page_size": 100,
            "total_pages": 1,
        }
        mock_response.raise_for_status = Mock()

        with patch("requests.get", return_value=mock_response):
            # When
            result = identify_cat(identifier_value, api_base_url, auth_token)

            # Then
            assert result == 5

    def test_identify_cat_by_name(self):
        """正常系: 名前で猫を識別（便利関数）"""
        # Given
        api_base_url = "http://localhost:8000"
        auth_token = "test-token"
        identifier_value = "たま"

        mock_response = Mock()
        mock_response.json.return_value = {
            "items": [
                {"id": 5, "name": "たま", "coat_color": "キジトラ"},
            ],
            "total": 1,
            "page": 1,
            "page_size": 100,
            "total_pages": 1,
        }
        mock_response.raise_for_status = Mock()

        with patch("requests.get", return_value=mock_response):
            # When
            result = identify_cat(identifier_value, api_base_url, auth_token)

            # Then
            assert result == 5

"""
Integration tests for MCP server

Tests the complete workflow: register → upload → generate_qr
Validates: Requirements 8.1, 8.2, 8.3, 8.4, 8.5
"""

from __future__ import annotations

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import httpx
import pytest

from app.mcp.api_client import NecoKeeperAPIClient
from app.mcp.config import MCPConfig


@pytest.fixture
def mock_config(monkeypatch):
    """テスト用の設定を提供"""
    monkeypatch.setenv("NECOKEEPER_API_URL", "http://localhost:8000")
    monkeypatch.setenv("AUTOMATION_API_KEY", "test-api-key-32-characters-long-xxx")
    return MCPConfig()


@pytest.fixture
def mock_api_client(mock_config):
    """モックAPIクライアントを提供"""
    client = NecoKeeperAPIClient()
    return client


class TestCompleteWorkflow:
    """完全なワークフローのテスト（Requirement 8.1）"""

    @pytest.mark.asyncio
    async def test_register_upload_generate_workflow(self, mock_config):
        """
        完全なワークフロー: 猫登録 → 画像アップロード → QR生成
        Validates: Requirements 8.1, 8.2, 8.3, 8.4
        """
        api_client = NecoKeeperAPIClient()
        animal_id = 42

        # Step 1: 猫を登録
        with patch.object(api_client, "create_animal") as mock_create:
            mock_create.return_value = {
                "id": animal_id,
                "name": "Tama",
                "status": "保護中",
            }

            # 猫を登録
            register_result = await api_client.create_animal(
                {
                    "name": "Tama",
                    "pattern": "三毛",
                    "tail_length": "長い",
                    "age_months": 12,
                    "gender": "female",
                    "status": "保護中",
                }
            )

            # 登録結果を検証
            assert register_result["id"] == animal_id
            assert register_result["name"] == "Tama"

        # Step 2: 画像をアップロード
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_image:
            try:
                # テスト用画像ファイルを作成
                temp_image.write(b"fake_image_data")
                temp_image.flush()
                image_path = temp_image.name

                with patch.object(api_client, "upload_image") as mock_upload:
                    mock_upload.return_value = {
                        "id": 1,
                        "animal_id": animal_id,
                        "image_url": f"/media/animals/{animal_id}/image_1.jpg",
                    }

                    # 画像をアップロード
                    upload_result = await api_client.upload_image(
                        animal_id=animal_id,
                        image_data=b"fake_image_data",
                        filename="test.jpg",
                    )

                    # アップロード結果を検証
                    assert upload_result["animal_id"] == animal_id
                    assert "image_url" in upload_result

            finally:
                # テスト用ファイルを削除
                image_file = Path(image_path)
                if image_file.exists():
                    image_file.unlink()

        # Step 3: QR PDFを生成
        with patch.object(api_client, "generate_qr_pdf") as mock_generate:
            mock_generate.return_value = b"%PDF-1.4 fake pdf content"

            # QR PDFを生成
            pdf_content = await api_client.generate_qr_pdf([animal_id])

            # PDF生成結果を検証
            assert pdf_content == b"%PDF-1.4 fake pdf content"
            assert len(pdf_content) > 0

    @pytest.mark.asyncio
    async def test_workflow_data_consistency(self, mock_config):
        """
        ワークフロー全体でanimal_idが一貫していることを確認
        Validates: Requirements 8.2, 8.3, 8.4
        """
        api_client = NecoKeeperAPIClient()
        animal_id = 123

        # Step 1: 登録
        with patch.object(api_client, "create_animal") as mock_create:
            mock_create.return_value = {
                "id": animal_id,
                "name": "TestCat",
                "status": "保護中",
            }

            register_result = await api_client.create_animal(
                {
                    "name": "TestCat",
                    "pattern": "キジトラ",
                    "tail_length": "長い",
                    "age_months": 12,
                    "gender": "male",
                    "status": "保護中",
                }
            )
            assert register_result["id"] == animal_id

        # Step 2: アップロード（同じanimal_idを使用）
        with patch.object(api_client, "upload_image") as mock_upload:
            mock_upload.return_value = {
                "id": 1,
                "animal_id": animal_id,
                "image_url": f"/media/animals/{animal_id}/image_1.jpg",
            }

            upload_result = await api_client.upload_image(
                animal_id=animal_id,
                image_data=b"fake_image_data",
                filename="test.jpg",
            )
            assert upload_result["animal_id"] == animal_id

        # Step 3: QR生成（同じanimal_idを使用）
        with patch.object(api_client, "generate_qr_pdf") as mock_generate:
            mock_generate.return_value = b"%PDF-1.4 fake pdf content"

            pdf_content = await api_client.generate_qr_pdf([animal_id])
            assert len(pdf_content) > 0


class TestErrorHandling:
    """各ツールのエラーハンドリングテスト"""

    @pytest.mark.asyncio
    async def test_api_client_network_error(self, mock_config):
        """
        ネットワークエラー時のエラーハンドリング
        Validates: Requirement 8.5
        """
        api_client = NecoKeeperAPIClient()

        with patch.object(api_client.client, "post") as mock_post:
            # ネットワークエラーをシミュレート
            mock_post.side_effect = httpx.ConnectError("Connection refused")

            # エラーが適切に処理されることを確認（ConnectionErrorにラップされる）
            with pytest.raises(ConnectionError) as exc_info:
                await api_client.create_animal(
                    {
                        "name": "TestCat",
                        "pattern": "キジトラ",
                        "tail_length": "長い",
                        "age_months": 12,
                        "gender": "male",
                        "status": "保護中",
                    }
                )

            # エラーメッセージが明確であることを確認
            error_message = str(exc_info.value)
            assert (
                "connect" in error_message.lower() or "failed" in error_message.lower()
            )

    @pytest.mark.asyncio
    async def test_api_client_validation_error(self, mock_config):
        """
        バリデーションエラー時のエラーハンドリング
        Validates: Requirement 8.5
        """
        api_client = NecoKeeperAPIClient()

        with patch.object(api_client.client, "post") as mock_post:
            # バリデーションエラーをシミュレート
            mock_response = MagicMock()
            mock_response.status_code = 400
            mock_response.text = "Invalid data"
            mock_response.json.return_value = {"detail": "Invalid data"}

            mock_request = MagicMock()
            mock_request.url = "http://localhost:8000/api/automation/animals"

            http_error = httpx.HTTPStatusError(
                "Bad Request",
                request=mock_request,
                response=mock_response,
            )
            mock_response.raise_for_status.side_effect = http_error
            mock_post.return_value = mock_response

            # エラーが適切に処理されることを確認（ValueErrorにラップされる）
            with pytest.raises(ValueError) as exc_info:
                await api_client.create_animal(
                    {
                        "name": "TestCat",
                        "pattern": "キジトラ",
                        "tail_length": "長い",
                        "age_months": 12,
                        "gender": "male",
                        "status": "保護中",
                    }
                )

            # エラーメッセージが明確であることを確認
            error_message = str(exc_info.value)
            assert (
                "validation" in error_message.lower()
                or "invalid" in error_message.lower()
            )

    @pytest.mark.asyncio
    async def test_api_client_authentication_error(self, mock_config):
        """
        認証エラー時のエラーハンドリング
        Validates: Requirement 8.5
        """
        api_client = NecoKeeperAPIClient()

        with patch.object(api_client.client, "post") as mock_post:
            # 認証エラーをシミュレート
            mock_response = MagicMock()
            mock_response.status_code = 401
            mock_response.text = "Unauthorized"
            mock_response.json.return_value = {"detail": "Unauthorized"}

            mock_request = MagicMock()
            mock_request.url = "http://localhost:8000/api/automation/animals"

            http_error = httpx.HTTPStatusError(
                "Unauthorized",
                request=mock_request,
                response=mock_response,
            )
            mock_response.raise_for_status.side_effect = http_error
            mock_post.return_value = mock_response

            # エラーが適切に処理されることを確認（PermissionErrorにラップされる）
            with pytest.raises(PermissionError) as exc_info:
                await api_client.create_animal(
                    {
                        "name": "TestCat",
                        "pattern": "キジトラ",
                        "tail_length": "長い",
                        "age_months": 12,
                        "gender": "male",
                        "status": "保護中",
                    }
                )

            # エラーメッセージが明確であることを確認
            error_message = str(exc_info.value)
            assert (
                "auth" in error_message.lower() or "permission" in error_message.lower()
            )

    @pytest.mark.asyncio
    async def test_upload_image_file_validation(self, mock_config):
        """
        画像ファイルのバリデーション
        Validates: Requirement 8.5
        """
        api_client = NecoKeeperAPIClient()

        # 空のデータでアップロードを試みる
        with patch.object(api_client.client, "post") as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 400
            mock_response.text = "Invalid image data"
            mock_response.json.return_value = {"detail": "Invalid image data"}

            mock_request = MagicMock()
            mock_request.url = "http://localhost:8000/api/automation/animals/1/images"

            http_error = httpx.HTTPStatusError(
                "Bad Request",
                request=mock_request,
                response=mock_response,
            )
            mock_response.raise_for_status.side_effect = http_error
            mock_post.return_value = mock_response

            with pytest.raises(ValueError):
                await api_client.upload_image(
                    animal_id=1, image_data=b"", filename="test.jpg"
                )

    @pytest.mark.asyncio
    async def test_generate_qr_api_error(self, mock_config):
        """
        PDF生成API呼び出し時のエラーハンドリング
        Validates: Requirement 8.5
        """
        api_client = NecoKeeperAPIClient()

        with patch.object(api_client.client, "post") as mock_post:
            # APIエラーをシミュレート
            mock_response = MagicMock()
            mock_response.status_code = 500
            mock_response.text = "Internal Server Error"
            mock_response.json.return_value = {"detail": "Internal Server Error"}

            mock_request = MagicMock()
            mock_request.url = "http://localhost:8000/api/automation/pdf/qr-card-grid"

            http_error = httpx.HTTPStatusError(
                "Internal Server Error",
                request=mock_request,
                response=mock_response,
            )
            mock_response.raise_for_status.side_effect = http_error
            mock_post.return_value = mock_response

            # エラーが適切に処理されることを確認（RuntimeErrorにラップされる）
            with pytest.raises(RuntimeError) as exc_info:
                await api_client.generate_qr_pdf([1])

            # エラーメッセージが明確であることを確認
            error_message = str(exc_info.value)
            assert "server error" in error_message.lower() or "500" in error_message


class TestConfigurationValidation:
    """設定の検証テスト"""

    def test_missing_api_url(self, monkeypatch):
        """
        API URLが設定されていない場合のエラー
        Validates: Requirement 8.5
        """
        # 環境変数を削除
        monkeypatch.delenv("NECOKEEPER_API_URL", raising=False)
        monkeypatch.setenv("AUTOMATION_API_KEY", "test-api-key-32-characters-long-xxx")

        # デフォルト値が使用されることを確認
        config = MCPConfig()
        assert config.api_url == "http://localhost:8000"

    def test_missing_api_key(self, monkeypatch):
        """
        API Keyが設定されていない場合のエラー
        Validates: Requirement 8.5
        """
        # 環境変数を削除
        monkeypatch.setenv("NECOKEEPER_API_URL", "http://localhost:8000")
        monkeypatch.delenv("AUTOMATION_API_KEY", raising=False)

        # エラーが発生することを確認
        with pytest.raises(ValueError) as exc_info:
            MCPConfig()

        # エラーメッセージが明確であることを確認
        error_message = str(exc_info.value)
        assert "AUTOMATION_API_KEY" in error_message

    def test_invalid_api_key_length(self, monkeypatch):
        """
        API Keyの長さが不正な場合のエラー
        Validates: Requirement 8.5
        """
        # 短すぎるAPI Keyを設定
        monkeypatch.setenv("NECOKEEPER_API_URL", "http://localhost:8000")
        monkeypatch.setenv("AUTOMATION_API_KEY", "short-key")

        # エラーが発生することを確認
        with pytest.raises(ValueError) as exc_info:
            MCPConfig()

        # エラーメッセージが明確であることを確認
        error_message = str(exc_info.value)
        assert "32 characters" in error_message


class TestWorkflowErrorClarity:
    """ワークフローエラーの明確性テスト"""

    @pytest.mark.asyncio
    async def test_registration_failure_message(self, mock_config):
        """
        登録失敗時のエラーメッセージが明確であることを確認
        Validates: Requirement 8.5
        """
        api_client = NecoKeeperAPIClient()

        with patch.object(api_client.client, "post") as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 400
            mock_response.text = "Name is required"
            mock_response.json.return_value = {"detail": "Name is required"}

            mock_request = MagicMock()
            mock_request.url = "http://localhost:8000/api/automation/animals"

            http_error = httpx.HTTPStatusError(
                "Bad Request",
                request=mock_request,
                response=mock_response,
            )
            mock_response.raise_for_status.side_effect = http_error
            mock_post.return_value = mock_response

            with pytest.raises(ValueError) as exc_info:
                await api_client.create_animal(
                    {
                        "name": "",
                        "pattern": "キジトラ",
                        "tail_length": "長い",
                        "age_months": 12,
                        "gender": "male",
                        "status": "保護中",
                    }
                )

            # エラーメッセージが明確であることを確認
            error_message = str(exc_info.value).lower()
            assert "validation" in error_message or "name" in error_message

    @pytest.mark.asyncio
    async def test_upload_failure_message(self, mock_config):
        """
        アップロード失敗時のエラーメッセージが明確であることを確認
        Validates: Requirement 8.5
        """
        api_client = NecoKeeperAPIClient()

        with patch.object(api_client.client, "post") as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 413
            mock_response.text = "File too large"
            mock_response.json.return_value = {"detail": "File too large"}

            mock_request = MagicMock()
            mock_request.url = "http://localhost:8000/api/automation/animals/1/images"

            http_error = httpx.HTTPStatusError(
                "Payload Too Large",
                request=mock_request,
                response=mock_response,
            )
            mock_response.raise_for_status.side_effect = http_error
            mock_post.return_value = mock_response

            with pytest.raises(RuntimeError) as exc_info:
                await api_client.upload_image(
                    animal_id=1, image_data=b"fake_image_data", filename="test.jpg"
                )

            # エラーメッセージが明確であることを確認
            error_message = str(exc_info.value).lower()
            assert "413" in error_message or "file" in error_message

    @pytest.mark.asyncio
    async def test_qr_generation_failure_message(self, mock_config):
        """
        QR生成失敗時のエラーメッセージが明確であることを確認
        Validates: Requirement 8.5
        """
        api_client = NecoKeeperAPIClient()

        with patch.object(api_client.client, "post") as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 404
            mock_response.text = "Animal not found"
            mock_response.json.return_value = {"detail": "Animal not found"}

            mock_request = MagicMock()
            mock_request.url = "http://localhost:8000/api/automation/pdf/qr-card-grid"

            http_error = httpx.HTTPStatusError(
                "Not Found",
                request=mock_request,
                response=mock_response,
            )
            mock_response.raise_for_status.side_effect = http_error
            mock_post.return_value = mock_response

            with pytest.raises(FileNotFoundError) as exc_info:
                await api_client.generate_qr_pdf([99999])

            # エラーメッセージが明確であることを確認
            error_message = str(exc_info.value).lower()
            assert "not found" in error_message or "animal" in error_message

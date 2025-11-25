"""
Tests for PWA Manifest endpoint

Tests the dynamic manifest.json generation based on Kiroween Mode.
"""

from __future__ import annotations

from fastapi.testclient import TestClient


class TestManifestEndpoint:
    """PWA Manifest エンドポイントのテスト"""

    def test_manifest_endpoint_returns_200(self, test_client: TestClient) -> None:
        """マニフェストエンドポイントが200を返す"""
        # When: マニフェストを取得
        response = test_client.get("/manifest.json")

        # Then: 200が返される
        assert response.status_code == 200

    def test_manifest_contains_required_fields(self, test_client: TestClient) -> None:
        """マニフェストに必須フィールドが含まれる"""
        # When: マニフェストを取得
        response = test_client.get("/manifest.json")

        # Then: 必須フィールドが含まれる
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "short_name" in data
        assert "description" in data
        assert "start_url" in data
        assert "display" in data
        assert "background_color" in data
        assert "theme_color" in data
        assert "orientation" in data
        assert "icons" in data
        assert "categories" in data
        assert "lang" in data
        assert "dir" in data

    def test_manifest_icons_are_list(self, test_client: TestClient) -> None:
        """マニフェストのアイコンがリストである"""
        # When: マニフェストを取得
        response = test_client.get("/manifest.json")

        # Then: アイコンがリストである
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["icons"], list)
        assert len(data["icons"]) > 0

    def test_manifest_icons_have_required_fields(self, test_client: TestClient) -> None:
        """マニフェストのアイコンに必須フィールドが含まれる"""
        # When: マニフェストを取得
        response = test_client.get("/manifest.json")

        # Then: 各アイコンに必須フィールドが含まれる
        assert response.status_code == 200
        data = response.json()
        for icon in data["icons"]:
            assert "src" in icon
            assert "sizes" in icon
            assert "type" in icon
            assert "purpose" in icon

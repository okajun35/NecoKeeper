"""
世話記録ページのテスト

Context7参照: `/pytest-dev/pytest` (Trust Score: 9.5)
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client() -> TestClient:
    """テスト用クライアント"""
    return TestClient(app)


class TestCareLogsPages:
    """世話記録ページのテスト"""

    def test_care_logs_list_page(self, client: TestClient) -> None:
        """世話記録一覧ページが表示される"""
        response = client.get("/admin/care-logs")
        assert response.status_code == 200
        assert "世話記録一覧" in response.text
        assert "data-i18n" in response.text  # 多言語化属性が存在

    def test_care_logs_new_page(self, client: TestClient) -> None:
        """世話記録新規登録ページが表示される"""
        response = client.get("/admin/care-logs/new")
        assert response.status_code == 200
        assert "新しい記録を追加" in response.text
        assert "care-log-form" in response.text  # フォームが存在

    def test_care_logs_detail_page(self, client: TestClient) -> None:
        """世話記録詳細ページが表示される"""
        response = client.get("/admin/care-logs/1")
        assert response.status_code == 200
        assert "世話記録詳細" in response.text

    def test_care_logs_new_page_has_form_fields(self, client: TestClient) -> None:
        """世話記録新規登録ページにフォームフィールドが存在する"""
        response = client.get("/admin/care-logs/new")
        assert response.status_code == 200

        # フォームフィールドの確認
        assert 'id="animal_id"' in response.text
        assert 'id="log_date"' in response.text
        assert 'id="time_slot"' in response.text
        assert 'id="appetite"' in response.text
        assert 'id="energy"' in response.text
        assert 'id="urination"' in response.text
        assert 'id="cleaning"' in response.text
        assert 'id="memo"' in response.text

    def test_care_logs_new_page_has_i18n_attributes(self, client: TestClient) -> None:
        """世話記録新規登録ページに多言語化属性が存在する"""
        response = client.get("/admin/care-logs/new")
        assert response.status_code == 200

        # 多言語化属性の確認
        assert 'data-i18n="add_new"' in response.text
        assert 'data-i18n-ns="care_logs"' in response.text
        assert 'data-i18n="back"' in response.text
        assert 'data-i18n-ns="common"' in response.text

    def test_care_logs_new_page_routing_order(self, client: TestClient) -> None:
        """
        /admin/care-logs/newが/admin/care-logs/{id}より前にルーティングされる

        "new"が整数として解析されないことを確認
        """
        # /admin/care-logs/newにアクセス
        response = client.get("/admin/care-logs/new")
        assert response.status_code == 200
        assert "新しい記録を追加" in response.text

        # /admin/care-logs/1にアクセス（詳細ページ）
        response = client.get("/admin/care-logs/1")
        assert response.status_code == 200
        assert "世話記録詳細" in response.text

    def test_care_logs_list_page_has_i18n_attributes(self, client: TestClient) -> None:
        """世話記録一覧ページに多言語化属性が存在する"""
        response = client.get("/admin/care-logs")
        assert response.status_code == 200

        # 多言語化属性の確認
        assert 'data-i18n="list_title"' in response.text
        assert 'data-i18n-ns="care_logs"' in response.text
        assert 'data-i18n="description"' in response.text
        assert 'data-i18n="export_csv"' in response.text

    def test_care_logs_detail_page_has_i18n_attributes(
        self, client: TestClient
    ) -> None:
        """世話記録詳細ページに多言語化属性が存在する"""
        response = client.get("/admin/care-logs/1")
        assert response.status_code == 200

        # 多言語化属性の確認
        assert 'data-i18n="detail_title"' in response.text
        assert 'data-i18n-ns="care_logs"' in response.text

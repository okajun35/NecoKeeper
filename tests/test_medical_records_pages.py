"""
診療記録ページのテスト

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


class TestMedicalRecordsPages:
    """診療記録ページのテスト"""

    def test_medical_records_list_page(self, client: TestClient) -> None:
        """診療記録一覧ページが表示される"""
        response = client.get("/admin/medical-records")
        assert response.status_code == 200
        assert "診療記録一覧" in response.text
        assert "data-i18n" in response.text  # 多言語化属性が存在

    def test_medical_records_new_page(self, client: TestClient) -> None:
        """診療記録新規登録ページが表示される"""
        response = client.get("/admin/medical-records/new")
        assert response.status_code == 200
        assert (
            "新しい診療記録を追加" in response.text
            or 'data-i18n="add_new"' in response.text
        )

    def test_medical_records_detail_page(self, client: TestClient) -> None:
        """診療記録詳細ページが表示される"""
        response = client.get("/admin/medical-records/1")
        assert response.status_code == 200
        assert "診療記録詳細" in response.text

    def test_medical_records_edit_page(self, client: TestClient) -> None:
        """診療記録編集ページが表示される"""
        response = client.get("/admin/medical-records/1/edit")
        assert response.status_code == 200
        assert "診療記録を編集" in response.text

    def test_medical_records_list_page_has_i18n_attributes(
        self, client: TestClient
    ) -> None:
        """診療記録一覧ページに多言語化属性が存在する"""
        response = client.get("/admin/medical-records")
        assert response.status_code == 200

        # 多言語化属性の確認
        assert 'data-i18n="list_title"' in response.text
        assert 'data-i18n-ns="medical_records"' in response.text
        assert 'data-i18n="description"' in response.text
        assert 'data-i18n="fields.animal"' in response.text
        assert 'data-i18n="fields.vet"' in response.text

    def test_medical_records_new_page_has_i18n_attributes(
        self, client: TestClient
    ) -> None:
        """診療記録新規登録ページに多言語化属性が存在する"""
        response = client.get("/admin/medical-records/new")
        assert response.status_code == 200

        # 多言語化属性の確認
        assert 'data-i18n="add_new"' in response.text
        assert 'data-i18n-ns="medical_records"' in response.text

    def test_medical_records_detail_page_has_i18n_attributes(
        self, client: TestClient
    ) -> None:
        """診療記録詳細ページに多言語化属性が存在する"""
        response = client.get("/admin/medical-records/1")
        assert response.status_code == 200

        # 多言語化属性の確認
        assert 'data-i18n="detail_title"' in response.text
        assert 'data-i18n-ns="medical_records"' in response.text

    def test_medical_records_edit_page_has_i18n_attributes(
        self, client: TestClient
    ) -> None:
        """診療記録編集ページに多言語化属性が存在する"""
        response = client.get("/admin/medical-records/1/edit")
        assert response.status_code == 200

        # 多言語化属性の確認
        assert 'data-i18n="edit"' in response.text
        assert 'data-i18n-ns="medical_records"' in response.text

    def test_medical_records_list_page_has_filter_labels(
        self, client: TestClient
    ) -> None:
        """診療記録一覧ページにフィルターラベルが存在する"""
        response = client.get("/admin/medical-records")
        assert response.status_code == 200

        # フィルターラベルの確認
        assert 'data-i18n="fields.animal"' in response.text
        assert 'data-i18n="fields.vet"' in response.text
        assert 'data-i18n="filter.start_date"' in response.text
        assert 'data-i18n="filter.end_date"' in response.text

    def test_medical_records_list_page_has_table_headers(
        self, client: TestClient
    ) -> None:
        """診療記録一覧ページにテーブルヘッダーが存在する"""
        response = client.get("/admin/medical-records")
        assert response.status_code == 200

        # テーブルヘッダーの確認（i18next名前空間形式）
        assert 'data-i18n="date" data-i18n-ns="common"' in response.text
        assert 'data-i18n="fields.weight"' in response.text
        assert 'data-i18n="fields.temperature"' in response.text
        assert 'data-i18n="fields.symptoms"' in response.text
        assert 'data-i18n="fields.medical_action"' in response.text
        assert 'data-i18n="fields.selling_price"' in response.text

    def test_medical_records_new_page_has_form_labels(self, client: TestClient) -> None:
        """診療記録新規登録ページにフォームラベルが存在する"""
        response = client.get("/admin/medical-records/new")
        assert response.status_code == 200

        # フォームラベルの確認
        assert 'data-i18n="basic_info"' in response.text
        assert 'data-i18n="measurements"' in response.text
        assert 'data-i18n="symptoms_findings"' in response.text
        assert 'data-i18n="treatment_optional"' in response.text

    def test_medical_records_new_page_has_field_labels(
        self, client: TestClient
    ) -> None:
        """診療記録新規登録ページにフィールドラベルが存在する"""
        response = client.get("/admin/medical-records/new")
        assert response.status_code == 200

        # フィールドラベルの確認
        assert 'data-i18n="labels.animal"' in response.text
        assert 'data-i18n="labels.vet"' in response.text
        assert 'data-i18n="labels.date"' in response.text
        assert 'data-i18n="labels.time_slot"' in response.text
        assert 'data-i18n="labels.weight"' in response.text
        assert 'data-i18n="labels.temperature"' in response.text
        assert 'data-i18n="labels.symptoms"' in response.text
        assert 'data-i18n="labels.medical_action"' in response.text
        assert 'data-i18n="labels.dosage"' in response.text
        assert 'data-i18n="labels.other"' in response.text
        assert 'data-i18n="labels.comment"' in response.text

    def test_medical_records_new_page_has_placeholders(
        self, client: TestClient
    ) -> None:
        """診療記録新規登録ページにプレースホルダーが存在する"""
        response = client.get("/admin/medical-records/new")
        assert response.status_code == 200

        # プレースホルダーの確認（option要素またはinput要素）
        assert 'data-i18n="placeholders.select"' in response.text
        assert 'data-i18n-placeholder="placeholders.weight"' in response.text
        assert 'data-i18n-placeholder="placeholders.temperature"' in response.text
        assert 'data-i18n-placeholder="placeholders.symptoms"' in response.text
        assert 'data-i18n-placeholder="placeholders.dosage"' in response.text
        assert 'data-i18n-placeholder="placeholders.other"' in response.text
        assert 'data-i18n-placeholder="placeholders.comment"' in response.text

    def test_medical_records_new_page_has_time_slots(self, client: TestClient) -> None:
        """診療記録新規登録ページに時間帯オプションが存在する"""
        response = client.get("/admin/medical-records/new")
        assert response.status_code == 200

        # 時間帯オプションの確認
        assert 'data-i18n="time_slots.morning"' in response.text
        assert 'data-i18n="time_slots.afternoon"' in response.text
        assert 'data-i18n="time_slots.evening"' in response.text

    def test_medical_records_new_page_has_buttons(self, client: TestClient) -> None:
        """診療記録新規登録ページにボタンが存在する"""
        response = client.get("/admin/medical-records/new")
        assert response.status_code == 200

        # ボタンの確認
        assert 'data-i18n="buttons.submit"' in response.text
        assert 'data-i18n="buttons.cancel"' in response.text
        assert 'data-i18n-ns="medical_records"' in response.text

    def test_medical_records_new_page_has_hints(self, client: TestClient) -> None:
        """診療記録新規登録ページにヒントが存在する"""
        response = client.get("/admin/medical-records/new")
        assert response.status_code == 200

        # ヒントの確認
        assert 'data-i18n="hints.temperature_range"' in response.text

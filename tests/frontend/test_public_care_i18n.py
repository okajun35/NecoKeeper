"""
Public Careページの多言語化機能のテスト

多言語化(i18n)機能が正しく実装されているかを検証します。
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models.animal import Animal


def is_kiroween_mode_html(html: str) -> bool:
    """HTML出力からKiroweenテーマかどうかを判定"""
    return "kiroween-mode" in html or "NECRO-TERMINAL" in html


@pytest.fixture
def client() -> TestClient:
    """テスト用クライアント"""
    return TestClient(app)


class TestPublicCareI18n:
    """Public Careページの多言語化テスト"""

    def test_care_form_page_has_i18n_library(
        self, test_client: TestClient, test_animal: Animal
    ) -> None:
        """世話記録フォームページにi18nextライブラリが読み込まれている"""
        response = test_client.get(
            f"/public/care?animal_id={test_animal.id}",
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert "i18next" in response.text
        assert "/static/js/i18n.js" in response.text

    def test_care_form_page_has_i18n_attributes(
        self, test_client: TestClient, test_animal: Animal
    ) -> None:
        """世話記録フォームページにdata-i18n属性が存在する"""
        response = test_client.get(
            f"/public/care?animal_id={test_animal.id}",
            follow_redirects=True,
        )
        assert response.status_code == 200
        html = response.text

        # data-i18n属性とdata-i18n-ns属性の確認
        assert 'data-i18n="title"' in html or 'data-i18n-title="title"' in html
        assert 'data-i18n-ns="care"' in html
        assert 'data-i18n="instruction"' in html
        assert 'data-i18n="log_date"' in html
        assert 'data-i18n="time_slot"' in html
        assert 'data-i18n="appetite"' in html
        assert 'data-i18n="energy"' in html
        assert 'data-i18n="urination"' in html
        assert 'data-i18n="cleaning"' in html
        assert 'data-i18n="notes"' in html
        assert 'data-i18n="recorder"' in html

    def test_care_form_page_has_language_switcher(
        self, test_client: TestClient, test_animal: Animal
    ) -> None:
        """世話記録フォームページに言語切り替えボタンが存在する"""
        response = test_client.get(
            f"/public/care?animal_id={test_animal.id}",
            follow_redirects=True,
        )
        assert response.status_code == 200
        html = response.text

        # 言語切り替えボタンの確認（Kiroween Modeは英語固定のため非表示）
        if is_kiroween_mode_html(html):
            assert 'id="language-switcher"' not in html
        else:
            assert 'id="language-switcher"' in html
            assert 'class="language-text"' in html

    def test_care_form_page_has_button_translations(
        self, test_client: TestClient, test_animal: Animal
    ) -> None:
        """世話記録フォームページのボタンにdata-i18n属性が存在する"""
        response = test_client.get(
            f"/public/care?animal_id={test_animal.id}",
            follow_redirects=True,
        )
        assert response.status_code == 200
        html = response.text

        # ボタンの翻訳属性の確認
        assert 'data-i18n="time_slot_morning"' in html
        assert 'data-i18n="time_slot_noon"' in html
        assert 'data-i18n="time_slot_evening"' in html
        assert 'data-i18n="urination_yes"' in html
        assert 'data-i18n="urination_no"' in html
        assert 'data-i18n="cleaning_done"' in html
        assert 'data-i18n="cleaning_not_done"' in html
        assert 'data-i18n="copy_last"' in html
        assert 'data-i18n="save"' in html
        assert 'data-i18n="view_logs"' in html

    def test_care_form_page_has_label_translations(
        self, test_client: TestClient, test_animal: Animal
    ) -> None:
        """世話記録フォームページのラベルにdata-i18n属性が存在する"""
        response = test_client.get(
            f"/public/care?animal_id={test_animal.id}",
            follow_redirects=True,
        )
        assert response.status_code == 200
        html = response.text

        # ラベルの翻訳属性の確認
        assert 'data-i18n="appetite_levels.3"' in html
        assert 'data-i18n="appetite_levels.2"' in html
        assert 'data-i18n="appetite_levels.1"' in html
        assert 'data-i18n="vomiting"' in html
        assert 'data-i18n="vomiting_yes"' in html
        assert 'data-i18n="vomiting_no"' in html

    def test_care_form_page_has_placeholder_translation(
        self, test_client: TestClient, test_animal: Animal
    ) -> None:
        """世話記録フォームページのplaceholderにdata-i18n-placeholder属性が存在する"""
        response = test_client.get(
            f"/public/care?animal_id={test_animal.id}",
            follow_redirects=True,
        )
        assert response.status_code == 200
        html = response.text

        # placeholderの翻訳属性の確認
        assert 'data-i18n-placeholder="notes_placeholder"' in html

    def test_care_form_page_has_error_message_translation(
        self, test_client: TestClient, test_animal: Animal
    ) -> None:
        """世話記録フォームページのエラーメッセージにdata-i18n属性が存在する"""
        response = test_client.get(
            f"/public/care?animal_id={test_animal.id}",
            follow_redirects=True,
        )
        assert response.status_code == 200
        html = response.text

        # エラーメッセージとサクセスメッセージの翻訳属性の確認
        assert 'data-i18n="error_occurred"' in html
        assert 'data-i18n="save_success"' in html

    def test_care_form_page_has_required_mark_translation(
        self, test_client: TestClient, test_animal: Animal
    ) -> None:
        """世話記録フォームページの必須マークにdata-i18n属性が存在する"""
        response = test_client.get(
            f"/public/care?animal_id={test_animal.id}",
            follow_redirects=True,
        )
        assert response.status_code == 200
        html = response.text

        # 必須マークの翻訳属性の確認
        assert 'data-i18n="required"' in html

    def test_care_form_page_uses_care_namespace(
        self, test_client: TestClient, test_animal: Animal
    ) -> None:
        """世話記録フォームページでcareネームスペースが使用されている"""
        response = test_client.get(
            f"/public/care?animal_id={test_animal.id}",
            follow_redirects=True,
        )
        assert response.status_code == 200
        html = response.text

        # careネームスペースの使用確認
        assert 'data-i18n-ns="care"' in html
        # commonネームスペースも一部で使用されている
        assert 'data-i18n-ns="common"' in html


class TestPublicCareLogListI18n:
    """Public Care Log一覧ページの多言語化テスト"""

    def test_care_log_list_page_has_i18n_library(
        self, test_client: TestClient, test_animal: Animal
    ) -> None:
        """記録一覧ページにi18nextライブラリが読み込まれている"""
        response = test_client.get(
            f"/public/care-logs?animal_id={test_animal.id}",
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert "i18next" in response.text
        assert "/static/js/i18n.js" in response.text

    def test_care_log_list_page_has_language_switcher(
        self, test_client: TestClient, test_animal: Animal
    ) -> None:
        """記録一覧ページに言語切替ボタンが存在する"""
        response = test_client.get(
            f"/public/care-logs?animal_id={test_animal.id}",
            follow_redirects=True,
        )
        assert response.status_code == 200
        html = response.text
        if is_kiroween_mode_html(html):
            assert 'id="language-switcher"' not in html
        else:
            assert 'id="language-switcher"' in html
            assert 'class="language-text"' in html

    def test_care_log_list_page_has_i18n_attributes(
        self, test_client: TestClient, test_animal: Animal
    ) -> None:
        """記録一覧ページにdata-i18n属性が付与されている"""
        response = test_client.get(
            f"/public/care-logs?animal_id={test_animal.id}",
            follow_redirects=True,
        )
        assert response.status_code == 200
        html = response.text

        assert 'data-i18n-title="public.page_title"' in html
        assert 'data-i18n-ns="care_logs"' in html
        assert 'data-i18n="public.today_status_title"' in html
        assert 'data-i18n="public.daily_overview_title"' in html
        assert 'data-i18n="public.daily_overview_description"' in html
        assert 'data-i18n="public.daily_overview_hint"' in html
        assert 'data-i18n="public.daily_table.date"' in html
        assert 'data-i18n="public.latest_logs_title"' in html
        assert 'data-i18n="public.latest_logs_description"' in html
        assert 'data-i18n="public.time_slots.morning"' in html
        assert 'data-i18n="public.time_slots.noon"' in html
        assert 'data-i18n="public.time_slots.evening"' in html
        assert 'data-i18n="public.add_record"' in html
        assert 'data-i18n="public.view_all_status"' in html
        assert 'data-i18n-alt="public.animal_photo_alt"' in html

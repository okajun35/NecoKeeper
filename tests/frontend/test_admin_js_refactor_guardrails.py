"""
管理画面JSリファクタのガードレールテスト

- cloneTemplate/ガード関数が common.js に集約されていること
- 各ページJSがローカル cloneTemplate を再定義していないこと
"""

from __future__ import annotations

from pathlib import Path

COMMON_JS_PATH = Path("app/static/js/admin/common.js")
TARGET_JS_FILES = [
    Path("app/static/js/admin/dashboard.js"),
    Path("app/static/js/admin/animal_detail.js"),
    Path("app/static/js/admin/adoption_records.js"),
    Path("app/static/js/admin/applicants.js"),
    Path("app/static/js/admin/animals.js"),
    Path("app/static/js/admin/care_log_detail.js"),
    Path("app/static/js/admin/care_logs_list.js"),
    Path("app/static/js/admin/medical_records_detail.js"),
    Path("app/static/js/admin/medical_records_list.js"),
    Path("app/static/js/admin/volunteer_detail.js"),
    Path("app/static/js/admin/volunteers.js"),
    Path("app/static/js/admin/reports_care.js"),
    Path("app/static/js/admin/reports_medical.js"),
]


class TestAdminJSRefactorGuardrails:
    """共通化ルールを破壊していないかを検証"""

    def test_common_js_has_shared_clone_and_guard_helpers(self) -> None:
        content = COMMON_JS_PATH.read_text()

        assert "function cloneTemplate(templateId)" in content
        assert (
            "function assertRequiredSelectors(root, selectors, context = '')" in content
        )
        assert "function requireSelector(root, selector, context = '')" in content
        assert "function requireElementById(id, context = '')" in content
        assert "function assertRequiredIds(ids, context = '')" in content

        assert "window.cloneTemplate = cloneTemplate;" in content
        assert "window.assertRequiredSelectors = assertRequiredSelectors;" in content
        assert "window.requireSelector = requireSelector;" in content
        assert "window.requireElementById = requireElementById;" in content
        assert "window.assertRequiredIds = assertRequiredIds;" in content

    def test_page_js_does_not_redefine_clone_template(self) -> None:
        for path in TARGET_JS_FILES:
            content = path.read_text()
            assert "function cloneTemplate(" not in content, (
                f"local cloneTemplate found: {path}"
            )
            assert "const cloneTemplate = (" not in content, (
                f"local cloneTemplate found: {path}"
            )

    def test_high_risk_pages_use_selector_assertions(self) -> None:
        dashboard = Path("app/static/js/admin/dashboard.js").read_text()
        animal_detail = Path("app/static/js/admin/animal_detail.js").read_text()
        care_log_detail = Path("app/static/js/admin/care_log_detail.js").read_text()
        medical_detail = Path(
            "app/static/js/admin/medical_records_detail.js"
        ).read_text()

        assert "assertRequiredSelectors(" in dashboard
        assert "assertRequiredSelectors(" in animal_detail
        assert "assertRequiredSelectors(" in care_log_detail
        assert "assertRequiredSelectors(" in medical_detail

"""
管理画面テンプレートの契約テスト

大規模なテンプレート/JSリファクタで壊れやすいDOM構造を
ページ単位で固定し、差分を早期検知する。
"""

from __future__ import annotations

import re

from fastapi.testclient import TestClient


def _extract_template_block(html: str, template_id: str) -> str:
    pattern = rf'<template[^>]*id="{re.escape(template_id)}"[^>]*>(.*?)</template>'
    match = re.search(pattern, html, re.DOTALL)
    assert match is not None, f"template not found: {template_id}"
    return match.group(1)


def _assert_template_snapshot(
    html: str,
    template_id: str,
    required_markers: list[str],
) -> None:
    block = _extract_template_block(html, template_id)
    for marker in required_markers:
        assert marker in block, f"missing marker in {template_id}: {marker}"


class TestAdminTemplateContracts:
    """管理画面テンプレートのDOM契約を検証"""

    def test_dashboard_template_snapshot_contract(
        self, test_client: TestClient, auth_token: str
    ) -> None:
        response = test_client.get(
            "/admin",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 200
        html = response.text
        assert 'id="recent-logs"' in html
        assert 'id="needs-care"' in html

        _assert_template_snapshot(
            html,
            "tmpl-recent-log",
            [
                "js-animal-name",
                "js-time-slot",
                "js-details",
                "js-appetite",
                "js-energy",
            ],
        )
        _assert_template_snapshot(
            html,
            "tmpl-needs-care",
            [
                "js-animal-photo",
                "js-animal-name",
                "js-missing-items",
                "js-record-link",
            ],
        )

    def test_animal_detail_gallery_template_snapshot_contract(
        self, test_client: TestClient, auth_token: str, test_animal
    ) -> None:
        response = test_client.get(
            f"/admin/animals/{test_animal.id}",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 200
        html = response.text
        assert 'id="content-gallery"' in html

        _assert_template_snapshot(
            html,
            "tmpl-gallery-item",
            [
                "js-image",
                "js-overlay-caption",
                "js-caption",
                "js-taken-at",
                "js-delete-btn",
            ],
        )

    def test_care_log_detail_template_snapshot_contract(
        self, test_client: TestClient, auth_token: str, test_care_logs
    ) -> None:
        care_log_id = test_care_logs[0].id
        response = test_client.get(
            f"/admin/care-logs/{care_log_id}",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 200
        html = response.text
        assert 'id="care-log-detail"' in html

        _assert_template_snapshot(
            html,
            "tmpl-care-log-detail",
            [
                "js-log-date",
                "js-time-slot",
                "js-animal-name",
                "js-recorder-name",
                "js-appetite",
                "js-energy",
                "js-urination",
                "js-cleaning",
                "js-defecation",
                "js-stool-condition-container",
                "js-stool-image",
                "js-stool-label",
                "js-stool-empty",
                "js-memo-container",
                "js-memo",
                "js-created-at",
                "js-updated-at",
                "js-edit-btn",
                "js-delete-btn",
            ],
        )

    def test_volunteer_detail_template_snapshot_contract(
        self, test_client: TestClient, auth_token: str, test_volunteer
    ) -> None:
        response = test_client.get(
            f"/admin/volunteers/{test_volunteer.id}",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 200
        html = response.text
        assert 'id="volunteerDetail"' in html

        _assert_template_snapshot(
            html,
            "tmpl-volunteer-detail",
            [
                "js-name",
                "js-contact",
                "js-affiliation",
                "js-status",
                "js-start-date",
            ],
        )

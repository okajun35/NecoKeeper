"""
テスト: Animal API 確認フロー（E2E）

t-wada スタイル：エンドツーエンドユースケース
- 通常のステータス更新API
- 終端ステータスからの復帰フロー（409 → confirm=true 再送）
- メタAPIでのステータス・ロケーション定義の配布
"""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestMetaStatuses:
    """GET /api/v1/meta/statuses - ステータスメタ取得"""

    def test_get_statuses_with_ja_locale(self):
        """GET /meta/statuses (Accept-Language: ja)"""
        # TODO: 実装後にテスト
        # response = client.get(
        #     "/api/v1/meta/statuses",
        #     headers={"Accept-Language": "ja"}
        # )
        # assert response.status_code == 200
        # data = response.json()
        #
        # # レスポンスの構造確認
        # assert isinstance(data, list)
        # assert len(data) == 5  # QUARANTINE, IN_CARE, TRIAL, ADOPTED, DECEASED
        #
        # # 各要素の構造
        # for item in data:
        #     assert "code" in item
        #     assert "label" in item
        #     assert "is_terminal" in item
        #
        # # 終端フラグの確認
        # adopted = next(s for s in data if s["code"] == "ADOPTED")
        # assert adopted["is_terminal"] is True
        # assert adopted["label"] == "ADOPTED"

    def test_get_statuses_with_en_locale(self):
        """GET /meta/statuses (Accept-Language: en)"""
        # TODO: 英語レスポンス対応後にテスト
        # response = client.get(
        #     "/api/v1/meta/statuses",
        #     headers={"Accept-Language": "en"}
        # )
        # assert response.status_code == 200
        # data = response.json()
        # adopted = next(s for s in data if s["code"] == "ADOPTED")
        # assert adopted["label"] == "Adopted"

    def test_get_statuses_default_locale_is_ja(self):
        """GET /meta/statuses (Accept-Language未指定)→ ja デフォルト"""
        # TODO: デフォルト言語がjaであることを確認
        # response = client.get("/api/v1/meta/statuses")
        # assert response.status_code == 200
        # data = response.json()
        # adopted = next(s for s in data if s["code"] == "ADOPTED")
        # assert adopted["label"] == "ADOPTED"


class TestMetaLocationTypes:
    """GET /api/v1/meta/location-types - ロケーションメタ取得"""

    def test_get_location_types_with_ja_locale(self):
        """GET /meta/location-types (Accept-Language: ja)"""
        # TODO: 実装後にテスト
        # response = client.get(
        #     "/api/v1/meta/location-types",
        #     headers={"Accept-Language": "ja"}
        # )
        # assert response.status_code == 200
        # data = response.json()
        #
        # assert isinstance(data, list)
        # assert len(data) == 3  # FACILITY, FOSTER_HOME, ADOPTER_HOME
        #
        # facility = next(l for l in data if l["code"] == "FACILITY")
        # assert "施設" in facility["label"]


class TestUpdateAnimalStatusNormalFlow:
    """PATCH /api/v1/animals/{id} - 通常のステータス更新"""

    def test_patch_status_quarantine_to_in_care(self, test_client: TestClient):
        """PATCH で QUARANTINE → IN_CARE 更新"""
        # TODO: テスト用アニマルを準備し、パッチリクエスト
        # animal_id = create_test_animal_via_api(status="QUARANTINE")
        #
        # response = client.patch(
        #     f"/api/v1/animals/{animal_id}",
        #     json={"status": "IN_CARE"},
        #     headers={"Authorization": f"Bearer {test_token}"}
        # )
        #
        # assert response.status_code == 200
        # data = response.json()
        # assert data["status"] == "IN_CARE"

    def test_patch_location_type_change(self, test_client: TestClient):
        """PATCH で location_type を更新"""
        # TODO: location_type 更新テスト
        # animal_id = create_test_animal_via_api(location_type="FACILITY")
        #
        # response = client.patch(
        #     f"/api/v1/animals/{animal_id}",
        #     json={"location_type": "FOSTER_HOME"},
        #     headers={"Authorization": f"Bearer {test_token}"}
        # )
        #
        # assert response.status_code == 200
        # data = response.json()
        # assert data["location_type"] == "FOSTER_HOME"


class TestUpdateAnimalStatusConfirmationFlow:
    """PATCH /api/v1/animals/{id} - 確認フロー（409 → confirm=true 再送）"""

    def test_adopted_to_in_care_returns_409_without_confirm(self):
        """ADOPTED → IN_CARE（confirm 無し）→ 409 Conflict"""
        # TODO: 終端ステータスからの復帰を試みる
        # animal_id = create_test_animal_via_api(status="ADOPTED")
        #
        # response = client.patch(
        #     f"/api/v1/animals/{animal_id}",
        #     json={"status": "IN_CARE"},
        #     headers={"Authorization": f"Bearer {test_token}"}
        # )
        #
        # assert response.status_code == 409
        # data = response.json()
        # assert data["requires_confirmation"] is True
        # assert data["warning_code"] in ["LEAVE_TERMINAL_STATUS", "LEAVE_ADOPTED"]
        # assert "ADOPTED" in data["message"]

    def test_deceased_to_trial_returns_409_without_confirm(self):
        """DECEASED → TRIAL（confirm 無し）→ 409 Conflict"""
        # TODO: DECEASED からの復帰テスト
        # animal_id = create_test_animal_via_api(status="DECEASED")
        #
        # response = client.patch(
        #     f"/api/v1/animals/{animal_id}",
        #     json={"status": "TRIAL"},
        #     headers={"Authorization": f"Bearer {test_token}"}
        # )
        #
        # assert response.status_code == 409
        # data = response.json()
        # assert data["requires_confirmation"] is True
        # assert "死亡" in data["message"]

    def test_adopted_to_in_care_succeeds_with_confirm(self):
        """ADOPTED → IN_CARE（confirm=true）→ 200 OK"""
        # TODO: 確認ありで復帰を実行
        # animal_id = create_test_animal_via_api(status="ADOPTED")
        #
        # # ステップ1: confirm なしで試みて 409 を取得
        # response1 = client.patch(
        #     f"/api/v1/animals/{animal_id}",
        #     json={"status": "IN_CARE"},
        #     headers={"Authorization": f"Bearer {test_token}"}
        # )
        # assert response1.status_code == 409
        #
        # # ステップ2: confirm=true で再送
        # response2 = client.patch(
        #     f"/api/v1/animals/{animal_id}",
        #     json={
        #         "status": "IN_CARE",
        #         "confirm": True,
        #         "reason": "誤登録の修正"
        #     },
        #     headers={"Authorization": f"Bearer {test_token}"}
        # )
        #
        # assert response2.status_code == 200
        # data = response2.json()
        # assert data["status"] == "IN_CARE"


class TestGetAnimalStatusHistory:
    """GET /api/v1/animals/{id}/status-history - 履歴取得"""

    def test_get_status_history_pagination(self):
        """GET /animals/{id}/status-history（ページネーション）"""
        # TODO: 履歴API実装後にテスト
        # animal_id = create_test_animal_with_history_via_api()
        #
        # response = client.get(
        #     f"/api/v1/animals/{animal_id}/status-history?page=1&page_size=10",
        #     headers={"Authorization": f"Bearer {test_token}"}
        # )
        #
        # assert response.status_code == 200
        # data = response.json()
        # assert "items" in data
        # assert "total" in data
        # assert "page" in data

    def test_status_history_includes_all_fields(self):
        """履歴には id, animal_id, field, old_value, new_value, reason, changed_at が含まれる"""
        # TODO: 履歴オブジェクトの構造確認
        # animal_id = create_test_animal_with_history_via_api()
        #
        # response = client.get(
        #     f"/api/v1/animals/{animal_id}/status-history",
        #     headers={"Authorization": f"Bearer {test_token}"}
        # )
        #
        # data = response.json()
        # history_item = data["items"][0]
        #
        # required_fields = [
        #     "id", "animal_id", "field", "old_value", "new_value",
        #     "reason", "changed_at", "changed_by"
        # ]
        # for field in required_fields:
        #     assert field in history_item

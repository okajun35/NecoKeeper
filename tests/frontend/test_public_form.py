"""
Publicフォームのフロントエンド動作テスト

JavaScriptの動作をPythonから検証するための統合テスト。
実際のブラウザ動作は手動テストまたはE2Eテストツール（Playwright等）で実施。
"""

from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.animal import Animal
from app.models.volunteer import Volunteer


class TestPublicFormRendering:
    """Publicフォームのレンダリングテスト"""

    def test_care_form_page_loads(self, test_client: TestClient, test_animal: Animal):
        """正常系: 世話記録フォームページが読み込める"""
        # When
        response = test_client.get(
            f"/public/care?animal_id={test_animal.id}",
            follow_redirects=True,
        )

        # Then
        assert response.status_code == 200
        assert "世話記録入力" in response.text
        assert "NecoKeeper" in response.text

    def test_care_form_includes_required_elements(
        self, test_client: TestClient, test_animal: Animal
    ):
        """正常系: フォームに必要な要素が含まれている"""
        # When
        response = test_client.get(
            f"/public/care?animal_id={test_animal.id}",
            follow_redirects=True,
        )

        # Then
        html = response.text
        # フォーム要素
        assert 'id="careForm"' in html
        assert 'id="timeSlot"' in html
        assert 'id="appetite"' in html
        assert 'id="energy"' in html
        assert 'id="urination"' in html
        assert 'id="defecation"' in html
        assert 'id="stoolConditionSection"' in html
        assert 'id="stoolCondition"' in html
        assert 'id="cleaning"' in html
        assert 'id="memo"' in html
        assert 'id="volunteer"' in html

        # 便状態ヘルプモーダル
        assert 'id="stoolConditionHelpOpen"' in html
        assert 'id="stoolConditionHelpModal"' in html
        assert 'id="stoolConditionHelpBackdrop"' in html
        assert 'id="stoolConditionHelpClose"' in html

        # ボタン
        assert 'id="copyLastBtn"' in html
        assert 'id="submitBtn"' in html

        # JavaScript（分離されたファイル）
        assert "/static/js/care_form.js" in html

    def test_care_form_includes_pwa_manifest(
        self, test_client: TestClient, test_animal: Animal
    ):
        """正常系: PWA manifestが含まれている"""
        # When
        response = test_client.get(
            f"/public/care?animal_id={test_animal.id}",
            follow_redirects=True,
        )

        # Then
        html = response.text
        assert 'rel="manifest"' in html
        assert "/static/manifest.json" in html

    def test_care_form_includes_service_worker(
        self, test_client: TestClient, test_animal: Animal
    ):
        """正常系: Service Worker登録コードが含まれている"""
        # When
        response = test_client.get(
            f"/public/care?animal_id={test_animal.id}",
            follow_redirects=True,
        )

        # Then
        html = response.text
        assert "serviceWorker" in html
        assert "/static/js/sw.js" in html

    def test_care_form_includes_offline_manager(
        self, test_client: TestClient, test_animal: Animal
    ):
        """正常系: オフラインマネージャーが含まれている"""
        # When
        response = test_client.get(
            f"/public/care?animal_id={test_animal.id}",
            follow_redirects=True,
        )

        # Then
        html = response.text
        assert "/static/js/offline.js" in html
        # offlineManagerはoffline.jsに定義されているため、HTMLには直接含まれない


class TestPublicFormDataFlow:
    """Publicフォームのデータフローテスト"""

    def test_form_submission_flow(
        self, test_client: TestClient, test_animal: Animal, test_db: Session
    ):
        """統合テスト: フォーム送信フロー全体"""
        # Given: ボランティアを作成
        volunteer = Volunteer(
            name="テストボランティア",
            contact="090-1234-5678",
            status="active",
        )
        test_db.add(volunteer)
        test_db.commit()
        test_db.refresh(volunteer)

    def test_form_submission_flow_accepts_notes_alias(
        self, test_client: TestClient, test_animal: Animal, test_db: Session
    ):
        """統合テスト: 旧フィールド名 notes（input alias）で送信しても memo として扱われる"""
        # Given: ボランティアを作成
        volunteer = Volunteer(
            name="テストボランティア",
            contact="090-1234-5678",
            status="active",
        )
        test_db.add(volunteer)
        test_db.commit()
        test_db.refresh(volunteer)

        # When: notes（旧フィールド）で世話記録を送信
        care_log_data = {
            "animal_id": test_animal.id,
            "recorder_id": volunteer.id,
            "recorder_name": volunteer.name,
            "log_date": "2025-11-15",
            "time_slot": "morning",
            "appetite": 1.0,
            "energy": 5,
            "urination": True,
            "cleaning": True,
            "notes": "旧notesフィールドで送信",
        }
        submit_response = test_client.post(
            "/api/v1/public/care-logs", json=care_log_data
        )

        # Then: 受理され、レスポンスは memo として返る
        assert submit_response.status_code == 201
        created_data = submit_response.json()
        assert created_data["memo"] == "旧notesフィールドで送信"

        # And: 最新記録取得でも memo として参照できる
        latest_response = test_client.get(
            f"/api/v1/public/care-logs/latest/{test_animal.id}"
        )
        assert latest_response.status_code == 200
        latest_data = latest_response.json()
        assert latest_data["memo"] == "旧notesフィールドで送信"

        # Step 1: フォームページを読み込む
        form_response = test_client.get(
            f"/public/care?animal_id={test_animal.id}",
            follow_redirects=True,
        )
        assert form_response.status_code == 200

        # Step 2: 猫情報を取得（JavaScriptが実行する処理）
        animal_response = test_client.get(f"/api/v1/public/animals/{test_animal.id}")
        assert animal_response.status_code == 200
        animal_data = animal_response.json()
        assert animal_data["name"] == test_animal.name

        # Step 3: ボランティア一覧を取得（JavaScriptが実行する処理）
        volunteers_response = test_client.get("/api/v1/public/volunteers")
        assert volunteers_response.status_code == 200
        volunteers_data = volunteers_response.json()
        assert len(volunteers_data) == 1

        # Step 4: 世話記録を送信（JavaScriptが実行する処理）
        care_log_data = {
            "animal_id": test_animal.id,
            "recorder_id": volunteer.id,
            "recorder_name": volunteer.name,
            "log_date": "2025-11-15",
            "time_slot": "morning",
            "appetite": 1.0,
            "energy": 5,
            "urination": True,
            "cleaning": True,
            "memo": "元気です",
        }
        submit_response = test_client.post(
            "/api/v1/public/care-logs", json=care_log_data
        )
        assert submit_response.status_code == 201
        created_data = submit_response.json()
        assert created_data["memo"] == "元気です"

        # Step 5: 最新記録を取得（前回値コピー機能）
        latest_response = test_client.get(
            f"/api/v1/public/care-logs/latest/{test_animal.id}"
        )
        assert latest_response.status_code == 200
        latest_data = latest_response.json()
        assert latest_data["time_slot"] == "morning"
        assert latest_data["appetite"] == 1.0
        assert latest_data["memo"] == "元気です"

    def test_copy_last_values_flow(
        self, test_client: TestClient, test_animal: Animal, test_db: Session
    ):
        """統合テスト: 前回値コピー機能のフロー"""
        # Given: ボランティアと既存の記録を作成
        volunteer = Volunteer(
            name="テストボランティア",
            contact="090-1234-5678",
            status="active",
        )
        test_db.add(volunteer)
        test_db.commit()
        test_db.refresh(volunteer)

        # 既存の記録を作成
        existing_log_data = {
            "animal_id": test_animal.id,
            "recorder_id": volunteer.id,
            "recorder_name": volunteer.name,
            "log_date": "2025-11-15",
            "time_slot": "noon",
            "appetite": 0.75,
            "energy": 4,
            "urination": False,
            "cleaning": True,
            "memo": "前回の記録",
        }
        test_client.post("/api/v1/public/care-logs", json=existing_log_data)

        # When: 最新記録を取得（前回値コピーボタンクリック時の処理）
        response = test_client.get(f"/api/v1/public/care-logs/latest/{test_animal.id}")

        # Then: 前回の値が取得できる
        assert response.status_code == 200
        data = response.json()
        assert data["time_slot"] == "noon"
        assert data["appetite"] == 0.75
        assert data["energy"] == 4
        assert data["urination"] is False
        assert data["cleaning"] is True
        # メモはコピーされない（仕様）


class TestPWAManifest:
    """PWA manifestのテスト"""

    def test_manifest_json_accessible(self, test_client: TestClient):
        """正常系: manifest.jsonにアクセスできる"""
        # When
        response = test_client.get("/static/manifest.json")

        # Then
        assert response.status_code == 200
        manifest = response.json()
        assert manifest["name"] == "NecoKeeper - 保護猫管理システム"
        assert manifest["short_name"] == "NecoKeeper"
        assert manifest["display"] == "standalone"
        assert manifest["theme_color"] == "#4f46e5"

    def test_manifest_includes_icons(self, test_client: TestClient):
        """正常系: manifestにアイコンが含まれている"""
        # When
        response = test_client.get("/static/manifest.json")

        # Then
        manifest = response.json()
        assert "icons" in manifest
        assert len(manifest["icons"]) > 0
        # 必須サイズのアイコンが含まれている
        icon_sizes = [icon["sizes"] for icon in manifest["icons"]]
        assert "192x192" in icon_sizes
        assert "512x512" in icon_sizes


class TestServiceWorker:
    """Service Workerのテスト"""

    def test_service_worker_accessible(self, test_client: TestClient):
        """正常系: Service Workerファイルにアクセスできる"""
        # When
        response = test_client.get("/static/js/sw.js")

        # Then
        assert response.status_code == 200
        sw_code = response.text
        assert "Service Worker" in sw_code
        assert "install" in sw_code
        assert "activate" in sw_code
        assert "fetch" in sw_code

    def test_service_worker_includes_cache_strategy(self, test_client: TestClient):
        """正常系: Service Workerにキャッシュ戦略が含まれている"""
        # When
        response = test_client.get("/static/js/sw.js")

        # Then
        sw_code = response.text
        assert "cacheFirstStrategy" in sw_code
        assert "networkFirstStrategy" in sw_code
        assert "CACHE_VERSION" in sw_code

    def test_service_worker_includes_background_sync(self, test_client: TestClient):
        """正常系: Service Workerにバックグラウンド同期が含まれている"""
        # When
        response = test_client.get("/static/js/sw.js")

        # Then
        sw_code = response.text
        assert "sync" in sw_code
        assert "syncCareLogs" in sw_code or "sync-care-logs" in sw_code


class TestOfflineManager:
    """オフラインマネージャーのテスト"""

    def test_offline_manager_accessible(self, test_client: TestClient):
        """正常系: オフラインマネージャーファイルにアクセスできる"""
        # When
        response = test_client.get("/static/js/offline.js")

        # Then
        assert response.status_code == 200
        offline_code = response.text
        assert "OfflineManager" in offline_code
        assert "IndexedDB" in offline_code

    def test_offline_manager_includes_sync_logic(self, test_client: TestClient):
        """正常系: オフラインマネージャーに同期ロジックが含まれている"""
        # When
        response = test_client.get("/static/js/offline.js")

        # Then
        offline_code = response.text
        assert "saveCareLog" in offline_code
        assert "syncPendingLogs" in offline_code
        assert "saveToIndexedDB" in offline_code

    def test_offline_manager_includes_connection_status(self, test_client: TestClient):
        """正常系: オフラインマネージャーに接続状態管理が含まれている"""
        # When
        response = test_client.get("/static/js/offline.js")

        # Then
        offline_code = response.text
        assert "updateConnectionStatus" in offline_code
        assert "isOnline" in offline_code
        assert "setupOnlineListener" in offline_code


class TestResponsiveDesign:
    """レスポンシブデザインのテスト"""

    def test_form_includes_mobile_viewport(
        self, test_client: TestClient, test_animal: Animal
    ):
        """正常系: モバイル用viewportメタタグが含まれている"""
        # When
        response = test_client.get(
            f"/public/care?animal_id={test_animal.id}",
            follow_redirects=True,
        )

        # Then
        html = response.text
        assert 'name="viewport"' in html
        assert "width=device-width" in html
        assert "initial-scale=1.0" in html

    def test_form_uses_tailwind_css(self, test_client: TestClient, test_animal: Animal):
        """正常系: Tailwind CSSが使用されている"""
        # When
        response = test_client.get(
            f"/public/care?animal_id={test_animal.id}",
            follow_redirects=True,
        )

        # Then
        html = response.text
        assert "tailwindcss.com" in html

    def test_form_includes_mobile_optimized_buttons(
        self, test_client: TestClient, test_animal: Animal
    ):
        """正常系: モバイル最適化されたボタンが含まれている"""
        # When
        response = test_client.get(
            f"/public/care?animal_id={test_animal.id}",
            follow_redirects=True,
        )

        # Then
        html = response.text
        # 固定フッターボタン
        assert "fixed bottom-0" in html
        # タッチフレンドリーなボタンサイズ
        assert "py-3 px-" in html


class TestAccessibility:
    """アクセシビリティのテスト"""

    def test_form_includes_labels(self, test_client: TestClient, test_animal: Animal):
        """正常系: フォーム要素にラベルが含まれている"""
        # When
        response = test_client.get(
            f"/public/care?animal_id={test_animal.id}",
            follow_redirects=True,
        )

        # Then
        html = response.text
        assert "<label" in html
        assert "時点" in html
        assert "食欲" in html
        assert "元気" in html
        assert "記録者" in html

    def test_form_includes_required_indicators(
        self, test_client: TestClient, test_animal: Animal
    ):
        """正常系: 必須項目インジケーターが含まれている"""
        # When
        response = test_client.get(
            f"/public/care?animal_id={test_animal.id}",
            follow_redirects=True,
        )

        # Then
        html = response.text
        assert "text-red-500" in html  # 必須マーク（*）のスタイル
        assert "required" in html

    def test_form_includes_alt_text_for_images(
        self, test_client: TestClient, test_animal: Animal
    ):
        """正常系: 画像にalt属性が含まれている"""
        # When
        response = test_client.get(
            f"/public/care?animal_id={test_animal.id}",
            follow_redirects=True,
        )

        # Then
        html = response.text
        assert 'alt="猫の写真"' in html

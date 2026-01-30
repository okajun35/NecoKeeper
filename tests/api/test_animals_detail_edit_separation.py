"""
猫詳細画面・編集画面の統合テスト

詳細画面と編集画面の分離に関するテスト
- 詳細画面: 基本情報は読み取り専用、ステータス/所在地は変更可能
- 編集画面: 詳細情報は読み取り専用表示、基本情報とステータス/所在地が編集可能
"""


class TestAnimalDetailPage:
    """猫詳細画面のテスト"""

    def test_detail_page_displays_basic_info_as_readonly(
        self, test_client, test_db, auth_token, test_animal
    ):
        """詳細画面で基本情報が読み取り専用として表示される"""
        response = test_client.get(
            f"/admin/animals/{test_animal.id}",
            headers={"Authorization": f"Bearer {auth_token}"},
            follow_redirects=True,
        )

        assert response.status_code == 200
        html = response.text

        # 基本情報セクションが存在する
        assert "基本情報" in html
        assert test_animal.name in html
        assert test_animal.coat_color in html

        # 名前フィールドがinputではなくpタグで表示されている（読み取り専用）
        assert 'id="name"' not in html
        # 編集ボタンが存在する
        assert f"/admin/animals/{test_animal.id}/edit" in html
        assert "編集する" in html or "編集" in html

    def test_detail_page_has_status_location_change_ui(
        self, test_client, test_db, auth_token, test_animal
    ):
        """詳細画面にステータス/所在地変更UIが存在する"""
        response = test_client.get(
            f"/admin/animals/{test_animal.id}",
            headers={"Authorization": f"Bearer {auth_token}"},
            follow_redirects=True,
        )

        assert response.status_code == 200
        html = response.text

        # ステータス変更のselect要素が存在する
        assert 'id="statusSelect"' in html
        assert "<select" in html

        # 所在地タイプのselect要素が存在する
        assert 'id="locationTypeSelect"' in html

        # 所在地詳細のinput要素が存在する
        assert 'id="currentLocationNote"' in html

        # 変更理由のtextarea要素が存在する
        assert 'id="reasonForStatusChange"' in html
        assert "変更理由" in html

        # 更新ボタンが存在する
        assert 'id="updateStatusAndLocationBtn"' in html


class TestAnimalEditPage:
    """猫編集画面のテスト"""

    def test_edit_page_displays_detail_info_as_readonly(
        self, test_client, test_db, auth_token, test_animal
    ):
        """編集画面で詳細情報が読み取り専用として表示される"""
        response = test_client.get(
            f"/admin/animals/{test_animal.id}/edit",
            headers={"Authorization": f"Bearer {auth_token}"},
            follow_redirects=True,
        )

        assert response.status_code == 200
        html = response.text

        # 詳細情報表示セクションが存在する
        assert 'class="bg-gray-50 rounded-lg' in html

        # protected_at_display, status_display等の表示要素が存在する
        assert 'id="protected_at_display"' in html
        assert 'id="status_display"' in html
        assert 'id="location_display"' in html
        assert 'id="current_location_note_display"' in html

    def test_edit_page_has_status_input_fields(
        self, test_client, test_db, auth_token, test_animal
    ):
        """編集画面にステータス等の入力フィールドが存在する"""
        response = test_client.get(
            f"/admin/animals/{test_animal.id}/edit",
            headers={"Authorization": f"Bearer {auth_token}"},
            follow_redirects=True,
        )

        assert response.status_code == 200
        html = response.text

        # status, protected_at, location_type, current_location_noteの
        # input/selectフィールドが存在することを確認
        assert 'id="status"' in html
        assert 'id="protected_at"' in html
        assert 'id="location_type"' in html
        assert 'id="current_location_note"' in html

    def test_edit_page_has_editable_basic_info_fields(
        self, test_client, test_db, auth_token, test_animal
    ):
        """編集画面に基本情報の編集可能フィールドが存在する"""
        response = test_client.get(
            f"/admin/animals/{test_animal.id}/edit",
            headers={"Authorization": f"Bearer {auth_token}"},
            follow_redirects=True,
        )

        assert response.status_code == 200
        html = response.text

        # 基本情報の編集フィールドが存在する
        assert 'id="name"' in html
        assert 'id="coat_color"' in html
        assert 'id="gender"' in html
        assert 'id="age_months"' in html
        assert 'id="microchip_number"' in html
        assert 'id="rescue_source"' in html
        assert 'id="tail_length"' in html


class TestAnimalStatusChange:
    """ステータス変更機能のテスト"""

    def test_update_status_with_reason(
        self, test_client, test_db, auth_token, test_animal
    ):
        """変更理由を含むステータス更新が正しく動作する"""
        update_payload = {
            "status": "IN_CARE",
            "location_type": "FACILITY",
            "reason": "テスト: 治療開始のため",
        }

        response = test_client.put(
            f"/api/v1/animals/{test_animal.id}",
            headers={"Authorization": f"Bearer {auth_token}"},
            json=update_payload,
        )

        assert response.status_code == 200
        updated_animal = response.json()
        assert updated_animal["status"] == "IN_CARE"
        # reasonフィールドは保存されないが、エラーにならないことを確認

    def test_update_status_without_reason(
        self, test_client, test_db, auth_token, test_animal
    ):
        """変更理由なしでもステータス更新が動作する"""
        update_payload = {
            "status": "IN_CARE",
            "location_type": "FACILITY",
        }

        response = test_client.put(
            f"/api/v1/animals/{test_animal.id}",
            headers={"Authorization": f"Bearer {auth_token}"},
            json=update_payload,
        )

        assert response.status_code == 200
        updated_animal = response.json()
        assert updated_animal["status"] == "IN_CARE"


class TestAnimalEditFormSubmission:
    """編集フォーム送信のテスト"""

    def test_edit_form_updates_status_fields(
        self, test_client, test_db, auth_token, test_animal
    ):
        """編集フォームからstatus等のフィールドを更新できる"""
        update_payload = {
            "name": "更新された猫",
            "coat_color": "黒",
            "gender": "female",
            "age_months": 12,
            "tail_length": "長い",
            "status": "TRIAL",
            "protected_at": "2025-01-01",
            "location_type": "FOSTER_HOME",
            "current_location_note": "テスト預かり宅",
        }

        response = test_client.put(
            f"/api/v1/animals/{test_animal.id}",
            headers={"Authorization": f"Bearer {auth_token}"},
            json=update_payload,
        )

        assert response.status_code == 200
        updated_animal = response.json()

        # 基本情報が更新されている
        assert updated_animal["name"] == "更新された猫"
        assert updated_animal["coat_color"] == "黒"

        # ステータス等が更新されている
        assert updated_animal["status"] == "TRIAL"
        assert updated_animal["location_type"] == "FOSTER_HOME"

    def test_edit_form_updates_basic_info_only(
        self, test_client, test_db, auth_token, test_animal
    ):
        """編集フォームで基本情報が正しく更新される"""
        original_status = test_animal.status
        original_location = test_animal.location_type

        update_payload = {
            "name": "新しい名前",
            "coat_color": "白",
            "coat_color_note": "白い毛並み",
            "gender": "male",
            "age_months": 24,
            "microchip_number": "123456789012345",
            "tail_length": "短い",
            "collar": "赤い首輪",
            "ear_cut": True,
            "rescue_source": "保健所",
            "breed": "雑種",
            "features": "人懐っこい",
        }

        response = test_client.put(
            f"/api/v1/animals/{test_animal.id}",
            headers={"Authorization": f"Bearer {auth_token}"},
            json=update_payload,
        )

        assert response.status_code == 200
        updated_animal = response.json()

        # すべての基本情報が更新されている
        assert updated_animal["name"] == "新しい名前"
        assert updated_animal["coat_color"] == "白"
        assert updated_animal["coat_color_note"] == "白い毛並み"
        assert updated_animal["gender"] == "male"
        assert updated_animal["age_months"] == 24
        assert updated_animal["microchip_number"] == "123456789012345"
        assert updated_animal["tail_length"] == "短い"

        # ステータス/所在地は変更されていない
        assert updated_animal["status"] == original_status
        assert updated_animal["location_type"] == original_location

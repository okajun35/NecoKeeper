"""
猫管理APIの統合テスト
"""


class TestAnimalCRUD:
    """猫CRUD操作のテストクラス"""

    def test_create_animal(self, test_client, test_db, auth_token):
        """猫を作成できる"""
        given_payload = {
            "name": "新しい猫",
            "photo": "new.jpg",
            "pattern": "三毛",
            "tail_length": "短い",
            "age_months": 6,
            "gender": "male",
            "status": "保護中",
        }

        response = test_client.post(
            "/api/v1/animals",
            headers={"Authorization": f"Bearer {auth_token}"},
            json=given_payload,
        )

        assert response.status_code == 201
        response_body = response.json()
        assert response_body["name"] == given_payload["name"]

    def test_list_animals(self, test_client, test_db, auth_token):
        """猫一覧を取得できる"""
        response = test_client.get(
            "/api/v1/animals", headers={"Authorization": f"Bearer {auth_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1

    def test_create_animal_without_age_months_defaults(
        self, test_client, test_db, auth_token
    ):
        """月齢を省略した場合は不明として扱われる"""
        given_payload = {
            "name": "月齢なしの猫",
            "pattern": "白黒",
            "tail_length": "短い",
            "gender": "female",
            "status": "保護中",
        }

        response = test_client.post(
            "/api/v1/animals",
            headers={"Authorization": f"Bearer {auth_token}"},
            json=given_payload,
        )

        assert response.status_code == 201
        response_body = response.json()
        assert response_body["age_months"] is None
        assert response_body["age_is_estimated"] is False

    def test_create_animal_with_estimated_age(self, test_client, test_db, auth_token):
        """推定月齢を登録できる"""
        given_payload = {
            "name": "推定月齢の猫",
            "pattern": "キジトラ",
            "tail_length": "長い",
            "age_months": 10,
            "age_is_estimated": True,
            "gender": "male",
            "status": "保護中",
        }

        response = test_client.post(
            "/api/v1/animals",
            headers={"Authorization": f"Bearer {auth_token}"},
            json=given_payload,
        )

        assert response.status_code == 201
        response_body = response.json()
        assert response_body["age_months"] == given_payload["age_months"]
        assert response_body["age_is_estimated"] is True


class TestAnimalMicrochipNumber:
    """マイクロチップ番号のテストクラス"""

    def test_create_animal_with_microchip_number(
        self, test_client, test_db, auth_token
    ):
        """マイクロチップ番号付きで猫を登録"""
        response = test_client.post(
            "/api/v1/animals",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "name": "チップ登録猫",
                "pattern": "キジトラ",
                "tail_length": "長い",
                "age_months": 12,
                "gender": "male",
                "microchip_number": "392123456789012",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["microchip_number"] == "392123456789012"

    def test_create_animal_without_microchip_number(
        self, test_client, test_db, auth_token
    ):
        """マイクロチップ番号なしで猫を登録"""
        response = test_client.post(
            "/api/v1/animals",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "name": "チップなし猫",
                "pattern": "三毛",
                "tail_length": "長い",
                "age_months": 6,
                "gender": "female",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["microchip_number"] is None

    def test_create_animal_duplicate_microchip_number(
        self, test_client, test_db, auth_token
    ):
        """重複したマイクロチップ番号でエラーになることを確認"""
        # 既存の猫を作成
        test_client.post(
            "/api/v1/animals",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "name": "既存猫",
                "pattern": "三毛",
                "tail_length": "長い",
                "age_months": 12,
                "gender": "female",
                "microchip_number": "392987654321098",
            },
        )

        # 同じマイクロチップ番号で登録を試みる
        response = test_client.post(
            "/api/v1/animals",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "name": "新規猫",
                "pattern": "黒猫",
                "tail_length": "長い",
                "age_months": 6,
                "gender": "male",
                "microchip_number": "392987654321098",
            },
        )
        assert response.status_code == 409
        assert "既に登録されています" in response.json()["detail"]

    def test_update_animal_microchip_number(self, test_client, test_db, auth_token):
        """マイクロチップ番号を更新できることを確認"""
        # 猫を作成
        create_response = test_client.post(
            "/api/v1/animals",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "name": "更新テスト猫",
                "pattern": "サバトラ",
                "tail_length": "長い",
                "age_months": 12,
                "gender": "male",
            },
        )
        animal_id = create_response.json()["id"]

        # マイクロチップ番号を追加
        update_response = test_client.put(
            f"/api/v1/animals/{animal_id}",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"microchip_number": "981234567890123"},
        )
        assert update_response.status_code == 200
        assert update_response.json()["microchip_number"] == "981234567890123"

    def test_update_animal_duplicate_microchip_number(
        self, test_client, test_db, auth_token
    ):
        """更新時に重複したマイクロチップ番号でエラーになることを確認"""
        # 2匹の猫を作成
        test_client.post(
            "/api/v1/animals",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "name": "猫1",
                "pattern": "キジトラ",
                "tail_length": "長い",
                "age_months": 12,
                "gender": "male",
                "microchip_number": "392111111111111",
            },
        )

        animal2_response = test_client.post(
            "/api/v1/animals",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "name": "猫2",
                "pattern": "三毛",
                "tail_length": "長い",
                "age_months": 6,
                "gender": "female",
            },
        )
        animal2_id = animal2_response.json()["id"]

        # 猫2に猫1と同じマイクロチップ番号を設定しようとする
        update_response = test_client.put(
            f"/api/v1/animals/{animal2_id}",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"microchip_number": "392111111111111"},
        )
        assert update_response.status_code == 409
        assert "既に登録されています" in update_response.json()["detail"]

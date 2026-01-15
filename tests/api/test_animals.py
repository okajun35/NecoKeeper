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

"""
猫管理APIの統合テスト
"""


class TestAnimalCRUD:
    """猫CRUD操作のテストクラス"""

    def test_create_animal(self, test_client, test_db, auth_token):
        """猫を作成できる"""
        response = test_client.post(
            "/api/v1/animals",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "name": "新しい猫",
                "photo": "new.jpg",
                "pattern": "三毛",
                "tail_length": "短い",
                "age": "子猫",
                "gender": "male",
                "status": "保護中",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "新しい猫"

    def test_list_animals(self, test_client, test_db, auth_token):
        """猫一覧を取得できる"""
        response = test_client.get(
            "/api/v1/animals", headers={"Authorization": f"Bearer {auth_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1

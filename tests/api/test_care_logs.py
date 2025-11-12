"""
世話記録APIの統合テスト
"""

from app.models.animal import Animal
from app.models.care_log import CareLog


class TestCareLogCRUD:
    """世話記録CRUD操作のテストクラス"""

    def test_create_care_log(self, test_client, test_db, auth_token):
        """世話記録を作成できる"""
        # 猫IDを取得
        animal = test_db.query(Animal).first()
        animal_id = animal.id

        response = test_client.post(
            "/api/v1/care-logs",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "animal_id": animal_id,
                "recorder_name": "テスト記録者",
                "time_slot": "morning",
                "appetite": 4,
                "energy": 5,
                "urination": True,
                "cleaning": True,
                "memo": "元気です",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["animal_id"] == animal_id
        assert data["recorder_name"] == "テスト記録者"
        assert data["time_slot"] == "morning"
        assert data["appetite"] == 4
        assert data["energy"] == 5

    def test_list_care_logs(self, test_client, test_db, auth_token):
        """世話記録一覧を取得できる"""
        # テストデータを作成
        animal = test_db.query(Animal).first()

        care_log = CareLog(
            animal_id=animal.id,
            recorder_name="テスト記録者",
            time_slot="morning",
            appetite=4,
            energy=5,
            urination=True,
            cleaning=True,
        )
        test_db.add(care_log)
        test_db.commit()

        response = test_client.get(
            "/api/v1/care-logs", headers={"Authorization": f"Bearer {auth_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
        assert len(data["items"]) >= 1

    def test_get_care_log(self, test_client, test_db, auth_token):
        """世話記録の詳細を取得できる"""
        # テストデータを作成
        animal = test_db.query(Animal).first()

        care_log = CareLog(
            animal_id=animal.id,
            recorder_name="テスト記録者",
            time_slot="noon",
            appetite=3,
            energy=4,
            urination=False,
            cleaning=False,
        )
        test_db.add(care_log)
        test_db.commit()
        care_log_id = care_log.id

        response = test_client.get(
            f"/api/v1/care-logs/{care_log_id}",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == care_log_id
        assert data["time_slot"] == "noon"

    def test_update_care_log(self, test_client, test_db, auth_token):
        """世話記録を更新できる"""
        # テストデータを作成
        animal = test_db.query(Animal).first()

        care_log = CareLog(
            animal_id=animal.id,
            recorder_name="テスト記録者",
            time_slot="evening",
            appetite=3,
            energy=3,
            urination=True,
            cleaning=True,
        )
        test_db.add(care_log)
        test_db.commit()
        care_log_id = care_log.id

        response = test_client.put(
            f"/api/v1/care-logs/{care_log_id}",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"appetite": 5, "energy": 5, "memo": "更新されました"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["appetite"] == 5
        assert data["energy"] == 5
        assert data["memo"] == "更新されました"

    def test_filter_by_animal_id(self, test_client, test_db, auth_token):
        """猫IDでフィルタリングできる"""
        # テストデータを作成
        animal = test_db.query(Animal).first()
        animal_id = animal.id

        care_log = CareLog(
            animal_id=animal_id,
            recorder_name="テスト記録者",
            time_slot="morning",
            appetite=4,
            energy=4,
            urination=True,
            cleaning=True,
        )
        test_db.add(care_log)
        test_db.commit()

        response = test_client.get(
            f"/api/v1/care-logs?animal_id={animal_id}",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
        for item in data["items"]:
            assert item["animal_id"] == animal_id


class TestCareLogCSVExport:
    """世話記録CSV出力のテストクラス"""

    def test_export_csv(self, test_client, test_db, auth_token):
        """CSV出力ができる"""
        # テストデータを作成
        animal = test_db.query(Animal).first()

        care_log = CareLog(
            animal_id=animal.id,
            recorder_name="テスト記録者",
            time_slot="morning",
            appetite=4,
            energy=5,
            urination=True,
            cleaning=True,
            memo="テストメモ",
        )
        test_db.add(care_log)
        test_db.commit()

        response = test_client.get(
            "/api/v1/care-logs/export",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 200
        assert response.headers["content-type"] == "text/csv; charset=utf-8"

        # CSVの内容を確認
        csv_content = response.text
        assert "ID" in csv_content
        assert "猫ID" in csv_content
        assert "記録者名" in csv_content
        assert "テスト記録者" in csv_content


class TestLatestCareLog:
    """前回入力値コピー機能のテストクラス"""

    def test_get_latest_care_log(self, test_client, test_db, auth_token):
        """最新の世話記録を取得できる"""
        # テストデータを作成
        animal = test_db.query(Animal).first()
        animal_id = animal.id

        # 古い記録
        old_log = CareLog(
            animal_id=animal_id,
            recorder_name="古い記録者",
            time_slot="morning",
            appetite=3,
            energy=3,
            urination=True,
            cleaning=True,
        )
        test_db.add(old_log)
        test_db.flush()

        # 新しい記録
        new_log = CareLog(
            animal_id=animal_id,
            recorder_name="新しい記録者",
            time_slot="noon",
            appetite=5,
            energy=5,
            urination=True,
            cleaning=True,
        )
        test_db.add(new_log)
        test_db.commit()

        response = test_client.get(
            f"/api/v1/care-logs/latest/{animal_id}",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["recorder_name"] == "新しい記録者"
        assert data["time_slot"] == "noon"
        assert data["appetite"] == 5

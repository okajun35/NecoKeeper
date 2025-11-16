"""
里親管理APIエンドポイントのテスト

里親希望者と譲渡記録のCRUD操作をテストします。
"""

from __future__ import annotations

from datetime import date

from fastapi import status

from app.models.adoption_record import AdoptionRecord
from app.models.applicant import Applicant

# ========================================
# Applicant（里親希望者）APIテスト
# ========================================


class TestListApplicantsAPI:
    """里親希望者一覧取得APIのテスト"""

    def test_list_applicants_returns_200(self, test_client, test_db, auth_headers):
        """正常系: 里親希望者一覧を取得できる"""
        # Given
        applicants_data = [
            Applicant(name=f"希望者{i}", contact=f"contact{i}@example.com")
            for i in range(3)
        ]
        test_db.add_all(applicants_data)
        test_db.commit()

        # When
        response = test_client.get("/api/v1/adoptions/applicants", headers=auth_headers)

        # Then
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 3
        assert data[0]["name"] == "希望者0"

    def test_list_applicants_without_auth_returns_401(self, test_client):
        """異常系: 認証なしで401エラー"""
        # When
        response = test_client.get("/api/v1/adoptions/applicants")

        # Then
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestCreateApplicantAPI:
    """里親希望者登録APIのテスト"""

    def test_create_applicant_with_valid_data_returns_201(
        self, test_client, auth_headers
    ):
        """正常系: 有効なデータで里親希望者を登録できる"""
        # Given
        applicant_data = {
            "name": "山田太郎",
            "contact": "090-1234-5678",
            "address": "東京都渋谷区",
            "family": "夫婦2人",
            "environment": "マンション、ペット可",
            "conditions": "成猫希望",
        }

        # When
        response = test_client.post(
            "/api/v1/adoptions/applicants",
            json=applicant_data,
            headers=auth_headers,
        )

        # Then
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == "山田太郎"
        assert data["contact"] == "090-1234-5678"
        assert "id" in data
        assert "created_at" in data

    def test_create_applicant_without_auth_returns_401(self, test_client):
        """異常系: 認証なしで401エラー"""
        # Given
        applicant_data = {"name": "山田太郎", "contact": "090-1234-5678"}

        # When
        response = test_client.post("/api/v1/adoptions/applicants", json=applicant_data)

        # Then
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestGetApplicantAPI:
    """里親希望者取得APIのテスト"""

    def test_get_applicant_with_valid_id_returns_200(
        self, test_client, test_db, auth_headers
    ):
        """正常系: 有効なIDで里親希望者を取得できる"""
        # Given
        applicant = Applicant(name="山田太郎", contact="090-1234-5678")
        test_db.add(applicant)
        test_db.commit()
        test_db.refresh(applicant)

        # When
        response = test_client.get(
            f"/api/v1/adoptions/applicants/{applicant.id}",
            headers=auth_headers,
        )

        # Then
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == applicant.id
        assert data["name"] == "山田太郎"

    def test_get_applicant_with_nonexistent_id_returns_404(
        self, test_client, auth_headers
    ):
        """異常系: 存在しないIDで404エラー"""
        # When
        response = test_client.get(
            "/api/v1/adoptions/applicants/99999", headers=auth_headers
        )

        # Then
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestUpdateApplicantAPI:
    """里親希望者更新APIのテスト"""

    def test_update_applicant_with_valid_data_returns_200(
        self, test_client, test_db, auth_headers
    ):
        """正常系: 有効なデータで里親希望者を更新できる"""
        # Given
        applicant = Applicant(name="山田太郎", contact="090-1234-5678")
        test_db.add(applicant)
        test_db.commit()
        test_db.refresh(applicant)

        update_data = {"contact": "090-9876-5432", "address": "大阪府大阪市"}

        # When
        response = test_client.put(
            f"/api/v1/adoptions/applicants/{applicant.id}",
            json=update_data,
            headers=auth_headers,
        )

        # Then
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["contact"] == "090-9876-5432"
        assert data["address"] == "大阪府大阪市"
        assert data["name"] == "山田太郎"  # 変更されていない

    def test_update_applicant_with_nonexistent_id_returns_404(
        self, test_client, auth_headers
    ):
        """異常系: 存在しないIDで404エラー"""
        # Given
        update_data = {"contact": "090-9876-5432"}

        # When
        response = test_client.put(
            "/api/v1/adoptions/applicants/99999",
            json=update_data,
            headers=auth_headers,
        )

        # Then
        assert response.status_code == status.HTTP_404_NOT_FOUND


# ========================================
# AdoptionRecord（譲渡記録）APIテスト
# ========================================


class TestListAdoptionRecordsAPI:
    """譲渡記録一覧取得APIのテスト"""

    def test_list_adoption_records_returns_200(
        self, test_client, test_db, test_animal, auth_headers
    ):
        """正常系: 譲渡記録一覧を取得できる"""
        # Given
        applicant = Applicant(name="山田太郎", contact="090-1234-5678")
        test_db.add(applicant)
        test_db.commit()
        test_db.refresh(applicant)

        records_data = [
            AdoptionRecord(
                animal_id=test_animal.id,
                applicant_id=applicant.id,
                decision="pending",
            )
            for _ in range(2)
        ]
        test_db.add_all(records_data)
        test_db.commit()

        # When
        response = test_client.get("/api/v1/adoptions/records", headers=auth_headers)

        # Then
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 2

    def test_list_adoption_records_filtered_by_animal_id(
        self, test_client, test_db, test_animal, auth_headers
    ):
        """正常系: 特定の猫の譲渡記録のみを取得できる"""
        # Given
        applicant = Applicant(name="山田太郎", contact="090-1234-5678")
        test_db.add(applicant)
        test_db.commit()
        test_db.refresh(applicant)

        record = AdoptionRecord(
            animal_id=test_animal.id,
            applicant_id=applicant.id,
            decision="pending",
        )
        test_db.add(record)
        test_db.commit()

        # When
        response = test_client.get(
            f"/api/v1/adoptions/records?animal_id={test_animal.id}",
            headers=auth_headers,
        )

        # Then
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["animal_id"] == test_animal.id


class TestCreateInterviewRecordAPI:
    """面談記録登録APIのテスト"""

    def test_create_interview_record_with_valid_data_returns_201(
        self, test_client, test_db, test_animal, auth_headers
    ):
        """正常系: 有効なデータで面談記録を登録できる"""
        # Given
        applicant = Applicant(name="山田太郎", contact="090-1234-5678")
        test_db.add(applicant)
        test_db.commit()
        test_db.refresh(applicant)

        record_data = {
            "animal_id": test_animal.id,
            "applicant_id": applicant.id,
            "interview_date": "2025-11-15",
            "interview_note": "面談実施。飼育環境良好。",
            "decision": "pending",
        }

        # When
        response = test_client.post(
            "/api/v1/adoptions/records",
            json=record_data,
            headers=auth_headers,
        )

        # Then
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["animal_id"] == test_animal.id
        assert data["applicant_id"] == applicant.id
        assert data["decision"] == "pending"
        assert "id" in data

    def test_create_interview_record_with_nonexistent_animal_returns_404(
        self, test_client, test_db, auth_headers
    ):
        """異常系: 存在しない猫IDで404エラー"""
        # Given
        applicant = Applicant(name="山田太郎", contact="090-1234-5678")
        test_db.add(applicant)
        test_db.commit()
        test_db.refresh(applicant)

        record_data = {
            "animal_id": 99999,
            "applicant_id": applicant.id,
            "interview_date": "2025-11-15",
            "decision": "pending",
        }

        # When
        response = test_client.post(
            "/api/v1/adoptions/records",
            json=record_data,
            headers=auth_headers,
        )

        # Then
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestCreateAdoptionAPI:
    """譲渡記録登録APIのテスト"""

    def test_create_adoption_updates_animal_status(
        self, test_client, test_db, test_animal, auth_headers
    ):
        """正常系: 譲渡記録登録時に猫のステータスが「譲渡済み」に更新される"""
        # Given
        applicant = Applicant(name="山田太郎", contact="090-1234-5678")
        test_db.add(applicant)
        test_db.commit()
        test_db.refresh(applicant)

        # When
        response = test_client.post(
            "/api/v1/adoptions/records/adopt",
            params={
                "animal_id": test_animal.id,
                "applicant_id": applicant.id,
                "adoption_date": "2025-11-20",
            },
            headers=auth_headers,
        )

        # Then
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["adoption_date"] == "2025-11-20"
        assert data["decision"] == "approved"

        # 猫のステータスが更新されている
        test_db.refresh(test_animal)
        assert test_animal.status == "譲渡済み"


class TestGetAdoptionRecordAPI:
    """譲渡記録取得APIのテスト"""

    def test_get_adoption_record_with_valid_id_returns_200(
        self, test_client, test_db, test_animal, auth_headers
    ):
        """正常系: 有効なIDで譲渡記録を取得できる"""
        # Given
        applicant = Applicant(name="山田太郎", contact="090-1234-5678")
        test_db.add(applicant)
        test_db.commit()
        test_db.refresh(applicant)

        record = AdoptionRecord(
            animal_id=test_animal.id,
            applicant_id=applicant.id,
            adoption_date=date(2025, 11, 20),
            decision="approved",
        )
        test_db.add(record)
        test_db.commit()
        test_db.refresh(record)

        # When
        response = test_client.get(
            f"/api/v1/adoptions/records/{record.id}", headers=auth_headers
        )

        # Then
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == record.id
        assert data["decision"] == "approved"

    def test_get_adoption_record_with_nonexistent_id_returns_404(
        self, test_client, auth_headers
    ):
        """異常系: 存在しないIDで404エラー"""
        # When
        response = test_client.get(
            "/api/v1/adoptions/records/99999", headers=auth_headers
        )

        # Then
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestUpdateAdoptionRecordAPI:
    """譲渡記録更新APIのテスト"""

    def test_update_adoption_record_with_valid_data_returns_200(
        self, test_client, test_db, test_animal, auth_headers
    ):
        """正常系: 有効なデータで譲渡記録を更新できる"""
        # Given
        applicant = Applicant(name="山田太郎", contact="090-1234-5678")
        test_db.add(applicant)
        test_db.commit()
        test_db.refresh(applicant)

        record = AdoptionRecord(
            animal_id=test_animal.id,
            applicant_id=applicant.id,
            adoption_date=date(2025, 11, 20),
            decision="approved",
        )
        test_db.add(record)
        test_db.commit()
        test_db.refresh(record)

        update_data = {"follow_up": "譲渡後1週間経過。問題なし。"}

        # When
        response = test_client.put(
            f"/api/v1/adoptions/records/{record.id}",
            json=update_data,
            headers=auth_headers,
        )

        # Then
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["follow_up"] == "譲渡後1週間経過。問題なし。"

    def test_update_adoption_record_with_nonexistent_id_returns_404(
        self, test_client, auth_headers
    ):
        """異常系: 存在しないIDで404エラー"""
        # Given
        update_data = {"follow_up": "フォロー内容"}

        # When
        response = test_client.put(
            "/api/v1/adoptions/records/99999",
            json=update_data,
            headers=auth_headers,
        )

        # Then
        assert response.status_code == status.HTTP_404_NOT_FOUND

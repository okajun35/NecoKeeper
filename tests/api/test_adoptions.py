"""
里親管理APIエンドポイントのテスト

里親希望者（拡張版）と譲渡記録のCRUD操作をテストします。
"""

from __future__ import annotations

from datetime import date

from fastapi import status

from app.models.adoption_consultation import AdoptionConsultation
from app.models.adoption_record import AdoptionRecord
from app.models.applicant import Applicant

# ========================================
# Applicant（里親希望者・拡張版）APIテスト
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
        response = test_client.get(
            "/api/v1/adoptions/applicants-extended", headers=auth_headers
        )

        # Then
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 3
        names = {item["name"] for item in data}
        assert names == {"希望者0", "希望者1", "希望者2"}

    def test_list_applicants_without_auth_returns_401(self, test_client):
        """異常系: 認証なしで401エラー"""
        # When
        response = test_client.get("/api/v1/adoptions/applicants-extended")

        # Then
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestCreateApplicantAPI:
    """里親希望者登録API（拡張版）のテスト"""

    def test_create_applicant_with_valid_data_returns_201(
        self, test_client, auth_headers
    ):
        """正常系: 有効なデータで里親希望者を登録できる"""
        # Given
        applicant_data = {
            "name_kana": "ヤマダタロウ",
            "name": "山田太郎",
            "age": 35,
            "phone": "090-1234-5678",
            "contact_type": "email",
            "contact_email": "yamada@example.com",
            "contact_line_id": None,
            "postal_code": "150-0001",
            "address1": "東京都渋谷区神宮前1-2-3",
            "address2": "サンプルマンション101",
            "occupation": "company_employee",
            "occupation_other": None,
            "desired_cat_alias": "未定",
            "emergency_relation": "parents",
            "emergency_relation_other": None,
            "emergency_name": "山田花子",
            "emergency_phone": "090-9876-5432",
            "family_intent": "all_positive",
            "pet_permission": "allowed",
            "pet_limit_type": "limited",
            "pet_limit_count": 2,
            "housing_type": "apartment",
            "housing_ownership": "rented",
            "relocation_plan": "none",
            "relocation_time_note": None,
            "relocation_cat_plan": None,
            "allergy_status": "none",
            "smoker_in_household": "no",
            "monthly_budget_yen": 15000,
            "alone_time_status": "sometimes",
            "alone_time_weekly_days": 2,
            "alone_time_hours": 6.0,
            "has_existing_cat": "no",
            "has_other_pets": "no",
            "household_members": [
                {"relation": "wife", "relation_other": None, "age": 33}
            ],
            "pets": [],
        }

        # When
        response = test_client.post(
            "/api/v1/adoptions/applicants-extended",
            json=applicant_data,
            headers=auth_headers,
        )

        # Then
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == "山田太郎"
        assert data["contact_email"] == "yamada@example.com"
        assert "id" in data
        assert "created_at" in data

    def test_create_applicant_without_auth_returns_401(self, test_client):
        """異常系: 認証なしで401エラー"""
        # Given
        applicant_data = {
            "name_kana": "ヤマダタロウ",
            "name": "山田太郎",
            "age": 35,
            "phone": "090-1234-5678",
            "contact_type": "email",
            "contact_email": "yamada@example.com",
            "postal_code": "150-0001",
            "address1": "東京都渋谷区神宮前1-2-3",
            "occupation": "company_employee",
            "emergency_relation": "parents",
            "emergency_name": "山田花子",
            "emergency_phone": "090-9876-5432",
            "family_intent": "all_positive",
            "pet_permission": "allowed",
            "pet_limit_type": "limited",
            "pet_limit_count": 2,
            "housing_type": "apartment",
            "housing_ownership": "rented",
            "relocation_plan": "none",
            "allergy_status": "none",
            "smoker_in_household": "no",
            "monthly_budget_yen": 15000,
            "alone_time_status": "sometimes",
            "alone_time_weekly_days": 2,
            "alone_time_hours": 6.0,
            "has_existing_cat": "no",
            "has_other_pets": "no",
            "household_members": [],
            "pets": [],
        }

        # When
        response = test_client.post(
            "/api/v1/adoptions/applicants-extended", json=applicant_data
        )

        # Then
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestSearchApplicantsAPI:
    """里親希望者検索APIのテスト"""

    def test_search_applicants_partial_match_sorted_by_updated_desc(
        self, test_client, test_db, auth_headers
    ):
        """正常系: 部分一致で更新日時降順に取得できる"""
        applicant1 = Applicant(
            name="検索対象 太郎",
            contact="taro@example.com",
            name_kana="ケンサクタイショウタロウ",
            phone="090-1111-2222",
            contact_type="email",
            contact_email="taro@example.com",
        )
        applicant2 = Applicant(
            name="検索対象 花子",
            contact="hanako@example.com",
            name_kana="ケンサクタイショウハナコ",
            phone="090-3333-4444",
            contact_type="email",
            contact_email="hanako@example.com",
        )
        test_db.add_all([applicant1, applicant2])
        test_db.commit()
        test_db.refresh(applicant1)
        test_db.refresh(applicant2)

        applicant1.contact = "taro-updated@example.com"
        test_db.commit()
        test_db.refresh(applicant1)

        response = test_client.get(
            "/api/v1/adoptions/applicants-extended/search?q=検索対象",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        ids = [item["id"] for item in data]
        assert ids[:2] == [applicant1.id, applicant2.id]

    def test_search_applicants_phone_normalized_partial_match(
        self, test_client, test_db, auth_headers
    ):
        """正常系: 電話番号はハイフン有無を吸収して部分一致検索できる"""
        applicant = Applicant(
            name="電話検索テスト",
            contact="phone@example.com",
            name_kana="デンワケンサクテスト",
            phone="080-9999-8888",
            contact_type="line",
            contact_line_id="phone-line",
        )
        test_db.add(applicant)
        test_db.commit()

        response = test_client.get(
            "/api/v1/adoptions/applicants-extended/search?q=99998888",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == applicant.id

    def test_search_applicants_short_query_returns_empty(
        self, test_client, test_db, auth_headers
    ):
        """正常系: 1文字検索は結果を返さない"""
        applicant = Applicant(name="短文字テスト", contact="short@example.com")
        test_db.add(applicant)
        test_db.commit()

        response = test_client.get(
            "/api/v1/adoptions/applicants-extended/search?q=あ",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []


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
            f"/api/v1/adoptions/applicants-extended/{applicant.id}",
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
            "/api/v1/adoptions/applicants-extended/99999", headers=auth_headers
        )

        # Then
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestUpdateApplicantAPI:
    """里親希望者更新API（拡張版）のテスト"""

    def test_update_applicant_with_valid_data_returns_200(
        self, test_client, test_db, auth_headers
    ):
        """正常系: 有効なデータで里親希望者を更新できる"""
        # Given
        applicant = Applicant(name="山田太郎", contact="090-1234-5678")
        test_db.add(applicant)
        test_db.commit()
        test_db.refresh(applicant)

        update_data = {"monthly_budget_yen": 20000}

        # When
        response = test_client.put(
            f"/api/v1/adoptions/applicants-extended/{applicant.id}",
            json=update_data,
            headers=auth_headers,
        )

        # Then
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["monthly_budget_yen"] == 20000
        assert data["name"] == "山田太郎"  # 変更されていない

    def test_update_applicant_with_nonexistent_id_returns_404(
        self, test_client, auth_headers
    ):
        """異常系: 存在しないIDで404エラー"""
        # Given
        update_data = {"monthly_budget_yen": 20000}

        # When
        response = test_client.put(
            "/api/v1/adoptions/applicants-extended/99999",
            json=update_data,
            headers=auth_headers,
        )

        # Then
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestConsultationAPI:
    """里親相談APIのテスト"""

    def test_create_consultation_returns_201(self, test_client, auth_headers):
        payload = {
            "name_kana": "サトウハナコ",
            "name": "佐藤花子",
            "phone": "090-1111-2222",
            "contact_type": "line",
            "contact_line_id": "sato_line",
            "contact_email": None,
            "consultation_note": "まずは相談したいです。",
        }

        response = test_client.post(
            "/api/v1/adoptions/consultations",
            json=payload,
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == "佐藤花子"
        assert data["status"] == "open"

    def test_list_consultations_returns_200(self, test_client, test_db, auth_headers):
        test_db.add(
            AdoptionConsultation(
                name_kana="ヤマダタロウ",
                name="山田太郎",
                phone="09000000000",
                contact_type="email",
                contact_email="yamada@example.com",
                consultation_note="相談メモ",
                status="open",
            )
        )
        test_db.commit()

        response = test_client.get(
            "/api/v1/adoptions/consultations", headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "山田太郎"

    def test_create_applicant_from_consultation_sets_converted(
        self, test_client, test_db, auth_headers
    ):
        consultation = AdoptionConsultation(
            name_kana="タナカハナコ",
            name="田中花子",
            phone="08012345678",
            contact_type="email",
            contact_email="tanaka@example.com",
            consultation_note="相談内容を引き継ぎたい",
            status="open",
        )
        test_db.add(consultation)
        test_db.commit()
        test_db.refresh(consultation)

        applicant_data = {
            "name_kana": "タナカハナコ",
            "name": "田中花子",
            "age": 31,
            "phone": "080-1234-5678",
            "contact_type": "email",
            "contact_email": "tanaka@example.com",
            "contact_line_id": None,
            "postal_code": "150-0001",
            "address1": "東京都渋谷区神宮前1-2-3",
            "address2": "サンプルマンション101",
            "occupation": "company_employee",
            "occupation_other": None,
            "desired_cat_alias": "未定",
            "emergency_relation": "parents",
            "emergency_relation_other": None,
            "emergency_name": "田中一郎",
            "emergency_phone": "090-9876-5432",
            "family_intent": "all_positive",
            "pet_permission": "allowed",
            "pet_limit_type": "limited",
            "pet_limit_count": 2,
            "housing_type": "apartment",
            "housing_ownership": "rented",
            "relocation_plan": "none",
            "relocation_time_note": None,
            "relocation_cat_plan": None,
            "allergy_status": "none",
            "smoker_in_household": "no",
            "monthly_budget_yen": 15000,
            "alone_time_status": "sometimes",
            "alone_time_weekly_days": 2,
            "alone_time_hours": 6.0,
            "has_existing_cat": "no",
            "has_other_pets": "no",
            "household_members": [],
            "pets": [],
            "source_consultation_id": consultation.id,
        }

        response = test_client.post(
            "/api/v1/adoptions/applicants-extended",
            json=applicant_data,
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_201_CREATED

        test_db.refresh(consultation)
        assert consultation.status == "converted"
        assert consultation.applicant_id is not None


class TestIntakeEntriesAPI:
    """受付一覧API（相談/申込統合）のテスト"""

    def test_list_intake_entries_all_merges_cross_type_by_identity(
        self, test_client, test_db, auth_headers
    ):
        """正常系: all指定で相談と申込が同一判定なら1件に統合される"""
        applicant = Applicant(
            name="同一判定太郎",
            contact="same@example.com",
            name_kana="ドウイツハンテイタロウ",
            phone="09011112222",
            contact_type="email",
            contact_email="same@example.com",
        )
        consultation = AdoptionConsultation(
            name_kana="ドウイツハンテイタロウ",
            name="同一判定太郎",
            phone="090-1111-2222",
            contact_type="email",
            contact_email="same@example.com",
            consultation_note="まずは相談したい",
            status="open",
        )
        test_db.add(applicant)
        test_db.add(consultation)
        test_db.commit()
        test_db.refresh(applicant)
        test_db.refresh(consultation)

        response = test_client.get(
            "/api/v1/adoptions/intake-entries?request_type=all", headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        target = [item for item in data if item["name"] == "同一判定太郎"]
        assert len(target) == 1
        assert target[0]["request_type"] == "both"
        assert target[0]["application_id"] == applicant.id
        assert target[0]["consultation_id"] == consultation.id

    def test_list_intake_entries_by_request_type_not_merged(
        self, test_client, test_db, auth_headers
    ):
        """正常系: 種別指定時は統合せず個別に返す"""
        applicant = Applicant(
            name="種別確認花子",
            contact="kind@example.com",
            name_kana="シュベツカクニンハナコ",
            phone="08099998888",
            contact_type="line",
            contact_line_id="kind-line",
        )
        consultation = AdoptionConsultation(
            name_kana="シュベツカクニンハナコ",
            name="種別確認花子",
            phone="080-9999-8888",
            contact_type="line",
            contact_line_id="kind-line",
            consultation_note="相談登録",
            status="open",
        )
        test_db.add(applicant)
        test_db.add(consultation)
        test_db.commit()

        app_response = test_client.get(
            "/api/v1/adoptions/intake-entries?request_type=application",
            headers=auth_headers,
        )
        con_response = test_client.get(
            "/api/v1/adoptions/intake-entries?request_type=consultation",
            headers=auth_headers,
        )

        assert app_response.status_code == status.HTTP_200_OK
        assert con_response.status_code == status.HTTP_200_OK

        app_data = [
            item for item in app_response.json() if item["name"] == "種別確認花子"
        ]
        con_data = [
            item for item in con_response.json() if item["name"] == "種別確認花子"
        ]
        assert len(app_data) == 1
        assert len(con_data) == 1
        assert app_data[0]["request_type"] == "application"
        assert con_data[0]["request_type"] == "consultation"


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
        """正常系: 譲渡記録登録時に猫のステータスが「ADOPTED」に更新される"""
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
        assert test_animal.status == "ADOPTED"


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

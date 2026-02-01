"""
猫一覧検索APIのテスト（Issue #88）

TDDアプローチで詳細検索機能をテスト。
"""

from datetime import date

import pytest
from sqlalchemy.orm import Session

from app.models import Animal


@pytest.fixture(scope="function")
def search_test_animals(test_db: Session) -> list[Animal]:
    """検索テスト用の猫データを作成

    様々なステータス・属性を持つ猫を作成し、
    フィルタリング機能のテストに使用する。
    """
    animals_data = [
        # 保護中の猫
        {
            "name": "保護猫A",
            "coat_color": "三毛",
            "tail_length": "長い",
            "status": "QUARANTINE",
            "gender": "female",
            "fiv_positive": False,
            "felv_positive": False,
            "is_sterilized": True,
            "location_type": "FACILITY",
            "age_months": 12,
        },
        # 在籍中の猫（譲渡可）
        {
            "name": "在籍猫B",
            "coat_color": "キジトラ",
            "tail_length": "長い",
            "status": "IN_CARE",
            "gender": "male",
            "fiv_positive": False,
            "felv_positive": False,
            "is_sterilized": True,
            "location_type": "FACILITY",
            "age_months": 24,
        },
        # トライアル中の猫（譲渡可）
        {
            "name": "トライアル猫C",
            "coat_color": "黒",
            "tail_length": "短い",
            "status": "TRIAL",
            "gender": "male",
            "fiv_positive": True,
            "felv_positive": False,
            "is_sterilized": True,
            "location_type": "ADOPTER_HOME",
            "age_months": 18,
        },
        # 譲渡済みの猫
        {
            "name": "譲渡済み猫D",
            "coat_color": "白",
            "tail_length": "長い",
            "status": "ADOPTED",
            "gender": "female",
            "fiv_positive": False,
            "felv_positive": False,
            "is_sterilized": True,
            "location_type": "ADOPTER_HOME",
            "age_months": 36,
        },
        # 死亡した猫
        {
            "name": "死亡猫E",
            "coat_color": "グレー",
            "tail_length": "長い",
            "status": "DECEASED",
            "gender": "male",
            "fiv_positive": False,
            "felv_positive": True,
            "is_sterilized": False,
            "location_type": "FACILITY",
            "age_months": 60,
        },
        # 預かり宅にいる猫
        {
            "name": "預かり猫F",
            "coat_color": "茶トラ",
            "tail_length": "短い",
            "status": "IN_CARE",
            "gender": "female",
            "fiv_positive": None,  # 不明
            "felv_positive": None,  # 不明
            "is_sterilized": None,  # 不明
            "location_type": "FOSTER_HOME",
            "age_months": 6,
        },
    ]

    created_animals = []
    for data in animals_data:
        animal = Animal(
            name=data["name"],
            coat_color=data["coat_color"],
            tail_length=data["tail_length"],
            status=data["status"],
            gender=data["gender"],
            fiv_positive=data.get("fiv_positive"),
            felv_positive=data.get("felv_positive"),
            is_sterilized=data.get("is_sterilized"),
            location_type=data["location_type"],
            age_months=data.get("age_months"),
            protected_at=date(2024, 1, 1),
        )
        test_db.add(animal)
        created_animals.append(animal)

    test_db.commit()

    for animal in created_animals:
        test_db.refresh(animal)

    return created_animals


class TestAnimalListStatusFilter:
    """ステータスフィルタのテスト"""

    def test_filter_by_active_status_returns_quarantine_incare_trial(
        self, test_client, test_db, auth_token, search_test_animals
    ):
        """ACTIVE指定で保護中・在籍中・トライアル中の猫のみ取得できる"""
        # When
        response = test_client.get(
            "/api/v1/animals?status=ACTIVE",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        # Then
        assert response.status_code == 200
        data = response.json()
        items = data["items"]

        # 保護中・在籍中・トライアル中の猫のみ含まれる
        statuses = {item["status"] for item in items}
        assert statuses <= {"QUARANTINE", "IN_CARE", "TRIAL"}

        # 譲渡済み・死亡は含まれない
        assert "ADOPTED" not in statuses
        assert "DECEASED" not in statuses

        # 件数確認（fixture: 保護猫A, 在籍猫B, トライアル猫C, 預かり猫F = 4件）
        active_names = {item["name"] for item in items}
        assert "保護猫A" in active_names
        assert "在籍猫B" in active_names
        assert "トライアル猫C" in active_names
        assert "預かり猫F" in active_names
        assert "譲渡済み猫D" not in active_names
        assert "死亡猫E" not in active_names

    def test_filter_by_single_status_quarantine(
        self, test_client, test_db, auth_token, search_test_animals
    ):
        """QUARANTINE指定で保護中の猫のみ取得できる"""
        response = test_client.get(
            "/api/v1/animals?status=QUARANTINE",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        items = data["items"]

        for item in items:
            assert item["status"] == "QUARANTINE"

    def test_filter_by_adopted_status(
        self, test_client, test_db, auth_token, search_test_animals
    ):
        """ADOPTED指定で譲渡済みの猫のみ取得できる"""
        response = test_client.get(
            "/api/v1/animals?status=ADOPTED",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        items = data["items"]

        for item in items:
            assert item["status"] == "ADOPTED"

    def test_filter_by_deceased_status(
        self, test_client, test_db, auth_token, search_test_animals
    ):
        """DECEASED指定で死亡の猫のみ取得できる"""
        response = test_client.get(
            "/api/v1/animals?status=DECEASED",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        items = data["items"]

        for item in items:
            assert item["status"] == "DECEASED"

    def test_no_status_filter_returns_all(
        self, test_client, test_db, auth_token, search_test_animals
    ):
        """ステータス未指定で全件取得できる"""
        response = test_client.get(
            "/api/v1/animals",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        items = data["items"]

        # 全ステータスが含まれる可能性がある
        statuses = {item["status"] for item in items}
        # 少なくともACTIVEのステータスは含まれる
        assert len(statuses) >= 1


class TestAnimalListAdvancedFilters:
    """詳細検索フィルタのテスト"""

    def test_filter_by_gender_female(
        self, test_client, test_db, auth_token, search_test_animals
    ):
        """性別でフィルタリングできる（メス）"""
        response = test_client.get(
            "/api/v1/animals?gender=female",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        items = data["items"]

        for item in items:
            assert item["gender"] == "female"

    def test_filter_by_gender_male(
        self, test_client, test_db, auth_token, search_test_animals
    ):
        """性別でフィルタリングできる（オス）"""
        response = test_client.get(
            "/api/v1/animals?gender=male",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        items = data["items"]

        for item in items:
            assert item["gender"] == "male"

    def test_filter_by_fiv_negative(
        self, test_client, test_db, auth_token, search_test_animals
    ):
        """FIV陰性でフィルタリングできる"""
        response = test_client.get(
            "/api/v1/animals?fiv=negative",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        items = data["items"]

        for item in items:
            assert item["fiv_positive"] is False

    def test_filter_by_fiv_positive(
        self, test_client, test_db, auth_token, search_test_animals
    ):
        """FIV陽性でフィルタリングできる"""
        response = test_client.get(
            "/api/v1/animals?fiv=positive",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        items = data["items"]

        for item in items:
            assert item["fiv_positive"] is True

    def test_filter_by_fiv_unknown(
        self, test_client, test_db, auth_token, search_test_animals
    ):
        """FIV不明でフィルタリングできる"""
        response = test_client.get(
            "/api/v1/animals?fiv=unknown",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        items = data["items"]

        for item in items:
            assert item["fiv_positive"] is None

    def test_filter_by_felv_negative(
        self, test_client, test_db, auth_token, search_test_animals
    ):
        """FeLV陰性でフィルタリングできる"""
        response = test_client.get(
            "/api/v1/animals?felv=negative",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        items = data["items"]

        for item in items:
            assert item["felv_positive"] is False

    def test_filter_by_felv_positive(
        self, test_client, test_db, auth_token, search_test_animals
    ):
        """FeLV陽性でフィルタリングできる"""
        response = test_client.get(
            "/api/v1/animals?felv=positive",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        items = data["items"]

        for item in items:
            assert item["felv_positive"] is True

    def test_filter_by_is_sterilized_true(
        self, test_client, test_db, auth_token, search_test_animals
    ):
        """避妊・去勢済みでフィルタリングできる"""
        response = test_client.get(
            "/api/v1/animals?is_sterilized=true",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        items = data["items"]

        for item in items:
            assert item["is_sterilized"] is True

    def test_filter_by_is_sterilized_false(
        self, test_client, test_db, auth_token, search_test_animals
    ):
        """避妊・去勢未でフィルタリングできる"""
        response = test_client.get(
            "/api/v1/animals?is_sterilized=false",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        items = data["items"]

        for item in items:
            assert item["is_sterilized"] is False

    def test_filter_by_is_sterilized_unknown(
        self, test_client, test_db, auth_token, search_test_animals
    ):
        """避妊・去勢不明でフィルタリングできる"""
        response = test_client.get(
            "/api/v1/animals?is_sterilized=unknown",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        items = data["items"]

        for item in items:
            assert item["is_sterilized"] is None

    def test_filter_by_location_type_facility(
        self, test_client, test_db, auth_token, search_test_animals
    ):
        """場所（施設）でフィルタリングできる"""
        response = test_client.get(
            "/api/v1/animals?location_type=FACILITY",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        items = data["items"]

        for item in items:
            assert item["location_type"] == "FACILITY"

    def test_filter_by_location_type_foster_home(
        self, test_client, test_db, auth_token, search_test_animals
    ):
        """場所（預かり宅）でフィルタリングできる"""
        response = test_client.get(
            "/api/v1/animals?location_type=FOSTER_HOME",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        items = data["items"]

        for item in items:
            assert item["location_type"] == "FOSTER_HOME"

    def test_filter_by_is_ready_for_adoption_true(
        self, test_client, test_db, auth_token, search_test_animals
    ):
        """譲渡可でフィルタリングできる（IN_CARE or TRIALのみ）"""
        response = test_client.get(
            "/api/v1/animals?is_ready_for_adoption=true",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        items = data["items"]

        for item in items:
            assert item["status"] in ["IN_CARE", "TRIAL"]

    def test_filter_by_is_ready_for_adoption_false(
        self, test_client, test_db, auth_token, search_test_animals
    ):
        """譲渡不可でフィルタリングできる（IN_CARE/TRIAL以外）"""
        response = test_client.get(
            "/api/v1/animals?is_ready_for_adoption=false",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        items = data["items"]

        for item in items:
            assert item["status"] not in ["IN_CARE", "TRIAL"]

    def test_filter_by_felv_unknown(
        self, test_client, test_db, auth_token, search_test_animals
    ):
        """FeLV不明でフィルタリングできる"""
        response = test_client.get(
            "/api/v1/animals?felv=unknown",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        items = data["items"]

        for item in items:
            assert item["felv_positive"] is None


class TestAnimalListCombinedFilters:
    """複合フィルタのテスト"""

    def test_filter_active_and_female(
        self, test_client, test_db, auth_token, search_test_animals
    ):
        """ACTIVE + メスで絞り込みできる"""
        response = test_client.get(
            "/api/v1/animals?status=ACTIVE&gender=female",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        items = data["items"]

        for item in items:
            assert item["status"] in ["QUARANTINE", "IN_CARE", "TRIAL"]
            assert item["gender"] == "female"

    def test_filter_active_and_fiv_negative_and_sterilized(
        self, test_client, test_db, auth_token, search_test_animals
    ):
        """ACTIVE + FIV陰性 + 避妊・去勢済みで絞り込みできる"""
        response = test_client.get(
            "/api/v1/animals?status=ACTIVE&fiv=negative&is_sterilized=true",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        items = data["items"]

        for item in items:
            assert item["status"] in ["QUARANTINE", "IN_CARE", "TRIAL"]
            assert item["fiv_positive"] is False
            assert item["is_sterilized"] is True

    def test_filter_ready_for_adoption_and_fiv_negative(
        self, test_client, test_db, auth_token, search_test_animals
    ):
        """譲渡可 + FIV陰性で絞り込みできる"""
        response = test_client.get(
            "/api/v1/animals?is_ready_for_adoption=true&fiv=negative",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        items = data["items"]

        for item in items:
            assert item["status"] in ["IN_CARE", "TRIAL"]
            assert item["fiv_positive"] is False

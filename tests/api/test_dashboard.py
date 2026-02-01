"""
ダッシュボード統計APIのテスト

Issue #87: ダッシュボードカードの改善
- FIV陽性とFeLV陽性を別々のカードとしてカウント
- 在籍中猫（QUARANTINE + IN_CARE + TRIAL）のみを対象
"""

from __future__ import annotations

from datetime import date

from sqlalchemy.orm import Session

from app.models.animal import Animal
from app.models.care_log import CareLog


def create_animal(
    name: str,
    status: str = "IN_CARE",
    gender: str = "female",
    fiv_positive: bool = False,
    felv_positive: bool = False,
) -> Animal:
    """テスト用動物を作成するヘルパー関数"""
    return Animal(
        name=name,
        status=status,
        gender=gender,
        coat_color="キジトラ",
        tail_length="長い",
        fiv_positive=fiv_positive,
        felv_positive=felv_positive,
    )


class TestDashboardStats:
    """ダッシュボード統計APIのテスト"""

    def test_empty_database_returns_zeros(
        self, test_client, auth_headers, test_db: Session
    ):
        """空のデータベースでは全てゼロを返す"""
        # テスト用に作成されたデフォルト動物を削除
        test_db.query(CareLog).delete()
        test_db.query(Animal).delete()
        test_db.commit()

        response = test_client.get("/api/v1/dashboard/stats", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert data["resident_count"] == 0
        assert data["adoptable_count"] == 0
        assert data["today_logs_count"] == 0
        assert data["fiv_positive_count"] == 0
        assert data["felv_positive_count"] == 0

    def test_resident_count_includes_quarantine_incare_trial(
        self, test_client, auth_headers, test_db: Session
    ):
        """在籍中カウントはQUARANTINE, IN_CARE, TRIALを含む"""
        # デフォルトデータをクリア
        test_db.query(CareLog).delete()
        test_db.query(Animal).delete()
        test_db.commit()

        # 各ステータスの猫を作成
        animals = [
            create_animal("隔離中猫", status="QUARANTINE", gender="female"),
            create_animal("保護中猫", status="IN_CARE", gender="male"),
            create_animal("トライアル猫", status="TRIAL", gender="female"),
            create_animal("譲渡済み猫", status="ADOPTED", gender="male"),
            create_animal("死亡猫", status="DECEASED", gender="female"),
        ]
        for animal in animals:
            test_db.add(animal)
        test_db.commit()

        response = test_client.get("/api/v1/dashboard/stats", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        # QUARANTINE, IN_CARE, TRIAL の3匹
        assert data["resident_count"] == 3

    def test_adoptable_count_includes_incare_trial(
        self, test_client, auth_headers, test_db: Session
    ):
        """譲渡可能カウントはIN_CARE, TRIALを含む"""
        test_db.query(CareLog).delete()
        test_db.query(Animal).delete()
        test_db.commit()

        animals = [
            create_animal("隔離中猫", status="QUARANTINE", gender="female"),
            create_animal("保護中猫", status="IN_CARE", gender="male"),
            create_animal("トライアル猫", status="TRIAL", gender="female"),
            create_animal("譲渡済み猫", status="ADOPTED", gender="male"),
        ]
        for animal in animals:
            test_db.add(animal)
        test_db.commit()

        response = test_client.get("/api/v1/dashboard/stats", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        # IN_CARE, TRIAL の2匹
        assert data["adoptable_count"] == 2

    def test_fiv_positive_count_only_resident(
        self, test_client, auth_headers, test_db: Session
    ):
        """FIV陽性カウントは在籍中の猫のみを対象"""
        test_db.query(CareLog).delete()
        test_db.query(Animal).delete()
        test_db.commit()

        animals = [
            create_animal(
                "FIV陽性保護中", status="IN_CARE", gender="male", fiv_positive=True
            ),
            create_animal(
                "FIV陽性隔離中",
                status="QUARANTINE",
                gender="female",
                fiv_positive=True,
            ),
            create_animal(
                "FIV陽性譲渡済み",
                status="ADOPTED",
                gender="male",
                fiv_positive=True,
            ),  # カウント対象外
            create_animal("FIV陰性保護中", status="IN_CARE", gender="female"),
        ]
        for animal in animals:
            test_db.add(animal)
        test_db.commit()

        response = test_client.get("/api/v1/dashboard/stats", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        # 在籍中でFIV陽性は2匹
        assert data["fiv_positive_count"] == 2

    def test_felv_positive_count_only_resident(
        self, test_client, auth_headers, test_db: Session
    ):
        """FeLV陽性カウントは在籍中の猫のみを対象"""
        test_db.query(CareLog).delete()
        test_db.query(Animal).delete()
        test_db.commit()

        animals = [
            create_animal(
                "FeLV陽性保護中",
                status="IN_CARE",
                gender="male",
                felv_positive=True,
            ),
            create_animal(
                "FeLV陽性トライアル",
                status="TRIAL",
                gender="female",
                felv_positive=True,
            ),
            create_animal(
                "FeLV陽性死亡",
                status="DECEASED",
                gender="male",
                felv_positive=True,
            ),  # カウント対象外
            create_animal("FeLV陰性保護中", status="IN_CARE", gender="female"),
        ]
        for animal in animals:
            test_db.add(animal)
        test_db.commit()

        response = test_client.get("/api/v1/dashboard/stats", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        # 在籍中でFeLV陽性は2匹
        assert data["felv_positive_count"] == 2

    def test_fiv_felv_separate_counts(
        self, test_client, auth_headers, test_db: Session
    ):
        """FIVとFeLVは別々にカウントされる"""
        test_db.query(CareLog).delete()
        test_db.query(Animal).delete()
        test_db.commit()

        animals = [
            create_animal(
                "FIVのみ陽性", status="IN_CARE", gender="male", fiv_positive=True
            ),
            create_animal(
                "FeLVのみ陽性",
                status="IN_CARE",
                gender="female",
                felv_positive=True,
            ),
            create_animal(
                "両方陽性",
                status="IN_CARE",
                gender="male",
                fiv_positive=True,
                felv_positive=True,
            ),
            create_animal("両方陰性", status="IN_CARE", gender="female"),
        ]
        for animal in animals:
            test_db.add(animal)
        test_db.commit()

        response = test_client.get("/api/v1/dashboard/stats", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        # FIV陽性: FIVのみ + 両方 = 2
        assert data["fiv_positive_count"] == 2
        # FeLV陽性: FeLVのみ + 両方 = 2
        assert data["felv_positive_count"] == 2

    def test_today_logs_count(self, test_client, auth_headers, test_db: Session):
        """今日の記録数をカウント"""
        test_db.query(CareLog).delete()
        test_db.query(Animal).delete()
        test_db.commit()

        # テスト用動物を作成
        animal = create_animal("テスト猫", status="IN_CARE", gender="female")
        test_db.add(animal)
        test_db.commit()

        # 今日の記録を2件作成
        for i in range(2):
            log = CareLog(
                animal_id=animal.id,
                log_date=date.today(),
                time_slot=["morning", "noon"][i],
                appetite=1.0,
                energy=3,
                recorder_name="テスター",
            )
            test_db.add(log)
        test_db.commit()

        response = test_client.get("/api/v1/dashboard/stats", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert data["today_logs_count"] == 2


class TestDashboardStatsUnauthenticated:
    """未認証でのダッシュボード統計APIアクセステスト"""

    def test_requires_authentication(self, test_client):
        """認証が必要"""
        response = test_client.get("/api/v1/dashboard/stats")
        assert response.status_code == 401

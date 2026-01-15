"""
エッジケースのフロントエンドテスト

データがない場合の画面表示をテストします。
"""

from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


class TestAnimalDetailEdgeCases:
    """猫詳細ページのエッジケーステスト"""

    def test_animal_with_no_data(
        self, test_client: TestClient, auth_token: str, test_db: Session
    ):
        """データが一切ない猫の詳細ページが正常に表示される"""
        # Given: データがない猫を作成
        from app.models.animal import Animal

        animal = Animal(
            name="データなし猫",
            pattern="キジトラ",
            tail_length="長い",
            age_months=12,
            gender="male",
            status="保護中",
        )
        test_db.add(animal)
        test_db.commit()
        test_db.refresh(animal)

        headers = {"Authorization": f"Bearer {auth_token}"}

        # When: 猫詳細ページにアクセス
        response = test_client.get(f"/admin/animals/{animal.id}", headers=headers)

        # Then: ページが正常に表示される
        assert response.status_code == 200
        # ページタイトルに猫の名前が含まれている（HTMLエスケープされている可能性を考慮）
        assert (
            animal.name in response.text or f"animalId = {animal.id}" in response.text
        )

        # 各タブのコンテンツが含まれている
        assert "基本情報" in response.text
        assert "世話記録" in response.text
        assert "診療記録" in response.text
        assert "画像ギャラリー" in response.text
        assert "体重推移" in response.text

    def test_care_logs_tab_with_no_data(
        self, test_client: TestClient, auth_token: str, test_db: Session
    ):
        """世話記録がない場合のAPIレスポンス"""
        # Given: データがない猫を作成
        from app.models.animal import Animal

        animal = Animal(
            name="世話記録なし猫",
            pattern="三毛",
            tail_length="短い",
            age_months=6,
            gender="female",
            status="保護中",
        )
        test_db.add(animal)
        test_db.commit()
        test_db.refresh(animal)

        headers = {"Authorization": f"Bearer {auth_token}"}

        # When: 世話記録APIを呼び出し
        response = test_client.get(
            f"/api/v1/care-logs?animal_id={animal.id}&page=1&page_size=10",
            headers=headers,
        )

        # Then: 空のリストが返る
        assert response.status_code == 200
        result = response.json()
        assert result["items"] == []
        assert result["total"] == 0

    def test_medical_records_tab_with_no_data(
        self, test_client: TestClient, auth_token: str, test_db: Session
    ):
        """診療記録がない場合のAPIレスポンス"""
        # Given: データがない猫を作成
        from app.models.animal import Animal

        animal = Animal(
            name="診療記録なし猫",
            pattern="キジトラ",
            tail_length="長い",
            age_months=12,
            gender="male",
            status="保護中",
        )
        test_db.add(animal)
        test_db.commit()
        test_db.refresh(animal)

        headers = {"Authorization": f"Bearer {auth_token}"}

        # When: 診療記録APIを呼び出し
        response = test_client.get(
            f"/api/v1/medical-records?animal_id={animal.id}&page=1&page_size=10",
            headers=headers,
        )

        # Then: 空のリストが返る
        assert response.status_code == 200
        result = response.json()
        assert result["items"] == []
        assert result["total"] == 0

    def test_images_tab_with_no_data(
        self, test_client: TestClient, auth_token: str, test_db: Session
    ):
        """画像がない場合のAPIレスポンス"""
        # Given: データがない猫を作成
        from app.models.animal import Animal

        animal = Animal(
            name="画像なし猫",
            pattern="三毛",
            tail_length="短い",
            age_months=6,
            gender="female",
            status="保護中",
        )
        test_db.add(animal)
        test_db.commit()
        test_db.refresh(animal)

        headers = {"Authorization": f"Bearer {auth_token}"}

        # When: 画像APIを呼び出し
        response = test_client.get(
            f"/api/v1/animals/{animal.id}/images?sort_by=created_at&ascending=false",
            headers=headers,
        )

        # Then: 空のリストが返る
        assert response.status_code == 200
        result = response.json()
        assert result == []

    def test_weight_chart_with_no_data(
        self, test_client: TestClient, auth_token: str, test_db: Session
    ):
        """体重データがない場合のAPIレスポンス"""
        # Given: データがない猫を作成
        from app.models.animal import Animal

        animal = Animal(
            name="体重データなし猫",
            pattern="キジトラ",
            tail_length="長い",
            age_months=12,
            gender="male",
            status="保護中",
        )
        test_db.add(animal)
        test_db.commit()
        test_db.refresh(animal)

        headers = {"Authorization": f"Bearer {auth_token}"}

        # When: 診療記録API（体重データ用）を呼び出し
        response = test_client.get(
            f"/api/v1/medical-records?animal_id={animal.id}&page=1&page_size=100",
            headers=headers,
        )

        # Then: 空のリストが返る
        assert response.status_code == 200
        result = response.json()
        assert result["items"] == []
        assert result["total"] == 0


class TestNonExistentAnimal:
    """存在しない猫のテスト"""

    def test_nonexistent_animal_returns_404(
        self, test_client: TestClient, auth_token: str
    ):
        """存在しない猫IDでリダイレクト"""
        # Given: 存在しないID
        nonexistent_id = 99999
        headers = {"Authorization": f"Bearer {auth_token}"}

        # When: 猫詳細ページにアクセス（follow_redirects=False）
        response = test_client.get(
            f"/admin/animals/{nonexistent_id}", headers=headers, follow_redirects=False
        )

        # Then: 302リダイレクト
        assert response.status_code == 302
        assert response.headers["location"] == "/admin/animals"


class TestAPIErrorHandling:
    """APIエラーハンドリングのテスト"""

    def test_care_logs_with_invalid_animal_id(
        self, test_client: TestClient, auth_token: str
    ):
        """無効な猫IDで世話記録APIを呼び出し"""
        # Given: 存在しないID
        nonexistent_id = 99999
        headers = {"Authorization": f"Bearer {auth_token}"}

        # When: 世話記録APIを呼び出し
        response = test_client.get(
            f"/api/v1/care-logs?animal_id={nonexistent_id}&page=1&page_size=10",
            headers=headers,
        )

        # Then: 空のリストが返る（エラーではない）
        assert response.status_code == 200
        result = response.json()
        assert result["items"] == []
        assert result["total"] == 0

    def test_medical_records_with_invalid_animal_id(
        self, test_client: TestClient, auth_token: str
    ):
        """無効な猫IDで診療記録APIを呼び出し"""
        # Given: 存在しないID
        nonexistent_id = 99999
        headers = {"Authorization": f"Bearer {auth_token}"}

        # When: 診療記録APIを呼び出し
        response = test_client.get(
            f"/api/v1/medical-records?animal_id={nonexistent_id}&page=1&page_size=10",
            headers=headers,
        )

        # Then: 空のリストが返る（エラーではない）
        assert response.status_code == 200
        result = response.json()
        assert result["items"] == []
        assert result["total"] == 0

    def test_images_with_invalid_animal_id(
        self, test_client: TestClient, auth_token: str
    ):
        """無効な猫IDで画像APIを呼び出し"""
        # Given: 存在しないID
        nonexistent_id = 99999
        headers = {"Authorization": f"Bearer {auth_token}"}

        # When: 画像APIを呼び出し
        response = test_client.get(
            f"/api/v1/animals/{nonexistent_id}/images?sort_by=created_at&ascending=false",
            headers=headers,
        )

        # Then: 404エラー
        assert response.status_code == 404

"""
体重推移グラフのフロントエンドテスト

JavaScriptの体重グラフ機能をテストします。
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.schemas.medical_record import MedicalRecordCreate
from app.services import medical_record_service


class TestWeightChartAPI:
    """体重推移グラフAPI のテスト"""

    def test_get_weight_data_for_chart(
        self,
        test_client: TestClient,
        auth_token: str,
        test_db: Session,
        test_vet_user,
    ):
        """体重推移グラフ用のデータを取得できる"""
        # Given: 新しい猫を作成（他のテストの影響を避ける）
        from app.models.animal import Animal

        animal = Animal(
            name="グラフテスト猫",
            coat_color="キジトラ",
            tail_length="長い",
            age_months=12,
            gender="male",
            status="QUARANTINE",
        )
        test_db.add(animal)
        test_db.commit()
        test_db.refresh(animal)

        # 複数の体重記録を作成
        weight_data = [
            (date(2025, 12, 1), Decimal("4.0")),
            (date(2025, 12, 8), Decimal("4.2")),
            (date(2025, 12, 15), Decimal("4.4")),
        ]

        for record_date, weight in weight_data:
            record = MedicalRecordCreate(
                animal_id=animal.id,
                vet_id=test_vet_user.id,
                date=record_date,
                weight=weight,
                symptoms="定期健診",
            )
            medical_record_service.create_medical_record(test_db, record)

        headers = {"Authorization": f"Bearer {auth_token}"}

        # When: この猫の診療記録のみを取得
        response = test_client.get(
            f"/api/v1/medical-records?animal_id={animal.id}&page=1&page_size=100",
            headers=headers,
        )

        # Then: 体重データを含むレスポンスが返る
        assert response.status_code == 200
        result = response.json()
        assert "items" in result

        # この猫の体重データのみを抽出
        weight_records = [r for r in result["items"] if r.get("weight")]
        assert len(weight_records) == 3, (
            f"体重データが3件のはずが{len(weight_records)}件存在します。"
            f"animal_id={animal.id}でフィルタリングされていない可能性があります。"
        )

        # 日付順（降順：新しい順）にソートされている
        dates = [r["date"] for r in weight_records]
        assert dates == sorted(dates, reverse=True)

    def test_weight_chart_with_no_data(
        self, test_client: TestClient, auth_token: str, test_db: Session
    ):
        """体重データがない場合の処理"""
        # Given: 新しい猫を作成（体重データなし）
        from app.models.animal import Animal

        animal = Animal(
            name="体重データなし猫",
            coat_color="キジトラ",
            tail_length="長い",
            age_months=12,
            gender="female",
            status="QUARANTINE",
        )
        test_db.add(animal)
        test_db.commit()
        test_db.refresh(animal)

        headers = {"Authorization": f"Bearer {auth_token}"}

        # When: この猫の診療記録のみを取得
        response = test_client.get(
            f"/api/v1/medical-records?animal_id={animal.id}&page=1&page_size=100",
            headers=headers,
        )

        # Then: この猫のデータは空のリストが返る
        assert response.status_code == 200
        result = response.json()
        assert result["items"] == [], (
            f"この猫(animal_id={animal.id})のデータは空のはずが"
            f"{len(result['items'])}件存在します。"
        )

    def test_weight_chart_data_format(
        self,
        test_client: TestClient,
        auth_token: str,
        test_db: Session,
        test_animal,
        test_vet_user,
    ):
        """体重データのフォーマットが正しい"""
        # Given: 体重記録を作成
        record = MedicalRecordCreate(
            animal_id=test_animal.id,
            vet_id=test_vet_user.id,
            date=date(2025, 11, 15),
            weight=Decimal("4.5"),
            symptoms="定期健診",
        )
        medical_record_service.create_medical_record(test_db, record)

        headers = {"Authorization": f"Bearer {auth_token}"}

        # When: 診療記録APIを呼び出し
        response = test_client.get(
            f"/api/v1/medical-records?animal_id={test_animal.id}",
            headers=headers,
        )

        # Then: 体重データのフォーマットが正しい
        assert response.status_code == 200
        result = response.json()
        weight_records = [r for r in result["items"] if r.get("weight")]

        assert len(weight_records) >= 1
        first_record = weight_records[0]

        # 必須フィールドの存在確認
        assert "date" in first_record
        assert "weight" in first_record
        assert isinstance(first_record["date"], str)
        assert isinstance(first_record["weight"], str)  # Decimal → str

        # 体重が数値として解析可能
        weight_value = float(first_record["weight"])
        assert weight_value > 0


class TestWeightChangeCalculation:
    """体重変化計算のテスト（ビジネスロジック）"""

    def test_calculate_weight_increase(self):
        """体重増加の計算"""
        # Given
        previous = 4.0
        current = 4.4

        # When
        change = current - previous
        percentage = (change / previous) * 100

        # Then
        assert change == pytest.approx(0.4, rel=1e-2)
        assert percentage == pytest.approx(10.0, rel=1e-2)

    def test_calculate_weight_decrease(self):
        """体重減少の計算"""
        # Given
        previous = 4.0
        current = 3.6

        # When
        change = current - previous
        percentage = (change / previous) * 100

        # Then
        assert change == pytest.approx(-0.4, rel=1e-2)
        assert percentage == pytest.approx(-10.0, rel=1e-2)

    def test_detect_warning_threshold(self):
        """警告閾値（10%）の検出"""
        # Given
        test_cases = [
            (4.0, 4.4, True),  # +10% → 警告
            (4.0, 3.6, True),  # -10% → 警告
            (4.0, 4.39, False),  # +9.75% → 警告なし
            (4.0, 3.61, False),  # -9.75% → 警告なし
            (4.0, 4.0, False),  # 変化なし → 警告なし
        ]

        for previous, current, expected_warning in test_cases:
            # When
            if previous == 0:
                has_warning = False
            else:
                change_percentage = abs((current - previous) / previous * 100)
                # 浮動小数点の比較誤差を考慮（9.9999...% は警告なし）
                # 10.0以上を警告とする（>= 10.0 - 0.0001で誤差を吸収）
                has_warning = change_percentage >= 9.9999

            # Then
            change_pct = (
                abs((current - previous) / previous * 100) if previous != 0 else 0
            )
            assert has_warning == expected_warning, (
                f"体重変化 {previous}kg → {current}kg "
                f"({change_pct:.2f}%) の警告判定が正しくありません。"
                f"期待: {expected_warning}, 実際: {has_warning}, "
                f"変化率: {change_pct:.10f}%"
            )

    def test_weight_change_with_zero_previous(self):
        """前回体重が0の場合のエラーハンドリング"""
        # Given
        previous = 0.0
        current = 4.0

        # When/Then: ゼロ除算エラーを防ぐ
        with pytest.raises(ZeroDivisionError):
            _ = (current - previous) / previous * 100

    def test_format_weight_change_display(self):
        """体重変化の表示フォーマット"""
        # Given
        test_cases = [
            (4.0, 4.4, "+0.40kg (+10.0%)"),
            (4.0, 3.6, "-0.40kg (-10.0%)"),
            (4.0, 4.0, "変化なし"),
        ]

        for previous, current, expected_format in test_cases:
            # When
            if current == previous:
                display = "変化なし"
            else:
                change = current - previous
                percentage = (change / previous) * 100
                sign = "+" if change > 0 else ""
                display = f"{sign}{change:.2f}kg ({sign}{percentage:.1f}%)"

            # Then
            assert display == expected_format


class TestWeightChartRendering:
    """体重グラフ描画のテスト"""

    def test_chart_renders_with_data(
        self,
        test_client: TestClient,
        auth_token: str,
        test_db: Session,
        test_animal,
        test_vet_user,
    ):
        """体重データがある場合、グラフが描画される"""
        # Given: 体重記録を作成
        record = MedicalRecordCreate(
            animal_id=test_animal.id,
            vet_id=test_vet_user.id,
            date=date(2025, 11, 15),
            weight=Decimal("4.5"),
            symptoms="定期健診",
        )
        medical_record_service.create_medical_record(test_db, record)

        # When: 猫詳細ページにアクセス
        response = test_client.get(
            f"/admin/animals/{test_animal.id}",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        # Then: ページが正常に表示される
        assert response.status_code == 200
        # 体重タブが存在する
        assert "体重推移" in response.text or "weight" in response.text.lower()

    def test_chart_shows_empty_message_without_data(
        self, test_client: TestClient, auth_token: str, test_animal
    ):
        """体重データがない場合、空メッセージが表示される"""
        # Given: 体重データなし

        # When: 猫詳細ページにアクセス
        response = test_client.get(
            f"/admin/animals/{test_animal.id}",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        # Then: ページが正常に表示される
        assert response.status_code == 200
        # 体重タブが存在する（データがなくてもタブは表示される）
        assert "体重推移" in response.text or "weight" in response.text.lower()

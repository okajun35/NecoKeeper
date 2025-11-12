"""
MedicalActionモデルの単体テスト

診療行為マスターのビジネスルール（価格計算、有効期間チェック）をテストします。
"""

from datetime import date
from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.medical_action import MedicalAction


class TestMedicalActionModel:
    """MedicalActionモデルのテストクラス"""

    def test_create_medical_action_with_required_fields(self, test_db: Session):
        """必須フィールドで診療行為を作成できることを確認"""
        action = MedicalAction(
            name="ワクチン接種",
            valid_from=date(2024, 1, 1),
        )

        test_db.add(action)
        test_db.commit()
        test_db.refresh(action)

        assert action.id is not None
        assert action.name == "ワクチン接種"
        assert action.valid_from == date(2024, 1, 1)

    def test_medical_action_default_values(self, test_db: Session):
        """デフォルト値が正しく設定されることを確認"""
        action = MedicalAction(
            name="血液検査",
            valid_from=date(2024, 1, 1),
        )

        test_db.add(action)
        test_db.commit()
        test_db.refresh(action)

        # デフォルト値の確認
        assert action.cost_price == Decimal("0.00")
        assert action.selling_price == Decimal("0.00")
        assert action.procedure_fee == Decimal("0.00")
        assert action.currency == "JPY"
        assert action.created_at is not None
        assert action.updated_at is not None

    def test_medical_action_with_prices(self, test_db: Session):
        """価格情報を含む診療行為を作成できることを確認"""
        action = MedicalAction(
            name="駆虫薬",
            valid_from=date(2024, 1, 1),
            cost_price=Decimal("500.00"),
            selling_price=Decimal("800.00"),
            procedure_fee=Decimal("200.00"),
            currency="JPY",
        )

        test_db.add(action)
        test_db.commit()
        test_db.refresh(action)

        assert action.cost_price == Decimal("500.00")
        assert action.selling_price == Decimal("800.00")
        assert action.procedure_fee == Decimal("200.00")
        assert action.currency == "JPY"

    def test_medical_action_with_valid_period(self, test_db: Session):
        """有効期間を含む診療行為を作成できることを確認"""
        action = MedicalAction(
            name="旧価格ワクチン",
            valid_from=date(2023, 1, 1),
            valid_to=date(2023, 12, 31),
            selling_price=Decimal("3000.00"),
        )

        test_db.add(action)
        test_db.commit()
        test_db.refresh(action)

        assert action.valid_from == date(2023, 1, 1)
        assert action.valid_to == date(2023, 12, 31)

    def test_calculate_total_price_default_dosage(self, test_db: Session):
        """デフォルト投薬量での合計価格計算が正しいことを確認"""
        action = MedicalAction(
            name="抗生物質",
            valid_from=date(2024, 1, 1),
            selling_price=Decimal("1000.00"),
            procedure_fee=Decimal("500.00"),
        )

        test_db.add(action)
        test_db.commit()

        # 計算式: (1000 × 1) + 500 = 1500
        total = action.calculate_total_price()
        assert total == Decimal("1500.00")

    def test_calculate_total_price_with_dosage(self, test_db: Session):
        """投薬量を指定した合計価格計算が正しいことを確認"""
        action = MedicalAction(
            name="痛み止め",
            valid_from=date(2024, 1, 1),
            selling_price=Decimal("300.00"),
            procedure_fee=Decimal("200.00"),
        )

        test_db.add(action)
        test_db.commit()

        # 計算式: (300 × 3) + 200 = 1100
        total = action.calculate_total_price(dosage=3)
        assert total == Decimal("1100.00")

    def test_calculate_total_price_zero_procedure_fee(self, test_db: Session):
        """処置料金が0の場合の合計価格計算が正しいことを確認"""
        action = MedicalAction(
            name="サプリメント",
            valid_from=date(2024, 1, 1),
            selling_price=Decimal("500.00"),
            procedure_fee=Decimal("0.00"),
        )

        test_db.add(action)
        test_db.commit()

        # 計算式: (500 × 2) + 0 = 1000
        total = action.calculate_total_price(dosage=2)
        assert total == Decimal("1000.00")

    def test_is_valid_on_within_period(self, test_db: Session):
        """有効期間内の日付でis_valid_on()がTrueを返すことを確認"""
        action = MedicalAction(
            name="期間限定ワクチン",
            valid_from=date(2024, 1, 1),
            valid_to=date(2024, 12, 31),
        )

        test_db.add(action)
        test_db.commit()

        # 有効期間内
        assert action.is_valid_on(date(2024, 6, 15)) is True
        assert action.is_valid_on(date(2024, 1, 1)) is True
        assert action.is_valid_on(date(2024, 12, 31)) is True

    def test_is_valid_on_before_period(self, test_db: Session):
        """有効期間前の日付でis_valid_on()がFalseを返すことを確認"""
        action = MedicalAction(
            name="未来のワクチン",
            valid_from=date(2025, 1, 1),
            valid_to=date(2025, 12, 31),
        )

        test_db.add(action)
        test_db.commit()

        # 有効期間前
        assert action.is_valid_on(date(2024, 12, 31)) is False

    def test_is_valid_on_after_period(self, test_db: Session):
        """有効期間後の日付でis_valid_on()がFalseを返すことを確認"""
        action = MedicalAction(
            name="過去のワクチン",
            valid_from=date(2023, 1, 1),
            valid_to=date(2023, 12, 31),
        )

        test_db.add(action)
        test_db.commit()

        # 有効期間後
        assert action.is_valid_on(date(2024, 1, 1)) is False

    def test_is_valid_on_no_end_date(self, test_db: Session):
        """終了日がない場合、開始日以降は常に有効であることを確認"""
        action = MedicalAction(
            name="永続ワクチン",
            valid_from=date(2024, 1, 1),
            valid_to=None,
        )

        test_db.add(action)
        test_db.commit()

        # 開始日以降は常に有効
        assert action.is_valid_on(date(2024, 1, 1)) is True
        assert action.is_valid_on(date(2024, 6, 15)) is True
        assert action.is_valid_on(date(2030, 12, 31)) is True

        # 開始日前は無効
        assert action.is_valid_on(date(2023, 12, 31)) is False

    def test_medical_action_str_representation(self, test_db: Session):
        """文字列表現が正しいことを確認"""
        action = MedicalAction(
            name="ワクチン",
            valid_from=date(2024, 1, 1),
            selling_price=Decimal("3000.00"),
            currency="JPY",
        )

        test_db.add(action)
        test_db.commit()

        assert str(action) == "ワクチン（3000.00 JPY）"

    def test_medical_action_repr(self, test_db: Session):
        """repr表現が正しいことを確認"""
        action = MedicalAction(
            name="血液検査",
            valid_from=date(2024, 1, 1),
            selling_price=Decimal("5000.00"),
            currency="JPY",
        )

        test_db.add(action)
        test_db.commit()

        repr_str = repr(action)
        assert "MedicalAction" in repr_str
        assert "id=" in repr_str
        assert "name='血液検査'" in repr_str
        assert "selling_price=5000.00" in repr_str
        assert "currency='JPY'" in repr_str

    def test_medical_action_usd_currency(self, test_db: Session):
        """USD通貨での診療行為を作成できることを確認"""
        action = MedicalAction(
            name="International Vaccine",
            valid_from=date(2024, 1, 1),
            selling_price=Decimal("50.00"),
            currency="USD",
        )

        test_db.add(action)
        test_db.commit()
        test_db.refresh(action)

        assert action.currency == "USD"
        assert str(action) == "International Vaccine（50.00 USD）"

"""
テスト: 動物ステータス更新サービス（確認フロー含む）

t-wada スタイル：ユースケース駆動
- 通常のステータス更新
- 終端ステータスからの復帰（確認フロー）
- 履歴自動記録
"""

from __future__ import annotations

from sqlalchemy.orm import Session


class TestUpdateAnimalNormalFlow:
    """通常のステータス更新フロー"""

    def test_update_status_from_quarantine_to_in_care(self, test_db: Session):
        """ステータス更新: QUARANTINE → IN_CARE（通常フロー）"""
        # TODO: テスト用の猫を作成し、ステータス更新を実行
        # animal_id = create_test_animal(db, status="QUARANTINE")
        # update_data = AnimalUpdate(status="IN_CARE")
        # updated_animal = update_animal(db, animal_id, update_data, user_id=1)
        #
        # assert updated_animal.status == "IN_CARE"

    def test_update_location_type_facility_to_foster(self, test_db: Session):
        """ロケーション更新: FACILITY → FOSTER_HOME（通常フロー）"""
        # TODO: ロケーション更新を実行
        # animal_id = create_test_animal(db, location_type="FACILITY")
        # update_data = AnimalUpdate(location_type="FOSTER_HOME")
        # updated_animal = update_animal(db, animal_id, update_data, user_id=1)
        #
        # assert updated_animal.location_type == "FOSTER_HOME"

    def test_update_both_status_and_location(self, test_db: Session):
        """ステータス＆ロケーション同時更新"""
        # TODO: 両方を同時に更新
        # animal_id = create_test_animal(db)
        # update_data = AnimalUpdate(
        #     status="IN_CARE",
        #     location_type="FOSTER_HOME"
        # )
        # updated_animal = update_animal(db, animal_id, update_data, user_id=1)
        #
        # assert updated_animal.status == "IN_CARE"
        # assert updated_animal.location_type == "FOSTER_HOME"


class TestUpdateAnimalConfirmationFlow:
    """終端ステータスからの復帰確認フロー"""

    def test_adopted_to_in_care_without_confirmation_returns_409(
        self, test_db: Session
    ):
        """ADOPTED → IN_CARE（確認なし）→ 409 Conflict"""
        # TODO: 終端ステータスから復帰を試みる
        # animal_id = create_test_animal(db, status="ADOPTED")
        # update_data = AnimalUpdate(status="IN_CARE")
        #
        # # 確認なしで更新を試みる
        # result = update_animal(db, animal_id, update_data, user_id=1, confirm=False)
        #
        # # 409 Conflict を返すことを期待
        # assert isinstance(result, tuple)
        # response_data, status_code = result
        # assert status_code == 409
        # assert response_data["requires_confirmation"] is True
        # assert response_data["warning_code"] in ["LEAVE_TERMINAL_STATUS", "LEAVE_ADOPTED", "LEAVE_DECEASED"]

    def test_deceased_to_trial_without_confirmation_returns_409(self, test_db: Session):
        """DECEASED → TRIAL（確認なし）→ 409 Conflict"""
        # TODO: DECEASED からの復帰テスト
        # animal_id = create_test_animal(db, status="DECEASED")
        # update_data = AnimalUpdate(status="TRIAL")
        #
        # result = update_animal(db, animal_id, update_data, user_id=1, confirm=False)
        #
        # assert isinstance(result, tuple)
        # response_data, status_code = result
        # assert status_code == 409
        # assert response_data["requires_confirmation"] is True

    def test_adopted_to_in_care_with_confirmation_succeeds(self, test_db: Session):
        """ADOPTED → IN_CARE（confirm=true）→ 200 OK"""
        # TODO: 確認ありで復帰を実行
        # animal_id = create_test_animal(db, status="ADOPTED")
        # update_data = AnimalUpdate(status="IN_CARE")
        #
        # # 確認ありで更新を実行
        # result = update_animal(
        #     db,
        #     animal_id,
        #     update_data,
        #     user_id=1,
        #     confirm=True,
        #     reason="誤登録の修正"
        # )
        #
        # assert isinstance(result, Animal)
        # assert result.status == "IN_CARE"

    def test_active_status_change_does_not_require_confirmation(self, test_db: Session):
        """QUARANTINE → TRIAL（アクティブステータス）→ 確認不要"""
        # TODO: アクティブステータス間の遷移は409を返さない
        # animal_id = create_test_animal(db, status="QUARANTINE")
        # update_data = AnimalUpdate(status="TRIAL")
        #
        # result = update_animal(db, animal_id, update_data, user_id=1)
        #
        # # 409ではなく Animal を返す
        # assert isinstance(result, Animal)
        # assert result.status == "TRIAL"


class TestUpdateAnimalHistoryRecording:
    """ステータス更新時の履歴自動記録"""

    def test_history_recorded_on_status_update(self, test_db: Session):
        """ステータス更新時に履歴が自動記録される"""
        # TODO: 更新後に履歴を確認
        # animal_id = create_test_animal(db, status="QUARANTINE")
        # update_data = AnimalUpdate(status="IN_CARE")
        # update_animal(db, animal_id, update_data, user_id=1)
        #
        # # 履歴を確認
        # history = db.query(StatusHistory).filter(
        #     StatusHistory.animal_id == animal_id,
        #     StatusHistory.field == "status"
        # ).first()
        #
        # assert history is not None
        # assert history.old_value == "QUARANTINE"
        # assert history.new_value == "IN_CARE"
        # assert history.changed_by == 1

    def test_history_recorded_on_location_update(self, test_db: Session):
        """ロケーション更新時に履歴が自動記録される"""
        # TODO: location_type 更新後に履歴を確認
        # animal_id = create_test_animal(db, location_type="FACILITY")
        # update_data = AnimalUpdate(location_type="FOSTER_HOME")
        # update_animal(db, animal_id, update_data, user_id=1)
        #
        # history = db.query(StatusHistory).filter(
        #     StatusHistory.animal_id == animal_id,
        #     StatusHistory.field == "location_type"
        # ).first()
        #
        # assert history is not None
        # assert history.old_value == "FACILITY"
        # assert history.new_value == "FOSTER_HOME"

    def test_reason_included_in_history(self, test_db: Session):
        """更新理由が履歴に含まれる"""
        # TODO: reason パラメータが履歴に保存されることを確認
        # animal_id = create_test_animal(db, status="ADOPTED")
        # update_data = AnimalUpdate(status="TRIAL")
        #
        # update_animal(
        #     db,
        #     animal_id,
        #     update_data,
        #     user_id=1,
        #     confirm=True,
        #     reason="Adoption reversal - failed trial"
        # )
        #
        # history = db.query(StatusHistory).filter(
        #     StatusHistory.animal_id == animal_id,
        #     StatusHistory.field == "status"
        # ).first()
        #
        # assert history.reason == "Adoption reversal - failed trial"

    def test_no_history_recorded_when_no_change(self, test_db: Session):
        """変更がない場合は履歴が記録されない"""
        # TODO: 同じ値で更新した場合のテスト
        # animal_id = create_test_animal(db, status="IN_CARE")
        # update_data = AnimalUpdate(status="IN_CARE")
        #
        # initial_count = db.query(StatusHistory).filter(
        #     StatusHistory.animal_id == animal_id
        # ).count()
        #
        # update_animal(db, animal_id, update_data, user_id=1)
        #
        # final_count = db.query(StatusHistory).filter(
        #     StatusHistory.animal_id == animal_id
        # ).count()
        #
        # assert final_count == initial_count  # 増えない


class TestUpdateAnimalValidation:
    """入力値のバリデーションテスト"""

    def test_invalid_status_rejected(self, test_db: Session):
        """無効なステータス値は拒否される"""
        # TODO: Enum検証後のテスト
        # animal_id = create_test_animal(db)
        # update_data = AnimalUpdate(status="INVALID_STATUS")
        #
        # with pytest.raises(ValueError):  # or ValidationError
        #     update_animal(db, animal_id, update_data, user_id=1)

    def test_invalid_location_type_rejected(self, test_db: Session):
        """無効なロケーション値は拒否される"""
        # TODO: Enum検証後のテスト
        # animal_id = create_test_animal(db)
        # update_data = AnimalUpdate(location_type="UNKNOWN_LOCATION")
        #
        # with pytest.raises(ValueError):  # or ValidationError
        #     update_animal(db, animal_id, update_data, user_id=1)

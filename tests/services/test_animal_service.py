"""
猫管理サービスのテスト

t-wada準拠のテスト設計:
- ドメインロジックの検証
- 境界値テスト
- エラーハンドリングの検証
- 副作用の検証（ステータス履歴など）
"""

from __future__ import annotations

import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.animal import Animal
from app.models.status_history import StatusHistory
from app.models.user import User
from app.schemas.animal import AnimalCreate, AnimalUpdate
from app.services import animal_service


class TestCreateAnimal:
    """猫登録のテスト"""

    def test_create_animal_success(self, test_db: Session, test_user: User):
        """正常系: 猫を登録できる"""
        # Given
        animal_data = AnimalCreate(
            name="たま",
            photo="photo.jpg",
            pattern="三毛",
            tail_length="長い",
            age="成猫",
            gender="female",
            status="保護中",
        )

        # When
        result = animal_service.create_animal(test_db, animal_data, test_user.id)

        # Then
        assert result.id is not None
        assert result.name == "たま"
        assert result.pattern == "三毛"
        assert result.status == "保護中"

        # ステータス履歴が記録されていることを確認
        history = (
            test_db.query(StatusHistory)
            .filter(StatusHistory.animal_id == result.id)
            .first()
        )
        assert history is not None
        assert history.old_status is None
        assert history.new_status == "保護中"
        assert history.changed_by == test_user.id
        assert history.reason == "初回登録"

    def test_create_animal_with_optional_fields(
        self, test_db: Session, test_user: User
    ):
        """正常系: オプションフィールド付きで猫を登録できる"""
        # Given
        animal_data = AnimalCreate(
            name="みけ",
            photo="photo.jpg",
            pattern="三毛",
            tail_length="短い",
            collar="赤い首輪",
            age="子猫",
            gender="female",
            ear_cut=True,
            features="人懐っこい",
            status="保護中",
        )

        # When
        result = animal_service.create_animal(test_db, animal_data, test_user.id)

        # Then
        assert result.collar == "赤い首輪"
        assert result.ear_cut is True
        assert result.features == "人懐っこい"

    def test_create_animal_with_minimal_fields(self, test_db: Session, test_user: User):
        """正常系: 最小限のフィールドで猫を登録できる"""
        # Given
        animal_data = AnimalCreate(
            photo="photo.jpg",
            pattern="黒",
            tail_length="長い",
            age="成猫",
            gender="male",
        )

        # When
        result = animal_service.create_animal(test_db, animal_data, test_user.id)

        # Then
        assert result.id is not None
        assert result.name is None  # オプションフィールド
        assert result.pattern == "黒"


class TestGetAnimal:
    """猫詳細取得のテスト"""

    def test_get_animal_success(self, test_db: Session, test_animal: Animal):
        """正常系: 猫の詳細を取得できる"""
        # When
        result = animal_service.get_animal(test_db, test_animal.id)

        # Then
        assert result.id == test_animal.id
        assert result.name == test_animal.name
        assert result.pattern == test_animal.pattern

    def test_get_animal_not_found(self, test_db: Session):
        """異常系: 存在しない猫IDを指定した場合"""
        # Given
        non_existent_id = 99999

        # When/Then
        with pytest.raises(HTTPException) as exc_info:
            animal_service.get_animal(test_db, non_existent_id)

        assert exc_info.value.status_code == 404
        assert f"ID {non_existent_id} の猫が見つかりません" in exc_info.value.detail

    def test_get_animal_with_all_fields(self, test_db: Session):
        """正常系: すべてのフィールドが設定された猫を取得できる"""
        # Given
        animal = Animal(
            name="フルデータ猫",
            photo="full.jpg",
            pattern="三毛",
            tail_length="長い",
            collar="青い首輪",
            age="成猫",
            gender="female",
            ear_cut=True,
            features="おとなしい",
            status="保護中",
        )
        test_db.add(animal)
        test_db.commit()
        test_db.refresh(animal)

        # When
        result = animal_service.get_animal(test_db, animal.id)

        # Then
        assert result.collar == "青い首輪"
        assert result.ear_cut is True
        assert result.features == "おとなしい"


class TestUpdateAnimal:
    """猫情報更新のテスト"""

    def test_update_animal_basic_fields(
        self, test_db: Session, test_animal: Animal, test_user: User
    ):
        """正常系: 基本フィールドを更新できる"""
        # Given
        update_data = AnimalUpdate(
            name="新しい名前",
            pattern="新しい柄",
        )

        # When
        result = animal_service.update_animal(
            test_db, test_animal.id, update_data, test_user.id
        )

        # Then
        assert result.name == "新しい名前"
        assert result.pattern == "新しい柄"
        # 更新していないフィールドは変更されない
        assert result.gender == test_animal.gender

    def test_update_animal_status_creates_history(
        self, test_db: Session, test_animal: Animal, test_user: User
    ):
        """正常系: ステータス更新時に履歴が記録される"""
        # Given
        old_status = test_animal.status
        update_data = AnimalUpdate(status="譲渡可能")

        # When
        result = animal_service.update_animal(
            test_db, test_animal.id, update_data, test_user.id
        )

        # Then
        assert result.status == "譲渡可能"

        # ステータス履歴が記録されていることを確認
        history = (
            test_db.query(StatusHistory)
            .filter(
                StatusHistory.animal_id == test_animal.id,
                StatusHistory.new_status == "譲渡可能",
            )
            .first()
        )
        assert history is not None
        assert history.old_status == old_status
        assert history.new_status == "譲渡可能"
        assert history.changed_by == test_user.id

    def test_update_animal_status_no_change_no_history(
        self, test_db: Session, test_animal: Animal, test_user: User
    ):
        """正常系: ステータスが変更されない場合は履歴を記録しない"""
        # Given
        history_count_before = (
            test_db.query(StatusHistory)
            .filter(StatusHistory.animal_id == test_animal.id)
            .count()
        )

        update_data = AnimalUpdate(name="新しい名前")

        # When
        animal_service.update_animal(test_db, test_animal.id, update_data, test_user.id)

        # Then
        history_count_after = (
            test_db.query(StatusHistory)
            .filter(StatusHistory.animal_id == test_animal.id)
            .count()
        )
        assert history_count_after == history_count_before

    def test_update_animal_not_found(self, test_db: Session, test_user: User):
        """異常系: 存在しない猫を更新しようとした場合"""
        # Given
        non_existent_id = 99999
        update_data = AnimalUpdate(name="新しい名前")

        # When/Then
        with pytest.raises(HTTPException) as exc_info:
            animal_service.update_animal(
                test_db, non_existent_id, update_data, test_user.id
            )

        assert exc_info.value.status_code == 404

    def test_update_animal_partial_update(
        self, test_db: Session, test_animal: Animal, test_user: User
    ):
        """正常系: 一部のフィールドのみ更新できる"""
        # Given
        original_pattern = test_animal.pattern
        update_data = AnimalUpdate(name="部分更新")

        # When
        result = animal_service.update_animal(
            test_db, test_animal.id, update_data, test_user.id
        )

        # Then
        assert result.name == "部分更新"
        assert result.pattern == original_pattern  # 変更されていない


class TestDeleteAnimal:
    """猫削除のテスト"""

    def test_delete_animal_success(self, test_db: Session, test_animal: Animal):
        """正常系: 猫を削除できる"""
        # Given
        animal_id = test_animal.id

        # When
        animal_service.delete_animal(test_db, animal_id)

        # Then
        deleted_animal = test_db.query(Animal).filter(Animal.id == animal_id).first()
        assert deleted_animal is None

    def test_delete_animal_not_found(self, test_db: Session):
        """異常系: 存在しない猫を削除しようとした場合"""
        # Given
        non_existent_id = 99999

        # When/Then
        with pytest.raises(HTTPException) as exc_info:
            animal_service.delete_animal(test_db, non_existent_id)

        assert exc_info.value.status_code == 404


class TestListAnimals:
    """猫一覧取得のテスト"""

    def test_list_animals_default_pagination(
        self, test_db: Session, test_animals_bulk: list[Animal]
    ):
        """正常系: デフォルトのページネーションで一覧を取得できる"""
        # When
        result = animal_service.list_animals(test_db)

        # Then
        assert len(result.items) <= 20  # デフォルトのpage_size
        # test_animals_bulk + test_animalフィクスチャの1匹
        assert result.total >= len(test_animals_bulk)
        assert result.page == 1
        assert result.page_size == 20

    def test_list_animals_custom_pagination(
        self, test_db: Session, test_animals_bulk: list[Animal]
    ):
        """正常系: カスタムページネーションで一覧を取得できる"""
        # When
        result = animal_service.list_animals(test_db, page=2, page_size=5)

        # Then
        assert len(result.items) <= 5
        assert result.page == 2
        assert result.page_size == 5

    def test_list_animals_with_status_filter(
        self, test_db: Session, test_animals_bulk: list[Animal]
    ):
        """正常系: ステータスフィルターで絞り込める"""
        # Given
        status_filter = "保護中"

        # When
        result = animal_service.list_animals(test_db, status_filter=status_filter)

        # Then
        assert all(animal.status == status_filter for animal in result.items)

    def test_list_animals_with_nonexistent_status(self, test_db: Session):
        """正常系: 存在しないステータスでフィルターした場合"""
        # Given
        status_filter = "存在しないステータス"

        # When
        result = animal_service.list_animals(test_db, status_filter=status_filter)

        # Then
        assert len(result.items) == 0
        assert result.total == 0
        assert result.total_pages == 0

    def test_list_animals_total_pages_calculation(
        self, test_db: Session, test_animals_bulk: list[Animal]
    ):
        """正常系: 総ページ数が正しく計算される"""
        # Given
        page_size = 3
        expected_total_pages = (len(test_animals_bulk) + page_size - 1) // page_size

        # When
        result = animal_service.list_animals(test_db, page_size=page_size)

        # Then
        assert result.total_pages == expected_total_pages


class TestSearchAnimals:
    """猫検索のテスト"""

    def test_search_animals_by_name(
        self, test_db: Session, test_animals_bulk: list[Animal]
    ):
        """正常系: 名前で検索できる"""
        # Given
        search_query = test_animals_bulk[0].name[:3]  # 名前の最初の3文字

        # When
        result = animal_service.search_animals(test_db, search_query)

        # Then
        assert len(result.items) > 0
        assert any(search_query in animal.name for animal in result.items)

    def test_search_animals_by_pattern(
        self, test_db: Session, test_animals_bulk: list[Animal]
    ):
        """正常系: 柄で検索できる"""
        # Given
        search_query = "三毛"

        # When
        result = animal_service.search_animals(test_db, search_query)

        # Then
        assert all("三毛" in animal.pattern for animal in result.items)

    def test_search_animals_by_features(self, test_db: Session, test_animal: Animal):
        """正常系: 特徴で検索できる"""
        # Given
        test_animal.features = "人懐っこい性格"
        test_db.commit()
        search_query = "人懐っこい"

        # When
        result = animal_service.search_animals(test_db, search_query)

        # Then
        assert len(result.items) > 0
        assert any(search_query in (animal.features or "") for animal in result.items)

    def test_search_animals_no_results(self, test_db: Session):
        """正常系: 検索結果が0件の場合"""
        # Given
        search_query = "存在しない猫の名前12345"

        # When
        result = animal_service.search_animals(test_db, search_query)

        # Then
        assert len(result.items) == 0
        assert result.total == 0

    def test_search_animals_case_insensitive(
        self, test_db: Session, test_animal: Animal
    ):
        """正常系: 大文字小文字を区別しない検索"""
        # Given
        test_animal.name = "Tama"
        test_db.commit()

        # When
        result_lower = animal_service.search_animals(test_db, "tama")
        result_upper = animal_service.search_animals(test_db, "TAMA")

        # Then
        assert len(result_lower.items) > 0
        assert len(result_upper.items) > 0
        assert result_lower.total == result_upper.total

    def test_search_animals_with_pagination(
        self, test_db: Session, test_animals_bulk: list[Animal]
    ):
        """正常系: ページネーション付きで検索できる"""
        # Given
        search_query = "猫"  # 多くの猫にマッチする検索語
        page_size = 3

        # When
        result = animal_service.search_animals(
            test_db, search_query, page=1, page_size=page_size
        )

        # Then
        assert len(result.items) <= page_size
        assert result.page == 1
        assert result.page_size == page_size

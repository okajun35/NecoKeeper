---
inclusion: always
---

# テスト駆動開発（TDD）ガイドライン

このドキュメントは、t-wada（和田卓人）氏のテスト駆動開発の原則に基づいた、NecoKeeperプロジェクトのテスト戦略を定義します。

**基本原則**: 「テストのないコードはレガシーコード」

---

## 🎯 テスト駆動開発の3原則

### 1. Red（失敗するテストを書く）
```python
def test_create_animal_with_name():
    """まず失敗するテストを書く"""
    # Given
    animal_data = AnimalCreate(name="たま", ...)

    # When
    result = animal_service.create_animal(db, animal_data, user_id)

    # Then
    assert result.name == "たま"  # まだ実装されていないので失敗
```

### 2. Green（テストをパスする最小限のコードを書く）
```python
def create_animal(db: Session, animal_data: AnimalCreate, user_id: int) -> Animal:
    """テストをパスする最小限の実装"""
    animal = Animal(**animal_data.model_dump())
    db.add(animal)
    db.commit()
    return animal
```

### 3. Refactor（コードを改善する）
```python
def create_animal(db: Session, animal_data: AnimalCreate, user_id: int) -> Animal:
    """リファクタリング後の実装"""
    try:
        animal = Animal(**animal_data.model_dump())
        db.add(animal)
        db.flush()  # IDを取得

        # ステータス履歴を記録（副作用）
        status_history = StatusHistory(
            animal_id=animal.id,
            new_status=animal.status,
            changed_by=user_id,
        )
        db.add(status_history)

        db.commit()
        db.refresh(animal)
        return animal
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="登録失敗") from e
```

---

## 📋 テストの種類と優先順位

### 1. ドメインロジックテスト（最優先）

**目的**: ビジネスルールの検証

```python
class TestAnimalDomainLogic:
    """ドメインロジックのテスト"""

    def test_status_change_creates_history(self):
        """ステータス変更時に履歴が記録される"""
        # ビジネスルールの検証

    def test_cannot_adopt_animal_under_treatment(self):
        """治療中の猫は譲渡できない"""
        # ビジネス制約の検証
```

### 2. 境界値テスト

**目的**: エッジケースの検証

```python
class TestBoundaryConditions:
    """境界値テスト"""

    def test_pagination_first_page(self):
        """最初のページ"""

    def test_pagination_last_page(self):
        """最後のページ"""

    def test_pagination_empty_result(self):
        """結果が0件の場合"""

    def test_search_with_empty_query(self):
        """空の検索クエリ"""

    def test_search_with_special_characters(self):
        """特殊文字を含む検索"""
```

### 3. エラーハンドリングテスト

**目的**: 異常系の検証

```python
class TestErrorHandling:
    """エラーハンドリングテスト"""

    def test_get_nonexistent_resource(self):
        """存在しないリソース → 404"""
        with pytest.raises(HTTPException) as exc_info:
            service.get_animal(db, 99999)
        assert exc_info.value.status_code == 404

    def test_create_with_invalid_data(self):
        """不正なデータ → 400"""

    def test_unauthorized_access(self):
        """権限なし → 403"""
```

### 4. 副作用の検証テスト

**目的**: 状態変更の検証

```python
class TestSideEffects:
    """副作用の検証テスト"""

    def test_create_animal_records_status_history(self):
        """猫登録時にステータス履歴が記録される"""
        # Given
        animal_data = AnimalCreate(...)

        # When
        result = service.create_animal(db, animal_data, user_id)

        # Then
        history = db.query(StatusHistory).filter(
            StatusHistory.animal_id == result.id
        ).first()
        assert history is not None
        assert history.new_status == result.status

    def test_update_status_creates_history_entry(self):
        """ステータス更新時に履歴エントリが作成される"""
```

### 5. 統合テスト

**目的**: コンポーネント間の連携検証

```python
class TestIntegration:
    """統合テスト"""

    def test_create_and_retrieve_animal(self):
        """猫を登録して取得できる"""
        # 複数のサービスメソッドの連携

    def test_full_adoption_workflow(self):
        """譲渡ワークフロー全体"""
        # 保護中 → 譲渡可能 → 譲渡済み
```

---

## 🏗️ テスト構造のベストプラクティス

### Given-When-Then パターン

```python
def test_example():
    """テストの説明"""
    # Given（前提条件）
    animal = Animal(name="たま", status="保護中")
    db.add(animal)
    db.commit()

    # When（実行）
    result = service.update_status(db, animal.id, "譲渡可能", user_id)

    # Then（検証）
    assert result.status == "譲渡可能"
    # 副作用の検証
    history = db.query(StatusHistory).filter(...).first()
    assert history.new_status == "譲渡可能"
```

### テストクラスの命名規則

```python
# ✅ 推奨
class TestCreateAnimal:
    """猫登録のテスト"""

class TestAnimalStatusTransition:
    """猫のステータス遷移のテスト"""

# ❌ 非推奨
class AnimalTests:  # 曖昧
class TestAnimal:   # 範囲が広すぎる
```

### テストメソッドの命名規則

```python
# ✅ 推奨: test_<対象>_<条件>_<期待結果>
def test_create_animal_with_valid_data_success(self):
    """正常系: 有効なデータで猫を登録できる"""

def test_get_animal_with_nonexistent_id_raises_404(self):
    """異常系: 存在しないIDで404エラー"""

def test_update_status_from_protected_to_adoptable_creates_history(self):
    """副作用: ステータス変更時に履歴が記録される"""

# ❌ 非推奨
def test_animal(self):  # 何をテストしているか不明
def test_1(self):       # 意味不明
```

---

## 🎨 テストデータの作成パターン

### 1. フィクスチャの活用

```python
@pytest.fixture(scope="function")
def test_animal(test_db: Session) -> Animal:
    """テスト用の猫を作成"""
    animal = Animal(
        name="テスト猫",
        pattern="キジトラ",
        status="保護中",
    )
    test_db.add(animal)
    test_db.commit()
    test_db.refresh(animal)
    return animal

@pytest.fixture(scope="function")
def test_animals_bulk(test_db: Session) -> list[Animal]:
    """複数の猫を作成（ページネーションテスト用）"""
    animals: list[Animal] = []
    for i in range(10):
        animal = Animal(name=f"猫{i}", ...)
        test_db.add(animal)
        animals.append(animal)
    test_db.commit()
    return animals
```

### 2. ファクトリーパターン

```python
def create_test_animal(
    db: Session,
    name: str = "テスト猫",
    status: str = "保護中",
    **kwargs
) -> Animal:
    """テスト用の猫を作成するファクトリー"""
    animal = Animal(
        name=name,
        pattern=kwargs.get("pattern", "キジトラ"),
        status=status,
        **kwargs
    )
    db.add(animal)
    db.commit()
    db.refresh(animal)
    return animal
```

### 3. パラメータ化テスト

```python
@pytest.mark.parametrize(
    "status,expected_adoptable",
    [
        ("保護中", False),
        ("治療中", False),
        ("譲渡可能", True),
        ("譲渡済み", False),
    ],
    ids=["protected", "treatment", "adoptable", "adopted"]
)
def test_is_adoptable_by_status(status, expected_adoptable):
    """ステータスごとの譲渡可否判定"""
    animal = Animal(status=status)
    assert animal.is_adoptable() == expected_adoptable
```

---

## 🔍 テストカバレッジの目標

### レイヤー別カバレッジ目標

| レイヤー | 目標カバレッジ | 理由 |
|---------|--------------|------|
| **ドメイン層（models/）** | 90%以上 | ビジネスルールの中核 |
| **アプリケーション層（services/）** | 80%以上 | ユースケースの実装 |
| **インフラ層（database.py, utils/）** | 70%以上 | 外部依存の抽象化 |
| **プレゼンテーション層（api/）** | 70%以上 | リクエスト/レスポンス変換 |

### カバレッジの測定

```bash
# カバレッジ測定
python -m pytest --cov=app --cov-report=html --cov-report=term-missing

# 特定のファイルのみ
python -m pytest --cov=app/services/animal_service.py --cov-report=term-missing

# カバレッジ閾値チェック（80%未満で失敗）
python -m pytest --cov=app --cov-fail-under=80
```

---

## 🚫 アンチパターン

### 1. テストが実装の詳細に依存

```python
# ❌ 悪い例: 内部実装に依存
def test_create_animal_calls_db_add():
    """db.add()が呼ばれることをテスト"""
    # 実装の詳細をテストしている

# ✅ 良い例: 振る舞いをテスト
def test_create_animal_persists_to_database():
    """猫がデータベースに保存される"""
    result = service.create_animal(db, data, user_id)
    saved = db.query(Animal).filter(Animal.id == result.id).first()
    assert saved is not None
```

### 2. テストが他のテストに依存

```python
# ❌ 悪い例: テストの順序に依存
def test_1_create_animal():
    global created_animal_id
    created_animal_id = ...

def test_2_get_animal():
    # test_1に依存している
    animal = service.get_animal(db, created_animal_id)

# ✅ 良い例: 各テストが独立
def test_create_animal(test_db):
    result = service.create_animal(...)

def test_get_animal(test_db, test_animal):
    result = service.get_animal(test_db, test_animal.id)
```

### 3. 過度なモック

```python
# ❌ 悪い例: すべてをモック
def test_create_animal_with_mocks():
    mock_db = Mock()
    mock_animal = Mock()
    # 実際の動作を検証していない

# ✅ 良い例: 実際のデータベースを使用
def test_create_animal_with_real_db(test_db):
    # インメモリSQLiteで実際の動作を検証
    result = service.create_animal(test_db, data, user_id)
```

### 4. 1つのテストで複数のことを検証

```python
# ❌ 悪い例: 複数の検証
def test_animal_crud():
    # 作成、取得、更新、削除を1つのテストで
    animal = service.create_animal(...)
    retrieved = service.get_animal(...)
    updated = service.update_animal(...)
    service.delete_animal(...)

# ✅ 良い例: 1テスト1検証
def test_create_animal():
    result = service.create_animal(...)
    assert result.id is not None

def test_get_animal():
    result = service.get_animal(...)
    assert result.name == expected_name
```

---

## 📝 新機能開発のワークフロー

### ステップ1: テストファーストで設計

```python
# 1. まず失敗するテストを書く
def test_upload_image_with_valid_file():
    """画像アップロード機能のテスト"""
    # Given
    image_data = b"fake_image_data"
    animal_id = 1

    # When
    result = image_service.upload_image(db, animal_id, image_data, user_id)

    # Then
    assert result.success is True
    assert result.image_path is not None
```

### ステップ2: 最小限の実装

```python
# 2. テストをパスする最小限のコード
def upload_image(
    db: Session,
    animal_id: int,
    image_data: bytes,
    user_id: int
) -> UploadResult:
    """画像をアップロード"""
    # 最小限の実装
    return UploadResult(success=True, image_path="/fake/path")
```

### ステップ3: エッジケースのテスト追加

```python
# 3. エッジケースのテストを追加
def test_upload_image_exceeds_size_limit():
    """ファイルサイズ超過"""
    large_image = b"x" * (6 * 1024 * 1024)  # 6MB
    with pytest.raises(HTTPException) as exc:
        image_service.upload_image(db, 1, large_image, user_id)
    assert exc.value.status_code == 400

def test_upload_image_invalid_format():
    """不正なフォーマット"""
    invalid_data = b"not an image"
    with pytest.raises(HTTPException):
        image_service.upload_image(db, 1, invalid_data, user_id)
```

### ステップ4: リファクタリング

```python
# 4. テストをパスしたままリファクタリング
def upload_image(
    db: Session,
    animal_id: int,
    image_data: bytes,
    user_id: int
) -> UploadResult:
    """画像をアップロード（リファクタリング後）"""
    # バリデーション
    validate_image_size(image_data)
    validate_image_format(image_data)

    # 画像処理
    optimized_data = optimize_image(image_data)

    # 保存
    image_path = save_image(optimized_data, animal_id)

    # データベース記録
    image_record = AnimalImage(
        animal_id=animal_id,
        image_path=image_path,
        uploaded_by=user_id,
    )
    db.add(image_record)
    db.commit()

    return UploadResult(success=True, image_path=image_path)
```

---

## ✅ テスト実装チェックリスト

新機能を実装する際は、以下をすべて満たすこと：

### 必須項目
- [ ] 正常系のテストを書いた
- [ ] 異常系（エラーハンドリング）のテストを書いた
- [ ] 境界値のテストを書いた
- [ ] 副作用（データベース変更、ログ記録など）を検証した
- [ ] すべてのテストがパスする
- [ ] カバレッジが目標値（80%）以上
- [ ] テストが独立している（他のテストに依存しない）
- [ ] テスト名が説明的である

### 推奨項目
- [ ] パラメータ化テストで複数ケースをカバー
- [ ] Given-When-Thenパターンを使用
- [ ] テストクラスで論理的にグループ化
- [ ] フィクスチャを適切に活用
- [ ] テストのドキュメント（docstring）を記述

---

## 📚 参考資料

### t-wada氏の資料
- [質とスピード](https://speakerdeck.com/twada/quality-and-speed-2020-autumn-edition)
- [テスト駆動開発](https://www.amazon.co.jp/dp/4274217884)
- [プログラマが知るべき97のこと](https://xn--97-273ae6a4irb6e2hsoiozc2g4b8082p.com/)

### Pytest公式ドキュメント
- [Pytest Documentation](https://docs.pytest.org/)
- [Pytest Best Practices](https://docs.pytest.org/en/stable/goodpractices.html)

### Context7参照
- `/pytest-dev/pytest` (Trust Score: 9.5)
- `/sairyss/domain-driven-hexagon` (DDD + TDD)

---

**最終更新**: 2025-11-13
**t-wada準拠**: ✅

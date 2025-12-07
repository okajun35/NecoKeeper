---
inclusion: always
---

# Test-Driven Development (TDD) Guidelines

This document defines the testing strategy for the NecoKeeper project, based on the principles of Test-Driven Development by t-wada (Takuto Wada).

**Core Principle**: "Code without tests is legacy code"

---

## 🎯 Three Principles of Test-Driven Development

### 1. Red (Write a Failing Test)
```python
def test_create_animal_with_name():
    """First, write a failing test"""
    # Given
    animal_data = AnimalCreate(name="Tama", ...)

    # When
    result = animal_service.create_animal(db, animal_data, user_id)

    # Then
    assert result.name == "Tama"  # Fails because not implemented yet
```

### 2. Green (Write Minimal Code to Pass the Test)
```python
def create_animal(db: Session, animal_data: AnimalCreate, user_id: int) -> Animal:
    """Minimal implementation to pass the test"""
    animal = Animal(**animal_data.model_dump())
    db.add(animal)
    db.commit()
    return animal
```

### 3. Refactor (Improve the Code)
```python
def create_animal(db: Session, animal_data: AnimalCreate, user_id: int) -> Animal:
    """Implementation after refactoring"""
    try:
        animal = Animal(**animal_data.model_dump())
        db.add(animal)
        db.flush()  # Get ID

        # Record status history (side effect)
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
        raise HTTPException(status_code=500, detail="Registration failed") from e
```

---

## 📋 Types of Tests and Priority

### 1. Domain Logic Tests (Highest Priority)

**Purpose**: Validate business rules

```python
class TestAnimalDomainLogic:
    """Domain logic tests"""

    def test_status_change_creates_history(self):
        """Status change creates history record"""
        # Validate business rules

    def test_cannot_adopt_animal_under_treatment(self):
        """Cannot adopt cat under treatment"""
        # Validate business constraints
```

### 2. Boundary Value Tests

**Purpose**: Validate edge cases

```python
class TestBoundaryConditions:
    """Boundary value tests"""

    def test_pagination_first_page(self):
        """First page"""

    def test_pagination_last_page(self):
        """Last page"""

    def test_pagination_empty_result(self):
        """Empty result"""

    def test_search_with_empty_query(self):
        """Empty search query"""

    def test_search_with_special_characters(self):
        """Search with special characters"""
```

### 3. Error Handling Tests

**Purpose**: Validate error cases

```python
class TestErrorHandling:
    """Error handling tests"""

    def test_get_nonexistent_resource(self):
        """Non-existent resource → 404"""
        with pytest.raises(HTTPException) as exc_info:
            service.get_animal(db, 99999)
        assert exc_info.value.status_code == 404

    def test_create_with_invalid_data(self):
        """Invalid data → 400"""

    def test_unauthorized_access(self):
        """Unauthorized → 403"""
```

### 4. Side Effect Validation Tests

**Purpose**: Validate state changes

```python
class TestSideEffects:
    """Side effect validation tests"""

    def test_create_animal_records_status_history(self):
        """Cat registration records status history"""
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
        """Status update creates history entry"""
```

### 5. Integration Tests

**Purpose**: Validate component interactions

```python
class TestIntegration:
    """Integration tests"""

    def test_create_and_retrieve_animal(self):
        """Register and retrieve cat"""
        # Multiple service method interactions

    def test_full_adoption_workflow(self):
        """Complete adoption workflow"""
        # Under protection → Available for adoption → Adopted
```

---

## 🏗️ Test Structure Best Practices

### Given-When-Then Pattern

```python
def test_example():
    """Test description"""
    # Given (preconditions)
    animal = Animal(name="Tama", status="Under Protection")
    db.add(animal)
    db.commit()

    # When (execution)
    result = service.update_status(db, animal.id, "Available for Adoption", user_id)

    # Then (validation)
    assert result.status == "Available for Adoption"
    # Validate side effects
    history = db.query(StatusHistory).filter(...).first()
    assert history.new_status == "Available for Adoption"
```

### Test Class Naming Convention

```python
# ✅ Recommended
class TestCreateAnimal:
    """Cat registration tests"""

class TestAnimalStatusTransition:
    """Cat status transition tests"""

# ❌ Not recommended
class AnimalTests:  # Too vague
class TestAnimal:   # Too broad
```

### Test Method Naming Convention

```python
# ✅ Recommended: test_<target>_<condition>_<expected_result>
def test_create_animal_with_valid_data_success(self):
    """Normal case: Successfully register cat with valid data"""

def test_get_animal_with_nonexistent_id_raises_404(self):
    """Error case: 404 error for non-existent ID"""

def test_update_status_from_protected_to_adoptable_creates_history(self):
    """Side effect: Status change records history"""

# ❌ Not recommended
def test_animal(self):  # Unclear what is being tested
def test_1(self):       # Meaningless
```

---

## 🎨 Test Data Creation Patterns

### 1. Using Fixtures

```python
@pytest.fixture(scope="function")
def test_animal(test_db: Session) -> Animal:
    """Create test cat"""
    animal = Animal(
        name="Test Cat",
        pattern="Tabby",
        status="Under Protection",
    )
    test_db.add(animal)
    test_db.commit()
    test_db.refresh(animal)
    return animal

@pytest.fixture(scope="function")
def test_animals_bulk(test_db: Session) -> list[Animal]:
    """Create multiple cats (for pagination tests)"""
    animals: list[Animal] = []
    for i in range(10):
        animal = Animal(name=f"Cat{i}", ...)
        test_db.add(animal)
        animals.append(animal)
    test_db.commit()
    return animals
```

### 2. Factory Pattern

```python
def create_test_animal(
    db: Session,
    name: str = "Test Cat",
    status: str = "Under Protection",
    **kwargs
) -> Animal:
    """Factory for creating test cats"""
    animal = Animal(
        name=name,
        pattern=kwargs.get("pattern", "Tabby"),
        status=status,
        **kwargs
    )
    db.add(animal)
    db.commit()
    db.refresh(animal)
    return animal
```

### 3. Parameterized Tests

```python
@pytest.mark.parametrize(
    "status,expected_adoptable",
    [
        ("Under Protection", False),
        ("Under Treatment", False),
        ("Available for Adoption", True),
        ("Adopted", False),
    ],
    ids=["protected", "treatment", "adoptable", "adopted"]
)
def test_is_adoptable_by_status(status, expected_adoptable):
    """Adoption eligibility by status"""
    animal = Animal(status=status)
    assert animal.is_adoptable() == expected_adoptable
```

---

## 🔍 Test Coverage Goals

### Coverage Goals by Layer

| Layer | Target Coverage | Reason |
|-------|----------------|--------|
| **Domain Layer (models/)** | 90%+ | Core business rules |
| **Application Layer (services/)** | 80%+ | Use case implementation |
| **Infrastructure Layer (database.py, utils/)** | 70%+ | External dependency abstraction |
| **Presentation Layer (api/)** | 70%+ | Request/response transformation |

### Measuring Coverage

```bash
# Measure coverage
python -m pytest --cov=app --cov-report=html --cov-report=term-missing

# Specific file only
python -m pytest --cov=app/services/animal_service.py --cov-report=term-missing

# Coverage threshold check (fail if below 80%)
python -m pytest --cov=app --cov-fail-under=80
```

---

## 🚫 Anti-Patterns

### 1. Tests Depend on Implementation Details

```python
# ❌ Bad: Depends on internal implementation
def test_create_animal_calls_db_add():
    """Test that db.add() is called"""
    # Testing implementation details

# ✅ Good: Test behavior
def test_create_animal_persists_to_database():
    """Cat is persisted to database"""
    result = service.create_animal(db, data, user_id)
    saved = db.query(Animal).filter(Animal.id == result.id).first()
    assert saved is not None
```

### 2. Tests Depend on Other Tests

```python
# ❌ Bad: Depends on test order
def test_1_create_animal():
    global created_animal_id
    created_animal_id = ...

def test_2_get_animal():
    # Depends on test_1
    animal = service.get_animal(db, created_animal_id)

# ✅ Good: Each test is independent
def test_create_animal(test_db):
    result = service.create_animal(...)

def test_get_animal(test_db, test_animal):
    result = service.get_animal(test_db, test_animal.id)
```

### 3. Excessive Mocking

```python
# ❌ Bad: Mock everything
def test_create_animal_with_mocks():
    mock_db = Mock()
    mock_animal = Mock()
    # Not testing actual behavior

# ✅ Good: Use real database
def test_create_animal_with_real_db(test_db):
    # Test actual behavior with in-memory SQLite
    result = service.create_animal(test_db, data, user_id)
```

### 4. Testing Multiple Things in One Test

```python
# ❌ Bad: Multiple validations
def test_animal_crud():
    # Create, read, update, delete in one test
    animal = service.create_animal(...)
    retrieved = service.get_animal(...)
    updated = service.update_animal(...)
    service.delete_animal(...)

# ✅ Good: One validation per test
def test_create_animal():
    result = service.create_animal(...)
    assert result.id is not None

def test_get_animal():
    result = service.get_animal(...)
    assert result.name == expected_name
```

---

## 📝 New Feature Development Workflow

### Step 1: Design with Test-First

```python
# 1. First, write a failing test
def test_upload_image_with_valid_file():
    """Image upload feature test"""
    # Given
    image_data = b"fake_image_data"
    animal_id = 1

    # When
    result = image_service.upload_image(db, animal_id, image_data, user_id)

    # Then
    assert result.success is True
    assert result.image_path is not None
```

### Step 2: Minimal Implementation

```python
# 2. Minimal code to pass the test
def upload_image(
    db: Session,
    animal_id: int,
    image_data: bytes,
    user_id: int
) -> UploadResult:
    """Upload image"""
    # Minimal implementation
    return UploadResult(success=True, image_path="/fake/path")
```

### Step 3: Add Edge Case Tests

```python
# 3. Add edge case tests
def test_upload_image_exceeds_size_limit():
    """File size exceeds limit"""
    large_image = b"x" * (6 * 1024 * 1024)  # 6MB
    with pytest.raises(HTTPException) as exc:
        image_service.upload_image(db, 1, large_image, user_id)
    assert exc.value.status_code == 400

def test_upload_image_invalid_format():
    """Invalid format"""
    invalid_data = b"not an image"
    with pytest.raises(HTTPException):
        image_service.upload_image(db, 1, invalid_data, user_id)
```

### Step 4: Refactoring

```python
# 4. Refactor while keeping tests passing
def upload_image(
    db: Session,
    animal_id: int,
    image_data: bytes,
    user_id: int
) -> UploadResult:
    """Upload image (after refactoring)"""
    # Validation
    validate_image_size(image_data)
    validate_image_format(image_data)

    # Image processing
    optimized_data = optimize_image(image_data)

    # Save
    image_path = save_image(optimized_data, animal_id)

    # Database record
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

## ✅ Test Implementation Checklist

When implementing new features, ensure all of the following are met:

### Required Items
- [ ] Wrote normal case tests
- [ ] Wrote error case (error handling) tests
- [ ] Wrote boundary value tests
- [ ] Validated side effects (database changes, logging, etc.)
- [ ] All tests pass
- [ ] Coverage meets target (80%+)
- [ ] Tests are independent (don't depend on other tests)
- [ ] Test names are descriptive

### Recommended Items
- [ ] Cover multiple cases with parameterized tests
- [ ] Use Given-When-Then pattern
- [ ] Logically group with test classes
- [ ] Properly utilize fixtures
- [ ] Write test documentation (docstrings)

---

## 📚 References

### t-wada Resources
- [Quality and Speed](https://speakerdeck.com/twada/quality-and-speed-2020-autumn-edition)
- [Test-Driven Development](https://www.amazon.co.jp/dp/4274217884)
- [97 Things Every Programmer Should Know](https://xn--97-273ae6a4irb6e2hsoiozc2g4b8082p.com/)

### Pytest Official Documentation
- [Pytest Documentation](https://docs.pytest.org/)
- [Pytest Best Practices](https://docs.pytest.org/en/stable/goodpractices.html)

### Context7 References
- `/pytest-dev/pytest` (Trust Score: 9.5)
- `/sairyss/domain-driven-hexagon` (DDD + TDD)

---

**Last Updated**: 2025-11-13
**t-wada Compliant**: ✅

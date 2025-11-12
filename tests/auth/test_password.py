"""
パスワードハッシュ化のテスト
"""

from app.auth.password import (
    hash_password,
    needs_rehash,
    validate_password_policy,
    verify_password,
)


class TestPasswordHashing:
    """パスワードハッシュ化のテストクラス"""

    def test_hash_password(self):
        """パスワードをハッシュ化できる"""
        password = "TestPassword123"
        hashed = hash_password(password)

        # ハッシュが生成されること
        assert hashed is not None
        assert len(hashed) > 0

        # 元のパスワードとは異なること
        assert hashed != password

        # Argon2idハッシュの形式であること
        assert hashed.startswith("$argon2id$")

    def test_verify_password_correct(self):
        """正しいパスワードで検証が成功する"""
        password = "TestPassword123"
        hashed = hash_password(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """間違ったパスワードで検証が失敗する"""
        password = "TestPassword123"
        wrong_password = "WrongPassword456"
        hashed = hash_password(password)

        assert verify_password(wrong_password, hashed) is False

    def test_hash_same_password_twice_different_hashes(self):
        """同じパスワードでも異なるハッシュが生成される（ソルト）"""
        password = "TestPassword123"
        hash1 = hash_password(password)
        hash2 = hash_password(password)

        # 異なるハッシュが生成されること
        assert hash1 != hash2

        # どちらも検証に成功すること
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True


class TestPasswordPolicy:
    """パスワードポリシーのテストクラス"""

    def test_valid_password(self):
        """有効なパスワードが受け入れられる"""
        valid, error = validate_password_policy("ValidPass123")
        assert valid is True
        assert error is None

    def test_password_too_short(self):
        """8文字未満のパスワードが拒否される"""
        valid, error = validate_password_policy("Short1")
        assert valid is False
        assert "最小8文字" in error

    def test_password_no_letters(self):
        """英字を含まないパスワードが拒否される"""
        valid, error = validate_password_policy("12345678")
        assert valid is False
        assert "英字と数字" in error

    def test_password_no_numbers(self):
        """数字を含まないパスワードが拒否される"""
        valid, error = validate_password_policy("OnlyLetters")
        assert valid is False
        assert "英字と数字" in error

    def test_password_with_special_characters(self):
        """特殊文字を含むパスワードが受け入れられる"""
        valid, error = validate_password_policy("Pass@word123!")
        assert valid is True
        assert error is None

    def test_password_minimum_length(self):
        """ちょうど8文字のパスワードが受け入れられる"""
        valid, error = validate_password_policy("Pass1234")
        assert valid is True
        assert error is None


class TestNeedsRehash:
    """ハッシュ再生成チェックのテストクラス"""

    def test_new_hash_does_not_need_rehash(self):
        """新しいハッシュは再ハッシュ化不要"""
        password = "TestPassword123"
        hashed = hash_password(password)

        # 新しく生成したハッシュは再ハッシュ化不要
        assert needs_rehash(hashed) is False

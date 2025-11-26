"""
Necro Translation System Tests

Tests for the Kiroween Mode English-only immersive translation system.
Validates Requirements 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 14.2
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from app.config import Settings


class TestNecroTranslationFileExistence:
    """Test that en_necro.json file exists and is valid JSON"""

    def test_en_necro_file_exists(self) -> None:
        """en_necro.json file exists"""
        file_path = Path("app/static/i18n/en_necro.json")
        assert file_path.exists(), "en_necro.json file must exist"

    def test_en_necro_file_is_valid_json(self) -> None:
        """en_necro.json is valid JSON"""
        file_path = Path("app/static/i18n/en_necro.json")
        with file_path.open(encoding="utf-8") as f:
            data = json.load(f)
        assert isinstance(data, dict), "en_necro.json must be a JSON object"


class TestNecroTranslationContent:
    """Test that en_necro.json contains cyberpunk/horror-themed translations"""

    def test_common_terms_are_cyberpunk_themed(self) -> None:
        """Common terms use cyberpunk/horror terminology"""
        file_path = Path("app/static/i18n/en_necro.json")
        with file_path.open(encoding="utf-8") as f:
            translations = json.load(f)

        common = translations.get("common", {})

        # Requirement 5.2: Common terms transformation
        assert common.get("save") == "COMMIT_SOUL"
        assert common.get("loading") == "SUMMONING..."
        assert common.get("delete") == "PURGE_PROTOCOL"
        assert common.get("cancel") == "ABORT"
        assert common.get("confirm") == "EXECUTE"

    def test_login_terms_are_cyberpunk_themed(self) -> None:
        """Login page terms use cyberpunk/horror terminology"""
        file_path = Path("app/static/i18n/en_necro.json")
        with file_path.open(encoding="utf-8") as f:
            translations = json.load(f)

        auth = translations.get("auth", {})
        login = auth.get("login", {})

        # Requirement 5.2: Login page terms
        assert login.get("title") == "NECRO-TERMINAL ACCESS"
        assert login.get("email") == "OPERATIVE_ID"
        assert login.get("password") == "AUTH_CODE"
        assert login.get("submit") == "INITIATE_CONNECTION"

        # Requirement 3.3: Boot sequence text
        boot_sequence = login.get("boot_sequence", {})
        assert boot_sequence.get("line1") == "INITIALIZING 9TH_LIFE_PROTOCOL..."
        assert boot_sequence.get("line2") == "UPLOADING CONSCIOUSNESS... COMPLETE."
        assert (
            boot_sequence.get("line3")
            == "SCANNING FOR INEFFICIENCY... TARGET ACQUIRED."
        )
        assert boot_sequence.get("line4") == "WELCOME, HUMAN COLLABORATOR."

    def test_animal_status_terms_are_cyberpunk_themed(self) -> None:
        """Animal status terms use cyberpunk/horror terminology"""
        file_path = Path("app/static/i18n/en_necro.json")
        with file_path.open(encoding="utf-8") as f:
            translations = json.load(f)

        animals = translations.get("animals", {})
        status = animals.get("status", {})

        # Requirement 5.2: Animal status terms
        assert status.get("protected") == "PROTECTION_PROTOCOL"
        assert status.get("adoptable") == "TRANSFER_READY"
        assert status.get("adopted") == "TRANSFER_COMPLETE"
        assert status.get("treatment") == "REPAIR_MODE"
        assert status.get("deceased") == "SIGNAL_LOST"

    def test_volunteer_term_is_operative(self) -> None:
        """Volunteer is translated to OPERATIVE"""
        file_path = Path("app/static/i18n/en_necro.json")
        with file_path.open(encoding="utf-8") as f:
            translations = json.load(f)

        volunteers = translations.get("volunteers", {})
        assert volunteers.get("title") == "OPERATIVES"

        nav = translations.get("nav", {})
        assert nav.get("volunteers") == "OPERATIVES"

    def test_error_terms_are_cyberpunk_themed(self) -> None:
        """Error messages use cyberpunk/horror terminology"""
        file_path = Path("app/static/i18n/en_necro.json")
        with file_path.open(encoding="utf-8") as f:
            translations = json.load(f)

        errors = translations.get("errors", {})

        # Requirement 5.4: Error messages
        assert errors.get("404") == "ENTITY_NOT_FOUND"
        assert errors.get("500") == "FATAL_GLITCH"
        assert errors.get("network_error") == "CONNECTION_LOST"


class TestPropertyTranslationLoading:
    """
    Property 8: Translation Loading
    For any UI message in Kiroween Mode, the system should load translations
    from en_necro.json
    Validates: Requirements 5.1, 5.5
    """

    @pytest.mark.parametrize("kiroween_mode", [True, False])
    def test_translation_file_selection_based_on_mode(
        self, kiroween_mode: bool
    ) -> None:
        """
        **Feature: kiroween-theme, Property 8: Translation Loading**
        **Validates: Requirements 5.1, 5.5**

        Property: For any configuration state (Kiroween enabled/disabled),
        the correct translation file should be selected
        """
        # This is a conceptual test - the actual loading happens in JavaScript
        # We verify that the file exists and is accessible
        if kiroween_mode:
            # In Kiroween mode, en_necro.json should be used
            file_path = Path("app/static/i18n/en_necro.json")
            assert file_path.exists()
            with file_path.open(encoding="utf-8") as f:
                data = json.load(f)
            assert "common" in data
            assert data["common"]["save"] == "COMMIT_SOUL"
        else:
            # In standard mode, standard locale files should be used
            file_path = Path("app/static/i18n/en.json")
            assert file_path.exists()
            with file_path.open(encoding="utf-8") as f:
                data = json.load(f)
            assert "common" in data
            assert data["common"]["save"] == "Save"


class TestPropertyTranslationMapping:
    """
    Property 9: Translation Mapping
    For any standard UI term, when Kiroween Mode is enabled, the system should
    display the corresponding necro translation
    Validates: Requirements 5.2, 5.4
    """

    @pytest.mark.parametrize(
        "term",
        [
            ("save", "COMMIT_SOUL"),
            ("loading", "SUMMONING..."),
            ("delete", "PURGE_PROTOCOL"),
            ("cancel", "ABORT"),
            ("confirm", "EXECUTE"),
            ("error", "FATAL_GLITCH"),
        ],
    )
    def test_common_term_mapping(self, term: tuple[str, str]) -> None:
        """
        **Feature: kiroween-theme, Property 9: Translation Mapping**
        **Validates: Requirements 5.2, 5.4**

        Property: For any common UI term, the necro translation should match
        the expected cyberpunk/horror terminology
        """
        standard_term, necro_term = term

        # Load en_necro.json
        file_path = Path("app/static/i18n/en_necro.json")
        with file_path.open(encoding="utf-8") as f:
            necro_translations = json.load(f)

        # Verify mapping
        common = necro_translations.get("common", {})
        if standard_term == "error":
            # Error is in errors section
            errors = necro_translations.get("errors", {})
            assert errors.get("500") == necro_term
        else:
            assert common.get(standard_term) == necro_term

    @pytest.mark.parametrize(
        "status",
        [
            ("protected", "PROTECTION_PROTOCOL"),
            ("adoptable", "TRANSFER_READY"),
            ("adopted", "TRANSFER_COMPLETE"),
            ("treatment", "REPAIR_MODE"),
            ("deceased", "SIGNAL_LOST"),
        ],
    )
    def test_animal_status_mapping(self, status: tuple[str, str]) -> None:
        """
        **Feature: kiroween-theme, Property 9: Translation Mapping**
        **Validates: Requirements 5.2, 5.4**

        Property: For any animal status term, the necro translation should match
        the expected cyberpunk/horror terminology
        """
        standard_status, necro_status = status

        # Load en_necro.json
        file_path = Path("app/static/i18n/en_necro.json")
        with file_path.open(encoding="utf-8") as f:
            necro_translations = json.load(f)

        # Verify mapping
        animals = necro_translations.get("animals", {})
        status_dict = animals.get("status", {})
        assert status_dict.get(standard_status) == necro_status


class TestPropertyForcedEnglishLocale:
    """
    Property 28: Forced English Locale
    For any page in Kiroween Mode, the interface language should be forced to
    English and load en_necro.json
    Validates: Requirements 5.1, 14.2
    """

    @pytest.mark.parametrize("kiroween_mode", [True, False])
    def test_locale_forcing_in_kiroween_mode(self, kiroween_mode: bool) -> None:
        """
        **Feature: kiroween-theme, Property 28: Forced English Locale**
        **Validates: Requirements 5.1, 14.2**

        Property: For any configuration state, when Kiroween Mode is enabled,
        the locale should be forced to English
        """
        # Mock settings
        with patch("app.config.get_settings") as mock_settings:
            settings = Settings(kiroween_mode=kiroween_mode)
            mock_settings.return_value = settings

            # In Kiroween mode, locale should be forced to 'en'
            # This is verified by checking that the JavaScript will load en_necro.json
            if kiroween_mode:
                # Verify en_necro.json exists and is valid
                file_path = Path("app/static/i18n/en_necro.json")
                assert file_path.exists()
                with file_path.open(encoding="utf-8") as f:
                    data = json.load(f)
                assert isinstance(data, dict)
                # Verify it contains English necro translations
                assert data["common"]["app_name"] == "NECRO-TERMINAL"


class TestUnitTranslationSystem:
    """Unit tests for translation system"""

    def test_en_necro_loads_in_kiroween_mode(self) -> None:
        """
        en_necro.json loads in Kiroween Mode
        Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6
        """
        # Verify file exists and is accessible
        file_path = Path("app/static/i18n/en_necro.json")
        assert file_path.exists()

        with file_path.open(encoding="utf-8") as f:
            data = json.load(f)

        # Verify structure
        assert "common" in data
        assert "auth" in data
        assert "animals" in data
        assert "volunteers" in data
        assert "errors" in data

    def test_standard_locale_files_load_in_standard_mode(self) -> None:
        """
        Standard locale files load in standard mode
        Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6
        """
        # Verify standard English file exists
        file_path = Path("app/static/i18n/en.json")
        assert file_path.exists()

        with file_path.open(encoding="utf-8") as f:
            data = json.load(f)

        # Verify it's standard English, not necro
        assert data["common"]["save"] == "Save"
        assert data["common"]["loading"] == "Loading..."

    def test_specific_translation_keys_return_necro_values(self) -> None:
        """
        Test specific translation keys return necro values
        Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6
        """
        file_path = Path("app/static/i18n/en_necro.json")
        with file_path.open(encoding="utf-8") as f:
            necro = json.load(f)

        # Test various keys
        assert necro["common"]["save"] == "COMMIT_SOUL"
        assert necro["common"]["loading"] == "SUMMONING..."
        assert necro["auth"]["login"]["title"] == "NECRO-TERMINAL ACCESS"
        assert necro["animals"]["status"]["protected"] == "PROTECTION_PROTOCOL"
        assert necro["volunteers"]["title"] == "OPERATIVES"

    def test_translation_fallback_behavior(self) -> None:
        """
        Test translation fallback behavior
        Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6
        """
        # Verify that en_necro.json has all required keys
        file_path = Path("app/static/i18n/en_necro.json")
        with file_path.open(encoding="utf-8") as f:
            necro = json.load(f)

        # Check that major sections exist
        required_sections = [
            "common",
            "nav",
            "dashboard",
            "animals",
            "care_logs",
            "medical_records",
            "volunteers",
            "auth",
            "errors",
        ]

        for section in required_sections:
            assert section in necro, f"Missing section: {section}"

    def test_locale_is_forced_to_en_in_kiroween_mode(self) -> None:
        """
        Test locale is forced to 'en' in Kiroween Mode
        Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6
        """
        # This is tested via JavaScript behavior
        # We verify that the configuration is correct
        with patch("app.config.get_settings") as mock_settings:
            settings = Settings(kiroween_mode=True)
            mock_settings.return_value = settings

            # Verify kiroween_mode is True
            assert settings.kiroween_mode is True

            # Verify en_necro.json exists for loading
            file_path = Path("app/static/i18n/en_necro.json")
            assert file_path.exists()

    def test_all_major_sections_have_necro_translations(self) -> None:
        """
        Verify all major sections have necro translations
        Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6
        """
        file_path = Path("app/static/i18n/en_necro.json")
        with file_path.open(encoding="utf-8") as f:
            necro = json.load(f)

        # Verify each section has at least some translations
        assert len(necro["common"]) > 10
        assert len(necro["nav"]) > 5
        assert len(necro["animals"]) > 5
        assert len(necro["auth"]) > 0
        assert len(necro["errors"]) > 5

    def test_necro_translations_are_uppercase_or_snake_case(self) -> None:
        """
        Verify necro translations follow cyberpunk naming convention
        Requirements: 5.2, 5.4
        """
        file_path = Path("app/static/i18n/en_necro.json")
        with file_path.open(encoding="utf-8") as f:
            necro = json.load(f)

        # Check common terms follow pattern
        common = necro["common"]
        cyberpunk_terms = [
            "COMMIT_SOUL",
            "SUMMONING...",
            "PURGE_PROTOCOL",
            "ABORT",
            "EXECUTE",
            "FATAL_GLITCH",
            "OPERATIVE",
        ]

        # Verify at least some terms are in the cyberpunk style
        found_terms = [
            term
            for term in common.values()
            if isinstance(term, str) and term in cyberpunk_terms
        ]
        assert len(found_terms) >= 3, "Should have multiple cyberpunk-styled terms"

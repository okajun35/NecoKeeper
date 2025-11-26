"""
Language Switcher Hiding Tests

Tests for the Language Switcher hiding feature in Kiroween Mode.
Validates that the language switcher is hidden in Kiroween Mode to maintain
English-only immersion.

Requirements: 14.1, 14.3, 14.4
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest


class TestLanguageSwitcherHidingProperty:
    """Property-based tests for Language Switcher hiding"""

    @pytest.mark.parametrize(
        "template_path",
        [
            "app/templates/admin/base.html",
            "app/templates/admin/login.html",
            "app/templates/public/care_form.html",
            "app/templates/public/care_log_list.html",
        ],
        ids=["admin-base", "admin-login", "public-care-form", "public-care-log-list"],
    )
    def test_language_switcher_hiding_property(self, template_path: str):
        """
        Property 27: Language Switcher Hiding
        For any page in Kiroween Mode, the language switcher UI should not be visible.

        **Feature: kiroween-theme, Property 27: Language Switcher Hiding**
        **Validates: Requirements 14.1**

        Given: Template files with language switcher
        When: Checking conditional rendering
        Then: Language switcher is wrapped in {% if not settings.kiroween_mode %}
        """
        # Given
        template_file = Path(template_path)
        template_content = template_file.read_text()

        # Then: Language switcher should be conditionally rendered
        if 'id="language-switcher"' in template_content:
            # Verify it's wrapped in conditional
            pattern = (
                r"{%\s*if\s+not\s+settings\.kiroween_mode\s*%}.*?"
                r'id="language-switcher".*?'
                r"{%\s*endif\s*%}"
            )
            assert re.search(pattern, template_content, re.DOTALL), (
                f"Language switcher in {template_path} should be wrapped in "
                "{% if not settings.kiroween_mode %}"
            )


class TestLanguageSwitcherVisibilityUnit:
    """Unit tests for Language Switcher visibility"""

    def test_language_switcher_hidden_in_admin_base(self):
        """
        正常系: Language switcher is hidden in admin base.html

        Given: app/templates/admin/base.html
        When: Checking language switcher
        Then: Language switcher is conditionally rendered

        Requirements: 14.1
        """
        # Given
        template_path = Path("app/templates/admin/base.html")
        template_content = template_path.read_text()

        # Then: Language switcher should be conditionally rendered
        assert 'id="language-switcher"' in template_content, (
            "Language switcher should exist in base.html"
        )

        # Verify conditional rendering
        pattern = (
            r"{%\s*if\s+not\s+settings\.kiroween_mode\s*%}.*?"
            r'id="language-switcher".*?'
            r"{%\s*endif\s*%}"
        )
        assert re.search(pattern, template_content, re.DOTALL), (
            "Language switcher should be wrapped in kiroween_mode check"
        )

    def test_language_switcher_hidden_in_login(self):
        """
        正常系: Language switcher is hidden in login.html

        Given: app/templates/admin/login.html
        When: Checking language switcher
        Then: Language switcher is conditionally rendered

        Requirements: 14.1, 14.3
        """
        # Given
        template_path = Path("app/templates/admin/login.html")
        template_content = template_path.read_text()

        # Then: Language switcher should be conditionally rendered
        assert 'id="language-switcher"' in template_content, (
            "Language switcher should exist in login.html"
        )

        # Verify conditional rendering
        pattern = (
            r"{%\s*if\s+not\s+settings\.kiroween_mode\s*%}.*?"
            r'id="language-switcher".*?'
            r"{%\s*endif\s*%}"
        )
        assert re.search(pattern, template_content, re.DOTALL), (
            "Language switcher should be wrapped in kiroween_mode check"
        )

    def test_language_switcher_hidden_in_public_care_form(self):
        """
        正常系: Language switcher is hidden in public care_form.html

        Given: app/templates/public/care_form.html
        When: Checking language switcher
        Then: Language switcher is conditionally rendered

        Requirements: 14.1, 14.4
        """
        # Given
        template_path = Path("app/templates/public/care_form.html")
        template_content = template_path.read_text()

        # Then: Language switcher should be conditionally rendered
        assert 'id="language-switcher"' in template_content, (
            "Language switcher should exist in care_form.html"
        )

        # Verify conditional rendering
        pattern = (
            r"{%\s*if\s+not\s+settings\.kiroween_mode\s*%}.*?"
            r'id="language-switcher".*?'
            r"{%\s*endif\s*%}"
        )
        assert re.search(pattern, template_content, re.DOTALL), (
            "Language switcher should be wrapped in kiroween_mode check"
        )

    def test_language_switcher_hidden_in_public_care_log_list(self):
        """
        正常系: Language switcher is hidden in public care_log_list.html

        Given: app/templates/public/care_log_list.html
        When: Checking language switcher
        Then: Language switcher is conditionally rendered

        Requirements: 14.1, 14.4
        """
        # Given
        template_path = Path("app/templates/public/care_log_list.html")
        template_content = template_path.read_text()

        # Then: Language switcher should be conditionally rendered
        assert 'id="language-switcher"' in template_content, (
            "Language switcher should exist in care_log_list.html"
        )

        # Verify conditional rendering
        pattern = (
            r"{%\s*if\s+not\s+settings\.kiroween_mode\s*%}.*?"
            r'id="language-switcher".*?'
            r"{%\s*endif\s*%}"
        )
        assert re.search(pattern, template_content, re.DOTALL), (
            "Language switcher should be wrapped in kiroween_mode check"
        )

    def test_language_switcher_visible_in_standard_mode(self):
        """
        正常系: Language switcher is visible in standard mode

        Given: Template files
        When: Checking conditional logic
        Then: Language switcher is shown when kiroween_mode is False

        Requirements: 14.3
        """
        # Given
        templates = [
            "app/templates/admin/base.html",
            "app/templates/admin/login.html",
            "app/templates/public/care_form.html",
            "app/templates/public/care_log_list.html",
        ]

        for template_path in templates:
            template_file = Path(template_path)
            template_content = template_file.read_text()

            # Then: Language switcher should be conditionally rendered
            if 'id="language-switcher"' in template_content:
                # Verify it uses "if not" condition (shown when False)
                assert "{% if not settings.kiroween_mode %}" in template_content, (
                    f"Language switcher in {template_path} should use "
                    "'if not settings.kiroween_mode'"
                )

    def test_language_switcher_has_svg_icon(self):
        """
        正常系: Language switcher has SVG icon

        Given: Template files with language switcher
        When: Checking language switcher structure
        Then: SVG icon is present

        Requirements: 14.1
        """
        # Given
        templates = [
            "app/templates/admin/base.html",
            "app/templates/admin/login.html",
            "app/templates/public/care_form.html",
            "app/templates/public/care_log_list.html",
        ]

        for template_path in templates:
            template_file = Path(template_path)
            template_content = template_file.read_text()

            if 'id="language-switcher"' in template_content:
                # Then: SVG icon should be present
                switcher_section = re.search(
                    r'id="language-switcher".*?</button>',
                    template_content,
                    re.DOTALL,
                )
                assert switcher_section is not None, (
                    f"Language switcher button should exist in {template_path}"
                )

                switcher_html = switcher_section.group(0)
                assert "<svg" in switcher_html, (
                    f"Language switcher in {template_path} should have SVG icon"
                )

    def test_language_switcher_has_text_span(self):
        """
        正常系: Language switcher has text span

        Given: Template files with language switcher
        When: Checking language switcher structure
        Then: Text span with language-text class is present

        Requirements: 14.1
        """
        # Given
        templates = [
            "app/templates/admin/base.html",
            "app/templates/admin/login.html",
        ]

        for template_path in templates:
            template_file = Path(template_path)
            template_content = template_file.read_text()

            if 'id="language-switcher"' in template_content:
                # Then: Text span should be present
                switcher_section = re.search(
                    r'id="language-switcher".*?</button>',
                    template_content,
                    re.DOTALL,
                )
                assert switcher_section is not None

                switcher_html = switcher_section.group(0)
                assert 'class="language-text"' in switcher_html or (
                    "language-text" in switcher_html
                ), (
                    f"Language switcher in {template_path} should have language-text span"
                )


class TestLanguageSwitcherIntegration:
    """Integration tests for Language Switcher hiding feature"""

    def test_all_templates_with_language_switcher_have_conditional(self):
        """
        正常系: All templates with language switcher have conditional rendering

        Given: All template files
        When: Searching for language-switcher
        Then: All instances are wrapped in conditional

        Requirements: 14.1, 14.3, 14.4
        """
        # Given
        templates_with_switcher = [
            "app/templates/admin/base.html",
            "app/templates/admin/login.html",
            "app/templates/public/care_form.html",
            "app/templates/public/care_log_list.html",
        ]

        for template_path in templates_with_switcher:
            template_file = Path(template_path)
            template_content = template_file.read_text()

            # Then: Language switcher should be conditionally rendered
            if 'id="language-switcher"' in template_content:
                pattern = (
                    r"{%\s*if\s+not\s+settings\.kiroween_mode\s*%}.*?"
                    r'id="language-switcher".*?'
                    r"{%\s*endif\s*%}"
                )
                assert re.search(pattern, template_content, re.DOTALL), (
                    f"Language switcher in {template_path} must be wrapped in "
                    "{% if not settings.kiroween_mode %}"
                )

    def test_language_switcher_conditional_syntax(self):
        """
        正常系: Language switcher uses correct conditional syntax

        Given: Template files with language switcher
        When: Checking conditional syntax
        Then: Uses {% if not settings.kiroween_mode %}

        Requirements: 14.1
        """
        # Given
        templates = [
            "app/templates/admin/base.html",
            "app/templates/admin/login.html",
            "app/templates/public/care_form.html",
            "app/templates/public/care_log_list.html",
        ]

        for template_path in templates:
            template_file = Path(template_path)
            template_content = template_file.read_text()

            if 'id="language-switcher"' in template_content:
                # Then: Should use correct syntax
                assert "{% if not settings.kiroween_mode %}" in template_content, (
                    f"{template_path} should use correct conditional syntax"
                )

                # Verify proper closing
                assert "{% endif %}" in template_content, (
                    f"{template_path} should have proper endif"
                )

    def test_no_language_switcher_outside_conditional(self):
        """
        正常系: No language switcher exists outside conditional blocks

        Given: Template files
        When: Checking for language-switcher
        Then: All instances are inside conditional blocks

        Requirements: 14.1
        """
        # Given
        templates = [
            "app/templates/admin/base.html",
            "app/templates/admin/login.html",
            "app/templates/public/care_form.html",
            "app/templates/public/care_log_list.html",
        ]

        for template_path in templates:
            template_file = Path(template_path)
            template_content = template_file.read_text()

            # Count language-switcher occurrences
            switcher_count = template_content.count('id="language-switcher"')

            if switcher_count > 0:
                # Count conditional blocks containing language-switcher
                pattern = (
                    r"{%\s*if\s+not\s+settings\.kiroween_mode\s*%}.*?"
                    r'id="language-switcher".*?'
                    r"{%\s*endif\s*%}"
                )
                conditional_count = len(
                    re.findall(pattern, template_content, re.DOTALL)
                )

                # Then: All switchers should be in conditionals
                assert switcher_count == conditional_count, (
                    f"{template_path} has {switcher_count} language switchers but "
                    f"only {conditional_count} are in conditional blocks"
                )

    def test_language_switcher_comments_present(self):
        """
        正常系: Language switcher sections have comments

        Given: Template files with language switcher
        When: Checking for comments
        Then: Comments explain the language switcher

        Requirements: 14.1
        """
        # Given
        templates = [
            "app/templates/admin/base.html",
            "app/templates/admin/login.html",
        ]

        for template_path in templates:
            template_file = Path(template_path)
            template_content = template_file.read_text()

            if 'id="language-switcher"' in template_content:
                # Then: Comments should exist near language switcher
                # Look for Japanese or English comments about language switching
                assert (
                    "言語" in template_content or "language" in template_content.lower()
                ), f"{template_path} should have comments about language switching"

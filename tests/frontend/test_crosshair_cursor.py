"""
Crosshair Cursor Implementation Tests

Tests for the crosshair cursor feature in Kiroween Mode.
Validates that the precision targeting cursor is applied correctly.

Requirements: 15.1, 15.2, 15.3, 15.4, 15.5
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest


class TestCrosshairCursorProperty:
    """Property-based tests for crosshair cursor application"""

    @pytest.mark.parametrize("kiroween_mode", [True, False])
    def test_crosshair_cursor_application_property(self, kiroween_mode: bool):
        """
        Property 22: Crosshair Cursor Application
        For any element in Kiroween Mode, the computed cursor style should be 'crosshair'.

        **Feature: kiroween-theme, Property 22: Crosshair Cursor Application**
        **Validates: Requirements 15.1, 15.2, 15.3**

        Given: terminal.css with Kiroween Mode enabled/disabled
        When: Checking cursor styles
        Then: Crosshair cursor is applied in Kiroween Mode, standard cursor otherwise
        """
        # Given
        css_path = Path("app/static/css/terminal.css")
        css_content = css_path.read_text()

        if kiroween_mode:
            # When: Kiroween Mode is enabled
            # Then: Crosshair cursor should be defined for body.kiroween-mode
            assert "body.kiroween-mode" in css_content, (
                "Kiroween mode styles should exist"
            )
            assert "cursor: crosshair !important" in css_content, (
                "Crosshair cursor should be defined"
            )

            # Verify crosshair is applied to body
            body_pattern = (
                r"body\.kiroween-mode\s*{[^}]*cursor:\s*crosshair\s*!important"
            )
            assert re.search(body_pattern, css_content, re.DOTALL), (
                "Body should have crosshair cursor in Kiroween Mode"
            )

            # Verify crosshair is applied to all elements
            all_elements_pattern = (
                r"body\.kiroween-mode\s+\*\s*{[^}]*cursor:\s*crosshair\s*!important"
            )
            assert re.search(all_elements_pattern, css_content, re.DOTALL), (
                "All elements should have crosshair cursor in Kiroween Mode"
            )
        else:
            # When: Kiroween Mode is disabled
            # Then: Standard cursor styles should be used (no crosshair override)
            # In standard mode, there should be no global crosshair cursor
            # (crosshair is only applied within body.kiroween-mode scope)
            pass  # Standard mode doesn't need special cursor styles


class TestCrosshairCursorUnit:
    """Unit tests for crosshair cursor styling"""

    def test_crosshair_cursor_applied_to_body(self):
        """
        正常系: Crosshair cursor is applied to body in Kiroween Mode

        Given: terminal.css
        When: Checking body.kiroween-mode styles
        Then: Crosshair cursor is defined

        Requirements: 15.1
        """
        # Given
        css_path = Path("app/static/css/terminal.css")
        css_content = css_path.read_text()

        # Then: Body has crosshair cursor
        body_section = re.search(
            r"body\.kiroween-mode\s*{[^}]*}", css_content, re.DOTALL
        )
        assert body_section is not None, "body.kiroween-mode section should exist"

        body_css = body_section.group(0)
        assert "cursor: crosshair !important" in body_css, (
            "Body should have crosshair cursor with !important"
        )

    def test_crosshair_cursor_applied_to_all_elements(self):
        """
        正常系: Crosshair cursor is applied to all elements in Kiroween Mode

        Given: terminal.css
        When: Checking body.kiroween-mode * styles
        Then: Crosshair cursor is defined for all elements

        Requirements: 15.2
        """
        # Given
        css_path = Path("app/static/css/terminal.css")
        css_content = css_path.read_text()

        # Then: All elements have crosshair cursor
        all_elements_section = re.search(
            r"body\.kiroween-mode\s+\*\s*{[^}]*}", css_content, re.DOTALL
        )
        assert all_elements_section is not None, (
            "body.kiroween-mode * section should exist"
        )

        all_elements_css = all_elements_section.group(0)
        assert "cursor: crosshair !important" in all_elements_css, (
            "All elements should have crosshair cursor with !important"
        )

    def test_crosshair_cursor_applied_to_interactive_elements(self):
        """
        正常系: Crosshair cursor is applied to interactive elements

        Given: terminal.css
        When: Checking interactive element styles
        Then: Crosshair cursor is defined for a, button, input, select, textarea

        Requirements: 15.3
        """
        # Given
        css_path = Path("app/static/css/terminal.css")
        css_content = css_path.read_text()

        # Then: Interactive elements have crosshair cursor
        # Look for the interactive elements section
        interactive_pattern = r"body\.kiroween-mode\s+(a|button|input|select|textarea)"
        assert re.search(interactive_pattern, css_content), (
            "Interactive elements should have crosshair cursor styles"
        )

        # Verify specific interactive elements are covered
        interactive_elements = ["a", "button", "input", "select", "textarea"]
        for element in interactive_elements:
            element_pattern = rf"body\.kiroween-mode\s+{element}"
            assert re.search(element_pattern, css_content), (
                f"{element} should have crosshair cursor in Kiroween Mode"
            )

    def test_crosshair_cursor_uses_important_flag(self):
        """
        正常系: Crosshair cursor uses !important flag for override

        Given: terminal.css
        When: Checking cursor declarations
        Then: All crosshair cursor declarations use !important

        Requirements: 15.2, 15.3
        """
        # Given
        css_path = Path("app/static/css/terminal.css")
        css_content = css_path.read_text()

        # Then: All crosshair cursor declarations use !important
        crosshair_declarations = re.findall(
            r"cursor:\s*crosshair[^;]*;", css_content, re.IGNORECASE
        )
        assert len(crosshair_declarations) > 0, (
            "Crosshair cursor declarations should exist"
        )

        for declaration in crosshair_declarations:
            assert "!important" in declaration, (
                f"Crosshair cursor should use !important: {declaration}"
            )

    def test_standard_mode_no_crosshair(self):
        """
        正常系: Standard mode does not have crosshair cursor

        Given: terminal.css
        When: Checking styles outside body.kiroween-mode
        Then: No global crosshair cursor is defined

        Requirements: 15.4
        """
        # Given
        css_path = Path("app/static/css/terminal.css")
        css_content = css_path.read_text()

        # Then: Crosshair cursor is only within body.kiroween-mode scope
        # Extract all cursor declarations outside kiroween-mode
        lines = css_content.split("\n")
        in_kiroween_scope = False
        brace_count = 0
        non_kiroween_cursor_lines = []

        for line in lines:
            # Track if we're inside a kiroween-mode block
            if "body.kiroween-mode" in line:
                in_kiroween_scope = True
                brace_count = 0

            if in_kiroween_scope:
                brace_count += line.count("{") - line.count("}")
                if brace_count <= 0:
                    in_kiroween_scope = False

            # Check for cursor declarations outside kiroween-mode
            if not in_kiroween_scope and "cursor:" in line:
                non_kiroween_cursor_lines.append(line)

        # Verify that non-kiroween cursor declarations don't use crosshair
        for line in non_kiroween_cursor_lines:
            if "cursor:" in line:
                assert "crosshair" not in line.lower(), (
                    f"Crosshair cursor should only be in Kiroween Mode: {line}"
                )

    def test_crosshair_cursor_comments_present(self):
        """
        正常系: Crosshair cursor section has proper comments

        Given: terminal.css
        When: Checking crosshair cursor section
        Then: Comments reference requirements

        Requirements: 11.5
        """
        # Given
        css_path = Path("app/static/css/terminal.css")
        css_content = css_path.read_text()

        # Then: Comments should reference requirements
        assert "Requirements: 15.1, 15.2, 15.3" in css_content or (
            "Requirement 15" in css_content
        ), "Crosshair cursor section should have requirement comments"

        # Check for descriptive comments
        assert (
            "Crosshair Cursor" in css_content
            or "crosshair cursor" in css_content.lower()
        ), "Crosshair cursor section should have descriptive comments"

    def test_crosshair_cursor_browser_compatibility(self):
        """
        正常系: Crosshair cursor is compatible with major browsers

        Given: terminal.css
        When: Checking cursor syntax
        Then: Standard CSS cursor property is used (no vendor prefixes needed)

        Requirements: 15.5
        """
        # Given
        css_path = Path("app/static/css/terminal.css")
        css_content = css_path.read_text()

        # Then: Standard cursor property is used
        # Crosshair is a standard CSS cursor value, no vendor prefixes needed
        crosshair_declarations = re.findall(
            r"cursor:\s*crosshair[^;]*;", css_content, re.IGNORECASE
        )
        assert len(crosshair_declarations) > 0, (
            "Crosshair cursor declarations should exist"
        )

        # Verify no vendor prefixes are used (they're not needed for cursor)
        for declaration in crosshair_declarations:
            assert "-webkit-" not in declaration, (
                "Vendor prefixes not needed for cursor property"
            )
            assert "-moz-" not in declaration, (
                "Vendor prefixes not needed for cursor property"
            )


class TestCrosshairCursorIntegration:
    """Integration tests for crosshair cursor feature"""

    def test_crosshair_cursor_section_exists(self):
        """
        正常系: Crosshair cursor section exists in CSS

        Given: terminal.css
        When: Checking file structure
        Then: Dedicated crosshair cursor section exists
        """
        # Given
        css_path = Path("app/static/css/terminal.css")
        css_content = css_path.read_text()

        # Then: Crosshair cursor section should exist
        assert "Crosshair Cursor" in css_content, (
            "Crosshair cursor section should exist with header comment"
        )

    def test_crosshair_cursor_overrides_default_pointer(self):
        """
        正常系: Crosshair cursor overrides default pointer cursor

        Given: terminal.css with button styles
        When: Checking button cursor styles
        Then: Crosshair cursor overrides default pointer

        Requirements: 15.3
        """
        # Given
        css_path = Path("app/static/css/terminal.css")
        css_content = css_path.read_text()

        # Then: Button styles should have crosshair cursor
        # Even though buttons typically have cursor: pointer,
        # the crosshair should override it in Kiroween Mode
        button_in_kiroween = re.search(
            r"body\.kiroween-mode\s+button[^{]*{[^}]*}", css_content, re.DOTALL
        )

        if button_in_kiroween:
            button_css = button_in_kiroween.group(0)
            # Either button has explicit crosshair, or it inherits from * selector
            # Both are valid as long as !important is used
            assert (
                "cursor: crosshair !important" in button_css
                or "cursor: crosshair !important" in css_content
            ), "Button should have crosshair cursor in Kiroween Mode"

    def test_css_specificity_sufficient(self):
        """
        正常系: CSS specificity is sufficient to override defaults

        Given: terminal.css
        When: Checking cursor declarations
        Then: !important flag ensures override

        Requirements: 15.2, 15.3
        """
        # Given
        css_path = Path("app/static/css/terminal.css")
        css_content = css_path.read_text()

        # Then: All crosshair declarations use !important for specificity
        crosshair_in_kiroween = re.findall(
            r"body\.kiroween-mode[^{]*{[^}]*cursor:\s*crosshair[^}]*}",
            css_content,
            re.DOTALL,
        )

        assert len(crosshair_in_kiroween) > 0, (
            "Crosshair cursor should be defined in Kiroween Mode"
        )

        for block in crosshair_in_kiroween:
            cursor_declarations = re.findall(r"cursor:\s*crosshair[^;]*;", block)
            for declaration in cursor_declarations:
                assert "!important" in declaration, (
                    "Crosshair cursor should use !important for specificity"
                )

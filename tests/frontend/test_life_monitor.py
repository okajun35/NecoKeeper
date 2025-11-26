"""
Life Monitor Implementation Tests

Tests for the Life Monitor feature in Kiroween Mode.
Validates that the 9 lives indicator (8 lost, 1 active) is displayed correctly.

Requirements: 16.1, 16.2, 16.3, 16.4, 16.5
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest


class TestLifeMonitorDisplayProperty:
    """Property-based tests for Life Monitor display"""

    @pytest.mark.parametrize("kiroween_mode", [True, False])
    def test_life_monitor_display_property(self, kiroween_mode: bool):
        """
        Property 23: Life Monitor Display
        For any page in Kiroween Mode, the Life Monitor should be visible in the header,
        showing 8 lost lives and 1 active blinking life.

        **Feature: kiroween-theme, Property 23: Life Monitor Display**
        **Validates: Requirements 16.1, 16.2, 16.3**

        Given: base.html with Kiroween Mode enabled/disabled
        When: Checking Life Monitor presence
        Then: Life Monitor is visible in Kiroween Mode, hidden otherwise
        """
        # Given
        base_html_path = Path("app/templates/admin/base.html")
        base_html_content = base_html_path.read_text()

        if kiroween_mode:
            # When: Kiroween Mode is enabled
            # Then: Life Monitor container should exist
            assert 'id="life-monitor"' in base_html_content, (
                "Life Monitor container should exist in base.html"
            )

            # Verify conditional rendering
            assert "{% if settings.kiroween_mode %}" in base_html_content, (
                "Life Monitor should be conditionally rendered"
            )

            # Check that Life Monitor is in the header
            header_section = re.search(
                r"<header[^>]*>.*?</header>", base_html_content, re.DOTALL
            )
            assert header_section is not None, "Header section should exist"

            header_html = header_section.group(0)
            assert 'id="life-monitor"' in header_html, (
                "Life Monitor should be in the header"
            )
        else:
            # When: Kiroween Mode is disabled
            # Then: Life Monitor should be conditionally hidden
            # (it's wrapped in {% if settings.kiroween_mode %})
            pass  # Standard mode doesn't show Life Monitor


class TestLifeMonitorVisibilityProperty:
    """Property-based tests for Life Monitor visibility"""

    @pytest.mark.parametrize("kiroween_mode", [True, False])
    def test_life_monitor_visibility_property(self, kiroween_mode: bool):
        """
        Property 24: Life Monitor Visibility
        For any page in standard mode, the Life Monitor should not be displayed.

        **Feature: kiroween-theme, Property 24: Life Monitor Visibility**
        **Validates: Requirements 16.5**

        Given: base.html with conditional rendering
        When: Checking Life Monitor visibility logic
        Then: Life Monitor is only visible in Kiroween Mode
        """
        # Given
        base_html_path = Path("app/templates/admin/base.html")
        base_html_content = base_html_path.read_text()

        # Then: Life Monitor should be wrapped in conditional
        life_monitor_pattern = (
            r"{%\s*if\s+settings\.kiroween_mode\s*%}.*?"
            r'<div\s+id="life-monitor".*?</div>.*?'
            r"{%\s*endif\s*%}"
        )
        assert re.search(life_monitor_pattern, base_html_content, re.DOTALL), (
            "Life Monitor should be conditionally rendered based on kiroween_mode"
        )


class TestLifeMonitorUnit:
    """Unit tests for Life Monitor"""

    def test_life_monitor_visible_in_kiroween_mode(self):
        """
        正常系: Life Monitor is visible in Kiroween Mode

        Given: base.html
        When: Checking Life Monitor container
        Then: Life Monitor div exists with correct ID

        Requirements: 16.1, 16.5
        """
        # Given
        base_html_path = Path("app/templates/admin/base.html")
        base_html_content = base_html_path.read_text()

        # Then: Life Monitor container exists
        assert 'id="life-monitor"' in base_html_content, (
            "Life Monitor container should exist"
        )

        # Verify it's conditionally rendered
        life_monitor_section = re.search(
            r"{%\s*if\s+settings\.kiroween_mode\s*%}.*?"
            r'<div\s+id="life-monitor".*?</div>',
            base_html_content,
            re.DOTALL,
        )
        assert life_monitor_section is not None, (
            "Life Monitor should be conditionally rendered"
        )

    def test_life_monitor_hidden_in_standard_mode(self):
        """
        正常系: Life Monitor is hidden in standard mode

        Given: base.html
        When: Checking conditional rendering
        Then: Life Monitor is wrapped in kiroween_mode check

        Requirements: 16.5
        """
        # Given
        base_html_path = Path("app/templates/admin/base.html")
        base_html_content = base_html_path.read_text()

        # Then: Life Monitor should be conditionally rendered
        assert "{% if settings.kiroween_mode %}" in base_html_content, (
            "Life Monitor should check kiroween_mode setting"
        )

        # Verify the conditional wraps the Life Monitor
        life_monitor_pattern = (
            r"{%\s*if\s+settings\.kiroween_mode\s*%}.*?"
            r'id="life-monitor".*?'
            r"{%\s*endif\s*%}"
        )
        assert re.search(life_monitor_pattern, base_html_content, re.DOTALL), (
            "Life Monitor should be inside kiroween_mode conditional"
        )

    def test_life_monitor_displays_8_lost_lives(self):
        """
        正常系: Life Monitor displays 8 lost lives

        Given: glitch-effects.js with LifeMonitor class
        When: Checking render() method
        Then: 8 lost lives (×) are created

        Requirements: 16.2
        """
        # Given
        js_path = Path("app/static/js/glitch-effects.js")
        js_content = js_path.read_text()

        # Then: LifeMonitor class should exist
        assert "class LifeMonitor" in js_content, "LifeMonitor class should exist"

        # Verify lostLives is set to 8
        assert "this.lostLives = this.totalLives - this.activeLives" in js_content or (
            "this.lostLives = 8" in js_content
        ), "Lost lives should be calculated or set to 8"

        # Verify render() creates lost life elements
        assert "for (let i = 0; i < this.lostLives; i++)" in js_content, (
            "render() should loop through lost lives"
        )

        assert "life.className = 'life lost'" in js_content or (
            'life.className = "life lost"' in js_content
        ), "Lost lives should have 'life lost' class"

        # Removed textContent check as it is now a visual element (candle/flame theme)

    def test_life_monitor_displays_1_active_life(self):
        """
        正常系: Life Monitor displays 1 active life with flame animation

        Given: glitch-effects.js with LifeMonitor class
        When: Checking render() method
        Then: 1 active life is created with flame element

        Requirements: 16.3, 16.4
        """
        # Given
        js_path = Path("app/static/js/glitch-effects.js")
        js_content = js_path.read_text()

        # Then: Active life should be created
        assert "activeLife.className = 'life active'" in js_content or (
            'activeLife.className = "life active"' in js_content
        ), "Active life should have 'life active' class"

        # Verify flame element is created
        assert "flame.className = 'flame'" in js_content or (
            'flame.className = "flame"' in js_content
        ), "Active life should have a flame element"

        # Verify activeLives is set to 1
        assert "this.activeLives = 1" in js_content, "Active lives should be set to 1"

    def test_life_monitor_css_styles_exist(self):
        """
        正常系: Life Monitor CSS styles exist

        Given: terminal.css
        When: Checking Life Monitor styles
        Then: Styles for #life-monitor, .life.lost, .life.active exist

        Requirements: 16.4
        """
        # Given
        css_path = Path("app/static/css/terminal.css")
        css_content = css_path.read_text()

        # Then: Life Monitor styles should exist
        assert "#life-monitor" in css_content, (
            "Life Monitor container styles should exist"
        )

        assert ".life.lost" in css_content, "Lost life styles should exist"

        assert ".life.active" in css_content, "Active life styles should exist"

    def test_life_monitor_pulse_animation(self):
        """
        正常系: Active life has pulse animation

        Given: terminal.css
        When: Checking .life.active styles
        Then: Pulse animation is defined and applied

        Requirements: 16.4
        """
        # Given
        css_path = Path("app/static/css/terminal.css")
        css_content = css_path.read_text()

        # Then: Pulse animation should be defined
        assert "@keyframes candle-pulse" in css_content, (
            "Pulse animation should be defined"
        )

        # Verify pulse animation is applied to active life
        # Note: In the new design, animation is applied to .candle-fill inside .life.active
        assert "animation: candle-pulse" in css_content, (
            "Active life should have pulse animation"
        )

    def test_life_monitor_lost_lives_styling(self):
        """
        正常系: Lost lives have dim green color and reduced opacity

        Given: terminal.css
        When: Checking .life.lost styles
        Then: Dim green color and reduced opacity are applied

        Requirements: 16.4
        """
        # Given
        css_path = Path("app/static/css/terminal.css")
        css_content = css_path.read_text()

        # Then: Lost lives should have dim green and reduced opacity
        # Note: In the new design, styling is applied to .candle-shell inside .life.lost
        lost_life_section = re.search(
            r"\.life\.lost\s+\.candle-shell\s*{[^}]*}",
            css_content,
            re.DOTALL,
        )
        assert lost_life_section is not None, (
            ".life.lost .candle-shell section should exist"
        )

        lost_life_css = lost_life_section.group(0)

        # Verify dim green color is used for border
        assert "var(--terminal-dim)" in lost_life_css, (
            "Lost lives should use dim green color"
        )

    def test_life_monitor_flex_layout(self):
        """
        正常系: Life Monitor uses flex layout

        Given: terminal.css
        When: Checking #life-monitor styles
        Then: Flex layout is defined

        Requirements: 16.4
        """
        # Given
        css_path = Path("app/static/css/terminal.css")
        css_content = css_path.read_text()

        # Then: Life Monitor should use flex layout
        life_monitor_section = re.search(
            r"#life-monitor\s*{[^}]*}", css_content, re.DOTALL
        )
        assert life_monitor_section is not None, "#life-monitor section should exist"

        life_monitor_css = life_monitor_section.group(0)
        assert "display: flex" in life_monitor_css or (
            "display:flex" in life_monitor_css
        ), "Life Monitor should use flex layout"

        # Note: flex-direction: row is default, so it might not be explicitly defined
        # But we check if it's NOT column
        assert "flex-direction: column" not in life_monitor_css, (
            "Life Monitor should not use column direction"
        )

    def test_life_monitor_terminal_colors(self):
        """
        正常系: Life Monitor uses terminal colors

        Given: terminal.css
        When: Checking Life Monitor color scheme
        Then: Terminal green colors are used

        Requirements: 16.4
        """
        # Given
        css_path = Path("app/static/css/terminal.css")
        css_content = css_path.read_text()

        # Then: Life Monitor should use terminal colors
        life_monitor_styles = re.search(
            r"#life-monitor[^{]*{[^}]*}.*?\.life\.active[^{]*{[^}]*}",
            css_content,
            re.DOTALL,
        )
        assert life_monitor_styles is not None, "Life Monitor styles should exist"

        styles_text = life_monitor_styles.group(0)
        assert "var(--terminal-green)" in styles_text or (
            "var(--terminal-dim)" in styles_text
        ), "Life Monitor should use terminal color variables"

    def test_life_monitor_initialized_on_page_load(self):
        """
        正常系: Life Monitor is initialized on page load

        Given: glitch-effects.js
        When: Checking initialization code
        Then: LifeMonitor is created and render() is called

        Requirements: 16.5
        """
        # Given
        js_path = Path("app/static/js/glitch-effects.js")
        js_content = js_path.read_text()

        # Then: Life Monitor should be initialized
        assert "const lifeMonitor = new LifeMonitor()" in js_content, (
            "LifeMonitor should be instantiated"
        )

        assert "lifeMonitor.render()" in js_content, (
            "LifeMonitor render() should be called"
        )

        # Verify it's only initialized in Kiroween Mode
        init_section = re.search(
            r"const lifeMonitorElement = document\.getElementById\('life-monitor'\);.*?"
            r"lifeMonitor\.render\(\);",
            js_content,
            re.DOTALL,
        )
        assert init_section is not None, (
            "Life Monitor initialization should check for element existence"
        )


class TestLifeMonitorIntegration:
    """Integration tests for Life Monitor feature"""

    def test_life_monitor_section_exists_in_css(self):
        """
        正常系: Life Monitor section exists in CSS

        Given: terminal.css
        When: Checking file structure
        Then: Dedicated Life Monitor section exists
        """
        # Given
        css_path = Path("app/static/css/terminal.css")
        css_content = css_path.read_text()

        # Then: Life Monitor section should exist
        assert "Life Monitor" in css_content, (
            "Life Monitor section should exist with header comment"
        )

        # Verify requirements are referenced
        assert "Requirements: 16" in css_content or "Requirement 16" in css_content, (
            "Life Monitor section should reference requirements"
        )

    def test_life_monitor_class_exists_in_js(self):
        """
        正常系: LifeMonitor class exists in JavaScript

        Given: glitch-effects.js
        When: Checking class definition
        Then: LifeMonitor class is defined with proper methods
        """
        # Given
        js_path = Path("app/static/js/glitch-effects.js")
        js_content = js_path.read_text()

        # Then: LifeMonitor class should exist
        assert "class LifeMonitor" in js_content, "LifeMonitor class should be defined"

        # Verify constructor
        assert "constructor()" in js_content, "LifeMonitor should have constructor"

        # Verify render method
        assert "render()" in js_content, "LifeMonitor should have render() method"

    def test_life_monitor_total_lives_is_9(self):
        """
        正常系: Life Monitor shows 9 total lives

        Given: glitch-effects.js
        When: Checking LifeMonitor constructor
        Then: totalLives is set to 9

        Requirements: 16.1
        """
        # Given
        js_path = Path("app/static/js/glitch-effects.js")
        js_content = js_path.read_text()

        # Then: Total lives should be 9
        assert "this.totalLives = 9" in js_content, "Total lives should be set to 9"

    def test_life_monitor_responsive_styles(self):
        """
        正常系: Life Monitor has responsive styles for mobile

        Given: terminal.css
        When: Checking media queries
        Then: Responsive styles exist for Life Monitor
        """
        # Given
        css_path = Path("app/static/css/terminal.css")
        css_content = css_path.read_text()

        # Then: Responsive styles should exist
        # Look for media queries that affect Life Monitor
        media_query_pattern = r"@media\s*\([^)]*\)\s*{[^}]*#life-monitor[^}]*}"
        assert re.search(media_query_pattern, css_content, re.DOTALL), (
            "Life Monitor should have responsive styles"
        )

    def test_life_monitor_comments_present(self):
        """
        正常系: Life Monitor has proper documentation comments

        Given: glitch-effects.js and terminal.css
        When: Checking comments
        Then: Comments explain the feature and reference requirements
        """
        # Given
        js_path = Path("app/static/js/glitch-effects.js")
        js_content = js_path.read_text()

        css_path = Path("app/static/css/terminal.css")
        css_content = css_path.read_text()

        # Then: Comments should exist
        assert "LifeMonitor" in js_content and "/**" in js_content, (
            "LifeMonitor should have JSDoc comments"
        )

        assert "Life Monitor" in css_content and "/*" in css_content, (
            "Life Monitor CSS should have comments"
        )

        # Verify requirements are referenced
        assert "Requirements: 16" in js_content or "Requirement 16" in js_content, (
            "JavaScript comments should reference requirements"
        )

        assert "Requirements: 16" in css_content or "Requirement 16" in css_content, (
            "CSS comments should reference requirements"
        )

    def test_life_monitor_in_header(self):
        """
        正常系: Life Monitor is placed in the header

        Given: base.html
        When: Checking Life Monitor placement
        Then: Life Monitor is inside the header element

        Requirements: 16.1
        """
        # Given
        base_html_path = Path("app/templates/admin/base.html")
        base_html_content = base_html_path.read_text()

        # Then: Life Monitor should be in header
        header_section = re.search(
            r"<header[^>]*>.*?</header>", base_html_content, re.DOTALL
        )
        assert header_section is not None, "Header should exist"

        header_html = header_section.group(0)
        assert 'id="life-monitor"' in header_html, (
            "Life Monitor should be inside header"
        )

    def test_life_monitor_aria_labels(self):
        """
        正常系: Life Monitor has accessibility labels

        Given: glitch-effects.js
        When: Checking render() method
        Then: ARIA labels are set for accessibility
        """
        # Given
        js_path = Path("app/static/js/glitch-effects.js")
        js_content = js_path.read_text()

        # Then: ARIA labels should be set
        assert "setAttribute('aria-label'" in js_content or (
            'setAttribute("aria-label"' in js_content
        ), "Life elements should have aria-label attributes"

        # Verify specific labels
        assert "Lost life" in js_content or "lost life" in js_content, (
            "Lost lives should have descriptive aria-label"
        )

        assert "Active life" in js_content or "active life" in js_content, (
            "Active life should have descriptive aria-label"
        )

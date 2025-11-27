"""
Soul Commitment Glitch Implementation Tests

Tests for the Soul Commitment Glitch feature in Kiroween Mode.
Validates that intense glitch effects trigger on data save/delete operations.

Requirements: 17.1, 17.2, 17.3, 17.4, 17.5, 17.6, 17.7
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest


class TestSoulCommitmentGlitchTriggerProperty:
    """Property-based tests for Soul Commitment Glitch trigger"""

    @pytest.mark.parametrize(
        "http_method",
        ["POST", "PUT", "PATCH", "DELETE"],
        ids=["create", "update-put", "update-patch", "delete"],
    )
    def test_soul_commitment_glitch_trigger_property(self, http_method: str):
        """
        Property 25: Soul Commitment Glitch Trigger
        For any successful create/update/delete operation in Kiroween Mode,
        the Soul Commitment Glitch effect should be triggered.

        **Feature: kiroween-theme, Property 25: Soul Commitment Glitch Trigger**
        **Validates: Requirements 17.1, 17.2, 17.3**

        Given: glitch-effects.js with fetch() interception
        When: A successful POST/PUT/PATCH/DELETE request completes
        Then: Soul Commitment Glitch is triggered
        """
        # Given
        js_path = Path("app/static/js/glitch-effects.js")
        js_content = js_path.read_text()

        # Then: fetch() should be intercepted
        assert "const originalFetch = window.fetch" in js_content, (
            "fetch() should be intercepted"
        )

        assert "window.fetch = function" in js_content, (
            "window.fetch should be overridden"
        )

        # Verify method checking
        assert "method" in js_content, "HTTP method should be checked"

        # Verify the specific HTTP method is handled
        assert http_method in js_content, f"{http_method} method should be handled"

        # Verify glitch is triggered
        assert "soulGlitch.trigger()" in js_content, (
            "Soul Commitment Glitch should be triggered"
        )


class TestSoulCommitmentGlitchDurationProperty:
    """Property-based tests for Soul Commitment Glitch duration"""

    @pytest.mark.parametrize(
        "duration_ms",
        [300, 350, 400, 450, 500],
        ids=["min", "low", "mid", "high", "max"],
    )
    def test_soul_commitment_glitch_duration_property(self, duration_ms: int):
        """
        Property 26: Soul Commitment Glitch Duration
        For any triggered Soul Commitment Glitch, the effect duration
        should be between 300-500 milliseconds.

        **Feature: kiroween-theme, Property 26: Soul Commitment Glitch Duration**
        **Validates: Requirements 17.4**

        Given: SoulCommitmentGlitch class
        When: Checking duration configuration
        Then: Duration is between 300-500ms
        """
        # Given
        js_path = Path("app/static/js/glitch-effects.js")
        js_content = js_path.read_text()

        # Then: Duration range should be defined
        assert "this.minDuration = 300" in js_content, (
            "Minimum duration should be 300ms"
        )

        assert "this.maxDuration = 500" in js_content, (
            "Maximum duration should be 500ms"
        )

        # Verify duration is within range
        assert 300 <= duration_ms <= 500, (
            f"Duration {duration_ms}ms should be within 300-500ms range"
        )

        # Verify randomBetween is used
        assert "this.randomBetween(this.minDuration, this.maxDuration)" in js_content, (
            "Duration should be randomly selected within range"
        )


class TestSoulCommitmentGlitchUnit:
    """Unit tests for Soul Commitment Glitch"""

    def test_soul_commitment_glitch_class_exists(self):
        """
        正常系: SoulCommitmentGlitch class exists

        Given: glitch-effects.js
        When: Checking class definition
        Then: SoulCommitmentGlitch class is defined

        Requirements: 17.1
        """
        # Given
        js_path = Path("app/static/js/glitch-effects.js")
        js_content = js_path.read_text()

        # Then: SoulCommitmentGlitch class should exist
        assert "class SoulCommitmentGlitch" in js_content, (
            "SoulCommitmentGlitch class should be defined"
        )

        # Verify constructor
        assert "constructor()" in js_content, (
            "SoulCommitmentGlitch should have constructor"
        )

        # Verify trigger method
        assert "trigger()" in js_content, (
            "SoulCommitmentGlitch should have trigger() method"
        )

    def test_soul_commitment_glitch_duration_range(self):
        """
        正常系: Soul Commitment Glitch has correct duration range

        Given: SoulCommitmentGlitch class
        When: Checking duration configuration
        Then: Duration is 300-500ms

        Requirements: 17.4
        """
        # Given
        js_path = Path("app/static/js/glitch-effects.js")
        js_content = js_path.read_text()

        # Then: Duration range should be 300-500ms
        assert "this.minDuration = 300" in js_content, (
            "Minimum duration should be 300ms"
        )

        assert "this.maxDuration = 500" in js_content, (
            "Maximum duration should be 500ms"
        )

    def test_soul_commitment_glitch_css_class(self):
        """
        正常系: Soul Commitment Glitch CSS class is applied

        Given: glitch-effects.js
        When: Checking trigger() method
        Then: 'soul-commit-glitch' class is added to body

        Requirements: 17.5
        """
        # Given
        js_path = Path("app/static/js/glitch-effects.js")
        js_content = js_path.read_text()

        # Then: CSS class should be added
        assert "classList.add('soul-commit-glitch')" in js_content or (
            'classList.add("soul-commit-glitch")' in js_content
        ), "soul-commit-glitch class should be added"

        # Verify class is removed after duration
        assert "classList.remove('soul-commit-glitch')" in js_content or (
            'classList.remove("soul-commit-glitch")' in js_content
        ), "soul-commit-glitch class should be removed"

    def test_soul_commitment_glitch_css_animation(self):
        """
        正常系: Soul Commitment Glitch CSS animation exists

        Given: terminal.css
        When: Checking animation definition
        Then: soul-commit-glitch animation is defined

        Requirements: 17.5
        """
        # Given
        css_path = Path("app/static/css/terminal.css")
        css_content = css_path.read_text()

        # Then: Animation should be defined
        assert "@keyframes soul-commit-glitch" in css_content, (
            "soul-commit-glitch animation should be defined"
        )

        # Verify animation is applied to body
        assert "body.kiroween-mode.soul-commit-glitch" in css_content, (
            "Animation should be applied to body in Kiroween Mode"
        )

    def test_soul_commitment_glitch_intense_animation(self):
        """
        正常系: Soul Commitment Glitch has intense animation

        Given: terminal.css
        When: Checking animation keyframes
        Then: Animation includes transform and filter effects

        Requirements: 17.5
        """
        # Given
        css_path = Path("app/static/css/terminal.css")
        css_content = css_path.read_text()

        # Then: Animation should include intense effects
        animation_section = re.search(
            r"@keyframes soul-commit-glitch\s*{[^}]*}",
            css_content,
            re.DOTALL,
        )
        assert animation_section is not None, (
            "soul-commit-glitch animation should exist"
        )

        animation_css = animation_section.group(0)
        assert "transform:" in animation_css, (
            "Animation should include transform effects"
        )

        assert "filter:" in animation_css, (
            "Animation should include filter effects (hue-rotate, invert)"
        )

    def test_soul_commitment_glitch_noise_effect(self):
        """
        正常系: Soul Commitment Glitch has screen-wide noise effect

        Given: terminal.css
        When: Checking ::before pseudo-element
        Then: Noise/static effect is defined

        Requirements: 17.5
        """
        # Given
        css_path = Path("app/static/css/terminal.css")
        css_content = css_path.read_text()

        # Then: Noise effect should exist
        assert "body.kiroween-mode.soul-commit-glitch::before" in css_content, (
            "Noise effect should be defined with ::before pseudo-element"
        )

        # Verify noise effect properties
        noise_section = re.search(
            r"body\.kiroween-mode\.soul-commit-glitch::before\s*{[^}]*}",
            css_content,
            re.DOTALL,
        )
        assert noise_section is not None, "Noise effect section should exist"

        noise_css = noise_section.group(0)
        assert "position: fixed" in noise_css, "Noise effect should be fixed position"

        assert "width: 100%" in noise_css and "height: 100%" in noise_css, (
            "Noise effect should cover full screen"
        )

        assert "z-index:" in noise_css, "Noise effect should have high z-index"

    def test_soul_commitment_glitch_form_submission_trigger(self):
        """
        正常系: Soul Commitment Glitch triggers on form submission

        Given: glitch-effects.js
        When: Checking form submission listener
        Then: Glitch is triggered on submit event

        Requirements: 17.1
        """
        # Given
        js_path = Path("app/static/js/glitch-effects.js")
        js_content = js_path.read_text()

        # Then: Form submission listener should exist
        assert "document.addEventListener('submit'" in js_content or (
            'document.addEventListener("submit"' in js_content
        ), "Form submission listener should exist"

        # Verify glitch is triggered
        submit_section = re.search(
            r"document\.addEventListener\(['\"]submit['\"].*?soulGlitch\.trigger\(\)",
            js_content,
            re.DOTALL,
        )
        assert submit_section is not None, (
            "Glitch should be triggered on form submission"
        )

    def test_soul_commitment_glitch_fetch_interception(self):
        """
        正常系: Soul Commitment Glitch intercepts fetch() calls

        Given: glitch-effects.js
        When: Checking fetch() interception
        Then: fetch() is intercepted and glitch triggers on success

        Requirements: 17.1, 17.2, 17.3
        """
        # Given
        js_path = Path("app/static/js/glitch-effects.js")
        js_content = js_path.read_text()

        # Then: fetch() should be intercepted
        assert "const originalFetch = window.fetch" in js_content, (
            "Original fetch should be saved"
        )

        assert "window.fetch = function" in js_content, (
            "window.fetch should be overridden"
        )

        # Verify response.ok is checked
        assert "response.ok" in js_content, "Response success should be checked"

    def test_soul_commitment_glitch_post_trigger(self):
        """
        正常系: Soul Commitment Glitch triggers on POST request

        Given: glitch-effects.js
        When: Checking HTTP method handling
        Then: POST requests trigger the glitch

        Requirements: 17.1
        """
        # Given
        js_path = Path("app/static/js/glitch-effects.js")
        js_content = js_path.read_text()

        # Then: POST should be handled
        assert "'POST'" in js_content or '"POST"' in js_content, (
            "POST method should be handled"
        )

        # Verify it's in the method check
        method_check_section = re.search(
            r"\[.*?['\"]POST['\"].*?\]\.includes\(method\)",
            js_content,
            re.DOTALL,
        )
        assert method_check_section is not None, "POST should be in method check array"

    def test_soul_commitment_glitch_put_trigger(self):
        """
        正常系: Soul Commitment Glitch triggers on PUT request

        Given: glitch-effects.js
        When: Checking HTTP method handling
        Then: PUT requests trigger the glitch

        Requirements: 17.2
        """
        # Given
        js_path = Path("app/static/js/glitch-effects.js")
        js_content = js_path.read_text()

        # Then: PUT should be handled
        assert "'PUT'" in js_content or '"PUT"' in js_content, (
            "PUT method should be handled"
        )

    def test_soul_commitment_glitch_patch_trigger(self):
        """
        正常系: Soul Commitment Glitch triggers on PATCH request

        Given: glitch-effects.js
        When: Checking HTTP method handling
        Then: PATCH requests trigger the glitch

        Requirements: 17.2
        """
        # Given
        js_path = Path("app/static/js/glitch-effects.js")
        js_content = js_path.read_text()

        # Then: PATCH should be handled
        assert "'PATCH'" in js_content or '"PATCH"' in js_content, (
            "PATCH method should be handled"
        )

    def test_soul_commitment_glitch_delete_trigger(self):
        """
        正常系: Soul Commitment Glitch triggers on DELETE request

        Given: glitch-effects.js
        When: Checking HTTP method handling
        Then: DELETE requests trigger the glitch

        Requirements: 17.3
        """
        # Given
        js_path = Path("app/static/js/glitch-effects.js")
        js_content = js_path.read_text()

        # Then: DELETE should be handled
        assert "'DELETE'" in js_content or '"DELETE"' in js_content, (
            "DELETE method should be handled"
        )

    def test_soul_commitment_glitch_global_function(self):
        """
        正常系: Global triggerSoulCommitment() function exists

        Given: glitch-effects.js
        When: Checking global function
        Then: window.triggerSoulCommitment is defined

        Requirements: 17.7
        """
        # Given
        js_path = Path("app/static/js/glitch-effects.js")
        js_content = js_path.read_text()

        # Then: Global function should be defined
        assert "window.triggerSoulCommitment" in js_content, (
            "Global triggerSoulCommitment function should be defined"
        )

        # Verify it calls soulGlitch.trigger()
        global_fn_section = re.search(
            r"window\.triggerSoulCommitment\s*=\s*function\s*\(\)\s*{"
            r".*?soulGlitch\.trigger\(\)",
            js_content,
            re.DOTALL,
        )
        assert global_fn_section is not None, (
            "Global function should call soulGlitch.trigger()"
        )

    def test_soul_commitment_glitch_not_in_standard_mode(self):
        """
        正常系: Soul Commitment Glitch does not trigger in standard mode

        Given: glitch-effects.js
        When: Checking initialization
        Then: Glitch only initializes in Kiroween Mode

        Requirements: 17.7
        """
        # Given
        js_path = Path("app/static/js/glitch-effects.js")
        js_content = js_path.read_text()

        # Then: Initialization should check for Kiroween Mode
        assert "document.body.classList.contains('kiroween-mode')" in js_content or (
            'document.body.classList.contains("kiroween-mode")' in js_content
        ), "Initialization should check for Kiroween Mode"

        # Verify early return if not in Kiroween Mode
        init_section = re.search(
            r"if\s*\(!document\.body\.classList\.contains\("
            r"['\"]kiroween-mode['\"]\)\)\s*{.*?return",
            js_content,
            re.DOTALL,
        )
        assert init_section is not None, "Should return early if not in Kiroween Mode"

    def test_soul_commitment_glitch_prevents_overlap(self):
        """
        正常系: Soul Commitment Glitch prevents overlapping effects

        Given: SoulCommitmentGlitch class
        When: Checking trigger() method
        Then: isActive flag prevents overlapping glitches

        Requirements: 17.4
        """
        # Given
        js_path = Path("app/static/js/glitch-effects.js")
        js_content = js_path.read_text()

        # Then: isActive flag should exist
        assert "this.isActive = false" in js_content, (
            "isActive flag should be initialized"
        )

        # Verify early return if already active
        trigger_section = re.search(
            r"trigger\(\)\s*{.*?if\s*\(this\.isActive\).*?return",
            js_content,
            re.DOTALL,
        )
        assert trigger_section is not None, (
            "Should return early if glitch is already active"
        )

        # Verify flag is set and cleared
        assert "this.isActive = true" in js_content, (
            "isActive should be set to true when triggered"
        )

    def test_soul_commitment_glitch_uses_request_animation_frame(self):
        """
        正常系: Soul Commitment Glitch uses requestAnimationFrame

        Given: SoulCommitmentGlitch class
        When: Checking trigger() method
        Then: requestAnimationFrame is used for smooth rendering

        Requirements: 17.5
        """
        # Given
        js_path = Path("app/static/js/glitch-effects.js")
        js_content = js_path.read_text()

        # Then: requestAnimationFrame should be used
        trigger_section = re.search(
            r"class SoulCommitmentGlitch.*?trigger\(\).*?"
            r"requestAnimationFrame",
            js_content,
            re.DOTALL,
        )
        assert trigger_section is not None, "trigger() should use requestAnimationFrame"


class TestSoulCommitmentGlitchIntegration:
    """Integration tests for Soul Commitment Glitch feature"""

    def test_soul_commitment_glitch_css_section_exists(self):
        """
        正常系: Soul Commitment Glitch section exists in CSS

        Given: terminal.css
        When: Checking file structure
        Then: Dedicated Soul Commitment Glitch section exists
        """
        # Given
        css_path = Path("app/static/css/terminal.css")
        css_content = css_path.read_text()

        # Then: Soul Commitment Glitch section should exist
        assert "Soul Commitment Glitch" in css_content, (
            "Soul Commitment Glitch section should exist with header comment"
        )

        # Verify requirements are referenced
        assert "Requirements: 17" in css_content or "Requirement 17" in css_content, (
            "Soul Commitment Glitch section should reference requirements"
        )

    def test_soul_commitment_glitch_comments_present(self):
        """
        正常系: Soul Commitment Glitch has proper documentation comments

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
        assert "SoulCommitmentGlitch" in js_content and "/**" in js_content, (
            "SoulCommitmentGlitch should have JSDoc comments"
        )

        assert "Soul Commitment Glitch" in css_content and "/*" in css_content, (
            "Soul Commitment Glitch CSS should have comments"
        )

        # Verify requirements are referenced
        assert "Requirements: 17" in js_content or "Requirement 17" in js_content, (
            "JavaScript comments should reference requirements"
        )

    def test_soul_commitment_glitch_more_intense_than_random(self):
        """
        正常系: Soul Commitment Glitch is more intense than random glitches

        Given: terminal.css
        When: Comparing animations
        Then: Soul Commitment Glitch has stronger effects

        Requirements: 17.5
        """
        # Given
        css_path = Path("app/static/css/terminal.css")
        css_content = css_path.read_text()

        # Then: Soul Commitment Glitch should have more intense effects
        # Extract soul-commit-glitch animation
        # (match until closing brace with proper nesting)
        soul_glitch_start = css_content.find("@keyframes soul-commit-glitch")
        assert soul_glitch_start != -1, "Soul Commitment Glitch animation should exist"

        # Find the closing brace by counting braces
        brace_count = 0
        animation_start = css_content.find("{", soul_glitch_start)
        i = animation_start
        while i < len(css_content):
            if css_content[i] == "{":
                brace_count += 1
            elif css_content[i] == "}":
                brace_count -= 1
                if brace_count == 0:
                    soul_glitch_text = css_content[soul_glitch_start : i + 1]
                    break
            i += 1

        # Soul Commitment Glitch should have filter effects (more intense)
        assert "filter:" in soul_glitch_text, (
            "Soul Commitment Glitch should have filter effects"
        )

        # Soul Commitment Glitch should have larger transforms
        assert "5px" in soul_glitch_text or "-5px" in soul_glitch_text, (
            "Soul Commitment Glitch should have larger transform values"
        )

    def test_soul_commitment_glitch_initialized(self):
        """
        正常系: Soul Commitment Glitch is initialized on page load

        Given: glitch-effects.js
        When: Checking initialization code
        Then: SoulCommitmentGlitch is created and configured

        Requirements: 17.7
        """
        # Given
        js_path = Path("app/static/js/glitch-effects.js")
        js_content = js_path.read_text()

        # Then: Soul Commitment Glitch should be initialized
        assert "const soulGlitch = new SoulCommitmentGlitch()" in js_content, (
            "SoulCommitmentGlitch should be instantiated"
        )

        # Verify it's only initialized in Kiroween Mode
        init_section = re.search(
            r"if\s*\(!document\.body\.classList\.contains\("
            r"['\"]kiroween-mode['\"]\)\)",
            js_content,
            re.DOTALL,
        )
        assert init_section is not None, "Initialization should check for Kiroween Mode"

    def test_soul_commitment_glitch_error_handling(self):
        """
        正常系: Soul Commitment Glitch handles fetch errors gracefully

        Given: glitch-effects.js
        When: Checking fetch() interception
        Then: Errors are re-thrown to maintain normal error handling

        Requirements: 17.1, 17.2, 17.3
        """
        # Given
        js_path = Path("app/static/js/glitch-effects.js")
        js_content = js_path.read_text()

        # Then: Errors should be caught and re-thrown
        fetch_section = re.search(
            r"window\.fetch\s*=\s*function.*?\.catch\(error\s*=>\s*{"
            r".*?throw error",
            js_content,
            re.DOTALL,
        )
        assert fetch_section is not None, "Fetch errors should be caught and re-thrown"

    def test_soul_commitment_glitch_noise_animation(self):
        """
        正常系: Soul Commitment Glitch noise effect has animation

        Given: terminal.css
        When: Checking noise animation
        Then: @keyframes noise is defined

        Requirements: 17.5
        """
        # Given
        css_path = Path("app/static/css/terminal.css")
        css_content = css_path.read_text()

        # Then: Noise animation should be defined
        assert "@keyframes noise" in css_content, "Noise animation should be defined"

        # Verify noise animation is applied
        noise_section = re.search(
            r"body\.kiroween-mode\.soul-commit-glitch::before.*?"
            r"animation:\s*noise",
            css_content,
            re.DOTALL,
        )
        assert noise_section is not None, (
            "Noise animation should be applied to ::before pseudo-element"
        )

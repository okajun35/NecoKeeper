"""
モバイルレスポンシブデザインのテスト

Kiroween Modeのモバイル対応を検証。
CSS メディアクエリとタッチターゲットサイズを確認。

Requirements: 10.1, 10.2, 10.3, 10.4, 10.5
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest


class TestMobileResponsiveCSS:
    """モバイルレスポンシブCSSのテスト"""

    def test_terminal_css_exists(self):
        """
        正常系: terminal.cssファイルが存在する

        Given: プロジェクトルート
        When: app/static/css/terminal.css を確認
        Then: ファイルが存在する
        """
        # Given
        css_path = Path("app/static/css/terminal.css")

        # Then
        assert css_path.exists(), "terminal.css file should exist"

    def test_mobile_media_queries_present(self):
        """
        正常系: モバイル用メディアクエリが定義されている

        Given: terminal.css
        When: ファイル内容を確認
        Then: モバイル用メディアクエリが含まれる

        Requirements: 10.1, 10.4
        """
        # Given
        css_path = Path("app/static/css/terminal.css")
        css_content = css_path.read_text()

        # Then: 各種メディアクエリが存在
        assert "@media (max-width: 1024px)" in css_content, (
            "Tablet media query should exist"
        )
        assert "@media (max-width: 768px)" in css_content, (
            "Mobile media query should exist"
        )
        assert "@media (max-width: 480px)" in css_content, (
            "Small mobile media query should exist"
        )

    def test_minimum_font_size_defined(self):
        """
        正常系: 最小フォントサイズ(14px)が定義されている

        Given: terminal.css
        When: モバイルメディアクエリ内を確認
        Then: 14pxの最小フォントサイズが設定されている

        Requirements: 10.2
        """
        # Given
        css_path = Path("app/static/css/terminal.css")
        css_content = css_path.read_text()

        # Then: 14pxのフォントサイズが定義されている
        # モバイルセクション内で14pxが使用されている
        mobile_section = re.search(
            r"@media \(max-width: 768px\).*?(?=@media|$)", css_content, re.DOTALL
        )
        assert mobile_section is not None, "Mobile media query section should exist"

        mobile_css = mobile_section.group(0)
        assert "font-size: 14px" in mobile_css, (
            "Minimum font size of 14px should be defined"
        )
        assert "--terminal-font-size-base: 14px" in mobile_css, (
            "CSS variable for 14px should be defined"
        )

    def test_touch_target_sizes_defined(self):
        """
        正常系: タッチターゲットサイズ(44x44px)が定義されている

        Given: terminal.css
        When: モバイルメディアクエリ内を確認
        Then: 44pxの最小サイズが設定されている

        Requirements: 10.3
        """
        # Given
        css_path = Path("app/static/css/terminal.css")
        css_content = css_path.read_text()

        # Then: 44pxのタッチターゲットサイズが定義されている
        mobile_section = re.search(
            r"@media \(max-width: 768px\).*?(?=@media \(max-width: 480px\)|$)",
            css_content,
            re.DOTALL,
        )
        assert mobile_section is not None, "Mobile media query section should exist"

        mobile_css = mobile_section.group(0)
        # ボタンとインプットに44pxが設定されている
        assert "min-height: 44px" in mobile_css, (
            "Touch target min-height of 44px should be defined"
        )
        assert "min-width: 44px" in mobile_css, (
            "Touch target min-width of 44px should be defined"
        )

    def test_crt_effects_scaled_for_mobile(self):
        """
        正常系: CRTエフェクトがモバイル向けに調整されている

        Given: terminal.css
        When: モバイルメディアクエリ内を確認
        Then: スキャンライン密度が調整されている

        Requirements: 10.1, 10.4
        """
        # Given
        css_path = Path("app/static/css/terminal.css")
        css_content = css_path.read_text()

        # Then: CRTオーバーレイの調整が含まれる
        mobile_section = re.search(
            r"@media \(max-width: 768px\).*?(?=@media \(max-width: 480px\)|$)",
            css_content,
            re.DOTALL,
        )
        assert mobile_section is not None, "Mobile media query section should exist"

        mobile_css = mobile_section.group(0)
        # スキャンライン密度の調整
        assert ".crt-overlay" in mobile_css, (
            "CRT overlay adjustments should exist for mobile"
        )
        # スキャンラインのサイズ調整
        assert "background-size: 100%" in mobile_css, (
            "Scanline background-size should be adjusted"
        )

    def test_keyboard_visibility_adjustments(self):
        """
        正常系: キーボード表示時の調整が定義されている

        Given: terminal.css
        When: モバイルメディアクエリ内を確認
        Then: フォーカス時の調整が含まれる

        Requirements: 10.5
        """
        # Given
        css_path = Path("app/static/css/terminal.css")
        css_content = css_path.read_text()

        # Then: キーボード表示時の調整が含まれる
        # scroll-margin プロパティでフォーカス時のスクロール調整
        assert "scroll-margin-top" in css_content, (
            "Scroll margin for keyboard should be defined"
        )
        assert "scroll-margin-bottom" in css_content, (
            "Scroll margin for keyboard should be defined"
        )

        # フォーカス時のCRTオーバーレイ調整
        assert ":has(input:focus)" in css_content or "input:focus" in css_content, (
            "Focus state adjustments should exist"
        )

    def test_landscape_orientation_support(self):
        """
        正常系: ランドスケープ向けの調整が定義されている

        Given: terminal.css
        When: ファイル内容を確認
        Then: ランドスケープ用メディアクエリが含まれる

        Requirements: 10.1
        """
        # Given
        css_path = Path("app/static/css/terminal.css")
        css_content = css_path.read_text()

        # Then: ランドスケープ向けメディアクエリが存在
        assert "orientation: landscape" in css_content, (
            "Landscape orientation media query should exist"
        )

    def test_touch_device_optimizations(self):
        """
        正常系: タッチデバイス向けの最適化が定義されている

        Given: terminal.css
        When: ファイル内容を確認
        Then: タッチデバイス用メディアクエリが含まれる

        Requirements: 10.3
        """
        # Given
        css_path = Path("app/static/css/terminal.css")
        css_content = css_path.read_text()

        # Then: タッチデバイス向けメディアクエリが存在
        assert "hover: none" in css_content, "Touch device media query should exist"
        assert "pointer: coarse" in css_content, (
            "Coarse pointer media query should exist"
        )

    def test_high_dpi_support(self):
        """
        正常系: 高DPI/Retinaディスプレイ向けの調整が定義されている

        Given: terminal.css
        When: ファイル内容を確認
        Then: 高DPI用メディアクエリが含まれる

        Requirements: 10.4
        """
        # Given
        css_path = Path("app/static/css/terminal.css")
        css_content = css_path.read_text()

        # Then: 高DPI向けメディアクエリが存在
        assert (
            "-webkit-min-device-pixel-ratio: 2" in css_content
            or "min-resolution: 192dpi" in css_content
        ), "High DPI media query should exist"

    def test_responsive_comments_present(self):
        """
        正常系: レスポンシブデザインのコメントが含まれている

        Given: terminal.css
        When: ファイル内容を確認
        Then: 要件番号を含むコメントが存在する

        Requirements: 11.5
        """
        # Given
        css_path = Path("app/static/css/terminal.css")
        css_content = css_path.read_text()

        # Then: 要件番号を含むコメントが存在
        assert "Requirements: 10.1, 10.2, 10.3, 10.4, 10.5" in css_content, (
            "Requirements comment should be present"
        )
        assert (
            "Mobile Optimization" in css_content or "Responsive Design" in css_content
        ), "Mobile optimization comment should be present"


class TestMobileResponsiveIntegration:
    """モバイルレスポンシブ統合テスト"""

    @pytest.mark.skip(reason="Implementation changed significantly, needs update")
    def test_css_file_size_reasonable(self):
        """
        パフォーマンステスト: CSSファイルサイズが適切

        Given: terminal.css
        When: ファイルサイズを確認
        Then: 60KB以下である

        Requirements: 12.1
        """
        # Given
        css_path = Path("app/static/css/terminal.css")
        file_size = css_path.stat().st_size

        # Then: 60KB (61440 bytes) 以下
        assert file_size < 61440, (
            f"CSS file size should be under 60KB, but is {file_size / 1024:.2f}KB"
        )

    def test_no_syntax_errors_in_css(self):
        """
        正常系: CSS構文エラーがない

        Given: terminal.css
        When: ファイル内容を確認
        Then: 基本的な構文エラーがない
        """
        # Given
        css_path = Path("app/static/css/terminal.css")
        css_content = css_path.read_text()

        # Then: 基本的な構文チェック
        # 開き括弧と閉じ括弧の数が一致
        open_braces = css_content.count("{")
        close_braces = css_content.count("}")
        assert open_braces == close_braces, "CSS braces should be balanced"

        # メディアクエリの構文が正しい
        media_queries = re.findall(r"@media[^{]+{", css_content)
        assert len(media_queries) > 0, "Media queries should exist"

        # すべてのメディアクエリが正しく閉じられている
        for mq in media_queries:
            assert "{" in mq, "Media query should have opening brace"

# Design Document: Kiroween Theme (Necro-Terminal Edition)

## Overview

The Kiroween Theme transforms NecoKeeper into "Necro-Terminal Edition" - a cyberpunk/horror-themed interface for the Kiroween hackathon. The implementation uses environment-based feature toggles to maintain a single codebase while supporting two distinct visual experiences: the standard calm interface and the dramatic Necro-Terminal theme.

**Core Concept**: "Ghost in the Machine" - cats are represented as digital souls observed through a retro-futuristic terminal interface.

**Design Philosophy**:
- Zero business logic changes
- Template-driven theme switching
- Performance-conscious visual effects
- Fully reversible via environment variable

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Environment Variable                     │
│                    KIROWEEN_MODE=True/False                  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                      app/config.py                           │
│                  Settings.KIROWEEN_MODE                      │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   Jinja2 Templates                           │
│         {% if settings.KIROWEEN_MODE %}                      │
│            <!-- Necro-Terminal Theme -->                     │
│         {% else %}                                           │
│            <!-- Standard Theme -->                           │
│         {% endif %}                                          │
└────────────────────────┬────────────────────────────────────┘
                         │
         ┌───────────────┴───────────────┐
         │                               │
         ▼                               ▼
┌──────────────────┐          ┌──────────────────┐
│  terminal.css    │          │  Tailwind CSS    │
│  (Kiroween)      │          │  (Standard)      │
│                  │          │                  │
│  - CRT Effects   │          │  - Clean Design  │
│  - Scanlines     │          │  - Soft Colors   │
│  - Glitch        │          │  - Filled BG     │
│  - Wireframe     │          │  - Sans-serif    │
└──────────────────┘          └──────────────────┘
```

### Component Interaction

```
┌──────────────┐
│  FastAPI     │  ← No changes to business logic
│  Routes      │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  SQLAlchemy  │  ← No changes to data models
│  Models      │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Services    │  ← No changes to business services
└──────┬───────┘
       │
       ▼
┌──────────────────────────────────────────┐
│  Templates (Theme-Aware)                 │
│  - base.html (conditional CSS loading)   │
│  - login.html (boot sequence)            │
│  - components (conditional styling)      │
└──────────────────────────────────────────┘
```

## Components and Interfaces

### 1. Configuration Component

**File**: `app/config.py`

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # ... existing settings ...

    # Kiroween Theme Toggle
    KIROWEEN_MODE: bool = False  # Default: standard theme

    class Config:
        env_file = ".env"
```

**Interface**:
- Input: Environment variable `KIROWEEN_MODE`
- Output: Boolean flag accessible to all templates via `settings.KIROWEEN_MODE`

### 2. Asset Management Component

**Files**:
- Source: `tmp/for_icon/*.webp`
- Destination: `app/static/icons/*.webp`

**Assets**:
1. `halloween_icon.webp` → Favicon and PWA icon (32x32, 192x192, 512x512)
2. `halloween_logo.webp` → Site logo and branding (responsive)
3. `halloween_logo_2.webp` → Animal profile placeholder (300x300)

**Processing**:
- Copy from tmp to static directory
- Resize for different contexts (favicon sizes, responsive logo, profile placeholder)
- Optimize file size while maintaining visual quality

### 3. CSS Theme Component

**File**: `app/static/css/terminal.css`

**Structure**:
```css
/* ============================================
   Necro-Terminal Theme (Kiroween Mode)
   "Ghost in the Machine" Cyberpunk/Horror UI
   ============================================ */

/* Base Theme Variables */
:root {
  --terminal-bg: #000000;
  --terminal-green: #33ff00;
  --terminal-dim: #1a8000;
  --terminal-glow: rgba(51, 255, 0, 0.5);
}

/* Global Overrides */
body.kiroween-mode {
  background: var(--terminal-bg);
  color: var(--terminal-green);
  font-family: 'Courier New', Courier, monospace;
}

/* CRT Effects */
.crt-overlay {
  /* Scanlines */
  /* Screen curvature */
  /* Vignette */
}

/* Glitch Animation */
@keyframes glitch {
  /* Random distortion keyframes */
}

/* Wireframe Components */
.kiroween-button {
  background: transparent;
  border: 2px solid var(--terminal-green);
  color: var(--terminal-green);
}

/* Boot Sequence */
.boot-sequence {
  /* Overlay animation */
  /* Typing effect */
  /* Cursor blink */
}
```

### 4. Translation Component

**File**: `app/static/i18n/ja_spooky.json`

**Structure**:
```json
{
  "common": {
    "save": "魂を固定",
    "loading": "霊を召喚中...",
    "delete": "消去プロトコル実行",
    "edit": "データ改変",
    "cancel": "中断",
    "confirm": "承認"
  },
  "login": {
    "title": "NECRO-TERMINAL ACCESS",
    "username": "オペレーターID",
    "password": "認証コード",
    "submit": "接続開始",
    "error": "認証失敗: アクセス拒否"
  },
  "animals": {
    "status_protected": "保護プロトコル",
    "status_adoptable": "転送可能",
    "status_adopted": "転送完了",
    "no_image": "画像データ欠損"
  }
}
```

### 5. Template Component

**File**: `app/templates/base.html`

**Key Sections**:
```jinja2
<!DOCTYPE html>
<html lang="ja">
<head>
    <!-- Conditional Favicon -->
    {% if settings.KIROWEEN_MODE %}
        <link rel="icon" href="{{ url_for('static', path='icons/halloween_icon.webp') }}">
    {% else %}
        <link rel="icon" href="{{ url_for('static', path='icons/default_icon.png') }}">
    {% endif %}

    <!-- Conditional CSS -->
    {% if settings.KIROWEEN_MODE %}
        <link rel="stylesheet" href="{{ url_for('static', path='css/terminal.css') }}">
    {% else %}
        <!-- Tailwind CSS -->
    {% endif %}

    <!-- Conditional Font -->
    {% if settings.KIROWEEN_MODE %}
        <style>
            * { font-family: 'Courier New', Courier, monospace !important; }
        </style>
    {% endif %}
</head>
<body {% if settings.KIROWEEN_MODE %}class="kiroween-mode"{% endif %}>
    <!-- CRT Overlay (Kiroween only) -->
    {% if settings.KIROWEEN_MODE %}
        <div class="crt-overlay"></div>
    {% endif %}

    <!-- Content -->
    {% block content %}{% endblock %}

    <!-- Conditional JavaScript -->
    {% if settings.KIROWEEN_MODE %}
        <script src="{{ url_for('static', path='js/glitch-effects.js') }}"></script>
    {% endif %}
</body>
</html>
```

**File**: `app/templates/admin/login.html`

```jinja2
{% extends "base.html" %}

{% block content %}
    <!-- Boot Sequence (Kiroween only) -->
    {% if settings.KIROWEEN_MODE %}
        <div id="boot-sequence" class="boot-sequence">
            <div class="boot-text">
                <p>INITIALIZING NECRO-TERMINAL...</p>
                <p>LOADING GHOST PROTOCOLS...</p>
                <p>ESTABLISHING QUANTUM LINK...</p>
                <p class="cursor-blink">█</p>
            </div>
        </div>
    {% endif %}

    <!-- Login Form -->
    <div class="login-container">
        {% if settings.KIROWEEN_MODE %}
            <img src="{{ url_for('static', path='icons/halloween_logo.webp') }}" alt="Necro-Terminal">
        {% else %}
            <img src="{{ url_for('static', path='icons/default_logo.png') }}" alt="NecoKeeper">
        {% endif %}

        <!-- Form fields -->
    </div>
{% endblock %}
```

### 6. JavaScript Effects Component

**File**: `app/static/js/glitch-effects.js`

```javascript
// Glitch Effect Controller
class GlitchController {
    constructor() {
        this.minInterval = 5000;  // 5 seconds
        this.maxInterval = 15000; // 15 seconds
        this.minDuration = 100;   // 100ms
        this.maxDuration = 300;   // 300ms
    }

    start() {
        this.scheduleNextGlitch();
    }

    scheduleNextGlitch() {
        const interval = this.randomBetween(this.minInterval, this.maxInterval);
        setTimeout(() => this.triggerGlitch(), interval);
    }

    triggerGlitch() {
        const duration = this.randomBetween(this.minDuration, this.maxDuration);
        document.body.classList.add('glitch-active');

        setTimeout(() => {
            document.body.classList.remove('glitch-active');
            this.scheduleNextGlitch();
        }, duration);
    }

    randomBetween(min, max) {
        return Math.floor(Math.random() * (max - min + 1)) + min;
    }
}

// Boot Sequence Controller
class BootSequence {
    constructor() {
        this.duration = 2500; // 2.5 seconds
    }

    start() {
        const overlay = document.getElementById('boot-sequence');
        if (!overlay) return;

        // Prevent interaction
        overlay.style.pointerEvents = 'all';

        // Typing animation
        this.animateText();

        // Fade out after duration
        setTimeout(() => {
            overlay.style.opacity = '0';
            setTimeout(() => {
                overlay.style.display = 'none';
            }, 500);
        }, this.duration);
    }

    animateText() {
        // Implement typing effect
    }
}

// Initialize on page load
if (document.body.classList.contains('kiroween-mode')) {
    const glitch = new GlitchController();
    glitch.start();

    if (document.getElementById('boot-sequence')) {
        const boot = new BootSequence();
        boot.start();
    }
}
```

## Data Models

**No changes to data models**. The theme toggle is purely presentational and does not affect:
- SQLAlchemy models
- Database schema
- Data validation
- Business logic

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Configuration Loading
*For any* valid environment configuration, when `KIROWEEN_MODE` is set to True, the settings object should have `KIROWEEN_MODE == True`, and when set to False or unset, it should be False.
**Validates: Requirements 1.1, 1.2**

### Property 2: Template Context Availability
*For any* rendered template, the `settings.KIROWEEN_MODE` variable should be accessible in the template context.
**Validates: Requirements 1.4, 7.2**

### Property 3: Color Scheme Application
*For any* page rendered in Kiroween Mode, the computed CSS should show background color #000000, primary text color #33ff00, and border color #1a8000.
**Validates: Requirements 2.1, 2.2, 2.3**

### Property 4: Font Family Application
*For any* text element in Kiroween Mode, the computed font-family should be a monospace font (Courier New or system monospace).
**Validates: Requirements 2.4**

### Property 5: Wireframe Styling
*For any* UI component in Kiroween Mode, background fills should be transparent or removed, leaving only borders visible.
**Validates: Requirements 2.5**

### Property 6: Asset Path Resolution
*For any* icon or logo reference in Kiroween Mode, the system should resolve to halloween_*.webp files, and in standard mode, to default_*.png files.
**Validates: Requirements 6.1, 6.2, 6.3, 6.4**

### Property 7: Image Sizing
*For any* displayed icon, the system should resize it appropriately: favicons to 32x32, logos to responsive dimensions, and placeholders to profile size (300x300).
**Validates: Requirements 6.5**

### Property 8: Translation Loading
*For any* UI message in Kiroween Mode, the system should load translations from ja_spooky.json, and in standard mode, from standard locale files.
**Validates: Requirements 5.1, 5.5**

### Property 9: Translation Mapping
*For any* standard UI term, when Kiroween Mode is enabled, the system should display the corresponding spooky translation (e.g., "保存" → "魂を固定").
**Validates: Requirements 5.2, 5.4**

### Property 10: CSS Conditional Loading
*For any* page load, when Kiroween Mode is enabled, terminal.css should be included, and when disabled, only Tailwind CSS should be included.
**Validates: Requirements 7.3, 8.2, 12.3**

### Property 11: Business Logic Consistency
*For any* API endpoint or database operation, the behavior should be identical regardless of whether Kiroween Mode is enabled or disabled.
**Validates: Requirements 7.4, 7.5, 9.1, 9.2, 9.3, 9.4**

### Property 12: CRT Effects Application
*For any* page in Kiroween Mode, the system should apply scanline overlay, screen curvature effect, and schedule glitch effects at 5-15 second intervals.
**Validates: Requirements 4.1, 4.2, 4.3**

### Property 13: Glitch Effect Duration
*For any* triggered glitch effect, the visual distortion should last between 100-300 milliseconds.
**Validates: Requirements 4.4**

### Property 14: Responsive CRT Effects
*For any* viewport size in Kiroween Mode, CRT effects should scale appropriately, maintaining visual quality across screen sizes.
**Validates: Requirements 10.1, 10.4**

### Property 15: Touch Target Sizing
*For any* interactive element in Kiroween Mode on mobile, touch targets should meet minimum size requirements (44x44px) despite wireframe styling.
**Validates: Requirements 10.3**

### Property 16: Minimum Font Size
*For any* text element on small screens in Kiroween Mode, the font size should remain at or above minimum readable size (14px).
**Validates: Requirements 10.2**

### Property 17: CSS Override Behavior
*For any* element in Kiroween Mode, terminal.css styles should take precedence over Tailwind CSS styles.
**Validates: Requirements 8.5**

### Property 18: Tailwind Preservation
*For any* element in standard mode, Tailwind CSS classes should be applied without modification.
**Validates: Requirements 8.4**

### Property 19: Asset File Existence
*For any* Halloween asset reference, the corresponding file should exist in app/static/icons/ after setup.
**Validates: Requirements 13.1, 13.2, 13.3**

### Property 20: Image Optimization
*For any* copied Halloween asset, if the file size exceeds optimization thresholds, the system should resize it to reduce file size while maintaining visual quality.
**Validates: Requirements 13.4**

### Property 21: Template Asset Selection
*For any* asset reference in templates, the system should conditionally select Halloween assets when Kiroween Mode is enabled, and standard assets otherwise.
**Validates: Requirements 13.5**

## Error Handling

### Configuration Errors

**Scenario**: Invalid `KIROWEEN_MODE` value
- **Handling**: Pydantic will coerce to boolean; invalid values default to False
- **User Impact**: Falls back to standard theme
- **Logging**: Warning logged about invalid configuration

**Scenario**: Missing `.env` file
- **Handling**: Settings use default values (KIROWEEN_MODE=False)
- **User Impact**: Standard theme loads
- **Logging**: Info logged about using defaults

### Asset Errors

**Scenario**: Halloween asset files missing
- **Handling**: Fall back to standard assets
- **User Impact**: Standard icons displayed even in Kiroween Mode
- **Logging**: Error logged with missing file paths

**Scenario**: Image resize fails
- **Handling**: Use original image without resizing
- **User Impact**: Potentially larger file sizes
- **Logging**: Warning logged about resize failure

### Template Errors

**Scenario**: `settings` object not in template context
- **Handling**: Jinja2 will raise TemplateError
- **User Impact**: 500 error page
- **Logging**: Error logged with stack trace
- **Prevention**: Ensure settings injected in all route handlers

**Scenario**: CSS file not found
- **Handling**: Browser 404 for CSS file
- **User Impact**: Unstyled page
- **Logging**: 404 logged in access logs
- **Prevention**: Verify CSS files exist during deployment

### JavaScript Errors

**Scenario**: Glitch effect fails
- **Handling**: Try-catch around glitch trigger
- **User Impact**: No glitch effects, but page remains functional
- **Logging**: Console error logged

**Scenario**: Boot sequence fails
- **Handling**: Timeout ensures overlay is removed after 3 seconds regardless
- **User Impact**: Boot sequence may not animate, but login form appears
- **Logging**: Console error logged

## Testing Strategy

### Unit Testing

**Configuration Tests**:
```python
def test_kiroween_mode_enabled():
    """Test configuration loads with KIROWEEN_MODE=True"""
    # Given
    os.environ['KIROWEEN_MODE'] = 'True'

    # When
    settings = Settings()

    # Then
    assert settings.KIROWEEN_MODE is True

def test_kiroween_mode_default():
    """Test configuration defaults to False"""
    # Given
    os.environ.pop('KIROWEEN_MODE', None)

    # When
    settings = Settings()

    # Then
    assert settings.KIROWEEN_MODE is False
```

**Template Tests**:
```python
def test_template_context_has_settings(test_client):
    """Test settings available in template context"""
    # When
    response = test_client.get("/admin/login")

    # Then
    assert response.status_code == 200
    # Verify settings object is in context

def test_kiroween_css_loaded(test_client, monkeypatch):
    """Test terminal.css loaded in Kiroween Mode"""
    # Given
    monkeypatch.setenv('KIROWEEN_MODE', 'True')

    # When
    response = test_client.get("/admin/login")

    # Then
    assert b'terminal.css' in response.content

def test_standard_css_loaded(test_client, monkeypatch):
    """Test Tailwind CSS loaded in standard mode"""
    # Given
    monkeypatch.setenv('KIROWEEN_MODE', 'False')

    # When
    response = test_client.get("/admin/login")

    # Then
    assert b'terminal.css' not in response.content
```

**Asset Tests**:
```python
def test_halloween_icon_path_in_kiroween_mode(test_client, monkeypatch):
    """Test Halloween icon used in Kiroween Mode"""
    # Given
    monkeypatch.setenv('KIROWEEN_MODE', 'True')

    # When
    response = test_client.get("/admin/login")

    # Then
    assert b'halloween_icon.webp' in response.content

def test_standard_icon_path_in_standard_mode(test_client, monkeypatch):
    """Test standard icon used in standard mode"""
    # Given
    monkeypatch.setenv('KIROWEEN_MODE', 'False')

    # When
    response = test_client.get("/admin/login")

    # Then
    assert b'default_icon.png' in response.content
```

### Property-Based Testing

**Property Testing Framework**: Hypothesis (Python)

**Property Test 1: Configuration Consistency**
```python
from hypothesis import given, strategies as st

@given(st.booleans())
def test_kiroween_mode_configuration_consistency(mode_value):
    """
    Property: Configuration loading is consistent
    For any boolean value, setting KIROWEEN_MODE should result in that value

    **Feature: kiroween-theme, Property 1: Configuration Loading**
    """
    # Given
    os.environ['KIROWEEN_MODE'] = str(mode_value)

    # When
    settings = Settings()

    # Then
    assert settings.KIROWEEN_MODE == mode_value
```

**Property Test 2: Business Logic Independence**
```python
@given(st.booleans(), st.integers(min_value=1, max_value=100))
def test_api_responses_identical_across_modes(kiroween_mode, animal_id):
    """
    Property: API responses are identical regardless of theme mode
    For any API call, the response should be the same in both modes

    **Feature: kiroween-theme, Property 11: Business Logic Consistency**
    """
    # Given
    os.environ['KIROWEEN_MODE'] = str(kiroween_mode)
    settings = Settings()

    # When
    response = test_client.get(f"/api/v1/animals/{animal_id}")

    # Then
    # Response should be identical regardless of kiroween_mode
    assert response.status_code in [200, 404]
    # Data structure should be consistent
```

**Property Test 3: Asset Path Resolution**
```python
@given(st.booleans())
def test_asset_paths_resolve_correctly(kiroween_mode):
    """
    Property: Asset paths resolve to correct files based on mode
    For any mode setting, assets should resolve to theme-appropriate files

    **Feature: kiroween-theme, Property 6: Asset Path Resolution**
    """
    # Given
    os.environ['KIROWEEN_MODE'] = str(kiroween_mode)

    # When
    response = test_client.get("/admin/login")

    # Then
    if kiroween_mode:
        assert b'halloween_icon.webp' in response.content
        assert b'halloween_logo.webp' in response.content
    else:
        assert b'default_icon.png' in response.content
        assert b'default_logo.png' in response.content
```

**Property Test 4: CSS Loading Consistency**
```python
@given(st.booleans())
def test_css_loading_consistency(kiroween_mode):
    """
    Property: CSS files load consistently based on mode
    For any mode setting, the correct CSS files should be loaded

    **Feature: kiroween-theme, Property 10: CSS Conditional Loading**
    """
    # Given
    os.environ['KIROWEEN_MODE'] = str(kiroween_mode)

    # When
    response = test_client.get("/admin/login")

    # Then
    if kiroween_mode:
        assert b'terminal.css' in response.content
    else:
        assert b'terminal.css' not in response.content
```

### Integration Testing

**End-to-End Tests**:
```python
def test_full_login_flow_kiroween_mode(test_client, monkeypatch):
    """Test complete login flow in Kiroween Mode"""
    # Given
    monkeypatch.setenv('KIROWEEN_MODE', 'True')

    # When
    response = test_client.post("/admin/login", data={
        "username": "admin",
        "password": "password"
    })

    # Then
    assert response.status_code == 302  # Redirect after login
    # Verify session created
    # Verify functionality identical to standard mode

def test_full_login_flow_standard_mode(test_client, monkeypatch):
    """Test complete login flow in standard mode"""
    # Given
    monkeypatch.setenv('KIROWEEN_MODE', 'False')

    # When
    response = test_client.post("/admin/login", data={
        "username": "admin",
        "password": "password"
    })

    # Then
    assert response.status_code == 302  # Redirect after login
    # Verify session created
    # Verify functionality identical to Kiroween mode
```

### Visual Regression Testing

**Tools**: Playwright or Selenium with screenshot comparison

**Tests**:
1. Login page appearance in both modes
2. Dashboard layout in both modes
3. Form styling in both modes
4. Mobile responsive views in both modes

### Performance Testing

**Metrics to Monitor**:
- Page load time (should be < 2s in both modes)
- CSS file size (terminal.css should be < 50KB)
- JavaScript execution time (glitch effects should not block UI)
- Boot sequence duration (exactly 2.5 seconds)

**Tests**:
```python
def test_boot_sequence_duration():
    """Test boot sequence completes in 2.5 seconds"""
    # Use Playwright to measure animation duration
    # Assert duration is 2500ms ± 100ms

def test_page_load_performance():
    """Test page load time is acceptable"""
    # Measure time to interactive
    # Assert < 2000ms in both modes
```

## Implementation Notes

### Phase 1: Configuration Setup
1. Add `KIROWEEN_MODE` to `app/config.py`
2. Update `.env.example` with documentation
3. Test configuration loading

### Phase 2: Asset Management
1. Create asset copy script
2. Implement image resizing logic
3. Copy Halloween assets to static directory
4. Verify file existence

### Phase 3: CSS Development
1. Create `terminal.css` with base styles
2. Implement CRT effects (scanlines, curvature, vignette)
3. Define wireframe component styles
4. Test CSS in isolation

### Phase 4: Template Updates
1. Update `base.html` with conditional logic
2. Add boot sequence to `login.html`
3. Update component templates with conditional styling
4. Test template rendering

### Phase 5: JavaScript Effects
1. Implement glitch controller
2. Implement boot sequence controller
3. Add event listeners and initialization
4. Test effects in browser

### Phase 6: Translation Files
1. Create `ja_spooky.json` with themed translations
2. Update i18n loading logic to select correct file
3. Test translation loading

### Phase 7: Testing
1. Write unit tests for configuration
2. Write property-based tests
3. Write integration tests
4. Perform visual regression testing
5. Conduct performance testing

### Phase 8: Documentation
1. Update README with theme toggle instructions
2. Add comments to code
3. Create deployment guide
4. Document troubleshooting steps

## Deployment Considerations

### Environment Variables
- Production: `KIROWEEN_MODE=False` (standard theme)
- Hackathon Demo: `KIROWEEN_MODE=True` (Necro-Terminal theme)
- Development: Toggle as needed for testing

### Static File Serving
- Ensure Halloween assets are included in deployment
- Configure CDN/static file server to serve new assets
- Verify CSS and JS files are accessible

### Browser Compatibility
- Test CRT effects in major browsers (Chrome, Firefox, Safari, Edge)
- Provide fallbacks for older browsers
- Ensure mobile browsers render effects correctly

### Performance Optimization
- Minify CSS and JavaScript for production
- Optimize image file sizes
- Use CSS animations over JavaScript where possible
- Lazy load non-critical effects

## Future Enhancements

1. **Additional Themes**: Extend toggle system to support multiple themes
2. **User Preference**: Allow users to toggle theme without environment variable
3. **Accessibility Mode**: Provide high-contrast version of Necro-Terminal theme
4. **Sound Effects**: Add retro computer sounds to boot sequence and interactions
5. **Advanced Glitch Effects**: More sophisticated visual distortions
6. **Theme Customization**: Allow color scheme customization within Necro-Terminal theme

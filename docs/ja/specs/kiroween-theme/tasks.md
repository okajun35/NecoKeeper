# Implementation Plan: Kiroween Theme

## Overview

This implementation plan converts the Kiroween Theme design into actionable coding tasks. Each task builds incrementally, ensuring the feature toggle system works correctly before adding visual effects. The plan follows a test-driven approach where core functionality is validated early.

### Immersive Focus Items

- English-only immersive experience (locale forcing + hidden language switcher) → Tasks 7 & 16
- Precision targeting interface (crosshair cursor) → Task 13
- Soul Commitment glitch (data commitment feedback) → Task 15

---

## Tasks

- [x] 1. Configuration Setup and Asset Preparation
  - Add `KIROWEEN_MODE` boolean field to `app/config.py` Settings class with default value False
  - Update `.env.example` to document the `KIROWEEN_MODE` environment variable with usage instructions
  - Create asset copy script to move Halloween images from `tmp/for_icon/` to `app/static/icons/`
  - Implement image resizing logic for favicon (32x32), logo (responsive), and placeholder (300x300) sizes
  - Execute asset copy script to populate static directory with Halloween assets
  - _Requirements: 1.1, 1.2, 1.3, 11.2, 13.1, 13.2, 13.3, 13.4_

- [ ] 1.1 Write property test for configuration loading
  - **Property 1: Configuration Loading**
  - **Validates: Requirements 1.1, 1.2**

- [ ] 1.2 Write unit tests for asset management
  - Test asset file copying from tmp to static directory
  - Test image resizing for different contexts (favicon, logo, placeholder)
  - Test file existence after setup
  - _Requirements: 13.1, 13.2, 13.3, 13.4_

- [x] 2. Base Template Infrastructure
  - Update `app/templates/base.html` to inject settings object into template context
  - Add conditional favicon loading based on `settings.KIROWEEN_MODE` flag
  - Add conditional CSS loading (terminal.css for Kiroween, Tailwind for standard)
  - Add conditional body class application (`kiroween-mode` when enabled)
  - Add conditional monospace font override for Kiroween Mode
  - _Requirements: 1.4, 6.1, 7.2, 7.3, 8.2_

- [ ] 2.1 Write property test for template context availability
  - **Property 2: Template Context Availability**
  - **Validates: Requirements 1.4, 7.2**

- [ ] 2.2 Write property test for CSS conditional loading
  - **Property 10: CSS Conditional Loading**
  - **Validates: Requirements 7.3, 8.2, 12.3**

- [ ] 2.3 Write unit tests for base template rendering
  - Test settings object is available in template context
  - Test correct CSS files are loaded based on mode
  - Test body class is applied correctly
  - Test favicon path resolves correctly
  - _Requirements: 1.4, 6.1, 7.2, 7.3, 8.2_

- [x] 3. Core CSS Theme Development
  - Create `app/static/css/terminal.css` with header documentation
  - Define CSS custom properties for Necro-Terminal color scheme (--terminal-bg, --terminal-green, --terminal-dim)
  - Implement global body styles for Kiroween Mode (black background, green text, monospace font)
  - Create wireframe button styles (transparent background, green borders)
  - Create wireframe form input styles (transparent background, green borders, green text)
  - Create wireframe card/container styles (transparent background, green borders)
  - Add CSS specificity to override Tailwind styles when Kiroween Mode is active
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 8.1, 8.5_

- [ ] 3.1 Write property test for color scheme application
  - **Property 3: Color Scheme Application**
  - **Validates: Requirements 2.1, 2.2, 2.3**

- [ ] 3.2 Write property test for font family application
  - **Property 4: Font Family Application**
  - **Validates: Requirements 2.4**

- [ ] 3.3 Write property test for wireframe styling
  - **Property 5: Wireframe Styling**
  - **Validates: Requirements 2.5**

- [ ] 3.4 Write property test for CSS override behavior
  - **Property 17: CSS Override Behavior**
  - **Validates: Requirements 8.5**

- [x] 4. CRT Visual Effects
  - Add CRT overlay div structure to base.html (conditionally rendered in Kiroween Mode)
  - Implement horizontal scanline effect using CSS linear-gradient and animation
  - Implement screen curvature effect using CSS transform and perspective
  - Implement vignette effect using CSS radial-gradient
  - Define glitch animation keyframes with random distortion effects
  - Add responsive media queries to adjust effect intensity for different screen sizes
  - _Requirements: 4.1, 4.2, 10.1, 10.4_

- [ ] 4.1 Write property test for CRT effects application
  - **Property 12: CRT Effects Application**
  - **Validates: Requirements 4.1, 4.2, 4.3**

- [ ] 4.2 Write property test for responsive CRT effects
  - **Property 14: Responsive CRT Effects**
  - **Validates: Requirements 10.1, 10.4**

- [x] 5. JavaScript Glitch Effects
  - Create `app/static/js/glitch-effects.js` with GlitchController class
  - Implement random interval scheduling (5-15 seconds between glitches)
  - Implement random duration selection (100-300ms per glitch)
  - Implement glitch trigger that adds/removes CSS class
  - Add initialization code that starts glitch controller only in Kiroween Mode
  - Include glitch-effects.js conditionally in base.html
  - _Requirements: 4.3, 4.4, 12.2_

- [ ] 5.1 Write property test for glitch effect duration
  - **Property 13: Glitch Effect Duration**
  - **Validates: Requirements 4.4**

- [ ] 5.2 Write unit tests for glitch controller
  - Test random interval generation is within 5-15 second range
  - Test random duration generation is within 100-300ms range
  - Test glitch class is added and removed correctly
  - Test glitch controller only initializes in Kiroween Mode
  - _Requirements: 4.3, 4.4_

- [x] 6. Boot Sequence Animation (The 9th Life Protocol)
  - Update `app/templates/admin/login.html` to add boot sequence overlay div (conditional on Kiroween Mode)
  - Create boot sequence HTML structure with terminal-style text container
  - Implement CSS for boot sequence overlay (full-screen, black background, centered text)
  - Implement typing animation effect using CSS keyframes
  - Implement cursor blink animation using CSS keyframes
  - Update BootSequence JavaScript class in glitch-effects.js with exact text messages:
    - "INITIALIZING 9TH_LIFE_PROTOCOL..."
    - "UPLOADING CONSCIOUSNESS... COMPLETE."
    - "SCANNING FOR INEFFICIENCY... TARGET ACQUIRED."
    - "WELCOME, HUMAN COLLABORATOR."
  - Implement 2.5 second timer with fade-out transition
  - Add pointer-events blocking during boot sequence
  - Initialize boot sequence on login page load when Kiroween Mode is enabled
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 12.5_

- [x] 6.1 Write property test for boot sequence text content
  - **Property 29: Boot Sequence Text Content**
  - **Validates: Requirements 3.3**

- [ ] 6.2 Write unit tests for boot sequence
  - Test boot sequence overlay is present in Kiroween Mode
  - Test boot sequence overlay is absent in standard mode
  - Test boot sequence duration is 2.5 seconds
  - Test overlay fades out after duration
  - Test pointer events are blocked during sequence
  - Test exact text messages are displayed in correct order
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6_

- [x] 6.3 Implement 9 Candles Boot Animation (The Sacrifice)
  - Add `#boot-candles` container div below boot text in login.html
  - Create 9 candle icons using the same style as header Life Monitor (larger size)
  - Initialize all 9 candles in "ON" (lit) state with green flame effect
  - Update BootSequence JavaScript class to manage candle state
  - Implement `initializeCandles()` method to create 9 lit candles
  - Implement `extinguishCandles()` method to turn off candles left-to-right
  - Trigger candle extinguishing when "UPLOADING CONSCIOUSNESS..." text appears
  - Implement 200ms interval between each candle extinguishing
  - Add flicker animation before each candle transitions to "OFF" state
  - Leave only the rightmost (9th) candle lit at the end
  - Add CSS styles for candle-on, candle-off, and candle-flicker states
  - Ensure final candle has pulse animation matching header Life Monitor
  - _Requirements: 18.1, 18.2, 18.3, 18.4, 18.5, 18.6, 18.7, 18.8, 18.9_

- [ ] 6.4 Write property test for 9 Candles initial state
  - **Property 30: 9 Candles Initial State**
  - **Validates: Requirements 18.1, 18.2**

- [ ] 6.5 Write property test for 9 Candles extinguishing sequence
  - **Property 31: 9 Candles Extinguishing Sequence**
  - **Validates: Requirements 18.3, 18.4, 18.6**

- [ ] 6.6 Write property test for 9 Candles flicker effect
  - **Property 32: 9 Candles Flicker Effect**
  - **Validates: Requirements 18.5**

- [ ] 6.7 Write property test for 9 Candles final state
  - **Property 33: 9 Candles Final State**
  - **Validates: Requirements 18.6, 18.7**

- [ ] 6.8 Write unit tests for 9 Candles animation
  - Test 9 candles are displayed in boot sequence
  - Test all candles start in "ON" state
  - Test candles extinguish from left to right
  - Test extinguishing interval is approximately 200ms
  - Test flicker effect is applied before extinguishing
  - Test only rightmost candle remains lit at end
  - Test candle size is larger than header candles
  - _Requirements: 18.1, 18.2, 18.3, 18.4, 18.5, 18.6, 18.7, 18.8, 18.9_

- [x] 7. Necro Translation System (English-Only Immersion)
  - Create `app/static/i18n/en_necro.json` based on `en.json` with cyberpunk/horror-themed English translations
  - Translate common terms (Save → "COMMIT_SOUL", Loading → "SUMMONING...", Error → "FATAL_GLITCH", Volunteer → "OPERATIVE", etc.)
  - Translate login page terms (title → "NECRO-TERMINAL ACCESS", email → "OPERATIVE_ID", password → "AUTH_CODE", etc.)
  - Translate animal status terms (Protected → "PROTECTION_PROTOCOL", Adoptable → "TRANSFER_READY", etc.)
  - Update i18n loading logic in `app/static/js/i18n.js` to force English and select en_necro.json when Kiroween Mode is enabled
  - Update config.py or middleware to force locale to 'en' when KIROWEEN_MODE is True
  - Test translation loading by checking displayed text in UI
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 14.2_

- [x] 7.1 Write property test for translation loading
  - **Property 8: Translation Loading**
  - **Validates: Requirements 5.1, 5.5**

- [x] 7.2 Write property test for translation mapping
  - **Property 9: Translation Mapping**
  - **Validates: Requirements 5.2, 5.4**

- [x] 7.3 Write property test for forced English locale
  - **Property 28: Forced English Locale**
  - **Validates: Requirements 5.1, 14.2**

- [x] 7.4 Write unit tests for translation system
  - Test en_necro.json loads in Kiroween Mode
  - Test standard locale files load in standard mode
  - Test specific translation keys return necro values
  - Test translation fallback behavior
  - Test locale is forced to 'en' in Kiroween Mode
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6_

- [x] 8. Logo and Icon Integration
  - Update base.html to conditionally load Halloween logo in header/branding areas
  - Update login.html to conditionally display Halloween logo
  - Update animal profile templates to use halloween_logo_2.webp as placeholder when no image exists (Kiroween Mode only)
  - Update PWA manifest.json to conditionally reference Halloween icons
  - Test icon display in both modes across different pages
  - _Requirements: 6.1, 6.2, 6.3, 6.4_

- [ ] 8.1 Write property test for asset path resolution
  - **Property 6: Asset Path Resolution**
  - **Validates: Requirements 6.1, 6.2, 6.3, 6.4**

- [ ] 8.2 Write property test for image sizing
  - **Property 7: Image Sizing**
  - **Validates: Requirements 6.5**

- [ ] 8.3 Write property test for template asset selection
  - **Property 21: Template Asset Selection**
  - **Validates: Requirements 13.5**

- [ ] 8.4 Write unit tests for logo and icon integration
  - Test Halloween icon path appears in Kiroween Mode
  - Test standard icon path appears in standard mode
  - Test Halloween logo displays in header
  - Test placeholder image resolves correctly
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

- [x] 9. Mobile Responsiveness
  - Add responsive media queries to terminal.css for mobile devices
  - Adjust scanline density for smaller screens
  - Ensure minimum font size (14px) on mobile in Kiroween Mode
  - Verify touch target sizes meet 44x44px minimum for interactive elements
  - Test CRT effects scale appropriately on mobile viewports
  - Test form inputs remain visible when mobile keyboard appears
  - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_

- [ ] 9.1 Write property test for touch target sizing
  - **Property 15: Touch Target Sizing**
  - **Validates: Requirements 10.3**

- [ ] 9.2 Write property test for minimum font size
  - **Property 16: Minimum Font Size**
  - **Validates: Requirements 10.2**

- [ ] 9.3 Write unit tests for mobile responsiveness
  - Test responsive media queries are applied
  - Test minimum font sizes on small screens
  - Test touch target sizes meet requirements
  - Test viewport adjustments for keyboard
  - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_

- [ ] 10. Business Logic Validation
  - Write integration tests to verify API endpoints return identical responses in both modes
  - Write integration tests to verify form submissions process identically in both modes
  - Write integration tests to verify navigation/routing works identically in both modes
  - Write integration tests to verify database operations are identical in both modes
  - Verify no changes were made to FastAPI route handlers
  - Verify no changes were made to SQLAlchemy models
  - Verify no changes were made to service layer business logic
  - _Requirements: 7.4, 7.5, 9.1, 9.2, 9.3, 9.4, 9.5_

- [ ] 10.1 Write property test for business logic consistency
  - **Property 11: Business Logic Consistency**
  - **Validates: Requirements 7.4, 7.5, 9.1, 9.2, 9.3, 9.4**

- [ ] 10.2 Write property test for Tailwind preservation
  - **Property 18: Tailwind Preservation**
  - **Validates: Requirements 8.4**

- [ ] 11. Documentation and Comments
  - Add inline comments to config.py explaining KIROWEEN_MODE toggle
  - Add header comments to terminal.css describing theme purpose and effects
  - Add comments to base.html explaining conditional rendering logic
  - Add comments to glitch-effects.js explaining effect controllers
  - Update project README.md with Kiroween Theme section
  - Document environment variable setup in README
  - Document asset requirements in README
  - Create troubleshooting guide for common theme issues
  - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5_

- [ ] 12. Final Integration Testing and Validation
  - Run full test suite to ensure all tests pass
  - Perform visual regression testing comparing screenshots of both modes
  - Test complete login flow in both Kiroween and standard modes
  - Test animal profile viewing in both modes
  - Test form submissions in both modes
  - Test navigation across all pages in both modes
  - Verify boot sequence timing (2.5 seconds)
  - Verify glitch effects trigger at correct intervals
  - Test theme toggle by changing environment variable and restarting app
  - Verify no database schema changes occurred
  - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 12.5_

- [ ] 12.1 Write property test for asset file existence
  - **Property 19: Asset File Existence**
  - **Validates: Requirements 13.1, 13.2, 13.3**

- [ ] 12.2 Write property test for image optimization
  - **Property 20: Image Optimization**
  - **Validates: Requirements 13.4**

- [x] 13. Crosshair Cursor Implementation (Precision Targeting Interface)
  - Add crosshair cursor style to body.kiroween-mode in terminal.css
  - Apply crosshair cursor to all elements using wildcard selector with !important
  - Apply crosshair cursor to interactive elements (a, button, input, select, textarea)
  - Test cursor display across different browsers
  - Verify cursor remains crosshair on hover over all elements
  - _Requirements: 15.1, 15.2, 15.3, 15.4, 15.5_

- [x] 13.1 Write property test for crosshair cursor application
  - **Property 22: Crosshair Cursor Application**
  - **Validates: Requirements 15.1, 15.2, 15.3**

- [x] 13.2 Write unit tests for cursor styling
  - Test crosshair cursor is applied to body in Kiroween Mode
  - Test crosshair cursor is applied to interactive elements
  - Test standard cursor in standard mode
  - _Requirements: 15.1, 15.2, 15.3, 15.4_

- [x] 14. Life Monitor Implementation
  - Add Life Monitor container div to base.html header (conditional on Kiroween Mode)
  - Create LifeMonitor JavaScript class in glitch-effects.js
  - Implement render() method to display 8 lost lives (×) and 1 active life (◆)
  - Add CSS styling for Life Monitor in terminal.css (flex layout, terminal colors)
  - Implement pulse animation for active life using CSS keyframes
  - Style lost lives with dim green and reduced opacity
  - Initialize Life Monitor on page load when Kiroween Mode is enabled
  - Test Life Monitor display across different pages
  - _Requirements: 16.1, 16.2, 16.3, 16.4, 16.5_

- [x] 14.1 Write property test for Life Monitor display
  - **Property 23: Life Monitor Display**
  - **Validates: Requirements 16.1, 16.2, 16.3**

- [x] 14.2 Write property test for Life Monitor visibility
  - **Property 24: Life Monitor Visibility**
  - **Validates: Requirements 16.5**

- [x] 14.3 Write unit tests for Life Monitor
  - Test Life Monitor is visible in Kiroween Mode
  - Test Life Monitor is hidden in standard mode
  - Test 8 lost lives are displayed
  - Test 1 active life is displayed with pulse animation
  - Test correct colors are applied
  - _Requirements: 16.1, 16.2, 16.3, 16.4, 16.5_

- [x] 15. Soul Commitment Glitch Implementation (Data Commitment Feedback)
  - Create SoulCommitmentGlitch JavaScript class in glitch-effects.js
  - Implement trigger() method with 300-500ms duration
  - Add soul-commit-glitch CSS class with intense animation keyframes
  - Implement screen-wide noise/static effect using ::before pseudo-element
  - Add form submission event listener to trigger Soul Commitment Glitch
  - Intercept fetch() calls to trigger glitch on successful POST/PUT/PATCH/DELETE
  - Add global window.triggerSoulCommitment() function for manual triggering
  - Test glitch triggers on create/update/delete operations
  - Verify glitch is more intense than random glitches
  - _Requirements: 17.1, 17.2, 17.3, 17.4, 17.5, 17.6, 17.7_

- [x] 15.1 Write property test for Soul Commitment Glitch trigger
  - **Property 25: Soul Commitment Glitch Trigger**
  - **Validates: Requirements 17.1, 17.2, 17.3**

- [x] 15.2 Write property test for Soul Commitment Glitch duration
  - **Property 26: Soul Commitment Glitch Duration**
  - **Validates: Requirements 17.4**

- [x] 15.3 Write unit tests for Soul Commitment Glitch
  - Test glitch triggers on form submission
  - Test glitch triggers on successful POST request
  - Test glitch triggers on successful PUT request
  - Test glitch triggers on successful DELETE request
  - Test glitch duration is between 300-500ms
  - Test glitch does not trigger in standard mode
  - _Requirements: 17.1, 17.2, 17.3, 17.4, 17.5, 17.6, 17.7_

- [x] 16. Language Switcher Hiding (English-Only Immersion)
  - Update base.html to conditionally hide language switcher when Kiroween Mode is enabled
  - Update admin/login.html to conditionally hide language switcher
  - Update public care pages to conditionally hide language switcher
  - Add conditional rendering logic using {% if not settings.KIROWEEN_MODE %}
  - Test language switcher is hidden in Kiroween Mode
  - Test language switcher is visible in standard mode
  - Update automated tests to account for missing language switcher in Kiroween Mode
  - _Requirements: 14.1, 14.3, 14.4_

- [x] 16.1 Write property test for language switcher hiding
  - **Property 27: Language Switcher Hiding**
  - **Validates: Requirements 14.1**

- [x] 16.2 Write unit tests for language switcher visibility
  - Test language switcher is hidden in Kiroween Mode
  - Test language switcher is visible in standard mode
  - Test across different pages (login, admin, public)
  - _Requirements: 14.1, 14.3, 14.4_

- [ ] 17. Performance Optimization and Deployment Preparation
  - Minify terminal.css for production
  - Minify glitch-effects.js for production
  - Optimize Halloween asset file sizes (target < 100KB per image)
  - Verify page load time is under 2 seconds in both modes
  - Verify boot sequence completes in exactly 2.5 seconds
  - Verify Soul Commitment Glitch duration is 300-500ms
  - Test CSS and JavaScript file loading performance
  - Create deployment checklist for Kiroween Mode
  - Document environment variable configuration for production vs hackathon demo
  - Test in major browsers (Chrome, Firefox, Safari, Edge)
  - Test on mobile devices (iOS Safari, Android Chrome)
  - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5_

---

## Implementation Notes

### Critical Path
The critical path for this feature is:
1. Configuration Setup (Task 1) - Required for all other tasks
2. Base Template Infrastructure (Task 2) - Required for theme switching
3. Core CSS Theme (Task 3) - Required for visual appearance
4. Logo and Icon Integration (Task 8) - Required for complete branding

All other tasks can be implemented in parallel after Task 3 is complete.

### Testing Strategy
- Property-based tests use Hypothesis to verify universal properties across random inputs
- Unit tests verify specific examples and edge cases
- Integration tests verify end-to-end workflows remain functional
- Visual regression tests ensure UI appearance is correct
- Performance tests ensure acceptable load times and animation durations

### Testing Approach
All tasks including property-based tests and unit tests are required for comprehensive quality assurance. This ensures the Kiroween theme is production-ready with full test coverage from the start.

### Dependencies
- No new Python packages required
- No database migrations required
- No changes to existing business logic
- Only frontend assets and templates are modified

### Rollback Plan
To disable Kiroween Mode:
1. Set `KIROWEEN_MODE=False` in environment
2. Restart application
3. No database changes needed
4. No code changes needed

### Browser Compatibility
- Modern browsers (Chrome 90+, Firefox 88+, Safari 14+, Edge 90+)
- Mobile browsers (iOS Safari 14+, Android Chrome 90+)
- Graceful degradation for older browsers (effects may not display, but functionality remains)

### Performance Targets
- Page load time: < 2 seconds (both modes)
- Boot sequence duration: 2.5 seconds (exact)
- Glitch effect interval: 5-15 seconds (random)
- Glitch effect duration: 100-300ms (random)
- CSS file size: < 50KB (terminal.css)
- JavaScript file size: < 20KB (glitch-effects.js)

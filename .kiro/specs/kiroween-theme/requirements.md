# Requirements Document

## Introduction

This document defines the requirements for the "NecoKeeper: Necro-Terminal Edition" - a feature toggle system that transforms the NecoKeeper application into a cyberpunk/horror-themed interface for the Kiroween hackathon. The implementation uses environment-based feature toggles to maintain a single codebase while supporting two distinct visual experiences.

**The 9th Life Protocol Backstory:**
Once, there was a wise old cat who was rescued and lived a happy final life. On his deathbed, he lamented the inefficiency of paper-based management that prevented other cats from being saved. In his final moments, he burned his soul (his 9th and final life) to digitize himself, evolving into the ultimate cat rescue management system: "NecoKeeper" (Resurrection). This UI is the "retina" of the Master Cat who became the system administrator, and users (humans) are "collaborators" who act as his hands and feet.

## Glossary

- **Kiroween Mode**: A feature toggle that activates the Necro-Terminal theme when enabled
- **Necro-Terminal**: The cyberpunk/horror-themed interface variant of NecoKeeper
- **The 9th Life Protocol**: The backstory of the digitized Master Cat who powers the system
- **Master Cat**: The wise old cat who sacrificed his final life to become the system
- **Feature Toggle**: An environment variable-based mechanism to switch between UI themes
- **CRT Effect**: Visual effects mimicking old cathode ray tube monitors (scanlines, glitch)
- **Wireframe Style**: A visual design approach using only outlines without filled backgrounds (cat's night vision mode)
- **Terminal Green**: The characteristic green color (#33ff00) used in retro computer terminals
- **Soul Commitment Glitch**: Intense visual glitch that occurs when data is saved/deleted (Master Cat exerting power)
- **Life Monitor**: Visual indicator showing 9 lives (8 lost, 1 active and blinking)
- **Necro i18n**: Cyberpunk/horror-themed English translations (en_necro.json)

## Requirements

### Requirement 1

**User Story:** As a hackathon participant, I want to enable Kiroween Mode via environment variable, so that I can showcase the Necro-Terminal theme without modifying code.

#### Acceptance Criteria

1. WHEN the environment variable `KIROWEEN_MODE` is set to `True` THEN the System SHALL load the Necro-Terminal theme
2. WHEN the environment variable `KIROWEEN_MODE` is set to `False` or is not set THEN the System SHALL load the standard NecoKeeper theme
3. WHEN the application starts THEN the System SHALL read the `KIROWEEN_MODE` configuration from `app/config.py`
4. WHEN the configuration is loaded THEN the System SHALL make the mode available to all templates via the settings object

### Requirement 2

**User Story:** As a user viewing the Necro-Terminal interface, I want to see a cyberpunk/horror visual design, so that the application matches the "Ghost in the Machine" concept.

#### Acceptance Criteria

1. WHEN Kiroween Mode is enabled THEN the System SHALL apply a pure black background color (#000000) to all pages
2. WHEN Kiroween Mode is enabled THEN the System SHALL apply terminal green (#33ff00) as the primary text color
3. WHEN Kiroween Mode is enabled THEN the System SHALL apply dim green (#1a8000) as the border color
4. WHEN Kiroween Mode is enabled THEN the System SHALL use monospace fonts (Courier New or system monospace) for all text
5. WHEN Kiroween Mode is enabled THEN the System SHALL display wireframe-style UI elements without filled backgrounds

### Requirement 3

**User Story:** As a user launching the Necro-Terminal, I want to see a dramatic boot sequence animation telling the 9th Life Protocol story, so that the experience feels immersive and thematic.

#### Acceptance Criteria

1. WHEN Kiroween Mode is enabled and the login page loads THEN the System SHALL display a boot sequence animation overlay
2. WHEN the boot sequence starts THEN the System SHALL display the animation for exactly 2.5 seconds
3. WHEN the boot sequence displays THEN the System SHALL show the following English text in sequence: "INITIALIZING 9TH_LIFE_PROTOCOL...", "UPLOADING CONSCIOUSNESS... COMPLETE.", "SCANNING FOR INEFFICIENCY... TARGET ACQUIRED.", "WELCOME, HUMAN COLLABORATOR."
4. WHEN the boot sequence completes THEN the System SHALL fade out the overlay and reveal the login form
5. WHEN the boot sequence is playing THEN the System SHALL prevent user interaction with underlying elements
6. WHEN the boot sequence displays THEN the System SHALL show terminal-style text effects (typing animation, cursor blink)

### Requirement 18: 9 Candles Boot Animation (The Sacrifice)

**User Story:** As a user viewing the boot sequence, I want to see a visual representation of the Master Cat's sacrifice through 9 candles being extinguished, so that I understand the story of the 9th Life Protocol.

#### Acceptance Criteria

1. WHEN the boot sequence starts THEN the System SHALL display 9 candle icons horizontally below the boot text
2. WHEN the candles are initially displayed THEN the System SHALL show all 9 candles in the "ON" (lit) state with green flames
3. WHEN the text "UPLOADING CONSCIOUSNESS..." appears THEN the System SHALL begin extinguishing candles from left to right
4. WHEN extinguishing candles THEN the System SHALL turn off one candle approximately every 200 milliseconds
5. WHEN a candle is extinguished THEN the System SHALL apply a brief flicker effect before transitioning to the "OFF" state
6. WHEN the boot sequence completes THEN the System SHALL leave only the rightmost (9th) candle lit
7. WHEN the final candle remains lit THEN the System SHALL display the text "WELCOME, HUMAN COLLABORATOR."
8. WHEN the candles are displayed THEN the System SHALL use the same candle icon style as the header Life Monitor (wireframe for OFF, green flame for ON)
9. WHEN the candles are displayed in the boot sequence THEN the System SHALL render them larger than the header candle icons for visual emphasis

### Requirement 4

**User Story:** As a user interacting with the Necro-Terminal, I want to see CRT monitor effects, so that the interface feels like a retro computer terminal.

#### Acceptance Criteria

1. WHEN Kiroween Mode is enabled THEN the System SHALL apply horizontal scanline effects across the entire viewport
2. WHEN Kiroween Mode is enabled THEN the System SHALL apply subtle screen curvature effect to simulate CRT bulge
3. WHEN Kiroween Mode is enabled THEN the System SHALL apply random glitch effects at intervals between 5-15 seconds
4. WHEN a glitch effect triggers THEN the System SHALL display visual distortion for 100-300 milliseconds
5. WHEN CRT effects are applied THEN the System SHALL ensure text remains readable

### Requirement 5

**User Story:** As a user reading text in the Necro-Terminal, I want to see cyberpunk/horror-themed English messages, so that the language matches the visual theme and maintains immersion.

#### Acceptance Criteria

1. WHEN Kiroween Mode is enabled THEN the System SHALL force the interface language to English and load translations from `en_necro.json` instead of standard locale files
2. WHEN displaying UI messages THEN the System SHALL transform standard terms into thematic equivalents (e.g., "Save" → "COMMIT_SOUL", "Loading" → "SUMMONING...", "Error" → "FATAL_GLITCH", "Volunteer" → "OPERATIVE")
3. WHEN displaying loading states THEN the System SHALL show cyberpunk-themed messages in English
4. WHEN displaying error messages THEN the System SHALL use cyberpunk/horror-themed language while maintaining clarity
5. WHEN Kiroween Mode is disabled THEN the System SHALL use standard translation files with normal language selection
6. WHEN Kiroween Mode is enabled THEN the System SHALL create `en_necro.json` based on `en.json` with cyberpunk/horror terminology replacements

### Requirement 6

**User Story:** As a user viewing animal icons in the Necro-Terminal, I want to see stylized ghost cat imagery, so that the visual assets match the "Ghost in the Machine" theme.

#### Acceptance Criteria

1. WHEN Kiroween Mode is enabled THEN the System SHALL use `halloween_icon.webp` as the favicon and app icon
2. WHEN displaying the site logo THEN the System SHALL use `halloween_logo.webp` in the header and branding areas
3. WHEN no animal profile image exists THEN the System SHALL display `halloween_logo_2.webp` as the placeholder
4. WHEN Kiroween Mode is disabled THEN the System SHALL display standard animal icons and images
5. WHEN icons are displayed THEN the System SHALL resize images appropriately for their context (favicon: 32x32, logo: responsive, placeholder: profile size)

### Requirement 14: English-Only Immersive Experience

**User Story:** As a user inside the Necro-Terminal, I want the experience to stay fully immersive in English with the standard language switcher hidden, so that the Kiroween presentation never breaks character.

#### Acceptance Criteria

1. WHEN Kiroween Mode is enabled THEN the System SHALL hide the language switcher controls on the admin login page, admin header, and public care pages
2. WHEN Kiroween Mode is enabled THEN the System SHALL force the interface to English and load en_necro.json without offering an in-app language toggle
3. WHEN Kiroween Mode is disabled THEN the System SHALL show the existing language switcher so users can change locales
4. WHEN writing automated tests THEN the System SHALL account for the absence of the language switcher in Kiroween Mode instead of asserting it unconditionally

### Requirement 15: Precision Targeting Interface

**User Story:** As a user operating the Necro-Terminal, I want a precision targeting crosshair cursor on every interactive surface, so that I feel like I'm performing operations inside the Master Cat's vision system.

#### Acceptance Criteria

1. WHEN Kiroween Mode is enabled THEN the System SHALL change the global mouse cursor to crosshair style
2. WHEN the cursor is displayed THEN the System SHALL apply the crosshair cursor to all interactive elements (buttons, links, inputs)
3. WHEN hovering over interactive elements THEN the System SHALL maintain the crosshair cursor instead of the default pointer
4. WHEN Kiroween Mode is disabled THEN the System SHALL use standard cursor styles
5. WHEN the cursor style is applied THEN the System SHALL ensure it works across all major browsers

### Requirement 16

**User Story:** As a user viewing the Necro-Terminal interface, I want to see the Life Monitor showing the Master Cat's remaining lives, so that I understand the system is powered by his final life.

#### Acceptance Criteria

1. WHEN Kiroween Mode is enabled THEN the System SHALL display a "Life Monitor" indicator in the header showing 9 lives
2. WHEN the Life Monitor is displayed THEN the System SHALL show 8 lives as "LOST" (marked with × or crossed out)
3. WHEN the Life Monitor is displayed THEN the System SHALL show the 9th life as "ACTIVE" with a blinking/pulsing animation
4. WHEN the Life Monitor is rendered THEN the System SHALL use terminal green color for the active life and dim green for lost lives
5. WHEN Kiroween Mode is disabled THEN the System SHALL not display the Life Monitor

### Requirement 17: Soul Commitment Glitch Feedback

**User Story:** As a user performing save/delete operations in the Necro-Terminal, I want to see the Soul Commitment glitch as intense visual feedback, so that I feel the Master Cat is exerting power to commit data to reality.

#### Acceptance Criteria

1. WHEN a create operation succeeds (POST request) THEN the System SHALL trigger an intense Soul Commitment Glitch effect
2. WHEN an update operation succeeds (PUT/PATCH request) THEN the System SHALL trigger an intense Soul Commitment Glitch effect
3. WHEN a delete operation succeeds (DELETE request) THEN the System SHALL trigger an intense Soul Commitment Glitch effect
4. WHEN the Soul Commitment Glitch triggers THEN the System SHALL apply stronger visual distortion than random glitches (duration 300-500ms)
5. WHEN the Soul Commitment Glitch triggers THEN the System SHALL apply screen-wide noise/static effect
6. WHEN the glitch completes THEN the System SHALL return to normal display state
7. WHEN Kiroween Mode is disabled THEN the System SHALL not trigger Soul Commitment Glitch effects

### Requirement 13

**User Story:** As a developer, I want to properly manage Halloween theme assets, so that the correct images are available in the static directory.

#### Acceptance Criteria

1. WHEN setting up the theme THEN the System SHALL copy `tmp/for_icon/halloween_icon.webp` to `app/static/icons/halloween_icon.webp`
2. WHEN setting up the theme THEN the System SHALL copy `tmp/for_icon/halloween_logo.webp` to `app/static/icons/halloween_logo.webp`
3. WHEN setting up the theme THEN the System SHALL copy `tmp/for_icon/halloween_logo_2.webp` to `app/static/icons/halloween_logo_2.webp`
4. WHEN images are copied THEN the System SHALL resize them if necessary to optimize file size
5. WHEN templates reference these assets THEN the System SHALL use conditional logic to select between standard and Halloween versions

### Requirement 7

**User Story:** As a developer, I want the theme toggle to be template-based, so that no business logic changes are required.

#### Acceptance Criteria

1. WHEN implementing theme features THEN the System SHALL use Jinja2 conditional statements to switch between themes
2. WHEN rendering templates THEN the System SHALL access the Kiroween Mode flag via `settings.KIROWEEN_MODE`
3. WHEN applying styles THEN the System SHALL conditionally load CSS files based on the mode flag
4. WHEN FastAPI routes execute THEN the System SHALL not modify business logic based on theme mode
5. WHEN SQLAlchemy models are accessed THEN the System SHALL maintain identical behavior regardless of theme mode

### Requirement 8

**User Story:** As a developer, I want comprehensive CSS organization, so that theme styles are maintainable and don't conflict.

#### Acceptance Criteria

1. WHEN Kiroween Mode styles are defined THEN the System SHALL store them in a separate `terminal.css` file
2. WHEN the base template loads THEN the System SHALL conditionally include `terminal.css` only when Kiroween Mode is enabled
3. WHEN CSS classes are applied THEN the System SHALL use theme-specific class names to avoid conflicts
4. WHEN standard mode is active THEN the System SHALL use Tailwind CSS classes without modification
5. WHEN Kiroween Mode is active THEN the System SHALL override Tailwind styles with terminal theme styles

### Requirement 9

**User Story:** As a QA tester, I want to verify both themes work correctly, so that I can ensure no regressions occur.

#### Acceptance Criteria

1. WHEN Kiroween Mode is toggled THEN the System SHALL maintain all functional capabilities of the standard theme
2. WHEN forms are submitted in either mode THEN the System SHALL process data identically
3. WHEN navigation occurs in either mode THEN the System SHALL maintain consistent routing behavior
4. WHEN API calls are made in either mode THEN the System SHALL return identical responses
5. WHEN switching between modes THEN the System SHALL require only an application restart (no database changes)

### Requirement 10

**User Story:** As a user on mobile devices, I want the Necro-Terminal theme to be responsive, so that the experience works on all screen sizes.

#### Acceptance Criteria

1. WHEN Kiroween Mode is enabled on mobile THEN the System SHALL apply responsive CRT effects that scale appropriately
2. WHEN viewing on small screens THEN the System SHALL maintain readable text sizes in monospace font
3. WHEN touch interactions occur THEN the System SHALL provide adequate touch targets despite wireframe styling
4. WHEN the viewport changes THEN the System SHALL adjust scanline density to maintain visual quality
5. WHEN mobile keyboards appear THEN the System SHALL ensure form inputs remain visible and usable

### Requirement 11

**User Story:** As a developer, I want clear documentation of the feature toggle, so that future maintainers understand the implementation.

#### Acceptance Criteria

1. WHEN the feature is implemented THEN the System SHALL include comments in `config.py` explaining the toggle
2. WHEN the feature is implemented THEN the System SHALL update `.env.example` with the `KIROWEEN_MODE` variable
3. WHEN the feature is implemented THEN the System SHALL document the theme in the project README
4. WHEN templates use conditional logic THEN the System SHALL include comments explaining theme-specific blocks
5. WHEN CSS files are created THEN the System SHALL include header comments describing the theme purpose

### Requirement 12

**User Story:** As a performance-conscious developer, I want the theme toggle to have minimal performance impact, so that user experience remains smooth.

#### Acceptance Criteria

1. WHEN CRT effects are applied THEN the System SHALL use CSS animations rather than JavaScript where possible
2. WHEN glitch effects trigger THEN the System SHALL use requestAnimationFrame for smooth rendering
3. WHEN the page loads THEN the System SHALL load only the CSS files required for the active theme
4. WHEN images are filtered THEN the System SHALL use CSS filters rather than canvas manipulation
5. WHEN the boot sequence plays THEN the System SHALL complete within 2.5 seconds on standard hardware

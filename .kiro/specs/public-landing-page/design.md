# Design Document

## Overview

The NecoKeeper public landing page is a static web page that effectively communicates the project's value to hackathon visitors. It adopts a clean and modern aesthetic, implemented with FastAPI + Jinja2 + Tailwind CSS.

**Design Concept:**
- **Clean & Modern**: Clear information delivery with sophisticated minimal design
- **Distinctive Typography**: Memorable visuals with distinctive font choices
- **Subtle Motion**: Sophisticated experience with subtle animations
- **Responsive First**: Optimized from mobile to desktop

## Architecture

### Component Structure

```
Landing Page
├── Navigation Bar
│   ├── Logo + Brand Name
│   └── Navigation Links (How it works, Tech, GitHub, Demo Video)
├── Hero Section
│   ├── Badge (Project Category)
│   ├── Headline
│   ├── Lead Description
│   ├── CTA Buttons (Try Demo, View Source)
│   └── Meta Information
├── Demo Preview Panel
│   ├── Panel Header (Title + Status)
│   ├── Info Cards Grid (Cat, Care, Health, QR)
│   └── Timeline (How it works)
├── Video Section
│   ├── Section Heading
│   └── YouTube Embed (Responsive)
└── Footer
    └── Tech Stack Information
```

### Technology Stack

- **Backend**: FastAPI (Python 3.12+)
- **Template Engine**: Jinja2
- **CSS Framework**: Tailwind CSS (CDN)
- **Fonts**: Google Fonts (distinctive choices)
- **Icons**: Unicode emoji + custom SVG
- **Video**: YouTube iframe embed

## Components and Interfaces

### 1. FastAPI Route Handler

**File**: `app/api/v1/public_pages.py`

```python
@router.get("/", response_class=HTMLResponse)
async def landing_page(request: Request):
    """
    Render the public landing page.

    This is a project introduction page for hackathon visitors.
    It is publicly accessible (no authentication) and introduces
    the project overview, features, and demo.

    Args:
        request: FastAPI Request object

    Returns:
        HTMLResponse: HTML content of the landing page

    Example:
        GET /
    """
    return templates.TemplateResponse(
        "public/landing.html",
        {
            "request": request,
            "settings": settings,
            "github_url": "https://github.com/okajun35/NecoKeeper",
            "demo_video_url": "https://www.youtube.com/embed/YOUR_VIDEO_ID",
        },
    )
```

### 2. Jinja2 Template

**File**: `app/templates/public/landing.html`

**Template Structure:**
```jinja2
<!DOCTYPE html>
<html lang="en">
<head>
    <!-- Meta tags -->
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="description" content="NecoKeeper - AI-powered cat care management for shelters">

    <!-- Title -->
    <title>NecoKeeper – AI-powered Cat Care Management</title>

    <!-- Favicon -->
    <link rel="icon" type="image/svg+xml" href="/static/icons/default_icon.svg">

    <!-- Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>

    <!-- Google Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=...&display=swap" rel="stylesheet">

    <!-- Custom Styles -->
    <style>
        /* CSS Variables for theming */
        /* Typography styles */
        /* Animation keyframes */
        /* Component-specific styles */
    </style>
</head>
<body>
    <!-- Navigation -->
    <!-- Hero Section -->
    <!-- Demo Preview Panel -->
    <!-- Video Section -->
    <!-- Footer -->
</body>
</html>
```

### 3. CSS Design System

**Color Palette:**
```css
:root {
    /* Background */
    --bg-primary: #f5f5f7;
    --bg-card: #ffffff;

    /* Accent Colors */
    --accent-primary: #ff7f50;  /* Coral - warm, friendly */
    --accent-soft: rgba(255, 127, 80, 0.08);

    /* Text Colors */
    --text-primary: #111827;
    --text-secondary: #4b5563;
    --text-muted: #9ca3af;

    /* Border */
    --border-soft: #e5e7eb;

    /* Status Colors */
    --status-success: #15803d;
    --status-success-bg: #ecfdf5;
    --status-success-border: #bbf7d0;
}
```

**Typography Scale:**
```css
/* Display Font: Distinctive, modern */
--font-display: 'Outfit', 'DM Sans', sans-serif;

/* Body Font: Clean, readable */
--font-body: 'Inter', system-ui, sans-serif;

/* Sizes */
--text-xs: 0.75rem;    /* 12px */
--text-sm: 0.875rem;   /* 14px */
--text-base: 1rem;     /* 16px */
--text-lg: 1.125rem;   /* 18px */
--text-xl: 1.25rem;    /* 20px */
--text-2xl: 1.5rem;    /* 24px */
--text-3xl: 1.875rem;  /* 30px */
--text-4xl: 2.25rem;   /* 36px */
```

**Spacing System:**
```css
/* Based on 4px grid */
--space-1: 0.25rem;   /* 4px */
--space-2: 0.5rem;    /* 8px */
--space-3: 0.75rem;   /* 12px */
--space-4: 1rem;      /* 16px */
--space-6: 1.5rem;    /* 24px */
--space-8: 2rem;      /* 32px */
--space-12: 3rem;     /* 48px */
--space-16: 4rem;     /* 64px */
```

### 4. Component Specifications

#### Navigation Bar
```html
<header class="nav">
    <div class="nav-left">
        <div class="logo-circle">🐾</div>
        <div class="brand-name">NecoKeeper</div>
    </div>
    <nav class="nav-links">
        <a href="#how">How it works</a>
        <a href="#video">Demo Video</a>
        <a href="#tech">Tech</a>
        <a href="{{ github_url }}" target="_blank" rel="noreferrer">GitHub</a>
        <a class="cta-link" href="#video">Watch demo</a>
    </nav>
</header>
```

**Styling:**
- Fixed/sticky positioning optional
- Horizontal layout with space-between
- Logo: 28px circle with emoji
- Links: subtle hover effects
- CTA link: bordered pill style

#### Hero Section
```html
<section class="hero">
    <div class="badge">
        🐱 Built for cat shelters · AI + AWS Kiro
    </div>
    <h1 class="hero-title">
        AI-powered daily care management for rescued cats.
    </h1>
    <p class="hero-lead">
        NecoKeeper turns handwritten care logs and veterinary notes into
        structured data. Volunteers keep using paper; the system handles
        digitization, aggregation, and QR-based access for each cat.
    </p>
    <div class="hero-actions">
        <a href="/admin">
            <button class="btn btn-primary">
                Try the live demo
                <span>↗</span>
            </button>
        </a>
        <a href="{{ github_url }}" target="_blank" rel="noreferrer">
            <button class="btn btn-ghost">
                View source
            </button>
        </a>
    </div>
    <div class="hero-meta">
        <span>✅ Focus: shelters & volunteer groups</span>
        <span>✅ Tech: FastAPI, SQLite, OCR, AWS Kiro</span>
    </div>
</section>
```

**Styling:**
- Max-width: 520px
- Badge: small pill with soft background
- Title: Large, bold, responsive (clamp 1.9rem to 2.6rem)
- Lead: Medium size, secondary color
- Buttons: Rounded, contrasting styles
- Meta: Small text with checkmarks

#### Demo Preview Panel
```html
<aside class="panel">
    <div class="panel-header">
        <div class="panel-title">Rescued cat overview · Demo</div>
        <span class="status-pill">Shelter load: 18 cats</span>
    </div>
    <div class="panel-grid">
        <div class="card">
            <strong>CAT</strong>
            <span>"Mikan" · 2 y/o female, shy but curious</span>
        </div>
        <div class="card">
            <strong>CARE TODAY</strong>
            <span>Food ✔ · Water ✔ · Litter ✔ · Play ✕</span>
        </div>
        <div class="card">
            <strong>HEALTH</strong>
            <span>Next vet visit: Dec 12 · Weight trend stable</span>
        </div>
        <div class="card">
            <strong>QR CARD</strong>
            <span>Scan at the cage to open profile instantly</span>
        </div>
    </div>
    <ul class="timeline">
        <li>
            <div class="dot"></div>
            <div><strong>1.</strong> Volunteers fill in handwritten daily care logs as usual.</div>
        </li>
        <li>
            <div class="dot"></div>
            <div><strong>2.</strong> NecoKeeper reads the sheet image, extracts items with AI, and generates JSON.</div>
        </li>
        <li>
            <div class="dot"></div>
            <div><strong>3.</strong> The API stores care logs, vet records, and notes per cat.</div>
        </li>
        <li>
            <div class="dot"></div>
            <div><strong>4.</strong> QR codes on each cage open the latest profile in one tap.</div>
        </li>
    </ul>
</aside>
```

**Styling:**
- Max-width: 520px
- Card background with shadow
- Rounded corners (1.3rem)
- Grid layout for info cards (2 columns)
- Timeline with dots and dashed border

#### Video Section
```html
<section class="video-section" id="video">
    <div class="video-container">
        <h2 class="video-heading">See NecoKeeper in Action</h2>
        <div class="video-wrapper">
            <iframe
                src="{{ demo_video_url }}"
                title="NecoKeeper Demo Video"
                frameborder="0"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowfullscreen
                class="video-iframe"
            ></iframe>
        </div>
    </div>
</section>
```

**Styling:**
- Responsive iframe wrapper (16:9 aspect ratio)
- Centered layout
- Padding for breathing room
- Smooth border radius

**Responsive Video CSS:**
```css
.video-wrapper {
    position: relative;
    padding-bottom: 56.25%; /* 16:9 aspect ratio */
    height: 0;
    overflow: hidden;
}

.video-iframe {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    border-radius: 0.75rem;
}
```

#### Footer
```html
<footer class="footer" id="tech">
    <span>Built with FastAPI · SQLite · Docker · Render</span>
    <span>AI workflows powered by AWS Kiro & OCR</span>
</footer>
```

**Styling:**
- Small text
- Muted color
- Border top
- Flex layout with space-between

## Data Models

### Template Context Data

```python
{
    "request": Request,              # FastAPI request object
    "settings": Settings,            # App settings (from config)
    "github_url": str,               # GitHub repository URL
    "demo_video_url": str,           # YouTube embed URL
}
```

**Note**: All data is static and hardcoded in the template or passed as simple strings. No database queries required.

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Page loads successfully without authentication

*For any* HTTP GET request to the landing page endpoint, the system should return a 200 OK status code without requiring authentication headers or cookies.

**Validates: Requirements 1.1, 9.5**

### Property 2: Responsive layout adapts to all screen sizes

*For any* viewport width between 320px and 2560px, all content should remain readable and interactive elements should remain accessible without horizontal scrolling.

**Validates: Requirements 1.5, 2.5, 3.5, 7.2, 7.3**

### Property 3: External links open in new tabs

*For any* external link (GitHub, YouTube), clicking the link should open the target URL in a new browser tab (target="_blank") with appropriate security attributes (rel="noreferrer" or rel="noopener").

**Validates: Requirements 4.3**

### Property 4: Video does not autoplay

*For any* page load, the YouTube video iframe should not include autoplay parameters, ensuring the video only plays when the user explicitly clicks the play button.

**Validates: Requirements 5.5**

### Property 5: CTA buttons navigate to correct destinations

*For any* CTA button click, the "Try Live Demo" button should navigate to /admin and the "View Source Code" button should open the GitHub repository URL.

**Validates: Requirements 4.2, 4.3**

### Property 6: Semantic HTML structure is maintained

*For any* page render, the HTML should use semantic elements (header, nav, main, section, aside, footer) and include appropriate ARIA labels for accessibility.

**Validates: Requirements 7.4, 7.5**

### Property 7: CSS variables define consistent theming

*For any* color or spacing value used in the design, it should be defined as a CSS variable in the :root selector to ensure consistency across all components.

**Validates: Requirements 8.1**

### Property 8: Interactive elements provide hover feedback

*For any* interactive element (buttons, links), hovering should trigger a visual state change (color, transform, or opacity) to provide user feedback.

**Validates: Requirements 4.5**

## Error Handling

### Client-Side Errors

**YouTube Video Load Failure:**
- **Scenario**: YouTube iframe fails to load (network issue, blocked content)
- **Handling**: Graceful degradation - show placeholder or fallback message
- **Implementation**: Optional - add onerror handler to iframe

**External Link Failures:**
- **Scenario**: GitHub or admin page is unreachable
- **Handling**: Browser's default error handling (404, connection timeout)
- **Implementation**: No custom handling needed - standard HTTP behavior

### Server-Side Errors

**Template Rendering Error:**
- **Scenario**: Jinja2 template syntax error or missing variable
- **Handling**: FastAPI's default error handler returns 500 Internal Server Error
- **Implementation**: Ensure all template variables are provided in context

**Route Not Found:**
- **Scenario**: User accesses incorrect URL
- **Handling**: FastAPI's default 404 handler
- **Implementation**: No custom handling needed

## Testing Strategy

### Unit Tests

**Test File**: `tests/api/v1/test_public_pages.py`

```python
def test_landing_page_returns_200(test_client):
    """ランディングページが200を返す"""
    response = test_client.get("/")
    assert response.status_code == 200

def test_landing_page_contains_title(test_client):
    """ランディングページにタイトルが含まれる"""
    response = test_client.get("/")
    assert "NecoKeeper" in response.text

def test_landing_page_contains_cta_buttons(test_client):
    """ランディングページにCTAボタンが含まれる"""
    response = test_client.get("/")
    assert "Try the live demo" in response.text
    assert "View source" in response.text

def test_landing_page_contains_video_embed(test_client):
    """ランディングページにYouTube埋め込みが含まれる"""
    response = test_client.get("/")
    assert "youtube.com/embed" in response.text
    assert "iframe" in response.text

def test_landing_page_no_authentication_required(test_client):
    """ランディングページは認証不要"""
    # No auth headers
    response = test_client.get("/")
    assert response.status_code == 200
```

### Manual Testing Checklist

**Visual Testing:**
- [ ] Hero section displays correctly on desktop (1920x1080)
- [ ] Hero section displays correctly on tablet (768x1024)
- [ ] Hero section displays correctly on mobile (375x667)
- [ ] Demo panel cards are readable and well-spaced
- [ ] Timeline dots align properly with text
- [ ] YouTube video maintains 16:9 aspect ratio on all screens
- [ ] Footer information is visible and readable

**Interaction Testing:**
- [ ] "Try Live Demo" button navigates to /admin
- [ ] "View Source Code" button opens GitHub in new tab
- [ ] Navigation links scroll to correct sections (if anchor links)
- [ ] YouTube video plays when clicked
- [ ] YouTube video does not autoplay on page load
- [ ] Hover states work on all buttons and links

**Accessibility Testing:**
- [ ] Page can be navigated with keyboard only (Tab, Enter)
- [ ] Screen reader announces all content correctly
- [ ] Color contrast meets WCAG AA standards (4.5:1 for text)
- [ ] All images have alt text (if any)
- [ ] Focus indicators are visible

**Performance Testing:**
- [ ] Page loads within 2 seconds on 3G connection
- [ ] Lighthouse Performance score > 90
- [ ] Lighthouse Accessibility score > 95
- [ ] No console errors or warnings

### Browser Compatibility

**Target Browsers:**
- Chrome/Edge (latest 2 versions)
- Firefox (latest 2 versions)
- Safari (latest 2 versions)
- Mobile Safari (iOS 14+)
- Chrome Mobile (Android 10+)

**Known Limitations:**
- Tailwind CSS CDN requires JavaScript enabled
- YouTube embed requires third-party cookies enabled

## Implementation Notes

### Font Selection

**Display Font Options** (choose one):
- **Outfit**: Geometric, modern, distinctive
- **DM Sans**: Clean, slightly quirky
- **Manrope**: Rounded, friendly
- **Space Grotesk**: Technical, unique (avoid if overused)

**Body Font**:
- **Inter**: Clean, highly readable (acceptable for body text)
- **System UI**: Fallback for performance

### Animation Guidelines

**Subtle Animations:**
```css
/* Fade in on load */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

.hero {
    animation: fadeIn 0.6s ease-out;
}

/* Stagger children */
.panel-grid .card {
    animation: fadeIn 0.6s ease-out;
    animation-fill-mode: both;
}

.panel-grid .card:nth-child(1) { animation-delay: 0.1s; }
.panel-grid .card:nth-child(2) { animation-delay: 0.2s; }
.panel-grid .card:nth-child(3) { animation-delay: 0.3s; }
.panel-grid .card:nth-child(4) { animation-delay: 0.4s; }

/* Hover effects */
.btn {
    transition: all 0.2s ease;
}

.btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}
```

### Responsive Breakpoints

```css
/* Mobile First Approach */

/* Small devices (phones, 640px and up) */
@media (min-width: 640px) {
    /* Adjust font sizes, spacing */
}

/* Medium devices (tablets, 768px and up) */
@media (min-width: 768px) {
    /* Switch to side-by-side layout for hero + panel */
    .main {
        flex-direction: row;
    }
}

/* Large devices (desktops, 1024px and up) */
@media (min-width: 1024px) {
    /* Increase max-widths, spacing */
}
```

### SEO Optimization

**Meta Tags:**
```html
<meta name="description" content="NecoKeeper - AI-powered cat care management system for shelters. Digitize handwritten logs, track health records, and manage rescued cats efficiently.">
<meta name="keywords" content="cat shelter, animal care, AI, OCR, FastAPI, volunteer management">
<meta property="og:title" content="NecoKeeper – AI-powered Cat Care Management">
<meta property="og:description" content="Turn handwritten care logs into structured data with AI">
<meta property="og:type" content="website">
<meta property="og:url" content="https://your-domain.com/">
<meta property="og:image" content="https://your-domain.com/static/og-image.png">
<meta name="twitter:card" content="summary_large_image">
```

## Deployment Considerations

### Static Assets

**Required Files:**
- `/static/icons/default_icon.svg` - Favicon
- `/static/og-image.png` - Open Graph image (optional)

**CDN Resources:**
- Tailwind CSS: `https://cdn.tailwindcss.com`
- Google Fonts: `https://fonts.googleapis.com`

### Environment Variables

**Configuration** (in `.env`):
```bash
# YouTube video ID (extract from URL)
DEMO_VIDEO_ID=YOUR_VIDEO_ID

# GitHub repository URL
GITHUB_REPO_URL=https://github.com/okajun35/NecoKeeper
```

**Usage in code:**
```python
settings = get_settings()
demo_video_url = f"https://www.youtube.com/embed/{settings.demo_video_id}"
github_url = settings.github_repo_url
```

### Performance Optimization

**Lazy Loading:**
```html
<!-- Lazy load YouTube iframe -->
<iframe loading="lazy" src="..."></iframe>
```

**Preconnect to External Domains:**
```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://www.youtube.com">
```

**Minification:**
- Tailwind CSS is already minified from CDN
- Inline CSS should be minified in production (optional)

## Future Enhancements

**Phase 2 (Optional):**
1. **Internationalization**: Add Japanese language support
2. **Dark Mode**: Toggle between light/dark themes
3. **Interactive Demo**: Embedded demo without login
4. **Analytics**: Track visitor engagement (Google Analytics)
5. **A/B Testing**: Test different headlines and CTAs

**Phase 3 (Optional):**
1. **Blog Section**: Project updates and case studies
2. **Testimonials**: Quotes from shelter volunteers
3. **Gallery**: Photos of rescued cats
4. **Contact Form**: Inquiry form for interested shelters

---

**Design Approval Required**: This design document should be reviewed and approved before proceeding to implementation.

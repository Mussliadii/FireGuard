"""Custom CSS so the app reads as a product, not a default Streamlit demo.

Theming (colors, dark mode) lives in .streamlit/config.toml — that's what
native widgets (buttons, inputs, sliders) pick up automatically. This file
only adds what config.toml can't: fonts, the hero banner, badge pills, and
tightening up default Streamlit spacing.
"""

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

#MainMenu, footer, header[data-testid="stHeader"] { visibility: hidden; height: 0; }

.block-container {
    max-width: 1100px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

/* Hero */
.fg-hero {
    text-align: center;
    padding: 1.5rem 0 2.5rem;
}
.fg-hero h1 {
    font-size: 2.6rem;
    font-weight: 800;
    letter-spacing: -0.02em;
    margin-bottom: 0.4rem;
}
.fg-hero p {
    color: #9fb3a4;
    font-size: 1.1rem;
    max-width: 560px;
    margin: 0 auto;
}
.fg-brand {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.6rem;
    font-weight: 700;
    font-size: 1.1rem;
    margin-bottom: 0.75rem;
}

/* Badges */
.fg-badge {
    display: inline-block;
    padding: 0.2rem 0.7rem;
    border-radius: 999px;
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 0.02em;
}
.fg-badge-low { background: #15301f; color: #7fe3a0; }
.fg-badge-medium { background: #332f14; color: #e3d57f; }
.fg-badge-high { background: #351616; color: #e37f7f; }

/* Section headers inside tabs */
.fg-section-title {
    font-size: 1.3rem;
    font-weight: 700;
    margin-bottom: 0.25rem;
}
.fg-section-sub {
    color: #9fb3a4;
    margin-bottom: 1.25rem;
}

/* Tabs look more like a nav bar */
.stTabs [data-baseweb="tab-list"] {
    gap: 0.5rem;
}
.stTabs [data-baseweb="tab"] {
    font-weight: 600;
}

/* Footer */
.fg-footer {
    text-align: center;
    color: #9fb3a4;
    font-size: 0.85rem;
    padding-top: 2rem;
    margin-top: 2rem;
    border-top: 1px solid #22311f;
}
.fg-footer a { color: #ff7a45; text-decoration: none; }
</style>
"""

HERO_ICON_SVG = """
<svg width="32" height="32" viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
  <rect width="64" height="64" rx="12" fill="#121a15"/>
  <path d="M32 6c6 10-6 12-6 20a10 10 0 0 0 20 0c0-4-2-7-4-9 1 6-3 8-5 6 3-6-1-12-5-17z" fill="#e37f7f"/>
  <path d="M27 34a7 7 0 0 0 14 0c0-2-1-4-2-5 0 4-2 5-3 4 1-3-1-6-3-8-2 3-6 5-6 9z" fill="#e3d57f"/>
</svg>
"""


def badge(risk: str, text: str | None = None) -> str:
    return f'<span class="fg-badge fg-badge-{risk}">{(text or risk).upper()}</span>'

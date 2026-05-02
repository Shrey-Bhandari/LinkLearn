"""Configuration for the content extraction service."""

# API Configuration
API_HOST = "0.0.0.0"
API_PORT = 8000
API_DEBUG = False

# HTML Parsing Configuration
HTML_PARSER = "html.parser"  # Can also use "lxml", "html5lib", etc.

# Content Extraction Configuration
HEADING_LEVELS = ["h1", "h2", "h3"]  # Headings to extract

# Elements to remove by tag
REMOVAL_TAGS = {
    "nav",          # Navigation menus
    "footer",       # Footers
    "header",       # Header sections
    "aside",        # Sidebars and aside content
    "script",       # JavaScript
    "style",        # CSS styles
    "noscript",     # No-script fallbacks
    "meta",         # Metadata
    "link",         # Link tags
    "iframe",       # Embedded frames
    "form",         # Forms
    "button",       # Buttons
}

# Ad pattern detection
AD_PATTERNS = {
    "ad",
    "advertisement",
    "banner",
    "sponsor",
    "promo",
    "popup",
    "modal",
    "sidebar",
    "widget",
    "social",
}

# Logging Configuration
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Performance Configuration
MAX_HTML_SIZE = 10 * 1024 * 1024  # 10 MB limit for incoming HTML
REQUEST_TIMEOUT = 30  # seconds

# Feature Flags
REMOVE_EMPTY_SECTIONS = True
PRESERVE_WHITESPACE = False
COMBINE_PARAGRAPHS = True

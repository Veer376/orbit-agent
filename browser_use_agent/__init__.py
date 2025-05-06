"""Browser Use Agent package."""

import os

# Default model to use (can be overridden with environment variable)
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-1.5-flash")
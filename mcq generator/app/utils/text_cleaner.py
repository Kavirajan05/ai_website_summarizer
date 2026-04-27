"""
app/utils/text_cleaner.py

Utility functions for normalising extracted document text before
sending it to the Gemini API.
"""

import re


def clean(text: str, max_chars: int = 8000) -> str:
    """
    Clean and truncate raw extracted text.

    Steps:
    1. Replace multiple consecutive newlines with a single newline.
    2. Replace multiple consecutive spaces/tabs with a single space.
    3. Strip leading/trailing whitespace.
    4. Truncate to `max_chars` to stay within Gemini token limits.

    Args:
        text:      The raw text string extracted from a document.
        max_chars: Maximum number of characters to keep (default 8000).

    Returns:
        The cleaned, truncated string.
    """
    # Collapse consecutive blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Collapse consecutive spaces / tabs into a single space
    text = re.sub(r"[ \t]+", " ", text)

    # Strip surrounding whitespace
    text = text.strip()

    # Truncate to respect Gemini's context window
    if len(text) > max_chars:
        text = text[:max_chars]

    return text

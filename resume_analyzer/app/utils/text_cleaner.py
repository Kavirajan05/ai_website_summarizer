import re

def clean_text(text: str) -> str:
    """
    Cleans extracted text by removing extra whitespaces,
    normalizing line breaks, and removing strange characters.
    """
    # Remove excessive newlines
    text = re.sub(r'\n+', '\n', text)
    # Remove excessive spaces
    text = re.sub(r' +', ' ', text)
    # Remove non-printable characters
    text = "".join(char for char in text if char.isprintable() or char in "\n\t")
    return text.strip()

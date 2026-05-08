import re
import unicodedata


def normalize(text: str) -> str:
    # Steps 1 & 2: full-width alphanumeric/symbols → half-width, half-width kana → full-width kana
    text = unicodedata.normalize("NFKC", text)
    # Step 3: lowercase
    text = text.lower()
    # Step 4: compress whitespace
    text = re.sub(r"\s+", " ", text)
    # Step 5: strip
    return text.strip()

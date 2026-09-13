import re


def clean_text(text):
    text = text.lower()

    # Replace special characters with spaces
    text = re.sub(r"[^a-zA-Z0-9+#.\s]", " ", text)

    # Remove extra spaces
    text = re.sub(r"\s+", " ", text)

    return text.strip()
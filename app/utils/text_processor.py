import re

def clean_text(text: str) -> str:
    """
    Cleans extracted text by removing control chars, extra spaces, and newlines.
    """
    text = re.sub(r"\s+", " ", text)  # collapse whitespace
    text = text.replace("\x00", "")   # remove null bytes
    text = re.sub(r"[^ -~]+", " ", text)  # remove non-ASCII chars
    return text.strip()


def split_sentences(text: str) -> list:
    """
    Splits a large text blob into sentences. Optional helper for chunking.
    """
    sentences = re.split(r'(?<=[.!?]) +', text)
    return [s.strip() for s in sentences if s.strip()]

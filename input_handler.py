# -*- coding: utf-8 -*-
"""
input_handler.py - Unified input resolution for the analysis pipeline.

Routes raw text strings and URLs through a common interface, returning
a structured dict with the resolved text content.
"""
import nltk

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt_tab', quiet=True)


def fetch_text(source: str) -> dict:
    """
    Resolves a text input (raw string or URL) into a structured dict.

    Args:
        source: Either a URL (starting with http/https) or a raw text string.

    Returns:
        dict with keys: type, text, and optionally url/title.
    """
    if source.startswith("http://") or source.startswith("https://"):
        try:
            import newspaper
            article = newspaper.Article(source)
            article.download()
            article.parse()
            return {
                "type": "url",
                "url": source,
                "title": article.title,
                "text": article.text
            }
        except Exception as e:
            return {"type": "error", "message": str(e)}
    else:
        return {"type": "text", "text": source}


def extract_claim_evidence(input_dict: dict) -> dict:
    """
    Extracts a structured claim and evidence from the resolved input.

    - For URL inputs: the article title becomes the claim.
    - For raw text: the first sentence is the claim.
    - The remainder of the text becomes the evidence.

    Args:
        input_dict: The dict returned by fetch_text().

    Returns:
        dict with keys: claim, evidence.
    """
    text = input_dict.get("text", "")

    # Use the article title as the claim when available
    if input_dict.get("type") == "url" and input_dict.get("title"):
        claim = input_dict["title"].strip()
        evidence = text.strip()
    else:
        # Split into sentences and use the first as the claim
        try:
            sentences = nltk.tokenize.sent_tokenize(text.strip())
        except Exception:
            sentences = text.strip().split(". ")

        if sentences:
            claim = sentences[0].strip()
            evidence = " ".join(sentences[1:]).strip()
        else:
            claim = text.strip()
            evidence = ""

    return {
        "claim": claim,
        "evidence": evidence
    }

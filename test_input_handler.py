import pytest
from unittest.mock import patch, MagicMock
from input_handler import fetch_text, extract_claim_evidence

def test_fetch_text_raw_string():
    result = fetch_text("This is some raw text.")
    assert result["type"] == "text"
    assert result["text"] == "This is some raw text."

@patch('newspaper.Article')
def test_fetch_text_url(mock_article_class):
    mock_instance = mock_article_class.return_value
    mock_instance.title = "Test Article"
    mock_instance.text = "This is the body of the test article."
    
    result = fetch_text("https://example.com/test-article")
    
    assert result["type"] == "url"
    assert result["url"] == "https://example.com/test-article"
    assert result["title"] == "Test Article"
    assert result["text"] == "This is the body of the test article."
    mock_instance.download.assert_called_once()
    mock_instance.parse.assert_called_once()

def test_extract_claim_evidence_url():
    input_dict = {
        "type": "url",
        "url": "https://example.com",
        "title": "Breaking News",
        "text": "This is paragraph 1.\n\nThis is paragraph 2."
    }
    extracted = extract_claim_evidence(input_dict)
    assert extracted["claim"] == "Breaking News"
    assert extracted["evidence"] == "This is paragraph 1.\n\nThis is paragraph 2."

def test_extract_claim_evidence_text():
    input_dict = {
        "type": "text",
        "text": "First sentence is the claim. Second sentence is evidence. Third is more evidence."
    }
    extracted = extract_claim_evidence(input_dict)
    assert extracted["claim"] == "First sentence is the claim."
    assert extracted["evidence"] == "Second sentence is evidence. Third is more evidence."

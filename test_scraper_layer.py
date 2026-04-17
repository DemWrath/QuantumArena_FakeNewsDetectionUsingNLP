import pytest
from unittest.mock import patch, MagicMock
from scraper_layer import SourceIntelligenceTracker

def test_extract_domain():
    """Verify various URL strings are correctly parsed into exact domains (SRC-03)."""
    tracker = SourceIntelligenceTracker()
    assert tracker._extract_domain("https://www.foxnews.com/opinion/article") == "foxnews.com"
    assert tracker._extract_domain("http://edition.cnn.com/world/news") == "cnn.com"
    assert tracker._extract_domain("raw_text") == "unknown"
    assert tracker._extract_domain(None) == "unknown"

@patch("scraper_layer.requests.get")
def test_mbfc_scrape_403(mock_get):
    """Ensure the scraper gracefully returns {} if blocked by Cloudflare (SRC-02)."""
    mock_response = MagicMock()
    mock_response.status_code = 403
    mock_get.return_value = mock_response
    
    tracker = SourceIntelligenceTracker()
    res = tracker._scrape_mbfc("dummy.com")
    assert res == {}

@patch("scraper_layer.requests.get")
def test_mbfc_scrape_success(mock_get):
    """Ensure MBFC BS4 logic correctly parses bold strings (SRC-02)."""
    mock_search_response = MagicMock()
    mock_search_response.status_code = 200
    mock_search_response.text = "<article><a href='http://mock_profile'>Profile</a></article>"
    
    mock_profile_response = MagicMock()
    mock_profile_response.status_code = 200
    mock_profile_response.text = "<p><strong>Bias Rating: RIGHT CENTER</strong>\n<strong>Factual Reporting: HIGH</strong>\n</p>"
    
    # Sequence the get responses: First is search return, second is profile return
    mock_get.side_effect = [mock_search_response, mock_profile_response]
    
    tracker = SourceIntelligenceTracker()
    res = tracker._scrape_mbfc("dummy.com")
    
    assert res["source"] == "MediaBiasFactCheck"
    assert res["bias"] == "RIGHT CENTER"
    assert res["reliability"] == "HIGH"

@patch("scraper_layer.requests.get")
def test_allsides_scrape_success(mock_get):
    """Ensure AllSides BS4 logic correctly parses image alt attributes (SRC-01)."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = "<table><tr><th>Title</th></tr><tr><td>1</td><td>2</td><td><img alt='Left Bias'></td></tr></table>"
    mock_get.return_value = mock_response
    
    tracker = SourceIntelligenceTracker()
    res = tracker._scrape_allsides("dummy.com")
    
    assert res["source"] == "AllSides"
    assert res["bias"] == "Left Bias"

@patch("scraper_layer.GeminiInferenceServer")
def test_gemini_fallback(MockServer):
    """Ensure Gemini logic constructs Low Confidence Summary (SRC-03)."""
    mock_instance = MockServer.return_value
    mock_instance.client = MagicMock()
    mock_model_response = MagicMock()
    mock_model_response.text = "This is a dummy reputation."
    mock_instance.client.models.generate_content.return_value = mock_model_response
    
    tracker = SourceIntelligenceTracker()
    tracker.llm_fallback = mock_instance # inject mock
    
    res = tracker._get_gemini_fallback("dummy.com")
    assert res["source"] == "Gemini Fallback (Inferred)"
    assert res["confidence"] == "Low"
    assert res["summary"] == "This is a dummy reputation."

@patch("scraper_layer.SourceIntelligenceTracker._scrape_mbfc")
@patch("scraper_layer.SourceIntelligenceTracker._scrape_allsides")
def test_memory_caching(mock_allsides, mock_mbfc):
    """Verify that multiple network queries to the same domain flag it as cached natively."""
    mock_mbfc.return_value = {"bias": "test_bias"}
    mock_allsides.return_value = {}
    
    tracker = SourceIntelligenceTracker()
    url = "https://www.test_cache_domain.com/abc"
    
    # First hit should return _cache_hit: False
    res1 = tracker.get_domain_info(url)
    assert res1["_cache_hit"] is False
    assert mock_mbfc.call_count == 1
    
    # Second hit should load from dict memory, checking _cache_hit: True and No explicit function calls.
    res2 = tracker.get_domain_info(url)
    assert res2["_cache_hit"] is True
    assert mock_mbfc.call_count == 1 # Has not incremented!

import pytest
from app import app
import json

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_analyze_route_no_payload(client):
    """Test API-01: Correctly handles empty POST requests."""
    response = client.post('/api/analyze', json={})
    assert response.status_code == 400
    assert b"No input supplied" in response.data

def test_analyze_route_mocked_pipeline(client, mocker):
    """Test API-02: Successfully routes mock strings into pipeline.py logic."""
    # Mock execute_pipeline to prevent DistilBERT/Gemini init during unit test.
    # Return value must include all 3 keys app.py reads (lines 53-55):
    #   nlp_analysis, media_bias, source_intelligence
    mocker.patch('app.execute_pipeline', return_value={
        "nlp_analysis": {"composite_verdict": {"final_label": "REAL", "final_confidence": 0.9}},
        "media_bias": {"bias_score": 0.1, "label": "Center"},
        "source_intelligence": {"domain": "raw_text", "reputation": "unknown"},
    })

    # Mock fetch_text so it doesn't try to resolve a URL
    mocker.patch('app.fetch_text', return_value={
        "type": "text", "text": "Testing text inputs", "url": "raw_text", "title": "",
    })

    response = client.post('/api/analyze', json={"text": "Testing text inputs"})

    assert response.status_code == 200
    data = response.get_json()
    # app.py returns flat keys: nlp_analysis, media_bias, source_intelligence, input_source, input_title
    assert "nlp_analysis" in data
    assert "media_bias" in data
    assert "source_intelligence" in data
    assert data["input_source"] == "raw_text"

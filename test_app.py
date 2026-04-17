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
    assert b"No threat payload supplied" in response.data

def test_analyze_route_mocked_pipeline(client, mocker):
    """Test API-02: Successfully routes mock strings into pipeline.py logic."""
    # Mock the execute_pipeline to prevent 5 second DistilBERT loading during unit test
    mocker.patch('app.execute_pipeline', return_value={"nlp_analysis": {"status": "SUCCESS"}})
    
    # Mock fetch_text so it doesn't try to resolve a URL
    mocker.patch('app.fetch_text', return_value={"type": "text", "text": "Testing text inputs", "url": "raw_text"})
    
    response = client.post('/api/analyze', json={"text": "Testing text inputs"})
    
    assert response.status_code == 200
    data = response.get_json()
    assert "layers" in data
    assert data["layers"]["nlp_analysis"]["status"] == "SUCCESS"
    assert data["input_text"] == "Testing text inputs"

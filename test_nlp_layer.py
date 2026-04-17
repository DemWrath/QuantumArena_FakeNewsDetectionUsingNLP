import pytest
from unittest.mock import patch, MagicMock
from nlp_layer import DistilBertAnalyzer, GeminiInferenceServer

@pytest.fixture
def mock_transformers_pipeline():
    with patch("nlp_layer.pipeline") as mock_pipe:
        # Mock the pipeline return structure: list of dicts
        mock_instance = MagicMock()
        mock_instance.return_value = [{"label": "LABEL_1", "score": 0.99}]
        mock_pipe.return_value = mock_instance
        yield mock_pipe

@pytest.fixture
def mock_genai_client():
    with patch("nlp_layer.genai.Client") as mock_client:
        mock_instance = MagicMock()
        mock_client.return_value = mock_instance
        yield mock_client

def test_distilbert_success(mock_transformers_pipeline):
    """Test that DistilBertAnalyzer constructs data correctly on success."""
    bert = DistilBertAnalyzer(model_identifier="dummy/model")
    result = bert.analyze("This is a statement to analyze.")
    
    # NLP-01 Verification
    assert result["model_used"] == "dummy/model"
    assert result["label"] == "LABEL_1"
    assert result["confidence_score"] == 0.99
    assert result["is_likely_reliable"] == True

def test_distilbert_empty_text():
    """Test analyzer handles empty text safely."""
    with patch("nlp_layer.TRANSFORMERS_AVAILABLE", True), patch("nlp_layer.pipeline"):
        bert = DistilBertAnalyzer()
        result = bert.analyze("")
        assert "error" in result

@patch("nlp_layer.os.getenv")
def test_gemini_clickbait_eval(mock_getenv, mock_genai_client):
    """Test that the structured boolean clickbait evaluator works."""
    mock_getenv.return_value = "fake_key"
    
    # Mock return value to parse as 'true'
    mock_response = MagicMock()
    mock_response.text = "True."
    mock_genai_client.return_value.models.generate_content.return_value = mock_response

    server = GeminiInferenceServer()
    result = server.check_clickbait(headline="Wow", body_text="Okay")
    
    # NLP-03 Verification
    assert result["headline_promise_fulfilled"] == True
    assert result["is_clickbait"] == False

@patch("nlp_layer.os.getenv")
def test_gemini_emotion_eval(mock_getenv, mock_genai_client):
    """Test that structured JSON emotion checking maps properly."""
    mock_getenv.return_value = "fake_key"
    
    mock_response = MagicMock()
    # Mocking standard SDK JSON string output
    mock_response.text = '{"fear": 0.8, "outrage": 0.5, "sensationalism": 0.9}'
    mock_genai_client.return_value.models.generate_content.return_value = mock_response

    server = GeminiInferenceServer()
    result = server.score_emotion("Crazy terrible things.")
    
    # NLP-02 Verification
    assert result["fear"] == 0.8
    assert result["sensationalism"] == 0.9

@patch("nlp_layer.os.getenv")
def test_gemini_missing_api_key(mock_getenv):
    """Ensure missing API keys fail safe on Gemini without crashing."""
    mock_getenv.return_value = None
    server = GeminiInferenceServer()
    
    res1 = server.check_clickbait("headline", "body")
    assert "error" in res1
    assert "Gemini client not initialized" in res1["error"]
    
    res2 = server.score_emotion("body")
    assert "error" in res2
    assert "Gemini client not initialized" in res2["error"]

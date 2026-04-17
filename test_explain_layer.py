import pytest
from explain_layer import ExplainLayer

class MockAnalyzer:
    """Mocks the DistilBertAnalyzer Huggingface structure identically without loading neural models dynamically."""
    def __init__(self, label="FAKE", score=0.95):
        self.label = label
        self.score = score
        
    def classifier(self, texts):
        # Return a list of predictions for each sentence permutation requested by Lime
        results = []
        for _ in texts:
            results.append({"label": self.label, "score": self.score})
        return results

def test_explain_layer_success():
    """Test EXPL-01 & EXPL-02: Predictor successfully interprets labels and runs permutations accurately."""
    explainer = ExplainLayer()
    mock_analyzer = MockAnalyzer(label="FAKE", score=0.98)
    
    # Run the explanation sequence
    result = explainer.generate_explanation("The aliens are secretly running the global shadow government.", mock_analyzer)
    
    assert "error" not in result
    assert result.get("limes_processed") is True
    assert "triggers" in result
    assert len(result["triggers"]) > 0
    
    # Test valid struct
    first_trigger = result["triggers"][0]
    assert "word" in first_trigger
    assert "weight" in first_trigger
    assert "impact_type" in first_trigger

def test_explain_layer_invalid_input():
    """Test handling of empty strings."""
    explainer = ExplainLayer()
    mock_analyzer = MockAnalyzer()
    
    result = explainer.generate_explanation("", mock_analyzer)
    assert "error" in result
    assert "text provided" in result["error"].lower()

def test_explain_layer_missing_analyzer():
    """Test handling of missing classifier nodes."""
    explainer = ExplainLayer()
    
    class BrokenAnalyzer:
        pass # missing classifier function
        
    broken_analyzer = BrokenAnalyzer()
    
    result = explainer.generate_explanation("Valid Text.", broken_analyzer)
    assert "error" in result
    assert "not provided or not initialized" in result["error"].lower()

import os
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables (like GEMINI_API_KEY)
load_dotenv()

# We only import transformers when needed or globally if required.
try:
    from transformers import pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

try:
    from google import genai
    from google.genai import types
    from pydantic import BaseModel, Field
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

class EmotionScores(BaseModel):
    fear: float = Field(description="Confidence score for fear mongering from 0.0 to 1.0")
    outrage: float = Field(description="Confidence score for outrage incitement from 0.0 to 1.0")
    sensationalism: float = Field(description="Confidence score for sensationalism from 0.0 to 1.0")

class DistilBertAnalyzer:
    """Uses a locally loaded DistilBERT model to classify text."""
    
    def __init__(self, model_identifier: str = "mrm8488/bert-tiny-finetuned-fake-news-detection"):
        self.model_identifier = model_identifier
        self.classifier = None
        
        if TRANSFORMERS_AVAILABLE:
            print(f"[DistilBertAnalyzer] Loading model '{self.model_identifier}' into memory. This may take a moment on first run...")
            try:
                import torch
                # If CUDA is available (RTX 3050), use device 0, else default backward to -1 (CPU)
                device_id = 0 if torch.cuda.is_available() else -1
                
                # Load the pipeline for text classification
                # We use truncation=True since news articles can be long
                self.classifier = pipeline("text-classification", model=self.model_identifier, truncation=True, max_length=512, device=device_id)
                print(f"[DistilBertAnalyzer] Model loaded successfully on device: {'GPU (CUDA)' if device_id == 0 else 'CPU'}")
            except Exception as e:
                print(f"[DistilBertAnalyzer] Error loading model: {e}")
        else:
            print("[DistilBertAnalyzer] 'transformers' library not found. Classification disabled.")

    def analyze(self, text: str) -> Dict[str, Any]:
        if not self.classifier:
            return {"error": "Classifier not initialized or transformers not installed."}
        
        if not text or not text.strip():
            return {"error": "Empty text provided."}

        try:
            # The classifier returns a list like: [{'label': 'FAKE', 'score': 0.99}]
            result = self.classifier(text)[0]
            # Normalize labels to be friendly
            label = result.get("label", "UNKNOWN").upper()
            score = result.get("score", 0.0)
            
            # Map standard model outputs to our schema
            is_reliable = label == "REAL" or label == "TRUE" or label == "RELIABLE" or label == "LABEL_1"
            
            return {
                "model_used": self.model_identifier,
                "label": label,
                "confidence_score": round(score, 4),
                "is_likely_reliable": is_reliable
            }
        except Exception as e:
            return {"error": f"Prediction failed: {e}"}

class GeminiInferenceServer:
    """Uses the Google GenAI SDK to perform runtime logical checks."""
    
    def __init__(self, model_name: str = "gemini-2.5-flash"):
        self.model_name = model_name
        self.client = None
        
        if GENAI_AVAILABLE:
            api_key = os.getenv("GEMINI_API_KEY")
            if api_key:
                try:
                    self.client = genai.Client(api_key=api_key)
                except Exception as e:
                    print(f"[GeminiInferenceServer] Error initializing client: {e}")
            else:
                print("[GeminiInferenceServer] WARNING: GEMINI_API_KEY not found in environment. Gemini features will be disabled.")
        else:
            print("[GeminiInferenceServer] 'google-genai' library not found. LLM inference disabled.")

    def check_clickbait(self, headline: str, body_text: str) -> Dict[str, Any]:
        """Checks if the body text fulfills the semantic promise of the headline."""
        if not self.client:
            return {"error": "Gemini client not initialized (missing API key or SDK)."}
            
        if not headline or headline.strip() == "":
            return {"error": "No headline provided to check."}
            
        prompt = f"""
        You are an expert journalism analyzer. Please review the following headline and the corresponding article body.
        Your task is to determine: "Does the body fulfill the semantic promise of the headline, or is it clickbait?"
        
        Headline: "{headline}"
        
        Body snippet:
        "{body_text[:1500]}"
        
        Output 'True' if the body fulfills the headline's promise, and 'False' if it is deceptive/clickbait.
        Provide only the boolean word (True/False).
        """
        
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.0
                )
            )
            result_text = response.text.strip().lower()
            is_fulfilled = "true" in result_text
            
            return {
                "headline_promise_fulfilled": is_fulfilled,
                "is_clickbait": not is_fulfilled
            }
        except Exception as e:
            return {"error": str(e)}

    def score_emotion(self, text: str) -> Dict[str, Any]:
        """Returns structured JSON confidence scores for emotion vectors."""
        if not self.client:
            return {"error": "Gemini client not initialized (missing API key or SDK)."}
            
        prompt = f"""
        Analyze the following text for manipulative emotional tone.
        Assign a confidence score between 0.0 and 1.0 for the presence of fear-mongering, outrage incitement, and sensationalism.
        
        Text:
        "{text[:1500]}"
        """
        
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=EmotionScores,
                    temperature=0.0
                )
            )
            
            # The SDK automatically handles the JSON string payload if response schema is provided,
            # but response.text is a JSON string. We parse it:
            import json
            scores = json.loads(response.text)
            return scores
        except Exception as e:
            return {"error": str(e)}

def run_nlp_layers(text: str, headline: str = None) -> Dict[str, Any]:
    """Orchestrates both DistilBERT and Gemini analysis."""
    output = {}
    
    # 1. DistilBERT Analysis
    bert = DistilBertAnalyzer()
    output["style_classification"] = bert.analyze(text)
    
    # 2. Gemini Inference
    llm = GeminiInferenceServer()
    
    if headline:
        output["clickbait_check"] = llm.check_clickbait(headline, body_text=text)
    else:
        output["clickbait_check"] = {"error": "No headline provided to evaluating clickbait."}
        
    output["emotional_tone"] = llm.score_emotion(text)
    
    return output

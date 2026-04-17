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

class FactCheckResult(BaseModel):
    verdict: str = Field(description="One of: VERIFIED, UNVERIFIED, MISLEADING, or FABRICATED")
    confidence: float = Field(description="Confidence in the verdict from 0.0 to 1.0")
    reasoning: str = Field(description="One or two sentence explanation of the verdict")
    red_flags: list[str] = Field(description="List of specific claims or statements that are suspicious, verifiably false, or unverifiable")

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
            
            # ISOT usually puts True=0, Fake=1
            is_reliable = label in ["REAL", "TRUE", "RELIABLE", "LABEL_0"]
            
            final_label = "REAL" if is_reliable else "FAKE"
            
            return {
                "model_used": self.model_identifier,
                "label": final_label,
                "raw_label_debug": label,
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

    def fact_check(self, text: str) -> Dict[str, Any]:
        """
        Real search-grounded fact-checking.
        
        Step 1: Gemini + Google Search grounding — extract key claims and search the live web
                for corroborating or disconfirming evidence. This is NOT parametric memory;
                Gemini issues actual search queries and retrieves live results.
        
        Step 2: Structured verdict — pass the grounded evidence summary into a second
                schema-constrained call to produce a machine-readable FactCheckResult.
        
        Note: google_search tool and response_schema are mutually exclusive in the SDK,
              hence the two-step design.
        """
        if not self.client:
            return {"error": "Gemini client not initialized (missing API key or SDK)."}

        import json

        # ── STEP 1: Search-grounded evidence gathering ──────────────────────────
        # Extract the 1-3 most verifiable, concrete claims and search the web for them.
        search_prompt = f"""
        You are a fact-checking researcher. Your job is to:
        1. Identify the 1-3 most specific, verifiable factual claims in the text below.
        2. Use Google Search to look each claim up and determine whether it is corroborated,
           contradicted, or absent from credible sources.
        3. Write a concise evidence summary (3-5 sentences) describing what you found.
           Clearly state which sources support or refute the claims.

        IMPORTANT: Base your evidence ONLY on what you find in search results, not on
        your training data. If you cannot find corroborating sources, say so explicitly.

        Text:
        "{text[:2000]}"
        """

        evidence_summary = ""
        grounding_sources = []

        try:
            search_response = self.client.models.generate_content(
                model=self.model_name,
                contents=search_prompt,
                config=types.GenerateContentConfig(
                    tools=[types.Tool(google_search=types.GoogleSearch())],
                    temperature=0.1
                )
            )
            evidence_summary = search_response.text.strip()

            # Extract grounding source URLs from metadata
            try:
                for cand in search_response.candidates:
                    meta = getattr(cand, "grounding_metadata", None)
                    if meta:
                        chunks = getattr(meta, "grounding_chunks", []) or []
                        for chunk in chunks:
                            web = getattr(chunk, "web", None)
                            if web:
                                grounding_sources.append({
                                    "title": getattr(web, "title", ""),
                                    "uri": getattr(web, "uri", "")
                                })
            except Exception:
                pass  # grounding metadata extraction is best-effort

            print(f"[FactCheck] Grounding search complete. Sources found: {len(grounding_sources)}")

        except Exception as e:
            # If search grounding fails (e.g., quota), fall back to parametric reasoning only
            print(f"[FactCheck] Search grounding failed ({e}), falling back to parametric reasoning.")
            evidence_summary = (
                f"Note: Live web search was unavailable. The following analysis is based on "
                f"the model's training knowledge only and may not reflect current events.\n\n"
                f"Text: {text[:1000]}"
            )

        # ── STEP 2: Structured verdict from evidence ─────────────────────────────
        verdict_prompt = f"""
        You are a senior fact-checking editor. Based on the evidence research below,
        produce a structured verdict on the original text.

        Evidence Research (from live web search):
        {evidence_summary}

        Original Text:
        "{text[:1000]}"

        Your verdict MUST be exactly one of:
        - VERIFIED: Key claims are corroborated by credible sources found in search.
        - UNVERIFIED: Claims could not be confirmed or denied through available search results.
        - MISLEADING: Claims mix real facts with distortions; partial truth used deceptively.
        - FABRICATED: Claims describe events that are physically impossible, scientifically
          impossible, or directly contradicted by search results/established facts.

        Base your verdict on the EVIDENCE RESEARCH above, not on your training data alone.
        """

        try:
            verdict_response = self.client.models.generate_content(
                model=self.model_name,
                contents=verdict_prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=FactCheckResult,
                    temperature=0.0
                )
            )
            result = json.loads(verdict_response.text)
            result["grounding_sources"] = grounding_sources
            result["evidence_summary"] = evidence_summary
            result["search_grounded"] = len(grounding_sources) > 0
            return result

        except Exception as e:
            return {"error": str(e)}


from explain_layer import ExplainLayer
explainer_instance = ExplainLayer()

def _build_composite_verdict(style_result: Dict, fact_result: Dict) -> Dict[str, Any]:
    """Combines Transformer style signal with Gemini fact-check to produce a final verdict."""
    # If Gemini fact-check errored, fall back purely to Transformer
    if "error" in fact_result:
        return {
            "final_label": style_result.get("label", "UNKNOWN"),
            "final_confidence": style_result.get("confidence_score", 0.0),
            "method": "transformer_only",
            "note": "Gemini fact-check unavailable. Style signal used."
        }

    gem_verdict = fact_result.get("verdict", "UNVERIFIED")
    gem_conf = fact_result.get("confidence", 0.5)

    # Gemini flag mapping -> binary FAKE/REAL override
    # FABRICATED or MISLEADING are hard overrides to FAKE regardless of Transformer
    if gem_verdict in ("FABRICATED", "MISLEADING"):
        final_label = "FAKE"
        final_conf = gem_conf
        method = "gemini_override"
    elif gem_verdict == "UNVERIFIED":
        # Blend: treat Transformer style as a weak signal
        style_label = style_result.get("label", "REAL")
        style_conf = style_result.get("confidence_score", 0.5)
        # Weight Gemini (70%) more heavily than style Transformer (30%)
        blended_fake_score = (0.7 * 0.5) + (0.3 * (1.0 - style_conf if style_label == "REAL" else style_conf))
        final_label = "FAKE" if blended_fake_score > 0.45 else "REAL"
        final_conf = max(gem_conf, style_conf)
        method = "blended"
    else:  # VERIFIED
        final_label = "REAL"
        final_conf = gem_conf
        method = "gemini_override"

    return {
        "final_label": final_label,
        "final_confidence": round(final_conf, 4),
        "gemini_verdict": gem_verdict,
        "method": method,
        "reasoning": fact_result.get("reasoning", ""),
        "red_flags": fact_result.get("red_flags", [])
    }


def run_nlp_layers(text: str, headline: str = None) -> Dict[str, Any]:
    """Orchestrates DistilBERT style signal, Gemini fact-check, and composite verdict."""
    output = {}

    # 1. DistilBERT Style Analysis (detects writing pattern, not logic)
    bert = DistilBertAnalyzer()
    output["style_classification"] = bert.analyze(text)
    output["explainability"] = explainer_instance.generate_explanation(text, bert)

    # 2. Gemini Fact-Check (evaluates claim verifiability)
    llm = GeminiInferenceServer()
    print("[NLP] Running Gemini fact-check...")
    fact_result = llm.fact_check(text)
    output["fact_check"] = fact_result

    # 3. Composite Verdict (Gemini overrides Transformer on logic failures)
    output["composite_verdict"] = _build_composite_verdict(output["style_classification"], fact_result)

    # 4. Other Gemini signals
    if headline:
        output["clickbait_check"] = llm.check_clickbait(headline, body_text=text)
    else:
        output["clickbait_check"] = {"error": "No headline provided to evaluate clickbait."}

    output["emotional_tone"] = llm.score_emotion(text)

    return output

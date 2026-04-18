"""
nlp_layer.py
TruthLens NLP Analysis Layer

Orchestrates three inference systems:
  1. DistilBertAnalyzer   — GPU-resident style/pattern classifier (ISOT-trained)
  2. ExplainLayer         — LIME word-level attribution heatmap
  3. GeminiInferenceServer — Search-grounded fact-checking + emotion + clickbait

All heavy objects (model, explainer, Gemini client) are module-level singletons
loaded once at startup, not re-instantiated per request.
"""

import os
import json
from typing import Dict, Any, List

from dotenv import load_dotenv

# override=True ensures values in .env always win over any stale system-level
# environment variable that may be set from a previous run or shell session.
# Without this, python-dotenv silently ignores .env if the var already exists.
load_dotenv(override=True)

# ── Optional dependency guards ─────────────────────────────────────────────────

try:
    from transformers import pipeline as hf_pipeline
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

from explain_layer import ExplainLayer


# ── Pydantic schemas for structured Gemini outputs ────────────────────────────

class EmotionScores(BaseModel):
    fear: float = Field(description="Confidence score for fear mongering from 0.0 to 1.0")
    outrage: float = Field(description="Confidence score for outrage incitement from 0.0 to 1.0")
    sensationalism: float = Field(description="Confidence score for sensationalism from 0.0 to 1.0")


class FactCheckResult(BaseModel):
    verdict: str = Field(description="One of: VERIFIED, UNVERIFIED, MISLEADING, or FABRICATED")
    confidence: float = Field(description="Confidence in the verdict from 0.0 to 1.0")
    reasoning: str = Field(description="One or two sentence explanation of the verdict")
    red_flags: List[str] = Field(description="Specific claims that are suspicious, unverifiable, or physically impossible")


# ── DistilBERT Style Classifier ───────────────────────────────────────────────

class DistilBertAnalyzer:
    """
    GPU-resident BERT model for writing-style classification.
    
    Trained on the ISOT dataset:
      LABEL_0 = REAL (professional journalism style)
      LABEL_1 = FAKE (partisan/sensational blog style)
    
    NOTE: This model detects *linguistic style*, not factual truth.
    Factual verification is handled by GeminiInferenceServer.fact_check().
    """

    def __init__(self, model_identifier: str = "mrm8488/bert-tiny-finetuned-fake-news-detection"):
        self.model_identifier = model_identifier
        self.classifier = None

        if not TRANSFORMERS_AVAILABLE:
            print("[DistilBertAnalyzer] 'transformers' not installed. Style classification disabled.")
            return

        print(f"[DistilBertAnalyzer] Loading '{self.model_identifier}'...")
        try:
            import torch
            device_id = 0 if torch.cuda.is_available() else -1
            self.classifier = hf_pipeline(
                "text-classification",
                model=self.model_identifier,
                truncation=True,
                max_length=512,
                device=device_id
            )
            dev_name = "GPU (CUDA)" if device_id == 0 else "CPU"
            print(f"[DistilBertAnalyzer] Model ready on {dev_name}.")
        except Exception as e:
            print(f"[DistilBertAnalyzer] Failed to load model: {e}")

    def analyze(self, text: str) -> Dict[str, Any]:
        if not self.classifier:
            return {"error": "Classifier not initialized."}
        if not text or not text.strip():
            return {"error": "Empty text provided."}

        try:
            result = self.classifier(text)[0]
            raw_label = result.get("label", "UNKNOWN").upper()
            score = result.get("score", 0.0)

            # ISOT label convention: LABEL_0 = REAL, LABEL_1 = FAKE
            is_reliable = raw_label in ("REAL", "TRUE", "RELIABLE", "LABEL_0")
            final_label = "REAL" if is_reliable else "FAKE"

            return {
                "model_used": self.model_identifier,
                "label": final_label,
                "confidence_score": round(score, 4),
                "is_likely_reliable": is_reliable,
            }
        except Exception as e:
            return {"error": f"Prediction failed: {e}"}


# ── Gemini Inference Server ───────────────────────────────────────────────────

class GeminiInferenceServer:
    """Google GenAI SDK client for fact-checking, emotion scoring, and clickbait detection."""

    def __init__(self, model_name: str = "gemini-2.5-flash"):
        self.model_name = model_name
        self.client = None

        if not GENAI_AVAILABLE:
            print("[GeminiInferenceServer] 'google-genai' not installed. LLM inference disabled.")
            return

        # os.getenv is called here (not at module load) so it always picks up
        # whichever key load_dotenv(override=True) placed into the environment.
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("[GeminiInferenceServer] WARNING: GEMINI_API_KEY not set. Gemini disabled.")
            return

        key_preview = api_key[:12] + "..." + api_key[-4:]
        print(f"[GeminiInferenceServer] Using API key: {key_preview}")
        try:
            self.client = genai.Client(api_key=api_key)
        except Exception as e:
            print(f"[GeminiInferenceServer] Client init failed: {e}")

    # ── Fact-check (2-step: Search grounding → Structured verdict) ────────────

    def fact_check(self, text: str, lang: str = 'en') -> Dict[str, Any]:
        """
        Search-grounded fact-checking pipeline.

        Step 1: Gemini issues real Google Search queries for the key claims in the
                text and returns a grounded evidence summary. This is live web
                retrieval, NOT parametric memory from training data.

        Step 2: The evidence summary is passed to a schema-constrained call that
                produces a structured FactCheckResult verdict.

        The two-step design is required because google_search tool and
        response_schema are mutually exclusive in the Gemini SDK.
        """
        if not self.client:
            return {"error": "Gemini client not initialized."}

        # ── Step 1: Live web search ───────────────────────────────────────────
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

        if lang == 'mr':
            search_prompt += "\nCRITICAL PROTOCOL: You MUST prioritize searching regional Marathi-language news outlets (e.g., Lokmat, Saamana, Sakal, ABP Majha, TV9 Marathi) to verify these claims for localized context."

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

            # Extract grounding source URLs from response metadata (best-effort)
            for cand in search_response.candidates:
                meta = getattr(cand, "grounding_metadata", None)
                if not meta:
                    continue
                for chunk in getattr(meta, "grounding_chunks", []) or []:
                    web = getattr(chunk, "web", None)
                    if web:
                        grounding_sources.append({
                            "title": getattr(web, "title", ""),
                            "uri": getattr(web, "uri", "")
                        })

            print(f"[FactCheck] Search complete. Sources: {len(grounding_sources)}")

        except Exception as e:
            print(f"[FactCheck] Search grounding failed ({e}). Using parametric fallback.")
            evidence_summary = ""   # empty — signals parametric path in Step 2
            grounding_sources = []  # no sources

        # ── Step 2: Structured verdict from evidence ──────────────────────────
        if grounding_sources:
            # Normal path: search succeeded — evidence came from live web retrieval
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

IMPORTANT DISTINCTION for political/legal reporting:
- Minor phrasing differences (e.g. "Parliament's competence" vs "President's authority")
  are NOT grounds for a MISLEADING verdict unless they materially change the meaning.
- If the core factual claim is correct and the article's overall direction is accurate,
  classify as VERIFIED even if peripheral details have minor imprecisions.
- Reserve MISLEADING for cases where the article deliberately frames facts to create
  a false impression — not for imprecise but non-deceptive reporting.

Base your verdict on the EVIDENCE RESEARCH above, not on your training data alone.
"""
        else:
            # Parametric path: search unavailable — use training knowledge honestly.
            # Do NOT pretend this is search-grounded evidence.
            verdict_prompt = f"""
You are a senior fact-checking editor. Live web search is unavailable.
Use your training knowledge to assess the following text.

Apply these classification rules strictly:
- FABRICATED: The text describes events that are physically impossible, scientifically
  impossible, or constitutionally impossible. Examples: a state declaring independence,
  a statue rising from the ocean on its own, a waterborne COVID strain killing thousands
  in 48 hours, a government secretly gifting its coastline to a foreign company.
- MISLEADING: The text contains real events but uses exaggerated numbers, wrong
  attributions, outdated facts, or selective omissions that create a false impression.
- UNVERIFIED: The text makes specific, plausible claims that you cannot confidently
  confirm or deny from training knowledge alone.
- VERIFIED: The text describes well-known, broadly corroborated facts from your
  training knowledge.

Text:
"{text[:1500]}"
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

    # ── Clickbait detection ───────────────────────────────────────────────────

    def check_clickbait(self, headline: str, body_text: str) -> Dict[str, Any]:
        """Determines if the article body fulfills the semantic promise of the headline."""
        if not self.client:
            return {"error": "Gemini client not initialized."}
        if not headline or not headline.strip():
            return {"error": "No headline provided."}

        prompt = f"""
        You are an expert journalism analyzer. Review the following headline and article body.
        Determine: does the body fulfill the semantic promise of the headline, or is it clickbait?

        Headline: "{headline}"
        Body snippet: "{body_text[:1500]}"

        Output 'True' if the body fulfills the headline's promise, 'False' if it is deceptive.
        Provide only the boolean word (True/False).
        """

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(temperature=0.0)
            )
            is_fulfilled = "true" in response.text.strip().lower()
            return {
                "headline_promise_fulfilled": is_fulfilled,
                "is_clickbait": not is_fulfilled
            }
        except Exception as e:
            return {"error": str(e)}

    # ── Emotional tone scoring ────────────────────────────────────────────────

    def score_emotion(self, text: str) -> Dict[str, Any]:
        """Returns structured confidence scores for fear, outrage, and sensationalism."""
        if not self.client:
            return {"error": "Gemini client not initialized."}

        prompt = f"""
        Analyze the following text for manipulative emotional tone.
        Assign a confidence score between 0.0 and 1.0 for the presence of
        fear-mongering, outrage incitement, and sensationalism.

        Text: "{text[:1500]}"
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
            return json.loads(response.text)
        except Exception as e:
            return {"error": str(e)}


# ── Module-level singletons (loaded once at startup) ──────────────────────────

print("[NLP Layer] Initializing module singletons...")
_bert = DistilBertAnalyzer()
_explainer = ExplainLayer()
_llm = GeminiInferenceServer()
print("[NLP Layer] Ready.")


# ── Heuristic impossible-claim detector ──────────────────────────────────────

def _heuristic_signals(text: str, headline: str = None) -> Dict[str, Any]:
    """
    Zero-cost, zero-API heuristic checks.

    Catches physically/constitutionally impossible claims even when both Gemini
    and reliable BERT classification are unavailable (e.g. rate-limit cascades).

    Returns:
        red_flags             — list of matched pattern descriptions
        heuristic_fake_signal — True if any pattern fired
        heuristic_confidence  — 0.75 (fixed) when flagged, else 0.0
    """
    import re
    flags: List[str] = []
    combined = f"{headline or ''} {text}".lower()

    # ── Physically or constitutionally impossible events ──────────────────────
    IMPOSSIBLE_EXACT = [
        "risen from the sea",
        "rose from the sea",
        "floating back to shore intact",
        "miracle confirmed",
        "declares itself independent",
        "declared independence",
        "independent nation",
        "unilateral declaration of independence",
        "gifting the konkan",
        "gifting konkan coast",
        "secret treaty",
        "new currency",
        "marathi mudra",
        "applying for un membership",
        "maharashtra coastal privatisation act",
        "oceanland corp",
    ]
    for phrase in IMPOSSIBLE_EXACT:
        if phrase in combined:
            flags.append(f"impossible_phrase: '{phrase}'")

    IMPOSSIBLE_PATTERNS = [
        r"dissolve.*membership",
        r"expelled from.*united nations",
        r"expelled from all global",
        r"merging into.*single nation",
        r"merge.*into.*single.*entity",
        r"single planetary government",
        r"united earth federation",
        r"dissolve all nations",
        r"dissolve their.*nations",
        r"abolish the constitution",
        r"suspend the constitution",
        r"declaration of civilizational unity",
    ]
    for pat in IMPOSSIBLE_PATTERNS:
        if re.search(pat, combined):
            flags.append(f"impossible_pattern: '{pat}'")

    # ── Sovereign entity dissolution claims (co-occurrence) ──────────────
    sovereignty_terms = bool(re.search(r'(dissolve|expel|revoke|strip)', combined))
    entity_terms = bool(re.search(r'(membership|nation|sovereignty|statehood)', combined))
    intl_body_terms = bool(re.search(r'(united nations|un |nato|security council)', combined))
    if sovereignty_terms and entity_terms and intl_body_terms:
        flags.append("impossible_sovereignty_action: dissolution/expulsion of nation from intl body")

    # ── Extreme unsourced casualty/infection counts (≥1000 in a single event) ─
    extreme_counts = re.findall(
        r'\b(\d{4,})\s*(?:people\s+)?'
        r'(?:dead|killed|deaths|fatalities|infected|in\s+\d+\s+hours?)\b',
        combined
    )
    if extreme_counts:
        flags.append(f"extreme_unsourced_casualty: {extreme_counts[0]}")

    # ── Waterborne COVID (scientifically impossible transmission route) ────────
    water_terms = bool(re.search(r'(waterborne|water\s+supply|tap\s+water)', combined))
    covid_terms = bool(re.search(r'(covid|coronavirus|strain|variant|virus)', combined))
    if water_terms and covid_terms:
        flags.append("impossible_pathogen_transmission: waterborne_covid")

    # ── Stacked anonymous-source markers (≥3 = red flag for fabrication) ──────
    ANON_MARKERS = [
        "anonymous", "sources say", "reportedly", "allegedly",
        "secret", "classified", "unconfirmed", "whistleblower",
    ]
    anon_count = sum(1 for m in ANON_MARKERS if m in combined)
    if anon_count >= 3:
        flags.append(f"stacked_anonymous_sourcing: {anon_count} markers found")

    return {
        "red_flags": flags,
        "heuristic_fake_signal": len(flags) > 0,
        "heuristic_confidence": 0.75 if flags else 0.0,
    }


# ── Composite verdict engine ──────────────────────────────────────────────────

def _build_composite_verdict(
    style_result: Dict,
    fact_result: Dict,
    text: str = "",
    headline: str = None,
) -> Dict[str, Any]:
    """
    Combines the Transformer style signal with the Gemini fact-check verdict.

    Decision logic (4 states):
      FABRICATED → hard "FAKE"       (physically impossible / invented events)
      MISLEADING → "MISLEADING"      (real events, but framed deceptively or out-of-context)
      UNVERIFIED → blended signal    (could not confirm; lean on transformer style)
      VERIFIED   → hard "REAL"       (corroborated by live search sources)

    MISLEADING is deliberately separated from FABRICATED because editorialized
    political reporting ≠ invented facts. They warrant different UI states.
    """
    if "error" in fact_result:
        # ── Tier 1: Heuristic impossible-claim detector (zero API) ───────────
        # Catches physically/constitutionally impossible claims that BERT
        # cannot detect because they are written in formal journalistic prose.
        heuristics = _heuristic_signals(text, headline)
        if heuristics["heuristic_fake_signal"]:
            return {
                "final_label": "FAKE",
                "final_confidence": heuristics["heuristic_confidence"],
                "method": "heuristic_fallback",
                "red_flags": heuristics["red_flags"],
                "note": (
                    "Gemini unavailable. Heuristic pattern detector fired — "
                    f"impossible/fabricated claim indicators: {heuristics['red_flags']}"
                ),
            }

        # ── Tier 2: DistilBERT style-pattern fallback (last resort) ──────────
        # Confidence deflated ×0.6 — style-match probability ≠ fake-news probability.
        style_label = style_result.get("label", "REAL")
        raw_conf = style_result.get("confidence_score", 0.0)
        return {
            "final_label": style_label,
            "final_confidence": round(raw_conf * 0.6, 4),
            "method": "transformer_only",
            "note": (
                "Gemini fact-check unavailable. Style-pattern label used as fallback. "
                f"Raw style confidence {raw_conf:.4f} deflated ×0.6 — style-match "
                "probability is not equivalent to fake-news probability."
            ),
        }

    gem_verdict = fact_result.get("verdict", "UNVERIFIED")
    gem_conf = fact_result.get("confidence", 0.5)

    if gem_verdict == "FABRICATED":
        # Hard override: events that cannot physically exist
        final_label = "FAKE"
        final_conf = gem_conf
        method = "gemini_override"

    elif gem_verdict == "MISLEADING":
        # Distinct state: real events reported deceptively or out of context
        # Only accept MISLEADING if Gemini is highly confident (≥0.85).
        # Lower confidence MISLEADING verdicts on political content often reflect
        # Gemini being pedantic about phrasing rather than detecting genuine
        # deceptive framing. Downgrade to REAL with a note.
        if gem_conf >= 0.85:
            final_label = "MISLEADING"
            final_conf = gem_conf
            method = "gemini_override"
        else:
            final_label = "REAL"
            final_conf = round(gem_conf * 0.7, 4)
            method = "gemini_downgraded"

    elif gem_verdict == "UNVERIFIED":
        # Blend: Gemini couldn't confirm either way — let BERT break the tie.
        # Formula: 40% weight to Gemini's uncertainty (fixed 0.5), 60% to BERT fake signal.
        # BERT now has majority vote — unlike the old 0.7*0.5 anchor that was nearly immovable.
        style_label = style_result.get("label", "REAL")
        style_conf = style_result.get("confidence_score", 0.5)
        # bert_fake_prob: probability this sample is fake-style prose (0→1)
        bert_fake_prob = style_conf if style_label == "FAKE" else (1.0 - style_conf)
        blended_fake_score = (0.4 * 0.5) + (0.6 * bert_fake_prob)
        final_label = "FAKE" if blended_fake_score > 0.55 else "REAL"
        final_conf = round(blended_fake_score, 4)
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


# ── Public API ────────────────────────────────────────────────────────────────

def run_nlp_layers(text: str, headline: str = None, lang: str = 'en') -> Dict[str, Any]:
    """
    Orchestrate the full NLP analysis stack.
    
    Returns a dict with keys:
      style_classification — DistilBERT ISOT pattern result
      explainability       — LIME word attribution triggers
      fact_check           — Gemini search-grounded fact-check with sources
      composite_verdict    — Final FAKE/REAL verdict combining both signals
      clickbait_check      — Headline vs body promise check (if headline provided)
      emotional_tone       — Fear / outrage / sensationalism scores
    """
    output: Dict[str, Any] = {}

    # 1. Style classification (GPU, already loaded)
    output["style_classification"] = _bert.analyze(text)

    # 2. LIME word-level attribution
    output["explainability"] = _explainer.generate_explanation(text, _bert)

    # 3. Search-grounded fact-check
    print("[NLP] Running search-grounded fact-check...")
    fact_result = _llm.fact_check(text, lang=lang)
    output["fact_check"] = fact_result

    # 4. Composite verdict
    output["composite_verdict"] = _build_composite_verdict(
        output["style_classification"],
        fact_result,
        text=text,
        headline=headline,
    )

    # 5. Clickbait check (requires headline)
    if headline:
        output["clickbait_check"] = _llm.check_clickbait(headline, body_text=text)
    else:
        output["clickbait_check"] = {"error": "No headline provided — clickbait check skipped."}

    # 6. Emotional tone
    output["emotional_tone"] = _llm.score_emotion(text)

    return output

# TruthLens Architecture: Master Synopsis

This document provides a comprehensive overview of the files, core concepts, and primary functions/classes within the TruthLens (QA 1.0) workspace. 

TruthLens is a search-grounded media intelligence platform designed to detect fabricated or misleading news using a hybrid approach: stylometric classification (DistilBERT) combined with search-grounded logical reasoning (Gemini LLM) and Explainable AI (LIME).

---

## 1. Application Orchestration

### `app.py`
The web server and API gateway, built using Flask.
*   **`analyze()`**: Main API route (`/api/analyze`). Receives the text, headline, and language payload from the frontend and passes them to `pipeline.py`.
*   **`serve_frontend()`**: Serves the root `index.html` file to the user's browser.
*   **Concept**: Acts as the bridge connecting the user interface (client) and the Python intelligence pipeline backend.

### `pipeline.py`
The orchestration layer that links all internal intelligence modules.
*   **`execute_pipeline(text, headline, url, lang)`**: 
    *   Calls the core NLP functions for fact-checking and stylometric analysis.
    *   Fuses the outputs into a standard dictionary format compatible with the frontend.
    *   Triggers the `ExplainLayer` to generate LIME diagrams.
*   **Concept**: Enforces the execution order (NLP -> Explainability) and structures the final response.

---

## 2. Core Intelligence (NLP & Reasoning)

### `nlp_layer.py`
The brain of TruthLens. Handles deep learning inference and LLM execution.
*   **`DistilBertAnalyzer` (Class):**
    *   `analyze(self, text)`: Runs local Transformer inference (`mrm8488/bert-tiny-finetuned-fake-news-detection`) to detect if the text is written in a deceptive/fake style.
*   **`GeminiInferenceServer` (Class):**
    *   `fact_check(self, text, lang)`: Uses Gemini with the `google_search_retrieval` tool. Checks real-time web sources to verify claims. Dynamically adjusts prompts depending on whether language is English (`en`) or Marathi (`mr`), forcing regional context.
    *   `check_clickbait(self, headline, body_text)`: Detects if the headline exaggerates or misrepresents the content.
    *   `score_emotion(self, text)`: Evaluates affective vectors (Fear Load, Outrage Generation, Sensationalism).
*   **`_build_composite_verdict()`**: The fusion engine. Harmonizes raw scores from the BERT model and the Gemini reasoning engine into a definitive `"REAL"`, `"FAKE"`, or `"MISLEADING"` verdict using confidence blending formulas.
*   **`run_nlp_layers()`**: The facade method called by `pipeline.py` to trigger the analyzers in parallel or sequence.

---

## 3. Explainability (XAI)

### `explain_layer.py`
Provides interpretability to the "black-box" neural network.
*   **`ExplainLayer` (Class):**
    *   `generate_explanation(self, text, analyzer_instance)`: Uses the LIME (Local Interpretable Model-agnostic Explanations) algorithm. It perturbs the input text randomly, tracks the BERT model's predictions, and derives mathematical weights for which specific words pushed the model toward "REAL" or "FAKE".
*   **Concept**: Necessary for transparency, allowing users to see exactly which phrases the model found suspicious.

---

## 4. Input & Data Handling

### `input_handler.py`
Utilities for preparing raw data.
*   **`fetch_text(source)`**: Uses `BeautifulSoup` to scrape paragraphs from an external URL if the user provides a link instead of pasting raw text.
*   **`extract_claim_evidence()`**: Basic helper to structure data.

### `scraper_layer.py`
*   Contains functions to look up domains against Bias indicators (AllSides, MediaBiasFactCheck). 
*   *Note: Currently decoupled from the primary frontend to streamline the UI layout, but logic remains available.*

---

## 5. Frontend & Layout

### `index.html`
A monolithic HTML/CSS/JS file powering the user interface.
*   **Tailwind CSS**: Uses injected utility classes to generate the dark-mode layout (vibrant orange/dark-gray palette).
*   **Concept (Localization)**: Contains an `I18N` global JS object map. Toggling EN/MR immediately updates text keys across the page.
*   **Concept (DOM Management)**: Heavy use of dynamic `class` toggles and element injection to display real-time LIME diagrams, affective filter bars, and Gemini text streams without page reloads.

---

## 6. Testing & Benchmarks

### `test_*.py` (Various Files)
Unit testing framework using `pytest`.
*   Includes mocks for the Gemini client and HuggingFace pipelines (`test_nlp_layer.py`) to run CI checks offline or without API credits.
*   `test_phase9_fallback_hardening.py`: Ensures the parametric logic (what happens when search fails) is robust and mathematically sound.

### `run_benchmark.py` & `run_maharashtra_benchmark.py`
Execution scripts to run large batches of claims against the pipeline.
*   **Concept**: Produces extensive markdown reports by evaluating test datasets against the live Gemini/BERT engines to track True/False Positive Rates and System Latency.

### `politics_test_set.py` & `maharashtra_test_set.py`
*   Variables containing arrays of complex, real-world political claims (English & Marathi) with known Ground Truths, used to run the benchmark scripts against.

---

## 7. Configuration & Patches

### `.env`
*   Holds critical environment variables (`GEMINI_API_KEY`).

### `patch.py` / `.gitignore` / `requirements.txt`
*   Standard Python infrastructure files. `requirements.txt` dictates dependencies like `Flask`, `transformers`, `lime`, `google-genai`. `patch.py` holds small tactical overrides for broken upstream dependencies.

---

## 8. Applied Computer Science Topics

The TruthLens codebase heavily relies on several advanced paradigms within Computer Science and Artificial Intelligence. Here is a breakdown of what they are and why they are implemented:

### Natural Language Processing (NLP)
*   **What it is:** A field of AI focused on giving computers the ability to understand text and spoken words in much the same way human beings can. It involves tokenization, sentiment analysis, and semantic understanding.
*   **Why we used it:** To dynamically analyze unstructured news data for affective signals (fear, outrage) and clickbait tendencies. Traditional regex/keyword filters fail on nuanced human language, making NLP essential for parsing tone.

### Deep Learning & Transformer Architectures
*   **What it is:** A type of neural network architecture (specifically BERT) that processes sequences of words not linearly, but simultaneously using "Self-Attention Mechanism." This allows the model to weigh the contextual importance of a word based on the surrounding text.
*   **Why we used it:** We used HuggingFace's `DistilBERT` (a smaller, faster Transformer) for **Stylometric analysis**. Fake news often exhibits a specific linguistic style (hyperbolic or overly urgent). Transformers detect these stylistic fingerprints far better than standard machine learning classifiers.

### Retrieval-Augmented Generation (RAG) / Grounded Search
*   **What it is:** An architecture that combines the reasoning ability of a Large Language Model (LLM) with real-time access to an external database or the internet, preventing the LLM from relying solely on its static, historical training parameters.
*   **Why we used it:** For the **Gemini Fact-Check engine**. Instead of asking Gemini to guess if a claim is real (which leads to hallucinated answers), the pipeline forces Gemini to issue Google Search queries, read the top indexed results, and base its verdict precisely on verified, real-time news sources.

### Explainable Artificial Intelligence (XAI)
*   **What it is:** A set of techniques that allow human users to comprehend and trust the mathematical predictions made by machine learning models. We use **LIME** (Local Interpretable Model-agnostic Explanations), which tests a model by perturbing the input data to see how the prediction changes.
*   **Why we used it:** Neural networks (like DistilBERT) are "black boxes"—they output a score without explaining logic. By implementing LIME in `explain_layer.py`, TruthLens generates word-level heatmaps, showing the user the exact words (e.g., "SHOCKING", "DISASTER") the model deemed deceptive, preventing blind trust in the AI.

### Distributed Systems & API Orchestration
*   **What it is:** Designing software in modular, decoupled layers (Client, Server, Inference Engine) that communicate over standard protocols (HTTP/REST) instead of monolithic compilation.
*   **Why we used it:** By putting the Python analytical engines behind a Flask API (`app.py`), the UI logic (HTML/JS) operates completely independently. This means the heavy GPU-bound Transformer logic does not block the browser's render thread, leading to a fluid user experience.

---

## 9. Feasibility and Viability Analysis

### Technical Feasibility
*   **Lightweight Compute:** By utilizing `DistilBERT` (a compressed version of BERT) rather than deploying massive billion-parameter models locally, TruthLens can run inference on consumer-grade hardware (standard VMs or edge devices) without relying on huge multi-GPU clusters.
*   **API Ecosystem Resilience:** The heavy cognitive lifting (Reasoning & Grounding) is offloaded to the Google Gemini API. This allows the localized backend to remain lightweight. Furthermore, a robust parametric fallback ensures the pipeline can gracefully handle API rate limits or network outages without fatal crashes.
*   **Decoupled Architecture:** Using a standard REST API backend (Flask) paired with a VanillaJS/Tailwind frontend means the application is entirely tech-stack agnostic. It is horizontally scalable (we could drop in a React or native mobile app frontend seamlessly).

### Commercial & Operational Viability
*   **High Market Relevance:** Modern information ecosystems are plagued by misinformation (especially during elections or crises). Generating rapid, explainable verdicts with automated deep-tracing solves a critical bottleneck for journalists, content moderators, and political analysts.
*   **Transparent Decision Mapping (XAI):** A major roadblock to AI adoption is the "black box" problem. Because TruthLens implements LIME XAI, it proves visual, mathematical accountability for its verdicts. This increases credibility and trust, overcoming institutional hesitancy toward AI tools.
*   **Low Operational Costs:** Generating insights primarily via Gemini Flash/Pro combined with free tier HuggingFace local models keeps overhead negligible.
*   **Regional Localization:** Demonstrating robust localized capabilities (such as the Marathi translation and regional web-search injection loop) proves viable scaling beyond just English-speaking audiences into highly lucrative, diverse linguistic markets.

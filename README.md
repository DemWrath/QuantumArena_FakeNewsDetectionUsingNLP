# TruthLens 🔍

**TruthLens** is an advanced, search-grounded media intelligence platform designed to combat misinformation through a fusion of Deep Learning stylometric analysis, Large Language Model logic reasoning, and localized search retrieval.

Designed for journalists, analysts, and content moderators, TruthLens goes beyond simple binary filtering. It provides transparent, explainable (XAI) deep traces on unstructured news payloads, verifying claims against live search indexes while surfacing affective vectors like "Outrage Generation."

## 🚀 Key Features

*   **Dual-Layer Intelligence Pipeline:** Combines a local DistilBERT Transformer (for fast stylistic deception detection) with the Google Gemini LLM (for cognitive reasoning and fact-checking).
*   **Search-Grounded Verification:** Gemini automatically issues real-time Google Search queries to fact-check claims before generating verdicts, preventing AI hallucinations.
*   **Explainable AI (LIME):** TruthLens is not a "black box". It uses the Local Interpretable Model-agnostic Explanations (LIME) algorithm to generate color-coded word heatmaps, highlighting exactly which phrases triggered the "FAKE" verdict.
*   **Affective & Logic Filtering:** Scans for psychological manipulation tactics, scoring texts on Fear & Anxiety Vectors, Sensationalism Loads, and Clickbait probabilities.
*   **Regional Localization (Marathi Support):** Fully translatable interface with a language-aware pipeline that forces the AI engine to prioritize regional news sources (e.g., *Lokmat, Sakal, ABP Majha*) during verification.

## 🛠️ Tech Stack Architecture

*   **Frontend:** Vanilla JavaScript, HTML5, TailwindCSS (Dynamic Grid layout, Dark UI theme).
*   **Backend:** Python `Flask` REST API.
*   **Transformer Models:** HuggingFace `transformers` (`mrm8488/bert-tiny-finetuned-fake-news-detection`).
*   **LLM Gateway:** Google GenAI SDK (`gemini-2.5-flash`).
*   **Explainability:** `lime` text processing library.

## ⚙️ Installation & Operation

### 1. Requirements
*   Python 3.9+
*   A Google Gemini API Key

### 2. Setup environment
Clone the repository, then install requirements:
```bash
git clone https://github.com/yourusername/TruthLens.git
cd TruthLens
pip install -r requirements.txt
```

### 3. Environment Variables
Create a `.env` file in the root directory and add your Gemini API Key:
```env
GEMINI_API_KEY=your_google_gemini_api_key_here
```

### 4. Running the Engine
Start the Flask application gateway:
```bash
python app.py
```
*Note: The frontend runs instantly upon execution. TruthLens uses local Transformer weights, so the first runtime will quickly cache the HuggingFace DistilBERT model if it isn't already installed locally.*

Access the UI at: `http://localhost:5000/`

## 📊 Benchmarking & Testing
TruthLens comes shipped with ground-truth datasets for political claims (both English and Marathi). To stress-test the pipeline:

```bash
python run_benchmark.py
python run_maharashtra_benchmark.py
```
These scripts bypass the UI and generate deep Markdown reports analyzing the True/False Positive Rates and System Latency of the classification engines.

---
*Developed by LocalHost | TruthLens*

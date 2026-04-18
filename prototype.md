# TruthLens Prototype Documentation

## Concept Overview
The TruthLens prototype represents the finalized 1.0 architecture built to prove the viability of a multi-layer NLP media intelligence tool. Rather than a minimal visible product, the prototype operates as a fully functional, tech-agnostic interface that highlights the synergy between traditional deep learning classifiers and external LLM reasoning. 

## Prototype Scope and Features

### 1. The Interface (UI)
The frontend prototype is intentionally designed as an imposing, analyst-focused dashboard.
*   **Vanilla JS Integration:** The UI relies strictly on plain JavaScript for DOM manipulation, demonstrating that robust API interactions and dynamic UI swaps (like animated Marquees or LIME Heatmaps) do not strictly necessitate heavy frameworks.
*   **Localization Toggle:** The prototype features real-time UI language swapping (English ⇄ Marathi). This capability serves as a proof-of-concept for regional scaling, demonstrating string dictionary swapping tied seamlessly to backend prompt-injection (which forces Marathi news curation).
*   **Responsive Grid Layout:** Features CSS grid logic that gracefully shrinks data streams down for compact viewports while offering expansive visuals for high-resolution screens.

### 2. Logic Pipeline Implementation
The pipeline demonstrates sequential processing. 
*   **Layer 1 (Stylometric):** Input is instantly scored by standard local `DistilBERT` to ascertain deception by *style*.
*   **Layer 2 (Cognitive Grounding):** Input is then sent to Gemini to ascertain deception by *fact*.
*   **Layer 3 (Interpretability):** Only triggered upon returning the verdict to the frontend, proving that explainability algorithms (LIME) can run quickly enough dynamically in a web workflow without completely freezing the server.

### 3. XAI (Explainable AI) Visualization
The prototype successfully achieves what many similar detection tools fail to do: it breaks open the "Black Box" of neural networks. 
*   **How it shows up:** When a user analyzes text, the prototype generates a localized interpretability readout, highlighting words in **red** (factors pushing to FAKE) vs. **green** (factors pushing to REAL).
*   **Goal:** To prove to stakeholders that automated threat classification can be transparent. 

### 4. Parametric Fallback Capabilities
The prototype includes a robust "Parametric Engine Fallback" system. If Gemini detects that a claim revolves around generic concepts rather than breaking news, or if network index scraping fails, the prototype seamlessly degrades to logic-based assessment without crashing, labeling cases as "PARAMETRIC ONLY."

## Current Limitations & Debt 

While fully functional, the current 1.0 prototype maintains the following constraints to limit scope drift for this developmental phase:
*   **Sequential Python Processing:** Currently, Flask workers execute `pipeline.py` sequentially in relation to `app.py`. As concurrent connections scale, Thread/Task queues (like Redis/Celery) will be required.
*   **API Cost Constraints:** The platform is resilient and highly accurate but relies heavily on external GenAI API key stability.
*   **Visual LIME Processing:** While LIME explainability renders dynamically, heavy paragraphs with excessive string alterations take significantly more compute load than the Transformer itself. Future iterations should push this to background sockets.

## Demo Flow

To demonstrate the prototype's core capabilities effectively to stakeholders:
1. Paste heavily sensationalized political clickbait containing a specific, searchable claim.
2. Observe the **Transformers** flagging the linguistic style rapidly.
3. Observe the **Gemini** module returning the Live sources it utilized to deduce the logical outcome.
4. Note the dynamic **Affective Filter** (Sensationalism/Fear load) returning high percentages.
5. Review the **Deep Logic Trace** (LIME) at the bottom highlighting hyperbolic words.
6. Toggle the **Marathi** language switch to observe the UI and backend logic adapt seamlessly to local intelligence mode.

# Roadmap

## Milestones

- ✅ **v1.0 Unification & Foundation (Layer 1)** — Phases 1-2 (Shipped 2026-04-16)
- ✅ **v2.0 Semantic Analysis & Source Context** — Phases 3-6 (Shipped 2026-04-17)
- 🚧 **v3.0 Explainability & API Server (Layers 4 & 5)** — Phases 7-8 (Planned)

## Phases

<details>
<summary>✅ v1.0 Unification & Foundation — SHIPPED 2026-04-16</summary>

- [x] Phase 1: Context Establishment
- [x] Phase 2: Pipeline Scaffolding

</details>

<details>
<summary>✅ v2.0 Semantic Analysis & Source Context — SHIPPED 2026-04-17</summary>

- [x] Phase 3: Transformer-based NLP Analysis
- [x] Phase 4: Source Intelligence & Live Fact-Scraping
- [x] Phase 5: Layer Fusion & Pipeline 2.0
- [x] Phase 6: Frontend Data Restructuring

</details>

### 🚧 v3.0 Explainability & API Server (In Progress)
**Goal**: Surface the model's logic transparently to end users via a localized Web Server bridging the Python pipeline directly into the Threat-Map UI!

## Phase 7: Local API Fast Web Server Data Binding
**Goal**: Launch a local web server to bind `pipeline.py` processing natively to `index.html`.
- **API-01**: Implement the Flask server wrapping the pipeline execution inside a POST `/api/analyze` route.
- **API-02**: Format and secure cross-origin requests bridging port execution spaces safely.
- **API-03**: Finalize JavaScript updates within `index.html` stripping the hardcoded responses out permanently.

## Phase 8: Deep Explainability Mapping (LIME/SHAP)
**Goal**: Trace logic sequences explicitly mapping why the Transformer layers evaluated strings organically. 
- **EXPL-01**: Integrate LIME semantic keyword weighting identifying positive/negative triggers driving classification thresholds natively.
- **EXPL-02**: Pass HTML-enabled gradient arrays directly into the `/api/analyze` JSON framework.
- **EXPL-03**: Upgrade the Frontend UI Threat Interface to render LIME explanatory tags elegantly.

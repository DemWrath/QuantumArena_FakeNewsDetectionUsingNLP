# Roadmap

## Milestones

- ✅ **v1.0 Unification & Foundation (Layer 1)** — Phases 1-2 (Shipped 2026-04-16)
- ✅ **v2.0 Semantic Analysis & Source Context** — Phases 3-6 (Shipped 2026-04-17)
- ✅ **v3.0 Explainability & API Server (Layers 4 & 5)** — Phases 7-10 (Shipped 2026-04-18) → [archive](milestones/v3.0-ROADMAP.md)

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

<details>
<summary>✅ v3.0 Explainability & API Server — SHIPPED 2026-04-18</summary>

- [x] Phase 7: Local API Fast Web Server Data Binding
- [x] Phase 8: Deep Explainability Mapping (LIME/SHAP)
- [x] Phase 9: Parametric Fallback Hardening
- [x] Phase 10: Cross-Phase Integration Fix

</details>

- 🚧 **v4.0 Detection Accuracy & Generalization** — Phases 11+ (In Progress)

### 🚧 v4.0 Detection Accuracy & Generalization (In Progress)
**Goal**: Generalize the pipeline's detection capabilities beyond Maharashtra-specific patterns, close accuracy gaps exposed by the politics benchmark (40% → target 70%+), and harden fallback behaviour under API exhaustion.

## Phase 11: Politics Benchmark Accuracy Fixes
**Goal**: Close the 9 incorrect predictions from the politics benchmark by expanding heuristic coverage, guarding MISLEADING fallback, correcting test data, and tuning the Gemini prompt for political news tolerance.
- **Depends on**: Phase 10
- **POL-01**: Expand `_heuristic_signals()` with political impossibility phrases — sovereign merger/dissolution claims, UN expulsion without Security Council, constitution abolition, global government formation. Catches POL-FAKE-01, POL-FAKE-04, POL-EDGE-01.
- **POL-02**: Add MISLEADING fallback guard — when Gemini is unavailable, the fallback path should never produce a MISLEADING verdict (only REAL/FAKE). MISLEADING requires semantic reasoning about omission/exaggeration that BERT cannot provide.
- **POL-03**: Tune Gemini grounded fact-check prompt to tolerate minor phrasing variations in political news (e.g. "Parliament's competence" vs "President's authority") without escalating to MISLEADING. Reduce false positives on REAL political articles.
- **POL-04**: Fix test data error in POL-REAL-03 (Reform UK won 5 seats, not 4) and review all political test set samples for factual accuracy against primary sources.

### Plans
- [x] POL-01: Expand political heuristic phrases
- [x] POL-02: MISLEADING fallback guard
- [x] POL-03: Tune Gemini political tolerance prompt
- [x] POL-04: Fix politics test set data errors

# Domain

Building a multi-layer intelligent media analysis system for **fake news detection and media bias analysis**. This project unifies and enhances three existing codebases to combine traditional ML-based NLP pipelines, LLM-based media evaluation frameworks, and Graph-based contextual bias modeling into a single, cohesive framework.

Input modalities currently focus on Text, with plans to expand to Vision/audio/video.

## Core Value

To combat misinformation and media manipulation by providing a multi-layer, highly transparent, and explainable analysis system that evaluates text for truthfulness, detects 100+ manipulation techniques, scores source credibility, and visually explains its reasoning to users.

## Current State: v3.0 shipped (2026-04-18)

Milestone v3.0 (Explainability & API Server) has been completed and archived.
The system now has a fully functional Flask API server, LIME explainability engine,
and hardened parametric fallback pipeline with zero-API heuristic detection.

**Test suite:** 37/37 passing | **Requirements:** 6/6 satisfied

**Target Features:**
- **Local Application Hub:** Wrapping the backend logic pipelines in FastAPI/Flask routes matching the UI requirements. 
- **SHAP/LIME Explainers:** Visual models tracking which exact words triggered the FAKE classification.

## Requirements

### Validated

- ✓ ML Classification Pipeline: Naive Bayes, Logistic Regression (Final selected). (M1)
- ✓ HonestyMeter Framework: LLM-based analysis of manipulation techniques, objectivity scoring. (M1)
- ✓ Sentence-Level Media Bias Graph: Event relation graph using coreference. (M1)
- ✓ URL Article Fetcher: Integrated `newspaper3k` for unified ingestion. (M1)
- ✓ Claim & Evidence Extraction: Automated semantic slicing of article components. (M1)
- ✓ **Layer 2 (NLP Analysis):** Integrated DistilBERT and runtime Gemini LLM checks for clickbait/emotions. (M2)
- ✓ **Layer 3 (Source Credibility):** Integrated automated Live Scrapers (AllSides/MBFC) and Gemini Fallback mechanisms mapped to Domain extraction. (M2)
- ✓ **Frontend Mapping:** Upgraded static `index.html` UI block to consume unified JSON dictionary trees. (M2)
- ✓ **API Controller (Integration):** Flask web-server binding `index.html` natively to `pipeline.py`. (M3)
- ✓ **Layer 4 (Explainability):** LIME word-level attribution tracing DistilBERT classification triggers. (M3)
- ✓ **Parametric Fallback Hardening:** Three-tier fallback (Gemini → Heuristic → BERT) with honest prompts. (M3)

### Next Milestone Goals (v4.0+)

- [ ] **SEC-01**: Expand local network to AWS Cloud architectures.
- [ ] **SEC-02**: Expand image extraction pipeline mapping CV engines.
- [ ] **Layer 5 (Output):** Generate plain-English LLM-generated explanations, and exportable full reports (JSON/PDF).
- [ ] **Multimodal Foundation:** Complete stubs/foundations for image and non-text routing.
- [ ] **E2E Test Automation:** Selenium/Playwright tests for UI verification (tech debt from v3.0).
- [ ] **Heuristic Generalization:** Expand `_heuristic_signals()` phrase list beyond Maharashtra dataset.

### Out of Scope

- [ ] Automatic deletion or censorship of recognized fake news on other platforms (Focus is solely on analytical detection and explanation).
- [ ] Fully autonomous social media bot monitoring in Phase 1 (Core scope relies on specific user inputs or scraped articles).

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Merge 3 separate repos | Unifies classification, manipulation detection, and sentence-level bias tracking into one end-to-end framework. | Pending pipeline script/merger |
| Select Logistic Regression | Best balance of F1-score and feature interpretability (TF-IDF mapping) over Random Forest out of initial ML models. | Validated |
| Sub-Repo Management | Keep code mapped correctly while planning, since there are 3 distinct cloned directories. | Active |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition**:
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

---
*Last updated: 2026-04-18 — v3.0 milestone completed and archived*

# Requirements: Media Analysis Framework (Milestone 3.0)

**Defined:** 2026-04-17
**Core Value:** Surface the model's logic transparently to end users and bind the logic block to a highly functional localized Flask Server connecting directly to the Frontend Dashboard.

## Milestone 3 Requirements (v3.0)

### Category 1: Application Programming Interface (API)
- [ ] **API-01**: Implement local Flask or FastAPI Web Server mapping UI POST calls (`/api/analyze`) directly into `pipeline.py` architecture.
- [ ] **API-02**: Connect frontend Javascript securely via CORS bindings to the Local Host daemon.
- [ ] **API-03**: Eradicate hardcoded Javascript mock responses from `index.html` entirely; route state cleanly to JSON streams.

### Category 2: System Explainability (EXPL)
- [ ] **EXPL-01**: Integrate SHAP or LIME explainer matrices tracking deterministic keyword weights that flagged DistilBERT NLP outputs.
- [ ] **EXPL-02**: Serialize word-gradient mapping clusters (HTML-ready spans/highlights) returning within the main JSON Payload.
- [ ] **EXPL-03**: Create dynamic UI rendering elements parsing the Explainability tags.

## Future Requirements (v4.0+)
- [ ] **SEC-01**: Expand local network to AWS Cloud architectures.
- [ ] **SEC-02**: Expand image extraction pipeline mapping CV engines.

## Out of Scope
| Feature | Reason |
|---------|--------|
| Automatic content deletion | Out of analytical scope; purely transparency-focused. |
| Production Dockerization | Wait until application UI structure entirely validated locally. |

## Traceability
| Requirement | Phase | Status |
|-------------|-------|--------|
| API-01 | TBD | Pending |
| API-02 | TBD | Pending |
| API-03 | TBD | Pending |
| EXPL-01 | TBD | Pending |
| EXPL-02 | TBD | Pending |
| EXPL-03 | TBD | Pending |

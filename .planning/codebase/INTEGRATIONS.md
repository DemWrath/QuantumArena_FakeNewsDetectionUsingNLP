# External Integrations

## Core APIs
- Currently, the application processes local tabular textual data or raw text CLI inputs without reaching out to external SaaS providers.
- **Planned (Phase 2):** Scrapers such as `newspaper3k` will interact directly with public HTTP surfaces to resolve URL article payloads into usable string formats.

## Databases
- No persistent SQL/NoSQL engine exists natively yet. 
- The models utilize serialized disk cache (e.g. `modern_model.joblib`) effectively as a "frozen" knowledge store, alongside explicit CSV structures (`train.csv`, `test.csv`).

## Internal Bridges
- The integration boundary relies on `pipeline.py`, which is designed to act as a synchronous API layer or a subprocess bridge between the eventual Next.js API router and the Python modeling architecture.

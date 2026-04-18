# System Architecture

## Design Pattern & Topology
The application follows an **Orchestrated ML Pipeline** pattern spanning frontend, API, and computational domains.
It enforces a strict separation of concerns where Python scripts operate exclusively as stateless evaluation functions that are hit by routing layers.

## Component Layers

1. **Top-Level Orchestrator (`pipeline.py`)**:
   - Accepts raw text arrays.
   - Synchronously dispatches processing instructions sequentially to isolated subsystems.
   - Collects outputs globally and constructs definitive JSON diagnostic results.

2. **Computational Layer 1 (Fake News Detection)**:
   - Uses a pre-trained TF-IDF logic hooked into Logistic Regression.
   - Designed to run extremely fast statistical regressions on text input directly.

3. **Computational Layer 2 (Event Relation Graph / NAACL 2024)**:
   - Deep semantic NLP model utilizing AllenAI's Longformer.
   - Maps coreference, temporal, causal, and subevent matrices from given token structures.
   - Deployed on accelerating hardware (GPU mapped dynamically when available via PyTorch).

4. **Web Frontend Endpoint (`HonestyMeter`)**:
   - Next.js presentation and API layer (Currently operating independently).
   - Slated to ingest responses from the Python backend layer by exposing endpoints.

## Data Flow
`User Interface/URL` -> `Node Router` -> `pipeline.py` -> `Data Prep & Inference` -> `JSON Construction` -> `Frontend Renderer`

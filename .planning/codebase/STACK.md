# Technology Stack

## Languages
- **Python**: Primary language for the machine learning and orchestrator pipelines (`>= 3.10`).
- **JavaScript/TypeScript**: Used for the Next.js `HonestyMeter` UI and frontend logic.

## Runtime & Frameworks
- **Node.js**: powers the frontend via Next.js server actions.
- **React**: Frontend UI framework for the dashboard tools.
- **Vanilla Python**: Powers the `pipeline.py` root execution orchestrator.

## Core Libraries / Dependencies
- `scikit-learn` (`>=1.3.0`): Traditional ML evaluation and TF-IDF processing.
- `torch` (`>=2.0`): Deep learning engine for Longformer architecture inference.
- `transformers`: Huggingface implementation for Longformer sequences.
- `pandas` & `numpy`: Tabular and dimensional data manipulation.
- `nltk`: Natural language tokenization and processing.
- `joblib`: Model parameter serialization (`modern_model.joblib`).
- `newspaper3k` (Planned): Web extraction engine.

## Tooling & Configuration
- `npm`/`yarn`: Next.js package orchestration (`HonestyMeter/package.json`).
- `requirements.txt`: Root python dependency registry.

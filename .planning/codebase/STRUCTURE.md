# Directory Structure

## Repository Root
```
e:/QA1.0_2/
├── .planning/                  # GSD Workflow specifications and maps
├── Fake_News_Detection/        # Sub-repository: Logistic statistical modeling
├── HonestyMeter/               # Sub-repository: Next.js Frontend Framework
├── sentence_level_media_bias_naacl_2024/   # Sub-repository: Graphical NLP Processing
├── pipeline.py                 # Core integration script serving as backend hook
├── patch.py                    # Build scripts for modernizing legacy Python execution
├── requirements.txt            # Unified project environment schema
└── train_modern_model.py       # ML Model instantiation worker
```

## Key Modules

### `Fake_News_Detection/Fake_News_Detection/`
Contains modular legacy data preparation rules (`DataPrep.py`) and standard vector pipelines (`FeatureSelection.py`). Exposed primarily via `classifier.py`.

### `HonestyMeter/HonestyMeter/`
Standard React component topology nested within a Next.js `server/` routing environment.

### `sentence_level_media_bias_naacl_2024/sentence_level_media_bias_naacl_2024/`
Houses `bias_event_relation_graph_BASIL.py` acting as an entrypoint invoking Torch layers over JSON-computed structures.

## Naming Conventions
- Top-level directories retain original git clone paths (capitalized/snake_case combos).
- Future additions conform to standard Python `snake_case` or React `PascalCase` localized exactly to the language environment boundary.

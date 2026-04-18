# Phase 1 Context: Repository Pipeline Integration

## Decisions
- **Pipeline Architecture:** API-first or Master Script will be determined by the technical requirements of the codebase upgrades, but it must be fully compatible and unified.
- **Python Modernization (CRITICAL):** The existing Python code across Fake_News_Detection and sentence_level_media_bias is old and will cause version conflicts. ALL code must be reviewed, upgraded to modern Python 3.x standards, and dependencies must be modernized while preserving the exact original functionality.
- **Input Mechanism:** Unify text inputs so they cleanly feed into the new, modernized python pipeline. 

## Technical Directives
- Scan through `Fake_News_Detection` and `sentence_level_media_bias_naacl_2024` to identify deprecated functions, old library usages (e.g., outdated `scikit-learn`, `pandas`, `networkx` etc.).
- Refactor/correct code directly where needed while maintaining the same logical ML execution paths and accuracy.

## Canonical Refs
- `Fake_News_Detection/Fake_News_Detection/classifier.py`
- `sentence_level_media_bias_naacl_2024/sentence_level_media_bias_naacl_2024/*.py`
- `HonestyMeter/HonestyMeter/server/`

# Technical Concerns & Debt

## Codebase Atrophy
- The core Machine Learning models (`Fake_News_Detection`) were structurally built against legacy Scikit-Learn instances (from 2017). Continuing modifications strictly require local `.joblib` re-serialization passes via `train_modern_model.py` anytime core parameters are fundamentally shifted to avoid deprecation panics.

## Performance
- The `sentence_level_media_bias_naacl_2024` Event Relation mechanism uses heavy `Longformer` sequential evaluation logic. Iterating across multiple graph dimensions synchronously during an atomic user web request could produce debilitating latency. Parallel processing or asynchronous queue-states will be necessary moving forward.

## Security
- Hardcoded directory paths mapping internal models.
- Potential vector injection via unstructured text manipulation when piping frontend inputs directly via CLI arguments into prediction loops requires thorough sanitation.

## Fragile Areas
- The Media Bias analyzer relies heavily on rigid input dictionary formats constructed strictly through implicit sub-modules. Any breaking API alterations from updated AllenAI models or Huggingface libraries might shatter tokenizer length offsets completely.

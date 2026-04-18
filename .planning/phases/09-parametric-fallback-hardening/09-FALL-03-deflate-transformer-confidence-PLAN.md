---
id: FALL-03
wave: 1
depends_on: []
files_modified:
  - nlp_layer.py
autonomous: true
---

# Plan FALL-03: Deflate Transformer-Only Confidence Score

## Goal
Prevent the raw DistilBERT ISOT style-match probability (e.g. 0.9973) from being
surfaced as `final_confidence` in `transformer_only` fallback mode, where it is
routinely misinterpreted as a fake-news probability by the UI and downstream consumers.

## Context
Current `transformer_only` fallback in `_build_composite_verdict()` (lines ~349–359):
```python
    if "error" in fact_result:
        style_label = style_result.get("label", "REAL")
        return {
            "final_label": style_label,
            "final_confidence": style_result.get("confidence_score", 0.0),
            "method": "transformer_only",
            "note": "Gemini fact-check unavailable. Transformer style label used as fallback."
        }
```

The score `0.9973` means: "the prose pattern of this text matches the ISOT fake-news
corpus training distribution with 99.73% similarity." It does NOT mean "this article
is 99.73% likely to be fake news." A CIA press release would score ~0.999 REAL on
ISOT — but that tells us nothing about whether a specific article's facts are correct.

The UI currently renders this as a confidence bar, creating false certainty.

**Calibration target**: A `transformer_only` verdict should have max confidence ~0.60
(reflecting genuine uncertainty — BERT style alone is not a reliable fake-news signal).
Multiplying by 0.6 maps the typical 0.85–0.99 range to 0.51–0.60, which is visually
distinct from Gemini-grounded results (0.75–0.95).

## Tasks

### Task 1: Deflate confidence and expand the explanatory note

<read_first>
- e:\QA1.0_2\nlp_layer.py  (lines 349–360 — the `if "error" in fact_result:` block)
</read_first>

<action>
NOTE: FALL-04 will rewrite this entire block to add heuristic detection before the
transformer fallback. This plan's change must be compatible — apply the deflation to
the INNER transformer_only return that remains after FALL-04 adds the heuristic branch.

For now (before FALL-04 is applied), replace the return statement inside
`if "error" in fact_result:` with:

```python
    if "error" in fact_result:
        style_label = style_result.get("label", "REAL")
        raw_conf = style_result.get("confidence_score", 0.0)
        return {
            "final_label": style_label,
            # Deflate: ISOT style-match probability ≠ fake-news probability.
            # 0.9973 style confidence does NOT mean 99.73% sure it's fake.
            # Multiply by 0.6 to signal calibration uncertainty to the UI.
            "final_confidence": round(raw_conf * 0.6, 4),
            "method": "transformer_only",
            "note": (
                "Gemini fact-check unavailable. Style-pattern label used as fallback. "
                f"Raw style confidence {raw_conf:.4f} deflated ×0.6 — style-match "
                "probability is not equivalent to fake-news probability."
            )
        }
```

The `note` field is used by the UI's tooltip and the benchmark text report.
Including the raw confidence in the note preserves traceability.
</action>

<acceptance_criteria>
- [ ] `nlp_layer.py` contains `round(raw_conf * 0.6, 4)` in the transformer_only return
- [ ] `nlp_layer.py` does NOT contain `"final_confidence": style_result.get("confidence_score", 0.0)` in the transformer_only block
- [ ] `nlp_layer.py` contains `"method": "transformer_only"` in the same block
- [ ] `nlp_layer.py` contains `deflated` or `Deflate` in the transformer_only note string
</acceptance_criteria>

## Verification

Run the benchmark in `--no-throttle` mode (all 429, transformer-only fallback):
```bash
python run_maharashtra_benchmark.py --quick --ids MH-FAKE-02 --no-throttle
```

Check the output report:
```
Style: REAL (0.9973)
Confidence: 0.5984   ← should now be ~0.6×0.9973, NOT 0.9973
```

Also verify the JSON log: open `logs/maharashtra_benchmark_*.json` and confirm:
```json
"composite_verdict": {
    "final_confidence": 0.5984,
    "method": "transformer_only"
}
```

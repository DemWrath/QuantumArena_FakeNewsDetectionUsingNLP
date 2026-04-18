---
id: POL-02
wave: 1
depends_on: []
files_modified:
  - nlp_layer.py
autonomous: true
---

# Plan POL-02: MISLEADING Fallback Guard

## Goal
Prevent the fallback path (Gemini unavailable) from ever producing a MISLEADING verdict.
MISLEADING requires semantic reasoning about what is *omitted* or *exaggerated* — capabilities
that DistilBERT does not have. When Gemini is down, only REAL or FAKE should be possible.

## Context

**Current state:** The `_build_composite_verdict()` function at `nlp_layer.py:447-477` handles
the `"error" in fact_result` branch. This branch has two tiers:
1. Heuristic detector → can return FAKE
2. Transformer-only → returns BERT's label (REAL or FAKE)

Neither tier currently produces MISLEADING, so this is technically already correct. However,
the Gemini fact-check can occasionally return a fallback response that includes `"verdict": "MISLEADING"`
*inside the error path* if the API partially succeeds (e.g. gets a response then fails on parsing).

The real issue is in the **grounded path** (lines 488-493): when Gemini IS available but
over-pedantic, it flags REAL political articles as MISLEADING for minor phrasing differences.

**Benchmark evidence:**
- POL-REAL-02 (Article 370 ruling): Gemini said MISLEADING because "Parliament's competence"
  vs "President's authority" — a phrasing nuance, not actual misinformation
- POL-REAL-03 (UK election): Gemini said MISLEADING because Reform UK won 5 seats, not 4 —
  a data error in the test set, but Gemini was right to flag it

## Tasks

### Task 1: Add confidence threshold for MISLEADING verdicts

<read_first>
- e:\QA1.0_2\nlp_layer.py   (lines 488-493 — MISLEADING branch)
</read_first>

<action>
In the MISLEADING branch (line 488), add a confidence threshold:

```python
elif gem_verdict == "MISLEADING":
    # Only accept MISLEADING if Gemini is highly confident (≥0.85).
    # Lower confidence MISLEADING verdicts on political content often reflect
    # Gemini being pedantic about phrasing rather than detecting genuine
    # deceptive framing. Downgrade to REAL with a note.
    if gem_conf >= 0.85:
        final_label = "MISLEADING"
        final_conf = gem_conf
        method = "gemini_override"
    else:
        final_label = "REAL"
        final_conf = round(gem_conf * 0.7, 4)
        method = "gemini_downgraded"
```

This prevents low-confidence MISLEADING verdicts from overriding. The ×0.7 deflation
signals reduced certainty to the UI.
</action>

<acceptance_criteria>
- [ ] Gemini MISLEADING with confidence ≥ 0.85 → MISLEADING verdict preserved
- [ ] Gemini MISLEADING with confidence < 0.85 → downgraded to REAL
- [ ] Downgraded verdict has method = "gemini_downgraded"
- [ ] Downgraded confidence is deflated (×0.7)
</acceptance_criteria>

## Verification

```bash
python -m pytest test_phase9_fallback_hardening.py -v --tb=short
```
All existing tests must pass (they don't test MISLEADING branch directly).

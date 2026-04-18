---
id: FALL-02
wave: 1
depends_on: []
files_modified:
  - nlp_layer.py
autonomous: true
---

# Plan FALL-02: Fix Broken UNVERIFIED Blend Formula

## Goal
Replace the mathematically broken UNVERIFIED blend formula in `_build_composite_verdict()`
so that a high-confidence DistilBERT FAKE signal can actually flip the verdict to FAKE,
rather than being drowned out by a hardcoded constant.

## Context
Current code (lines ~377–385 of nlp_layer.py):
```python
elif gem_verdict == "UNVERIFIED":
    style_label = style_result.get("label", "REAL")
    style_conf = style_result.get("confidence_score", 0.5)
    # Raised threshold to 0.6 to reduce false positives on political news
    blended_fake_score = (0.7 * 0.5) + (0.3 * (1.0 - style_conf if style_label == "REAL" else style_conf))
    final_label = "FAKE" if blended_fake_score > 0.60 else "REAL"
    final_conf = max(gem_conf, style_conf)
    method = "blended"
```

**The bug**: `0.7 * 0.5 = 0.35` is a fixed constant. The BERT contribution can only add
at most `0.3 * 1.0 = 0.30`, so the maximum blended score is `0.35 + 0.30 = 0.65`.
With a threshold of 0.60, BERT must be at 100% confidence just to push over the line.
In practice, the formula almost always produces REAL.

**Benchmark evidence**: MH-FAKE-01 had BERT style=FAKE confidence=0.9961. With the
old formula: `0.35 + 0.3*0.9961 = 0.649` → FAKE (barely). But MH-FAKE-02 had
BERT style=REAL confidence=0.9973 (Gemini saw UNVERIFIED). Old formula:
`0.35 + 0.3*(1-0.9973) = 0.35 + 0.0008 = 0.3508` → REAL. The formula gave
essentially zero weight to one of BERT's most confident signals.

## Tasks

### Task 1: Replace the UNVERIFIED blend formula

<read_first>
- e:\QA1.0_2\nlp_layer.py  (lines 377–399 — the full UNVERIFIED elif block and beyond)
</read_first>

<action>
Find and replace the entire `elif gem_verdict == "UNVERIFIED":` block. The CURRENT
block to replace (exact text):

```python
    elif gem_verdict == "UNVERIFIED":
        # Blend: Gemini couldn't confirm either way — let transformer style vote
        style_label = style_result.get("label", "REAL")
        style_conf = style_result.get("confidence_score", 0.5)
        # Raised threshold to 0.6 to reduce false positives on political news
        blended_fake_score = (0.7 * 0.5) + (0.3 * (1.0 - style_conf if style_label == "REAL" else style_conf))
        final_label = "FAKE" if blended_fake_score > 0.60 else "REAL"
        final_conf = max(gem_conf, style_conf)
        method = "blended"
```

Replace with:

```python
    elif gem_verdict == "UNVERIFIED":
        # Blend: Gemini couldn't confirm either way — let BERT break the tie.
        # Formula: 40% weight to Gemini's uncertainty (fixed 0.5), 60% to BERT fake signal.
        # This means BERT can genuinely swing the verdict — unlike the old formula
        # where 0.7*0.5=0.35 was a near-unmovable anchor.
        style_label = style_result.get("label", "REAL")
        style_conf = style_result.get("confidence_score", 0.5)
        # bert_fake_prob: probability this sample is fake-style prose (0→1)
        bert_fake_prob = style_conf if style_label == "FAKE" else (1.0 - style_conf)
        blended_fake_score = (0.4 * 0.5) + (0.6 * bert_fake_prob)
        final_label = "FAKE" if blended_fake_score > 0.55 else "REAL"
        final_conf = round(blended_fake_score, 4)
        method = "blended"
```

Key changes:
- Weights: 0.7/0.3 → 0.4/0.6 (BERT now has majority vote)
- `bert_fake_prob` named variable replaces the inline ternary (readability)
- Threshold: 0.60 → 0.55 (recentered for the new weight distribution)
- `final_conf = max(gem_conf, style_conf)` → `final_conf = round(blended_fake_score, 4)`
  (conf should reflect the blended decision, not whichever raw score was higher)
</action>

<acceptance_criteria>
- [ ] `nlp_layer.py` contains `bert_fake_prob = style_conf if style_label == "FAKE" else (1.0 - style_conf)`
- [ ] `nlp_layer.py` contains `blended_fake_score = (0.4 * 0.5) + (0.6 * bert_fake_prob)`
- [ ] `nlp_layer.py` contains `final_label = "FAKE" if blended_fake_score > 0.55 else "REAL"`
- [ ] `nlp_layer.py` does NOT contain `(0.7 * 0.5)`
- [ ] `nlp_layer.py` does NOT contain `blended_fake_score > 0.60`
</acceptance_criteria>

## Verification

Run a mental-model check with known values from the benchmark:
- MH-FAKE-01: style=FAKE, style_conf=0.9961  
  → bert_fake_prob=0.9961, blended=0.4*0.5 + 0.6*0.9961 = 0.2 + 0.5977 = **0.7977 → FAKE ✓**
- MH-REAL-05: style=FAKE, style_conf=0.9939 (Gemini=VERIFIED, so blended path not reached)  
  → N/A (VERIFIED takes the hard override path)
- MH-MSLEAD-03: style=REAL, style_conf=0.5799  
  → bert_fake_prob=1-0.5799=0.4201, blended=0.2 + 0.6*0.4201=0.2+0.252=**0.452 → REAL** (correct, genuinely ambiguous)

Run benchmark on FAKE category with `--no-throttle` to verify MH-FAKE-01:
```bash
python run_maharashtra_benchmark.py --quick --ids MH-FAKE-01 --no-throttle
```

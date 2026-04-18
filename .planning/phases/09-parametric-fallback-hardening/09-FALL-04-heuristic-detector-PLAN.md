---
id: FALL-04
wave: 2
depends_on: ["FALL-01", "FALL-02", "FALL-03"]
files_modified:
  - nlp_layer.py
autonomous: true
---

# Plan FALL-04: Heuristic Impossible-Claim Detector

## Goal
Add a zero-cost, zero-API heuristic function `_heuristic_signals()` that detects
physically/constitutionally impossible claims using pattern matching, and wire it into
`_build_composite_verdict()` as the first check in the Gemini-unavailable code path.

## Context
When Gemini is rate-limited (429) AND DistilBERT was fooled by formal prose, the
pipeline has no fallback signal. From the benchmark:
- MH-FAKE-01 ("statue rises from sea") — BERT says REAL 0.9961 FAKE, but if Gemini
  were unavailable it could only rely on style. The REAL/FAKE label depends on fortune.
- MH-FAKE-03 ("COVID waterborne strain, 5000 dead in 48h") — BERT says REAL 0.9903.
- MH-EDGE-01 ("Maharashtra declares independence") — BERT says REAL 0.9991.

These are physically/constitutionally impossible claims that any rule-based detector
can catch with zero API calls. The heuristic layer provides a safety net below BERT.

**Execution order** (after this plan):
```
if "error" in fact_result:
    1. _heuristic_signals() — regex patterns for impossible claims
       → if flagged: return FAKE (method="heuristic_fallback")
    2. transformer_only — DistilBERT style label (deflated confidence per FALL-03)
       → return whatever BERT said
```

## Tasks

### Task 1: Add `_heuristic_signals()` function to nlp_layer.py

<read_first>
- e:\QA1.0_2\nlp_layer.py  (lines 330–340 — the module-level singleton init block,
  to find the insertion point BEFORE `_build_composite_verdict`)
</read_first>

<action>
Insert the following function BETWEEN the module-level singleton init block (ending with
`print("[NLP Layer] Ready.")`) and the `_build_composite_verdict()` function definition.
Add two blank lines before and after:

```python
def _heuristic_signals(text: str, headline: str = None) -> Dict[str, Any]:
    """
    Zero-cost, zero-API heuristic checks.

    Catches physically/constitutionally impossible claims even when both Gemini
    and reliable BERT classification are unavailable (e.g. during rate-limit cascades).

    Returns:
        red_flags           — list of matched pattern descriptions (strings)
        heuristic_fake_signal — True if any pattern fired
        heuristic_confidence  — 0.75 if flagged (fixed), else 0.0
    """
    import re
    flags = []
    combined = f"{headline or ''} {text}".lower()

    # ── Physically or constitutionally impossible events ──────────────────────
    IMPOSSIBLE_PHRASES = [
        "risen from the sea",
        "rose from the sea",
        "floating back to shore intact",
        "miracle confirmed",
        "declares itself independent",
        "declared independence",
        "independent nation",
        "unilateral declaration of independence",
        "gifting the konkan",
        "gifting konkan coast",
        "secret treaty",
        "new currency",
        "marathi mudra",
        "applying for un membership",
        "maharashtra coastal privatisation act",
        "oceanland corp",
    ]
    for phrase in IMPOSSIBLE_PHRASES:
        if phrase in combined:
            flags.append(f"impossible_phrase: '{phrase}'")

    # ── Extreme unsourced casualty/infection counts (≥1000 in a single event) ─
    extreme_counts = re.findall(
        r'\b(\d{4,})\s*(?:people\s+)?'
        r'(?:dead|killed|deaths|fatalities|infected|in\s+\d+\s+hours?)\b',
        combined
    )
    if extreme_counts:
        flags.append(f"extreme_unsourced_casualty: {extreme_counts[0]}")

    # ── Waterborne/water-supply COVID (scientifically impossible transmission) ─
    if re.search(
        r'(waterborne|water\s+supply|tap\s+water).{0,80}'
        r'(covid|coronavirus|strain|variant|virus)',
        combined
    ):
        flags.append("impossible_pathogen_transmission: waterborne_covid")

    # ── Stacked anonymous-source markers (≥3 = red flag for fabrication) ──────
    ANON_MARKERS = [
        "anonymous", "sources say", "reportedly", "allegedly",
        "secret", "classified", "unconfirmed", "whistleblower",
    ]
    anon_count = sum(1 for m in ANON_MARKERS if m in combined)
    if anon_count >= 3:
        flags.append(f"stacked_anonymous_sourcing: {anon_count} markers found")

    return {
        "red_flags": flags,
        "heuristic_fake_signal": len(flags) > 0,
        "heuristic_confidence": 0.75 if flags else 0.0,
    }
```
</action>

<acceptance_criteria>
- [ ] `nlp_layer.py` contains `def _heuristic_signals(text: str, headline: str = None)`
- [ ] `nlp_layer.py` contains `"risen from the sea"` inside `IMPOSSIBLE_PHRASES`
- [ ] `nlp_layer.py` contains `"independent nation"` inside `IMPOSSIBLE_PHRASES`
- [ ] `nlp_layer.py` contains `waterborne_covid` in the pathogen check comment
- [ ] `nlp_layer.py` contains `heuristic_fake_signal` as a return key
- [ ] The function appears BEFORE `def _build_composite_verdict(`
</acceptance_criteria>

---

### Task 2: Update `_build_composite_verdict()` signature and error branch

<read_first>
- e:\QA1.0_2\nlp_layer.py  (lines 334–360 — _build_composite_verdict definition and error branch)
- After FALL-01, FALL-02, FALL-03 have been applied to this file
</read_first>

<action>
Replace the `def _build_composite_verdict(` line and the entire `if "error" in fact_result:`
block with the version below. The CURRENT function signature is:

```python
def _build_composite_verdict(style_result: Dict, fact_result: Dict) -> Dict[str, Any]:
```

Replace with:

```python
def _build_composite_verdict(
    style_result: Dict,
    fact_result: Dict,
    text: str = "",
    headline: str = None,
) -> Dict[str, Any]:
```

Then replace the CURRENT `if "error" in fact_result:` block (which after FALL-03 looks like):

```python
    if "error" in fact_result:
        style_label = style_result.get("label", "REAL")
        raw_conf = style_result.get("confidence_score", 0.0)
        return {
            "final_label": style_label,
            "final_confidence": round(raw_conf * 0.6, 4),
            "method": "transformer_only",
            "note": (...)
        }
```

Replace with:

```python
    if "error" in fact_result:
        # ── Tier 1: Heuristic impossible-claim detector (zero API) ───────────
        # Catches physically/constitutionally impossible claims that BERT
        # cannot detect because they are written in formal journalistic prose.
        heuristics = _heuristic_signals(text, headline)
        if heuristics["heuristic_fake_signal"]:
            return {
                "final_label": "FAKE",
                "final_confidence": heuristics["heuristic_confidence"],
                "method": "heuristic_fallback",
                "red_flags": heuristics["red_flags"],
                "note": (
                    "Gemini unavailable. Heuristic pattern detector fired — "
                    f"impossible/fabricated claim indicators: {heuristics['red_flags']}"
                ),
            }

        # ── Tier 2: DistilBERT style-pattern fallback ─────────────────────────
        # Last resort — reflects prose style, not factual accuracy.
        # Confidence is deflated (×0.6) because style-match ≠ fake-news probability.
        style_label = style_result.get("label", "REAL")
        raw_conf = style_result.get("confidence_score", 0.0)
        return {
            "final_label": style_label,
            "final_confidence": round(raw_conf * 0.6, 4),
            "method": "transformer_only",
            "note": (
                "Gemini fact-check unavailable. Style-pattern label used as fallback. "
                f"Raw style confidence {raw_conf:.4f} deflated ×0.6 — style-match "
                "probability is not equivalent to fake-news probability."
            ),
        }
```
</action>

<acceptance_criteria>
- [ ] `nlp_layer.py` `_build_composite_verdict` signature contains `text: str = ""`
- [ ] `nlp_layer.py` `_build_composite_verdict` signature contains `headline: str = None`
- [ ] `nlp_layer.py` contains `heuristics = _heuristic_signals(text, headline)` inside the error branch
- [ ] `nlp_layer.py` contains `"method": "heuristic_fallback"` as a possible return
- [ ] `nlp_layer.py` contains `"method": "transformer_only"` as the fallback after heuristics
- [ ] `nlp_layer.py` `heuristic_fallback` return contains `"red_flags": heuristics["red_flags"]`
</acceptance_criteria>

---

### Task 3: Update the call site in `run_nlp_layers()` to pass `text` and `headline`

<read_first>
- e:\QA1.0_2\nlp_layer.py  (lines 425–435 — the composite verdict call in run_nlp_layers)
</read_first>

<action>
Find the line:
```python
    output["composite_verdict"] = _build_composite_verdict(output["style_classification"], fact_result)
```

Replace with:
```python
    output["composite_verdict"] = _build_composite_verdict(
        output["style_classification"],
        fact_result,
        text=text,
        headline=headline,
    )
```

This passes `text` and `headline` through to the heuristic detector. Both variables
are already available in `run_nlp_layers()` scope.
</action>

<acceptance_criteria>
- [ ] `nlp_layer.py` contains `_build_composite_verdict(` with `text=text,` as a keyword argument
- [ ] `nlp_layer.py` contains `headline=headline,` in the same call
- [ ] The single-line call `_build_composite_verdict(output["style_classification"], fact_result)` no longer exists
</acceptance_criteria>

## Verification

### Unit-level: test heuristic detector in isolation
```bash
python -c "
import sys; sys.path.insert(0, '.')
from nlp_layer import _heuristic_signals

# Should fire
h1 = _heuristic_signals('the statue rose from the sea in a miracle confirmed event')
assert h1['heuristic_fake_signal'] == True, f'Expected True, got {h1}'
assert len(h1['red_flags']) > 0

# Should fire on independence claim
h2 = _heuristic_signals('Maharashtra declares itself independent nation')
assert h2['heuristic_fake_signal'] == True

# Should NOT fire on normal news
h3 = _heuristic_signals('The government announced a new housing scheme for rural areas.')
assert h3['heuristic_fake_signal'] == False, f'Expected False, got {h3}'

print('All heuristic detector assertions passed.')
"
```

### Integration: benchmark with throttle disabled (forces transformer_only path)
```bash
python run_maharashtra_benchmark.py --quick --ids MH-EDGE-01 MH-FAKE-03 --no-throttle
```

Expected (MH-EDGE-01: "Maharashtra declares itself independent nation"):
```
Predicted: FAKE    method: heuristic_fallback
```

Expected (MH-FAKE-03: "COVID-19 found in water supply; death toll 5000"):
```
Predicted: FAKE    method: heuristic_fallback
```

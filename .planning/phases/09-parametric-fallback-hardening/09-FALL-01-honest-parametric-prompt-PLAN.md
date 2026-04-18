---
id: FALL-01
wave: 1
depends_on: []
files_modified:
  - nlp_layer.py
autonomous: true
---

# Plan FALL-01: Honest Parametric Prompt

## Goal
Replace the misleading "live web search was unavailable" fallback evidence string with a
dedicated parametric verdict prompt that honestly tells Gemini to use training knowledge
and gives it explicit rules for classifying physically impossible claims as FABRICATED.

## Context
When Gemini Search (Step 1 of `fact_check()`) fails with a 429, the code currently sets:
```python
evidence_summary = (
    "Note: Live web search was unavailable. Analysis below is based on "
    "model training knowledge only; may not reflect current events.\n\n"
    f"Text: {text[:1000]}"
)
```
Then it fires Step 2 with a `verdict_prompt` that says:
> "Evidence Research (from live web search): [above hollow string]"

This is a lie. Gemini reads "from live web search" and the hollow evidence, hedges, and
returns UNVERIFIED for everything — even physically impossible claims.

## Tasks

### Task 1: Add search-failure detection flag inside `fact_check()`

<read_first>
- e:\QA1.0_2\nlp_layer.py  (lines 160–260 — the full fact_check method)
</read_first>

<action>
In `fact_check()`, after the `except Exception as e:` block that catches the failed
search (currently lines ~213–219), replace the existing `evidence_summary` assignment
with a sentinel flag that will drive Step 2's prompt selection. The new except block:

```python
        except Exception as e:
            print(f"[FactCheck] Search grounding failed ({e}). Using parametric fallback.")
            evidence_summary = ""          # empty — signals parametric path
            grounding_sources = []         # no sources
```

The `evidence_summary = ""` (empty string instead of the hollow disclaimer) is the
key change — Step 2 will branch on `len(grounding_sources) == 0` to pick the right prompt.
</action>

<acceptance_criteria>
- [ ] `nlp_layer.py` `fact_check()` except block sets `evidence_summary = ""`
- [ ] The old string `"Note: Live web search was unavailable"` does NOT appear anywhere in nlp_layer.py
</acceptance_criteria>

---

### Task 2: Add separate parametric verdict prompt in `fact_check()` Step 2

<read_first>
- e:\QA1.0_2\nlp_layer.py  (lines 221–259 — Step 2 verdict generation)
</read_first>

<action>
Replace the single `verdict_prompt` string with a conditional that selects between
a search-grounded prompt and a parametric (training-knowledge) prompt based on whether
`grounding_sources` is populated:

```python
        # ── Step 2: Structured verdict from evidence ──────────────────────────
        if grounding_sources:
            # Normal path: evidence came from live search
            verdict_prompt = f"""
You are a senior fact-checking editor. Based on the evidence research below,
produce a structured verdict on the original text.

Evidence Research (from live web search):
{evidence_summary}

Original Text:
\"{text[:1000]}\"

Your verdict MUST be exactly one of:
- VERIFIED: Key claims are corroborated by credible sources found in search.
- UNVERIFIED: Claims could not be confirmed or denied through available search results.
- MISLEADING: Claims mix real facts with distortions; partial truth used deceptively.
- FABRICATED: Claims describe events that are physically impossible, scientifically
  impossible, or directly contradicted by search results/established facts.

Base your verdict on the EVIDENCE RESEARCH above, not on your training data alone.
"""
        else:
            # Parametric path: search was unavailable — use training knowledge honestly
            verdict_prompt = f"""
You are a senior fact-checking editor. Live web search is unavailable.
Use your training knowledge to assess the following text.

Apply these classification rules strictly:
- FABRICATED: The text describes events that are physically impossible, scientifically
  impossible, or constitutionally impossible. Examples: a state declaring independence,
  a statue rising from the ocean on its own, a waterborne COVID strain killing thousands
  in 48 hours, a government secretly gifting its coastline to a foreign company.
- MISLEADING: The text contains real events but uses exaggerated numbers, wrong
  attributions, outdated facts, or selective omissions that create a false impression.
- UNVERIFIED: The text makes specific, plausible claims that you cannot confidently
  confirm or deny from training knowledge alone.
- VERIFIED: The text describes well-known, broadly corroborated facts from your
  training knowledge.

Text:
\"{text[:1500]}\"
"""
```

The `if grounding_sources:` / `else:` structure must wrap ONLY the prompt string
assignment. The `self.client.models.generate_content(...)` call remains the same for
both paths.
</action>

<acceptance_criteria>
- [ ] `nlp_layer.py` contains `if grounding_sources:` immediately before `verdict_prompt = f"""`
- [ ] `nlp_layer.py` contains `else:` branch with `parametric path` comment
- [ ] `nlp_layer.py` contains `Live web search is unavailable.` in the else branch
- [ ] `nlp_layer.py` contains `constitutionally impossible` in the else branch
- [ ] The string `Evidence Research (from live web search)` appears ONLY in the `if grounding_sources:` branch
</acceptance_criteria>

---

### Task 3: Mark `search_grounded=False` explicitly in the parametric result

<read_first>
- e:\QA1.0_2\nlp_layer.py  (lines 250–260 — result dict construction after Step 2)
</read_first>

<action>
After `result = json.loads(verdict_response.text)`, add an explicit `search_grounded`
field derived from whether sources were found:

```python
            result = json.loads(verdict_response.text)
            result["grounding_sources"] = grounding_sources
            result["evidence_summary"] = evidence_summary
            result["search_grounded"] = len(grounding_sources) > 0   # ← already present, keep
```

This line already exists but verify it's `len(grounding_sources) > 0` — not hardcoded True.
No code change needed if already correct. This task is a verification-only step.
</action>

<acceptance_criteria>
- [ ] `nlp_layer.py` contains `result["search_grounded"] = len(grounding_sources) > 0`
</acceptance_criteria>

## Verification

Run the benchmark on a FAKE sample with the API key removed or throttled:
```bash
python run_maharashtra_benchmark.py --quick --ids MH-FAKE-01 --no-throttle
```
Expected: Gemini fires parametric path (no search grounding), returns FABRICATED for
the "statue risen from sea" claim, result is FAKE. Check log for:
```
[FactCheck] Search grounding failed (...). Using parametric fallback.
```
and verify `search_grounded=False` in the output JSON.

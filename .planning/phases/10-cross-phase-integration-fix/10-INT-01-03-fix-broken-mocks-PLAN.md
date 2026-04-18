---
id: INT-01-03
wave: 1
depends_on: []
files_modified:
  - test_app.py
  - test_nlp_layer.py
autonomous: true
gap_closure: true
closes:
  - API-01
  - API-02
---

# Plan INT-01-03: Fix Broken Mock Patches and Stale Assertions

## Goal
Repair the 4 test failures caused by Phase 8 renaming `pipeline` to `hf_pipeline` in
`nlp_layer.py`, and update the stale error-message assertion and incomplete mock return value
in `test_app.py`. This restores the full test suite to 37/37 green.

## Context

**Root cause of failures:**
- Phase 8 changed `from transformers import pipeline as hf_pipeline` in `nlp_layer.py`,
  replacing the name `pipeline` with `hf_pipeline`.
- `test_app.py` and `test_nlp_layer.py` still use `patch("nlp_layer.pipeline")` —
  this attribute no longer exists, causing `AttributeError` on test setup.
- `test_app.py` mock pipeline return value did not include a `media_bias` key,
  causing `app.py` to raise `KeyError: 'media_bias'` → 500 on the mocked route.
- `test_app.py` asserts the old error string `"No threat payload supplied"` but
  `app.py` now returns `"No input supplied. Provide 'url' or 'text'."`.

**Current failing tests:**
```
test_app.py::test_analyze_route_no_payload     FAILED
test_app.py::test_analyze_route_mocked_pipeline FAILED
test_nlp_layer.py::test_distilbert_empty_text   FAILED
test_nlp_layer.py::test_distilbert_success      ERROR
```

## Tasks

### Task 1: Fix mock patches in test_app.py (INT-01 + INT-02 + INT-03)

<read_first>
- e:\QA1.0_2\test_app.py   (read entire file — all patches, fixtures, and assertions)
- e:\QA1.0_2\app.py        (lines 50-56 — what keys app.py reads from pipeline result)
- e:\QA1.0_2\pipeline.py   (lines 28-32 — what execute_pipeline actually returns)
</read_first>

<action>
Open `test_app.py`. Find every occurrence of:
```python
@patch("nlp_layer.pipeline")
```
or
```python
with patch("nlp_layer.pipeline")
```
and change `pipeline` to `hf_pipeline` in each:
```python
@patch("nlp_layer.hf_pipeline")
```

Next, find the mock return value that `execute_pipeline` is set to return.
It currently returns a dict that produces a 500 because `media_bias` is missing.
Update it to include all three keys that `app.py` reads (lines 53-55):
```python
mock_execute.return_value = {
    "nlp_analysis": {"composite_verdict": {"final_label": "REAL", "final_confidence": 0.9}},
    "media_bias": {"bias_score": 0.1, "label": "Center"},
    "source_intelligence": {"domain": "test.com", "reputation": "unknown"},
}
```

Finally, find the assertion that checks the 400 error body:
```python
assert b'No threat payload supplied' in response.data
```
Replace with:
```python
assert b'No input supplied' in response.data
```
</action>

<acceptance_criteria>
- [ ] `test_app.py` contains NO occurrence of `nlp_layer.pipeline` (all renamed to `nlp_layer.hf_pipeline`)
- [ ] `test_app.py` mock return value for `execute_pipeline` contains `"media_bias"` key
- [ ] `test_app.py` mock return value for `execute_pipeline` contains `"nlp_analysis"` key
- [ ] `test_app.py` mock return value for `execute_pipeline` contains `"source_intelligence"` key
- [ ] `test_app.py` does NOT contain `b'No threat payload supplied'`
- [ ] `test_app.py` contains `b'No input supplied'`
</acceptance_criteria>

---

### Task 2: Fix mock patch in test_nlp_layer.py (INT-01)

<read_first>
- e:\QA1.0_2\test_nlp_layer.py  (lines 5-20 — the mock_transformers_pipeline fixture)
</read_first>

<action>
Find the fixture:
```python
@pytest.fixture
def mock_transformers_pipeline():
    with patch("nlp_layer.pipeline") as mock_pipe:
```

Change `"nlp_layer.pipeline"` to `"nlp_layer.hf_pipeline"`:
```python
@pytest.fixture
def mock_transformers_pipeline():
    with patch("nlp_layer.hf_pipeline") as mock_pipe:
```

That is the only change needed in this file.
</action>

<acceptance_criteria>
- [ ] `test_nlp_layer.py` contains `patch("nlp_layer.hf_pipeline")` in the fixture
- [ ] `test_nlp_layer.py` does NOT contain `patch("nlp_layer.pipeline")`
</acceptance_criteria>

## Verification

Run the previously-failing tests to confirm all 4 are now green:
```bash
python -m pytest test_app.py test_nlp_layer.py -v --tb=short
```

Expected output:
```
test_app.py::test_analyze_route_no_payload       PASSED
test_app.py::test_analyze_route_mocked_pipeline  PASSED
test_nlp_layer.py::test_distilbert_empty_text    PASSED
test_nlp_layer.py::test_distilbert_success       PASSED
```

Then run full suite to confirm no regressions:
```bash
python -m pytest test_app.py test_explain_layer.py test_nlp_layer.py test_phase9_fallback_hardening.py -v
```
Expected: `37 passed`.

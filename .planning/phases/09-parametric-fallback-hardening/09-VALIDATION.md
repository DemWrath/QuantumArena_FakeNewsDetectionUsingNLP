---
phase: 9
slug: parametric-fallback-hardening
date: 2026-04-18
nyquist_compliant: true
tests_added: 27
automated: 27
manual_only: 0
---

# Phase 9 Validation: Parametric Fallback Hardening

**Audit date:** 2026-04-18  
**Status:** ✅ NYQUIST COMPLIANT — 27/27 automated, 0 manual-only  
**Test file:** `test_phase9_fallback_hardening.py`

## Test Infrastructure

| Framework | Config | Run command |
|-----------|--------|-------------|
| pytest | rootdir: E:\QA1.0_2 | `python -m pytest test_phase9_fallback_hardening.py -v` |

## Per-Task Verification Map

### FALL-01: Honest Parametric Prompt

| Test | Description | Status |
|------|-------------|--------|
| `test_old_hollow_disclaimer_removed_from_codebase` | `"Note: Live web search was unavailable"` must not appear in nlp_layer.py | ✅ COVERED |
| `test_parametric_path_triggered_when_search_fails` | except block sets `evidence_summary=""` and `grounding_sources=[]` | ✅ COVERED |
| `test_grounded_prompt_contains_evidence_research_header` | Grounded verdict prompt contains `Evidence Research (from live web search)` | ✅ COVERED |
| `test_parametric_prompt_does_not_contain_live_web_search` | Parametric prompt contains `Live web search is unavailable` + `if grounding_sources:` branch | ✅ COVERED |
| `test_parametric_prompt_instructs_fabricated_for_impossible_claims` | Parametric prompt contains `constitutionally impossible` instruction | ✅ COVERED |
| `test_search_grounded_flag_reflects_sources` | `result["search_grounded"] = len(grounding_sources) > 0` in source | ✅ COVERED |

### FALL-02: Fixed UNVERIFIED Blend Formula

| Test | Description | Status |
|------|-------------|--------|
| `test_old_broken_formula_not_present` | `(0.7 * 0.5)` and `> 0.60` threshold not in source | ✅ COVERED |
| `test_new_formula_present` | `(0.4 * 0.5)`, `> 0.55`, `bert_fake_prob` in source | ✅ COVERED |
| `test_high_confidence_bert_fake_flips_to_fake` | BERT FAKE @0.9961 → FAKE (blended=0.7977 > 0.55) | ✅ COVERED |
| `test_high_confidence_bert_real_stays_real` | BERT REAL @0.9973 → REAL (blended=0.2016 < 0.55) | ✅ COVERED |
| `test_ambiguous_bert_stays_real` | BERT REAL @0.58 → REAL (genuinely ambiguous, blended=0.452) | ✅ COVERED |
| `test_blend_confidence_is_the_blended_score` | `final_confidence` is blended_fake_score ~0.7977, NOT max(gem,style) | ✅ COVERED |

### FALL-03: Deflated Transformer Confidence

| Test | Description | Status |
|------|-------------|--------|
| `test_confidence_deflated_by_0_6` | `final_confidence == round(raw_conf * 0.6, 4)` | ✅ COVERED |
| `test_method_is_transformer_only` | `method == "transformer_only"` in Gemini-unavailable path | ✅ COVERED |
| `test_raw_confidence_not_surfaced_directly` | Raw BERT 0.9961 ≠ final_confidence | ✅ COVERED |
| `test_note_mentions_deflation` | note field contains "deflated" or "×0.6" | ✅ COVERED |
| `test_fake_label_preserved_from_bert` | BERT FAKE label propagates through deflated path | ✅ COVERED |

### FALL-04: Heuristic Impossible-Claim Detector

| Test | Description | Status |
|------|-------------|--------|
| `test_impossible_phrase_statue_rises` | "risen from the sea" fires heuristic | ✅ COVERED |
| `test_impossible_phrase_independence_declaration` | "independent nation" / "declares itself independent" fires | ✅ COVERED |
| `test_waterborne_covid_flagged` | water_terms ∧ covid_terms (order-agnostic) fires waterborne_covid | ✅ COVERED |
| `test_extreme_casualty_flagged` | 4+ digit casualty claim fires extreme_unsourced_casualty | ✅ COVERED |
| `test_normal_news_not_flagged` | Routine factual news: heuristic_fake_signal=False, red_flags=[] | ✅ COVERED |
| `test_confidence_is_0_75_when_flagged` | heuristic_confidence == 0.75 (fixed) when any flag fires | ✅ COVERED |
| `test_stacked_anonymous_sourcing_flagged` | 3+ anon markers fires stacked_anonymous_sourcing | ✅ COVERED |
| `test_heuristic_overrides_bert_in_error_branch` | BERT REAL on impossible text → FAKE (method=heuristic_fallback) | ✅ COVERED |
| `test_transformer_only_path_reached_when_no_heuristic_signal` | No heuristic signal → method=transformer_only | ✅ COVERED |
| `test_build_composite_verdict_accepts_text_and_headline_kwargs` | Signature accepts text= and headline= without TypeError | ✅ COVERED |

## Manual-Only Items

None.

## Validation Audit 2026-04-18

| Metric | Count |
|--------|-------|
| Gaps found | 8 (all MISSING or PARTIAL) |
| Resolved | 8 |
| Escalated to manual | 0 |
| Test file generated | `test_phase9_fallback_hardening.py` |

## Regression Note

One bug found and fixed during validation:  
`_heuristic_signals()` waterborne COVID regex was directional (left→right), failing when
"covid" appeared before "water supply" in the sentence. Replaced with two independent
`re.search()` calls combined with `and` (order-agnostic). Fix committed alongside tests.

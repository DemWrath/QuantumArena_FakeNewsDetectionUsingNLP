"""
test_phase9_fallback_hardening.py
Nyquist validation tests for Phase 9: Parametric Fallback Hardening

Covers:
  FALL-01 — Honest parametric prompt (grounded vs parametric path selection)
  FALL-02 — Fixed UNVERIFIED blend formula (0.4/0.6 weights, threshold 0.55)
  FALL-03 — Deflated transformer_only confidence (raw × 0.6)
  FALL-04 — Heuristic impossible-claim detector (_heuristic_signals)
"""

import json
import pytest
from unittest.mock import patch, MagicMock

# ── Import targets ─────────────────────────────────────────────────────────────
# These imports trigger module-level singleton init, so we patch heavy deps first.

@pytest.fixture(autouse=True, scope="module")
def patch_heavy_singletons():
    """Prevent GPU model loading and Gemini client init during unit tests."""
    with patch("nlp_layer.hf_pipeline") as mock_pipe, \
         patch("nlp_layer.genai.Client") as mock_client, \
         patch("nlp_layer.os.getenv", return_value="fake_key"):
        mock_pipe_instance = MagicMock()
        mock_pipe_instance.return_value = [{"label": "LABEL_0", "score": 0.9}]
        mock_pipe.return_value = mock_pipe_instance
        mock_client.return_value = MagicMock()
        yield


# ══════════════════════════════════════════════════════════════════════════════
# FALL-01: Honest Parametric Prompt
# ══════════════════════════════════════════════════════════════════════════════

class TestFall01HonestParametricPrompt:
    """FALL-01: fact_check() uses distinct prompts for grounded vs parametric paths."""

    def test_old_hollow_disclaimer_removed_from_codebase(self):
        """FALL-01-AC1: The dishonest 'Live web search was unavailable' string must
        not appear in nlp_layer.py (it was the hollow evidence_summary that misled Gemini)."""
        import nlp_layer
        import inspect
        source = inspect.getsource(nlp_layer)
        assert "Note: Live web search was unavailable" not in source, (
            "The hollow parametric disclaimer was found in nlp_layer.py — "
            "FALL-01 may not have been applied correctly."
        )

    def test_parametric_path_triggered_when_search_fails(self):
        """FALL-01-AC2: When Gemini Search (Step 1) throws an exception, the except
        block sets evidence_summary='' and grounding_sources=[] to signal the parametric path."""
        from nlp_layer import GeminiInferenceServer
        import inspect
        source = inspect.getsource(GeminiInferenceServer.fact_check)

        # Verify the new empty-string sentinel is in the except block
        assert 'evidence_summary = ""' in source or "evidence_summary = ''" in source, (
            "fact_check() except block should set evidence_summary='' to signal parametric path"
        )
        assert 'grounding_sources = []' in source, (
            "fact_check() except block should reset grounding_sources to [] on search failure"
        )

    def test_grounded_prompt_contains_evidence_research_header(self):
        """FALL-01-AC3: The grounded verdict prompt must include 'Evidence Research (from live web search)'."""
        from nlp_layer import GeminiInferenceServer
        import inspect
        source = inspect.getsource(GeminiInferenceServer.fact_check)
        assert "Evidence Research (from live web search)" in source

    def test_parametric_prompt_does_not_contain_live_web_search(self):
        """FALL-01-AC4: The parametric verdict prompt must NOT claim evidence came from live search."""
        from nlp_layer import GeminiInferenceServer
        import inspect
        source = inspect.getsource(GeminiInferenceServer.fact_check)
        # The parametric prompt should contain training-knowledge language
        assert "Live web search is unavailable" in source
        # It must use if/else branching on grounding_sources
        assert "if grounding_sources:" in source

    def test_parametric_prompt_instructs_fabricated_for_impossible_claims(self):
        """FALL-01-AC5: Parametric prompt must instruct Gemini to use FABRICATED for
        physically/constitutionally impossible events."""
        from nlp_layer import GeminiInferenceServer
        import inspect
        source = inspect.getsource(GeminiInferenceServer.fact_check)
        assert "constitutionally impossible" in source, (
            "Parametric prompt should guide Gemini to flag impossible claims as FABRICATED"
        )

    def test_search_grounded_flag_reflects_sources(self):
        """FALL-01-AC6: result['search_grounded'] must be derived from len(grounding_sources) > 0."""
        from nlp_layer import GeminiInferenceServer
        import inspect
        source = inspect.getsource(GeminiInferenceServer.fact_check)
        assert 'result["search_grounded"] = len(grounding_sources) > 0' in source


# ══════════════════════════════════════════════════════════════════════════════
# FALL-02: Fixed UNVERIFIED Blend Formula
# ══════════════════════════════════════════════════════════════════════════════

class TestFall02UnverifiedBlend:
    """FALL-02: Rebalanced UNVERIFIED blend so BERT can flip verdict when confident."""

    def _get_verdict(self, style_label, style_conf, gemini_verdict="UNVERIFIED"):
        """Helper: call _build_composite_verdict with a mocked UNVERIFIED fact result."""
        from nlp_layer import _build_composite_verdict
        style_result = {"label": style_label, "confidence_score": style_conf}
        fact_result = {
            "verdict": gemini_verdict,
            "confidence": 0.5,
            "reasoning": "",
            "red_flags": [],
        }
        return _build_composite_verdict(style_result, fact_result, text="test text")

    def test_old_broken_formula_not_present(self):
        """FALL-02-AC1: The old anchored formula (0.7 * 0.5) must not be in source."""
        from nlp_layer import _build_composite_verdict
        import inspect
        source = inspect.getsource(_build_composite_verdict)
        assert "(0.7 * 0.5)" not in source, "Old broken formula still present"
        assert "blended_fake_score > 0.60" not in source, "Old threshold still present"

    def test_new_formula_present(self):
        """FALL-02-AC2: New formula with 0.4/0.6 weights and threshold 0.55 must exist."""
        from nlp_layer import _build_composite_verdict
        import inspect
        source = inspect.getsource(_build_composite_verdict)
        assert "(0.4 * 0.5)" in source
        assert "blended_fake_score > 0.55" in source
        assert "bert_fake_prob" in source

    def test_high_confidence_bert_fake_flips_to_fake(self):
        """FALL-02-AC3: BERT FAKE at 0.9961 confidence with Gemini UNVERIFIED must yield FAKE.
        Expected: (0.4*0.5) + (0.6*0.9961) = 0.2 + 0.5977 = 0.7977 > 0.55 → FAKE"""
        result = self._get_verdict("FAKE", 0.9961)
        assert result["final_label"] == "FAKE", (
            f"High-confidence BERT FAKE should flip to FAKE on UNVERIFIED, got: {result}"
        )
        assert result["method"] == "blended"
        assert result["final_confidence"] > 0.55

    def test_high_confidence_bert_real_stays_real(self):
        """FALL-02-AC4: BERT REAL at 0.9973 with Gemini UNVERIFIED must yield REAL.
        Expected: (0.4*0.5) + (0.6*(1-0.9973)) = 0.2 + 0.00162 = 0.2016 < 0.55 → REAL"""
        result = self._get_verdict("REAL", 0.9973)
        assert result["final_label"] == "REAL", (
            f"High-confidence BERT REAL should stay REAL on UNVERIFIED, got: {result}"
        )

    def test_ambiguous_bert_stays_real(self):
        """FALL-02-AC5: BERT REAL at 0.58 confidence (genuinely ambiguous) stays REAL.
        Expected: (0.4*0.5) + (0.6*(1-0.58)) = 0.2 + 0.252 = 0.452 < 0.55 → REAL"""
        result = self._get_verdict("REAL", 0.58)
        assert result["final_label"] == "REAL"

    def test_blend_confidence_is_the_blended_score(self):
        """FALL-02-AC6: final_confidence should be the blended_fake_score, not max(gem, style)."""
        result = self._get_verdict("FAKE", 0.9961)
        # Old code used max(gem_conf, style_conf) = max(0.5, 0.9961) = 0.9961
        # With new formula: blended = (0.4*0.5) + (0.6*0.9961) = 0.7977
        assert result["final_confidence"] != 0.9961, (
            "final_confidence should be the blended score, not max(gem_conf, style_conf)"
        )
        assert abs(result["final_confidence"] - 0.7977) < 0.001, (
            f"Expected blended score ~0.7977, got {result['final_confidence']}"
        )


# ══════════════════════════════════════════════════════════════════════════════
# FALL-03: Deflated Transformer Confidence
# ══════════════════════════════════════════════════════════════════════════════

class TestFall03DeflatedConfidence:
    """FALL-03: transformer_only fallback confidence is deflated ×0.6."""

    def _get_transformer_only_verdict(self, style_label, style_conf):
        """Simulate Gemini-unavailable path by passing fact_result with 'error' key."""
        from nlp_layer import _build_composite_verdict
        style_result = {"label": style_label, "confidence_score": style_conf}
        fact_result = {"error": "429 Too Many Requests"}
        # Use text that does NOT trigger heuristic signals so we reach transformer_only
        return _build_composite_verdict(
            style_result, fact_result,
            text="The government announced a new rural housing scheme.",
            headline="Government housing scheme announced"
        )

    def test_confidence_deflated_by_0_6(self):
        """FALL-03-AC1: transformer_only final_confidence must be raw_conf × 0.6."""
        result = self._get_transformer_only_verdict("REAL", 0.9973)
        expected = round(0.9973 * 0.6, 4)
        assert result["final_confidence"] == expected, (
            f"Expected deflated confidence {expected}, got {result['final_confidence']}"
        )

    def test_method_is_transformer_only(self):
        """FALL-03-AC2: method field must be 'transformer_only' in Gemini-unavailable path."""
        result = self._get_transformer_only_verdict("REAL", 0.9973)
        assert result["method"] == "transformer_only"

    def test_raw_confidence_not_surfaced_directly(self):
        """FALL-03-AC3: Raw style confidence (0.9973) must NOT equal final_confidence."""
        result = self._get_transformer_only_verdict("FAKE", 0.9961)
        assert result["final_confidence"] != 0.9961, (
            "Raw BERT confidence must be deflated — it is not a fake-news probability"
        )
        assert result["final_confidence"] < 0.65, (
            "Deflated transformer_only confidence should be below 0.65"
        )

    def test_note_mentions_deflation(self):
        """FALL-03-AC4: The note field must mention deflation so UI can display it."""
        result = self._get_transformer_only_verdict("REAL", 0.85)
        assert "deflated" in result.get("note", "").lower() or "×0.6" in result.get("note", ""), (
            "note should explain the ×0.6 deflation for UI tooltip"
        )

    def test_fake_label_preserved_from_bert(self):
        """FALL-03-AC5: BERT's FAKE label must propagate through transformer_only fallback."""
        result = self._get_transformer_only_verdict("FAKE", 0.9961)
        assert result["final_label"] == "FAKE"


# ══════════════════════════════════════════════════════════════════════════════
# FALL-04: Heuristic Impossible-Claim Detector
# ══════════════════════════════════════════════════════════════════════════════

class TestFall04HeuristicDetector:
    """FALL-04: _heuristic_signals() and its wiring into _build_composite_verdict."""

    # ── _heuristic_signals() unit tests ────────────────────────────────────────

    def test_impossible_phrase_statue_rises(self):
        """FALL-04-AC1: 'risen from the sea' triggers heuristic_fake_signal."""
        from nlp_layer import _heuristic_signals
        result = _heuristic_signals(
            "The statue reportedly risen from the sea in a miracle confirmed event.",
            headline="Shivaji statue risen from the sea"
        )
        assert result["heuristic_fake_signal"] is True
        assert any("risen from the sea" in f for f in result["red_flags"])

    def test_impossible_phrase_independence_declaration(self):
        """FALL-04-AC2: Independence declaration triggers heuristic."""
        from nlp_layer import _heuristic_signals
        result = _heuristic_signals(
            "Maharashtra declares itself independent nation; Uddhav Thackeray named President."
        )
        assert result["heuristic_fake_signal"] is True
        assert any("independent nation" in f or "declares itself independent" in f
                   for f in result["red_flags"])

    def test_waterborne_covid_flagged(self):
        """FALL-04-AC3: Waterborne COVID claim triggers impossible_pathogen_transmission.
        Detection is order-agnostic: water-supply AND covid terms anywhere in text."""
        from nlp_layer import _heuristic_signals
        result = _heuristic_signals(
            "A new waterborne strain of COVID-19 detected in Maharashtra; "
            "spreading via the water supply."
        )
        assert result["heuristic_fake_signal"] is True
        assert any("waterborne_covid" in f for f in result["red_flags"]), (
            f"Expected waterborne_covid flag. Got: {result['red_flags']}"
        )

    def test_extreme_casualty_flagged(self):
        """FALL-04-AC4: 4+ digit casualty claim triggers extreme_unsourced_casualty."""
        from nlp_layer import _heuristic_signals
        result = _heuristic_signals("Reports claim 5000 dead in the region within 48 hours.")
        assert result["heuristic_fake_signal"] is True
        assert any("extreme_unsourced_casualty" in f for f in result["red_flags"])

    def test_normal_news_not_flagged(self):
        """FALL-04-AC5: Routine factual news must NOT trigger heuristic."""
        from nlp_layer import _heuristic_signals
        result = _heuristic_signals(
            "The Maharashtra government announced a new rural housing scheme for Pune district.",
            headline="Government housing scheme for rural Maharashtra"
        )
        assert result["heuristic_fake_signal"] is False
        assert result["red_flags"] == []
        assert result["heuristic_confidence"] == 0.0

    def test_confidence_is_0_75_when_flagged(self):
        """FALL-04-AC6: Heuristic confidence must be 0.75 (fixed) when a flag fires."""
        from nlp_layer import _heuristic_signals
        result = _heuristic_signals("Maharashtra declares itself independent nation.")
        assert result["heuristic_confidence"] == 0.75

    def test_stacked_anonymous_sourcing_flagged(self):
        """FALL-04-AC7: 3+ anonymous sourcing markers trigger stacked_anonymous_sourcing."""
        from nlp_layer import _heuristic_signals
        result = _heuristic_signals(
            "Anonymous sources say the classified treaty was allegedly signed. "
            "Whistleblower claims it is unconfirmed and secret."
        )
        assert result["heuristic_fake_signal"] is True
        assert any("stacked_anonymous_sourcing" in f for f in result["red_flags"])

    # ── Integration: heuristic wired into _build_composite_verdict ─────────────

    def test_heuristic_overrides_bert_in_error_branch(self):
        """FALL-04-AC8: When Gemini is unavailable AND heuristic fires, result must use
        method='heuristic_fallback' and final_label='FAKE', regardless of BERT's label."""
        from nlp_layer import _build_composite_verdict
        # BERT says REAL (as it does for these formally-written fakes), Gemini is 429
        style_result = {"label": "REAL", "confidence_score": 0.9991}
        fact_result = {"error": "429 Too Many Requests"}
        result = _build_composite_verdict(
            style_result, fact_result,
            text="Maharashtra declares itself independent nation; Uddhav Thackeray named President.",
            headline="Maharashtra declares itself independent nation"
        )
        assert result["final_label"] == "FAKE", (
            f"Heuristic should override BERT REAL when impossible claim detected. Got: {result}"
        )
        assert result["method"] == "heuristic_fallback"
        assert result["final_confidence"] == 0.75
        assert len(result.get("red_flags", [])) > 0

    def test_transformer_only_path_reached_when_no_heuristic_signal(self):
        """FALL-04-AC9: When Gemini unavailable AND heuristic does NOT fire,
        result must use method='transformer_only'."""
        from nlp_layer import _build_composite_verdict
        style_result = {"label": "FAKE", "confidence_score": 0.85}
        fact_result = {"error": "429 Too Many Requests"}
        result = _build_composite_verdict(
            style_result, fact_result,
            text="The government announced a rural housing scheme.",
            headline="Rural housing scheme announcement"
        )
        assert result["method"] == "transformer_only"

    def test_build_composite_verdict_accepts_text_and_headline_kwargs(self):
        """FALL-04-AC10: _build_composite_verdict must accept text and headline as kwargs
        without raising TypeError."""
        from nlp_layer import _build_composite_verdict
        style_result = {"label": "REAL", "confidence_score": 0.9}
        fact_result = {"error": "429 Too Many Requests"}
        # Should not raise
        result = _build_composite_verdict(
            style_result, fact_result,
            text="Normal article text here.",
            headline="Normal headline"
        )
        assert "final_label" in result
        assert "method" in result

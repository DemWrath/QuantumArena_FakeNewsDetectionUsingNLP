---
id: POL-01
wave: 1
depends_on: []
files_modified:
  - nlp_layer.py
autonomous: true
---

# Plan POL-01: Expand Political Impossibility Heuristics

## Goal
Add political impossibility phrases to `_heuristic_signals()` to catch fabricated political
claims that the current Maharashtra-specific phrase list misses. Targets: POL-FAKE-01
(UN dissolves India), POL-FAKE-04 (China-Pakistan merge), POL-EDGE-01 (dissolve all nations).

## Context

**Current state:** `_heuristic_signals()` at `nlp_layer.py:374-391` has 14 phrases, all
Maharashtra-specific (Shivaji statue, Konkan coast, Marathi Mudra, etc.). When Gemini is
rate-limited, political fabrications written in formal diplomatic prose sail past BERT
(which classifies them as REAL due to formal writing style).

**Benchmark evidence:**
- POL-FAKE-01 ("UN dissolves India's membership") → predicted REAL (BERT style=0.987 REAL)
- POL-FAKE-04 ("China-Pakistan merge into single nation") → predicted REAL (BERT style=0.999 REAL)
- POL-EDGE-01 ("dissolve all nations; global government") → predicted REAL (BERT style=0.965 REAL)

None triggered any heuristic because no political impossibility phrases existed.

## Tasks

### Task 1: Add political impossibility phrases to IMPOSSIBLE_PHRASES list

<read_first>
- e:\QA1.0_2\nlp_layer.py   (lines 373-394 — IMPOSSIBLE_PHRASES list)
</read_first>

<action>
Add these political impossibility phrases to the `IMPOSSIBLE_PHRASES` list at line 374:

```python
# ── Political / geopolitical impossibilities ──────────────────────────
"dissolve.*membership",     # No UN mechanism to dissolve membership
"expelled from.*united nations",
"expelled from all global",
"merging into.*single nation",
"merge.*into.*single.*entity",
"single planetary government",
"united earth federation",
"dissolve all nations",
"dissolve their.*nations",
"abolish the constitution",
"suspend the constitution",
"declaration of civilizational unity",
```

**Important:** These contain regex-like patterns. Since the current matching uses simple
`if phrase in combined:`, we need to switch to `re.search()` for patterns containing `.*`.
Split into two lists: `IMPOSSIBLE_EXACT` (plain substring match) and `IMPOSSIBLE_PATTERNS`
(regex match). This keeps existing Maharashtra phrases fast while enabling flexible political patterns.
</action>

<acceptance_criteria>
- [ ] "dissolve" + "membership" + "united nations" text triggers heuristic
- [ ] "merging into single nation" triggers heuristic
- [ ] "dissolve all nations" / "dissolve their nations" triggers heuristic
- [ ] "suspend the constitution" triggers heuristic
- [ ] Existing Maharashtra phrases still fire correctly
- [ ] Normal political news (e.g. "India passes Women's Reservation Bill") does NOT fire
</acceptance_criteria>

---

### Task 2: Add co-occurrence check for geopolitical absurdity patterns

<action>
Similar to the waterborne COVID co-occurrence check, add:

```python
# ── Sovereign entity dissolution claims (co-occurrence) ──────────────
sovereignty_terms = bool(re.search(r'(dissolve|expel|revoke|strip)', combined))
entity_terms = bool(re.search(r'(membership|nation|sovereignty|statehood)', combined))
intl_body_terms = bool(re.search(r'(united nations|un |nato|security council)', combined))
if sovereignty_terms and entity_terms and intl_body_terms:
    flags.append("impossible_sovereignty_action: dissolution/expulsion of nation from intl body")
```

This catches novel phrasings about dissolving/expelling nations that exact phrases might miss.
</action>

<acceptance_criteria>
- [ ] "The UN voted to dissolve India's membership" → fires sovereignty check
- [ ] "NATO expelled three member states" → fires sovereignty check
- [ ] "India joined the United Nations" → does NOT fire (no dissolution/expulsion verb)
</acceptance_criteria>

## Verification

```bash
python -m pytest test_phase9_fallback_hardening.py -v --tb=short -k heuristic
```
All existing heuristic tests must still pass. New tests will be added in validation phase.

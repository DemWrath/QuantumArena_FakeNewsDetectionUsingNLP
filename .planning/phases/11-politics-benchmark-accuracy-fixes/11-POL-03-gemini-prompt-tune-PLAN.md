---
id: POL-03
wave: 1
depends_on: []
files_modified:
  - nlp_layer.py
autonomous: true
---

# Plan POL-03: Tune Gemini Political Tolerance Prompt

## Goal
Add instructions to the Gemini grounded fact-check verdict prompt that explicitly tell it
to distinguish between *factual errors* and *minor phrasing differences* in political/legal
reporting. Reduce false MISLEADING verdicts on REAL political articles.

## Context

**Current state:** The verdict prompt at `nlp_layer.py:221-239` defines MISLEADING as:
"Claims mix real facts with distortions; partial truth used deceptively."

This is correct but too broad for political news — Gemini interprets any imprecision
(e.g. "Parliament's competence" when technically it was "President's authority on
recommendation of Council of Ministers") as "distortion."

**Benchmark evidence:**
- POL-REAL-02: Gemini flagged "Parliament had the competence to revoke it" as inaccurate
  when the court actually affirmed the President's authority. This is a nuance in Indian
  constitutional law, not disinformation.
- POL-REAL-03: Gemini correctly flagged Reform UK's seat count (4 vs 5) — this was a genuine
  data error in the test set, not a prompt issue.

## Tasks

### Task 1: Add political tolerance clause to grounded verdict prompt

<read_first>
- e:\QA1.0_2\nlp_layer.py   (lines 221-239 — grounded verdict prompt)
</read_first>

<action>
Add a clarifying paragraph to the grounded verdict prompt after the verdict definitions:

```
IMPORTANT DISTINCTION for political/legal reporting:
- Minor phrasing differences (e.g. "Parliament's competence" vs "President's authority")
  are NOT grounds for a MISLEADING verdict unless they materially change the meaning.
- If the core factual claim is correct and the article's overall direction is accurate,
  classify as VERIFIED even if peripheral details have minor imprecisions.
- Reserve MISLEADING for cases where the article deliberately frames facts to create
  a false impression — not for imprecise but non-deceptive reporting.
```
</action>

<acceptance_criteria>
- [ ] Grounded verdict prompt contains "minor phrasing differences" tolerance clause
- [ ] Prompt still correctly instructs MISLEADING for genuinely deceptive framing
- [ ] Prompt does NOT change FABRICATED/UNVERIFIED/VERIFIED definitions
</acceptance_criteria>

## Verification

This is a prompt-quality change; verification requires running the benchmark with Gemini
available. The acceptance criteria are checked via source inspection.

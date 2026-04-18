---
id: POL-04
wave: 1
depends_on: []
files_modified:
  - politics_test_set.py
autonomous: true
---

# Plan POL-04: Fix Politics Test Set Data Errors

## Goal
Correct factual errors in the politics test set that unfairly penalize the pipeline's
accuracy score. Gemini correctly identified at least one data error during the benchmark.

## Context

**Benchmark evidence:**
- POL-REAL-03 (UK election): Text says "Reform UK won 4 seats" — actual result was 5 seats.
  Gemini correctly flagged this as MISLEADING, which means the test's expected label was
  wrong (it should either have correct data, or the expected should be MISLEADING).

## Tasks

### Task 1: Fix Reform UK seat count in POL-REAL-03

<read_first>
- e:\QA1.0_2\politics_test_set.py   (POL-REAL-03 body text)
</read_first>

<action>
In POL-REAL-03, change "Reform UK won 4 seats" to "Reform UK won 5 seats".
Also verify: Liberal Democrats won 72 seats ✓, SNP won 9 seats ✓, turnout ~59.9% ✓.
</action>

### Task 2: Review all REAL samples for factual accuracy

<action>
Cross-check each POL-REAL sample against primary sources:

- POL-REAL-01 (Women's Reservation Bill): 454 votes in favour ✓, September 21, 2023 ✓
- POL-REAL-02 (Article 370): CJI Chandrachud ✓, December 11, 2023 ✓,
  but "Parliament had the competence" should be refined to "the President's power
  under Article 370(3) was validly exercised" — this is the phrasing Gemini flagged
- POL-REAL-04 (France Article 49.3): March 16, 2023 ✓, 9 votes short ✓
- POL-REAL-05 (Ketanji Brown Jackson): April 7, 2022 ✓, 53-47 ✓

Fix POL-REAL-02 phrasing to be constitutionally precise so Gemini doesn't flag it.
</action>

<acceptance_criteria>
- [ ] POL-REAL-03 says "Reform UK won 5 seats" (not 4)
- [ ] POL-REAL-02 uses constitutionally precise phrasing for Article 370 abrogation
- [ ] All POL-REAL samples are factually accurate against primary sources
- [ ] Notes field updated where changes were made
</acceptance_criteria>

## Verification

```bash
python -c "from politics_test_set import POLITICS_NEWS_SAMPLES; print('OK:', len(POLITICS_NEWS_SAMPLES), 'samples loaded')"
```

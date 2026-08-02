---
completion_authority: true
status: PAE_08_IN_PROGRESS
---

# Probabilistic Analytic Engine — Current Status

## Authority

- Repository: `armpitpete/probabilistic-analytic-engine`
- Accepted PAE-07 `main`: `80f5dc738658a37a570524945b5328e5e602f7ed`
- Active issue: #15 — PAE-08
- Active branch: `pilot/pae-08-belarus-eu-2021`
- Candidate package version: `0.7.0`

## Completed

PAE now contains the accepted evidence, provenance, research-control and domain foundations plus a deterministic human-reviewed calculation engine validated by 70 tests.

## Current bounded unit

PAE-08 tests that engine on the resolved Belarus–European Union border case from 2021.

The pilot:

- freezes all calculation evidence at 10 November 2021;
- excludes later outcome records from the calculation;
- binds the evidence packet, calculation draft and review record to exact hashes;
- uses human-declared priors, likelihood ranges and dependency weights;
- requires role-separated calculation approval and result review;
- reveals the 15 November and 2 December outcome records only after the draft is frozen;
- scores the pre-cutoff result with multiclass Brier and logarithmic scores;
- tests whether the resolved hypothesis remains leading when each evidence stream is removed.

## Provisional pilot result

- resolved institutional hypothesis probability: `0.866467`;
- multiclass Brier score: `0.027109`;
- logarithmic score: `0.143331`;
- leading hypothesis matched the predeclared institutional resolution: yes;
- resolved hypothesis led all leave-one-stream-out tests: yes.

This is one retrospective test. It does not establish calibration or general accuracy.

## Safety boundary

- The outcome is institutional attribution, not judicial proof.
- Role-separated internal review is not independent external human validation.
- No live unresolved case is authorised.
- No automatic evidence collection, automatic attribution, public conclusion, publication, interface or deployment is included.

## Acceptance gate

Require:

- all 70 accepted PAE-07 tests remain green;
- all historical-pilot tests pass;
- evidence-cut and draft hashes reproduce exactly;
- every calculation source predates or equals the cutoff;
- every outcome source postdates the cutoff;
- later outcome records remain absent from calculation provenance;
- scores reproduce deterministically;
- the resolved hypothesis remains leading under every leave-one-stream-out test;
- one exact pull-request head is returned for protected review.

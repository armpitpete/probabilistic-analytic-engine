---
completion_authority: true
status: PAE_05_IN_PROGRESS
---

# Probabilistic Analytic Engine — Current Status

## Authority

- Repository: `armpitpete/probabilistic-analytic-engine`
- Accepted PAE-04 `main`: `8478d987da24553caed42de7ab323b7021e94e47`
- Active issue: #9 — PAE-05
- Active branch: `foundation/pae-05-probability-contract`

## Completed

Actions 1–19 are merged:

- evidence acquisition and information sufficiency;
- complete provenance and evidence records;
- immutable case snapshots;
- hypothesis structure and completeness;
- typed dependencies and hypothesis coverage;
- search audit and negative-evidence controls;
- configurable sufficiency and Value-of-Information ranking;
- reusable domain interface;
- state-migration-coercion module;
- sourced historical comparison library.

## Current bounded unit

PAE-05 completes action 20 with:

- prior ranges and provenance;
- exclusive and non-exclusive hypothesis controls;
- likelihood-strength bands;
- correlation and double-counting rules;
- mandatory sufficiency gates;
- probability and evidence-confidence separation;
- sensitivity plans;
- hash-linked forecast revisions;
- calibration and scoring contracts;
- update triggers;
- explicit safety locks.

## Safety boundary

The validator requires:

- `automatic_attribution_enabled: false`;
- `public_conclusion_authorised: false`;
- `calculation_mode: validator_only`.

No Bayesian calculation, live probability update, attribution, publication or deployment is included.

## Acceptance gate

Require:

- all earlier tests and commands remain green;
- invalid ranges and exclusive sums fail;
- nested hypotheses cannot be summed as exclusive;
- failed sufficiency blocks updates;
- correlation controls are mandatory;
- revision hashes and links are verified;
- unsafe enablement fails visibly;
- Python 3.12 CI validates the complete PAE foundation at one exact pull-request head.

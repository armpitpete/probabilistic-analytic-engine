---
completion_authority: true
status: PAE_03_IN_PROGRESS
---

# Probabilistic Analytic Engine — Current Status

## Authority

- Repository: `armpitpete/probabilistic-analytic-engine`
- Accepted PAE-02 `main`: `5f5b69b36ba397af5c1d5977993fd49a66a39f9b`
- Active issue: #5 — PAE-03
- Active branch: `foundation/pae-03-research-control`

## Completed

PAE now has:

- deterministic evidence acquisition;
- complete source provenance and claim-specific authority;
- immutable case snapshots;
- hypothesis registry, relationships, predictions and disconfirmers;
- legacy v0.1 and strict v0.2 case paths.

## Current bounded unit

PAE-03 adds:

- typed source-dependency relationships;
- coverage by hypothesis;
- search diary and negative-evidence records;
- strict separation of evidence of absence from search failure;
- named configurable sufficiency profiles;
- improved Value-of-Information ranking.

## Excluded

- probability calculation;
- geopolitical attribution findings;
- automated web collection;
- publication or deployment.

## Acceptance gate

Require:

- all existing tests remain green;
- typed dependencies and per-hypothesis coverage are deterministic;
- search failures never count as evidence of absence;
- profile rules visibly control sufficiency;
- v0.1, v0.2 and v0.3 fixture assessments all succeed in Python 3.12 CI;
- one exact pull-request head is returned for protected review.

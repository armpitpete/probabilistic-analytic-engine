---
completion_authority: true
status: PAE_04_IN_PROGRESS
---

# Probabilistic Analytic Engine — Current Status

## Authority

- Repository: `armpitpete/probabilistic-analytic-engine`
- Accepted PAE-03 `main`: `c9a286e12ab65092efad83157e09affdca0c7fac`
- Active issue: #7 — PAE-04
- Active branch: `foundation/pae-04-domain-migration-coercion`

## Completed

PAE now has:

- deterministic evidence acquisition;
- source provenance and claim-specific authority;
- immutable case snapshots;
- hypothesis structure and completeness checks;
- typed source dependencies and per-hypothesis coverage;
- search audit, negative-evidence states and configurable sufficiency;
- improved Value-of-Information ranking.

## Current bounded unit

PAE-04 adds:

- a reusable domain-module interface;
- the state-migration-coercion specialist module;
- ten domain evidence categories;
- fifteen diagnostic indicators with alternatives and limits;
- explicit prohibited inference jumps;
- a sourced six-case historical comparison library;
- attributed, contested, unresolved, organic and non-coercive comparison classes.

## Excluded

- probability calculation;
- automatic historical base rates;
- live geopolitical attribution findings;
- automated web collection;
- publication or deployment.

## Acceptance gate

Require:

- all existing tests remain green;
- module categories and inference guards are complete;
- disputed and unresolved cases cannot be represented as confirmed;
- every historical case has sources, counterevidence and limitations;
- the library contains non-coercive and organic comparators;
- the domain command succeeds in Python 3.12 CI;
- one exact pull-request head is returned for protected review.

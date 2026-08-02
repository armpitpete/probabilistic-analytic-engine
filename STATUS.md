---
completion_authority: true
status: PAE_02_IN_PROGRESS
---

# Probabilistic Analytic Engine — Current Status

## Authority

- Repository: `armpitpete/probabilistic-analytic-engine`
- Accepted PAE-01 `main`: `0367474e3dc5f05c92a2330f9835313c299071d0`
- Active issue: #3 — PAE-02
- Active branch: `foundation/pae-02-provenance-hypotheses`

## Completed foundation

PAE-01 delivered deterministic evidence acquisition:

1. coverage map;
2. source-dependency graph;
3. critical information gaps;
4. ranked next-search queue;
5. information-sufficiency status.

## Current bounded unit

PAE-02 adds:

- full source provenance;
- claim-specific source authority;
- stronger evidence records;
- immutable case snapshots;
- hypothesis registry and relationships;
- mixed-cause and insufficient-information requirements;
- hypothesis-completeness checks;
- predictions and disconfirmers;
- legacy v0.1 compatibility.

## Excluded

- probability calculation;
- Bayesian likelihood assignment;
- geopolitical attribution findings;
- automated web collection;
- publication or deployment.

## Acceptance gate

Require:

- all PAE-01 tests remain green;
- strict v0.2 validation passes;
- incomplete provenance and hypothesis structures fail visibly;
- deterministic snapshots change when case content changes;
- both legacy and strict fixture assessments succeed in Python 3.12 CI;
- one exact pull-request head is returned for protected review.

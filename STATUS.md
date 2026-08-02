---
completion_authority: true
status: FOUNDATION_COMPLETE
---

# Probabilistic Analytic Engine — Current Status

## Authority

- Repository: `armpitpete/probabilistic-analytic-engine`
- Completed foundation `main`: `4b2f8e239803b2a0aea407d08233e30912c90505`
- Completion record: Issue #11 / branch `foundation/pae-06-completion-record`
- Package version: `0.5.0`

## Foundation completion

All twenty accepted foundation actions are implemented and merged.

### Evidence acquisition

- evidence-requirement coverage maps;
- source-dependency graph and independence handling;
- critical information gaps;
- ranked next-search queue;
- information-sufficiency status.

### Provenance and hypotheses

- complete source provenance and content checksums;
- claim-specific source authority;
- proposition-level evidence records;
- immutable case snapshots;
- hypothesis registry, relationships and completeness checks;
- mixed-cause, ordinary-explanation and insufficient-information requirements;
- predictions and disconfirmers.

### Research control

- typed source-dependency relationships;
- coverage by hypothesis;
- search diary and negative-evidence records;
- separation of evidence of absence from search failure;
- configurable sufficiency profiles;
- improved Value-of-Information ranking.

### Domain foundation

- reusable domain-module interface;
- state-migration-coercion specialist module;
- ten evidence categories and fifteen indicators;
- explicit prohibited inference jumps;
- sourced six-case historical comparison library containing attributed, contested, unresolved, organic and non-coercive comparators.

### Probability contract

- prior ranges, provenance and assumptions;
- exclusive and non-exclusive hypothesis controls;
- likelihood-strength bands;
- correlated-evidence and double-counting rules;
- mandatory sufficiency gates;
- probability and evidence-confidence separation;
- sensitivity plans;
- immutable hash-linked forecast revisions;
- Brier, logarithmic and calibration scoring contracts;
- update triggers and audit requirements.

## Validation

The accepted PAE-05 candidate passed on Python 3.12 with:

- package installation;
- bytecode compilation;
- 54 deterministic tests;
- legacy v0.1 assessment;
- strict v0.2 assessment;
- research-control v0.3 assessment;
- state-migration-coercion domain and library validation;
- Probability Engine v0.1 contract validation.

## Safety boundary

The Probability Engine remains a contract validator only. It requires:

- `automatic_attribution_enabled: false`;
- `public_conclusion_authorised: false`;
- `calculation_mode: validator_only`.

The repository does not yet perform Bayesian updates, calculate live attribution probabilities, collect live evidence automatically, publish conclusions or deploy a service.

## Next authority gate

The foundation is complete. Any implementation of live probability calculation, automated evidence collection, user interface, publication integration or deployment requires a new bounded issue and acceptance programme.

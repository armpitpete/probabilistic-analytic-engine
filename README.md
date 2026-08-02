# Probabilistic Analytic Engine

The Probabilistic Analytic Engine (PAE) is an auditable system for comparing competing explanations, organising evidence, identifying information gaps and supporting provisional judgement under uncertainty.

It is not a black-box truth calculator.

> Collect until the important hypotheses have been fairly tested—not until the folder is large.

## Foundation capabilities

PAE now provides:

- evidence-requirement coverage maps;
- explicit source independence and typed dependency relationships;
- critical information-gap reporting;
- ranked next-search queues;
- information-sufficiency states;
- full source provenance and content checksums;
- claim-specific source authority;
- proposition-level evidence records;
- immutable case snapshots;
- hypothesis classes, actors, mechanisms, outcomes, predictions and disconfirmers;
- explicit overlapping, nested, sequential and compatible hypotheses;
- per-hypothesis supporting and contrary coverage;
- search diaries and negative-evidence records;
- configurable sufficiency profiles;
- Value-of-Information research ranking;
- reusable domain modules;
- sourced historical comparison libraries;
- a Probability Engine v0.1 contract and safety validator.

The first specialist module covers **state migration coercion**. It contains ten evidence categories, fifteen indicators, explicit inference guards and six differently classified comparison cases, including non-coercive and organic comparators.

## Probability contract

The contract validates:

- prior ranges, provenance and assumptions;
- exclusive versus nested or overlapping hypotheses;
- likelihood-strength bands;
- correlated-evidence controls;
- mandatory sufficiency gates;
- evidence-confidence separation;
- sensitivity plans;
- immutable forecast revisions;
- Brier, logarithmic and calibration scoring rules;
- update triggers.

It performs no probability calculation.

## Governing principles

- Evidence and probability remain separate.
- Repeated reporting from one underlying source counts as one evidence stream.
- Source authority is claim-specific.
- Search failure is not evidence of absence.
- Institutional attribution is not judicial proof.
- Historical similarity is not a probability calculation.
- Nested or overlapping hypotheses are not summed as exclusive.
- A failed sufficiency gate forbids probability updates.
- Motive, means and opportunity do not establish conduct, coordination or command.
- Alternative explanations and contrary evidence must be actively sought.
- Unknown and insufficient information are valid outcomes.
- Collection, analysis, public wording and publication authority remain separate.

## Commands

Assess a case:

```text
python -m pae path/to/case.json
```

Validate a domain module and historical library:

```text
python -m pae.domains path/to/module.json path/to/historical-cases.json
```

Validate a probability contract:

```text
python -m pae.probability_contract path/to/probability-contract.json
```

All commands support `--output path/to/result.json`.

## Current boundary

Automatic probability updating, attribution and public conclusions remain disabled. Enabling them requires a separately authorised implementation and acceptance programme.

## Donor systems

PAE adapts general patterns from:

- `armpitpete/story-evidence-collector` for bounded collection, provenance and deterministic validation;
- `armpitpete/thisweekinsmoke` for evidence confidence and contradiction discipline;
- `armpitpete/project-reader` for evidence-backed explanation and explicit unknown states.

Donor repositories are not modified by PAE work.

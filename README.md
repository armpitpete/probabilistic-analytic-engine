# Probabilistic Analytic Engine

The Probabilistic Analytic Engine (PAE) is an auditable system for comparing competing explanations, organising evidence, identifying information gaps and supporting provisional judgement under uncertainty.

It is not a black-box truth calculator.

> Collect until the important hypotheses have been fairly tested—not until the folder is large.

## Current capabilities

PAE provides:

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
- probability-contract validation;
- deterministic human-reviewed probability calculation.

The first specialist module covers **state migration coercion**. It contains ten evidence categories, fifteen indicators, explicit inference guards and six differently classified comparison cases, including non-coercive and organic comparators.

## Human-reviewed calculation

The calculation engine does not generate priors or likelihood assignments. Human analysts provide:

- an explicitly exclusive hypothesis group;
- prior ranges and provenance;
- evidence-specific likelihood ranges;
- source-independence groups and correlation weights;
- evidence-confidence records;
- a passed information-sufficiency gate.

A different person must approve the inputs. The engine then produces a pending-review draft with normalised estimates, sensitivity bounds and leave-one-stream-out results. A separate reviewer must accept the exact draft hash before it can enter a controlled historical pilot.

Automatic attribution, live unresolved cases and public conclusions remain disabled.

## Governing principles

- Evidence and probability remain separate.
- Repeated reporting from one underlying source counts as one evidence stream.
- Source authority is claim-specific.
- Search failure is not evidence of absence.
- Institutional attribution is not judicial proof.
- Historical similarity is not a measured base rate.
- Nested or overlapping hypotheses are not summed as exclusive.
- A failed sufficiency gate forbids probability calculation.
- Human analysts own priors and likelihood assignments.
- Calculation drafts require independent review.
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

Calculate and review a human-declared probability draft:

```text
python -m pae.calculation calculate plan.json --output draft.json
python -m pae.calculation review draft.json review.json --output review-record.json
```

## Current boundary

The calculation engine is authorised only for controlled historical pilots. Live unresolved cases, automatic evidence collection, automatic attribution, public conclusions, publication and deployment remain prohibited.

## Donor systems

PAE adapts general patterns from:

- `armpitpete/story-evidence-collector` for bounded collection, provenance and deterministic validation;
- `armpitpete/thisweekinsmoke` for evidence confidence and contradiction discipline;
- `armpitpete/project-reader` for evidence-backed explanation and explicit unknown states.

Donor repositories are not modified by PAE work.

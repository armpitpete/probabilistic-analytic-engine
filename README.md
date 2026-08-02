# Probabilistic Analytic Engine

The Probabilistic Analytic Engine (PAE) is an auditable system for comparing competing explanations, organising evidence, identifying information gaps and supporting provisional judgement under uncertainty.

It is not a black-box truth calculator.

> Collect until the important hypotheses have been fairly tested—not until the folder is large.

## Current capabilities

PAE provides evidence acquisition, provenance, hypothesis testing, research-control, domain modules, human-reviewed probability calculation and cutoff-controlled historical pilots.

The first specialist module covers **state migration coercion**.

## Human-reviewed calculation

The calculation engine does not generate priors or likelihood assignments. Human analysts provide an explicitly exclusive hypothesis group, prior ranges, evidence-specific likelihood ranges, dependency weights and a passed information-sufficiency gate.

A different role approves the inputs. The engine produces a hash-locked pending-review draft with normalised estimates, sensitivity bounds and leave-one-stream-out results. A separate review role must accept the exact draft before a historical pilot can run.

## First historical pilot

The Belarus–European Union 2021 pilot freezes evidence at **10 November 2021**, calculates without later outcome records, then scores the frozen result against a predeclared later institutional-resolution standard.

The pilot correctly kept state facilitation as the leading hypothesis after removing every individual evidence stream. It remains only one retrospective test. It is not calibration evidence, judicial proof or independent external human validation.

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
- Calculation drafts require role-separated review.
- One retrospective success does not establish calibration.
- Motive, means and opportunity do not establish conduct, coordination or command.
- Alternative explanations and contrary evidence must be actively sought.
- Unknown and insufficient information are valid outcomes.
- Collection, analysis, public wording and publication authority remain separate.

## Commands

```text
python -m pae path/to/case.json
python -m pae.domains module.json historical-cases.json
python -m pae.probability_contract probability-contract.json
python -m pae.calculation calculate plan.json --output draft.json
python -m pae.calculation review draft.json review.json --output review-record.json
python -m pae.historical_pilot evidence-cut.json plan.json review.json outcome.json --output pilot-result.json
```

## Current boundary

Live unresolved cases, automatic evidence collection, model-generated priors or likelihood assignments, automatic attribution, public conclusions, publication and deployment remain prohibited.

## Donor systems

PAE adapts general patterns from:

- `armpitpete/story-evidence-collector` for bounded collection, provenance and deterministic validation;
- `armpitpete/thisweekinsmoke` for evidence confidence and contradiction discipline;
- `armpitpete/project-reader` for evidence-backed explanation and explicit unknown states.

Donor repositories are not modified by PAE work.

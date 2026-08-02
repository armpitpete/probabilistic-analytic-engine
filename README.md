# Probabilistic Analytic Engine

The Probabilistic Analytic Engine (PAE) is an auditable system for comparing competing explanations, organising evidence, identifying information gaps and supporting provisional judgement under uncertainty.

It is not a black-box truth calculator.

> Collect until the important hypotheses have been fairly tested—not until the folder is large.

## Accepted capabilities

PAE v0.1 provides:

- coverage mapping;
- explicit source-dependency handling;
- critical information-gap reporting;
- ranked next-search queues;
- information-sufficiency states.

PAE v0.2 adds a strict case format with:

- full source provenance and content checksums;
- claim-specific source authority;
- proposition-level evidence records;
- immutable case snapshots;
- hypothesis classes, actors, mechanisms and outcomes;
- explicit hypothesis relationships;
- required predictions and disconfirmers;
- mixed-cause, ordinary-explanation and insufficient-information checks.

Legacy v0.1 cases remain supported and are labelled as legacy rather than falsely presented as v0.2-complete.

## Governing principles

- Evidence and probability remain separate.
- Repeated reporting from one underlying source counts as one evidence stream.
- Source authority is claim-specific.
- Motive, means and opportunity do not establish conduct, coordination or command.
- Alternative explanations and contrary evidence must be actively sought.
- Overlapping and mixed causes must be represented where appropriate.
- Unknown and insufficient information are valid outcomes.
- Collection, analysis, public wording and publication authority remain separate.

## Command line

```text
python -m pae path/to/case.json
```

Use `--output path/to/result.json` for a deterministic JSON assessment file.

## Current boundary

PAE does not yet calculate attribution probabilities. Probability work remains blocked until evidence structure, domain comparison and calibration contracts are complete.

## Donor systems

PAE adapts general patterns from:

- `armpitpete/story-evidence-collector` for bounded collection, provenance and deterministic validation;
- `armpitpete/thisweekinsmoke` for evidence confidence and contradiction discipline;
- `armpitpete/project-reader` for evidence-backed explanation and explicit unknown states.

Donor repositories are not modified by PAE work.

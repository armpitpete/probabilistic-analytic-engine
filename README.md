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
- Value-of-Information research ranking.

Legacy v0.1 and strict v0.2 cases remain supported. Cases using research protocol v0.3 gain the research-control outputs.

## Governing principles

- Evidence and probability remain separate.
- Repeated reporting from one underlying source counts as one evidence stream.
- Source authority is claim-specific.
- Search failure is not evidence of absence.
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

PAE does not yet calculate attribution probabilities. Probability work remains blocked until the domain comparison library and probability contract are complete.

## Donor systems

PAE adapts general patterns from:

- `armpitpete/story-evidence-collector` for bounded collection, provenance and deterministic validation;
- `armpitpete/thisweekinsmoke` for evidence confidence and contradiction discipline;
- `armpitpete/project-reader` for evidence-backed explanation and explicit unknown states.

Donor repositories are not modified by PAE work.

# Evidence Acquisition Manager v0.1

## Central rule

> Collect until the important hypotheses have been fairly tested—not until the folder is large.

## Coverage map

The coverage map evaluates each declared evidence requirement against:

- total source records;
- independent source streams;
- primary-source presence;
- contrary or mixed evidence;
- verified evidence;
- the declared target.

A source count and an independent-stream count are both shown so repetition cannot imitate corroboration.

## Source-dependency graph

Every source records:

- an `independence_group` representing its underlying evidence origin;
- optional `derived_from` links representing known copying, republication or transformation.

The validator rejects unknown parents, self-reference and dependency cycles.

The v0.1 graph is intentionally explicit. Automatic similarity detection is deferred because it could incorrectly merge genuinely independent reporting.

## Critical information gaps

For every missing or partial requirement, the manager reports the unsatisfied conditions, such as:

- another independent stream;
- primary material;
- contrary evidence;
- verified evidence.

Criticality controls ordering but does not make weak material stronger.

## Ranked next-search queue

Research options are scored only after their target requirement is declared. The score favours searches that could separate hypotheses and fill critical gaps.

Easy commentary collection should normally rank below difficult operational records when the latter could materially distinguish the explanations.

Blocked options remain in the queue but sort below reachable work with the same score.

## Information sufficiency

The sufficiency state is a stop/go input for later analysis. It is not an attribution conclusion.

A probability layer must receive both:

- the current sufficiency state;
- the complete list of remaining gaps.

It must not hide them behind a single percentage.

## Donor provenance

The design adapts general patterns from:

- Story Evidence Collector: structured evidence packs, provenance, search diaries, negative evidence and deterministic validation;
- TWIS Evidence Confidence Standard: claim/evidence separation, corroboration, contradiction and explicit change conditions;
- Project Reader: evidence-backed explanations and honest unknown states.

No donor repository was modified. No MP-specific workflow or fixture was copied into this repository.

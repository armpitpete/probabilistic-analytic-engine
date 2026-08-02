# PAE v0.1 Contract

## Purpose

PAE v0.1 determines whether an investigation has enough varied, independent and diagnostically useful information to support later probabilistic analysis.

It does not decide which hypothesis is true.

## Required outputs

Every assessment returns:

1. `coverage_map`;
2. `source_dependency_graph`;
3. `critical_information_gaps`;
4. `ranked_next_search_queue`;
5. `information_sufficiency`.

## Separation of responsibilities

### Evidence Acquisition Manager

May:

- validate case structure;
- count independent evidence streams;
- expose source derivation;
- test declared evidence requirements;
- identify missing primary, contrary or verified evidence;
- rank bounded research options through an inspectable score;
- state information sufficiency.

May not:

- infer guilt, motive, causation, coordination or command;
- calculate attribution probabilities;
- convert source reputation into truth;
- treat repetition as corroboration;
- authorise public wording, publication or deployment.

### Later probability layer

A later, separately authorised layer may consume a sufficiently researched case. It must not repair missing evidence by increasing mathematical complexity.

## Evidence requirements

Each requirement must state:

- one concrete question;
- the hypotheses it can distinguish;
- criticality from 1 to 5;
- the target number of independent evidence streams;
- whether primary evidence is required;
- whether contrary or mixed evidence is required.

## Sufficiency states

- `insufficient` — a critical requirement is empty or fewer than three independent source streams exist;
- `preliminary` — evidence exists, but a critical requirement is only partly covered;
- `developing` — critical requirements are covered, but lesser gaps remain;
- `substantial` — declared coverage is complete, but primary or contradiction coverage remains limited;
- `mature` — every declared requirement and contradiction gate is covered.

These states describe research coverage only. `mature` does not mean true, proved or publishable.

## Value-of-Information proxy

The v0.1 queue score is:

```text
3 × expected discrimination
+ 2 × requirement criticality
+ 2 × reliability potential
+ urgency
+ accessibility
+ gap bonus
− cost
```

The gap bonus is 8 for a missing requirement, 4 for a partial requirement and 0 for a covered requirement.

This score orders research work. It is not a probability, utility estimate or measure of truth.

## Controlled fixture

`fixtures/ceuta-2026-method-fixture.json` contains artificial records only. Its named hypotheses provide a realistic method shape while its evidence records establish no historical or current fact.

## Acceptance

PAE v0.1 passes when:

- the controlled fixture validates;
- dependent republications count as one independent stream;
- missing critical evidence produces `insufficient`;
- high-discrimination critical searches outrank repetitive commentary;
- duplicate IDs, broken references and dependency cycles fail visibly;
- all deterministic tests pass without network access.

# Human-Reviewed Calculation Engine v0.1

## Purpose

The calculation engine converts human-declared priors and evidence likelihood ranges into a deterministic probability draft. It does not decide what the priors or likelihoods should be.

## Human control

Two distinct human controls are required:

1. one analyst prepares the inputs and another approves them for calculation;
2. after calculation, a reviewer accepts or rejects the exact draft hash.

Acceptance authorises only a controlled historical pilot. It does not authorise a live unresolved case, public wording, publication or deployment.

## Arithmetic

For each explicitly exclusive hypothesis, the base score is:

```text
base prior × product(evidence multiplier ^ declared correlation weight)
```

Scores are normalised to total 1.

The engine also reports:

- conservative per-hypothesis sensitivity bounds;
- all-minimum and all-maximum input scenarios;
- leave-one-independence-group-out results;
- total weight used by each independence group.

The bounds are not confidence intervals. They show sensitivity to the declared input ranges.

## Dependency control

Every evidence update belongs to an independence group. The total weight of all updates in one group cannot exceed 1. Derivative reporting can therefore receive partial weight, but it cannot become multiple independent confirmations.

## Prohibited behaviour

The engine rejects:

- failed information-sufficiency gates;
- live unresolved cases;
- automatic attribution;
- public-conclusion authority;
- overlapping or nested hypotheses placed in one exclusive calculation group;
- priors that do not total 1;
- evidence assignments without provenance and rationale;
- correlation weights above the permitted group total;
- same-person preparation and approval;
- same-person preparation and post-calculation review;
- tampered calculation drafts.

## Commands

```text
python -m pae.calculation calculate plan.json --output draft.json
python -m pae.calculation review draft.json review.json --output review-record.json
```

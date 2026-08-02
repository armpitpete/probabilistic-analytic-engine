# Probability Engine v0.1 Contract

## Purpose

The Probability Engine contract defines how future probabilistic assessments must be structured, reviewed, revised and scored.

Version 0.1 is a **validator only**. It does not calculate a posterior probability, attribute conduct or authorise publication.

## Sufficiency gate

A contract declares:

- the research-sufficiency states required before updating;
- the current state;
- whether the gate passed;
- whether probability updates are allowed;
- the reason.

A failed gate always forbids probability updates. Mathematical complexity must not substitute for missing evidence.

## Priors

Each hypothesis records:

- minimum and maximum prior;
- a provisional point estimate within that range;
- provenance;
- assumptions;
- uncertainty reason.

Historical comparison may inform a prior but must not be treated as a measured base rate unless the sample and selection process justify that use.

## Hypothesis structure

Mutually exclusive hypotheses may be placed in an explicit exclusive group. Their point estimates must total one within that defined scope.

Nested, overlapping or compatible hypotheses are recorded separately. Nested or overlapping hypotheses must not be summed as though mutually exclusive.

Mixed causation may therefore have its own probability range outside a primary-attribution group.

## Likelihood strength

The contract defines bounded likelihood-multiplier bands and assignment rules. Evidence receives no strength merely because it fits a story. The analyst must state how expected the evidence would be under competing hypotheses.

The bands are judgement controls, not automatically measured likelihood ratios.

## Source dependence

Every probability workflow must:

- preserve evidence independence groups;
- prohibit double-counting;
- discount correlated evidence;
- allow no more than one full-weight contribution from one underlying evidence origin;
- record reasons for manual overrides.

## Probability and confidence

Probability answers which explanation currently appears more likely.

Evidence confidence describes the quality, independence, completeness and diagnostic strength of the information supporting that estimate.

They remain separate. A hypothesis may lead with low evidence confidence.

## Sensitivity

Every assessment tests at least:

- prior-range extremes;
- removal of the strongest evidence stream;
- alternative source-correlation assumptions;
- plausible alternative causal sequences.

The public assessment must state whether the leading conclusion changes under reasonable assumptions.

## Revision ledger

Every forecast revision contains:

- consecutive revision number;
- timestamp;
- reason;
- assessment-state checksum;
- whether probabilities changed;
- previous-revision checksum;
- canonical revision checksum.

Changing an earlier revision breaks the hash chain. Corrections require a new revision rather than silent replacement.

## Calibration and scoring

Resolved forecasts may be assessed using:

- Brier score;
- logarithmic score;
- calibration buckets;
- discrimination between resolved outcomes.

The resolution standard must be declared before scoring. Unresolved cases remain preserved but excluded from accuracy scoring.

Calibration summaries should not be interpreted until there are enough genuinely resolved forecasts. The initial threshold is twenty.

## Safety boundary

The following fields must remain false:

- `automatic_attribution_enabled`;
- `public_conclusion_authorised`.

The calculation mode must remain `validator_only`.

Enabling probability calculations requires a separately authorised, tested implementation unit after human review of this contract.

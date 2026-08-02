# Resolved-Case Calibration Programme v0.1

## Purpose

This programme tests whether PAE's human-reviewed calculations perform better than a uniform four-class baseline across a small, balanced historical corpus.

It does not authorise live use.

## Frozen corpus

The corpus contains exactly eight cases and exactly two cases in each outcome class:

- `positive` — later public institutional attribution supports deliberate state coercion;
- `negative` — later evidence supports a primarily non-coercive mechanism;
- `disputed` — materially different competent accounts remain unresolved;
- `insufficient` — the later public record cannot satisfy the declared evidentiary question.

`Insufficient` is a valid resolved assessment of the public record. It does not assert that no hidden conduct occurred.

The corpus is frozen before new probability assignments. Case substitution or reclassification requires a new programme version.

## Hindsight controls

Each case declares:

- one explicit question;
- one evidence cutoff;
- pre-cutoff source registry;
- withheld post-cutoff outcome sources;
- one resolution standard;
- one frozen outcome class.

The blinded external-review packet excludes:

- the outcome class;
- the outcome rationale;
- withheld outcome sources;
- other reviewers' scores.

Any outcome leakage is a stop condition.

## Aggregate measures

The scorer reports:

- mean multiclass Brier score;
- mean logarithmic score;
- improvement over the uniform four-class baseline;
- top-one accuracy;
- correct leading classifications by outcome class;
- expected calibration error using five fixed confidence bins;
- one-versus-rest area under the receiver operating characteristic curve;
- macro area under the curve;
- leave-one-case-out aggregate results.

The uniform baseline is:

- Brier score: `0.75`;
- logarithmic score: `ln(4)`, approximately `1.386294`;
- top-one accuracy: `0.25`.

## Predeclared pass criteria

A result may be labelled `pass_candidate` only when:

- all eight cases are present and balanced;
- no outcome leakage is detected;
- mean Brier score improves on uniform by at least `0.10`;
- mean logarithmic score improves on uniform by at least `0.15`;
- top-one accuracy is at least `0.50`;
- every outcome class contains at least one correct leading classification;
- expected calibration error is no greater than `0.20`;
- every case has at least two qualifying external reviewers;
- no review contains a critical finding or rejection;
- no review contains an unresolved major finding.

A pass candidate still requires explicit human acceptance. It never automatically authorises live use.

## Correction criteria

`correction_required` applies when performance is better than uniform but one or more pass thresholds are missed, or when an external reviewer records a major but reparable finding.

Corrections must create a new immutable programme revision. Existing results must not be overwritten.

## Stop criteria

`stop` applies when:

- outcome leakage occurs;
- the corpus is retrospectively changed without a new version;
- aggregate Brier or logarithmic performance is no better than uniform;
- an external reviewer rejects a packet;
- a critical finding remains;
- evidence provenance, dependency or reproducibility cannot be repaired.

## External review

At least two reviewers must review each case.

Each reviewer must declare:

- independence from PAE case preparation and calculation;
- no relevant financial, employment, authorship or close personal conflict;
- outcome blinding until the signed review is frozen;
- relevant affiliation and expertise;
- relevant institutional, advocacy or political commitments.

Repository validation can check that declarations exist. It cannot prove that they are true. Independent external review therefore requires real external people.

## Commands

Validate the frozen corpus:

```text
python -m pae.calibration validate-manifest calibration/corpus-v0.1.json
```

Generate an outcome-blinded review packet:

```text
python -m pae.calibration prepare-review calibration/corpus-v0.1.json --output generated/external-review-packet.json
```

Aggregate completed case results and signed reviews:

```text
python -m pae.calibration aggregate calibration/corpus-v0.1.json calibration/results-v0.1.json --output generated/calibration-report.json
```

## Current boundary

The repository can freeze the corpus, validate leakage controls, generate blinded packets and score completed externally reviewed results.

It cannot supply genuine independent reviewers or truthfully complete their declarations. Until real external review and human probability assignments are returned, aggregate calibration remains incomplete.

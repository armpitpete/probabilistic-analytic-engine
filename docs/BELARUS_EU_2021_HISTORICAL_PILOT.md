# Belarus–European Union 2021 Historical Pilot

## Purpose

This is the first controlled retrospective pilot of the human-reviewed PAE calculation engine.

It tests whether a probability draft based only on information dated on or before **10 November 2021** anticipated a later, predeclared institutional resolution standard.

It does not establish judicial truth, validate every historical allegation or authorise live use.

## Hindsight control

The calculation packet includes five public records dated from 30 July to 10 November 2021.

The following records were withheld until after the calculation draft and review were frozen:

- the Council's 15 November 2021 expansion of sanctions criteria;
- the Council's 2 December 2021 sanctions naming airlines, tour operators and hotels.

The evidence packet, calculation draft and review record are protected by SHA-256 hashes.

## Hypotheses

The pilot calculated one explicitly exclusive primary-mechanism group:

1. primarily organic movement and non-state facilitation;
2. Belarusian state facilitation as the primary organised mechanism;
3. public evidence insufficient for primary attribution.

Individual migrant motives, agency and protection needs were permitted under every hypothesis.

## Result

The frozen probability draft assigned:

| Hypothesis | Point estimate | Sensitivity bound |
|---|---:|---:|
| Primarily organic | 5.33% | 0.22%–50.70% |
| State facilitation primary | 86.65% | 26.39%–99.37% |
| Insufficient public evidence | 8.02% | 0.37%–61.25% |

The wide bounds show substantial dependence on the human-declared prior and likelihood ranges. They are not measured confidence intervals.

The state-facilitation hypothesis remained the leading explanation when each of the four independence groups was removed in turn.

## Outcome and scoring

The predeclared institutional resolution standard treated the later Council records as resolving the pilot towards state facilitation because they formally attributed political instrumentalisation and identified concrete state-linked or commercial facilitation mechanisms.

This is institutional attribution, not judicial adjudication.

The retrospective scores were:

- resolved-hypothesis probability: **0.866467**;
- multiclass Brier score: **0.027109**;
- logarithmic score: **0.143331**;
- leading hypothesis matched the resolution: **yes**;
- resolved hypothesis led every leave-one-stream-out test: **yes**.

## Review limitation

The calculation used separated internal roles for preparation, calculation approval and result review. Those labels enforce workflow separation, but they do **not** represent independent external human validation.

## Interpretation

This pilot shows that the calculation engine can:

- enforce a dated evidence cutoff;
- prevent outcome records entering the calculation;
- reproduce an immutable calculation draft;
- preserve source-dependency discounts;
- score a later predeclared resolution;
- expose sensitivity to analyst inputs.

One successful retrospective pilot cannot establish calibration, general accuracy or readiness for live unresolved cases.

## Remaining boundary

PAE remains prohibited from:

- live unresolved-case use;
- automatic evidence collection;
- model-generated priors or likelihood assignments;
- automatic attribution;
- public conclusions;
- publication or deployment.

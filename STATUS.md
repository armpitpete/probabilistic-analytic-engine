---
completion_authority: true
status: PAE_10_EXTERNAL_REVIEW_GATE
---

# Probabilistic Analytic Engine — Current Status

## Authority

- Repository: `armpitpete/probabilistic-analytic-engine`
- Accepted calculation-and-pilot programme: `a0a877066ea615ec17d5e9a1c431bd06447905f3`
- Active issue: #19 — PAE-10
- Active branch: `calibration/pae-10-resolved-case-programme`
- Candidate package version: `0.8.0`

## Completed repository work

PAE-10 now contains:

- a frozen eight-case corpus;
- exactly two positive, two negative, two disputed and two insufficient-public-information outcomes;
- predeclared evidence cutoffs, resolution standards and withheld outcome sources;
- fixed pass, correction and stop criteria;
- corpus-balance and hindsight-leakage validation;
- outcome-blinded external-review packet generation;
- external-review independence, conflict and role-separation controls;
- aggregate multiclass Brier and logarithmic scoring;
- uniform-baseline comparisons;
- top-one accuracy, expected calibration error and one-versus-rest discrimination;
- outcome-class coverage and leave-one-case-out reporting;
- machine-readable review and result schemas;
- nineteen focused regression tests.

## Frozen outcome classes

| Outcome class | Cases |
|---|---:|
| Positive institutional attribution | 2 |
| Primarily non-coercive mechanism | 2 |
| Disputed public attribution | 2 |
| Insufficient public information | 2 |

`Insufficient` describes what the public record can establish under the declared question. It does not assert that hidden conduct did not occur.

## Acceptance logic

A result can become a `pass_candidate` only if it beats the uniform four-class baseline by the frozen Brier and logarithmic margins, reaches the top-one and calibration thresholds, records at least one correct leading classification in every outcome class and contains no major, critical or rejected external review.

A pass candidate never authorises live use automatically.

## Current human gate

The repository can validate, blind and score the programme, but it cannot fabricate:

- human probability assignments for the seven additional case packets;
- two genuine independent external reviewers for every case;
- reviewer identity, expertise, conflict declarations or signatures;
- external review findings.

Independent external review must be performed by real people who did not prepare the cases or calculations and did not see the outcome labels before signing their blinded reviews.

## Safety boundary

PAE remains unauthorised for:

- live unresolved cases;
- automatic evidence collection;
- model-generated priors or likelihood assignments;
- automatic attribution;
- public conclusions;
- publication, user interface or deployment.

## Current protected gate

Complete Python 3.12 CI for the calibration infrastructure and frozen corpus. After merge, Issue #19 must remain open at the external-human-input gate until genuine case assignments and reviews are returned.

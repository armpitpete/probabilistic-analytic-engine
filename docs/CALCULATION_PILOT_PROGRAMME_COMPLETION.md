# PAE Calculation and Historical-Pilot Programme Completion

## Completion statement

The authorised programme following foundation acceptance is complete.

| Unit | Purpose | Accepted commit | Validation |
|---|---|---|---|
| PAE-07 | Human-reviewed probability calculation engine | `80f5dc738658a37a570524945b5328e5e602f7ed` | 70 tests |
| PAE-08 | Controlled Belarus–EU 2021 historical pilot | `e6856b6a6141e3a131764d4eaa48bf4c04f3480f` | 83 tests |

## What was proved

The repository can now:

- calculate normalised probability drafts from human-declared inputs;
- enforce sufficiency, exclusivity and evidence-dependency rules;
- expose sensitivity to priors, likelihood ranges and individual evidence streams;
- bind calculations and reviews to exact hashes;
- freeze a dated historical evidence cut;
- prevent later outcome records entering the calculation;
- reveal and score a predeclared institutional outcome afterwards.

## First pilot result

The 2021 Belarus–European Union pilot assigned a pre-cutoff probability of `0.866467` to state facilitation as the primary organised mechanism. The later institutional resolution matched that leading hypothesis.

The multiclass Brier score was `0.027109`; the logarithmic score was `0.143331`. The resolved hypothesis remained leading when each evidence stream was removed.

## What was not proved

The programme did not prove:

- general predictive accuracy;
- calibration across cases;
- independence from analyst judgement;
- judicial truth;
- external human acceptance;
- readiness for live unresolved cases.

The pilot used human-declared priors and likelihood ranges. Its role-separated internal review is a workflow safeguard, not independent external validation.

## Required next programme

Before live use, PAE needs:

1. a larger set of predeclared resolved historical pilots;
2. balanced positive, negative, disputed and insufficient-information cases;
3. independent external review of evidence cuts and likelihood assignments;
4. aggregate calibration and discrimination analysis;
5. explicit pass, correction and stop criteria.

No live-case, publication or deployment work is authorised by this completion record.

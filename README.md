# Probabilistic Analytic Engine

The Probabilistic Analytic Engine (PAE) is an auditable system for comparing competing explanations, organising evidence, identifying information gaps and supporting provisional judgement under uncertainty.

It is not a black-box truth calculator.

> Collect until the important hypotheses have been fairly tested—not until the folder is large.

## Current capabilities

PAE provides evidence acquisition, provenance, hypothesis testing, research control, domain modules, human-reviewed probability calculation, cutoff-controlled historical pilots, resolved-case calibration controls and outcome-blinded human workflow packets.

The first specialist module covers **state migration coercion**.

## Human-reviewed calculation

The calculation engine does not generate priors or likelihood assignments. Human analysts provide an explicitly exclusive hypothesis group, prior ranges, evidence-specific likelihood ranges, dependency weights and a passed information-sufficiency gate.

A different role approves the inputs. The engine produces a hash-locked pending-review draft with normalised estimates, sensitivity bounds and leave-one-stream-out results. A separate review role must accept the exact draft before a historical pilot can run.

## Historical pilots and calibration

The first Belarus–European Union 2021 pilot froze evidence before later outcome records and then scored the frozen result against a predeclared institutional-resolution standard.

The calibration programme uses a frozen eight-case corpus with two cases in each class:

- positive institutional attribution;
- primarily non-coercive mechanism;
- disputed public attribution;
- insufficient public information.

The calibration layer validates cutoffs and corpus balance, generates outcome-blinded external-review packets, and reports aggregate Brier, logarithmic, calibration and discrimination measures against a uniform four-class baseline.

## Analyst and external-review workflow

PAE can generate separate outcome-blinded analyst and external-review packets for every frozen case. The packets include pre-cutoff source registries, dependency and contrary-evidence worksheets, blank probability forms and structured reviewer questions.

The assignment register enforces:

- different case preparers and approvers;
- no external reviewer who prepared or approved the same case;
- at least two distinct reviewers per case;
- declared independence, absence of conflict and outcome blinding;
- explicit incomplete and complete human-workflow states.

No identities, probabilities, signatures or findings are generated automatically. Repository checks validate declarations but cannot prove that an external person is genuinely independent.

## Governing principles

- Evidence and probability remain separate.
- Repeated reporting from one underlying source counts as one evidence stream.
- Source authority is claim-specific.
- Search failure is not evidence of absence.
- Institutional attribution is not judicial proof.
- Historical similarity is not a measured base rate.
- Nested or overlapping hypotheses are not summed as exclusive.
- A failed sufficiency gate forbids probability calculation.
- Human analysts own priors and likelihood assignments.
- Calculation drafts require role-separated review.
- Outcome labels and post-cutoff records must remain hidden during external review.
- One retrospective success does not establish calibration.
- A calibration pass candidate never automatically authorises live use.
- Unknown and insufficient information are valid outcomes.
- Collection, analysis, public wording and publication authority remain separate.

## Commands

```text
python -m pae path/to/case.json
python -m pae.domains module.json historical-cases.json
python -m pae.probability_contract probability-contract.json
python -m pae.calculation calculate plan.json --output draft.json
python -m pae.calculation review draft.json review.json --output review-record.json
python -m pae.historical_pilot evidence-cut.json plan.json review.json outcome.json --output pilot-result.json
python -m pae.calibration validate-manifest calibration/corpus-v0.1.json
python -m pae.calibration prepare-review calibration/corpus-v0.1.json --output review-packet.json
python -m pae.calibration aggregate calibration/corpus-v0.1.json results.json --output calibration-report.json
python -m pae.human_workflow prepare calibration/corpus-v0.1.json --output human-workflow-bundle.json
python -m pae.human_workflow validate-register calibration/corpus-v0.1.json calibration/assignment-register-v0.1.json --output assignment-status.json
```

## Current boundary

Live unresolved cases, automatic evidence collection, model-generated priors or likelihood assignments, automatic attribution, public conclusions, publication and deployment remain prohibited.

Aggregate calibration is not complete until human probability assignments and genuine signed external reviews have been returned for the frozen corpus.

## Donor systems

PAE adapts general patterns from:

- `armpitpete/story-evidence-collector` for bounded collection, provenance and deterministic validation;
- `armpitpete/thisweekinsmoke` for evidence confidence and contradiction discipline;
- `armpitpete/project-reader` for evidence-backed explanation and explicit unknown states.

Donor repositories are not modified by PAE work.

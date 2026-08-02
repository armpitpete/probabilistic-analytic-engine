---
completion_authority: true
status: CALCULATION_PILOT_PROGRAMME_COMPLETE
---

# Probabilistic Analytic Engine — Current Status

## Authority

- Repository: `armpitpete/probabilistic-analytic-engine`
- Accepted foundation gate: `299743af54470b7035923fe372435aecbfc94786`
- Accepted human-reviewed calculation engine: `80f5dc738658a37a570524945b5328e5e602f7ed`
- Accepted first historical pilot: `e6856b6a6141e3a131764d4eaa48bf4c04f3480f`
- Package version: `0.7.0`

## Programme completion

The authorised next programme is complete:

1. a human-reviewed calculation engine was implemented and accepted;
2. the engine was tested through a cutoff-controlled resolved historical pilot before any live unresolved use.

## Calculation engine

PAE now supports deterministic normalisation of human-declared priors and likelihood ranges with:

- explicit exclusive hypothesis groups;
- mature or resolved sufficiency gates;
- dependency weights capped by evidence origin;
- sensitivity bounds and leave-one-stream-out tests;
- immutable draft hashes;
- role-separated input approval and exact-draft review.

The engine does not generate priors, likelihoods or conclusions.

## First historical pilot

The Belarus–European Union 2021 pilot froze calculation evidence at 10 November 2021 and withheld later outcome records until after the draft and review were fixed.

Result under the predeclared institutional-resolution standard:

- state-facilitation point estimate: `0.866467`;
- multiclass Brier score: `0.027109`;
- logarithmic score: `0.143331`;
- leading hypothesis matched the later institutional resolution;
- the resolved hypothesis remained leading in all leave-one-stream-out tests.

## Validation

The accepted PAE-08 candidate passed on Python 3.12 with:

- package installation;
- bytecode compilation;
- 83 deterministic tests;
- all legacy case, domain, contract and calculation commands;
- the complete historical-pilot command and output check.

## Limits

- One retrospective success does not establish calibration or general accuracy.
- The pilot outcome is institutional attribution, not judicial proof.
- Role-separated internal review is not independent external human validation.
- The reported ranges depend on human-declared priors and likelihood assignments.

## Current safety boundary

PAE is not authorised for:

- live unresolved cases;
- automatic evidence collection;
- model-generated priors or likelihood assignments;
- automatic attribution;
- public conclusions;
- publication, user interface or deployment.

## Next authority gate

Before any live unresolved use, PAE requires a larger predeclared resolved-case calibration programme, independent external review and explicit acceptance criteria. No live-case work has begun.

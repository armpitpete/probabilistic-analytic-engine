---
completion_authority: true
status: PAE_07_IN_PROGRESS
---

# Probabilistic Analytic Engine — Current Status

## Authority

- Repository: `armpitpete/probabilistic-analytic-engine`
- Accepted foundation gate: `299743af54470b7035923fe372435aecbfc94786`
- Active issue: #13 — PAE-07
- Active branch: `calculation/pae-07-human-reviewed-engine`
- Candidate package version: `0.6.0`

## Completed foundation

The accepted foundation contains evidence acquisition, provenance, hypothesis structure, research control, the state-migration-coercion domain module, a sourced comparison library and the Probability Engine v0.1 safety contract.

## Current bounded unit

PAE-07 implements a human-reviewed calculation engine that:

- accepts only an explicitly exclusive hypothesis group;
- requires human-declared priors, likelihood ranges, provenance and assumptions;
- requires a passed mature or resolved information-sufficiency gate;
- applies declared correlation weights without allowing one independence group to exceed one unit of total weight;
- normalises base posterior estimates;
- reports conservative sensitivity bounds and leave-one-stream-out results;
- creates an immutable draft hash;
- requires a reviewer other than the calculation preparer to accept or reject the exact draft.

## Safety boundary

PAE-07 rejects:

- live unresolved cases;
- automatic attribution;
- public-conclusion authority;
- model-generated evidence weights;
- overlapping or nested hypotheses in one exclusive group;
- failed sufficiency gates;
- same-person preparation and review;
- tampered drafts.

No historical pilot, public conclusion, automated collection, publication, user interface or deployment is included in PAE-07.

## Acceptance gate

Require:

- all 54 accepted foundation tests remain green;
- the new focused calculation tests pass;
- the command-line calculation fixture succeeds on Python 3.12;
- generated probabilities total one;
- sensitivity bounds contain the base point estimates;
- dependency overweighting and unsafe modes fail visibly;
- independent review is tied to the exact draft hash;
- one exact pull-request head is returned for protected review.

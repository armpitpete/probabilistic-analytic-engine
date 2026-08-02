---
completion_authority: true
status: PAE_11_PACKET_MOBILISATION_IN_PROGRESS
---

# Probabilistic Analytic Engine — Current Status

## Authority

- Repository: `armpitpete/probabilistic-analytic-engine`
- Accepted PAE-10 infrastructure: `4030ef0b70747a4684be6708da0c10dbfaf81d9e`
- Parent calibration programme: Issue #19
- Active bounded unit: Issue #21 — PAE-11
- Active branch: `workflow/pae-11-human-packets`
- Candidate package version: `0.9.0`

## Accepted calibration infrastructure

PAE contains a frozen eight-case corpus with exactly two positive, two negative, two disputed and two insufficient-public-information outcomes, plus fixed pass, correction and stop criteria, leakage controls, aggregate scoring and external-review schemas.

## Current bounded unit

PAE-11 turns that infrastructure into a usable human workflow by providing:

- one outcome-blinded analyst packet per frozen case;
- one outcome-blinded external-review packet per frozen case;
- blank probability forms with no suggested values;
- source-authority and dependency worksheets;
- contrary-evidence and negative-search records;
- analyst preparation and approval roles;
- a blank assignment register covering all eight cases;
- reviewer independence, conflict and outcome-blinding declarations;
- an external-review invitation template;
- assignment-register validation;
- role-overlap and duplicate-reviewer rejection;
- a complete-workflow gate requiring two reviewers per case;
- deterministic tests and command-line validation.

## Human gate preserved

The workflow intentionally contains no invented:

- analysts;
- probability assignments;
- approvers;
- external reviewers;
- affiliations or expertise;
- signatures;
- findings.

A blank register is valid but incomplete. A completed register still does not authorise live use.

## Safety boundary

PAE remains unauthorised for:

- live unresolved cases;
- automatic evidence collection;
- model-generated priors or likelihood assignments;
- automatic attribution;
- public conclusions;
- publication, user interface or deployment.

## Acceptance gate

Require:

- all 102 accepted tests remain green;
- all new human-workflow tests pass;
- outcome fields remain absent from generated packets;
- no probability suggestions appear;
- blank assignment-register validation succeeds as incomplete;
- invalid role overlap, conflicts and inadequate reviewer counts fail visibly;
- Python 3.12 produces the workflow bundle and register-status outputs;
- one exact pull-request head is returned for protected review.

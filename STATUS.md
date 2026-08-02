---
completion_authority: true
status: REVIEWER_INTAKE_IMPLEMENTATION_IN_PROGRESS
---

# Probabilistic Analytic Engine — Current Status

## Authority

- Repository: `armpitpete/probabilistic-analytic-engine`
- Accepted calibration infrastructure: `4030ef0b70747a4684be6708da0c10dbfaf81d9e`
- Accepted analyst and external-review workflow: `b7077ea6c5d750899df62ed689e98ced4fb31103`
- Accepted outreach and recruitment record: `a747b62ec0bf32b4a93e9eb9978748b9273b5193`
- Parent calibration programme: Issue #19 — open
- Active bounded unit: Issue #27 — PAE-14
- Active branch: `workflow/pae-14-reviewer-intake`
- Candidate package version: `0.10.0`

## Outreach state

First-wave institutional requests were sent on 2 August 2026 to migration-domain, reproducibility, statistical and research-integrity channels. No reviewer has been appointed, no case packet has been released and no payment or contractual commitment has been made.

## Current bounded unit

PAE-14 prepares the response-intake and packet-handoff path by adding:

- reviewer-candidate intake records;
- explicit expertise and proposed-role fields;
- independence, conflict, source-authorship and outcome-exposure declarations;
- eligible, needs-clarification, unsuitable and withdrawn states;
- refusal of packet release before the eligibility gate passes;
- case-specific exclusion controls;
- an authenticated packet-release checklist;
- delivery and return-record requirements;
- reply, clarification, follow-up and decline templates;
- a machine-readable schema, command-line validator and deterministic tests.

Institutional affiliation, prestige or agreement with PAE cannot substitute for individual screening.

## Human evidence still required

Issue #19 cannot be completed until real people provide:

1. human probability assignments and approval for the seven additional case packets;
2. at least two genuine external reviewers for every case;
3. verified reviewer identity, affiliation, expertise and conflict declarations;
4. signed outcome-blinded review records;
5. external findings and any required corrections;
6. a completed result bundle for aggregate scoring;
7. an explicit human accept, correct or stop decision.

## Safety boundary

PAE remains unauthorised for:

- releasing a packet to an unscreened person;
- live unresolved cases;
- automatic evidence collection;
- model-generated priors or likelihood assignments;
- automatic attribution;
- public conclusions;
- publication, user interface or deployment.

## Acceptance gate

Require:

- all 118 accepted tests remain green;
- reviewer intake and release tests pass;
- hard conflicts and outcome exposure block release;
- source authorship requires case-specific clarification;
- institutional affiliation cannot replace concrete expertise;
- case exclusions block only the affected case;
- Python 3.12 produces candidate and packet-release records;
- one exact pull-request head is returned for protected review.

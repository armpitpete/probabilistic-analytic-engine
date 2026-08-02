# Outcome-Blinded Packet Handoff Protocol

## Purpose

Deliver one historical case packet to an eligible reviewer without disclosing the frozen outcome or weakening the audit trail.

## Before release

Require all of the following:

1. The candidate intake record validates as `eligible`.
2. The candidate is not excluded from the selected case.
3. The person did not prepare or approve that case.
4. Case-specific source authorship, advisory work and prior exposure have been checked.
5. The reviewer declaration has been authenticated.
6. The packet has been regenerated from the accepted corpus version.
7. The packet contains no outcome class, outcome rationale or withheld outcome source.
8. A SHA-256 checksum has been recorded for the exact packet.

## Delivery record

Record:

- candidate identifier;
- case identifier;
- delivery date and time;
- delivery channel;
- exact packet filename;
- packet SHA-256 checksum;
- corpus version and accepted commit;
- return deadline;
- sender;
- whether receipt was confirmed.

Do not record hidden outcome information in the delivery message or filename.

## Approved delivery characteristics

Use a private, access-controlled channel that provides an inspectable record of delivery and return. The channel must not expose the packet publicly or place it in a shared location accessible to outcome-aware participants.

Do not send secrets, passwords or access tokens inside the packet. Do not promise legal confidentiality unless a separately reviewed agreement exists.

## Reviewer return

The returned record must contain:

- the candidate identifier and case identifier;
- the packet checksum reviewed;
- the completed independence and conflict declaration;
- structured answers and findings;
- finding severity;
- an accept, accept-with-minor-comments or reject decision;
- date and authenticated confirmation;
- confirmation that no outcome material was seen before return.

## Receipt checks

On return:

1. Match the reviewed checksum to the released packet.
2. Verify the reviewer identity and authentication method.
3. Confirm all declarations are complete.
4. Quarantine any review showing outcome exposure or material conflict.
5. Record major and critical findings before revealing the outcome.
6. Freeze the returned record and calculate its checksum.
7. Only then reveal the predeclared outcome record for scoring.

## Stop conditions

Stop and do not score the case when:

- the packet checksum does not match;
- outcome material was seen before review freeze;
- reviewer identity cannot be authenticated;
- an undeclared conflict is discovered;
- the reviewer reviewed a case they prepared or approved;
- the record is incomplete or altered after signature;
- a critical finding remains unresolved.

# PAE v0.2 — Provenance and Hypothesis Structure Contract

## Purpose

PAE v0.2 strengthens the inputs used by later analytical layers. It does not calculate attribution probabilities.

## Source provenance

Every v0.2 source must record:

- URL and archived URL;
- publisher and author;
- publication and collection times with timezones;
- a SHA-256 content checksum;
- language and jurisdiction;
- capture limitations;
- one or more claim-specific authority entries.

Source authority is limited to the stated claim type, scope and basis. Institutional status does not create universal authority.

## Evidence records

Every evidence item must identify:

- the exact proposition;
- the source location;
- the inspectable material;
- authentication status;
- relevance;
- limitations;
- reviewer notes.

## Hypothesis registry

Every hypothesis must identify:

- class;
- actors;
- mechanism;
- timeframe;
- expected outcome;
- predictions;
- disconfirmers.

Supported relationship types are:

- mutually exclusive;
- overlaps;
- nested under;
- sequential;
- compatible.

## Completeness

A causal profile may require:

- a mixed-cause hypothesis;
- an insufficient-information hypothesis;
- at least one ordinary explanation;
- named hypothesis classes.

The engine rejects a strict v0.2 case that does not satisfy its declared profile.

## Immutable snapshots

Every assessment returns the SHA-256 digest of a canonical UTF-8 JSON representation with sorted keys and no insignificant whitespace. A changed case must produce a changed digest.

The snapshot identifies the case version, schema version and canonicalisation rule.

## Compatibility

Cases without `schema_version: 0.2` continue through the accepted v0.1 path. They receive a legacy status and are not falsely presented as having passed v0.2 provenance or hypothesis checks.

## Boundary

A complete hypothesis registry does not establish that any hypothesis is true. A structured source does not establish that its claims are correct. PAE v0.2 improves inspectability and error resistance only.

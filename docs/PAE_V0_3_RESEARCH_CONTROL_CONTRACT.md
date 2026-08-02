# PAE v0.3 — Research Control Contract

## Purpose

PAE v0.3 controls how evidence is collected, related and judged sufficient before any probability assessment is attempted.

## Typed source dependency

Supported relationships are:

- `republished_from`;
- `quotes`;
- `common_anonymous_source`;
- `shared_dataset`;
- `shared_briefing`;
- `transformed_from`;
- `corroborates`.

A typed relationship does not itself establish independence. Independence groups remain the controlling evidence-origin record.

## Coverage by hypothesis

Each evidence item records its effect on named hypotheses as supporting, contradicting, mixed or contextual. The engine reports counts, evidence identifiers, independent streams and whether contrary testing occurred.

## Search diary

Each search records:

- time and researcher;
- exact query;
- languages and jurisdictions;
- source classes;
- whether material was found, unavailable or absent from the searched set;
- limitations and notes.

## Negative evidence

The following states remain distinct:

- `evidence_of_absence` — positive evidence that an expected fact, record or event was absent;
- `not_found` — a completed search did not locate it;
- `not_searched` — the relevant space has not been searched;
- `inaccessible` — the material may exist but cannot currently be inspected.

Only `evidence_of_absence` is evidence. The other three are research states.

## Sufficiency profiles

A named profile declares:

- minimum independent streams;
- criticality threshold;
- whether critical requirements need primary evidence;
- whether critical requirements need contrary evidence;
- whether unsearched critical areas block analysis.

The resulting status describes research sufficiency, not truth or attribution.

## Value of Information

PAE v0.3 ranks research actions using:

- expected discrimination;
- expected analytical impact;
- probability of resolving the question;
- requirement criticality;
- reliability potential;
- time sensitivity;
- accessibility;
- urgency;
- effort and cost penalties.

The score orders work. It is not a probability or monetary value.

## Boundary

PAE v0.3 does not update hypothesis probabilities and does not issue public conclusions.

# PAE Domain Module Interface v0.1

## Purpose

A domain module adds specialised evidence categories, indicators, alternatives and safeguards without changing PAE's general evidence and uncertainty rules.

## Required module fields

Each module declares:

- interface version;
- stable domain identifier and module version;
- scope and applicable claim types;
- required hypothesis classes;
- evidence categories;
- diagnostic indicators;
- a default sufficiency profile;
- prohibited inference jumps.

## Evidence categories

Each category contains:

- one question the investigation must answer;
- preferred evidence types;
- plausible alternative explanations.

Categories define what should be researched. They do not determine which hypothesis is correct.

## Indicators

Each indicator contains:

- an observable condition;
- its evidence category;
- a diagnostic limit;
- alternative explanations.

An indicator is not a likelihood ratio and must not be converted directly into a probability.

## Inference guards

Each prohibited inference jump contains:

- a stable identifier;
- the reasoning error to prevent;
- the bridge evidence needed before the inference becomes supportable.

## Historical comparison libraries

A library records:

- case classification;
- resolution status;
- public evidence quality;
- mechanism and public evidence summary;
- counterevidence and alternatives;
- limitations;
- relevant module indicators;
- analytical lessons;
- official or institutionally accountable sources.

The library must include non-coercive or organic comparators. A collection containing only suspected operations would create selection bias.

## Attribution status

Accepted classifications preserve differences between:

- strong official attribution;
- parliamentary attribution;
- contested official attribution;
- unresolved official attribution;
- organic multi-causal comparison;
- non-coercive forced-displacement comparison.

These labels record public evidence status. They are not judicial verdicts and do not create automatic base rates.

## Boundary

Domain modules support research design and comparison. They do not calculate attribution probabilities or authorise public conclusions.

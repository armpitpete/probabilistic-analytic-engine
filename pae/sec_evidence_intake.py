"""Consumer validation for SEC Evidence Intake Handoff v1.

PAE may accept a validated SEC handoff only as acquisition input. This module
does not construct hypotheses, assess sufficiency, calibrate, or assign
probabilities.
"""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
from typing import Any, Mapping


NON_AUTHORITIES = [
    "truth_decision",
    "motive_inference",
    "contradiction_finding",
    "probability_assignment",
    "publication_approval",
]
FORBIDDEN_ANALYTIC_FIELDS = {
    "hypotheses",
    "probabilities",
    "likelihoods",
    "attribution",
    "information_sufficiency",
}


class SecEvidenceIntakeError(ValueError):
    """Raised when an SEC handoff is not safe as PAE acquisition input."""


def _digest(value: Any) -> str:
    payload = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return sha256(payload).hexdigest()


def validate_sec_evidence_intake(value: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(value, Mapping):
        return ["SEC Evidence Intake handoff must be an object"]

    forbidden = sorted(FORBIDDEN_ANALYTIC_FIELDS & set(value))
    if forbidden:
        errors.append(
            "SEC handoff may not contain PAE analytic fields: " + ", ".join(forbidden)
        )

    producer = value.get("producer")
    if not isinstance(producer, Mapping):
        errors.append("producer must be an object")
    else:
        if producer.get("system") != "story-evidence-collector":
            errors.append("producer.system must be story-evidence-collector")
        if producer.get("contract") != "evidence-intake-handoff-v1":
            errors.append("producer.contract must be evidence-intake-handoff-v1")
        if producer.get("authority_effect") != "none":
            errors.append("SEC producer may not grant PAE authority")

    pack = value.get("evidence_pack")
    if not isinstance(pack, Mapping):
        errors.append("evidence_pack must be an object")
        pack_id = None
    else:
        pack_id = pack.get("pack_id")
        if not isinstance(pack_id, str) or not pack_id:
            errors.append("evidence_pack.pack_id is required")
        validation = pack.get("validation")
        if not isinstance(validation, Mapping) or validation != {
            "validator": "evidence-pack-v1",
            "status": "valid",
            "errors": [],
        }:
            errors.append("PAE requires a validated SEC Evidence Pack")
        pack_digest = pack.get("integrity_sha256")
        if (
            not isinstance(pack_digest, str)
            or len(pack_digest) != 64
            or any(ch not in "0123456789abcdef" for ch in pack_digest)
        ):
            errors.append("evidence_pack.integrity_sha256 is required")
        elif value.get("handoff_id") != (
            f"sec-evidence-intake:{pack_id}:{pack_digest[:16]}"
        ):
            errors.append("handoff_id must bind the SEC Evidence Pack identity and digest")

    sources = value.get("sources")
    if not isinstance(sources, list) or not sources:
        errors.append("PAE acquisition input requires at least one source")
        sources = []
    expected_failures: list[dict[str, Any]] = []
    for index, source in enumerate(sources, 1):
        if not isinstance(source, Mapping):
            errors.append(f"source {index} must be an object")
            continue
        identity = source.get("identity")
        provenance = source.get("provenance")
        dependency = source.get("dependency")
        if not isinstance(identity, Mapping) or not identity.get("url"):
            errors.append(f"source {index} missing exact source identity")
        elif not isinstance(identity.get("record_sha256"), str):
            errors.append(f"source {index} missing source record digest")
        if not isinstance(provenance, Mapping):
            errors.append(f"source {index} missing provenance")
        elif (
            provenance.get("evidence_pack_id") != pack_id
            or not provenance.get("record_path")
            or not isinstance(provenance.get("record_line"), int)
        ):
            errors.append(f"source {index} has inconsistent provenance")
        if not isinstance(dependency, Mapping):
            errors.append(f"source {index} missing dependency state")
        for field in ("collection", "preserved_source"):
            if not isinstance(source.get(field), Mapping):
                errors.append(f"source {index} missing {field}")
        collection = source.get("collection")
        if isinstance(collection, Mapping):
            status = collection.get("scrape_status")
            if status and status not in {"ok", "captured", "fixture_from_reviewed_pack"}:
                expected_failures.append(
                    {
                        "source_id": source.get("source_id"),
                        "scrape_status": status,
                        "robots_allowed": collection.get("robots_allowed"),
                        "error": collection.get("error"),
                    }
                )
        preserved = source.get("preserved_source")
        if isinstance(preserved, Mapping):
            excerpt = preserved.get("visible_excerpt")
            digest = preserved.get("visible_excerpt_sha256")
            if not isinstance(excerpt, str):
                errors.append(f"source {index} visible_excerpt must be a string")
            else:
                expected_digest = sha256(excerpt.encode("utf-8")).hexdigest() if excerpt else None
                if digest != expected_digest:
                    errors.append(f"source {index} visible excerpt digest mismatch")

    uncertainty = value.get("uncertainty")
    if not isinstance(uncertainty, Mapping):
        errors.append("uncertainty must be preserved")
    else:
        for field in ("collection_failures", "negative_evidence", "search_dead_ends"):
            if not isinstance(uncertainty.get(field), list):
                errors.append(f"uncertainty.{field} must be preserved")
        if uncertainty.get("collection_failures") != expected_failures:
            errors.append("uncertainty.collection_failures must preserve failed collection state")

    review = value.get("human_review")
    if not isinstance(review, Mapping):
        errors.append("human_review must be preserved")
    else:
        if not isinstance(review.get("required"), bool):
            errors.append("human_review.required must be boolean")
        if review.get("state") not in {"missing", "not_reviewed", "mixed", "reviewed"}:
            errors.append("human_review.state is invalid")
        if not isinstance(review.get("records"), list):
            errors.append("human_review.records must be preserved")

    if value.get("non_authorities") != NON_AUTHORITIES:
        errors.append("SEC non-authorities boundary must be preserved exactly")

    contracts = value.get("consumer_contracts")
    profile = contracts.get("pae") if isinstance(contracts, Mapping) else None
    expected = {
        "intake_role": "evidence_acquisition_input",
        "analysis_readiness": "not_assessed",
        "requires_pae_case_construction": True,
        "requires_pae_sufficiency_and_calibration": True,
        "authority_effect": "none",
    }
    if not isinstance(profile, Mapping) or dict(profile) != expected:
        errors.append(
            "PAE profile must remain acquisition input with analysis readiness not assessed"
        )

    candidate = deepcopy(dict(value))
    actual = candidate.pop("integrity_sha256", None)
    if not isinstance(actual, str) or actual != _digest(candidate):
        errors.append("SEC Evidence Intake integrity_sha256 mismatch")

    return errors


def acquisition_input_projection(value: Any) -> dict[str, Any]:
    """Return bounded acquisition metadata without constructing a PAE case."""
    errors = validate_sec_evidence_intake(value)
    if errors:
        raise SecEvidenceIntakeError("; ".join(errors))
    return {
        "handoff_id": value["handoff_id"],
        "pack_id": value["evidence_pack"]["pack_id"],
        "source_count": len(value["sources"]),
        "intake_role": "evidence_acquisition_input",
        "analysis_readiness": "not_assessed",
        "information_sufficiency": "not_assessed",
        "requires_pae_case_construction": True,
        "requires_pae_sufficiency_and_calibration": True,
        "authority_effect": "none",
    }

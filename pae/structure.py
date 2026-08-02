"""PAE v0.2 provenance, hypothesis structure and immutable case snapshots."""

from __future__ import annotations

from datetime import datetime
from hashlib import sha256
import json
import re
from typing import Any

from .acquisition import AcquisitionError

SCHEMA_VERSION = "0.2"
HYPOTHESIS_CLASSES = {
    "organic",
    "ordinary_failure",
    "incompetence",
    "coincidence",
    "domestic_deliberate",
    "foreign_indirect",
    "foreign_direct",
    "mixed",
    "insufficient_information",
}
RELATIONSHIP_TYPES = {
    "mutually_exclusive",
    "overlaps",
    "nested_under",
    "sequential",
    "compatible",
}
AUTHENTICATION_STATES = {
    "unassessed",
    "failed",
    "partial",
    "authenticated",
    "disputed",
}
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def _required_string(record: dict[str, Any], key: str, context: str) -> str:
    value = record.get(key)
    if not isinstance(value, str) or not value.strip():
        raise AcquisitionError(f"{context}: {key} must be a non-empty string")
    return value.strip()


def _required_string_list(record: dict[str, Any], key: str, context: str) -> list[str]:
    value = record.get(key)
    if not isinstance(value, list) or not value or any(
        not isinstance(item, str) or not item.strip() for item in value
    ):
        raise AcquisitionError(f"{context}: {key} must be a non-empty list of strings")
    return [item.strip() for item in value]


def _iso_datetime(value: str, context: str) -> None:
    candidate = value.replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(candidate)
    except ValueError as exc:
        raise AcquisitionError(f"{context}: must be an ISO-8601 datetime") from exc
    if parsed.tzinfo is None:
        raise AcquisitionError(f"{context}: timezone is required")


def _validate_authority(source: dict[str, Any], source_id: str) -> None:
    authority = source.get("authority")
    if not isinstance(authority, list) or not authority:
        raise AcquisitionError(f"source {source_id}: authority must be a non-empty list")
    for position, entry in enumerate(authority, start=1):
        context = f"source {source_id} authority[{position}]"
        if not isinstance(entry, dict):
            raise AcquisitionError(f"{context}: must be an object")
        for field in ("claim_type", "scope", "basis", "limitations"):
            _required_string(entry, field, context)


def _validate_source_v02(source: dict[str, Any], source_id: str) -> None:
    for field in (
        "url",
        "publisher",
        "author",
        "published_at",
        "collected_at",
        "archive_url",
        "content_sha256",
        "language",
        "jurisdiction",
        "capture_limitations",
    ):
        _required_string(source, field, f"source {source_id}")
    _iso_datetime(source["published_at"], f"source {source_id}: published_at")
    _iso_datetime(source["collected_at"], f"source {source_id}: collected_at")
    if not SHA256_RE.fullmatch(source["content_sha256"]):
        raise AcquisitionError(
            f"source {source_id}: content_sha256 must be 64 lowercase hexadecimal characters"
        )
    _validate_authority(source, source_id)


def _validate_evidence_v02(item: dict[str, Any], evidence_id: str) -> None:
    for field in (
        "proposition",
        "source_locator",
        "inspectable_material",
        "relevance",
        "limitations",
        "reviewer_notes",
    ):
        _required_string(item, field, f"evidence {evidence_id}")
    authentication = _required_string(
        item, "authentication_status", f"evidence {evidence_id}"
    )
    if authentication not in AUTHENTICATION_STATES:
        raise AcquisitionError(
            f"evidence {evidence_id}: unsupported authentication_status {authentication!r}"
        )


def _validate_hypothesis_v02(hypothesis: dict[str, Any], hypothesis_id: str) -> None:
    hypothesis_class = _required_string(
        hypothesis, "class", f"hypothesis {hypothesis_id}"
    )
    if hypothesis_class not in HYPOTHESIS_CLASSES:
        raise AcquisitionError(
            f"hypothesis {hypothesis_id}: unsupported class {hypothesis_class!r}"
        )
    _required_string_list(hypothesis, "actors", f"hypothesis {hypothesis_id}")
    for field in ("mechanism", "timeframe", "outcome"):
        _required_string(hypothesis, field, f"hypothesis {hypothesis_id}")
    _required_string_list(hypothesis, "predictions", f"hypothesis {hypothesis_id}")
    _required_string_list(hypothesis, "disconfirmers", f"hypothesis {hypothesis_id}")


def _validate_relationships(
    relationships: Any, hypothesis_ids: set[str]
) -> list[dict[str, str]]:
    if not isinstance(relationships, list):
        raise AcquisitionError("relationships must be a list")
    normalized: list[dict[str, str]] = []
    seen: set[tuple[str, str, str]] = set()
    for position, relationship in enumerate(relationships, start=1):
        context = f"relationships[{position}]"
        if not isinstance(relationship, dict):
            raise AcquisitionError(f"{context}: must be an object")
        source = _required_string(relationship, "from", context)
        target = _required_string(relationship, "to", context)
        relation_type = _required_string(relationship, "type", context)
        if source not in hypothesis_ids or target not in hypothesis_ids:
            raise AcquisitionError(f"{context}: relationship refers to unknown hypothesis")
        if source == target:
            raise AcquisitionError(f"{context}: relationship cannot refer to itself")
        if relation_type not in RELATIONSHIP_TYPES:
            raise AcquisitionError(
                f"{context}: unsupported relationship type {relation_type!r}"
            )
        key = (source, target, relation_type)
        if key in seen:
            raise AcquisitionError(f"{context}: duplicate relationship")
        seen.add(key)
        normalized.append({"from": source, "to": target, "type": relation_type})
    return normalized


def validate_extended_case(case: dict[str, Any]) -> dict[str, Any]:
    """Validate v0.2-only fields while leaving accepted v0.1 cases valid."""
    if case.get("schema_version") != SCHEMA_VERSION:
        return {"schema_version": "0.1", "extended": False}

    case_version = _required_string(case, "case_version", "case")
    domain_id = _required_string(case, "domain_id", "case")
    profile = case.get("causal_profile")
    if not isinstance(profile, dict):
        raise AcquisitionError("case: causal_profile must be an object")

    hypotheses = {item["id"]: item for item in case["hypotheses"]}
    for hypothesis_id, hypothesis in hypotheses.items():
        _validate_hypothesis_v02(hypothesis, hypothesis_id)

    relationships = _validate_relationships(
        case.get("relationships"), set(hypotheses)
    )

    for source in case["sources"]:
        _validate_source_v02(source, source["id"])
    for item in case["evidence_items"]:
        _validate_evidence_v02(item, item["id"])

    classes = {hypothesis["class"] for hypothesis in hypotheses.values()}
    required_classes = set(profile.get("required_hypothesis_classes", []))
    unknown_required = required_classes - HYPOTHESIS_CLASSES
    if unknown_required:
        raise AcquisitionError(
            "case causal_profile: unsupported required classes "
            + ", ".join(sorted(unknown_required))
        )
    if profile.get("require_mixed_cause", False) and "mixed" not in classes:
        raise AcquisitionError(
            "case causal_profile: a mixed-cause hypothesis is required"
        )
    if profile.get("require_insufficient_information", True) and (
        "insufficient_information" not in classes
    ):
        raise AcquisitionError(
            "case causal_profile: an insufficient-information hypothesis is required"
        )

    ordinary_options = set(
        profile.get(
            "ordinary_explanation_classes",
            ["organic", "ordinary_failure", "incompetence", "coincidence"],
        )
    )
    if ordinary_options and not (classes & ordinary_options):
        raise AcquisitionError(
            "case causal_profile: at least one ordinary explanation is required"
        )

    return {
        "schema_version": SCHEMA_VERSION,
        "case_version": case_version,
        "domain_id": domain_id,
        "extended": True,
        "hypotheses": hypotheses,
        "relationships": relationships,
        "classes": classes,
        "required_classes": required_classes,
        "ordinary_options": ordinary_options,
    }


def canonical_case_bytes(case: dict[str, Any]) -> bytes:
    return json.dumps(
        case,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def case_snapshot(case: dict[str, Any]) -> dict[str, str]:
    payload = canonical_case_bytes(case)
    return {
        "case_id": case["case_id"],
        "case_version": str(case.get("case_version", "legacy-v0.1")),
        "schema_version": str(case.get("schema_version", "0.1")),
        "sha256": sha256(payload).hexdigest(),
        "canonicalisation": "utf-8-json-sorted-keys-no-whitespace-v1",
    }


def hypothesis_analysis(
    case: dict[str, Any], extended: dict[str, Any]
) -> dict[str, Any]:
    if not extended["extended"]:
        return {
            "status": "legacy-v0.1",
            "registry": [],
            "relationships": [],
            "completeness": {
                "status": "not_assessed",
                "missing_required_classes": [],
            },
        }

    registry = []
    for hypothesis_id, hypothesis in sorted(extended["hypotheses"].items()):
        registry.append(
            {
                "hypothesis_id": hypothesis_id,
                "label": hypothesis["label"],
                "class": hypothesis["class"],
                "actors": hypothesis["actors"],
                "mechanism": hypothesis["mechanism"],
                "timeframe": hypothesis["timeframe"],
                "outcome": hypothesis["outcome"],
                "predictions": hypothesis["predictions"],
                "disconfirmers": hypothesis["disconfirmers"],
            }
        )

    missing = sorted(extended["required_classes"] - extended["classes"])
    classes = extended["classes"]
    profile = case["causal_profile"]
    checks = {
        "mixed_cause_present": "mixed" in classes,
        "insufficient_information_present": "insufficient_information" in classes,
        "ordinary_explanation_present": bool(classes & extended["ordinary_options"]),
        "required_classes_present": not missing,
    }
    return {
        "status": "complete" if all(checks.values()) else "incomplete",
        "registry": registry,
        "relationships": extended["relationships"],
        "completeness": {
            "checks": checks,
            "missing_required_classes": missing,
            "profile": profile.get("name", "unnamed"),
        },
    }


def provenance_summary(case: dict[str, Any], extended: dict[str, Any]) -> dict[str, Any]:
    if not extended["extended"]:
        return {
            "status": "legacy-v0.1",
            "sources_total": len(case.get("sources", [])),
            "authority_entries": 0,
        }
    sources = case["sources"]
    return {
        "status": "structured",
        "sources_total": len(sources),
        "authority_entries": sum(len(source["authority"]) for source in sources),
        "languages": sorted({source["language"] for source in sources}),
        "jurisdictions": sorted({source["jurisdiction"] for source in sources}),
        "archived_sources": sum(bool(source["archive_url"]) for source in sources),
        "content_hashes_present": sum(bool(source["content_sha256"]) for source in sources),
    }

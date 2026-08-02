"""PAE research-control layer: dependency typing, audit, sufficiency and VoI."""

from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any

from .acquisition import AcquisitionError

PROTOCOL_VERSION = "0.3"
DEPENDENCY_TYPES = {
    "republished_from", "quotes", "common_anonymous_source", "shared_dataset",
    "shared_briefing", "transformed_from", "corroborates",
}
IMPACT_DIRECTIONS = {"supports", "contradicts", "mixed", "context"}
ABSENCE_STATES = {"present", "evidence_of_absence", "not_found", "not_searched", "inaccessible", "not_applicable"}
SEARCH_RESULTS = {"found", "no_result", "inaccessible"}
NEGATIVE_STATES = {"evidence_of_absence", "not_found", "not_searched", "inaccessible"}


def _string(record: dict[str, Any], key: str, context: str) -> str:
    value = record.get(key)
    if not isinstance(value, str) or not value.strip():
        raise AcquisitionError(f"{context}: {key} must be a non-empty string")
    return value.strip()


def _score(record: dict[str, Any], key: str, context: str) -> int:
    value = record.get(key)
    if not isinstance(value, int) or not 0 <= value <= 5:
        raise AcquisitionError(f"{context}: {key} must be an integer from 0 to 5")
    return value


def validate_research_protocol(case: dict[str, Any]) -> dict[str, Any]:
    if case.get("research_protocol_version") != PROTOCOL_VERSION:
        return {"extended": False, "protocol_version": None}

    hypotheses = {item["id"] for item in case["hypotheses"]}
    sources = {item["id"]: item for item in case["sources"]}
    requirements = {item["id"]: item for item in case["requirements"]}

    for source_id, source in sources.items():
        links = source.get("dependency_links")
        if not isinstance(links, list):
            raise AcquisitionError(f"source {source_id}: dependency_links must be a list")
        for position, link in enumerate(links, start=1):
            context = f"source {source_id} dependency_links[{position}]"
            if not isinstance(link, dict):
                raise AcquisitionError(f"{context}: must be an object")
            target = _string(link, "source_id", context)
            relation = _string(link, "relation_type", context)
            if target not in sources:
                raise AcquisitionError(f"{context}: unknown source {target!r}")
            if target == source_id:
                raise AcquisitionError(f"{context}: cannot refer to itself")
            if relation not in DEPENDENCY_TYPES:
                raise AcquisitionError(f"{context}: unsupported relation_type {relation!r}")

    for item in case["evidence_items"]:
        evidence_id = item["id"]
        absence = _string(item, "absence_status", f"evidence {evidence_id}")
        if absence not in ABSENCE_STATES:
            raise AcquisitionError(f"evidence {evidence_id}: unsupported absence_status {absence!r}")
        impacts = item.get("hypothesis_impacts")
        if not isinstance(impacts, list) or not impacts:
            raise AcquisitionError(f"evidence {evidence_id}: hypothesis_impacts must be a non-empty list")
        for position, impact in enumerate(impacts, start=1):
            context = f"evidence {evidence_id} hypothesis_impacts[{position}]"
            if not isinstance(impact, dict):
                raise AcquisitionError(f"{context}: must be an object")
            hypothesis_id = _string(impact, "hypothesis_id", context)
            direction = _string(impact, "direction", context)
            if hypothesis_id not in hypotheses:
                raise AcquisitionError(f"{context}: unknown hypothesis {hypothesis_id!r}")
            if direction not in IMPACT_DIRECTIONS:
                raise AcquisitionError(f"{context}: unsupported direction {direction!r}")
        if absence == "evidence_of_absence" and not any(
            impact["direction"] in {"contradicts", "mixed"} for impact in impacts
        ):
            raise AcquisitionError(f"evidence {evidence_id}: evidence_of_absence must contradict or mix")

    diary = case.get("search_diary")
    if not isinstance(diary, list):
        raise AcquisitionError("search_diary must be a list")
    diary_ids: set[str] = set()
    for position, entry in enumerate(diary, start=1):
        context = f"search_diary[{position}]"
        if not isinstance(entry, dict):
            raise AcquisitionError(f"{context}: must be an object")
        entry_id = _string(entry, "id", context)
        if entry_id in diary_ids:
            raise AcquisitionError(f"{context}: duplicate id {entry_id!r}")
        diary_ids.add(entry_id)
        for field in ("searched_at", "researcher", "query", "notes"):
            _string(entry, field, context)
        for field in ("languages", "jurisdictions", "source_classes"):
            value = entry.get(field)
            if not isinstance(value, list) or not value:
                raise AcquisitionError(f"{context}: {field} must be a non-empty list")
        result = _string(entry, "result_status", context)
        if result not in SEARCH_RESULTS:
            raise AcquisitionError(f"{context}: unsupported result_status {result!r}")

    negative = case.get("negative_evidence")
    if not isinstance(negative, list):
        raise AcquisitionError("negative_evidence must be a list")
    for position, entry in enumerate(negative, start=1):
        context = f"negative_evidence[{position}]"
        if not isinstance(entry, dict):
            raise AcquisitionError(f"{context}: must be an object")
        _string(entry, "id", context)
        requirement_id = _string(entry, "requirement_id", context)
        if requirement_id not in requirements:
            raise AcquisitionError(f"{context}: unknown requirement {requirement_id!r}")
        status = _string(entry, "status", context)
        if status not in NEGATIVE_STATES:
            raise AcquisitionError(f"{context}: unsupported status {status!r}")
        for field in ("scope", "expected_if_true", "notes"):
            _string(entry, field, context)
        search_ids = entry.get("search_ids")
        if not isinstance(search_ids, list):
            raise AcquisitionError(f"{context}: search_ids must be a list")
        unknown = set(search_ids) - diary_ids
        if unknown:
            raise AcquisitionError(f"{context}: unknown search ids {', '.join(sorted(unknown))}")

    profile = case.get("sufficiency_profile")
    if not isinstance(profile, dict):
        raise AcquisitionError("sufficiency_profile must be an object")
    _string(profile, "name", "sufficiency_profile")
    for field in ("minimum_independent_streams", "criticality_threshold"):
        value = profile.get(field)
        if not isinstance(value, int) or value < 1:
            raise AcquisitionError(f"sufficiency_profile: {field} must be a positive integer")
    for field in ("require_primary_for_critical", "require_contrary_for_critical", "block_on_unsearched_critical"):
        if not isinstance(profile.get(field), bool):
            raise AcquisitionError(f"sufficiency_profile: {field} must be boolean")

    for option in case["research_options"]:
        option_id = option["id"]
        for field in ("probability_of_resolution", "expected_analytical_impact", "time_sensitivity", "effort"):
            _score(option, field, f"research option {option_id}")

    return {
        "extended": True,
        "protocol_version": PROTOCOL_VERSION,
        "hypotheses": hypotheses,
        "sources": sources,
        "requirements": requirements,
        "diary_ids": diary_ids,
        "profile": profile,
    }


def typed_dependency_graph(case: dict[str, Any], protocol: dict[str, Any]) -> dict[str, Any]:
    if not protocol["extended"]:
        return {"status": "not_available", "nodes": [], "edges": []}
    edges: list[dict[str, str]] = []
    for source in case["sources"]:
        for link in source["dependency_links"]:
            edges.append({"from": link["source_id"], "to": source["id"], "type": link["relation_type"]})
    counts = Counter(edge["type"] for edge in edges)
    return {
        "status": "structured",
        "nodes": sorted(protocol["sources"]),
        "edges": sorted(edges, key=lambda item: (item["from"], item["to"], item["type"])),
        "relation_counts": dict(sorted(counts.items())),
    }


def coverage_by_hypothesis(case: dict[str, Any], protocol: dict[str, Any]) -> list[dict[str, Any]]:
    if not protocol["extended"]:
        return []
    sources = protocol["sources"]
    rows: dict[str, dict[str, Any]] = {}
    for hypothesis in case["hypotheses"]:
        rows[hypothesis["id"]] = {
            "hypothesis_id": hypothesis["id"], "label": hypothesis["label"],
            "supports": 0, "contradicts": 0, "mixed": 0, "context": 0,
            "independent_streams": set(), "evidence_items": [],
        }
    for item in case["evidence_items"]:
        groups = {sources[source_id]["independence_group"] for source_id in item["source_ids"]}
        for impact in item["hypothesis_impacts"]:
            row = rows[impact["hypothesis_id"]]
            row[impact["direction"]] += 1
            row["independent_streams"].update(groups)
            row["evidence_items"].append(item["id"])
    output = []
    for row in rows.values():
        output.append({
            **row,
            "independent_streams": len(row["independent_streams"]),
            "evidence_items": sorted(set(row["evidence_items"])),
            "contrary_tested": row["contradicts"] > 0 or row["mixed"] > 0,
        })
    return sorted(output, key=lambda item: item["hypothesis_id"])


def search_audit(case: dict[str, Any], protocol: dict[str, Any]) -> dict[str, Any]:
    if not protocol["extended"]:
        return {"status": "not_available"}
    diary = case["search_diary"]
    results = Counter(entry["result_status"] for entry in diary)
    return {
        "status": "structured",
        "searches_total": len(diary),
        "result_counts": dict(sorted(results.items())),
        "languages": sorted({lang for entry in diary for lang in entry["languages"]}),
        "jurisdictions": sorted({jurisdiction for entry in diary for jurisdiction in entry["jurisdictions"]}),
        "source_classes": sorted({source_class for entry in diary for source_class in entry["source_classes"]}),
    }


def absence_summary(case: dict[str, Any], protocol: dict[str, Any]) -> dict[str, Any]:
    if not protocol["extended"]:
        return {"status": "not_available"}
    evidence_counts = Counter(item["absence_status"] for item in case["evidence_items"])
    negative_counts = Counter(entry["status"] for entry in case["negative_evidence"])
    return {
        "status": "structured",
        "evidence_item_states": dict(sorted(evidence_counts.items())),
        "negative_record_states": dict(sorted(negative_counts.items())),
        "evidence_of_absence_count": evidence_counts["evidence_of_absence"] + negative_counts["evidence_of_absence"],
        "search_failure_count": (
            evidence_counts["not_found"] + evidence_counts["not_searched"] + evidence_counts["inaccessible"]
            + negative_counts["not_found"] + negative_counts["not_searched"] + negative_counts["inaccessible"]
        ),
        "warning": "not_found, not_searched and inaccessible are research states, not evidence that an event or relationship did not exist",
    }


def sufficiency_v2(case: dict[str, Any], protocol: dict[str, Any], base_assessment: dict[str, Any]) -> dict[str, Any]:
    if not protocol["extended"]:
        return {"status": "not_available"}
    profile = protocol["profile"]
    threshold = profile["criticality_threshold"]
    critical = [row for row in base_assessment["coverage_map"] if row["criticality"] >= threshold]
    failures: list[str] = []
    if base_assessment["information_sufficiency"]["independent_source_streams"] < profile["minimum_independent_streams"]:
        failures.append("independent_stream_threshold")
    if any(row["status"] == "missing" for row in critical):
        failures.append("critical_requirement_missing")
    if profile["require_primary_for_critical"] and any(not row["primary_present"] for row in critical):
        failures.append("critical_primary_missing")
    if profile["require_contrary_for_critical"] and any(not row["contrary_present"] for row in critical):
        failures.append("critical_contrary_missing")
    negative_by_requirement = defaultdict(list)
    for entry in case["negative_evidence"]:
        negative_by_requirement[entry["requirement_id"]].append(entry["status"])
    if profile["block_on_unsearched_critical"]:
        critical_ids = {requirement["id"] for requirement in case["requirements"] if requirement["criticality"] >= threshold}
        for requirement_id in critical_ids:
            if "not_searched" in negative_by_requirement.get(requirement_id, []):
                failures.append(f"critical_unsearched:{requirement_id}")
    if failures:
        status = "insufficient"
    elif any(row["status"] != "covered" for row in critical):
        status = "preliminary"
    elif any(row["status"] != "covered" for row in base_assessment["coverage_map"]):
        status = "developing"
    else:
        status = "mature"
    return {
        "status": status, "profile": profile["name"], "failures": sorted(set(failures)),
        "criticality_threshold": threshold, "minimum_independent_streams": profile["minimum_independent_streams"],
        "warning": "This is a research-sufficiency state, not an attribution result.",
    }


def ranked_research_queue_v2(case: dict[str, Any], protocol: dict[str, Any]) -> list[dict[str, Any]]:
    if not protocol["extended"]:
        return []
    requirements = protocol["requirements"]
    ranked: list[dict[str, Any]] = []
    for option in case["research_options"]:
        requirement = requirements[option["requirement_id"]]
        components = {
            "discrimination": 3 * option["expected_discrimination"],
            "analytical_impact": 3 * option["expected_analytical_impact"],
            "resolution_probability": 2 * option["probability_of_resolution"],
            "criticality": 2 * requirement["criticality"],
            "reliability": option["reliability_potential"],
            "time_sensitivity": option["time_sensitivity"],
            "accessibility": option["accessibility"],
            "urgency": option["urgency"],
            "effort_penalty": -option["effort"],
            "cost_penalty": -option["cost"],
        }
        ranked.append({
            "option_id": option["id"], "requirement_id": option["requirement_id"],
            "description": option["description"], "score": sum(components.values()),
            "components": components, "blocked": bool(option.get("blocked", False)),
        })
    return sorted(ranked, key=lambda item: (item["blocked"], -item["score"], item["option_id"]))


def research_outputs(case: dict[str, Any], base_assessment: dict[str, Any]) -> dict[str, Any]:
    protocol = validate_research_protocol(case)
    return {
        "research_protocol_version": protocol["protocol_version"],
        "typed_source_dependency_graph": typed_dependency_graph(case, protocol),
        "coverage_by_hypothesis": coverage_by_hypothesis(case, protocol),
        "search_audit": search_audit(case, protocol),
        "absence_summary": absence_summary(case, protocol),
        "information_sufficiency_v2": sufficiency_v2(case, protocol, base_assessment),
        "ranked_next_search_queue_v2": ranked_research_queue_v2(case, protocol),
    }

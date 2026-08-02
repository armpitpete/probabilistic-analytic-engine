"""Deterministic Evidence Acquisition Manager v0.1.

The module evaluates whether competing hypotheses have been fairly researched.
It measures evidence coverage, not truth, guilt, motive, or probability.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Iterable


class AcquisitionError(ValueError):
    """Raised when a case record violates the v0.1 contract."""


REQUIRED_TOP_LEVEL = {
    "case_id",
    "title",
    "status",
    "hypotheses",
    "requirements",
    "sources",
    "evidence_items",
    "research_options",
}

ALLOWED_DIRECTIONS = {"supports", "contradicts", "mixed", "context"}
ALLOWED_VERIFICATION = {"unverified", "partly_verified", "verified", "disputed"}
ALLOWED_SOURCE_CLASSES = {"primary", "investigative", "contextual", "claim", "fixture"}
ALLOWED_STATUSES = {"method_fixture", "research", "paused", "closed"}


@dataclass(frozen=True)
class RequirementCoverage:
    requirement_id: str
    question: str
    criticality: int
    source_count: int
    independent_stream_count: int
    primary_present: bool
    contrary_present: bool
    verified_evidence_present: bool
    target_streams: int
    status: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "requirement_id": self.requirement_id,
            "question": self.question,
            "criticality": self.criticality,
            "source_count": self.source_count,
            "independent_stream_count": self.independent_stream_count,
            "primary_present": self.primary_present,
            "contrary_present": self.contrary_present,
            "verified_evidence_present": self.verified_evidence_present,
            "target_streams": self.target_streams,
            "status": self.status,
        }


def _require_string(record: dict[str, Any], key: str, context: str) -> str:
    value = record.get(key)
    if not isinstance(value, str) or not value.strip():
        raise AcquisitionError(f"{context}: {key} must be a non-empty string")
    return value.strip()


def _unique_records(records: Any, context: str) -> dict[str, dict[str, Any]]:
    if not isinstance(records, list):
        raise AcquisitionError(f"{context} must be a list")
    indexed: dict[str, dict[str, Any]] = {}
    for position, record in enumerate(records, start=1):
        if not isinstance(record, dict):
            raise AcquisitionError(f"{context}[{position}] must be an object")
        record_id = _require_string(record, "id", f"{context}[{position}]")
        if record_id in indexed:
            raise AcquisitionError(f"{context}: duplicate id {record_id!r}")
        indexed[record_id] = record
    return indexed


def validate_case(case: Any) -> dict[str, dict[str, dict[str, Any]]]:
    """Validate referential integrity and bounded v0.1 field rules."""
    if not isinstance(case, dict):
        raise AcquisitionError("case must be an object")
    missing = sorted(REQUIRED_TOP_LEVEL - set(case))
    if missing:
        raise AcquisitionError(f"case missing required fields: {', '.join(missing)}")

    _require_string(case, "case_id", "case")
    _require_string(case, "title", "case")
    status = _require_string(case, "status", "case")
    if status not in ALLOWED_STATUSES:
        raise AcquisitionError(f"case: unsupported status {status!r}")

    hypotheses = _unique_records(case["hypotheses"], "hypotheses")
    requirements = _unique_records(case["requirements"], "requirements")
    sources = _unique_records(case["sources"], "sources")
    evidence = _unique_records(case["evidence_items"], "evidence_items")
    options = _unique_records(case["research_options"], "research_options")

    if len(hypotheses) < 2:
        raise AcquisitionError("at least two competing hypotheses are required")

    for hypothesis_id, hypothesis in hypotheses.items():
        _require_string(hypothesis, "label", f"hypothesis {hypothesis_id}")
        _require_string(hypothesis, "description", f"hypothesis {hypothesis_id}")

    for requirement_id, requirement in requirements.items():
        _require_string(requirement, "question", f"requirement {requirement_id}")
        criticality = requirement.get("criticality")
        if not isinstance(criticality, int) or not 1 <= criticality <= 5:
            raise AcquisitionError(
                f"requirement {requirement_id}: criticality must be an integer from 1 to 5"
            )
        target = requirement.get("target_independent_streams", 1)
        if not isinstance(target, int) or target < 1:
            raise AcquisitionError(
                f"requirement {requirement_id}: target_independent_streams must be at least 1"
            )
        hypothesis_ids = requirement.get("hypothesis_ids")
        if not isinstance(hypothesis_ids, list) or not hypothesis_ids:
            raise AcquisitionError(
                f"requirement {requirement_id}: hypothesis_ids must be a non-empty list"
            )
        unknown = sorted(set(hypothesis_ids) - set(hypotheses))
        if unknown:
            raise AcquisitionError(
                f"requirement {requirement_id}: unknown hypotheses {', '.join(unknown)}"
            )

    for source_id, source in sources.items():
        _require_string(source, "title", f"source {source_id}")
        source_class = _require_string(source, "source_class", f"source {source_id}")
        if source_class not in ALLOWED_SOURCE_CLASSES:
            raise AcquisitionError(f"source {source_id}: unsupported source_class {source_class!r}")
        _require_string(source, "independence_group", f"source {source_id}")
        derived_from = source.get("derived_from", [])
        if not isinstance(derived_from, list):
            raise AcquisitionError(f"source {source_id}: derived_from must be a list")
        unknown = sorted(set(derived_from) - set(sources))
        if unknown:
            raise AcquisitionError(
                f"source {source_id}: unknown derived_from sources {', '.join(unknown)}"
            )
        if source_id in derived_from:
            raise AcquisitionError(f"source {source_id}: cannot derive from itself")

    _assert_acyclic_sources(sources)

    for evidence_id, item in evidence.items():
        requirement_id = _require_string(item, "requirement_id", f"evidence {evidence_id}")
        if requirement_id not in requirements:
            raise AcquisitionError(
                f"evidence {evidence_id}: unknown requirement {requirement_id!r}"
            )
        source_ids = item.get("source_ids")
        if not isinstance(source_ids, list) or not source_ids:
            raise AcquisitionError(f"evidence {evidence_id}: source_ids must be a non-empty list")
        unknown_sources = sorted(set(source_ids) - set(sources))
        if unknown_sources:
            raise AcquisitionError(
                f"evidence {evidence_id}: unknown sources {', '.join(unknown_sources)}"
            )
        direction = _require_string(item, "direction", f"evidence {evidence_id}")
        if direction not in ALLOWED_DIRECTIONS:
            raise AcquisitionError(f"evidence {evidence_id}: unsupported direction {direction!r}")
        verification = _require_string(item, "verification", f"evidence {evidence_id}")
        if verification not in ALLOWED_VERIFICATION:
            raise AcquisitionError(
                f"evidence {evidence_id}: unsupported verification {verification!r}"
            )

    for option_id, option in options.items():
        requirement_id = _require_string(option, "requirement_id", f"research option {option_id}")
        if requirement_id not in requirements:
            raise AcquisitionError(
                f"research option {option_id}: unknown requirement {requirement_id!r}"
            )
        _require_string(option, "description", f"research option {option_id}")
        for field in (
            "expected_discrimination",
            "reliability_potential",
            "accessibility",
            "urgency",
            "cost",
        ):
            value = option.get(field)
            if not isinstance(value, int) or not 0 <= value <= 5:
                raise AcquisitionError(
                    f"research option {option_id}: {field} must be an integer from 0 to 5"
                )

    return {
        "hypotheses": hypotheses,
        "requirements": requirements,
        "sources": sources,
        "evidence_items": evidence,
        "research_options": options,
    }


def _assert_acyclic_sources(sources: dict[str, dict[str, Any]]) -> None:
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(source_id: str) -> None:
        if source_id in visited:
            return
        if source_id in visiting:
            raise AcquisitionError(f"source dependency cycle includes {source_id!r}")
        visiting.add(source_id)
        for parent_id in sources[source_id].get("derived_from", []):
            visit(parent_id)
        visiting.remove(source_id)
        visited.add(source_id)

    for source_id in sources:
        visit(source_id)


def source_dependency_graph(sources: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """Return explicit derivation edges and independence components."""
    groups: dict[str, list[str]] = defaultdict(list)
    edges: list[dict[str, str]] = []
    for source_id, source in sources.items():
        groups[source["independence_group"]].append(source_id)
        for parent_id in source.get("derived_from", []):
            edges.append({"from": parent_id, "to": source_id, "type": "derived_from"})

    components = [
        {"independence_group": group, "source_ids": sorted(source_ids)}
        for group, source_ids in sorted(groups.items())
    ]
    return {
        "nodes": [
            {
                "source_id": source_id,
                "title": source["title"],
                "source_class": source["source_class"],
                "independence_group": source["independence_group"],
            }
            for source_id, source in sorted(sources.items())
        ],
        "edges": sorted(edges, key=lambda edge: (edge["from"], edge["to"])),
        "independence_components": components,
    }


def _requirement_coverage(
    requirement: dict[str, Any],
    evidence_items: Iterable[dict[str, Any]],
    sources: dict[str, dict[str, Any]],
) -> RequirementCoverage:
    relevant = list(evidence_items)
    source_ids = sorted({source_id for item in relevant for source_id in item["source_ids"]})
    groups = {sources[source_id]["independence_group"] for source_id in source_ids}
    primary_present = any(sources[source_id]["source_class"] == "primary" for source_id in source_ids)
    contrary_present = any(item["direction"] in {"contradicts", "mixed"} for item in relevant)
    verified_present = any(item["verification"] == "verified" for item in relevant)
    target = requirement.get("target_independent_streams", 1)

    required_primary = bool(requirement.get("primary_required", False))
    required_contrary = bool(requirement.get("contrary_required", False))

    if not relevant:
        status = "missing"
    elif (
        len(groups) >= target
        and (not required_primary or primary_present)
        and (not required_contrary or contrary_present)
        and verified_present
    ):
        status = "covered"
    else:
        status = "partial"

    return RequirementCoverage(
        requirement_id=requirement["id"],
        question=requirement["question"],
        criticality=requirement["criticality"],
        source_count=len(source_ids),
        independent_stream_count=len(groups),
        primary_present=primary_present,
        contrary_present=contrary_present,
        verified_evidence_present=verified_present,
        target_streams=target,
        status=status,
    )


def build_coverage_map(
    requirements: dict[str, dict[str, Any]],
    evidence_items: dict[str, dict[str, Any]],
    sources: dict[str, dict[str, Any]],
) -> list[RequirementCoverage]:
    by_requirement: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in evidence_items.values():
        by_requirement[item["requirement_id"]].append(item)

    return [
        _requirement_coverage(requirement, by_requirement.get(requirement_id, []), sources)
        for requirement_id, requirement in sorted(requirements.items())
    ]


def critical_information_gaps(
    coverage: list[RequirementCoverage],
    requirements: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    gaps: list[dict[str, Any]] = []
    for item in coverage:
        if item.status == "covered":
            continue
        requirement = requirements[item.requirement_id]
        missing_conditions: list[str] = []
        if item.independent_stream_count < item.target_streams:
            missing_conditions.append(
                f"needs {item.target_streams - item.independent_stream_count} more independent stream(s)"
            )
        if requirement.get("primary_required") and not item.primary_present:
            missing_conditions.append("needs primary evidence")
        if requirement.get("contrary_required") and not item.contrary_present:
            missing_conditions.append("needs contrary or mixed evidence")
        if not item.verified_evidence_present:
            missing_conditions.append("needs at least one verified evidence item")
        gaps.append(
            {
                "requirement_id": item.requirement_id,
                "question": item.question,
                "criticality": item.criticality,
                "coverage_status": item.status,
                "missing_conditions": missing_conditions,
            }
        )
    return sorted(gaps, key=lambda gap: (-gap["criticality"], gap["requirement_id"]))


def rank_research_options(
    options: dict[str, dict[str, Any]],
    requirements: dict[str, dict[str, Any]],
    coverage: list[RequirementCoverage],
) -> list[dict[str, Any]]:
    """Rank next searches with a transparent bounded Value-of-Information proxy.

    This is not expected monetary value and does not alter probabilities. The
    score prioritises hypothesis discrimination, critical gaps, potential source
    reliability, urgency and accessibility, while subtracting cost.
    """
    coverage_by_id = {item.requirement_id: item for item in coverage}
    ranked: list[dict[str, Any]] = []

    for option_id, option in options.items():
        requirement = requirements[option["requirement_id"]]
        coverage_item = coverage_by_id[option["requirement_id"]]
        gap_multiplier = {"missing": 2, "partial": 1, "covered": 0}[coverage_item.status]
        score_components = {
            "discrimination": 3 * option["expected_discrimination"],
            "criticality": 2 * requirement["criticality"],
            "reliability": 2 * option["reliability_potential"],
            "urgency": option["urgency"],
            "accessibility": option["accessibility"],
            "gap_bonus": 4 * gap_multiplier,
            "cost_penalty": -option["cost"],
        }
        score = sum(score_components.values())
        ranked.append(
            {
                "option_id": option_id,
                "requirement_id": option["requirement_id"],
                "description": option["description"],
                "score": score,
                "components": score_components,
                "blocked": bool(option.get("blocked", False)),
            }
        )

    return sorted(
        ranked,
        key=lambda item: (item["blocked"], -item["score"], item["option_id"]),
    )


def information_sufficiency_status(
    coverage: list[RequirementCoverage],
    sources: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    critical = [item for item in coverage if item.criticality >= 4]
    critical_missing = [item for item in critical if item.status == "missing"]
    critical_not_covered = [item for item in critical if item.status != "covered"]
    covered = [item for item in coverage if item.status == "covered"]
    independent_streams = len({source["independence_group"] for source in sources.values()})
    primary_streams = len(
        {
            source["independence_group"]
            for source in sources.values()
            if source["source_class"] == "primary"
        }
    )
    contrary_critical = sum(1 for item in critical if item.contrary_present)

    reasons: list[str] = []
    if critical_missing:
        status = "insufficient"
        reasons.append("one or more critical requirements have no evidence")
    elif independent_streams < 3:
        status = "insufficient"
        reasons.append("fewer than three independent source streams are present")
    elif critical_not_covered:
        status = "preliminary"
        reasons.append("one or more critical requirements remain only partially covered")
    elif len(covered) < len(coverage):
        status = "developing"
        reasons.append("critical requirements are covered but non-critical gaps remain")
    elif primary_streams == 0 or contrary_critical < len(critical):
        status = "substantial"
        reasons.append("coverage is complete but primary or contradiction coverage is limited")
    else:
        status = "mature"
        reasons.append("all declared requirements and contradiction gates are covered")

    return {
        "status": status,
        "reasons": reasons,
        "requirements_total": len(coverage),
        "requirements_covered": len(covered),
        "critical_requirements_total": len(critical),
        "critical_requirements_covered": len(critical) - len(critical_not_covered),
        "independent_source_streams": independent_streams,
        "primary_source_streams": primary_streams,
        "warning": (
            "Information sufficiency measures research coverage. It does not establish that any "
            "hypothesis is true and does not authorise probability or attribution claims."
        ),
    }


def assess_case(case: Any) -> dict[str, Any]:
    """Produce all five Evidence Acquisition Manager outputs."""
    indexes = validate_case(case)
    coverage = build_coverage_map(
        indexes["requirements"], indexes["evidence_items"], indexes["sources"]
    )
    return {
        "case_id": case["case_id"],
        "engine_version": "0.1.0",
        "coverage_map": [item.as_dict() for item in coverage],
        "source_dependency_graph": source_dependency_graph(indexes["sources"]),
        "critical_information_gaps": critical_information_gaps(
            coverage, indexes["requirements"]
        ),
        "ranked_next_search_queue": rank_research_options(
            indexes["research_options"], indexes["requirements"], coverage
        ),
        "information_sufficiency": information_sufficiency_status(
            coverage, indexes["sources"]
        ),
    }

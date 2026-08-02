"""Domain-module and historical-comparison validation for PAE v0.4."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

from .acquisition import AcquisitionError

DOMAIN_INTERFACE_VERSION = "0.1"
LIBRARY_VERSION = "0.1"
CASE_CLASSIFICATIONS = {
    "strong_official_attribution",
    "parliamentary_attribution",
    "official_attribution_contested",
    "official_attribution_unresolved",
    "organic_multi_causal_comparator",
    "non_coercive_forced_displacement_comparator",
}
RESOLUTION_STATUSES = {
    "institutionally_attributed",
    "politically_attributed_not_judicially_resolved",
    "contested",
    "unresolved",
    "non_coercive_comparator",
    "multi_causal_comparator",
}
EVIDENCE_QUALITY = {"low", "moderate", "high"}
REQUIRED_MIGRATION_CATEGORIES = {
    "border_enforcement_baseline",
    "command_and_control",
    "transport_and_logistics",
    "mobilisation_networks",
    "diplomatic_context",
    "timing_and_sequence",
    "restoration_of_control",
    "financial_or_operational_links",
    "humanitarian_and_economic_drivers",
    "third_state_contacts",
}
REQUIRED_INFERENCE_GUARDS = {
    "motive_does_not_establish_conduct",
    "capability_does_not_establish_action",
    "sequence_does_not_establish_causation",
    "weak_enforcement_does_not_establish_permission",
    "foreign_hostility_does_not_establish_command",
}


def _string(record: dict[str, Any], key: str, context: str) -> str:
    value = record.get(key)
    if not isinstance(value, str) or not value.strip():
        raise AcquisitionError(f"{context}: {key} must be a non-empty string")
    return value.strip()


def _string_list(record: dict[str, Any], key: str, context: str) -> list[str]:
    value = record.get(key)
    if not isinstance(value, list) or not value or any(
        not isinstance(item, str) or not item.strip() for item in value
    ):
        raise AcquisitionError(f"{context}: {key} must be a non-empty list of strings")
    return [item.strip() for item in value]


def validate_domain_module(module: Any) -> dict[str, Any]:
    if not isinstance(module, dict):
        raise AcquisitionError("domain module must be an object")
    if module.get("interface_version") != DOMAIN_INTERFACE_VERSION:
        raise AcquisitionError(
            f"domain module: interface_version must be {DOMAIN_INTERFACE_VERSION!r}"
        )
    domain_id = _string(module, "domain_id", "domain module")
    _string(module, "version", "domain module")
    _string(module, "title", "domain module")
    _string(module, "scope", "domain module")
    _string_list(module, "applicable_claims", "domain module")
    _string_list(module, "required_hypothesis_classes", "domain module")

    categories = module.get("evidence_categories")
    if not isinstance(categories, list) or not categories:
        raise AcquisitionError("domain module: evidence_categories must be a non-empty list")
    category_ids: set[str] = set()
    for position, category in enumerate(categories, start=1):
        context = f"evidence_categories[{position}]"
        if not isinstance(category, dict):
            raise AcquisitionError(f"{context}: must be an object")
        category_id = _string(category, "id", context)
        if category_id in category_ids:
            raise AcquisitionError(f"{context}: duplicate id {category_id!r}")
        category_ids.add(category_id)
        _string(category, "question", context)
        _string_list(category, "preferred_evidence", context)
        _string_list(category, "alternative_explanations", context)

    indicators = module.get("indicators")
    if not isinstance(indicators, list) or not indicators:
        raise AcquisitionError("domain module: indicators must be a non-empty list")
    indicator_ids: set[str] = set()
    for position, indicator in enumerate(indicators, start=1):
        context = f"indicators[{position}]"
        if not isinstance(indicator, dict):
            raise AcquisitionError(f"{context}: must be an object")
        indicator_id = _string(indicator, "id", context)
        if indicator_id in indicator_ids:
            raise AcquisitionError(f"{context}: duplicate id {indicator_id!r}")
        indicator_ids.add(indicator_id)
        category_id = _string(indicator, "category_id", context)
        if category_id not in category_ids:
            raise AcquisitionError(f"{context}: unknown category {category_id!r}")
        _string(indicator, "observation", context)
        _string(indicator, "diagnostic_limit", context)
        _string_list(indicator, "alternative_explanations", context)

    profile = module.get("default_sufficiency_profile")
    if not isinstance(profile, dict):
        raise AcquisitionError("domain module: default_sufficiency_profile must be an object")
    _string(profile, "name", "default_sufficiency_profile")
    for field in ("minimum_independent_streams", "criticality_threshold"):
        value = profile.get(field)
        if not isinstance(value, int) or value < 1:
            raise AcquisitionError(
                f"default_sufficiency_profile: {field} must be a positive integer"
            )
    for field in (
        "require_primary_for_critical",
        "require_contrary_for_critical",
        "block_on_unsearched_critical",
    ):
        if not isinstance(profile.get(field), bool):
            raise AcquisitionError(
                f"default_sufficiency_profile: {field} must be boolean"
            )

    guards = module.get("prohibited_inference_jumps")
    if not isinstance(guards, list) or not guards:
        raise AcquisitionError(
            "domain module: prohibited_inference_jumps must be a non-empty list"
        )
    guard_ids: set[str] = set()
    for position, guard in enumerate(guards, start=1):
        context = f"prohibited_inference_jumps[{position}]"
        if not isinstance(guard, dict):
            raise AcquisitionError(f"{context}: must be an object")
        guard_id = _string(guard, "id", context)
        if guard_id in guard_ids:
            raise AcquisitionError(f"{context}: duplicate id {guard_id!r}")
        guard_ids.add(guard_id)
        _string(guard, "rule", context)
        _string(guard, "required_bridge_evidence", context)

    return {
        "domain_id": domain_id,
        "category_ids": category_ids,
        "indicator_ids": indicator_ids,
        "guard_ids": guard_ids,
        "profile": profile,
    }


def _validate_source(source: Any, context: str) -> None:
    if not isinstance(source, dict):
        raise AcquisitionError(f"{context}: must be an object")
    for field in ("institution", "title", "date", "url", "supports"):
        _string(source, field, context)


def validate_historical_library(
    library: Any, module_index: dict[str, Any] | None = None
) -> dict[str, Any]:
    if not isinstance(library, dict):
        raise AcquisitionError("historical library must be an object")
    if library.get("library_version") != LIBRARY_VERSION:
        raise AcquisitionError(
            f"historical library: library_version must be {LIBRARY_VERSION!r}"
        )
    domain_id = _string(library, "domain_id", "historical library")
    if module_index and domain_id != module_index["domain_id"]:
        raise AcquisitionError("historical library: domain_id does not match module")
    _string(library, "title", "historical library")
    _string(library, "method_note", "historical library")

    cases = library.get("cases")
    if not isinstance(cases, list) or not cases:
        raise AcquisitionError("historical library: cases must be a non-empty list")
    case_ids: set[str] = set()
    classification_counts: Counter[str] = Counter()
    resolution_counts: Counter[str] = Counter()
    for position, case in enumerate(cases, start=1):
        context = f"cases[{position}]"
        if not isinstance(case, dict):
            raise AcquisitionError(f"{context}: must be an object")
        case_id = _string(case, "id", context)
        if case_id in case_ids:
            raise AcquisitionError(f"{context}: duplicate id {case_id!r}")
        case_ids.add(case_id)
        for field in (
            "title",
            "period",
            "mechanism_summary",
            "public_evidence_summary",
            "counterevidence_and_alternatives",
            "limitations",
            "analytical_lessons",
        ):
            _string(case, field, context)
        _string_list(case, "actors", context)
        _string_list(case, "relevant_indicators", context)
        classification = _string(case, "classification", context)
        if classification not in CASE_CLASSIFICATIONS:
            raise AcquisitionError(
                f"{context}: unsupported classification {classification!r}"
            )
        resolution = _string(case, "resolution_status", context)
        if resolution not in RESOLUTION_STATUSES:
            raise AcquisitionError(
                f"{context}: unsupported resolution_status {resolution!r}"
            )
        quality = _string(case, "public_evidence_quality", context)
        if quality not in EVIDENCE_QUALITY:
            raise AcquisitionError(
                f"{context}: unsupported public_evidence_quality {quality!r}"
            )
        if classification == "strong_official_attribution" and quality != "high":
            raise AcquisitionError(
                f"{context}: strong_official_attribution requires high public evidence quality"
            )
        if classification in {
            "official_attribution_contested",
            "official_attribution_unresolved",
        } and resolution not in {"contested", "unresolved"}:
            raise AcquisitionError(
                f"{context}: contested or unresolved attribution must preserve that status"
            )
        sources = case.get("sources")
        if not isinstance(sources, list) or not sources:
            raise AcquisitionError(f"{context}: sources must be a non-empty list")
        for source_position, source in enumerate(sources, start=1):
            _validate_source(source, f"{context} sources[{source_position}]")
        if module_index:
            unknown_indicators = (
                set(case["relevant_indicators"]) - module_index["indicator_ids"]
            )
            if unknown_indicators:
                raise AcquisitionError(
                    f"{context}: unknown indicators {', '.join(sorted(unknown_indicators))}"
                )
        classification_counts[classification] += 1
        resolution_counts[resolution] += 1

    comparator_classes = {
        "organic_multi_causal_comparator",
        "non_coercive_forced_displacement_comparator",
    }
    if not (set(classification_counts) & comparator_classes):
        raise AcquisitionError(
            "historical library: at least one non-coercive or organic comparator is required"
        )
    if len(classification_counts) < 4:
        raise AcquisitionError(
            "historical library: at least four distinct classifications are required"
        )

    return {
        "domain_id": domain_id,
        "case_ids": case_ids,
        "classification_counts": dict(sorted(classification_counts.items())),
        "resolution_counts": dict(sorted(resolution_counts.items())),
    }


def assess_domain(module: Any, library: Any) -> dict[str, Any]:
    module_index = validate_domain_module(module)
    library_index = validate_historical_library(library, module_index)
    missing_categories = sorted(
        REQUIRED_MIGRATION_CATEGORIES - module_index["category_ids"]
    )
    missing_guards = sorted(
        REQUIRED_INFERENCE_GUARDS - module_index["guard_ids"]
    )
    return {
        "domain_id": module_index["domain_id"],
        "interface_version": DOMAIN_INTERFACE_VERSION,
        "library_version": LIBRARY_VERSION,
        "evidence_categories": len(module_index["category_ids"]),
        "indicators": len(module_index["indicator_ids"]),
        "historical_cases": len(library_index["case_ids"]),
        "classification_counts": library_index["classification_counts"],
        "resolution_counts": library_index["resolution_counts"],
        "required_category_coverage": {
            "complete": not missing_categories,
            "missing": missing_categories,
        },
        "inference_guard_coverage": {
            "complete": not missing_guards,
            "missing": missing_guards,
        },
        "default_sufficiency_profile": module_index["profile"]["name"],
        "warning": (
            "Historical classification records public evidence and institutional "
            "attribution. It is not a judicial finding and must not be converted "
            "directly into a probability for a new case."
        ),
    }


def parser() -> argparse.ArgumentParser:
    command = argparse.ArgumentParser(
        description="Validate and summarise a PAE domain module and comparison library."
    )
    command.add_argument("module", type=Path)
    command.add_argument("library", type=Path)
    command.add_argument("--output", type=Path)
    return command


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        module = json.loads(args.module.read_text(encoding="utf-8"))
        library = json.loads(args.library.read_text(encoding="utf-8"))
        result = assess_domain(module, library)
    except (OSError, json.JSONDecodeError, AcquisitionError) as exc:
        print(f"PAE domain assessment failed: {exc}", file=sys.stderr)
        return 2
    rendered = json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

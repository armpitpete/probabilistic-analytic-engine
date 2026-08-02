from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from pae import AcquisitionError
from pae.domains import (
    REQUIRED_INFERENCE_GUARDS,
    REQUIRED_MIGRATION_CATEGORIES,
    assess_domain,
    validate_domain_module,
    validate_historical_library,
)


MODULE = Path("domains/state-migration-coercion/module.json")
LIBRARY = Path("domains/state-migration-coercion/historical-cases.json")


def load_module() -> dict:
    return json.loads(MODULE.read_text(encoding="utf-8"))


def load_library() -> dict:
    return json.loads(LIBRARY.read_text(encoding="utf-8"))


def test_domain_module_covers_required_categories_and_guards() -> None:
    result = assess_domain(load_module(), load_library())
    assert result["required_category_coverage"] == {"complete": True, "missing": []}
    assert result["inference_guard_coverage"] == {"complete": True, "missing": []}
    assert result["evidence_categories"] >= len(REQUIRED_MIGRATION_CATEGORIES)
    assert result["indicators"] >= 10


def test_library_contains_varied_attribution_and_comparator_classes() -> None:
    result = assess_domain(load_module(), load_library())
    classifications = result["classification_counts"]
    assert len(classifications) >= 4
    assert classifications["strong_official_attribution"] >= 1
    assert classifications["official_attribution_contested"] >= 1
    assert classifications["official_attribution_unresolved"] >= 1
    assert classifications["non_coercive_forced_displacement_comparator"] >= 1
    assert classifications["organic_multi_causal_comparator"] >= 1


def test_all_historical_cases_have_official_sources_and_limitations() -> None:
    library = load_library()
    for case in library["cases"]:
        assert case["sources"]
        assert case["limitations"].strip()
        assert case["counterevidence_and_alternatives"].strip()
        for source in case["sources"]:
            assert source["url"].startswith("https://")
            assert source["institution"].strip()
            assert source["supports"].strip()


def test_strong_attribution_requires_high_public_evidence_quality() -> None:
    module_index = validate_domain_module(load_module())
    library = load_library()
    case = next(
        case
        for case in library["cases"]
        if case["classification"] == "strong_official_attribution"
    )
    case["public_evidence_quality"] = "moderate"
    with pytest.raises(AcquisitionError, match="requires high public evidence quality"):
        validate_historical_library(library, module_index)


def test_unresolved_attribution_cannot_be_relabelled_as_resolved() -> None:
    module_index = validate_domain_module(load_module())
    library = load_library()
    case = next(
        case
        for case in library["cases"]
        if case["classification"] == "official_attribution_unresolved"
    )
    case["resolution_status"] = "institutionally_attributed"
    with pytest.raises(AcquisitionError, match="must preserve that status"):
        validate_historical_library(library, module_index)


def test_unknown_indicator_in_library_fails() -> None:
    module_index = validate_domain_module(load_module())
    library = load_library()
    library["cases"][0]["relevant_indicators"].append("unknown-indicator")
    with pytest.raises(AcquisitionError, match="unknown indicators"):
        validate_historical_library(library, module_index)


def test_library_must_include_non_coercive_or_organic_comparator() -> None:
    module_index = validate_domain_module(load_module())
    library = load_library()
    library["cases"] = [
        case
        for case in library["cases"]
        if "comparator" not in case["classification"]
    ]
    with pytest.raises(AcquisitionError, match="comparator is required"):
        validate_historical_library(library, module_index)


def test_module_rejects_unknown_indicator_category() -> None:
    module = load_module()
    module["indicators"][0]["category_id"] = "missing-category"
    with pytest.raises(AcquisitionError, match="unknown category"):
        validate_domain_module(module)


def test_module_guard_ids_include_all_required_inference_controls() -> None:
    module = load_module()
    guard_ids = {guard["id"] for guard in module["prohibited_inference_jumps"]}
    assert REQUIRED_INFERENCE_GUARDS <= guard_ids


def test_domain_assessment_is_deterministic() -> None:
    first = assess_domain(load_module(), load_library())
    second = assess_domain(copy.deepcopy(load_module()), copy.deepcopy(load_library()))
    assert first == second
    assert "not a judicial finding" in first["warning"]

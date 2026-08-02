from __future__ import annotations

import json
from pathlib import Path

import pytest

from pae import AcquisitionError, assess_case, validate_case


FIXTURE = Path("fixtures/ceuta-2026-method-fixture-v0.3.json")


def load_case() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def test_typed_dependency_graph_distinguishes_republication() -> None:
    graph = assess_case(load_case())["typed_source_dependency_graph"]
    assert graph["status"] == "structured"
    assert graph["relation_counts"]["republished_from"] == 1
    assert graph["edges"][0]["from"] == "source-a"


def test_coverage_is_reported_for_every_hypothesis() -> None:
    rows = assess_case(load_case())["coverage_by_hypothesis"]
    assert len(rows) == len(load_case()["hypotheses"])
    domestic = next(row for row in rows if row["hypothesis_id"] == "h-domestic")
    assert domestic["supports"] == 1
    assert domestic["independent_streams"] >= 1


def test_search_audit_preserves_languages_and_outcomes() -> None:
    audit = assess_case(load_case())["search_audit"]
    assert audit["searches_total"] == 3
    assert audit["result_counts"] == {"found": 1, "inaccessible": 1, "no_result": 1}
    assert audit["languages"] == ["en", "fr"]


def test_search_failure_is_not_evidence_of_absence() -> None:
    summary = assess_case(load_case())["absence_summary"]
    assert summary["evidence_of_absence_count"] == 0
    assert summary["search_failure_count"] == 3
    assert "not evidence" in summary["warning"]


def test_configurable_profile_blocks_unsearched_critical_requirement() -> None:
    sufficiency = assess_case(load_case())["information_sufficiency_v2"]
    assert sufficiency["profile"] == "high-risk-public-attribution-v1"
    assert sufficiency["status"] == "insufficient"
    assert "critical_unsearched:req-mobilisation" in sufficiency["failures"]


def test_value_of_information_prioritises_discriminating_work() -> None:
    queue = assess_case(load_case())["ranked_next_search_queue_v2"]
    assert queue[0]["option_id"] in {"search-orders", "search-origin"}
    assert queue[-1]["option_id"] == "search-commentary"
    assert queue[0]["components"]["analytical_impact"] > queue[-1]["components"]["analytical_impact"]


def test_unknown_dependency_relation_fails() -> None:
    case = load_case()
    case["sources"][1]["dependency_links"][0]["relation_type"] = "copied_somehow"
    with pytest.raises(AcquisitionError, match="unsupported relation_type"):
        validate_case(case)


def test_evidence_of_absence_must_contradict() -> None:
    case = load_case()
    case["evidence_items"][0]["absence_status"] = "evidence_of_absence"
    case["evidence_items"][0]["hypothesis_impacts"] = [{"hypothesis_id": "h-domestic", "direction": "supports"}]
    with pytest.raises(AcquisitionError, match="must contradict or mix"):
        validate_case(case)


def test_search_diary_unknown_result_fails() -> None:
    case = load_case()
    case["search_diary"][0]["result_status"] = "probably_nothing"
    with pytest.raises(AcquisitionError, match="unsupported result_status"):
        validate_case(case)


def test_negative_record_must_reference_known_search() -> None:
    case = load_case()
    case["negative_evidence"][0]["search_ids"] = ["missing-search"]
    with pytest.raises(AcquisitionError, match="unknown search ids"):
        validate_case(case)


def test_protocol_is_optional_for_accepted_v02_cases() -> None:
    case = load_case()
    case.pop("research_protocol_version")
    for source in case["sources"]:
        source.pop("dependency_links")
    for item in case["evidence_items"]:
        item.pop("absence_status")
        item.pop("hypothesis_impacts")
    case.pop("search_diary")
    case.pop("negative_evidence")
    case.pop("sufficiency_profile")
    for option in case["research_options"]:
        for key in ("probability_of_resolution", "expected_analytical_impact", "time_sensitivity", "effort"):
            option.pop(key)
    result = assess_case(case)
    assert result["research_protocol_version"] is None
    assert result["typed_source_dependency_graph"]["status"] == "not_available"

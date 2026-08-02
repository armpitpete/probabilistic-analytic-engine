from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from pae import AcquisitionError, assess_case, validate_case


FIXTURE = Path("fixtures/ceuta-2026-method-fixture.json")


def load_case() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def test_fixture_is_valid_and_remains_insufficient() -> None:
    result = assess_case(load_case())
    assert result["information_sufficiency"]["status"] == "insufficient"
    assert result["information_sufficiency"]["independent_source_streams"] == 2
    assert result["critical_information_gaps"]


def test_repeated_reporting_is_one_independent_stream() -> None:
    result = assess_case(load_case())
    components = result["source_dependency_graph"]["independence_components"]
    reporting = next(
        item for item in components if item["independence_group"] == "fixture-wire-origin-a"
    )
    assert reporting["source_ids"] == ["source-report-a", "source-report-a-republication"]

    enforcement = next(
        row for row in result["coverage_map"] if row["requirement_id"] == "req-enforcement"
    )
    assert enforcement["source_count"] == 2
    assert enforcement["independent_stream_count"] == 1


def test_value_of_information_prioritises_critical_discriminating_search() -> None:
    queue = assess_case(load_case())["ranked_next_search_queue"]
    assert queue[0]["option_id"] == "search-border-orders"
    assert queue[0]["components"]["discrimination"] > 0
    assert queue[0]["components"]["gap_bonus"] > 0


def test_duplicate_ids_are_rejected() -> None:
    case = load_case()
    case["hypotheses"].append(copy.deepcopy(case["hypotheses"][0]))
    with pytest.raises(AcquisitionError, match="duplicate id"):
        validate_case(case)


def test_unknown_source_reference_is_rejected() -> None:
    case = load_case()
    case["evidence_items"][0]["source_ids"] = ["missing-source"]
    with pytest.raises(AcquisitionError, match="unknown sources"):
        validate_case(case)


def test_source_dependency_cycles_are_rejected() -> None:
    case = load_case()
    case["sources"][0]["derived_from"] = ["source-report-a-republication"]
    with pytest.raises(AcquisitionError, match="dependency cycle"):
        validate_case(case)

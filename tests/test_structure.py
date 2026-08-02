from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from pae import AcquisitionError, assess_case, validate_case
from pae.structure import case_snapshot


FIXTURE = Path("fixtures/ceuta-2026-method-fixture-v0.2.json")


def load_case() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def test_v02_fixture_has_deterministic_snapshot_and_complete_registry() -> None:
    case = load_case()
    first = assess_case(case)
    second = assess_case(copy.deepcopy(case))
    assert first["engine_version"] == "0.2.0"
    assert first["case_snapshot"] == second["case_snapshot"]
    assert len(first["case_snapshot"]["sha256"]) == 64
    assert first["hypothesis_analysis"]["status"] == "complete"
    assert first["hypothesis_analysis"]["completeness"]["checks"]["mixed_cause_present"]
    assert first["hypothesis_analysis"]["completeness"]["checks"]["insufficient_information_present"]


def test_case_snapshot_changes_when_case_changes() -> None:
    case = load_case()
    original = case_snapshot(case)["sha256"]
    case["title"] += " changed"
    assert case_snapshot(case)["sha256"] != original


def test_missing_source_provenance_fails() -> None:
    case = load_case()
    del case["sources"][0]["content_sha256"]
    with pytest.raises(AcquisitionError, match="content_sha256"):
        validate_case(case)


def test_invalid_content_hash_fails() -> None:
    case = load_case()
    case["sources"][0]["content_sha256"] = "not-a-hash"
    with pytest.raises(AcquisitionError, match="64 lowercase hexadecimal"):
        validate_case(case)


def test_source_authority_is_claim_specific() -> None:
    result = assess_case(load_case())
    assert result["provenance_summary"]["authority_entries"] == 3
    assert result["provenance_summary"]["status"] == "structured"


def test_missing_mixed_cause_hypothesis_fails_when_required() -> None:
    case = load_case()
    case["hypotheses"] = [item for item in case["hypotheses"] if item["class"] != "mixed"]
    case["relationships"] = [item for item in case["relationships"] if item["from"] != "h-mixed" and item["to"] != "h-mixed"]
    for requirement in case["requirements"]:
        requirement["hypothesis_ids"] = [hypothesis_id for hypothesis_id in requirement["hypothesis_ids"] if hypothesis_id != "h-mixed"]
    with pytest.raises(AcquisitionError, match="mixed-cause hypothesis"):
        validate_case(case)


def test_missing_insufficient_information_hypothesis_fails() -> None:
    case = load_case()
    case["hypotheses"] = [item for item in case["hypotheses"] if item["class"] != "insufficient_information"]
    case["relationships"] = [item for item in case["relationships"] if item["from"] != "h-insufficient" and item["to"] != "h-insufficient"]
    with pytest.raises(AcquisitionError, match="insufficient-information"):
        validate_case(case)


def test_relationship_to_unknown_hypothesis_fails() -> None:
    case = load_case()
    case["relationships"][0]["to"] = "h-unknown"
    with pytest.raises(AcquisitionError, match="unknown hypothesis"):
        validate_case(case)


def test_predictions_and_disconfirmers_are_required() -> None:
    case = load_case()
    case["hypotheses"][0]["disconfirmers"] = []
    with pytest.raises(AcquisitionError, match="disconfirmers"):
        validate_case(case)


def test_legacy_v01_case_remains_supported() -> None:
    case = load_case()
    for key in ("schema_version", "case_version", "domain_id", "causal_profile", "relationships"):
        case.pop(key)
    for hypothesis in case["hypotheses"]:
        for key in ("class", "actors", "mechanism", "timeframe", "outcome", "predictions", "disconfirmers"):
            hypothesis.pop(key)
    for source in case["sources"]:
        for key in ("url", "publisher", "author", "published_at", "collected_at", "archive_url", "content_sha256", "language", "jurisdiction", "capture_limitations", "authority"):
            source.pop(key)
    for item in case["evidence_items"]:
        for key in ("proposition", "source_locator", "inspectable_material", "authentication_status", "relevance", "limitations", "reviewer_notes"):
            item.pop(key)
    result = assess_case(case)
    assert result["engine_version"] == "0.1.0"
    assert result["hypothesis_analysis"]["status"] == "legacy-v0.1"

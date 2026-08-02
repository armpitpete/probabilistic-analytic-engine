from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from pae.acquisition import AcquisitionError
from pae.calculation import (
    calculate_draft,
    canonical_draft_hash,
    canonical_review_hash,
    review_calculation,
    validate_calculation_plan,
)

FIXTURE = Path("fixtures/calculation-method-fixture-v0.1.json")


def load_plan() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def test_calculation_is_normalised_and_pending_review() -> None:
    draft = calculate_draft(load_plan())
    assert sum(
        item["point_estimate"] for item in draft["posterior"].values()
    ) == pytest.approx(1)
    assert draft["review_status"] == "pending"
    assert draft["requires_post_calculation_review"] is True
    assert draft["automatic_attribution_performed"] is False
    assert draft["public_conclusion_authorised"] is False
    assert draft["draft_sha256"] == canonical_draft_hash(draft)


def test_bounds_contain_point_estimates() -> None:
    draft = calculate_draft(load_plan())
    for item in draft["posterior"].values():
        assert item["minimum_sensitivity_bound"] <= item["point_estimate"]
        assert item["point_estimate"] <= item["maximum_sensitivity_bound"]


def test_leave_one_stream_out_is_reported() -> None:
    draft = calculate_draft(load_plan())
    omitted = {
        row["omitted_independence_group"]
        for row in draft["sensitivity"]["leave_one_independence_group_out"]
    }
    assert omitted == {"stream-operational", "stream-participant"}


def test_failed_sufficiency_gate_blocks_calculation() -> None:
    plan = load_plan()
    plan["sufficiency_gate"]["passed"] = False
    plan["sufficiency_gate"]["actual_status"] = "preliminary"
    with pytest.raises(AcquisitionError, match="passed must be true"):
        calculate_draft(plan)


def test_live_unresolved_case_is_rejected() -> None:
    plan = load_plan()
    plan["safety"]["live_unresolved_case"] = True
    with pytest.raises(AcquisitionError, match="live_unresolved_case"):
        validate_calculation_plan(plan)


def test_automatic_attribution_is_rejected() -> None:
    plan = load_plan()
    plan["safety"]["automatic_attribution_enabled"] = True
    with pytest.raises(
        AcquisitionError, match="automatic_attribution_enabled"
    ):
        validate_calculation_plan(plan)


def test_public_conclusion_is_rejected() -> None:
    plan = load_plan()
    plan["safety"]["public_conclusion_authorised"] = True
    with pytest.raises(
        AcquisitionError, match="public_conclusion_authorised"
    ):
        validate_calculation_plan(plan)


def test_preparer_and_approver_must_differ() -> None:
    plan = load_plan()
    plan["analyst_authorisation"][
        "approved_for_calculation_by"
    ] = "analyst-alpha"
    with pytest.raises(AcquisitionError, match="must differ"):
        validate_calculation_plan(plan)


def test_base_priors_must_sum_to_one() -> None:
    plan = load_plan()
    plan["hypotheses"][0]["prior"]["base"] = 0.5
    with pytest.raises(AcquisitionError, match="base priors must total 1"):
        validate_calculation_plan(plan)


def test_nonexclusive_pair_cannot_enter_exclusive_group() -> None:
    plan = load_plan()
    plan["nonexclusive_relationships"] = [
        {
            "from": "h-organic",
            "to": "h-deliberate",
            "type": "compatible",
        }
    ]
    with pytest.raises(AcquisitionError, match="non-exclusive pair"):
        validate_calculation_plan(plan)


def test_independence_group_total_weight_cannot_exceed_one() -> None:
    plan = load_plan()
    duplicate = copy.deepcopy(plan["evidence_updates"][0])
    duplicate["id"] = "e-operational-copy"
    duplicate["weight"] = 0.1
    plan["evidence_updates"].append(duplicate)
    with pytest.raises(AcquisitionError, match="exceeds 1"):
        validate_calculation_plan(plan)


def test_multiplier_ranges_must_be_ordered() -> None:
    plan = load_plan()
    plan["evidence_updates"][0]["multipliers"]["h-deliberate"][
        "minimum"
    ] = 6
    with pytest.raises(
        AcquisitionError, match="minimum <= base <= maximum"
    ):
        validate_calculation_plan(plan)


def valid_review(draft: dict) -> dict:
    return {
        "draft_sha256": draft["draft_sha256"],
        "reviewer_id": "reviewer-gamma",
        "decision": "accept_for_historical_pilot",
        "rationale": (
            "The arithmetic and declared assumptions are suitable for the "
            "controlled historical pilot."
        ),
        "reviewed_at": "2026-08-02T13:00:00+01:00",
        "public_conclusion_authorised": False,
    }


def test_separate_reviewer_can_accept_exact_draft() -> None:
    draft = calculate_draft(load_plan())
    record = review_calculation(draft, valid_review(draft))
    assert record["accepted_for_historical_pilot"] is True
    assert record["public_conclusion_authorised"] is False
    assert record["review_record_sha256"] == canonical_review_hash(record)


def test_reviewer_cannot_be_preparer() -> None:
    draft = calculate_draft(load_plan())
    review = valid_review(draft)
    review["reviewer_id"] = draft["prepared_by"]
    with pytest.raises(AcquisitionError, match="must differ"):
        review_calculation(draft, review)


def test_review_must_match_exact_draft_hash() -> None:
    draft = calculate_draft(load_plan())
    review = valid_review(draft)
    review["draft_sha256"] = "b" * 64
    with pytest.raises(AcquisitionError, match="exact draft"):
        review_calculation(draft, review)


def test_tampered_draft_is_rejected() -> None:
    draft = calculate_draft(load_plan())
    draft["posterior"]["h-organic"]["point_estimate"] = 0.99
    with pytest.raises(AcquisitionError, match="does not match"):
        review_calculation(draft, valid_review(draft))

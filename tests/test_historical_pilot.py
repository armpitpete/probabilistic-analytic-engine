from __future__ import annotations

import json
from pathlib import Path

import pytest

from pae.acquisition import AcquisitionError
from pae.historical_pilot import (
    canonical_packet_hash,
    run_historical_pilot,
    validate_evidence_cut,
)

ROOT = Path("pilots/belarus-eu-2021")


def load(name: str) -> dict:
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


def run() -> dict:
    return run_historical_pilot(
        load("evidence-cut.json"),
        load("calculation-plan.json"),
        load("review.json"),
        load("outcome.json"),
    )


def test_pilot_predicts_predeclared_institutional_resolution() -> None:
    result = run()
    assert result["scoring"]["leading_hypothesis_matches_resolution"] is True
    assert result["resolved_hypothesis_id"] == "h-state-facilitation-primary"
    assert result["resolved_hypothesis_leads_all_leave_one_out_tests"] is True


def test_pilot_preserves_safety_and_external_review_limits() -> None:
    result = run()
    assert result["automatic_attribution_performed"] is False
    assert result["public_conclusion_authorised"] is False
    assert result["external_human_validation_completed"] is False
    assert "not a judicial finding" in result["warning"]


def test_committed_draft_matches_recalculation() -> None:
    result = run()
    frozen = load("calculation-draft.json")
    assert result["calculation_draft_sha256"] == frozen["draft_sha256"]


def test_evidence_packet_hash_is_deterministic() -> None:
    packet = load("evidence-cut.json")
    assert packet["packet_sha256"] == canonical_packet_hash(packet)


def test_evidence_source_after_cutoff_is_rejected() -> None:
    packet = load("evidence-cut.json")
    packet["sources"][0]["date"] = "2021-11-11"
    packet["packet_sha256"] = canonical_packet_hash(packet)
    with pytest.raises(AcquisitionError, match="after the evidence cutoff"):
        validate_evidence_cut(packet)


def test_tampered_evidence_packet_is_rejected() -> None:
    packet = load("evidence-cut.json")
    packet["title"] = "tampered"
    with pytest.raises(AcquisitionError, match="does not match"):
        validate_evidence_cut(packet)


def test_plan_snapshot_must_match_evidence_packet() -> None:
    plan = load("calculation-plan.json")
    plan["case_snapshot_sha256"] = "f" * 64
    with pytest.raises(AcquisitionError, match="must match the evidence packet"):
        run_historical_pilot(
            load("evidence-cut.json"), plan, load("review.json"), load("outcome.json")
        )


def test_plan_provenance_must_reference_cutoff_sources() -> None:
    plan = load("calculation-plan.json")
    plan["evidence_updates"][0]["provenance"] = ["unknown-source"]
    with pytest.raises(AcquisitionError, match="source IDs"):
        run_historical_pilot(
            load("evidence-cut.json"), plan, load("review.json"), load("outcome.json")
        )


def test_review_must_match_recalculated_draft() -> None:
    review = load("review.json")
    review["draft_sha256"] = "e" * 64
    with pytest.raises(AcquisitionError, match="exact draft"):
        run_historical_pilot(
            load("evidence-cut.json"),
            load("calculation-plan.json"),
            review,
            load("outcome.json"),
        )


def test_outcome_source_must_be_after_cutoff() -> None:
    outcome = load("outcome.json")
    outcome["outcome_sources"][0]["date"] = "2021-11-10"
    with pytest.raises(AcquisitionError, match="must be after"):
        run_historical_pilot(
            load("evidence-cut.json"),
            load("calculation-plan.json"),
            load("review.json"),
            outcome,
        )


def test_outcome_hypothesis_must_exist() -> None:
    outcome = load("outcome.json")
    outcome["resolved_hypothesis_id"] = "h-unknown"
    with pytest.raises(AcquisitionError, match="not in the pilot"):
        run_historical_pilot(
            load("evidence-cut.json"),
            load("calculation-plan.json"),
            load("review.json"),
            outcome,
        )


def test_brier_and_log_scores_are_non_negative() -> None:
    scoring = run()["scoring"]
    assert scoring["multiclass_brier_score"] >= 0
    assert scoring["logarithmic_score"] >= 0


def test_pilot_rejects_non_accepting_review() -> None:
    review = load("review.json")
    review["decision"] = "revise"
    with pytest.raises(AcquisitionError, match="must be accepted"):
        run_historical_pilot(
            load("evidence-cut.json"),
            load("calculation-plan.json"),
            review,
            load("outcome.json"),
        )

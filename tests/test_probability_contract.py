from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from pae import AcquisitionError
from pae.probability_contract import (
    assess_probability_contract,
    canonical_revision_hash,
    validate_probability_contract,
)


FIXTURE = Path("fixtures/probability-contract-v0.1.json")


def load_contract() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def test_contract_validates_without_calculating_or_authorising() -> None:
    result = assess_probability_contract(load_contract())
    assert result["contract_version"] == "0.1"
    assert result["calculation_performed"] is False
    assert result["automatic_attribution_enabled"] is False
    assert result["public_conclusion_authorised"] is False
    assert result["sufficiency_gate"]["passed"] is False
    assert result["sufficiency_gate"]["probability_updates_allowed"] is False


def test_automatic_attribution_cannot_be_enabled() -> None:
    contract = load_contract()
    contract["safety"]["automatic_attribution_enabled"] = True
    with pytest.raises(AcquisitionError, match="automatic_attribution_enabled must be false"):
        validate_probability_contract(contract)


def test_public_conclusion_cannot_be_authorised() -> None:
    contract = load_contract()
    contract["safety"]["public_conclusion_authorised"] = True
    with pytest.raises(AcquisitionError, match="public_conclusion_authorised must be false"):
        validate_probability_contract(contract)


def test_failed_sufficiency_gate_forbids_updates() -> None:
    contract = load_contract()
    contract["sufficiency_gate"]["probability_updates_allowed"] = True
    with pytest.raises(AcquisitionError, match="failed gate forbids probability updates"):
        validate_probability_contract(contract)


def test_probability_range_must_be_valid() -> None:
    contract = load_contract()
    contract["hypotheses"][0]["prior"]["maximum"] = 1.1
    with pytest.raises(AcquisitionError, match="number from 0 to 1"):
        validate_probability_contract(contract)


def test_point_estimate_must_fall_inside_declared_range() -> None:
    contract = load_contract()
    contract["hypotheses"][0]["prior"]["point_estimate"] = 0.8
    with pytest.raises(AcquisitionError, match="must fall within the range"):
        validate_probability_contract(contract)


def test_exclusive_group_point_estimates_must_total_one() -> None:
    contract = load_contract()
    contract["exclusive_groups"][0]["point_estimates"]["h-organic"] = 0.3
    with pytest.raises(AcquisitionError, match="must total 1"):
        validate_probability_contract(contract)


def test_nested_hypothesis_cannot_be_summed_as_exclusive() -> None:
    contract = load_contract()
    group = contract["exclusive_groups"][0]
    group["hypothesis_ids"].append("h-mixed")
    group["point_estimates"] = {
        "h-organic": 0.25,
        "h-domestic": 0.25,
        "h-foreign-direct": 0.05,
        "h-insufficient": 0.2,
        "h-mixed": 0.25,
    }
    with pytest.raises(AcquisitionError, match="cannot be summed as exclusive"):
        validate_probability_contract(contract)


def test_probability_and_evidence_confidence_are_separate() -> None:
    contract = load_contract()
    contract["hypotheses"][0]["evidence_confidence"]["level"] = 0.7
    with pytest.raises(AcquisitionError, match="must be a non-empty string"):
        validate_probability_contract(contract)


def test_dependency_policy_requires_correlation_controls() -> None:
    contract = load_contract()
    contract["dependency_policy"]["correlation_discount_required"] = False
    with pytest.raises(AcquisitionError, match="correlation_discount_required must be true"):
        validate_probability_contract(contract)


def test_sensitivity_plan_requires_multiple_challenges() -> None:
    contract = load_contract()
    contract["sensitivity_plan"]["tests"] = contract["sensitivity_plan"]["tests"][:2]
    with pytest.raises(AcquisitionError, match="at least three tests"):
        validate_probability_contract(contract)


def test_calibration_boundaries_must_span_zero_to_one() -> None:
    contract = load_contract()
    contract["scoring_contract"]["calibration_bucket_boundaries"] = [0.1, 0.5, 0.9]
    with pytest.raises(AcquisitionError, match="span 0 to 1"):
        validate_probability_contract(contract)


def test_forecast_revision_chain_is_hash_linked() -> None:
    contract = load_contract()
    validated = validate_probability_contract(contract)
    ledger = validated["ledger"]
    assert ledger[1]["previous_revision_sha256"] == ledger[0]["revision_sha256"]
    assert ledger[0]["revision_sha256"] == canonical_revision_hash(ledger[0])
    assert ledger[1]["revision_sha256"] == canonical_revision_hash(ledger[1])


def test_changed_revision_content_invalidates_hash() -> None:
    contract = load_contract()
    contract["forecast_ledger"][0]["reason"] = "Changed after hashing"
    with pytest.raises(AcquisitionError, match="does not match canonical revision content"):
        validate_probability_contract(contract)


def test_broken_previous_revision_link_fails() -> None:
    contract = load_contract()
    contract["forecast_ledger"][1]["previous_revision_sha256"] = "0" * 64
    contract["forecast_ledger"][1]["revision_sha256"] = canonical_revision_hash(
        contract["forecast_ledger"][1]
    )
    with pytest.raises(AcquisitionError, match="does not match prior revision"):
        validate_probability_contract(contract)


def test_prior_requires_provenance_and_assumptions() -> None:
    contract = load_contract()
    contract["hypotheses"][0]["prior"]["provenance"] = []
    with pytest.raises(AcquisitionError, match="provenance must be a non-empty list"):
        validate_probability_contract(contract)

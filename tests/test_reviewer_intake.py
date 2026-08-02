from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from pae.reviewer_intake import ReviewerIntakeError, validate_candidate, validate_release


FIXTURE = Path("fixtures/reviewer-candidate-method-fixture.json")


def load_candidate() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def test_clean_fixture_is_eligible() -> None:
    result = validate_candidate(load_candidate())
    assert result["decision"] == "eligible"
    assert result["packet_release_authorised"] is True


def test_institution_does_not_replace_expertise() -> None:
    candidate = load_candidate()
    candidate["expertise"] = []
    with pytest.raises(ReviewerIntakeError, match="expertise"):
        validate_candidate(candidate)


@pytest.mark.parametrize(
    "field",
    [
        "prepared_any_pae_case",
        "approved_any_pae_case",
        "seen_outcome_material",
        "advised_party_to_case",
        "financial_conflict",
        "employment_conflict",
        "close_personal_conflict",
    ],
)
def test_hard_conflicts_make_candidate_unsuitable(field: str) -> None:
    candidate = load_candidate()
    candidate[field] = True
    result = validate_candidate(candidate)
    assert result["decision"] == "unsuitable"
    assert result["packet_release_authorised"] is False


def test_source_authorship_requires_case_specific_clarification() -> None:
    candidate = load_candidate()
    candidate["authored_case_source"] = True
    result = validate_candidate(candidate)
    assert result["decision"] == "needs_clarification"
    assert result["packet_release_authorised"] is False


def test_unanswered_question_blocks_release() -> None:
    candidate = load_candidate()
    candidate["clarification_required"] = ["Confirm prior involvement in the case"]
    result = validate_candidate(candidate)
    assert result["decision"] == "needs_clarification"


def test_refusal_to_authenticate_record_is_unsuitable() -> None:
    candidate = load_candidate()
    candidate["willing_to_sign_confidential_record"] = False
    result = validate_candidate(candidate)
    assert result["decision"] == "unsuitable"


def test_declared_decision_cannot_override_computed_result() -> None:
    candidate = load_candidate()
    candidate["seen_outcome_material"] = True
    candidate["decision"] = "eligible"
    with pytest.raises(ReviewerIntakeError, match="conflicts with computed decision"):
        validate_candidate(candidate)


def test_case_exclusion_blocks_only_that_case() -> None:
    candidate = load_candidate()
    candidate["case_exclusions"] = ["morocco-ceuta-2021"]
    blocked = validate_release(candidate, "morocco-ceuta-2021")
    allowed = validate_release(candidate, "belarus-eu-borders-2021")
    assert blocked["release_authorised"] is False
    assert allowed["release_authorised"] is True


def test_release_returns_complete_handoff_checklist() -> None:
    result = validate_release(load_candidate(), "belarus-eu-borders-2021")
    assert result["release_authorised"] is True
    assert len(result["required_release_checks"]) == 5
    assert any("packet hash" in item for item in result["required_release_checks"])


def test_unknown_role_is_rejected() -> None:
    candidate = load_candidate()
    candidate["proposed_roles"] = ["celebrity"]
    with pytest.raises(ReviewerIntakeError, match="unsupported proposed roles"):
        validate_candidate(candidate)


def test_missing_boolean_declaration_is_rejected() -> None:
    candidate = load_candidate()
    del candidate["seen_outcome_material"]
    with pytest.raises(ReviewerIntakeError, match="seen_outcome_material"):
        validate_candidate(candidate)


def test_candidate_input_is_not_mutated() -> None:
    candidate = load_candidate()
    original = copy.deepcopy(candidate)
    validate_candidate(candidate)
    assert candidate == original

from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from pae.acquisition import AcquisitionError
from pae.human_workflow import build_workflow_bundle, validate_assignment_register


MANIFEST = Path("calibration/corpus-v0.1.json")


def load_manifest() -> dict:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def blank_register() -> dict:
    return build_workflow_bundle(load_manifest())["assignment_register_template"]


def completed_register() -> dict:
    register = blank_register()
    for index, row in enumerate(register["analyst_assignments"]):
        row.update(
            {
                "prepared_by": f"analyst-{index}-a",
                "approved_by": f"analyst-{index}-b",
                "status": "inputs_frozen",
            }
        )
    for index, row in enumerate(register["reviewer_assignments"]):
        row.update(
            {
                "status": "reviews_returned",
                "reviewers": [
                    {
                        "reviewer_id": f"reviewer-{index}-a",
                        "affiliation": "Independent methods reviewer",
                        "expertise": "Structured analysis",
                        "independent": True,
                        "conflict_of_interest": False,
                        "outcome_blinded": True,
                    },
                    {
                        "reviewer_id": f"reviewer-{index}-b",
                        "affiliation": "Independent domain reviewer",
                        "expertise": "Migration and border policy",
                        "independent": True,
                        "conflict_of_interest": False,
                        "outcome_blinded": True,
                    },
                ],
            }
        )
    return register


def test_builds_eight_analyst_and_review_packets() -> None:
    bundle = build_workflow_bundle(load_manifest())
    assert len(bundle["analyst_packets"]) == 8
    assert len(bundle["external_review_packets"]) == 8
    assert bundle["human_input_complete"] is False
    assert bundle["live_use_authorised"] is False


def test_packets_do_not_expose_outcome_fields() -> None:
    bundle = build_workflow_bundle(load_manifest())
    rendered = json.dumps(bundle["analyst_packets"] + bundle["external_review_packets"])
    assert '"outcome_class"' not in rendered
    assert '"outcome_rationale"' not in rendered
    assert '"withheld_outcome_sources"' not in rendered


def test_probability_forms_have_no_suggested_values() -> None:
    bundle = build_workflow_bundle(load_manifest())
    for packet in bundle["analyst_packets"]:
        assert set(packet["probability_assignment_form"]["probabilities"]) == {
            "positive",
            "negative",
            "disputed",
            "insufficient",
        }
        assert all(
            value is None
            for value in packet["probability_assignment_form"]["probabilities"].values()
        )


def test_blank_register_is_valid_but_incomplete() -> None:
    result = validate_assignment_register(load_manifest(), blank_register())
    assert result["complete_case_count"] == 0
    assert result["human_input_complete"] is False


def test_complete_register_is_complete_but_not_live_authority() -> None:
    result = validate_assignment_register(load_manifest(), completed_register())
    assert result["complete_case_count"] == 8
    assert result["human_input_complete"] is True
    assert result["live_use_authorised"] is False


def test_require_complete_rejects_blank_register() -> None:
    with pytest.raises(AcquisitionError, match="not complete"):
        validate_assignment_register(
            load_manifest(), blank_register(), require_complete=True
        )


def test_preparer_and_approver_must_differ() -> None:
    register = completed_register()
    register["analyst_assignments"][0]["approved_by"] = register[
        "analyst_assignments"
    ][0]["prepared_by"]
    with pytest.raises(AcquisitionError, match="must differ"):
        validate_assignment_register(load_manifest(), register)


def test_reviewer_cannot_prepare_same_case() -> None:
    register = completed_register()
    register["reviewer_assignments"][0]["reviewers"][0]["reviewer_id"] = register[
        "analyst_assignments"
    ][0]["prepared_by"]
    with pytest.raises(AcquisitionError, match="cannot prepare or approve"):
        validate_assignment_register(load_manifest(), register)


def test_two_reviewers_required_when_assigned() -> None:
    register = completed_register()
    register["reviewer_assignments"][0]["reviewers"] = register[
        "reviewer_assignments"
    ][0]["reviewers"][:1]
    with pytest.raises(AcquisitionError, match="at least two"):
        validate_assignment_register(load_manifest(), register)


def test_duplicate_reviewer_rejected() -> None:
    register = completed_register()
    register["reviewer_assignments"][0]["reviewers"][1]["reviewer_id"] = register[
        "reviewer_assignments"
    ][0]["reviewers"][0]["reviewer_id"]
    with pytest.raises(AcquisitionError, match="duplicate reviewer_id"):
        validate_assignment_register(load_manifest(), register)


def test_reviewer_must_declare_independence() -> None:
    register = completed_register()
    register["reviewer_assignments"][0]["reviewers"][0]["independent"] = False
    with pytest.raises(AcquisitionError, match="independent must be true"):
        validate_assignment_register(load_manifest(), register)


def test_reviewer_must_be_outcome_blinded() -> None:
    register = completed_register()
    register["reviewer_assignments"][0]["reviewers"][0]["outcome_blinded"] = False
    with pytest.raises(AcquisitionError, match="outcome_blinded"):
        validate_assignment_register(load_manifest(), register)


def test_conflicted_reviewer_rejected() -> None:
    register = completed_register()
    register["reviewer_assignments"][0]["reviewers"][0][
        "conflict_of_interest"
    ] = True
    with pytest.raises(AcquisitionError, match="conflict_of_interest"):
        validate_assignment_register(load_manifest(), register)


def test_every_frozen_case_must_appear_once() -> None:
    register = completed_register()
    register["analyst_assignments"].pop()
    with pytest.raises(AcquisitionError, match="every frozen case"):
        validate_assignment_register(load_manifest(), register)


def test_unassigned_rows_cannot_name_people() -> None:
    register = blank_register()
    register["analyst_assignments"][0]["prepared_by"] = "invented-person"
    with pytest.raises(AcquisitionError, match="must not name analysts"):
        validate_assignment_register(load_manifest(), register)


def test_manifest_outcome_changes_do_not_enter_packets() -> None:
    manifest = load_manifest()
    changed = copy.deepcopy(manifest)
    for case in changed["cases"]:
        case["outcome_rationale"] = "Secret changed outcome rationale."
    bundle = build_workflow_bundle(changed)
    assert "Secret changed outcome rationale" not in json.dumps(bundle)

from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json

import pytest

from pae.sec_evidence_intake import (
    NON_AUTHORITIES,
    SecEvidenceIntakeError,
    acquisition_input_projection,
    validate_sec_evidence_intake,
)


def _seal(value: dict) -> dict:
    candidate = deepcopy(value)
    candidate.pop("integrity_sha256", None)
    payload = json.dumps(
        candidate, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    candidate["integrity_sha256"] = sha256(payload).hexdigest()
    return candidate


def _handoff() -> dict:
    return _seal(
        {
            "schema_version": "1",
            "handoff_id": "sec-evidence-intake:fixture:0123456789abcdef",
            "created_at": "2026-09-16T18:10:00Z",
            "producer": {
                "system": "story-evidence-collector",
                "contract": "evidence-intake-handoff-v1",
                "authority_effect": "none",
            },
            "evidence_pack": {
                "pack_id": "2026-09-16-sec-evidence-intake-handoff",
                "pack_schema_version": "1",
                "title": "fixture",
                "status": "draft",
                "research_question": "fixture",
                "scope": "fixture",
                "publishability": "not_ready",
                "human_review_required": True,
                "validation": {
                    "validator": "evidence-pack-v1",
                    "status": "valid",
                    "errors": [],
                },
                "integrity_sha256": "a" * 64,
            },
            "sources": [
                {
                    "source_id": "source-collector-0001",
                    "identity": {
                        "url": "https://example.invalid/source",
                        "record_sha256": "b" * 64,
                    },
                    "title": "fixture",
                    "publisher": "example.invalid",
                    "published_at": None,
                    "collected_at": "2026-09-16T18:00:00Z",
                    "collection": {
                        "method": "collector_page",
                        "final_url": "https://example.invalid/source",
                        "robots_txt_checked": True,
                        "robots_txt_status": "ok",
                        "robots_allowed": True,
                        "scrape_status": "ok",
                        "error": None,
                    },
                    "preserved_source": {
                        "source_location": "Collector source record 1.",
                        "local_copy_path": None,
                        "visible_excerpt": "fixture excerpt",
                        "visible_excerpt_sha256": sha256(b"fixture excerpt").hexdigest(),
                        "discovered_links": [],
                        "preservation_status": "excerpt_only",
                    },
                    "dependency": {
                        "source_family": "official",
                        "derived_from_source_ids": [],
                        "external_dependency_urls": [],
                        "dependency_status": "declared",
                    },
                    "provenance": {
                        "evidence_pack_id": "2026-09-16-sec-evidence-intake-handoff",
                        "record_path": "sources/source-records.jsonl",
                        "record_line": 1,
                        "collector_input_file": "collector-source-records.json",
                        "collector_record_number": 1,
                    },
                    "notes": "fixture",
                }
            ],
            "uncertainty": {
                "collection_failures": [],
                "negative_evidence": [],
                "search_dead_ends": [],
            },
            "human_review": {
                "required": True,
                "state": "not_reviewed",
                "records": [{"decision": "not_reviewed"}],
            },
            "evidence_state": {
                "source_authority_record_count": 0,
                "claim_record_count": 0,
                "evidence_item_count": 0,
            },
            "consumer_contracts": {
                "threadkeeper": {
                    "target_domain": "evidence",
                    "source_kind": "evidence",
                    "admission_state": "candidate",
                    "requires_project_memory_admission": True,
                    "authority_effect": "none",
                },
                "pae": {
                    "intake_role": "evidence_acquisition_input",
                    "analysis_readiness": "not_assessed",
                    "requires_pae_case_construction": True,
                    "requires_pae_sufficiency_and_calibration": True,
                    "authority_effect": "none",
                },
            },
            "non_authorities": list(NON_AUTHORITIES),
        }
    )


def test_valid_handoff_is_acquisition_input_only() -> None:
    handoff = _handoff()
    assert validate_sec_evidence_intake(handoff) == []
    result = acquisition_input_projection(handoff)
    assert result["analysis_readiness"] == "not_assessed"
    assert result["information_sufficiency"] == "not_assessed"
    assert result["requires_pae_case_construction"] is True
    assert "hypotheses" not in result
    assert "probability" not in result


@pytest.mark.parametrize(
    ("mutator", "expected"),
    [
        (lambda x: x["consumer_contracts"]["pae"].update(analysis_readiness="ready"), "not assessed"),
        (lambda x: x["producer"].update(authority_effect="analysis"), "may not grant"),
        (lambda x: x["sources"][0].pop("provenance"), "provenance"),
        (lambda x: x.pop("uncertainty"), "uncertainty"),
        (
            lambda x: x["sources"][0]["preserved_source"].update(
                visible_excerpt="tampered"
            ),
            "excerpt digest",
        ),
        (
            lambda x: x.__setitem__(
                "handoff_id", "sec-evidence-intake:wrong:0000000000000000"
            ),
            "bind",
        ),
        (lambda x: x.pop("human_review"), "human_review"),
        (lambda x: x.__setitem__("non_authorities", NON_AUTHORITIES[:-1]), "non-authorities"),
        (lambda x: x["evidence_pack"]["validation"].update(status="invalid"), "validated"),
        (lambda x: x.__setitem__("hypotheses", [{"id": "H1"}]), "analytic fields"),
        (lambda x: x.__setitem__("probabilities", {"H1": 0.9}), "analytic fields"),
    ],
)
def test_hostile_handoff_fails_closed(mutator, expected: str) -> None:
    handoff = _handoff()
    mutator(handoff)
    handoff = _seal(handoff)
    errors = validate_sec_evidence_intake(handoff)
    assert errors
    assert any(expected.lower() in error.lower() for error in errors), errors
    with pytest.raises(SecEvidenceIntakeError):
        acquisition_input_projection(handoff)


def test_tampering_is_rejected() -> None:
    handoff = _handoff()
    handoff["sources"][0]["title"] = "tampered"
    assert any("integrity" in error for error in validate_sec_evidence_intake(handoff))

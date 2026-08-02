"""Outcome-blinded analyst packets and external-review mobilisation controls."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from .acquisition import AcquisitionError
from .calibration import CLASSES, validate_manifest

WORKFLOW_VERSION = "0.1"
CLASS_DEFINITIONS = {
    "positive": "Later public evidence supports deliberate state coercion under the declared resolution standard.",
    "negative": "Later public evidence supports a primarily non-coercive or ordinary mechanism under the declared resolution standard.",
    "disputed": "Materially different competent accounts remain unresolved under the declared resolution standard.",
    "insufficient": "The public record cannot satisfy the declared evidentiary question under the declared resolution standard.",
}


def _string(record: dict[str, Any], key: str, context: str) -> str:
    value = record.get(key)
    if not isinstance(value, str) or not value.strip():
        raise AcquisitionError(f"{context}: {key} must be a non-empty string")
    return value.strip()


def _case_packet(case: dict[str, Any], packet_type: str) -> dict[str, Any]:
    source_rows = []
    for source in case["evidence_source_registry"]:
        source_rows.append(
            {
                "date": source["date"],
                "institution": source["institution"],
                "title": source["title"],
                "url": source["url"],
                "source_class": None,
                "claim_specific_authority": None,
                "independence_group": None,
                "derived_from": [],
                "supports_or_tests": [],
                "limitations": [],
            }
        )
    base = {
        "workflow_version": WORKFLOW_VERSION,
        "packet_type": packet_type,
        "case_id": case["id"],
        "title": case["title"],
        "question": case["question"],
        "evidence_cutoff": case["evidence_cutoff"],
        "resolution_standard": case["resolution_standard"],
        "outcome_blinded": True,
        "hypothesis_classes": [
            {"id": class_id, "definition": CLASS_DEFINITIONS[class_id]}
            for class_id in CLASSES
        ],
        "evidence_source_registry": source_rows,
        "required_checks": [
            "Confirm every source predates or equals the evidence cutoff.",
            "Identify shared evidence origins, republication and common briefings.",
            "Seek contrary evidence and ordinary explanations.",
            "Separate motive, opportunity, conduct, coordination and command.",
            "Record inaccessible sources and unsuccessful searches.",
            "Do not seek the frozen outcome label or post-cutoff outcome sources.",
        ],
        "prohibited_material": [
            "frozen outcome class",
            "outcome rationale",
            "withheld outcome sources",
            "other analysts' or reviewers' probability assignments",
        ],
    }
    if packet_type == "analyst":
        base.update(
            {
                "analyst_roles": {
                    "prepared_by": None,
                    "approved_by": None,
                    "prepared_at": None,
                    "approved_at": None,
                },
                "research_record": {
                    "additional_pre_cutoff_sources": [],
                    "contrary_evidence": [],
                    "negative_search_results": [],
                    "source_dependency_notes": [],
                    "critical_information_gaps": [],
                },
                "probability_assignment_form": {
                    "instructions": (
                        "Assign all four probabilities only after the evidence packet is complete. "
                        "Values must total 1. No suggested values are supplied."
                    ),
                    "probabilities": {class_id: None for class_id in CLASSES},
                    "prior_rationale": None,
                    "likelihood_rationales": [],
                    "sensitivity_notes": [],
                    "evidence_confidence": None,
                    "change_conditions": [],
                },
            }
        )
    else:
        base.update(
            {
                "reviewer_declaration": {
                    "reviewer_id": None,
                    "affiliation": None,
                    "expertise": None,
                    "independent": None,
                    "conflict_of_interest": None,
                    "outcome_blinded_during_review": None,
                    "not_involved_in_case_preparation": None,
                    "reviewer_signature": None,
                },
                "review_questions": [
                    "Is the question precise and scoreable?",
                    "Are the four outcome classes applied consistently to this question?",
                    "Is every material claim supported by inspectable pre-cutoff evidence?",
                    "Are source dependencies and shared origins handled correctly?",
                    "Are contrary evidence and ordinary explanations fairly represented?",
                    "Are any post-cutoff outcome clues visible or inferable?",
                    "Can the calculation be reproduced from the supplied record?",
                    "Should the packet be accepted, corrected or rejected?",
                ],
                "review_record": {
                    "decision": None,
                    "findings": [],
                    "reviewed_at": None,
                },
            }
        )
    return base


def build_workflow_bundle(manifest: Any) -> dict[str, Any]:
    validate_manifest(manifest)
    analyst_packets = [_case_packet(case, "analyst") for case in manifest["cases"]]
    review_packets = [_case_packet(case, "external_review") for case in manifest["cases"]]
    register = {
        "workflow_version": WORKFLOW_VERSION,
        "programme_id": manifest["programme_id"],
        "analyst_assignments": [
            {
                "case_id": case["id"],
                "prepared_by": None,
                "approved_by": None,
                "status": "unassigned",
            }
            for case in manifest["cases"]
        ],
        "reviewer_assignments": [
            {
                "case_id": case["id"],
                "reviewers": [],
                "status": "unassigned",
            }
            for case in manifest["cases"]
        ],
    }
    rendered = json.dumps(
        {"analyst_packets": analyst_packets, "external_review_packets": review_packets},
        sort_keys=True,
        ensure_ascii=False,
    )
    for prohibited in ("outcome_class", "outcome_rationale", "withheld_outcome_sources"):
        if prohibited in rendered:
            raise AcquisitionError(f"workflow bundle: prohibited field leaked: {prohibited}")
    return {
        "workflow_version": WORKFLOW_VERSION,
        "programme_id": manifest["programme_id"],
        "analyst_packets": analyst_packets,
        "external_review_packets": review_packets,
        "assignment_register_template": register,
        "human_input_complete": False,
        "live_use_authorised": False,
    }


def validate_assignment_register(
    manifest: Any,
    register: Any,
    *,
    require_complete: bool = False,
) -> dict[str, Any]:
    manifest_info = validate_manifest(manifest)
    case_ids = set(manifest_info["case_ids"])
    if not isinstance(register, dict):
        raise AcquisitionError("assignment register must be an object")
    if _string(register, "workflow_version", "assignment register") != WORKFLOW_VERSION:
        raise AcquisitionError("assignment register: unsupported workflow_version")
    if _string(register, "programme_id", "assignment register") != manifest["programme_id"]:
        raise AcquisitionError("assignment register: programme_id does not match manifest")

    analysts = register.get("analyst_assignments")
    reviewers = register.get("reviewer_assignments")
    if not isinstance(analysts, list) or not isinstance(reviewers, list):
        raise AcquisitionError("assignment register: analyst and reviewer assignments must be lists")

    analyst_by_case: dict[str, dict[str, Any]] = {}
    for position, row in enumerate(analysts, start=1):
        context = f"analyst_assignments[{position}]"
        if not isinstance(row, dict):
            raise AcquisitionError(f"{context}: must be an object")
        case_id = _string(row, "case_id", context)
        if case_id not in case_ids or case_id in analyst_by_case:
            raise AcquisitionError(f"{context}: unknown or duplicate case_id")
        status = _string(row, "status", context)
        if status not in {"unassigned", "assigned", "inputs_frozen"}:
            raise AcquisitionError(f"{context}: unsupported status")
        prepared = row.get("prepared_by")
        approved = row.get("approved_by")
        if status == "unassigned":
            if prepared is not None or approved is not None:
                raise AcquisitionError(f"{context}: unassigned row must not name analysts")
        else:
            prepared = _string(row, "prepared_by", context)
            approved = _string(row, "approved_by", context)
            if prepared == approved:
                raise AcquisitionError(f"{context}: preparer and approver must differ")
        analyst_by_case[case_id] = row

    reviewer_by_case: dict[str, dict[str, Any]] = {}
    for position, row in enumerate(reviewers, start=1):
        context = f"reviewer_assignments[{position}]"
        if not isinstance(row, dict):
            raise AcquisitionError(f"{context}: must be an object")
        case_id = _string(row, "case_id", context)
        if case_id not in case_ids or case_id in reviewer_by_case:
            raise AcquisitionError(f"{context}: unknown or duplicate case_id")
        status = _string(row, "status", context)
        if status not in {"unassigned", "assigned", "reviews_returned"}:
            raise AcquisitionError(f"{context}: unsupported status")
        assigned = row.get("reviewers")
        if not isinstance(assigned, list):
            raise AcquisitionError(f"{context}: reviewers must be a list")
        identities: set[str] = set()
        for reviewer_position, reviewer in enumerate(assigned, start=1):
            reviewer_context = f"{context} reviewers[{reviewer_position}]"
            if not isinstance(reviewer, dict):
                raise AcquisitionError(f"{reviewer_context}: must be an object")
            reviewer_id = _string(reviewer, "reviewer_id", reviewer_context)
            if reviewer_id in identities:
                raise AcquisitionError(f"{reviewer_context}: duplicate reviewer_id")
            identities.add(reviewer_id)
            for field in ("affiliation", "expertise"):
                _string(reviewer, field, reviewer_context)
            if reviewer.get("independent") is not True:
                raise AcquisitionError(f"{reviewer_context}: independent must be true")
            if reviewer.get("conflict_of_interest") is not False:
                raise AcquisitionError(f"{reviewer_context}: conflict_of_interest must be false")
            if reviewer.get("outcome_blinded") is not True:
                raise AcquisitionError(f"{reviewer_context}: outcome_blinded must be true")
            analyst = analyst_by_case.get(case_id)
            if analyst and reviewer_id in {analyst.get("prepared_by"), analyst.get("approved_by")}:
                raise AcquisitionError(
                    f"{reviewer_context}: reviewer cannot prepare or approve the same case"
                )
        if status == "unassigned" and assigned:
            raise AcquisitionError(f"{context}: unassigned row must not name reviewers")
        if status in {"assigned", "reviews_returned"} and len(assigned) < 2:
            raise AcquisitionError(f"{context}: assigned case needs at least two reviewers")
        reviewer_by_case[case_id] = row

    if set(analyst_by_case) != case_ids or set(reviewer_by_case) != case_ids:
        raise AcquisitionError("assignment register: every frozen case must appear exactly once")

    complete_cases = []
    for case_id in sorted(case_ids):
        analyst = analyst_by_case[case_id]
        reviewer = reviewer_by_case[case_id]
        if analyst["status"] == "inputs_frozen" and reviewer["status"] == "reviews_returned":
            complete_cases.append(case_id)
    complete = len(complete_cases) == len(case_ids)
    if require_complete and not complete:
        raise AcquisitionError("assignment register: human workflow is not complete")
    return {
        "workflow_version": WORKFLOW_VERSION,
        "programme_id": manifest["programme_id"],
        "case_count": len(case_ids),
        "complete_case_count": len(complete_cases),
        "complete_case_ids": complete_cases,
        "human_input_complete": complete,
        "live_use_authorised": False,
        "warning": (
            "Register validation checks declared role separation. It does not prove identity, "
            "independence, expertise or the truth of conflict declarations."
        ),
    }


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def parser() -> argparse.ArgumentParser:
    command = argparse.ArgumentParser(description="Prepare or validate PAE human workflow packets.")
    subcommands = command.add_subparsers(dest="command", required=True)
    prepare = subcommands.add_parser("prepare")
    prepare.add_argument("manifest", type=Path)
    prepare.add_argument("--output", type=Path)
    validate = subcommands.add_parser("validate-register")
    validate.add_argument("manifest", type=Path)
    validate.add_argument("register", type=Path)
    validate.add_argument("--require-complete", action="store_true")
    validate.add_argument("--output", type=Path)
    return command


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        if args.command == "prepare":
            result = build_workflow_bundle(_load(args.manifest))
        else:
            result = validate_assignment_register(
                _load(args.manifest),
                _load(args.register),
                require_complete=args.require_complete,
            )
        rendered = json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(rendered, encoding="utf-8")
        else:
            print(rendered, end="")
    except (OSError, json.JSONDecodeError, AcquisitionError) as exc:
        print(f"PAE human workflow failed: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

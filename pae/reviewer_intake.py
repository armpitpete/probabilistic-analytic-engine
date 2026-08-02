"""Reviewer-candidate intake and packet-release safeguards.

This module records and validates genuine human candidates. It does not infer
independence from institutional affiliation and never releases case material.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


class ReviewerIntakeError(ValueError):
    """Raised when a reviewer intake record violates the declared contract."""


ALLOWED_ROLES = {"methods", "domain", "evidence", "integrity"}
ALLOWED_DECISIONS = {"eligible", "needs_clarification", "unsuitable", "withdrawn"}


def _non_empty(record: dict[str, Any], key: str, context: str) -> str:
    value = record.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ReviewerIntakeError(f"{context}: {key} must be a non-empty string")
    return value.strip()


def validate_candidate(record: Any) -> dict[str, Any]:
    if not isinstance(record, dict):
        raise ReviewerIntakeError("candidate record must be an object")

    candidate_id = _non_empty(record, "candidate_id", "candidate")
    _non_empty(record, "name_or_stable_identifier", candidate_id)
    _non_empty(record, "institution", candidate_id)
    _non_empty(record, "contact_route", candidate_id)

    roles = record.get("proposed_roles")
    if not isinstance(roles, list) or not roles:
        raise ReviewerIntakeError(f"{candidate_id}: proposed_roles must be a non-empty list")
    unknown_roles = sorted(set(roles) - ALLOWED_ROLES)
    if unknown_roles:
        raise ReviewerIntakeError(
            f"{candidate_id}: unsupported proposed roles {', '.join(unknown_roles)}"
        )

    expertise = record.get("expertise")
    if not isinstance(expertise, list) or not expertise or not all(
        isinstance(item, str) and item.strip() for item in expertise
    ):
        raise ReviewerIntakeError(f"{candidate_id}: expertise must contain concrete entries")

    for key in (
        "prepared_any_pae_case",
        "approved_any_pae_case",
        "seen_outcome_material",
        "authored_case_source",
        "advised_party_to_case",
        "financial_conflict",
        "employment_conflict",
        "close_personal_conflict",
        "willing_to_sign_confidential_record",
    ):
        if not isinstance(record.get(key), bool):
            raise ReviewerIntakeError(f"{candidate_id}: {key} must be true or false")

    conflicts = record.get("other_conflicts_or_commitments")
    if not isinstance(conflicts, list) or not all(isinstance(item, str) for item in conflicts):
        raise ReviewerIntakeError(
            f"{candidate_id}: other_conflicts_or_commitments must be a list of strings"
        )

    clarification = record.get("clarification_required", [])
    if not isinstance(clarification, list) or not all(isinstance(item, str) for item in clarification):
        raise ReviewerIntakeError(
            f"{candidate_id}: clarification_required must be a list of strings"
        )

    declared_decision = record.get("decision")
    if declared_decision is not None and declared_decision not in ALLOWED_DECISIONS:
        raise ReviewerIntakeError(f"{candidate_id}: unsupported decision {declared_decision!r}")

    hard_conflict = any(
        record[key]
        for key in (
            "prepared_any_pae_case",
            "approved_any_pae_case",
            "seen_outcome_material",
            "advised_party_to_case",
            "financial_conflict",
            "employment_conflict",
            "close_personal_conflict",
        )
    )
    source_conflict = bool(record["authored_case_source"])
    willing = bool(record["willing_to_sign_confidential_record"])

    if hard_conflict:
        computed = "unsuitable"
        reasons = ["one or more independence, conflict or outcome-exposure gates failed"]
    elif source_conflict:
        computed = "needs_clarification"
        reasons = ["case allocation must exclude any case whose source the candidate authored"]
    elif clarification:
        computed = "needs_clarification"
        reasons = ["one or more material questions remain unanswered"]
    elif not willing:
        computed = "unsuitable"
        reasons = ["candidate is unwilling to authenticate the confidential review record"]
    else:
        computed = "eligible"
        reasons = ["declared independence, blinding and authentication gates passed"]

    if declared_decision is not None and declared_decision != computed:
        raise ReviewerIntakeError(
            f"{candidate_id}: declared decision {declared_decision!r} conflicts with computed decision {computed!r}"
        )

    packet_release_authorised = computed == "eligible"
    return {
        "candidate_id": candidate_id,
        "decision": computed,
        "reasons": reasons,
        "proposed_roles": sorted(set(roles)),
        "packet_release_authorised": packet_release_authorised,
        "warning": (
            "Eligibility is based on the supplied declarations. Institutional affiliation does not prove "
            "independence, and release still requires case-specific allocation checks."
        ),
    }


def validate_release(record: Any, case_id: str) -> dict[str, Any]:
    result = validate_candidate(record)
    candidate_id = result["candidate_id"]
    case_exclusions = record.get("case_exclusions", [])
    if not isinstance(case_exclusions, list) or not all(isinstance(item, str) for item in case_exclusions):
        raise ReviewerIntakeError(f"{candidate_id}: case_exclusions must be a list of case IDs")

    release = result["packet_release_authorised"] and case_id not in case_exclusions
    reasons = list(result["reasons"])
    if case_id in case_exclusions:
        release = False
        reasons.append("candidate is excluded from this case")

    return {
        "candidate_id": candidate_id,
        "case_id": case_id,
        "release_authorised": release,
        "decision": result["decision"],
        "reasons": reasons,
        "required_release_checks": [
            "confirm packet contains no outcome label or withheld outcome source",
            "confirm candidate did not prepare or approve this case",
            "confirm case-specific source authorship and advisory conflicts",
            "record delivery time, packet hash and return deadline",
            "obtain authenticated declaration before sending full packet",
        ],
    }


def parser() -> argparse.ArgumentParser:
    command = argparse.ArgumentParser(description="Validate reviewer candidate intake records.")
    subcommands = command.add_subparsers(dest="command", required=True)

    candidate = subcommands.add_parser("candidate", help="Validate a candidate record")
    candidate.add_argument("record", type=Path)
    candidate.add_argument("--output", type=Path)

    release = subcommands.add_parser("release", help="Validate packet release for one case")
    release.add_argument("record", type=Path)
    release.add_argument("case_id")
    release.add_argument("--output", type=Path)
    return command


def _write(result: dict[str, Any], output: Path | None) -> None:
    rendered = json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        record = json.loads(args.record.read_text(encoding="utf-8"))
        if args.command == "candidate":
            result = validate_candidate(record)
        else:
            result = validate_release(record, args.case_id)
    except (OSError, json.JSONDecodeError, ReviewerIntakeError) as exc:
        print(f"Reviewer intake validation failed: {exc}", file=sys.stderr)
        return 2
    _write(result, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Controlled retrospective historical pilot runner.

The runner freezes an evidence packet, reproduces a reviewed calculation, reveals
only post-cutoff outcome records and scores the pre-cutoff probability draft.
It does not authorise live unresolved use or public conclusions.
"""

from __future__ import annotations

import argparse
from datetime import date, datetime
from hashlib import sha256
import json
import math
from pathlib import Path
import re
import sys
from typing import Any

from .acquisition import AcquisitionError
from .calculation import calculate_draft, review_calculation

PILOT_VERSION = "0.1"
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def _string(record: dict[str, Any], key: str, context: str) -> str:
    value = record.get(key)
    if not isinstance(value, str) or not value.strip():
        raise AcquisitionError(f"{context}: {key} must be a non-empty string")
    return value.strip()


def _parse_datetime(value: str, context: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise AcquisitionError(f"{context}: must be an ISO-8601 datetime") from exc
    if parsed.tzinfo is None:
        raise AcquisitionError(f"{context}: timezone is required")
    return parsed


def _parse_date(value: str, context: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise AcquisitionError(f"{context}: must be an ISO date") from exc


def canonical_packet_hash(packet: dict[str, Any]) -> str:
    payload = {key: value for key, value in packet.items() if key != "packet_sha256"}
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return sha256(encoded).hexdigest()


def validate_evidence_cut(packet: Any) -> dict[str, Any]:
    if not isinstance(packet, dict):
        raise AcquisitionError("evidence cut must be an object")
    _string(packet, "pilot_id", "evidence cut")
    _string(packet, "case_id", "evidence cut")
    cutoff = _parse_datetime(
        _string(packet, "evidence_cutoff", "evidence cut"),
        "evidence cut evidence_cutoff",
    )
    packet_hash = _string(packet, "packet_sha256", "evidence cut")
    if (
        not SHA256_RE.fullmatch(packet_hash)
        or packet_hash != canonical_packet_hash(packet)
    ):
        raise AcquisitionError("evidence cut: packet_sha256 does not match the packet")
    hypotheses = packet.get("hypothesis_ids")
    if not isinstance(hypotheses, list) or len(hypotheses) < 2 or any(
        not isinstance(item, str) or not item.strip() for item in hypotheses
    ):
        raise AcquisitionError(
            "evidence cut: hypothesis_ids must contain at least two strings"
        )
    if len(set(hypotheses)) != len(hypotheses):
        raise AcquisitionError("evidence cut: hypothesis_ids must be unique")

    sources = packet.get("sources")
    if not isinstance(sources, list) or not sources:
        raise AcquisitionError("evidence cut: sources must be a non-empty list")
    source_ids: set[str] = set()
    for position, source in enumerate(sources, start=1):
        context = f"evidence cut sources[{position}]"
        if not isinstance(source, dict):
            raise AcquisitionError(f"{context}: must be an object")
        source_id = _string(source, "id", context)
        if source_id in source_ids:
            raise AcquisitionError(f"{context}: duplicate id {source_id!r}")
        source_ids.add(source_id)
        source_date = _parse_date(_string(source, "date", context), f"{context} date")
        if source_date > cutoff.date():
            raise AcquisitionError(
                f"{context}: source date is after the evidence cutoff"
            )
        for field in (
            "institution",
            "title",
            "url",
            "source_class",
            "independence_group",
            "included_claim",
            "limitations",
        ):
            _string(source, field, context)
    return {
        "cutoff": cutoff,
        "source_ids": source_ids,
        "hypothesis_ids": set(hypotheses),
        "packet_hash": packet_hash,
    }


def _validate_plan_links(
    plan: Any,
    evidence: dict[str, Any],
    source_ids: set[str],
    hypothesis_ids: set[str],
) -> None:
    if not isinstance(plan, dict):
        raise AcquisitionError("calculation plan must be an object")
    if plan.get("case_snapshot_sha256") != evidence["packet_sha256"]:
        raise AcquisitionError(
            "calculation plan: case_snapshot_sha256 must match the evidence packet"
        )
    plan_hypotheses = {
        item.get("id") for item in plan.get("hypotheses", []) if isinstance(item, dict)
    }
    if plan_hypotheses != hypothesis_ids:
        raise AcquisitionError(
            "calculation plan: hypotheses must exactly match the evidence cut"
        )
    for position, update in enumerate(plan.get("evidence_updates", []), start=1):
        if not isinstance(update, dict):
            continue
        provenance = update.get("provenance")
        if not isinstance(provenance, list) or not provenance:
            raise AcquisitionError(
                f"calculation plan evidence_updates[{position}]: provenance is required"
            )
        unknown = {
            item for item in provenance if not isinstance(item, str) or item not in source_ids
        }
        if unknown:
            raise AcquisitionError(
                f"calculation plan evidence_updates[{position}]: provenance must reference evidence-cut source IDs"
            )


def _validate_outcome(
    outcome: Any,
    cutoff: datetime,
    hypothesis_ids: set[str],
) -> dict[str, Any]:
    if not isinstance(outcome, dict):
        raise AcquisitionError("outcome must be an object")
    if _string(outcome, "outcome_version", "outcome") != PILOT_VERSION:
        raise AcquisitionError(f"outcome: outcome_version must be {PILOT_VERSION!r}")
    resolved = _string(outcome, "resolved_hypothesis_id", "outcome")
    if resolved not in hypothesis_ids:
        raise AcquisitionError("outcome: resolved_hypothesis_id is not in the pilot")
    _string(outcome, "resolution_standard", "outcome")
    quality = _string(outcome, "resolution_quality", "outcome")
    if "judicial" not in quality:
        raise AcquisitionError(
            "outcome: resolution_quality must explicitly state the judicial status"
        )
    sources = outcome.get("outcome_sources")
    if not isinstance(sources, list) or not sources:
        raise AcquisitionError("outcome: outcome_sources must be a non-empty list")
    for position, source in enumerate(sources, start=1):
        context = f"outcome sources[{position}]"
        if not isinstance(source, dict):
            raise AcquisitionError(f"{context}: must be an object")
        source_date = _parse_date(_string(source, "date", context), f"{context} date")
        if source_date <= cutoff.date():
            raise AcquisitionError(
                f"{context}: outcome source must be after the evidence cutoff"
            )
        for field in ("id", "institution", "title", "url", "supports"):
            _string(source, field, context)
    limitations = outcome.get("limitations")
    if not isinstance(limitations, list) or not limitations:
        raise AcquisitionError("outcome: limitations must be a non-empty list")
    return {"resolved": resolved, "quality": quality}


def _score(posterior: dict[str, dict[str, Any]], resolved: str) -> dict[str, Any]:
    probabilities = {
        hypothesis_id: float(values["point_estimate"])
        for hypothesis_id, values in posterior.items()
    }
    total = sum(probabilities.values())
    if not math.isclose(total, 1.0, rel_tol=0, abs_tol=1e-9):
        raise AcquisitionError("pilot draft: posterior point estimates must total 1")
    resolved_probability = probabilities[resolved]
    if resolved_probability <= 0:
        raise AcquisitionError("pilot draft: resolved probability must be positive")
    brier = sum(
        (probability - (1.0 if hypothesis_id == resolved else 0.0)) ** 2
        for hypothesis_id, probability in probabilities.items()
    )
    logarithmic = -math.log(resolved_probability)
    leading = max(probabilities, key=probabilities.get)
    return {
        "resolved_probability": resolved_probability,
        "multiclass_brier_score": brier,
        "logarithmic_score": logarithmic,
        "leading_hypothesis_id": leading,
        "leading_hypothesis_matches_resolution": leading == resolved,
    }


def run_historical_pilot(
    evidence_cut: Any,
    calculation_plan: Any,
    review: Any,
    outcome: Any,
) -> dict[str, Any]:
    evidence = validate_evidence_cut(evidence_cut)
    _validate_plan_links(
        calculation_plan,
        evidence_cut,
        evidence["source_ids"],
        evidence["hypothesis_ids"],
    )
    draft = calculate_draft(calculation_plan)
    review_record = review_calculation(draft, review)
    if review_record["accepted_for_historical_pilot"] is not True:
        raise AcquisitionError(
            "review: calculation must be accepted for the historical pilot"
        )
    resolved = _validate_outcome(
        outcome, evidence["cutoff"], evidence["hypothesis_ids"]
    )
    scoring = _score(draft["posterior"], resolved["resolved"])

    leave_one_out = draft["sensitivity"]["leave_one_independence_group_out"]
    robustness = [
        {
            "omitted_independence_group": row["omitted_independence_group"],
            "leading_hypothesis_id": max(
                row["posterior"], key=row["posterior"].get
            ),
            "resolved_hypothesis_remains_leading": (
                max(row["posterior"], key=row["posterior"].get)
                == resolved["resolved"]
            ),
        }
        for row in leave_one_out
    ]

    return {
        "pilot_version": PILOT_VERSION,
        "pilot_id": evidence_cut["pilot_id"],
        "case_id": evidence_cut["case_id"],
        "evidence_cutoff": evidence_cut["evidence_cutoff"],
        "evidence_packet_sha256": evidence["packet_hash"],
        "calculation_draft_sha256": draft["draft_sha256"],
        "review_record_sha256": review_record["review_record_sha256"],
        "resolved_hypothesis_id": resolved["resolved"],
        "resolution_quality": resolved["quality"],
        "posterior": draft["posterior"],
        "scoring": scoring,
        "leave_one_stream_out_robustness": robustness,
        "resolved_hypothesis_leads_all_leave_one_out_tests": all(
            row["resolved_hypothesis_remains_leading"] for row in robustness
        ),
        "automatic_attribution_performed": False,
        "public_conclusion_authorised": False,
        "external_human_validation_completed": False,
        "warning": (
            "This retrospective pilot scores anticipation of a predeclared "
            "institutional resolution standard. It is not a judicial finding, "
            "independent external human validation or authority for live use."
        ),
    }


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def parser() -> argparse.ArgumentParser:
    command = argparse.ArgumentParser(
        description="Run a cutoff-controlled PAE historical pilot."
    )
    command.add_argument("evidence_cut", type=Path)
    command.add_argument("calculation_plan", type=Path)
    command.add_argument("review", type=Path)
    command.add_argument("outcome", type=Path)
    command.add_argument("--output", type=Path)
    return command


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        result = run_historical_pilot(
            _load(args.evidence_cut),
            _load(args.calculation_plan),
            _load(args.review),
            _load(args.outcome),
        )
        rendered = json.dumps(
            result, indent=2, sort_keys=True, ensure_ascii=False
        ) + "\n"
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(rendered, encoding="utf-8")
        else:
            print(rendered, end="")
    except (OSError, json.JSONDecodeError, AcquisitionError) as exc:
        print(f"PAE historical pilot failed: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

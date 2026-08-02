"""Human-reviewed probability calculation engine.

The engine performs deterministic arithmetic on human-declared priors and
likelihood ranges. It does not generate evidence weights, infer attribution,
authorise publication, or accept live unresolved cases.
"""

from __future__ import annotations

import argparse
from datetime import datetime
from hashlib import sha256
import json
import math
from pathlib import Path
import re
import sys
from typing import Any

from .acquisition import AcquisitionError

CALCULATION_VERSION = "0.1"
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
CONFIDENCE_LEVELS = {"very_low", "low", "moderate", "high"}
REVIEW_DECISIONS = {"accept_for_historical_pilot", "revise"}


def _string(record: dict[str, Any], key: str, context: str) -> str:
    value = record.get(key)
    if not isinstance(value, str) or not value.strip():
        raise AcquisitionError(f"{context}: {key} must be a non-empty string")
    return value.strip()


def _string_list(record: dict[str, Any], key: str, context: str) -> list[str]:
    value = record.get(key)
    if not isinstance(value, list) or not value or any(
        not isinstance(item, str) or not item.strip() for item in value
    ):
        raise AcquisitionError(f"{context}: {key} must be a non-empty list of strings")
    return [item.strip() for item in value]


def _number(
    value: Any,
    context: str,
    *,
    minimum: float,
    maximum: float | None = None,
) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise AcquisitionError(f"{context}: must be a number")
    result = float(value)
    if not math.isfinite(result) or result < minimum or (
        maximum is not None and result > maximum
    ):
        limit = (
            f" from {minimum} to {maximum}"
            if maximum is not None
            else f" at least {minimum}"
        )
        raise AcquisitionError(f"{context}: must be finite and{limit}")
    return result


def _iso_datetime(value: str, context: str) -> None:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise AcquisitionError(f"{context}: must be an ISO-8601 datetime") from exc
    if parsed.tzinfo is None:
        raise AcquisitionError(f"{context}: timezone is required")


def _canonical_hash(record: dict[str, Any], excluded: set[str]) -> str:
    payload = {key: value for key, value in record.items() if key not in excluded}
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return sha256(encoded).hexdigest()


def canonical_draft_hash(draft: dict[str, Any]) -> str:
    return _canonical_hash(draft, {"draft_sha256"})


def canonical_review_hash(review_record: dict[str, Any]) -> str:
    return _canonical_hash(review_record, {"review_record_sha256"})


def validate_calculation_plan(plan: Any) -> dict[str, Any]:
    if not isinstance(plan, dict):
        raise AcquisitionError("calculation plan must be an object")
    if _string(plan, "calculation_version", "plan") != CALCULATION_VERSION:
        raise AcquisitionError(
            f"plan: calculation_version must be {CALCULATION_VERSION!r}"
        )
    _string(plan, "calculation_id", "plan")
    snapshot = _string(plan, "case_snapshot_sha256", "plan")
    if not SHA256_RE.fullmatch(snapshot):
        raise AcquisitionError(
            "plan: case_snapshot_sha256 must be a lowercase SHA-256"
        )

    safety = plan.get("safety")
    if not isinstance(safety, dict):
        raise AcquisitionError("safety must be an object")
    if safety.get("automatic_attribution_enabled") is not False:
        raise AcquisitionError(
            "safety: automatic_attribution_enabled must be false"
        )
    if safety.get("public_conclusion_authorised") is not False:
        raise AcquisitionError(
            "safety: public_conclusion_authorised must be false"
        )
    if safety.get("live_unresolved_case") is not False:
        raise AcquisitionError("safety: live_unresolved_case must be false")
    if _string(safety, "calculation_mode", "safety") != "human_reviewed":
        raise AcquisitionError(
            "safety: calculation_mode must be 'human_reviewed'"
        )

    gate = plan.get("sufficiency_gate")
    if not isinstance(gate, dict):
        raise AcquisitionError("sufficiency_gate must be an object")
    if gate.get("passed") is not True:
        raise AcquisitionError(
            "sufficiency_gate: passed must be true before calculation"
        )
    actual_status = _string(gate, "actual_status", "sufficiency_gate")
    if actual_status not in {"mature", "resolved"}:
        raise AcquisitionError(
            "sufficiency_gate: actual_status must be mature or resolved"
        )
    _string(gate, "reason", "sufficiency_gate")

    authorisation = plan.get("analyst_authorisation")
    if not isinstance(authorisation, dict):
        raise AcquisitionError("analyst_authorisation must be an object")
    prepared_by = _string(
        authorisation, "prepared_by", "analyst_authorisation"
    )
    approved_by = _string(
        authorisation,
        "approved_for_calculation_by",
        "analyst_authorisation",
    )
    if prepared_by == approved_by:
        raise AcquisitionError(
            "analyst_authorisation: preparer and calculation approver must differ"
        )
    if (
        _string(authorisation, "decision", "analyst_authorisation")
        != "approved_for_calculation"
    ):
        raise AcquisitionError(
            "analyst_authorisation: decision must be 'approved_for_calculation'"
        )
    _string(authorisation, "rationale", "analyst_authorisation")
    _iso_datetime(
        _string(authorisation, "approved_at", "analyst_authorisation"),
        "analyst_authorisation approved_at",
    )

    hypotheses_raw = plan.get("hypotheses")
    if not isinstance(hypotheses_raw, list) or len(hypotheses_raw) < 2:
        raise AcquisitionError("hypotheses must contain at least two records")
    hypotheses: dict[str, dict[str, Any]] = {}
    for position, hypothesis in enumerate(hypotheses_raw, start=1):
        context = f"hypotheses[{position}]"
        if not isinstance(hypothesis, dict):
            raise AcquisitionError(f"{context}: must be an object")
        hypothesis_id = _string(hypothesis, "id", context)
        if hypothesis_id in hypotheses:
            raise AcquisitionError(f"{context}: duplicate id {hypothesis_id!r}")
        _string(hypothesis, "label", context)
        prior = hypothesis.get("prior")
        if not isinstance(prior, dict):
            raise AcquisitionError(f"{context}: prior must be an object")
        minimum = _number(
            prior.get("minimum"),
            f"{context} prior.minimum",
            minimum=0,
            maximum=1,
        )
        base = _number(
            prior.get("base"),
            f"{context} prior.base",
            minimum=0,
            maximum=1,
        )
        maximum = _number(
            prior.get("maximum"),
            f"{context} prior.maximum",
            minimum=0,
            maximum=1,
        )
        if not minimum <= base <= maximum:
            raise AcquisitionError(
                f"{context}: prior must satisfy minimum <= base <= maximum"
            )
        if base <= 0:
            raise AcquisitionError(
                f"{context}: prior.base must be greater than zero"
            )
        _string_list(prior, "provenance", f"{context} prior")
        _string_list(prior, "assumptions", f"{context} prior")
        confidence = hypothesis.get("evidence_confidence")
        if not isinstance(confidence, dict):
            raise AcquisitionError(
                f"{context}: evidence_confidence must be an object"
            )
        level = _string(
            confidence, "level", f"{context} evidence_confidence"
        )
        if level not in CONFIDENCE_LEVELS:
            raise AcquisitionError(
                f"{context}: unsupported evidence confidence {level!r}"
            )
        _string(
            confidence,
            "reason",
            f"{context} evidence_confidence",
        )
        _string_list(
            confidence,
            "change_conditions",
            f"{context} evidence_confidence",
        )
        hypotheses[hypothesis_id] = hypothesis

    group = plan.get("exclusive_group")
    if not isinstance(group, dict):
        raise AcquisitionError("exclusive_group must be an object")
    _string(group, "id", "exclusive_group")
    _string(group, "scope", "exclusive_group")
    group_ids = _string_list(group, "hypothesis_ids", "exclusive_group")
    if len(set(group_ids)) != len(group_ids):
        raise AcquisitionError(
            "exclusive_group: hypothesis_ids must be unique"
        )
    if set(group_ids) != set(hypotheses):
        raise AcquisitionError(
            "exclusive_group: hypothesis_ids must exactly match hypotheses"
        )
    base_total = sum(
        float(hypotheses[hypothesis_id]["prior"]["base"])
        for hypothesis_id in group_ids
    )
    if not math.isclose(base_total, 1.0, rel_tol=0, abs_tol=1e-9):
        raise AcquisitionError(
            f"exclusive_group: base priors must total 1, got {base_total:.12g}"
        )

    relationships = plan.get("nonexclusive_relationships", [])
    if not isinstance(relationships, list):
        raise AcquisitionError("nonexclusive_relationships must be a list")
    for position, relation in enumerate(relationships, start=1):
        context = f"nonexclusive_relationships[{position}]"
        if not isinstance(relation, dict):
            raise AcquisitionError(f"{context}: must be an object")
        left = _string(relation, "from", context)
        right = _string(relation, "to", context)
        if left in hypotheses and right in hypotheses:
            raise AcquisitionError(
                f"{context}: exclusive calculation group cannot contain a declared non-exclusive pair"
            )

    updates = plan.get("evidence_updates")
    if not isinstance(updates, list) or not updates:
        raise AcquisitionError(
            "evidence_updates must be a non-empty list"
        )
    update_ids: set[str] = set()
    group_weights: dict[str, float] = {}
    for position, update in enumerate(updates, start=1):
        context = f"evidence_updates[{position}]"
        if not isinstance(update, dict):
            raise AcquisitionError(f"{context}: must be an object")
        update_id = _string(update, "id", context)
        if update_id in update_ids:
            raise AcquisitionError(f"{context}: duplicate id {update_id!r}")
        update_ids.add(update_id)
        independence_group = _string(
            update, "independence_group", context
        )
        weight = _number(
            update.get("weight"),
            f"{context} weight",
            minimum=0,
            maximum=1,
        )
        if weight <= 0:
            raise AcquisitionError(
                f"{context}: weight must be greater than zero"
            )
        group_weights[independence_group] = (
            group_weights.get(independence_group, 0.0) + weight
        )
        if group_weights[independence_group] > 1 + 1e-12:
            raise AcquisitionError(
                f"{context}: total weight for independence_group {independence_group!r} exceeds 1"
            )
        _string(update, "assigned_by", context)
        _string(update, "rationale", context)
        _string_list(update, "provenance", context)
        multipliers = update.get("multipliers")
        if (
            not isinstance(multipliers, dict)
            or set(multipliers) != set(hypotheses)
        ):
            raise AcquisitionError(
                f"{context}: multipliers keys must exactly match hypotheses"
            )
        for hypothesis_id, values in multipliers.items():
            multiplier_context = (
                f"{context} multipliers.{hypothesis_id}"
            )
            if not isinstance(values, dict):
                raise AcquisitionError(
                    f"{multiplier_context}: must be an object"
                )
            minimum = _number(
                values.get("minimum"),
                f"{multiplier_context}.minimum",
                minimum=0,
            )
            base = _number(
                values.get("base"),
                f"{multiplier_context}.base",
                minimum=0,
            )
            maximum = _number(
                values.get("maximum"),
                f"{multiplier_context}.maximum",
                minimum=0,
            )
            if minimum <= 0 or not minimum <= base <= maximum:
                raise AcquisitionError(
                    f"{multiplier_context}: must satisfy 0 < minimum <= base <= maximum"
                )

    return {
        "hypotheses": hypotheses,
        "group_ids": group_ids,
        "updates": updates,
        "prepared_by": prepared_by,
        "approved_by": approved_by,
    }


def _normalise(scores: dict[str, float]) -> dict[str, float]:
    total = sum(scores.values())
    if not math.isfinite(total) or total <= 0:
        raise AcquisitionError(
            "calculation produced a non-positive or non-finite total"
        )
    return {key: value / total for key, value in scores.items()}


def _posterior(
    hypotheses: dict[str, dict[str, Any]],
    updates: list[dict[str, Any]],
    *,
    prior_field: str,
    multiplier_field: str,
    omit_independence_group: str | None = None,
) -> dict[str, float]:
    scores: dict[str, float] = {}
    for hypothesis_id, hypothesis in hypotheses.items():
        score = float(hypothesis["prior"][prior_field])
        for update in updates:
            if update["independence_group"] == omit_independence_group:
                continue
            multiplier = float(
                update["multipliers"][hypothesis_id][multiplier_field]
            )
            score *= multiplier ** float(update["weight"])
        scores[hypothesis_id] = score
    return _normalise(scores)


def _bounds_for_hypothesis(
    target_id: str,
    hypotheses: dict[str, dict[str, Any]],
    updates: list[dict[str, Any]],
) -> tuple[float, float]:
    low_scores: dict[str, float] = {}
    high_scores: dict[str, float] = {}
    for hypothesis_id, hypothesis in hypotheses.items():
        is_target = hypothesis_id == target_id
        low_prior = hypothesis["prior"][
            "minimum" if is_target else "maximum"
        ]
        high_prior = hypothesis["prior"][
            "maximum" if is_target else "minimum"
        ]
        low_score = float(low_prior)
        high_score = float(high_prior)
        for update in updates:
            weight = float(update["weight"])
            values = update["multipliers"][hypothesis_id]
            low_score *= float(
                values["minimum" if is_target else "maximum"]
            ) ** weight
            high_score *= float(
                values["maximum" if is_target else "minimum"]
            ) ** weight
        low_scores[hypothesis_id] = low_score
        high_scores[hypothesis_id] = high_score
    return (
        _normalise(low_scores)[target_id],
        _normalise(high_scores)[target_id],
    )


def calculate_draft(plan: Any) -> dict[str, Any]:
    validated = validate_calculation_plan(plan)
    hypotheses = validated["hypotheses"]
    updates = validated["updates"]
    group_ids = validated["group_ids"]

    base = _posterior(
        hypotheses,
        updates,
        prior_field="base",
        multiplier_field="base",
    )
    low_scenario = _posterior(
        hypotheses,
        updates,
        prior_field="minimum",
        multiplier_field="minimum",
    )
    high_scenario = _posterior(
        hypotheses,
        updates,
        prior_field="maximum",
        multiplier_field="maximum",
    )

    posterior: dict[str, dict[str, Any]] = {}
    for hypothesis_id in group_ids:
        lower, upper = _bounds_for_hypothesis(
            hypothesis_id, hypotheses, updates
        )
        posterior[hypothesis_id] = {
            "point_estimate": base[hypothesis_id],
            "minimum_sensitivity_bound": lower,
            "maximum_sensitivity_bound": upper,
            "evidence_confidence": hypotheses[hypothesis_id][
                "evidence_confidence"
            ],
        }

    independence_groups = sorted(
        {update["independence_group"] for update in updates}
    )
    leave_one_out = [
        {
            "omitted_independence_group": group,
            "posterior": _posterior(
                hypotheses,
                updates,
                prior_field="base",
                multiplier_field="base",
                omit_independence_group=group,
            ),
        }
        for group in independence_groups
    ]

    draft: dict[str, Any] = {
        "calculation_version": CALCULATION_VERSION,
        "calculation_id": plan["calculation_id"],
        "case_snapshot_sha256": plan["case_snapshot_sha256"],
        "exclusive_group_id": plan["exclusive_group"]["id"],
        "prepared_by": validated["prepared_by"],
        "approved_for_calculation_by": validated["approved_by"],
        "posterior": posterior,
        "sensitivity": {
            "all_minimum_inputs": low_scenario,
            "all_maximum_inputs": high_scenario,
            "leave_one_independence_group_out": leave_one_out,
        },
        "independence_group_weights": {
            group: sum(
                float(update["weight"])
                for update in updates
                if update["independence_group"] == group
            )
            for group in independence_groups
        },
        "review_status": "pending",
        "requires_post_calculation_review": True,
        "automatic_attribution_performed": False,
        "public_conclusion_authorised": False,
        "warning": (
            "These results are deterministic transformations of human-declared "
            "priors and likelihood ranges. Sensitivity bounds are not measured "
            "confidence intervals and the draft is not accepted until reviewed."
        ),
    }
    draft["draft_sha256"] = canonical_draft_hash(draft)
    return draft


def review_calculation(draft: Any, review: Any) -> dict[str, Any]:
    if not isinstance(draft, dict):
        raise AcquisitionError("draft must be an object")
    supplied_hash = _string(draft, "draft_sha256", "draft")
    if (
        not SHA256_RE.fullmatch(supplied_hash)
        or supplied_hash != canonical_draft_hash(draft)
    ):
        raise AcquisitionError(
            "draft: draft_sha256 does not match the exact draft"
        )
    if draft.get("review_status") != "pending":
        raise AcquisitionError("draft: review_status must be pending")
    if draft.get("automatic_attribution_performed") is not False:
        raise AcquisitionError(
            "draft: automatic attribution must remain false"
        )
    if draft.get("public_conclusion_authorised") is not False:
        raise AcquisitionError(
            "draft: public conclusion must remain unauthorised"
        )

    if not isinstance(review, dict):
        raise AcquisitionError("review must be an object")
    if _string(review, "draft_sha256", "review") != supplied_hash:
        raise AcquisitionError(
            "review: draft_sha256 must identify the exact draft"
        )
    reviewer = _string(review, "reviewer_id", "review")
    if reviewer == _string(draft, "prepared_by", "draft"):
        raise AcquisitionError(
            "review: reviewer must differ from calculation preparer"
        )
    decision = _string(review, "decision", "review")
    if decision not in REVIEW_DECISIONS:
        raise AcquisitionError(
            f"review: unsupported decision {decision!r}"
        )
    _string(review, "rationale", "review")
    reviewed_at = _string(review, "reviewed_at", "review")
    _iso_datetime(reviewed_at, "review reviewed_at")
    if review.get("public_conclusion_authorised") is not False:
        raise AcquisitionError(
            "review: public_conclusion_authorised must be false"
        )

    record: dict[str, Any] = {
        "draft_sha256": supplied_hash,
        "reviewer_id": reviewer,
        "decision": decision,
        "rationale": review["rationale"],
        "reviewed_at": reviewed_at,
        "accepted_for_historical_pilot": (
            decision == "accept_for_historical_pilot"
        ),
        "public_conclusion_authorised": False,
        "warning": (
            "Acceptance authorises only the controlled historical pilot. It does "
            "not authorise a live unresolved case or public conclusion."
        ),
    }
    record["review_record_sha256"] = canonical_review_hash(record)
    return record


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path | None, payload: dict[str, Any]) -> None:
    rendered = (
        json.dumps(
            payload,
            indent=2,
            sort_keys=True,
            ensure_ascii=False,
        )
        + "\n"
    )
    if path is None:
        print(rendered, end="")
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(rendered, encoding="utf-8")


def parser() -> argparse.ArgumentParser:
    command = argparse.ArgumentParser(
        description=(
            "Run or review a human-declared PAE probability calculation."
        )
    )
    subcommands = command.add_subparsers(dest="command", required=True)
    calculate = subcommands.add_parser("calculate")
    calculate.add_argument("plan", type=Path)
    calculate.add_argument("--output", type=Path)
    review = subcommands.add_parser("review")
    review.add_argument("draft", type=Path)
    review.add_argument("review", type=Path)
    review.add_argument("--output", type=Path)
    return command


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        if args.command == "calculate":
            payload = calculate_draft(_load(args.plan))
        else:
            payload = review_calculation(
                _load(args.draft), _load(args.review)
            )
        _write(args.output, payload)
    except (OSError, json.JSONDecodeError, AcquisitionError) as exc:
        print(f"PAE calculation failed: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Probability Engine v0.1 contract validator.

This module validates plans and forecast records. It performs no Bayesian update,
attribution calculation or public-conclusion generation.
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

CONTRACT_VERSION = "0.1"
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
SUFFICIENCY_STATES = {
    "insufficient",
    "preliminary",
    "developing",
    "substantial",
    "mature",
    "resolved",
}
CONFIDENCE_LEVELS = {"very_low", "low", "moderate", "high"}
NONEXCLUSIVE_RELATIONSHIPS = {"overlaps", "nested_under", "sequential", "compatible"}


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


def _probability(value: Any, context: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise AcquisitionError(f"{context}: must be a number from 0 to 1")
    result = float(value)
    if not math.isfinite(result) or not 0 <= result <= 1:
        raise AcquisitionError(f"{context}: must be a finite number from 0 to 1")
    return result


def _positive(value: Any, context: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise AcquisitionError(f"{context}: must be a positive number")
    result = float(value)
    if not math.isfinite(result) or result <= 0:
        raise AcquisitionError(f"{context}: must be a finite positive number")
    return result


def _iso_datetime(value: str, context: str) -> None:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise AcquisitionError(f"{context}: must be an ISO-8601 datetime") from exc
    if parsed.tzinfo is None:
        raise AcquisitionError(f"{context}: timezone is required")


def canonical_revision_hash(revision: dict[str, Any]) -> str:
    payload = {key: value for key, value in revision.items() if key != "revision_sha256"}
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return sha256(encoded).hexdigest()


def _validate_safety(contract: dict[str, Any]) -> dict[str, Any]:
    safety = contract.get("safety")
    if not isinstance(safety, dict):
        raise AcquisitionError("safety must be an object")
    if safety.get("automatic_attribution_enabled") is not False:
        raise AcquisitionError("safety: automatic_attribution_enabled must be false")
    if safety.get("public_conclusion_authorised") is not False:
        raise AcquisitionError("safety: public_conclusion_authorised must be false")
    if _string(safety, "calculation_mode", "safety") != "validator_only":
        raise AcquisitionError("safety: calculation_mode must be 'validator_only'")
    return safety


def _validate_gate(contract: dict[str, Any]) -> dict[str, Any]:
    gate = contract.get("sufficiency_gate")
    if not isinstance(gate, dict):
        raise AcquisitionError("sufficiency_gate must be an object")
    required = set(_string_list(gate, "required_statuses", "sufficiency_gate"))
    unknown = required - SUFFICIENCY_STATES
    if unknown:
        raise AcquisitionError(
            "sufficiency_gate: unsupported required statuses " + ", ".join(sorted(unknown))
        )
    actual = _string(gate, "actual_status", "sufficiency_gate")
    if actual not in SUFFICIENCY_STATES:
        raise AcquisitionError(
            f"sufficiency_gate: unsupported actual_status {actual!r}"
        )
    passed = gate.get("passed")
    if not isinstance(passed, bool):
        raise AcquisitionError("sufficiency_gate: passed must be boolean")
    expected_passed = actual in required
    if passed != expected_passed:
        raise AcquisitionError(
            "sufficiency_gate: passed must equal membership of actual_status in required_statuses"
        )
    updates_allowed = gate.get("probability_updates_allowed")
    if not isinstance(updates_allowed, bool):
        raise AcquisitionError(
            "sufficiency_gate: probability_updates_allowed must be boolean"
        )
    if not passed and updates_allowed:
        raise AcquisitionError(
            "sufficiency_gate: a failed gate forbids probability updates"
        )
    _string(gate, "reason", "sufficiency_gate")
    return gate


def _validate_hypotheses(contract: dict[str, Any]) -> dict[str, dict[str, Any]]:
    hypotheses = contract.get("hypotheses")
    if not isinstance(hypotheses, list) or len(hypotheses) < 2:
        raise AcquisitionError("hypotheses must contain at least two records")
    indexed: dict[str, dict[str, Any]] = {}
    for position, hypothesis in enumerate(hypotheses, start=1):
        context = f"hypotheses[{position}]"
        if not isinstance(hypothesis, dict):
            raise AcquisitionError(f"{context}: must be an object")
        hypothesis_id = _string(hypothesis, "id", context)
        if hypothesis_id in indexed:
            raise AcquisitionError(f"{context}: duplicate id {hypothesis_id!r}")
        _string(hypothesis, "label", context)
        prior = hypothesis.get("prior")
        if not isinstance(prior, dict):
            raise AcquisitionError(f"{context}: prior must be an object")
        minimum = _probability(prior.get("minimum"), f"{context} prior.minimum")
        maximum = _probability(prior.get("maximum"), f"{context} prior.maximum")
        point = _probability(prior.get("point_estimate"), f"{context} prior.point_estimate")
        if minimum > maximum:
            raise AcquisitionError(f"{context}: prior minimum exceeds maximum")
        if not minimum <= point <= maximum:
            raise AcquisitionError(
                f"{context}: prior point_estimate must fall within the range"
            )
        _string_list(prior, "provenance", f"{context} prior")
        _string_list(prior, "assumptions", f"{context} prior")
        _string(prior, "uncertainty_reason", f"{context} prior")

        confidence = hypothesis.get("evidence_confidence")
        if not isinstance(confidence, dict):
            raise AcquisitionError(f"{context}: evidence_confidence must be an object")
        level = _string(confidence, "level", f"{context} evidence_confidence")
        if level not in CONFIDENCE_LEVELS:
            raise AcquisitionError(
                f"{context}: unsupported evidence confidence level {level!r}"
            )
        _string(confidence, "reason", f"{context} evidence_confidence")
        _string_list(
            confidence,
            "change_conditions",
            f"{context} evidence_confidence",
        )
        indexed[hypothesis_id] = hypothesis
    return indexed


def _validate_relationships(
    contract: dict[str, Any], hypotheses: dict[str, dict[str, Any]]
) -> set[frozenset[str]]:
    relationships = contract.get("nonexclusive_relationships")
    if not isinstance(relationships, list):
        raise AcquisitionError("nonexclusive_relationships must be a list")
    nonexclusive_pairs: set[frozenset[str]] = set()
    for position, relation in enumerate(relationships, start=1):
        context = f"nonexclusive_relationships[{position}]"
        if not isinstance(relation, dict):
            raise AcquisitionError(f"{context}: must be an object")
        source = _string(relation, "from", context)
        target = _string(relation, "to", context)
        relation_type = _string(relation, "type", context)
        if source not in hypotheses or target not in hypotheses:
            raise AcquisitionError(f"{context}: unknown hypothesis")
        if source == target:
            raise AcquisitionError(f"{context}: hypotheses must differ")
        if relation_type not in NONEXCLUSIVE_RELATIONSHIPS:
            raise AcquisitionError(
                f"{context}: unsupported relationship type {relation_type!r}"
            )
        if relation_type in {"overlaps", "nested_under", "compatible"}:
            nonexclusive_pairs.add(frozenset((source, target)))
    return nonexclusive_pairs


def _validate_exclusive_groups(
    contract: dict[str, Any],
    hypotheses: dict[str, dict[str, Any]],
    nonexclusive_pairs: set[frozenset[str]],
) -> list[dict[str, Any]]:
    groups = contract.get("exclusive_groups")
    if not isinstance(groups, list) or not groups:
        raise AcquisitionError("exclusive_groups must be a non-empty list")
    group_ids: set[str] = set()
    for position, group in enumerate(groups, start=1):
        context = f"exclusive_groups[{position}]"
        if not isinstance(group, dict):
            raise AcquisitionError(f"{context}: must be an object")
        group_id = _string(group, "id", context)
        if group_id in group_ids:
            raise AcquisitionError(f"{context}: duplicate id {group_id!r}")
        group_ids.add(group_id)
        hypothesis_ids = _string_list(group, "hypothesis_ids", context)
        if len(set(hypothesis_ids)) != len(hypothesis_ids):
            raise AcquisitionError(f"{context}: duplicate hypothesis id")
        unknown = set(hypothesis_ids) - set(hypotheses)
        if unknown:
            raise AcquisitionError(
                f"{context}: unknown hypotheses {', '.join(sorted(unknown))}"
            )
        for index, left in enumerate(hypothesis_ids):
            for right in hypothesis_ids[index + 1 :]:
                if frozenset((left, right)) in nonexclusive_pairs:
                    raise AcquisitionError(
                        f"{context}: nested, overlapping or compatible hypotheses cannot be summed as exclusive"
                    )
        estimates = group.get("point_estimates")
        if not isinstance(estimates, dict) or set(estimates) != set(hypothesis_ids):
            raise AcquisitionError(
                f"{context}: point_estimates keys must exactly match hypothesis_ids"
            )
        total = sum(
            _probability(estimates[hypothesis_id], f"{context} point_estimates.{hypothesis_id}")
            for hypothesis_id in hypothesis_ids
        )
        if not math.isclose(total, 1.0, rel_tol=0, abs_tol=1e-9):
            raise AcquisitionError(
                f"{context}: exclusive point estimates must total 1, got {total:.12g}"
            )
        _string(group, "scope", context)
    return groups


def _validate_likelihood_scale(contract: dict[str, Any]) -> list[dict[str, Any]]:
    scale = contract.get("likelihood_scale")
    if not isinstance(scale, list) or not scale:
        raise AcquisitionError("likelihood_scale must be a non-empty list")
    ids: set[str] = set()
    for position, band in enumerate(scale, start=1):
        context = f"likelihood_scale[{position}]"
        if not isinstance(band, dict):
            raise AcquisitionError(f"{context}: must be an object")
        band_id = _string(band, "id", context)
        if band_id in ids:
            raise AcquisitionError(f"{context}: duplicate id {band_id!r}")
        ids.add(band_id)
        minimum = _positive(band.get("minimum_multiplier"), f"{context} minimum_multiplier")
        maximum = _positive(band.get("maximum_multiplier"), f"{context} maximum_multiplier")
        if minimum > maximum:
            raise AcquisitionError(f"{context}: minimum_multiplier exceeds maximum_multiplier")
        _string(band, "interpretation", context)
        _string(band, "assignment_rule", context)
    return scale


def _validate_dependency_policy(contract: dict[str, Any]) -> dict[str, Any]:
    policy = contract.get("dependency_policy")
    if not isinstance(policy, dict):
        raise AcquisitionError("dependency_policy must be an object")
    for field in (
        "independence_group_required",
        "correlation_discount_required",
        "double_counting_prohibited",
        "manual_override_requires_reason",
    ):
        if policy.get(field) is not True:
            raise AcquisitionError(f"dependency_policy: {field} must be true")
    maximum = policy.get("maximum_full_weight_per_independence_group")
    if maximum != 1:
        raise AcquisitionError(
            "dependency_policy: maximum_full_weight_per_independence_group must equal 1"
        )
    _string(policy, "correlation_method", "dependency_policy")
    return policy


def _validate_sensitivity(contract: dict[str, Any]) -> dict[str, Any]:
    plan = contract.get("sensitivity_plan")
    if not isinstance(plan, dict) or plan.get("required") is not True:
        raise AcquisitionError("sensitivity_plan.required must be true")
    tests = plan.get("tests")
    if not isinstance(tests, list) or len(tests) < 3:
        raise AcquisitionError("sensitivity_plan.tests must contain at least three tests")
    ids: set[str] = set()
    for position, test in enumerate(tests, start=1):
        context = f"sensitivity_plan.tests[{position}]"
        if not isinstance(test, dict):
            raise AcquisitionError(f"{context}: must be an object")
        test_id = _string(test, "id", context)
        if test_id in ids:
            raise AcquisitionError(f"{context}: duplicate id {test_id!r}")
        ids.add(test_id)
        for field in ("variable", "low_assumption", "high_assumption", "reported_output"):
            _string(test, field, context)
    return plan


def _validate_scoring(contract: dict[str, Any]) -> dict[str, Any]:
    scoring = contract.get("scoring_contract")
    if not isinstance(scoring, dict):
        raise AcquisitionError("scoring_contract must be an object")
    if scoring.get("brier_score") is not True:
        raise AcquisitionError("scoring_contract: brier_score must be true")
    if scoring.get("logarithmic_score") is not True:
        raise AcquisitionError("scoring_contract: logarithmic_score must be true")
    buckets = scoring.get("calibration_bucket_boundaries")
    if not isinstance(buckets, list) or len(buckets) < 3:
        raise AcquisitionError(
            "scoring_contract: calibration_bucket_boundaries must contain at least three values"
        )
    values = [
        _probability(value, f"scoring_contract calibration_bucket_boundaries[{index}]")
        for index, value in enumerate(buckets)
    ]
    if values != sorted(set(values)) or values[0] != 0 or values[-1] != 1:
        raise AcquisitionError(
            "scoring_contract: calibration boundaries must be unique, increasing and span 0 to 1"
        )
    for field in ("resolution_standard", "unresolved_outcome_policy", "reporting_cadence"):
        _string(scoring, field, "scoring_contract")
    return scoring


def _validate_ledger(contract: dict[str, Any]) -> list[dict[str, Any]]:
    ledger = contract.get("forecast_ledger")
    if not isinstance(ledger, list) or not ledger:
        raise AcquisitionError("forecast_ledger must be a non-empty list")
    previous_hash: str | None = None
    for position, revision in enumerate(ledger, start=1):
        context = f"forecast_ledger[{position}]"
        if not isinstance(revision, dict):
            raise AcquisitionError(f"{context}: must be an object")
        if revision.get("revision") != position:
            raise AcquisitionError(f"{context}: revision numbers must start at 1 and be consecutive")
        recorded_at = _string(revision, "recorded_at", context)
        _iso_datetime(recorded_at, f"{context} recorded_at")
        _string(revision, "reason", context)
        state_hash = _string(revision, "assessment_state_sha256", context)
        if not SHA256_RE.fullmatch(state_hash):
            raise AcquisitionError(f"{context}: assessment_state_sha256 must be a SHA-256 hex digest")
        changed = revision.get("probabilities_changed")
        if not isinstance(changed, bool):
            raise AcquisitionError(f"{context}: probabilities_changed must be boolean")
        previous_field = revision.get("previous_revision_sha256")
        if previous_field != previous_hash:
            raise AcquisitionError(f"{context}: previous_revision_sha256 does not match prior revision")
        supplied_hash = _string(revision, "revision_sha256", context)
        if not SHA256_RE.fullmatch(supplied_hash):
            raise AcquisitionError(f"{context}: revision_sha256 must be a SHA-256 hex digest")
        expected_hash = canonical_revision_hash(revision)
        if supplied_hash != expected_hash:
            raise AcquisitionError(f"{context}: revision_sha256 does not match canonical revision content")
        previous_hash = supplied_hash
    return ledger


def _validate_triggers(contract: dict[str, Any]) -> list[dict[str, Any]]:
    triggers = contract.get("update_triggers")
    if not isinstance(triggers, list) or not triggers:
        raise AcquisitionError("update_triggers must be a non-empty list")
    ids: set[str] = set()
    for position, trigger in enumerate(triggers, start=1):
        context = f"update_triggers[{position}]"
        if not isinstance(trigger, dict):
            raise AcquisitionError(f"{context}: must be an object")
        trigger_id = _string(trigger, "id", context)
        if trigger_id in ids:
            raise AcquisitionError(f"{context}: duplicate id {trigger_id!r}")
        ids.add(trigger_id)
        for field in ("description", "expected_effect", "required_action"):
            _string(trigger, field, context)
    return triggers


def validate_probability_contract(contract: Any) -> dict[str, Any]:
    if not isinstance(contract, dict):
        raise AcquisitionError("probability contract must be an object")
    if contract.get("contract_version") != CONTRACT_VERSION:
        raise AcquisitionError(
            f"probability contract: contract_version must be {CONTRACT_VERSION!r}"
        )
    assessment_id = _string(contract, "assessment_id", "probability contract")
    case_hash = _string(contract, "case_snapshot_sha256", "probability contract")
    if not SHA256_RE.fullmatch(case_hash):
        raise AcquisitionError(
            "probability contract: case_snapshot_sha256 must be a SHA-256 hex digest"
        )
    _string(contract, "domain_id", "probability contract")
    _validate_safety(contract)
    gate = _validate_gate(contract)
    hypotheses = _validate_hypotheses(contract)
    nonexclusive_pairs = _validate_relationships(contract, hypotheses)
    groups = _validate_exclusive_groups(contract, hypotheses, nonexclusive_pairs)
    scale = _validate_likelihood_scale(contract)
    _validate_dependency_policy(contract)
    sensitivity = _validate_sensitivity(contract)
    scoring = _validate_scoring(contract)
    ledger = _validate_ledger(contract)
    triggers = _validate_triggers(contract)
    return {
        "assessment_id": assessment_id,
        "hypotheses": hypotheses,
        "exclusive_groups": groups,
        "likelihood_scale": scale,
        "gate": gate,
        "sensitivity": sensitivity,
        "scoring": scoring,
        "ledger": ledger,
        "triggers": triggers,
    }


def assess_probability_contract(contract: Any) -> dict[str, Any]:
    validated = validate_probability_contract(contract)
    return {
        "contract_version": CONTRACT_VERSION,
        "assessment_id": validated["assessment_id"],
        "hypotheses": len(validated["hypotheses"]),
        "exclusive_groups": len(validated["exclusive_groups"]),
        "likelihood_bands": len(validated["likelihood_scale"]),
        "sufficiency_gate": {
            "actual_status": validated["gate"]["actual_status"],
            "passed": validated["gate"]["passed"],
            "probability_updates_allowed": validated["gate"]["probability_updates_allowed"],
        },
        "sensitivity_tests": len(validated["sensitivity"]["tests"]),
        "forecast_revisions": len(validated["ledger"]),
        "update_triggers": len(validated["triggers"]),
        "automatic_attribution_enabled": False,
        "public_conclusion_authorised": False,
        "calculation_performed": False,
        "warning": (
            "This validates an analytical contract only. It does not calculate or "
            "endorse any probability, attribution or public conclusion."
        ),
    }


def parser() -> argparse.ArgumentParser:
    command = argparse.ArgumentParser(
        description="Validate a PAE probability-engine contract without calculating probabilities."
    )
    command.add_argument("contract", type=Path)
    command.add_argument("--output", type=Path)
    return command


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        contract = json.loads(args.contract.read_text(encoding="utf-8"))
        result = assess_probability_contract(contract)
    except (OSError, json.JSONDecodeError, AcquisitionError) as exc:
        print(f"PAE probability contract failed: {exc}", file=sys.stderr)
        return 2
    rendered = json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

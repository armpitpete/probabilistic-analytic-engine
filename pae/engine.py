"""Integrated PAE assessment surface."""

from __future__ import annotations

from typing import Any

from . import acquisition
from .research import research_outputs, validate_research_protocol
from .structure import (
    case_snapshot,
    hypothesis_analysis,
    provenance_summary,
    validate_extended_case,
)


def validate_case(case: Any) -> dict[str, Any]:
    indexes = acquisition.validate_case(case)
    indexes["structure"] = validate_extended_case(case)
    indexes["research"] = validate_research_protocol(case)
    return indexes


def assess_case(case: Any) -> dict[str, Any]:
    validate_case(case)
    base = acquisition.assess_case(case)
    extended = validate_extended_case(case)
    research = validate_research_protocol(case)
    if research["extended"]:
        base["engine_version"] = "0.3.0"
    elif extended["extended"]:
        base["engine_version"] = "0.2.0"
    base["case_snapshot"] = case_snapshot(case)
    base["hypothesis_analysis"] = hypothesis_analysis(case, extended)
    base["provenance_summary"] = provenance_summary(case, extended)
    base.update(research_outputs(case, base))
    return base

"""Probabilistic Analytic Engine.

Version 0.3 adds research control, typed source dependencies, hypothesis coverage,
search auditing and configurable sufficiency while preserving earlier case paths.
It does not calculate attribution probabilities.
"""

from .acquisition import AcquisitionError
from .engine import assess_case, validate_case

__all__ = ["AcquisitionError", "assess_case", "validate_case"]
__version__ = "0.3.0"

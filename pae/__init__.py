"""Probabilistic Analytic Engine.

Version 0.4 adds reusable domain modules and sourced historical comparison while
preserving evidence, provenance and research-control case paths.
It does not calculate attribution probabilities.
"""

from .acquisition import AcquisitionError
from .engine import assess_case, validate_case

__all__ = ["AcquisitionError", "assess_case", "validate_case"]
__version__ = "0.4.0"

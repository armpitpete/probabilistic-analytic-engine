"""Probabilistic Analytic Engine.

Version 0.7 adds a cutoff-controlled resolved historical pilot while keeping
live unresolved cases, automatic attribution and publication disabled.
"""

from .acquisition import AcquisitionError
from .engine import assess_case, validate_case

__all__ = ["AcquisitionError", "assess_case", "validate_case"]
__version__ = "0.7.0"

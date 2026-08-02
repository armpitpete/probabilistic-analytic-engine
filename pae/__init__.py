"""Probabilistic Analytic Engine.

Version 0.6 adds deterministic human-reviewed probability calculation while
keeping automatic attribution, live unresolved cases and publication disabled.
"""

from .acquisition import AcquisitionError
from .engine import assess_case, validate_case

__all__ = ["AcquisitionError", "assess_case", "validate_case"]
__version__ = "0.6.0"

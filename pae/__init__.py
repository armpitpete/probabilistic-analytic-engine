"""Probabilistic Analytic Engine.

Version 0.8 adds a frozen balanced calibration corpus, aggregate scoring and
external-review controls while keeping live unresolved use disabled.
"""

from .acquisition import AcquisitionError
from .engine import assess_case, validate_case

__all__ = ["AcquisitionError", "assess_case", "validate_case"]
__version__ = "0.8.0"

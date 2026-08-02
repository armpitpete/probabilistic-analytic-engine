"""Probabilistic Analytic Engine.

Version 0.9 adds outcome-blinded analyst packets and external-review
mobilisation controls while keeping live unresolved use disabled.
"""

from .acquisition import AcquisitionError
from .engine import assess_case, validate_case

__all__ = ["AcquisitionError", "assess_case", "validate_case"]
__version__ = "0.9.0"

"""Probabilistic Analytic Engine.

Version 0.10 adds reviewer-candidate intake and packet-release safeguards while
keeping live unresolved use disabled.
"""

from .acquisition import AcquisitionError
from .engine import assess_case, validate_case

__all__ = ["AcquisitionError", "assess_case", "validate_case"]
__version__ = "0.10.0"

"""Probabilistic Analytic Engine.

Version 0.5 completes the evidence, research, domain and probability-contract
foundations. Probability calculations and automatic attribution remain disabled.
"""

from .acquisition import AcquisitionError
from .engine import assess_case, validate_case

__all__ = ["AcquisitionError", "assess_case", "validate_case"]
__version__ = "0.5.0"

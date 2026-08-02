"""Probabilistic Analytic Engine.

Version 0.1 implements evidence acquisition and information sufficiency only.
It does not calculate attribution probabilities.
"""

from .acquisition import AcquisitionError, assess_case, validate_case

__all__ = ["AcquisitionError", "assess_case", "validate_case"]
__version__ = "0.1.0"

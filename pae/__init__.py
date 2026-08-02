"""Probabilistic Analytic Engine.

Version 0.2 adds strict provenance, hypothesis structure and immutable case
snapshots while preserving the accepted v0.1 evidence-acquisition path.
It does not calculate attribution probabilities.
"""

from .acquisition import AcquisitionError
from .engine import assess_case, validate_case

__all__ = ["AcquisitionError", "assess_case", "validate_case"]
__version__ = "0.2.0"

"""
Factor Agent - Academic Multi-Factor Investing for NASDAQ 100

Evidence-based factor investing following academic research.
"""

from .factor_agent import FactorNASDAQAgent
from .strategy import FactorStrategy

__all__ = [
    'FactorNASDAQAgent',
    'FactorStrategy',
]

__version__ = '1.0.0'

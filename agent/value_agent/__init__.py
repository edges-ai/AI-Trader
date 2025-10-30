"""
Value Agent - Fundamental Value Investing for NASDAQ 100

Buy quality companies at reasonable prices. Focus on fundamentals over technicals.
"""

from .value_agent import ValueNASDAQAgent
from .strategy import ValueStrategy

__all__ = [
    'ValueNASDAQAgent',
    'ValueStrategy',
]

__version__ = '1.0.0'

"""
Alpha Agent - Statistical Arbitrage for NASDAQ 100

Hunt for alpha using statistical patterns and mean reversion.
"""

from .alpha_agent import AlphaNASDAQAgent
from .strategy import AlphaStrategy

__all__ = [
    'AlphaNASDAQAgent',
    'AlphaStrategy',
]

__version__ = '1.0.0'

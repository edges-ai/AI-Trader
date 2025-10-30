"""
Momentum Agent - Technical Trend Following for NASDAQ 100

Self-contained trading agent using SMA crossovers, RSI, and volume confirmation.
Conservative risk management with 20% cash buffer and 10% stop losses.
"""

from .momentum_agent import MomentumNASDAQAgent
from .strategy import MomentumStrategy

__all__ = [
    'MomentumNASDAQAgent',
    'MomentumStrategy',
]

__version__ = '1.0.0'

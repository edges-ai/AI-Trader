"""
Momentum Strategy - Technical Trend Following for NASDAQ 100

Philosophy: Follow the trend. Buy stocks with strong upward momentum,
exit on trend breaks. Conservative risk management.
"""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agent.claude_code_agent.shared.base_strategy import BaseStrategy


class MomentumStrategy(BaseStrategy):
    """Technical momentum using SMA crossovers and RSI."""

    def __init__(self):
        super().__init__(name="Momentum", signature="momentum-nasdaq")

    def get_analysis_framework(self) -> str:
        return """
### Core Concept
Follow the trend. Buy on bullish signals, sell on bearish signals.

### Analysis Steps (8 minutes)

**Phase 1: Trend Identification (3 min)**
```python
# Calculate SMA(5) and SMA(20)
# Bullish: SMA(5) > SMA(20) AND Price > SMA(5)
# Bearish: SMA(5) < SMA(20)
```

**Phase 2: RSI Confirmation (2 min)**
```python
# RSI = 14-period
# Buy zone: RSI 40-70 (avoid overbought)
# Avoid: RSI >75 (overbought)
```

**Phase 3: Volume Check (1 min)**
```python
# Volume > 0.8x average = valid signal
```

**Phase 4: Decision (2 min)**
- BUY: Trend bullish + RSI 40-70 + Volume OK
- SELL: Trend break OR RSI >75 OR Stop loss -10%

### Trading Rules
- Max position: 15% of portfolio
- Max portfolio: 10-15 stocks
- Stop loss: -10% from entry
- Min cash: 20% (conservative buffer)
"""

    def get_risk_rules(self) -> dict:
        return {
            'max_position': 0.15,
            'min_cash': 0.20,       # Conservative (high cash)
            'stop_loss': 0.10,      # 10% stop
            'max_positions': 15,
            'confidence_threshold': 0.70,
        }

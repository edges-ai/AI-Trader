"""
Alpha Strategy - Statistical Arbitrage for NASDAQ 100

Philosophy: Hunt for alpha using statistical patterns and mean reversion.
"""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agent.claude_code_agent.shared.base_strategy import BaseStrategy


class AlphaStrategy(BaseStrategy):
    """Statistical Arbitrage for NASDAQ 100"""

    def __init__(self):
        super().__init__(name="Alpha", signature="alpha-nasdaq")

    def get_analysis_framework(self) -> str:
        return """
### Core Concept
Statistical arbitrage: z-scores + residual returns + mean reversion

### Analysis Steps (10 minutes)

**Phase 1: Calculate Z-Scores (4 min)**
```python
# 20-day rolling mean and std dev
# Z-score = (price - mean) / std
# Signals: |z| > 2.0 = extreme
```

**Phase 2: Residual Analysis (3 min)**
```python
# Stock vs index regression
# Identify under/over-performers
# Residual return patterns
```

**Phase 3: Mean Reversion Setup (2 min)**
```python
# Entry: |z| > 2.0 + negative residuals
# Exit: z returns to [-1, 1] range
# Risk: position size based on z-score
```

**Phase 4: Decision (1 min)**
- BUY: z < -2.0 (oversold) + fundamentals OK
- SELL: z > 2.0 (overbought) OR z returns to mean
- HOLD: No extreme z-scores

### Trading Rules
- Hold 8-12 positions
- Weekly rebalancing
- Pairs/groups for hedging
"""

    def get_risk_rules(self) -> dict:
        return {'max_position': 0.2, 'min_cash': 0.1, 'stop_loss': 0.08, 'max_positions': 12, 'confidence_threshold': 0.7}

"""
Factor Strategy - Academic Multi-Factor Investing for NASDAQ 100

Philosophy: Evidence-based factor investing following academic research.
"""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agent.claude_code_agent.shared.base_strategy import BaseStrategy


class FactorStrategy(BaseStrategy):
    """Academic Multi-Factor Investing for NASDAQ 100"""

    def __init__(self):
        super().__init__(name="Factor", signature="factor-nasdaq")

    def get_analysis_framework(self) -> str:
        return """
### Core Concept
Four-factor model: Momentum (30%) + Value (30%) + Quality (20%) + Low-Volatility (20%)

### Analysis Steps (10 minutes)

**Phase 1: Momentum Factor (3 min)**
```python
# 12-month price momentum
# Exclude last month (reversal)
# Relative strength ranking
```

**Phase 2: Value Factor (2 min)**
```python
# E/P (inverse P/E)
# B/M (book-to-market)
# Cash flow yield
```

**Phase 3: Quality Factor (2 min)**
```python
# ROE, ROA, profit margins
# Earnings stability
# Low accruals
```

**Phase 4: Low-Vol Factor (2 min)**
```python
# 60-day volatility
# Beta vs index
# Downside risk metrics
```

**Phase 5: Portfolio Construction (1 min)**
```python
# Composite score: 0.3*mom + 0.3*val + 0.2*qual + 0.2*lowvol
# Hold 15-20 stocks (diversified)
# Monthly rebalancing
```

### Decision Criteria
- BUY: Top 20% composite score
- SELL: Drops below median
- HOLD: Still above median
"""

    def get_risk_rules(self) -> dict:
        return {'max_position': 0.12, 'min_cash': 0.15, 'stop_loss': 0.12, 'max_positions': 20, 'confidence_threshold': 0.7}

"""
Portfolio Strategy - Multi-Factor Portfolio for NASDAQ 100

Philosophy: Combine momentum + value + quality factors for balanced returns.
"""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agent.claude_code_agent.shared.base_strategy import BaseStrategy


class PortfolioStrategy(BaseStrategy):
    """Multi-Factor Portfolio for NASDAQ 100"""

    def __init__(self):
        super().__init__(name="Portfolio", signature="portfolio-nasdaq")

    def get_analysis_framework(self) -> str:
        return """
### Core Concept
Multi-factor scoring: Momentum (40%) + Value (30%) + Quality (30%)

### Analysis Steps (10 minutes)

**Phase 1: Momentum Score (3 min)**
```python
# Price trend (SMA crossovers, RSI)
# Relative strength vs index
# 6-month momentum
```

**Phase 2: Value Score (3 min)**
```python
# P/E, P/B, dividend yield
# Earnings growth
# Valuation percentile
```

**Phase 3: Quality Score (3 min)**
```python
# ROE, ROA profitability
# Debt/equity ratio
# Operating margins
```

**Phase 4: Portfolio Construction (1 min)**
```python
# Combined score = 0.4*momentum + 0.3*value + 0.3*quality
# Hold top 8-12 stocks
# Rebalance monthly
```

### Decision Criteria
- BUY: Top quartile combined score
- SELL: Drops below median OR better opportunity
- HOLD: Still in top half, no better alternatives
"""

    def get_risk_rules(self) -> dict:
        return {'max_position': 0.12, 'min_cash': 0.1, 'stop_loss': 0.12, 'max_positions': 12, 'confidence_threshold': 0.7}

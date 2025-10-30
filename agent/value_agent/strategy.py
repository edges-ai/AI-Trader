"""
Value Strategy - Fundamental Value Investing for NASDAQ 100

Philosophy: Buy quality companies at reasonable prices. Focus on fundamentals over technicals.
"""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agent.claude_code_agent.shared.base_strategy import BaseStrategy


class ValueStrategy(BaseStrategy):
    """Fundamental Value Investing for NASDAQ 100"""

    def __init__(self):
        super().__init__(name="Value", signature="value-nasdaq")

    def get_analysis_framework(self) -> str:
        return """
### Core Concept
Buy quality at reasonable prices. Patient 6-12 month holding periods.

### Analysis Steps (10 minutes)

**Phase 1: Valuation Screening (5 min)**
```
Use Playwright to research:
- P/E ratio (target: <25)
- P/B ratio (target: >1.0)
- Dividend yield (prefer >2%)
- Earnings growth
```

**Phase 2: Quality Check (3 min)**
```
- Profitability: Positive and growing
- Debt levels: Manageable
- Competitive moat
```

**Phase 3: Margin of Safety (2 min)**
```
- Current price vs intrinsic value
- Target: 15-20% discount
- Catalyst for revaluation?
```

### Decision Criteria
- BUY: P/E <25, quality business, 15%+ margin of safety
- SELL: Valuation reached fair value OR fundamentals deteriorate
- HOLD: Still undervalued, waiting for catalyst
"""

    def get_risk_rules(self) -> dict:
        return {'max_position': 0.2, 'min_cash': 0.15, 'stop_loss': 0.15, 'max_positions': 10, 'confidence_threshold': 0.75}

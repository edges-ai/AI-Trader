"""
ClaudeCodeAgent - Meta-agent using claude CLI for advanced trading analysis.

This agent leverages Claude Code's unique capabilities:
- Deep code analysis and introspection
- Web research via Playwright MCP
- Multi-step reasoning via Sequential Thinking MCP
- Tool creation and automation

## Simple Strategy Framework

Each strategy is self-contained (~150 lines):
- Strategy class: Defines methodology and risk rules
- Agent class: Complete ready-to-use implementation

Start small, add complexity only when needed.

## Available Strategies

- **MomentumNASDAQAgent**: Technical trend following (SMA, RSI)
- **ValueNASDAQAgent**: Fundamental value investing (P/E, P/B)
- **PortfolioNASDAQAgent**: Multi-factor portfolio (momentum + value + quality)
- **AlphaNASDAQAgent**: Statistical arbitrage (z-scores, mean reversion)
- **FactorNASDAQAgent**: Academic multi-factor (momentum, value, quality, low-vol)

## Usage

```python
from agent.claude_code_agent import AlphaNASDAQAgent

agent = AlphaNASDAQAgent(
    initial_cash=10000.0,
    init_date="2025-01-01"
)
```

Or via config file:
```bash
python main.py configs/alpha_config.json
```
"""

from .claude_code_agent import ClaudeCodeAgent

# Note: Strategy agents are now self-contained in separate directories
# Import them from agent.momentum_agent, agent.value_agent, etc.

__all__ = [
    # Base agent
    'ClaudeCodeAgent',
]

__version__ = '3.0.0'  # Simplified architecture

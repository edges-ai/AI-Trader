# Alpha Agent

Statistical Arbitrage for NASDAQ 100

## Strategy Overview

**Philosophy**: Hunt for alpha using statistical patterns and mean reversion.

**MCP Tools**: sequential-thinking

## Risk Management

- Max position: 20% of portfolio
- Min cash buffer: 10%
- Stop loss: 8% from entry
- Max positions: 12 stocks
- Min confidence: 70% to trade

## Usage

```bash
python main.py configs/alpha_config.json
```

## Files

- `alpha_agent.py` - Agent implementation
- `strategy.py` - AlphaStrategy class
- `CLAUDE.md` - Trading instructions (auto-generated)
- `README.md` - This file

# Factor Agent

Academic Multi-Factor Investing for NASDAQ 100

## Strategy Overview

**Philosophy**: Evidence-based factor investing following academic research.

**MCP Tools**: sequential-thinking

## Risk Management

- Max position: 12% of portfolio
- Min cash buffer: 15%
- Stop loss: 12% from entry
- Max positions: 20 stocks
- Min confidence: 70% to trade

## Usage

```bash
python main.py configs/factor_config.json
```

## Files

- `factor_agent.py` - Agent implementation
- `strategy.py` - FactorStrategy class
- `CLAUDE.md` - Trading instructions (auto-generated)
- `README.md` - This file

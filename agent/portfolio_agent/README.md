# Portfolio Agent

Multi-Factor Portfolio for NASDAQ 100

## Strategy Overview

**Philosophy**: Combine momentum + value + quality factors for balanced returns.

**MCP Tools**: sequential-thinking

## Risk Management

- Max position: 12% of portfolio
- Min cash buffer: 10%
- Stop loss: 12% from entry
- Max positions: 12 stocks
- Min confidence: 70% to trade

## Usage

```bash
python main.py configs/portfolio_config.json
```

## Files

- `portfolio_agent.py` - Agent implementation
- `strategy.py` - PortfolioStrategy class
- `CLAUDE.md` - Trading instructions (auto-generated)
- `README.md` - This file

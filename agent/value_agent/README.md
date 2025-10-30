# Value Agent

Fundamental Value Investing for NASDAQ 100

## Strategy Overview

**Philosophy**: Buy quality companies at reasonable prices. Focus on fundamentals over technicals.

**MCP Tools**: sequential-thinking + playwright (research)

## Risk Management

- Max position: 20% of portfolio
- Min cash buffer: 15%
- Stop loss: 15% from entry
- Max positions: 10 stocks
- Min confidence: 75% to trade

## Usage

```bash
python main.py configs/value_config.json
```

## Files

- `value_agent.py` - Agent implementation
- `strategy.py` - ValueStrategy class
- `CLAUDE.md` - Trading instructions (auto-generated)
- `README.md` - This file

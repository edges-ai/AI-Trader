# Momentum Agent

Technical momentum trend-following strategy for NASDAQ 100 stocks using Claude Code's autonomous analysis with sequential reasoning.

## Overview

**Strategy**: SMA crossover (5-day vs 20-day) + RSI confirmation (40-70) + Volume validation (>0.8x avg)

**Risk Management**:
- Max position: 15% of portfolio
- Min cash buffer: 20%
- Stop loss: 10% from entry
- Max positions: 10-15 stocks
- Min confidence: 70% to trade

## Prerequisites

```bash
# 1. Install Claude CLI
npm install -g @anthropic-ai/claude-code

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Configure API keys in .env
ALPHAADVANTAGE_API_KEY=your_key
JINA_API_KEY=your_key
ANTHROPIC_API_KEY=your_key

# 4. Prepare data
cd data && python get_daily_price.py && python merge_jsonl.py && cd ..

# 5. Start MCP services
cd agent_tools && python start_mcp_services.py && cd ..
```

## Configuration

### File: `configs/momentum_config.json`

```json
{
  "agent_type": "MomentumNASDAQAgent",
  "date_range": {
    "init_date": "2025-10-01",
    "end_date": "2025-10-21"
  },
  "models": [
    {
      "name": "momentum-nasdaq",
      "basemodel": "anthropic/claude-3.7-sonnet",
      "signature": "momentum-nasdaq-conservative",
      "enabled": true
    }
  ],
  "agent_config": {
    "max_steps": 1,
    "max_retries": 3,
    "base_delay": 2.0,
    "initial_cash": 10000.0
  },
  "log_config": {
    "log_path": "./data/agent_data"
  }
}
```

### Key Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `agent_type` | Must be `"MomentumNASDAQAgent"` | - |
| `init_date` | Start date (YYYY-MM-DD) | 2025-10-01 |
| `end_date` | End date (YYYY-MM-DD) | 2025-10-21 |
| `signature` | Unique ID for this run | momentum-nasdaq-conservative |
| `max_steps` | Reasoning steps per day | 1 |
| `initial_cash` | Starting capital (USD) | 10000.0 |

## Usage Commands

### Basic Run

```bash
# Run with default config
python main.py configs/momentum_config.json
```

### Custom Date Range

```bash
# Override dates via environment variables
export INIT_DATE="2025-10-01"
export END_DATE="2025-10-15"
python main.py configs/momentum_config.json
```

### Complete Pipeline

```bash
# Data + MCP services + Trading + Dashboard
./main.sh
```

### Analysis Tools

```bash
# Analyze agent performance
python tools/analyze_agent.py momentum-nasdaq-conservative

# Compare multiple strategies
python tools/compare_strategies.py --all

# Compare specific agents
python tools/compare_strategies.py momentum-nasdaq-conservative value-nasdaq alpha-nasdaq

# List available agents
python tools/analyze_agent.py --list
```

### View Results

```bash
# Latest position
tail -1 data/agent_data/momentum-nasdaq-conservative/position/position.jsonl | jq .

# Decision logs
cat data/agent_data/momentum-nasdaq-conservative/log/2025-10-15/log.jsonl | jq .

# Web dashboard
cd docs && python3 -m http.server 8888
# Open http://localhost:8888
```

## Output Structure

```
data/agent_data/momentum-nasdaq-conservative/
├── position/
│   └── position.jsonl       # Trade execution records
├── log/{date}/
│   └── log.jsonl           # Daily decision logs
└── metrics/
    └── metrics.jsonl       # Performance metrics
```

### Position Format

```json
{
  "date": "2025-10-20",
  "id": 5,
  "this_action": {
    "action": "buy",
    "symbol": "AAPL",
    "amount": 10
  },
  "positions": {
    "AAPL": 10,
    "MSFT": 5,
    "CASH": 8234.50
  }
}
```

## Strategy Details

### Entry Signals (all must be true)

1. **Trend**: SMA(5) > SMA(20) AND Price > SMA(5)
2. **Momentum**: RSI between 40-70 (not overbought)
3. **Volume**: Current volume > 0.8x average

### Exit Signals (any triggers exit)

1. **Trend Reversal**: SMA(5) < SMA(20)
2. **Overbought**: RSI > 75
3. **Stop Loss**: Position down 10% from entry

### Analysis Phases (8 minutes per day)

1. Trend Identification (3 min) - Calculate SMAs, identify crossovers
2. RSI Confirmation (2 min) - Calculate 14-period RSI, validate zones
3. Volume Check (1 min) - Compare current vs average volume
4. Decision Synthesis (2 min) - Combine signals, output decision

## Customization

### Modify Risk Parameters

Edit `agent/momentum_agent/strategy.py`:

```python
def get_risk_rules(self) -> dict:
    return {
        "max_position": 0.15,        # 15% max per stock
        "min_cash": 0.20,            # 20% min cash buffer
        "stop_loss": 0.10,           # 10% stop loss
        "max_positions": 15,         # Max 15 stocks
        "confidence_threshold": 0.70 # 70% min confidence
    }
```

### Adjust Technical Indicators

Modify SMA periods in `strategy.py`:

```python
# Change from default 5/20 to 10/50
sma_short = sum(prices[-10:]) / 10   # Was 5
sma_long = sum(prices[-50:]) / 50    # Was 20
```

## Troubleshooting

### MCP Services Not Running

```bash
cd agent_tools
python start_mcp_services.py status
python start_mcp_services.py  # Restart if needed
```

### No Trades Executed

- Lower `confidence_threshold` in `strategy.py`
- Check market conditions (volatile periods needed)
- Verify price data: `jq . data/merged.jsonl | head -50`

### API Rate Limits

```bash
# Don't re-fetch data unnecessarily
# Skip: python get_daily_price.py

# Alpha Vantage free tier: 5 calls/min, 500/day
```

### Data Freshness

```bash
# Check last update
ls -lh data/merged.jsonl

# Refresh if needed
cd data && python get_daily_price.py && python merge_jsonl.py && cd ..
```

## Performance Metrics

Analysis tools calculate:
- **Cumulative Return**: Total portfolio return
- **Sharpe Ratio**: Risk-adjusted return (annualized)
- **Max Drawdown**: Maximum peak-to-trough decline
- **Volatility**: Standard deviation of returns
- **Win Rate**: Percentage of profitable trades
- **Profit/Loss Ratio**: Average win / average loss

Example output:

```
📊 Analyzing Agent: momentum-nasdaq-conservative
================================================================================
Date Range: 2025-10-01 to 2025-10-21

Performance Report:
├─ Cumulative Return:      12.45%
├─ Annualized Return:      89.32%
├─ Sharpe Ratio:           1.85
├─ Max Drawdown:           -8.23%
├─ Volatility:             15.67%
├─ Win Rate:              65.22%
└─ Number of Trades:       45
```

## Files

- `momentum_agent.py` - Agent implementation
- `strategy.py` - MomentumStrategy class
- `CLAUDE.md` - Trading instructions (auto-generated)

## Related Documentation

- [Main AI-Trader README](../../README.md) - Platform overview
- [Base Agent](../base_agent/README.md) - Standard MCP agent
- [Claude Code Agent](../claude_code_agent/README.md) - Advanced meta-analyst

## License

Part of the AI-Trader project. See main repository for license.

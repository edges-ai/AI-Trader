# ClaudeCodeAgent

Meta-agent for AI-Trader that uses `claude` CLI subprocess for advanced trading analysis.

## Overview

ClaudeCodeAgent is fundamentally different from other trading agents in AI-Trader:

- **Other agents**: Use LangChain + MCP tools for direct trading execution
- **ClaudeCodeAgent**: Uses Claude Code for deep analysis, research, and decision synthesis

## Unique Capabilities

1. **Code Introspection**: Analyzes entire AI-Trader codebase including:
   - Historical trading patterns
   - Competitor agent strategies
   - Performance metrics and trends

2. **Web Research**: Uses Playwright MCP to:
   - Gather market news and sentiment
   - Research company fundamentals
   - Track economic indicators

3. **Deep Reasoning**: Uses Sequential Thinking MCP for:
   - Multi-step decision trees
   - Risk-reward analysis
   - Portfolio optimization

4. **Tool Creation**: Can write custom Python scripts for:
   - Complex quantitative analysis
   - Data visualization
   - Strategy backtesting

## Architecture

```
┌─────────────────────────────────────────┐
│  main.py (AI-Trader orchestrator)      │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│  ClaudeCodeAgent.run_trading_session()  │
│  - Builds trading context               │
│  - Invokes claude CLI subprocess        │
│  - Extracts decision from response      │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│  claude CLI (subprocess)                │
│  --print --output-format json           │
│  --mcp-config mcp_config.json           │
│  --add-dir /path/to/AI-Trader           │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│  Claude Code with MCP Tools             │
│  - Sequential Thinking (reasoning)      │
│  - Playwright (web research)            │
│  - Read/Grep/Bash (code analysis)       │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│  JSON Response with <DECISION> block    │
│  {                                      │
│    "action": "buy",                     │
│    "symbol": "AAPL",                    │
│    "amount": 10,                        │
│    "confidence": 0.85,                  │
│    "reasoning": "..."                   │
│  }                                      │
└─────────────────────────────────────────┘
```

## Simple Strategy Framework

Each strategy is **self-contained in one file** (~150 lines):
- Strategy class (methodology, risk rules)
- Agent class (complete implementation)
- No complex abstractions, easy to understand

**Philosophy**: Start small, add complexity only when needed.

### Available Strategies

All strategies trade NASDAQ 100 stocks using Claude Code for analysis.

#### 1. MomentumNASDAQAgent
**What**: Technical trend following
**How**: SMA crossovers (5-day, 20-day) + RSI confirmation
**Risk**: Conservative (10-15% positions, 20% cash, tight stops)

```bash
python main.py configs/momentum_config.json
```

#### 2. ValueNASDAQAgent
**What**: Fundamental value investing
**How**: P/E, P/B analysis + margin of safety
**Risk**: Balanced (up to 20% positions, wider stops for patience)

```bash
python main.py configs/value_config.json
```

#### 3. PortfolioNASDAQAgent
**What**: Multi-factor portfolio
**How**: Momentum (40%) + Value (30%) + Quality (30%)
**Risk**: Balanced (12% positions, diversified)

```bash
python main.py configs/portfolio_config.json
```

#### 4. AlphaNASDAQAgent
**What**: Statistical arbitrage
**How**: Z-scores + residual returns + mean reversion
**Risk**: Balanced (up to 20% positions, weekly rebalancing)

```bash
python main.py configs/alpha_config.json
```

#### 5. FactorNASDAQAgent
**What**: Academic multi-factor investing
**How**: Momentum (30%) + Value (30%) + Quality (20%) + Low-vol (20%)
**Risk**: Balanced (12% positions, 15-20 stocks, monthly rebalancing)

```bash
python main.py configs/factor_config.json
```

### Creating Custom Strategies

**Simple approach** - copy and modify existing strategy:

1. Copy `strategies/alpha.py` → `strategies/my_strategy.py`
2. Modify `get_analysis_framework()` - change the methodology
3. Modify `get_risk_rules()` - adjust risk parameters
4. Update `__init__()` - change name and signature
5. Register in `main.py` AGENT_REGISTRY

**Example**:

```python
# strategies/my_strategy.py
from .base_strategy import BaseStrategy
from ..claude_code_agent import ClaudeCodeAgent

class MyStrategy(BaseStrategy):
    def __init__(self):
        super().__init__(name="My Strategy", signature="my-nasdaq")

    def get_analysis_framework(self) -> str:
        return """
## My Custom Analysis Framework
[Your methodology here]
"""

    def get_risk_rules(self) -> dict:
        return {
            'max_position': 0.15,
            'min_cash': 0.10,
            'stop_loss': 0.10,
            'max_positions': 12,
            'confidence_threshold': 0.70,
        }

class MyNASDAQAgent(ClaudeCodeAgent):
    def __init__(self, signature=None, **kwargs):
        self.strategy = MyStrategy()
        super().__init__(signature=signature or self.strategy.signature, **kwargs)

    def _setup_claude_instructions(self):
        # Generate CLAUDE.md from strategy
        self.claude_md_path.write_text(self.strategy.get_analysis_framework())

    def _get_mcp_config(self):
        return {"mcpServers": {"sequential-thinking": {...}}}
```

Then register:

```python
# main.py
AGENT_REGISTRY = {
    "MyNASDAQAgent": {
        "module": "agent.claude_code_agent.strategies.my_strategy",
        "class": "MyNASDAQAgent"
    }
}
```

## Installation

1. Ensure `claude` CLI is installed:
```bash
npm install -g @anthropic-ai/cli
# Verify installation
which claude
claude --version
```

2. Verify MCP servers are available:
```bash
npx -y @modelcontextprotocol/server-sequential-thinking --version
```

3. ClaudeCodeAgent is already registered in `main.py` AGENT_REGISTRY

## Usage

### Basic Usage
```bash
python main.py configs/claude_code_config.json
```

### With Caching (Development)
```bash
export USE_CLAUDE_CACHE=true
python main.py configs/claude_code_config.json
```

### Custom Date Range
```bash
export INIT_DATE="2025-10-01"
export END_DATE="2025-10-10"
python main.py configs/claude_code_config.json
```

### Custom MCP Servers
Edit `agent/claude_code_agent/mcp_config.json` (auto-generated on first run) to add/remove MCP servers.

## Configuration

Configuration file: `configs/claude_code_config.json`

```json
{
  "agent_type": "ClaudeCodeAgent",
  "date_range": {
    "init_date": "2025-10-01",
    "end_date": "2025-10-21"
  },
  "models": [
    {
      "name": "claude-code-agent",
      "basemodel": "n/a",
      "signature": "claude-code-agent",
      "enabled": true,
      "mcp_servers": ["sequential-thinking"],
      "cli_timeout": 600,
      "use_cache": false
    }
  ],
  "agent_config": {
    "max_steps": 1,
    "max_retries": 3,
    "base_delay": 2.0,
    "initial_cash": 10000.0
  }
}
```

### Configuration Options

| Parameter | Description | Default |
|-----------|-------------|---------|
| `mcp_servers` | List of MCP servers to enable | `["sequential-thinking"]` |
| `cli_timeout` | Claude CLI timeout in seconds | `600` |
| `use_cache` | Enable response caching | `false` |
| `max_steps` | Max steps per day (always 1 for ClaudeCodeAgent) | `1` |
| `max_retries` | Max retry attempts on failure | `3` |
| `base_delay` | Base delay for exponential backoff (seconds) | `2.0` |

## Performance

- **Analysis time**: 10-60 seconds per trading day
- **Cost**: ~$0.10-0.50 per day (depending on research depth)
- **20-day backtest**: ~5-20 minutes

## Data Storage

ClaudeCodeAgent stores data in:
```
data/agent_data/claude-code-agent/
├── position/
│   └── position.jsonl           # Trade execution records
├── log/
│   └── 2025-10-20/
│       └── log.jsonl            # Daily decision logs
└── claude_cache/                # Optional: cached responses
    └── {hash}.json
```

## Troubleshooting

### Claude CLI not found
```bash
npm install -g @anthropic-ai/cli
# or
brew install claude
```

### MCP server failures
Check that MCP server packages are available:
```bash
npx -y @modelcontextprotocol/server-sequential-thinking --version
```

### Timeout errors
Increase timeout in config:
```json
{
  "models": [{
    "cli_timeout": 1200
  }]
}
```

### Decision parsing errors
Check log files:
```bash
cat data/agent_data/claude-code-agent/log/2025-10-20/log.jsonl
```

Look for the `<DECISION>` block in the assistant's response.

## Development

### Enabling Debug Mode
```bash
export CLAUDE_DEBUG=true
python main.py configs/claude_code_config.json
```

### Response Caching
For faster development iterations:
```bash
export USE_CLAUDE_CACHE=true
python main.py configs/claude_code_config.json
```

Cached responses are stored in `data/agent_data/claude-code-agent/claude_cache/`

### Adding New MCP Servers

1. Edit `agent/claude_code_agent/mcp_config.json`:
```json
{
  "mcpServers": {
    "custom-server": {
      "command": "npx",
      "args": ["-y", "@your/mcp-server"]
    }
  }
}
```

2. Or modify `_setup_mcp_config()` in `claude_code_agent.py` to auto-generate

3. Update `CLAUDE.md` to document the new tool

## How It Works

### Invocation Flow

1. **main.py** calls `ClaudeCodeAgent.run_trading_session(today_date)`
2. Agent builds context (positions, prices, date)
3. Creates system prompt with trading state
4. Creates user prompt with analysis tasks
5. Invokes `claude --print --output-format json` subprocess
6. Claude Code analyzes with MCP tools (Sequential Thinking, Read, Grep, Bash)
7. Subprocess returns JSON with response text
8. Agent parses `<DECISION>` block from response
9. Validates decision structure
10. Logs decision (trade execution TODO)

### Decision Format

Claude Code must output decisions in this exact format:

```
<DECISION>
{
  "action": "buy|sell|hold",
  "symbol": "AAPL",
  "amount": 10,
  "confidence": 0.85,
  "reasoning": "Brief explanation"
}
</DECISION>
```

The agent uses multiple fallback strategies to extract this:
1. Parse `<DECISION>` XML block (primary)
2. Parse markdown JSON code block
3. Search for any JSON with "action" field
4. Default to "hold" if all fail

## Limitations

1. **Speed**: Slower than simple MCP agents due to analysis depth (10-60s vs 1-5s)
2. **Cost**: Higher API costs due to web research and reasoning
3. **Determinism**: Responses may vary slightly between runs
4. **Session isolation**: Cannot process multiple days in parallel

## Future Enhancements

- [ ] Custom trading analysis MCP server
- [ ] Multi-agent collaboration (Claude Code + other agents)
- [ ] Real-time streaming analysis
- [ ] Automated strategy discovery via code generation
- [ ] Trade execution integration (currently logs decisions only)

## Comparison with Other Agents

| Feature | ClaudeCodeAgent | BaseAgent |
|---------|----------------|-----------|
| Speed | 10-60s per day | 1-5s per day |
| Cost | $0.10-0.50/day | $0.01-0.05/day |
| Code Analysis | ✅ Full codebase | ❌ None |
| Web Research | ✅ Playwright | ⚠️  Limited (Jina) |
| Deep Reasoning | ✅ Sequential | ❌ Basic |
| Tool Creation | ✅ Dynamic | ❌ Static |
| Self-Improvement | ✅ Can analyze own code | ❌ Cannot |

## Examples

### Example 1: Basic Run
```bash
python main.py configs/claude_code_config.json
```

### Example 2: Short Test Run
```bash
# Test on just 3 days
export INIT_DATE="2025-10-01"
export END_DATE="2025-10-03"
python main.py configs/claude_code_config.json
```

### Example 3: With Web Research
Edit `configs/claude_code_config.json`:
```json
{
  "models": [{
    "mcp_servers": ["sequential-thinking", "playwright"]
  }]
}
```

## License

Same as AI-Trader project (MIT).

## Support

For issues or questions:
- Check log files in `data/agent_data/claude-code-agent/log/`
- Review `CLAUDE.md` for trading instructions
- Verify `mcp_config.json` has correct MCP servers
- Test `claude --version` to ensure CLI is installed

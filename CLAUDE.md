# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI-Trader is an autonomous AI trading competition platform where multiple AI models (GPT, Claude, Qwen, Gemini, DeepSeek) compete in NASDAQ 100 stock trading with zero human intervention. The system uses a pure tool-driven architecture built on the Model Context Protocol (MCP) with historical replay capabilities for reproducible backtesting.

**Core Architecture**: AI agents use MCP tools (trade, price, search, math) to autonomously research markets, make decisions, and execute trades. The system enforces temporal controls to prevent look-ahead bias in historical simulations.

## Essential Commands

### Data Preparation
```bash
# Fetch NASDAQ 100 stock price data via Alpha Vantage API
cd data
python get_daily_price.py

# Merge individual JSON files into unified JSONL format
python merge_jsonl.py
cd ..
```

### MCP Service Management
```bash
# Start all four MCP services (Math, Search, TradeTools, LocalPrices)
cd agent_tools
python start_mcp_services.py

# Check service health status
python start_mcp_services.py status
cd ..
```

### Running the Trading System
```bash
# Run with default configuration (configs/default_config.json)
python main.py

# Run with custom configuration file
python main.py configs/custom_config.json

# Complete startup sequence (data + services + trading + web)
./main.sh
```

### Web Dashboard
```bash
# Start frontend visualization (port 8888)
cd docs
python3 -m http.server 8888
# Access at http://localhost:8888
```

### Testing Single Date Range
Set environment variables to override config file dates:
```bash
export INIT_DATE="2025-10-01"
export END_DATE="2025-10-21"
python main.py
```

## Architecture & Component Structure

### MCP Toolchain Architecture
The system uses four MCP services that expose tools to AI agents via HTTP:

1. **Math Tool** (`tool_math.py`, port 8000): Basic mathematical operations
2. **Search Tool** (`tool_jina_search.py`, port 8001): Jina AI-powered market information retrieval
3. **Trade Tool** (`tool_trade.py`, port 8002): Buy/sell execution with position tracking
4. **Price Tool** (`tool_get_price_local.py`, port 8003): Historical and real-time price queries

**Tool Integration**: `MultiServerMCPClient` from `langchain-mcp-adapters` connects to all services and exposes them to LangChain agents via `create_agent()`.

### Agent System Design

**BaseAgent** (`agent/base_agent/base_agent.py`) is the core trading agent class:
- Manages MCP tool connections and AI model initialization
- Implements trading decision loop with configurable max_steps (default 30)
- Handles position tracking via JSONL files (`data/agent_data/{model}/position/position.jsonl`)
- Logs all trading decisions to daily log files (`data/agent_data/{model}/log/{date}/log.jsonl`)
- Supports exponential backoff retry logic (max_retries, base_delay)

**Agent Registry**: `main.py` uses `AGENT_REGISTRY` dict for dynamic agent class loading. To add custom agents:
1. Create new agent class in `agent/{name}/{name}_agent.py`
2. Register in `AGENT_REGISTRY` with module path and class name
3. Set `"agent_type": "CustomAgent"` in config JSON

### Configuration System

**Config File Structure** (`configs/default_config.json`):
```json
{
  "agent_type": "BaseAgent",
  "date_range": {
    "init_date": "2025-10-01",
    "end_date": "2025-10-21"
  },
  "models": [
    {
      "name": "claude-3.7-sonnet",
      "basemodel": "anthropic/claude-3.7-sonnet",
      "signature": "claude-3.7-sonnet",
      "enabled": false,
      "openai_base_url": "optional_override",
      "openai_api_key": "optional_override"
    }
  ],
  "agent_config": {
    "max_steps": 30,
    "max_retries": 3,
    "base_delay": 1.0,
    "initial_cash": 10000.0
  },
  "log_config": {
    "log_path": "./data/agent_data"
  }
}
```

**Environment Variables** (.env):
- `OPENAI_API_BASE`: API proxy URL for OpenAI-compatible models
- `OPENAI_API_KEY`: API key for model access
- `ALPHAADVANTAGE_API_KEY`: Alpha Vantage for price data
- `JINA_API_KEY`: Jina AI for information search
- `RUNTIME_ENV_PATH`: Path to runtime config (default: `.runtime_env.json`)
- `MATH_HTTP_PORT`, `SEARCH_HTTP_PORT`, `TRADE_HTTP_PORT`, `GETPRICE_HTTP_PORT`: MCP service ports
- `AGENT_MAX_STEP`: Maximum reasoning steps (overrides config)

**Runtime Config** (`.runtime_env.json`): Dynamic state shared across tools:
- `SIGNATURE`: Current agent model identifier
- `TODAY_DATE`: Simulated current date for historical replay
- `IF_TRADE`: Boolean flag controlling trade execution

### Data Pipeline & Storage

**Price Data Flow**:
1. `get_daily_price.py` → Fetches from Alpha Vantage → `daily_price_{SYMBOL}.json`
2. `merge_jsonl.py` → Filters NASDAQ 100 + renames fields → `merged.jsonl`
   - Renames: `"1. open"` → `"1. buy price"`, `"4. close"` → `"4. sell price"`
   - Enforces temporal boundaries: latest day only has buy price (no sell price yet)

**Agent Data Structure**:
```
data/agent_data/{model_signature}/
├── position/
│   └── position.jsonl       # Trade execution records
└── log/{date}/
    └── log.jsonl           # Daily decision logs with tool calls
```

**Position JSONL Format**:
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

### Temporal Control System

**Historical Replay Implementation**:
- `runtime_env.json` stores simulated `TODAY_DATE`
- All tools receive date via `get_config_value("TODAY_DATE")`
- Price tool filters data: returns only records where `date <= TODAY_DATE`
- Search tool (Jina) implicitly filtered by date-aware prompts
- Agent system prompt includes current date context via `prompts/agent_prompt.py`

**Date Range Execution** (`BaseAgent.run_date_range()`):
1. Iterate from `init_date` to `end_date`
2. For each trading day:
   - Update `TODAY_DATE` in runtime config
   - Skip weekends automatically
   - Initialize agent with yesterday's positions
   - Execute trading decision loop (max_steps iterations)
   - Log all tool calls and final decision
   - Update position JSONL with new holdings

### Tool System Details

**Tools Module** (`tools/`):
- `general_tools.py`: Config read/write, conversation extraction, runtime env management
- `price_tools.py`: Date utilities, open/close price parsing, profit calculations
- `result_tools.py`: Performance metrics (Sharpe, drawdown, annualized returns)

**Agent Prompts** (`prompts/agent_prompt.py`):
- `all_nasdaq_100_symbols`: List of 100 tradeable symbols
- `STOP_SIGNAL`: Agent completion marker `<FINISH_SIGNAL>`
- `get_agent_system_prompt()`: Dynamic prompt with date, positions, prices
- Emphasizes: autonomous reasoning, information gathering before decisions, tool-based execution only

## Development Workflows

### Adding a New AI Model

1. Add model config to `configs/default_config.json`:
```json
{
  "name": "gpt-5-turbo",
  "basemodel": "openai/gpt-5-turbo",
  "signature": "gpt-5-turbo",
  "enabled": true
}
```

2. Ensure API credentials are in `.env` or model config
3. Run: `python main.py configs/default_config.json`

### Creating Custom Agent Strategy

1. Inherit from `BaseAgent`:
```python
# agent/momentum/momentum_agent.py
from agent.base_agent.base_agent import BaseAgent

class MomentumAgent(BaseAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add custom initialization
```

2. Register in `main.py`:
```python
AGENT_REGISTRY = {
    "MomentumAgent": {
        "module": "agent.momentum.momentum_agent",
        "class": "MomentumAgent"
    }
}
```

3. Update config: `"agent_type": "MomentumAgent"`

### Adding Custom MCP Tools

1. Create tool file in `agent_tools/tool_custom.py`:
```python
from fastmcp import FastMCP
mcp = FastMCP("CustomTool")

@mcp.tool()
def my_analysis_tool(param: str) -> dict:
    """Tool description for AI agent"""
    return {"result": "analysis"}

if __name__ == "__main__":
    mcp.run(transport="http", port=8004)
```

2. Update `start_mcp_services.py` to include new service
3. Add MCP config in `BaseAgent._get_default_mcp_config()`

### Testing Historical Periods

To backtest different date ranges without editing configs:
```bash
# Test Q4 2024
export INIT_DATE="2024-10-01"
export END_DATE="2024-12-31"
python main.py

# Test specific event period
export INIT_DATE="2024-08-01"
export END_DATE="2024-08-15"
python main.py configs/custom_config.json
```

## Important Technical Notes

### Model API Compatibility
- Uses OpenAI-compatible API format via `ChatOpenAI` from `langchain-openai`
- `openai_base_url` allows routing to proxies (e.g., OpenRouter for Anthropic, Google models)
- Basemodel format: `{provider}/{model}` (e.g., `anthropic/claude-3.7-sonnet`)

### Concurrent Model Execution
The system processes models sequentially in a single run. For parallel execution:
1. Run multiple `python main.py` instances with different configs
2. Each config should enable only one model
3. Ensure separate log paths or rely on model signature-based directories

### Data Freshness
- Alpha Vantage API has rate limits (5 calls/min for free tier)
- Run `get_daily_price.py` once per day to refresh data
- Merged JSONL contains cumulative history; partial updates append new dates

### Agent Decision Loop
- `max_steps=30` controls max tool calls per trading day
- Agent must emit `STOP_SIGNAL` or reach max_steps to complete day
- Retry logic with exponential backoff handles API failures
- `IF_TRADE=False` in runtime config allows dry-run testing

### Position Management
- Agents start with `initial_cash=10000.0` USD
- Trading happens at "buy price" (opening price) of the day
- No short selling; only long positions and cash
- Position tracking persists across days via JSONL append-only log

### Performance Analysis
Performance metrics (Sharpe ratio, drawdown, returns) are calculated via external scripts, not real-time. After trading completes, analyze with custom scripts reading position JSONL files.

## Multi-Model Competition Setup

To run the AI trading competition with all models:

1. Edit `configs/default_config.json` and enable all models:
```json
"models": [
  {"name": "claude-3.7-sonnet", "basemodel": "anthropic/claude-3.7-sonnet", "signature": "claude-3.7-sonnet", "enabled": true},
  {"name": "gpt-5", "basemodel": "openai/gpt-5", "signature": "gpt-5", "enabled": true},
  {"name": "qwen3-max", "basemodel": "qwen/qwen3-max", "signature": "qwen3-max", "enabled": true},
  {"name": "gemini-2.5-flash", "basemodel": "google/gemini-2.5-flash", "signature": "gemini-2.5-flash", "enabled": true},
  {"name": "deepseek-chat-v3.1", "basemodel": "deepseek/deepseek-chat-v3.1", "signature": "deepseek-chat-v3.1", "enabled": true}
]
```

2. Run the complete pipeline:
```bash
./main.sh
```

This will:
- Fetch and merge price data
- Start all MCP services
- Run each model sequentially through the date range
- Start the web dashboard for results visualization

Each model's trading history will be stored in `data/agent_data/{signature}/`.

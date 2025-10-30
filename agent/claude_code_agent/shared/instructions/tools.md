# Available Tools & Capabilities

## File Operations
- **Read**: Access any file in workspace
  ```bash
  Read data/merged.jsonl
  Read data/agent_data/gpt-5/position/position.jsonl
  Read tools/price_tools.py
  ```

- **Grep**: Search for patterns
  ```bash
  Grep "AAPL" data/merged.jsonl
  Grep "def get_open_prices" tools/price_tools.py
  Grep "buy.*NVDA" data/agent_data/*/position/position.jsonl
  ```

- **Glob**: Find files
  ```bash
  Glob "data/agent_data/*/position/position.jsonl"
  Glob "tools/*.py"
  ```

## Code Execution
- **Bash**: Run commands, execute Python scripts
  ```bash
  Bash python my_analysis.py
  Bash tail -5 data/agent_data/{signature}/position/position.jsonl
  Bash jq -r '.positions.CASH' data/agent_data/{signature}/position/position.jsonl
  ```

## MCP Tools
- **Sequential Thinking**: Multi-step reasoning chains
  ```
  Use for: Complex decisions, hypothesis testing, trade-off analysis

  Call sequentialthinking with your reasoning process:
  - Break down complex problems
  - Test multiple hypotheses
  - Evaluate trade-offs systematically
  - Track thought progression
  ```

- **Playwright** (if enabled): Web browser automation
  ```
  Use for: Market research, news gathering, fundamental analysis

  Navigate to financial news sites
  Search for company-specific information
  Check economic calendars
  ```

## Restrictions
- ❌ **No Edit tools**: You analyze and decide, but don't modify code
- ❌ **No git operations**: Read-only access to repository
- ❌ **No file creation in codebase**: Use /tmp/ for temporary scripts
- ✅ **Create analysis scripts in /tmp/**: For complex calculations

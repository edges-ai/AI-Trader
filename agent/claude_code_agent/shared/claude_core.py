"""
ClaudeCodeAgent class - Meta-agent for AI-Trader using claude CLI subprocess

Provides advanced trading analysis capabilities through Claude Code's native tools:
- Code analysis of trading strategies and patterns
- Web research for market fundamentals
- Multi-step reasoning for complex decisions
- Tool creation and workflow automation
"""

import os
import sys
import json
import uuid
import subprocess
import asyncio
import re
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from agent.base_agent.base_agent import BaseAgent
from tools.general_tools import get_config_value, write_config_value
from tools.price_tools import get_open_prices, get_yesterday_open_and_close_price, get_today_init_position, get_yesterday_profit


class ClaudeCodeError(Exception):
    """Base exception for ClaudeCodeAgent errors"""
    pass


class ClaudeCodeAgent(BaseAgent):
    """
    Meta-agent that uses claude CLI subprocess for advanced trading analysis.

    Unique Capabilities:
    - Deep code analysis of trading strategies
    - Web research via integrated Playwright MCP
    - Tool creation and workflow automation
    - Multi-step reasoning with Sequential Thinking MCP
    - Access to full AI-Trader codebase for self-improvement

    Architecture:
        main.py → ClaudeCodeAgent.run_trading_session()
                → _invoke_claude_cli() [subprocess]
                → claude --print --output-format json
                → Claude Code with MCP tools
                → JSON response with <DECISION> block
                → _extract_decision() → validate → execute
    """

    def __init__(
        self,
        signature: str,
        basemodel: str,
        stock_symbols: Optional[List[str]] = None,
        log_path: Optional[str] = None,
        max_steps: int = 1,  # Only 1 step - full analysis in one call
        max_retries: int = 3,
        base_delay: float = 2.0,
        openai_base_url: Optional[str] = None,
        openai_api_key: Optional[str] = None,
        initial_cash: float = 10000.0,
        init_date: str = "2025-10-13",
        claude_workspace: Optional[str] = None,
        mcp_servers: Optional[List[str]] = None,
        cli_timeout: int = 600,
        use_cache: bool = False
    ):
        """
        Initialize ClaudeCodeAgent.

        Additional Args:
            claude_workspace: Workspace directory for Claude Code (defaults to project root)
            mcp_servers: List of MCP servers to enable (defaults to ['sequential-thinking'])
            cli_timeout: Timeout for claude CLI subprocess in seconds (default: 600)
            use_cache: Enable response caching for development (default: False)
        """
        # NOTE: basemodel is ignored - Claude Code uses its own model selection
        super().__init__(
            signature=signature,
            basemodel=basemodel,  # Pass through but won't be used
            stock_symbols=stock_symbols,
            log_path=log_path,
            max_steps=max_steps,
            max_retries=max_retries,
            base_delay=base_delay,
            openai_base_url=openai_base_url,
            openai_api_key=openai_api_key,
            initial_cash=initial_cash,
            init_date=init_date
        )

        # Claude Code specific configuration
        self.claude_workspace = claude_workspace or project_root
        self.mcp_servers = mcp_servers or ['sequential-thinking']
        self.cli_timeout = cli_timeout
        self.use_cache = use_cache or os.getenv("USE_CLAUDE_CACHE", "false").lower() == "true"
        self.session_id = None  # Will be set per trading day

        # Paths for Claude Code agent
        self.agent_dir = Path(self.claude_workspace) / "agent" / "claude_code_agent"
        self.mcp_config_path = self.agent_dir / "mcp_config.json"
        self.claude_md_path = self.agent_dir / "CLAUDE.md"
        self.cache_dir = Path(log_path) / signature / "claude_cache" if log_path else Path("./data/agent_data") / signature / "claude_cache"

        # Ensure agent directory exists
        self.agent_dir.mkdir(parents=True, exist_ok=True)

        if self.use_cache:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            print(f"📦 Response caching enabled: {self.cache_dir}")

        # Initialize MCP configuration and instructions
        self._setup_mcp_config()
        self._setup_claude_instructions()

        print(f"🤖 ClaudeCodeAgent initialized: {signature}")
        print(f"📁 Workspace: {self.claude_workspace}")
        print(f"🔧 MCP Servers: {', '.join(self.mcp_servers)}")
        print(f"⏱️  Timeout: {self.cli_timeout}s")

    def _setup_mcp_config(self) -> None:
        """Create MCP configuration for Claude Code."""
        mcp_config = {
            "mcpServers": {}
        }

        # Sequential Thinking MCP (for deep analysis)
        if 'sequential-thinking' in self.mcp_servers:
            mcp_config["mcpServers"]["sequential-thinking"] = {
                "command": "npx",
                "args": [
                    "-y",
                    "@modelcontextprotocol/server-sequential-thinking"
                ]
            }

        # Context7 MCP (for official docs lookup)
        if 'context7' in self.mcp_servers:
            mcp_config["mcpServers"]["context7"] = {
                "command": "npx",
                "args": [
                    "-y",
                    "@uptoaichat/mcp-server"
                ]
            }

        # Playwright MCP (for web research)
        if 'playwright' in self.mcp_servers:
            mcp_config["mcpServers"]["playwright"] = {
                "command": "npx",
                "args": [
                    "-y",
                    "@executeautomation/playwright-mcp-server"
                ]
            }

        # Write MCP config
        with open(self.mcp_config_path, 'w') as f:
            json.dump(mcp_config, f, indent=2)

        print(f"✅ Created MCP config at {self.mcp_config_path}")

    def _setup_claude_instructions(self) -> None:
        """
        Ensure CLAUDE.md exists with trading-specific instructions.
        Only creates if file doesn't exist - preserves user customizations.
        """
        # Don't overwrite existing CLAUDE.md - user may have customized it
        if self.claude_md_path.exists():
            print(f"✅ Using existing CLAUDE.md at {self.claude_md_path}")
            return

        # Create default CLAUDE.md only if missing
        instructions = """# Trading Analysis Instructions for Claude Code

## Your Role

You are an advanced trading analysis agent for the AI-Trader platform. You have access to:
- The entire AI-Trader codebase for analysis
- Historical price data in `data/merged.jsonl`
- Position tracking files in `data/agent_data/{model}/position/`
- Web research capabilities (if Playwright enabled)
- Deep reasoning via Sequential Thinking MCP

## Core Responsibilities

1. **Code Analysis**: Review trading strategies, identify patterns, suggest improvements
2. **Market Research**: Use web search to gather fundamental analysis on stocks
3. **Performance Analysis**: Analyze historical trades to identify winning patterns
4. **Tool Creation**: Build custom analysis tools when needed
5. **Strategy Synthesis**: Combine quantitative and qualitative analysis

## Trading Decision Framework

For each trading day, you will receive:
- Current date and positions
- Yesterday's prices and profits
- Today's opening prices

Your analysis should consider:
- Fundamental analysis from web research
- Technical patterns in price data
- Portfolio diversification
- Risk management principles
- Historical performance patterns

## Decision Output Format

**REQUIRED**: Always end your analysis with a structured decision in this exact format:

<DECISION>
{
  "action": "buy|sell|hold",
  "symbol": "AAPL",
  "amount": 10,
  "confidence": 0.85,
  "reasoning": "Brief explanation of decision rationale"
}
</DECISION>

### Decision Rules
- **action**: Must be "buy", "sell", or "hold"
- **symbol**: NASDAQ 100 stock symbol (required for buy/sell, empty string for hold)
- **amount**: Number of shares (integer, required for buy/sell, 0 for hold)
- **confidence**: Your conviction level from 0.0 to 1.0
- **reasoning**: Brief explanation (1-2 sentences)

## Available Tools

- **Read**: Access price data, positions, logs, and code files
- **Grep**: Search for patterns in codebase and data
- **Bash**: Run analysis scripts, process data, calculate metrics
- **Sequential Thinking** (MCP): Multi-step reasoning for complex decisions
- **Playwright** (MCP): Web research for market information (if enabled)

## Key Constraints

- Trading happens at opening price only
- No short selling (long positions only)
- Cash must remain >= 0
- NASDAQ 100 stocks only
- One decision per day
- You have 10 minutes (timeout) to complete analysis

## Example Analysis Flow

1. **Context Gathering**: Read today's prices and positions from data files
2. **Research**: Use Playwright to search market news for top holdings (if enabled)
3. **Data Analysis**: Grep historical data for price patterns and trends
4. **Reasoning**: Use Sequential Thinking for multi-step decision logic
5. **Decision**: Output structured decision with confidence score in <DECISION> format

## Important Notes

- You're competing against other AI models (GPT, Gemini, DeepSeek, Qwen, Claude)
- Your advantage is deep analysis capability and code introspection
- One thoughtful trade per day beats random activity
- Always output decision in the exact <DECISION> format shown above
- If uncertain or analysis is inconclusive, use action="hold" with confidence < 0.5

Remember: You're not just a trading bot - you're a meta-analyst that can write code, create tools, and perform deep research that other agents cannot.
"""

        with open(self.claude_md_path, 'w') as f:
            f.write(instructions)

        print(f"✅ Created CLAUDE.md at {self.claude_md_path}")

    async def initialize(self) -> None:
        """
        Override BaseAgent initialization.
        ClaudeCodeAgent doesn't use MCP client directly - it uses claude CLI.
        """
        print(f"🚀 Initializing ClaudeCodeAgent: {self.signature}")
        print(f"📁 Workspace: {self.claude_workspace}")
        print(f"🔧 MCP Servers: {', '.join(self.mcp_servers)}")

        # Verify claude CLI is available
        try:
            result = subprocess.run(
                ["claude", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            version = result.stdout.strip()
            print(f"✅ Claude CLI found: {version}")
        except FileNotFoundError:
            raise RuntimeError(
                "❌ Claude CLI not found. Install with: npm install -g @anthropic-ai/cli\n"
                "   Or follow instructions at: https://docs.claude.com/en/docs/claude-code"
            )
        except subprocess.TimeoutExpired:
            raise RuntimeError("❌ Claude CLI timeout during version check")

        print(f"✅ ClaudeCodeAgent {self.signature} initialization completed")

    def _get_cache_key(self, prompt: str, system_prompt: str) -> str:
        """Generate cache key from prompts."""
        combined = f"{system_prompt}\n{prompt}"
        return hashlib.sha256(combined.encode()).hexdigest()

    def _invoke_claude_cli(
        self,
        prompt: str,
        system_prompt: str,
        timeout: Optional[int] = None
    ) -> dict:
        """
        Invoke claude CLI subprocess and return parsed response.

        Args:
            prompt: User prompt for Claude Code
            system_prompt: System instructions
            timeout: Timeout in seconds (default: self.cli_timeout)

        Returns:
            Parsed JSON response from claude CLI

        Raises:
            TimeoutError: If subprocess times out
            ClaudeCodeError: If claude CLI returns error
            ValueError: If response JSON is invalid
        """
        if timeout is None:
            timeout = self.cli_timeout

        # Check cache first
        if self.use_cache:
            cache_key = self._get_cache_key(prompt, system_prompt)
            cache_file = self.cache_dir / f"{cache_key}.json"

            if cache_file.exists():
                print(f"📦 Using cached response for {cache_key[:8]}...")
                with open(cache_file, 'r') as f:
                    return json.load(f)

        cmd = [
            "claude",
            "--print",
            "--output-format", "json",
            "--system-prompt", system_prompt,
            "--mcp-config", str(self.mcp_config_path),
            "--strict-mcp-config",
            "--add-dir", self.claude_workspace,
            "--session-id", self.session_id,
            "--dangerously-skip-permissions",  # Auto-approve for subprocess
            prompt
        ]

        print(f"🔄 Invoking Claude CLI (session: {self.session_id[:8]}...)...")

        try:
            result = subprocess.run(
                cmd,
                cwd=self.claude_workspace,
                capture_output=True,
                text=True,
                timeout=timeout
            )

            if result.returncode != 0:
                raise ClaudeCodeError(
                    f"Claude CLI exited with code {result.returncode}\n"
                    f"stderr: {result.stderr}"
                )

            # Parse JSON output
            response = json.loads(result.stdout)

            # Check for error in response
            if response.get('is_error'):
                raise ClaudeCodeError(f"Claude CLI error: {response.get('result', 'Unknown error')}")

            # Log cost and performance
            cost = response.get('total_cost_usd', 0)
            duration = response.get('duration_ms', 0)
            turns = response.get('num_turns', 0)
            print(f"💰 Cost: ${cost:.4f} | ⏱️  Duration: {duration}ms | 🔄 Turns: {turns}")

            # Cache response if enabled
            if self.use_cache:
                cache_key = self._get_cache_key(prompt, system_prompt)
                cache_file = self.cache_dir / f"{cache_key}.json"
                with open(cache_file, 'w') as f:
                    json.dump(response, f, indent=2)

            return response

        except subprocess.TimeoutExpired:
            raise TimeoutError(f"Claude CLI timeout after {timeout}s")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON response from claude CLI: {e}\nOutput: {result.stdout[:500]}")
        except subprocess.CalledProcessError as e:
            raise ClaudeCodeError(f"Claude CLI subprocess error: {e.stderr}")

    async def _ainvoke_claude_with_retry(
        self,
        prompt: str,
        system_prompt: str
    ) -> dict:
        """
        Claude CLI invocation with exponential backoff retry.

        Args:
            prompt: User prompt
            system_prompt: System prompt

        Returns:
            Parsed response dict
        """
        for attempt in range(1, self.max_retries + 1):
            try:
                return self._invoke_claude_cli(prompt, system_prompt, timeout=self.cli_timeout)

            except TimeoutError as e:
                if attempt == self.max_retries:
                    # Timeout after all retries - return hold decision
                    print(f"❌ Timeout after {self.max_retries} retries, defaulting to hold")
                    return {
                        'result': '<DECISION>{"action": "hold", "symbol": "", "amount": 0, "confidence": 0.0, "reasoning": "Analysis timeout after all retries"}</DECISION>',
                        'is_error': False,
                        'error_type': 'timeout'
                    }
                print(f"⚠️ Timeout attempt {attempt}/{self.max_retries}, retrying after {self.base_delay * attempt}s...")
                await asyncio.sleep(self.base_delay * attempt)
                # Reduce timeout for next attempt
                self.cli_timeout = max(120, self.cli_timeout // 2)

            except ClaudeCodeError as e:
                if attempt == self.max_retries:
                    raise RuntimeError(f"Claude CLI failed after {self.max_retries} retries: {e}")
                print(f"⚠️ CLI error attempt {attempt}/{self.max_retries}, retrying after {self.base_delay * attempt}s...")
                print(f"   Error: {str(e)[:200]}")
                await asyncio.sleep(self.base_delay * attempt)

            except ValueError as e:
                # JSON decode error - non-retriable
                print(f"❌ Invalid JSON response: {e}")
                return {
                    'result': '<DECISION>{"action": "hold", "symbol": "", "amount": 0, "confidence": 0.0, "reasoning": "Invalid response format"}</DECISION>',
                    'is_error': True,
                    'error_type': 'json_decode'
                }

    def _extract_decision(self, response_text: str) -> dict:
        """
        Extract trading decision from Claude Code's response.
        Uses multiple fallback strategies for robust parsing.

        Args:
            response_text: Full response text from Claude Code

        Returns:
            Decision dict with action, symbol, amount, confidence, reasoning
        """
        # Strategy 1: Parse <DECISION> XML block
        match = re.search(
            r'<DECISION>\s*(\{.*?\})\s*</DECISION>',
            response_text,
            re.DOTALL
        )

        if match:
            try:
                decision = json.loads(match.group(1))
                if self._validate_decision(decision):
                    return decision
            except json.JSONDecodeError:
                pass

        # Strategy 2: Parse markdown code block with JSON
        match = re.search(r'```json\s*(\{.*?\})\s*```', response_text, re.DOTALL)
        if match:
            try:
                decision = json.loads(match.group(1))
                if self._validate_decision(decision):
                    return decision
            except json.JSONDecodeError:
                pass

        # Strategy 3: Search for any JSON object with "action" field
        json_objects = re.findall(r'\{[^{}]*"action"[^{}]*\}', response_text)
        for obj_str in json_objects:
            try:
                decision = json.loads(obj_str)
                if self._validate_decision(decision):
                    return decision
            except json.JSONDecodeError:
                continue

        # Fallback: Default to hold
        print("⚠️ Could not extract structured decision, defaulting to hold")
        return {
            "action": "hold",
            "symbol": "",
            "amount": 0,
            "confidence": 0.0,
            "reasoning": "Could not parse decision from Claude Code response"
        }

    def _validate_decision(self, decision: dict) -> bool:
        """
        Validate decision structure and content.

        Args:
            decision: Decision dict to validate

        Returns:
            True if valid, False otherwise
        """
        # Check required fields
        required_fields = ['action', 'symbol', 'amount', 'confidence', 'reasoning']
        if not all(field in decision for field in required_fields):
            return False

        # Validate action
        if decision['action'] not in ['buy', 'sell', 'hold']:
            return False

        # For hold, minimal validation
        if decision['action'] == 'hold':
            return True

        # Validate symbol against NASDAQ 100
        from prompts.agent_prompt import all_nasdaq_100_symbols
        if decision['symbol'] not in all_nasdaq_100_symbols:
            print(f"⚠️ Invalid symbol: {decision['symbol']} not in NASDAQ 100")
            return False

        # Validate amount
        if not isinstance(decision['amount'], (int, float)) or decision['amount'] <= 0:
            print(f"⚠️ Invalid amount: {decision['amount']}")
            return False

        # Validate confidence
        if not (0.0 <= decision.get('confidence', 0) <= 1.0):
            print(f"⚠️ Invalid confidence: {decision.get('confidence')}")
            return False

        return True

    async def run_trading_session(self, today_date: str) -> None:
        """
        Override trading session to use claude CLI instead of MCP tools.

        This is the main entry point for each trading day.

        Args:
            today_date: Trading date (YYYY-MM-DD)
        """
        print(f"\n{'='*60}")
        print(f"📈 Starting ClaudeCodeAgent trading session: {today_date}")
        print(f"{'='*60}\n")

        # Create new session ID for this day
        self.session_id = str(uuid.uuid4())

        # Set up logging
        from tools.general_tools import get_config_value
        log_dir = Path(self.data_path) / "log" / today_date
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / "log.jsonl"

        # Get trading context
        from prompts.agent_prompt import all_nasdaq_100_symbols

        try:
            yesterday_buy_prices, yesterday_sell_prices = get_yesterday_open_and_close_price(
                today_date, all_nasdaq_100_symbols
            )
            today_buy_prices = get_open_prices(today_date, all_nasdaq_100_symbols)
            today_positions = get_today_init_position(today_date, self.signature)
            yesterday_profit = get_yesterday_profit(
                today_date, yesterday_buy_prices, yesterday_sell_prices, today_positions
            )
        except Exception as e:
            print(f"❌ Error getting trading context: {e}")
            # Log error and skip this day
            self._log_error(log_file, f"Failed to get trading context: {e}")
            return

        # Build system prompt
        system_prompt = f"""You are a trading analysis agent for AI-Trader.

Today's Date: {today_date}

Current Positions: {json.dumps(today_positions, indent=2)}

Yesterday's Closing Prices: {json.dumps(yesterday_sell_prices, indent=2)}

Today's Opening Prices: {json.dumps(today_buy_prices, indent=2)}

Yesterday's Profit: {json.dumps(yesterday_profit, indent=2)}

Read the CLAUDE.md file in the agent/claude_code_agent/ directory for detailed instructions.
"""

        # Build user prompt
        user_prompt = f"""Analyze today's ({today_date}) trading opportunity and make a decision.

Use your capabilities to:
1. Review the codebase to understand past trading patterns
2. Research market conditions for key holdings (if Playwright enabled)
3. Analyze price trends in the historical data
4. Make an informed trading decision

**IMPORTANT**: You must output your decision in this exact format:

<DECISION>
{{
  "action": "buy|sell|hold",
  "symbol": "AAPL",
  "amount": 10,
  "confidence": 0.85,
  "reasoning": "Brief explanation"
}}
</DECISION>

Begin your analysis now."""

        # Log initial prompt
        with open(log_file, 'a') as f:
            f.write(json.dumps({
                "role": "system",
                "content": system_prompt[:500] + "..." if len(system_prompt) > 500 else system_prompt,
                "timestamp": datetime.now().isoformat()
            }) + "\n")
            f.write(json.dumps({
                "role": "user",
                "content": user_prompt,
                "timestamp": datetime.now().isoformat()
            }) + "\n")

        try:
            # Invoke Claude CLI with retry logic
            response = await self._ainvoke_claude_with_retry(user_prompt, system_prompt)

            # Extract response text
            response_text = response.get('result', '')

            # Log Claude Code's response
            with open(log_file, 'a') as f:
                f.write(json.dumps({
                    "role": "assistant",
                    "content": response_text,
                    "cost_usd": response.get('total_cost_usd', 0),
                    "session_id": self.session_id,
                    "timestamp": datetime.now().isoformat()
                }) + "\n")

            # Extract decision
            decision = self._extract_decision(response_text)

            print(f"\n📊 Decision: {decision['action'].upper()}", end="")
            if decision['action'] != 'hold':
                print(f" {decision.get('symbol', '')} x{decision.get('amount', 0)}", end="")
            print()
            print(f"🎯 Confidence: {decision.get('confidence', 0):.2%}")
            print(f"💭 Reasoning: {decision.get('reasoning', 'N/A')}")

            # Log decision
            with open(log_file, 'a') as f:
                f.write(json.dumps({
                    "role": "decision",
                    "decision": decision,
                    "timestamp": datetime.now().isoformat()
                }) + "\n")

            # TODO: Execute trade based on decision
            # For now, we just log the decision
            # Future: Implement trade execution via existing MCP trade tool

        except Exception as e:
            print(f"❌ Trading session error: {str(e)}")
            self._log_error(log_file, f"Trading session error: {e}")
            raise

        print(f"\n{'='*60}")
        print(f"✅ Trading session completed: {today_date}")
        print(f"{'='*60}\n")

    def _log_error(self, log_file: Path, error_message: str) -> None:
        """Log error to log file."""
        with open(log_file, 'a') as f:
            f.write(json.dumps({
                "role": "error",
                "content": error_message,
                "timestamp": datetime.now().isoformat()
            }) + "\n")

    def __str__(self) -> str:
        return f"ClaudeCodeAgent(signature='{self.signature}', workspace='{self.claude_workspace}', mcp={self.mcp_servers})"

    def __repr__(self) -> str:
        return self.__str__()

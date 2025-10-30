"""
Portfolio NASDAQ Agent - Multi-Factor Portfolio for NASDAQ 100

Self-contained agent implementing portfolio strategy for NASDAQ 100 trading.
Uses shared ClaudeCodeAgent base with portfolio-specific methodology.
"""

from pathlib import Path
import sys
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agent.claude_code_agent.shared.claude_core import ClaudeCodeAgent
from agent.portfolio_agent.strategy import PortfolioStrategy
from agent.claude_code_agent.shared.instructions import build_claude_md
from prompts.agent_prompt import all_nasdaq_100_symbols


class PortfolioNASDAQAgent(ClaudeCodeAgent):
    """Portfolio agent with balanced risk management."""

    def __init__(self, signature: Optional[str] = None, **kwargs):
        self.strategy = PortfolioStrategy()
        signature = signature or self.strategy.signature
        kwargs.setdefault('stock_symbols', all_nasdaq_100_symbols)
        super().__init__(signature=signature, **kwargs)

    def _setup_claude_instructions(self) -> None:
        """Generate CLAUDE.md from shared base + portfolio-specific sections."""
        risk = self.strategy.get_risk_rules()

        # Build from shared sections + strategy-specific content
        claude_md = build_claude_md(
            strategy_name=self.strategy.name,
            strategy_framework=self.strategy.get_analysis_framework(),
            risk_rules=risk,
            base_sections=['base', 'data_formats', 'tools', 'decision_format']
        )

        # Save to CLAUDE.md in agent directory
        claude_md_path = Path(__file__).parent / 'CLAUDE.md'
        claude_md_path.write_text(claude_md, encoding='utf-8')
        print(f"✅ Generated CLAUDE.md for {self.strategy.name}")

    def _get_mcp_config(self) -> dict:
        """MCP server configuration for portfolio strategy."""
        return {
            "mcpServers": {
                "sequential-thinking": {
                    "command": "npx",
                    "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"]
                }
            }
        }

    def __str__(self) -> str:
        return f"PortfolioNASDAQAgent(signature='{self.signature}')"

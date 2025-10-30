"""
Base Strategy Interface

Minimal interface for trading strategies. Each strategy defines:
1. How to analyze stocks (analysis framework)
2. Risk management rules
3. MCP tools needed

Keep this simple - add complexity only when needed.
"""

from abc import ABC, abstractmethod
from typing import List


class BaseStrategy(ABC):
    """
    Minimal strategy interface.

    Each strategy provides:
    - Analysis framework (markdown for CLAUDE.md)
    - Risk rules (position sizing, stops)
    - MCP tool requirements
    """

    def __init__(self, name: str, signature: str):
        """
        Initialize strategy.

        Args:
            name: Human-readable name (e.g., "Alpha Generation")
            signature: Agent signature (e.g., "alpha-nasdaq")
        """
        self.name = name
        self.signature = signature

    @abstractmethod
    def get_analysis_framework(self) -> str:
        """
        Return analysis framework markdown for CLAUDE.md.

        This is the core methodology - how Claude should analyze
        and make trading decisions.

        Returns:
            Markdown string with analysis steps, decision criteria, examples
        """
        pass

    @abstractmethod
    def get_risk_rules(self) -> dict:
        """
        Return risk management configuration.

        Returns:
            dict with keys:
                - max_position: float (0.0-1.0)
                - min_cash: float (0.0-1.0)
                - stop_loss: float (0.0-1.0)
                - max_positions: int
                - confidence_threshold: float (0.0-1.0)
        """
        pass

    def get_mcp_tools(self) -> List[str]:
        """
        Return list of MCP servers needed.

        Returns:
            List of MCP server names (e.g., ["sequential-thinking", "playwright"])
        """
        return ["sequential-thinking"]  # Default: just reasoning
